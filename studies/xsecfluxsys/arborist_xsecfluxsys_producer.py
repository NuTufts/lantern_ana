import os,sys,time
from typing import Dict, Any, List, Optional, Type
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
import numpy as np

try:
    import ROOT as rt
    rt.gSystem.Load("libMapDict.so")
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
          1. observable to bin
          2. bin bounds
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
        self._tree = None
        self._num_entries = 0
        self._sample_rse_to_entryindex = {} # will hold entry dictionary for a given sample
        self._current_sample_name = "none"
        self._current_sample_tchain = None
        self._params_to_include = config.get('par_variations_to_include',[])
        if len(self._params_to_include)==0:
            raise ValueError("Parameter list for reweight variations to include is empty.")
        self._bin_config_list = config.get('bin_config')
        self.outfile = rt.TFile("temp_covar.root",'recreate')

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
            rfile = rt.TFile( weightfilepath )
            # get ttree
            ttree = rfile.Get(self._tree_name)
            # disable all but run, subrun, event branches to speed up read through file
            ttree.SetBranchStatus("*", 0)
            ttree.SetBranchStatus("run", 1)
            ttree.SetBranchStatus("subrun", 1)
            ttree.SetBranchStatus("event", 1)            
            nentries = ttree.GetEntries()
            print(f'Loaded "{samplename}" weight tree with {nentries} entries')
        except:
            raise RuntimeError(f'Weight file path for "{samplename}" could not be opened: {weightfilepath}')

        tstart = time.time()
        rsedict = {}
        # TODO: use a tqdm loop here?
        for iientry in range(nentries):
            #if (iientry%100000==0):
            #    print("  building index. entry ",iientry)
            ttree.GetEntry(iientry)
            rse = (ttree.run,ttree.subrun,ttree.event)
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

        hlist_cv = []
        hlist_w = []
        hlist_w2 = []
        hlist_n = []

        self.variable_list = []
        self.var_bin_info_dict = {}

        self.outfile.cd()

        for varname in self._bin_config_list:
            vardict = self._bin_config_list[varname]
            var_bin_info = {
                'formula':vardict['formula'],
                'samples':vardict['apply_to_datasets'],
                'criteria':vardict['criteria'],
                'sample_hists':{},
                'ibin_start':ibin_global
            }

            nbins = vardict['numbins']
            for sample in vardict['apply_to_datasets']:
                hname = f"h{varname}_{sample}"
                for x in ['cv','w','w2','N']:
                    h = rt.TH1D(hname+f"_{x}","",nbins, vardict['minvalue'],vardict['maxvalue'])
                var_bin_info['sample_hists'][sample] = h

            ibin_global += nbins
            self.variable_list.append( varname )
            self.var_bininfo[varname] = var_bin_info

        print("Number of total bins defined: ",ibin_global)
        
        return

    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]

    def _load_sample_weight_tree(self, datasetname ):
        if self._current_sample_tchain is not None:
            if datasetname != self._current_sample_name:
                self._current_sample_tchain.Close()
            else:
                return # already loaded

        self._current_sample_tchain = rt.TChain( self._tree_name )
        if datasetname not in self._sample_filepaths:
            raise ValueError(f"Could not find sample name, '{datasetname}' in file path dictionary parameter")

        self._current_sample_tchain.Add(self._sample_filepaths[datasetname])
        nentries = self._current_sample_tchain.GetEntries()
        print("Loaded weight tree for dataset: ",datasetname)


    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if event is signal nue CC inclusive."""
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)
        datasetname = params.get('dataset_name')

        # decide if this event is something we are going to fill
        # for debug:
        """
        cut = "vertex_properties_found==1"
        cut += " && muon_properties_pid_score>-0.9"
        cut += " && vertex_properties_infiducial==1"
        cut += " && muon_properties_energy>0.0"
        """
        passes = False
        if ntuple.vertex_properties_found==1 and ntuple.muon_properties_pid_score>-0.9 and ntuple.vertex_properties_infiducial==1 and ntuple.muon_properties_energy>0.0:
            passes = True
            
        print("event passes test numucc inclusive")
        
        if passes==False:
            return {}

        if datasetname not in self._sample_rse_to_entryindex:
            self._build_sample_entry_index( datasetname )
            self._load_sample_weight_tree( datasetname )

        rse = (ntuple.run, ntuple.subrun, ntuple.event)
        if rse in self._sample_rse_to_entryindex[datasetname]:
            entryindex = self._sample_rse_to_entryindex[datasetname][rse]
        else:
            raise ValueError(f'Could not find RSE={rse} in RSE->index dictionary')
        
        self._current_sample_tchain.GetEntry(entryindex)

        # now calculate event weights
        weight = 1.0

        # loop over all weights in the sys_weights branch. 
        # take product of specified parameters to get final event weight
        # would be faster with here I bet
        universe_weight = np.ones(1000)
        for key, values in self._current_sample_tchain.sys_weights:
            if key in self._params_to_include:
                for i in range(len(values)):
                    if i<1000 and np.isnan(values[i])==False and np.isfinite(values[i])==True:
                        universe_weight[i] *= values[i]
                    else:
                        print(f"entry[{entryindex}] bad value{key}[{i}] = {values[i]}")

        print(f"  first 10 universe event weights: ",universe_weight[:10])

        # fill bins
        varvalues = {}
        for varname in self.variable_list:
            varinfo = self.var_bin_info_dict['varname']
            varformula = varinfo['formula']
            eval(f'varvalues[varname] = ntuple.{varformula}')
        print(varvalues)
            
    #if len(values) > 0:
    #    print(f"  First few values: {list(values[:min(3, len(values))])}")

        


        return {}
        
