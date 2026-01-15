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
    from ROOT import CalcEventWeightVariations
    from ROOT import std
except:
    print("Error loading ROOT and/or libMapDict.so")
    sys.exit(1)

# Example implementation of a ROOT-based dataset
@register
class ArboristXsecFluxSysProducer(ProducerBaseClass):
    """
    Implementation of Dataset for ROOT files.
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
        super().__init__(name, config)
        self._tree_name = config.get('tree','eventweight_tree')
        self._sample_filepaths  = config.get('rootfilepaths',{})
        self.nvariations = config.get('num_variations',1000)
        self._tree = None
        self._num_entries = 0
        self._sample_rse_to_entryindex = {} # will hold entry dictionary for a given sample
        self._current_sample_name = "none"
        self._current_sample_tchain = None
        self._params_to_include = config.get('par_variations_to_include',[])
        if len(self._params_to_include)==0:
            raise ValueError("Parameter list for reweight variations to include is empty.")
        self._params_to_include_v = std.vector("string")()
        for parname in self._params_to_include:
            self._params_to_include_v.push_back( parname )
        self._bin_config_list = config.get('bin_config')
        self.weight_calc = CalcEventWeightVariations()
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
        self.sysweight_treename       = config.get('weight_tree_name', 'weights') # weights for surprise files, sys_weights for arborist

        # cap weight value: sometimes a crazy large weight occurs
        self.maxvalidweight = config.get('maxvalidweight',100)

        # allow us to now have an event in the weight tree
        # we set the event to one
        self.allow_missing_weights = config.get('allow_missing_weights',True)
        self.missing_entries = 0

        # save selection criteria
        self.cut_formulas = config.get('cut_formulas',{})
        self.event_selection_critera = config.get('event_selection_critera',[])

        # keep track of number of bad weights
        self.num_badweights_per_universe = [0]*self.nvariations

    def _build_sample_entry_index(self,samplename):
        """
        Open file and make (run,subrun,event) --> index dictionary
        """

        if samplename in self._sample_filepaths:
            weightfilepath = self._sample_filepaths[samplename]
        else:
            raise ValueError(f"Could not find sample name, '{samplename}' in file path dictionary parameter")

        try:
            # open file
            print(f'Build event index map in file {weightfilepath} and tree {self._tree_name}.')
            rfile = rt.TFile( weightfilepath )
            # get ttree
            ttree = rfile.Get(self._tree_name)
            # If not found, search TDirectoryFile(s)
            if not ttree or not hasattr(ttree, 'SetBranchStatus'):
                ttree = None
                for key in rfile.GetListOfKeys():
                    obj = key.ReadObj()
                    if obj.InheritsFrom("TDirectoryFile"):
                        dirfile = obj
                        candidate = dirfile.Get(self._tree_name)
                        if candidate and hasattr(candidate, 'SetBranchStatus'):
                            ttree = candidate
                            break
            if not ttree or not hasattr(ttree, 'SetBranchStatus'):
                raise RuntimeError(f'Could not find tree "{self._tree_name}" in file or subdirectories: {weightfilepath}')

            # disable all but run, subrun, event branches to speed up read through file
            ttree.SetBranchStatus("*", 0)
            ttree.SetBranchStatus(self.weighttree_run_branch, 1)
            ttree.SetBranchStatus(self.weighttree_subrun_branch, 1)
            ttree.SetBranchStatus(self.weighttree_event_branch, 1)            
            nentries = ttree.GetEntries()
            print(f'Setup "{samplename}" weight tree event index map with {nentries} entries')
        except Exception as e:
            raise RuntimeError(f'Weight file path for "{samplename}" could not be opened: {weightfilepath}. Error: ',e)

        tstart = time.time()
        rsedict = {}
        # TODO: use a tqdm loop here?
        for iientry in range(nentries):
            #if (iientry%100000==0):
            #    print("  building index. entry ",iientry)
            ttree.GetEntry(iientry)
            runindex = eval(f'ttree.{self.weighttree_run_branch}')
            subindex = eval(f'ttree.{self.weighttree_subrun_branch}')
            evtindex = eval(f'ttree.{self.weighttree_event_branch}')
            rse = (runindex,subindex,evtindex)
            rsedict[rse] = iientry
            if iientry%100000==0:
                print("  building index. entry ",iientry," rse=",rse)

        dt_index = time.time()-tstart
        print(f'Time to make index: {dt_index:.2f}')
        self._sample_rse_to_entryindex[samplename] = rsedict

        rfile.Close()


    def setDefaultValues(self):
        super().setDefaultValues()
        return

    def prepareStorage(self, output: Any) -> None:
        """
        Set up what to save in the output ROOT TTree. Here, we're saving histograms and covariances.

        # TODO
        #  - for each entry in the config list bin_config, define a histogram for each variable. 
        #  - we define a TH1D to store the information. Mostly to use the find bin function
        #  - make a copy of a histogram for seach sample
        #  - for each (var,sample) histogram, we make 3 copies: one for sum[w], sum[w^2], N
        #  - need a global index for each histogram, this way we can build a covariance matrix
        """
        ibin_global = 0

        self.variable_list = []
        self.var_bininfo = {}

        self.outfile.cd()

        for varname in self._bin_config_list:
            vardict = self._bin_config_list[varname]

            binedges = vardict.get('binedges',[])
            if len(binedges)==0:
                # specify uniform bins
                bintype = 'uniform'
            else:
                # specify binedges
                if len(binedges)==1:
                    raise ValueError("When specifying bin edges, need 2 or more edges. Only 1 given.")
                bintype = 'binedges'

            var_bin_info = {
                'formula':vardict['formula'],
                'samples':vardict['apply_to_datasets'],
                'criteria':vardict['criteria'],
                'numbins':vardict['numbins'],
                'sample_hists':{},
                'sample_array':{}, # we save an array (nbins,nvariations) for each (sample,par) combination. So many!
                'ibin_start':ibin_global,
                'bintype':bintype
            }


            nbins = vardict['numbins']
            
            for sample in vardict['apply_to_datasets']:
                # we save a histogram to
                # 1. help us look up the bin position for this observable
                # 2. store the central value and the number of entries per bin
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
                # we make a dictionary with a slot for an array
                # we create the actual array later once we know the number of variations of each parameter
                for par in self._params_to_include:
                    var_bin_info['sample_array'][(sample,par)] = None

            ibin_global += nbins
            self.variable_list.append( varname )
            self.var_bininfo[varname] = var_bin_info

        print("Number of total bins defined: ",ibin_global)
        
        return

    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]

    def _load_sample_weight_tree(self, datasetname):
        if self._current_sample_tchain is not None:
            if datasetname != self._current_sample_name:
                self._current_sample_tchain.Close()
            else:
                return # already loaded

        if datasetname not in self._sample_filepaths:
            raise ValueError(f"Could not find sample name, '{datasetname}' in file path dictionary parameter")

        weightfilepath = self._sample_filepaths[datasetname]
        
        # Determine correct tree path (may be inside TDirectoryFile)
        rfile = rt.TFile(weightfilepath)
        ttree = rfile.Get(self._tree_name)
        tree_path = self._tree_name
        
        # If not found at root level, search TDirectoryFile(s)
        if not ttree or not hasattr(ttree, 'SetBranchStatus'):
            for key in rfile.GetListOfKeys():
                obj = key.ReadObj()
                if obj.InheritsFrom("TDirectoryFile"):
                    dirfile = obj
                    candidate = dirfile.Get(self._tree_name)
                    if candidate and hasattr(candidate, 'SetBranchStatus'):
                        tree_path = f"{dirfile.GetName()}/{self._tree_name}"
                        break
        rfile.Close()
        
        self._current_sample_tchain = rt.TChain(tree_path)
        self._current_sample_tchain.Add(weightfilepath)
        self._current_sample_tchain.SetBranchStatus("*", 0)
        self._current_sample_tchain.SetBranchStatus(self.sysweight_treename,1)
        nentries = self._current_sample_tchain.GetEntries()
        print("Loaded weight tree for dataset: ",datasetname)


    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if event is signal nue CC inclusive."""
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)
        datasetname = params.get('dataset_name')

        # evaluate all the selection formulas
        # in order to decide if this event is something we are going to fill
        select_results = {}
        for cutname,cutformula in self.cut_formulas.items():
            # Extract placeholders from the formula (strings inside {})
            placeholders = re.findall(r'\{([^}]+)\}', cutformula)

            # Create clean expression and namespace
            clean_expression = cutformula
            namespace = {}

            for placeholder in placeholders:
                # Create a simple variable name from the placeholder
                var_name = placeholder.replace('.', '_').replace('[', '_').replace(']', '')
                clean_expression = clean_expression.replace(f"{{{placeholder}}}", var_name)
                # Evaluate the placeholder to get the actual value
                namespace[var_name] = eval(placeholder)

            # Evaluate the clean expression with the namespace
            select_results[cutname] = eval(clean_expression, namespace)
        
        passes = True
        for cutname in self.event_selection_critera:
            if select_results[cutname]==False:
                passes = False
                break
            
        if passes==False:
            return {}

        if datasetname not in self._sample_rse_to_entryindex:
            self._build_sample_entry_index( datasetname )
            self._load_sample_weight_tree( datasetname )

        run    = eval(f'ntuple.{self.run_branch}')
        subrun = eval(f'ntuple.{self.subrun_branch}')
        event  = eval(f'ntuple.{self.event_branch}')        
        rse = (run,subrun,event)
        #print("process: ",rse)
        if rse in self._sample_rse_to_entryindex[datasetname]:
            entryindex = self._sample_rse_to_entryindex[datasetname][rse]
        else:
            print(f'Could not find RSE={rse} in RSE->index dictionary')
            self.missing_entries += 1
            if not self.allow_missing_weights:
                raise ValueError(f'Could not find RSE={rse} in RSE->index dictionary')
            else:
                return {}
        
        self._current_sample_tchain.GetEntry(entryindex)

        # get event weight
        evweight = ntuple.eventweight_weight

        # now calculate event weights from the N parameter variations (sometimes referred to as 'universes')      
        #universe_weight = self.weight_calc.calc( 1000, self._params_to_include_v, self._current_sample_tchain.sys_weights )
        #print("sample variation weights: ",universe_weight[0]," ",universe_weight[1]," ",universe_weight[2])

        # fill bins
        varvalues = {}
        for varname in self.variable_list:

            varinfo = self.var_bininfo[varname]

            # does the current dataset (aka sample) apply to this variable? 
            if datasetname not in varinfo['sample_hists']:
                continue # if not, we continue

            # sample does apply to this variable, so we get the observable variable value
            varformula = varinfo['formula']
            x = eval(f'ntuple.{varformula}')            
            varvalues[varname] = x

            # get the histogram
            hists = varinfo['sample_hists'][datasetname]

            # fill the central value (CV) and N (unweighted) histogram
            hists['cv'].Fill(x,evweight)
            hists['N'].Fill(x)

            # find the bin
            ibin = hists['cv'].GetXaxis().FindBin( x )

            # Iterate over the map elements
            for parname, values in eval(f'self._current_sample_tchain.{self.sysweight_treename}'):
                if parname not in self._params_to_include:
                    continue

                sample_par = (datasetname,parname)
                arr = varinfo['sample_array'][sample_par]
                nvariations = values.size()
                if arr is None:
                    varinfo['sample_array'][sample_par] = np.zeros( (varinfo['numbins']+2,nvariations) )
                    arr = varinfo['sample_array'][sample_par]

                for i in range(nvariations):
                    if values[i]<self.maxvalidweight:
                        arr[ibin,i] += values[i]
                    else:
                        self.num_badweights_per_universe[i] += 1

                
        return {}

    def finalize(self):
        """
        Runs at end of each event loop for each data sample processed.
        """
        print("write arborist histograms")
        print(" number of entries missing a weight value: ",self.missing_entries)
        self.outfile.cd()
        for varname in self.var_bininfo:
            varinfo = self.var_bininfo[varname]
            for sample,hists in varinfo['sample_hists'].items():
                hists['cv'].Write()
                hists['N'].Write()
            for (sample,par),arr in varinfo['sample_array'].items():
                if arr is None:
                    continue                
                # save result of all variations for this parameter
                hname = f"h{varname}__{sample}__{par}"
                print("Fill variation hist: ",hname,": sample=",sample," par=",par," arr=",arr.shape)
                xmin = varinfo['sample_hists'][sample]['cv'].GetXaxis().GetXmin()
                xmax = varinfo['sample_hists'][sample]['cv'].GetXaxis().GetXmax()
                hout = rt.TH2D( hname, "", arr.shape[0]-2, xmin, xmax, arr.shape[1], 0, arr.shape[1] )
                for i in range(arr.shape[0]):
                    for j in range(arr.shape[1]):
                        hout.SetBinContent( i, j+1, arr[i,j] )

                hname_mean = f"h{varname}__{sample}__{par}_mean"
                hmean = rt.TH1D( hname_mean, "", arr.shape[0]-2, xmin, xmax )
                hname_var = f"h{varname}__{sample}__{par}_variance"
                hvar  = rt.TH1D( hname_var, "", arr.shape[0]-2, xmin, xmax )
                for i in range(arr.shape[0]):
                    hmean.SetBinContent(i,arr[i,:].mean())
                    if arr.shape[1]>2:
                        hvar.SetBinContent(i,arr[i,:].var())
                        hmean.SetBinError(i,arr[i,:].std())
                    elif arr.shape[1]==2:
                        # for parameters with only 2 variations
                        # use half the difference as the std
                        xdiff = 0.5*np.abs(arr[i,1]-arr[i,0])
                        hvar.SetBinContent(i,xdiff*xdiff)
                        hmean.SetBinError(i,xdiff)
                    else:
                        continue
                hmean.Write()
                hvar.Write()

                hout.Write()

        hbaduniverses = rt.TH1D("hnum_bad_universe_weights","Number of weights per universe;universe number",self.nvariations,0,self.nvariations)
        for i,nbad in enumerate(self.num_badweights_per_universe):
            hbaduniverses.SetBinContent(i+1,nbad)
        hbaduniverses.Write()
        #self.outfile.Close()
        
        
