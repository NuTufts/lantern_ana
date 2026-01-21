import os,sys,time
import re
from typing import Dict, Any, List, Optional, Type
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
import numpy as np

try:
    import ROOT as rt
    rt.gSystem.Load("libMapDict.so")
    from ROOT import XsecFluxAccumulator
    from ROOT import std
except:
    print("Error loading ROOT and/or libMapDict.so. Run 'make' to build. (Needs ROOT)")
    sys.exit(1)

# Example implementation of a ROOT-based dataset
@register
class ArboristXsecFluxSysProducer(ProducerBaseClass):
    """
    Implementation of Dataset for ROOT files.

    This producer estimates variance of model expectation for observable bins
    based on variations of xsec and flux model parameters.

    The heavy weight accumulation is offloaded to C++ (XsecFluxAccumulator) for performance.
    Python handles event selection and bin assignment, C++ handles the inner loop
    over ~1000 universe variations per parameter.
    """    
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        """
        Initialize producer, whose goal is to estimate the variance of the model expectation for observable bins
          based on variations of the xsec and flux model parameters.
        Also want co-variances between these bins.

        Example of bin_config block:

        bin_config:
          visible_energy: # bins of visible energy of the neutrino interaction
            formula: visible_energy
            numbins: 30
            minvalue: 0.0
            maxvalue: 3000.0
            apply_to_datasets: ['run1_bnb_nu_overlay_mcc9_v28_wctagger']
            criteria: ['pass_numu_cc_inclusive']

        We are saving the observed value of some set of bins
        For each bin,
          1. we save Sum[w] and Sum[w^2], where w is the weight for each event falling within a bin.
          2. we also save the number of entries, N, falling within a bin
          3. use Sum[w], Sum[w^2], N to calculate the mean and variance in each bin
        We also want correlations amongst all bins
          1. so we need to save  Sum[w_i*w_j] as well
        what do we need for a bin definition?
          1. observable quantify to histogram
          2. bin bounds:
             - either use binedges with N+1 values to specify N bins
             - or provide numbins, minvalue, and maxvalue to define uniform-spaced bins
          3. criteria to be filled within the bin
          4. sample that contributes to the bin

        Args:
            name: A unique identifier for this dataset
            config: Dictionary containing configuration parameters:
             - todo: document parameters
        """
        self._tree_name = config.get('tree','eventweight_tree')
        self._sample_filepaths  = config.get('rootfilepaths',{})
        self.nvariations = config.get('num_variations',1000)
        self._tree = None
        self._num_entries = 0
        self._current_sample_name = "none"
        self._params_to_include = config.get('par_variations_to_include',[])
        if len(self._params_to_include)==0:
            raise ValueError("Parameter list for reweight variations to include is empty.")
        self._bin_config_list = config.get('bin_config')
        self.outfile_path = config.get('output_filename','temp_covar.root')
        self.outfile = rt.TFile(self.outfile_path,'recreate')

        # name of the run, subrun, event branches in the analysis_tree
        self.run_branch    = config.get('run','run')
        self.subrun_branch = config.get('subrun','subrun')
        self.event_branch  = config.get('event','event')

        # name of the run, subrun, event branches in the weight tree
        self.weighttree_run_branch    = config.get('weight_tree_run','run')
        self.weighttree_subrun_branch = config.get('weight_tree_subrun','sub')
        self.weighttree_event_branch  = config.get('weight_tree_event','evt')
        self.sysweight_treename       = config.get('weight_tree_name', 'weights')
        self.weight_branch_type       = config.get('weight_branch_type',-1)
        if self.weight_branch_type==-1:
            raise ValueError("Must set config parameter 'weight_branch_type'. Options: 0=arborist file, 1=surprise file.")

        # cap weight value: sometimes a crazy large weight occurs
        self.maxvalidweight = config.get('maxvalidweight',1000)

        # save selection criteria
        self.cut_formulas = config.get('cut_formulas',{})
        self.event_selection_critera = config.get('event_selection_critera',[])

        # Storage for passing events per sample
        # Format: { sample_name: { 'rse': [...], 'bin_indices': [...], 'weights': [...] } }
        self._passing_events = {}

        # xsec
        self.xsec_params = config.get('xsec_params',[])

        # C++ accumulator instance
        self.accumulator = XsecFluxAccumulator()        

    def setDefaultValues(self):
        super().setDefaultValues()
        return

    def prepareStorage(self, output: Any) -> None:
        """
        Set up what to save in the output ROOT TTree. Here, we're saving histograms and covariances.
        """
        ibin_global = 0

        self.variable_list = []
        self.var_bininfo = {}

        self.outfile.cd()

        for varname in self._bin_config_list:
            vardict = self._bin_config_list[varname]

            binedges = vardict.get('binedges',[])
            if len(binedges)==0:
                bintype = 'uniform'
            else:
                if len(binedges)==1:
                    raise ValueError("When specifying bin edges, need 2 or more edges. Only 1 given.")
                bintype = 'binedges'

            var_bin_info = {
                'formula':vardict['formula'],
                'samples':vardict['apply_to_datasets'],
                'criteria':vardict['criteria'],
                'numbins':vardict['numbins'],
                'sample_hists':{},
                'ibin_start':ibin_global,
                'bintype':bintype
            }

            nbins = vardict['numbins']

            for sample in vardict['apply_to_datasets']:
                hname = f"h{varname}_{sample}"
                var_bin_info['sample_hists'][sample] = {}
                for x in ['cv','N']:
                    hvar_name = hname+f"_{x}"
                    if var_bin_info['bintype']=='uniform':
                        h = rt.TH1D(hvar_name,"",nbins, vardict['minvalue'],vardict['maxvalue'])
                    elif var_bin_info['bintype']=='binedges':
                        bin_array = array('f',binedges)
                        nbins = len(binedges)-1
                        h = rt.TH1D(hvar_name,"",nbins, bin_array)
                    var_bin_info['sample_hists'][sample][x] = h

            ibin_global += nbins
            self.variable_list.append( varname )
            self.var_bininfo[varname] = var_bin_info

        print("Number of total bins defined: ",ibin_global)

        # Configure the C++ accumulator
        bins_per_var = []
        for varname in self.variable_list:
            # +2 for underflow and overflow bins
            bins_per_var.append(self.var_bininfo[varname]['numbins'] + 2)

        # make c++ vector for xsec param list
        self.xsec_params_vec_cpp = rt.std.vector("string")()
        for xsecpar in self.xsec_params:
            self.xsec_params_vec_cpp.push_back( xsecpar )

        self.accumulator.configure(
            len(self.variable_list),
            bins_per_var,
            self._params_to_include,
            self.xsec_params_vec_cpp,
            self.nvariations,
            self.maxvalidweight,
            self.weight_branch_type
        )

        return

    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]

    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        First pass: determine if event passes selection and record bin assignments.

        This is now lightweight - just stores RSE, bin indices, and central weight.
        The heavy weight accumulation happens in finalize() via C++.
        """
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)
        datasetname = params.get('dataset_name')

        # Evaluate all the selection formulas
        select_results = {}
        for cutname,cutformula in self.cut_formulas.items():
            placeholders = re.findall(r'\{([^}]+)\}', cutformula)
            clean_expression = cutformula
            namespace = {}

            for placeholder in placeholders:
                var_name = placeholder.replace('.', '_').replace('[', '_').replace(']', '')
                clean_expression = clean_expression.replace(f"{{{placeholder}}}", var_name)
                namespace[var_name] = eval(placeholder)

            select_results[cutname] = eval(clean_expression, namespace)

        passes = True
        for cutname in self.event_selection_critera:
            if select_results[cutname]==False:
                passes = False
                break

        if passes==False:
            return {}

        # Get RSE
        run    = eval(f'ntuple.{self.run_branch}')
        subrun = eval(f'ntuple.{self.subrun_branch}')
        event  = eval(f'ntuple.{self.event_branch}')

        # Get central event weight
        evweight = ntuple.eventweight_weight

        # Compute bin indices for all variables
        bin_indices = []
        for varname in self.variable_list:
            varinfo = self.var_bininfo[varname]

            if datasetname not in varinfo['sample_hists']:
                # Variable doesn't apply to this dataset
                bin_indices.append(-1)
                continue

            # Get observable value and find bin
            varformula = varinfo['formula']
            x = eval(f'ntuple.{varformula}')

            hists = varinfo['sample_hists'][datasetname]

            # Fill CV and N histograms (still done per-event)
            hists['cv'].Fill(x, evweight)
            hists['N'].Fill(x)

            # Get bin index
            ibin = hists['cv'].GetXaxis().FindBin(x)
            bin_indices.append(ibin)

        # Initialize storage for this sample if needed
        if datasetname not in self._passing_events:
            self._passing_events[datasetname] = {
                'rse': [],
                'bin_indices': [],
                'weights': []
            }

        # Store this event's info for later C++ processing
        self._passing_events[datasetname]['rse'].append([run, subrun, event])
        self._passing_events[datasetname]['bin_indices'].append(bin_indices)
        self._passing_events[datasetname]['weights'].append(evweight)

        return {}

    def finalize(self):
        """
        Second pass: process all passing events through C++ accumulator.

        For each sample, call the C++ XsecFluxAccumulator to process all events
        and accumulate weights across all universe variations.
        """
        print("ArboristXsecFluxSysProducer: finalize()")

        self.outfile.cd()

        # Process each sample
        for datasetname, event_data in self._passing_events.items():
            if datasetname not in self._sample_filepaths:
                print(f"Warning: No weight file path for sample {datasetname}, skipping")
                continue

            weight_file_path = self._sample_filepaths[datasetname]
            num_events = len(event_data['rse'])

            print(f"Processing sample {datasetname}: {num_events} passing events")

            if num_events == 0:
                continue

            # Reset accumulator for this sample
            self.accumulator.reset()

            # Convert Python lists to std::vector for C++
            rse_vec = std.vector("std::vector<int>")()
            for rse in event_data['rse']:
                inner = std.vector("int")()
                for val in rse:
                    inner.push_back(int(val))
                rse_vec.push_back(inner)

            bin_indices_vec = std.vector("std::vector<int>")()
            for bins in event_data['bin_indices']:
                inner = std.vector("int")()
                for val in bins:
                    inner.push_back(int(val))
                bin_indices_vec.push_back(inner)

            weights_vec = std.vector("double")()
            for w in event_data['weights']:
                weights_vec.push_back(float(w))

            # Call C++ to process all events
            tstart = time.time()
            processed = self.accumulator.processAllEvents(
                weight_file_path,
                self._tree_name,
                self.sysweight_treename,
                self.weighttree_run_branch,
                self.weighttree_subrun_branch,
                self.weighttree_event_branch,
                rse_vec,
                bin_indices_vec,
                weights_vec
            )
            dt = time.time() - tstart
            print(f"  C++ processed {processed} events in {dt:.2f}s")
            print(f"  Missing events: {self.accumulator.getMissingEventCount()}")

            # IMPORTANT: C++ opened a TFile which changed ROOT's gDirectory
            # Must switch back to our output file before writing
            self.outfile.cd()

            # Get results from C++ and write histograms
            found_params = self.accumulator.getFoundParams()
            print(f"  Found parameters: {list(found_params)}")

            for var_idx, varname in enumerate(self.variable_list):
                varinfo = self.var_bininfo[varname]

                if datasetname not in varinfo['sample_hists']:
                    continue

                # Write CV and N histograms
                varinfo['sample_hists'][datasetname]['cv'].Write()
                varinfo['sample_hists'][datasetname]['N'].Write()

                # Get histogram properties for output
                h_cv = varinfo['sample_hists'][datasetname]['cv']
                xmin = h_cv.GetXaxis().GetXmin()
                xmax = h_cv.GetXaxis().GetXmax()
                nbins = varinfo['numbins']

                # Process each parameter
                for par in found_params:
                    nvariations = self.accumulator.getNumVariationsForParam(par)
                    if nvariations == 0:
                        continue

                    # Get accumulated array from C++
                    arr_flat = self.accumulator.getArray(var_idx, par)
                    if len(arr_flat) == 0:
                        continue

                    # Reshape to (nbins+2, nvariations)
                    # The C++ stores as row-major: arr[ibin * nvariations + iUniv]
                    nbins_with_overflow = nbins + 2
                    arr = np.array(arr_flat).reshape(nbins_with_overflow, nvariations)

                    # Create 2D histogram for all variations
                    hname = f"h{varname}__{datasetname}__{par}"
                    hout = rt.TH2D(hname, "", nbins, xmin, xmax, nvariations, 0, nvariations)
                    for i in range(nbins_with_overflow):
                        for j in range(nvariations):
                            hout.SetBinContent(i, j+1, arr[i,j])
                    hout.Write()

                    # Create mean and variance histograms
                    hname_mean = f"h{varname}__{datasetname}__{par}_mean"
                    hmean = rt.TH1D(hname_mean, "", nbins, xmin, xmax)
                    hname_var = f"h{varname}__{datasetname}__{par}_variance"
                    hvar = rt.TH1D(hname_var, "", nbins, xmin, xmax)
                    hname_badweights = f"h{varname}__{datasetname}__{par}_badweights"
                    hbadweights = rt.TH1D(hname_badweights, "", nbins, xmin, xmax)

                    for i in range(nbins_with_overflow):
                        hmean.SetBinContent(i, arr[i,:].mean())
                        if nvariations > 2:
                            hvar.SetBinContent(i, arr[i,:].var())
                            hmean.SetBinError(i, arr[i,:].std())
                        elif nvariations == 2:
                            xdiff = np.abs(arr[i,1] - arr[i,0])
                            hvar.SetBinContent(i, xdiff * xdiff)
                            hmean.SetBinError(i, xdiff )

                    badweights_per_varbin = self.accumulator.getBadWeightsPerVarBin(var_idx,par)
                    for ibin in range(1,hbadweights.GetXaxis().GetNbins()+1):
                        hbadweights.SetBinContent(ibin,badweights_per_varbin.at(ibin-1))

                    hmean.Write()
                    hvar.Write()
                    hbadweights.Write()

            # Write bad weight counts
            bad_weights = self.accumulator.getBadWeightCounts()
            hbaduniverses = rt.TH1D(
                f"hnum_bad_universe_weights_{datasetname}",
                f"Number of bad weights per universe ({datasetname});universe number",
                self.nvariations, 0, self.nvariations
            )
            for i, nbad in enumerate(bad_weights):
                if i < self.nvariations:
                    hbaduniverses.SetBinContent(i+1, nbad)
            hbaduniverses.Write()

        print("ArboristXsecFluxSysProducer: finalize() complete")
