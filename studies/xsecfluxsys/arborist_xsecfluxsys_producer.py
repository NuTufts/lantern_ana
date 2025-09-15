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
        Initialize Tree containing event weights from xsec and flux model parameter variations
        
        Args:
            name: A unique identifier for this dataset
            config: Dictionary containing configuration parameters:
                - tree: Name of the TTree to read, default: eventweight_tree
                - filepaths: List of ROOT file paths
                - ismc: Whether this is a Monte Carlo dataset, {default: False}
                - nspills: Number of spills this data set represents (optional) {default: None}
                - pot: POT for this data set (optional) {default: None}
                - friendtrees: A dict with keys being name of the friend tree and value being the file
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
        """Set up branches in the output ROOT TTree."""
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
        universe_weight = np.arrays('f',[1.0]*1000)
        for key, values in self._current_sample_tchain.sys_weights:
            if key in self._params_to_include:
                for i in range(len(values)):
                    if i<1000 and is not np.isnan(values[i]) and is np.isfinite(values[i]):
                        universe_weight[i] *= values[i]
                    else:
                        print(f"entry[{entryindex}] bad value{key}[{i}] = {values[i]}")

        print(f"  first 10 universe event weights: ",universe_weight[:10])
            
    #if len(values) > 0:
    #    print(f"  First few values: {list(values[:min(3, len(values))])}")

        


        return {}
        
