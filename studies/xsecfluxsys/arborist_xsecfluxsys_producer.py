import os,sys
from typing import Dict, Any, List, Optional, Type
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register

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
        self._filepath  = config.get('rootfilepath')
        self._tree = None
        self._num_entries = 0
        self._rse_to_entryindex = {}

    def get_default_particle_thresholds(self):
        """Get default particle energy thresholds."""
        return

    def setDefaultValues(self):
        super().setDefaultValues()
        return

    def prepareStorage(self, output: Any) -> None:
        """Set up branches in the output ROOT TTree."""
        return

    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]

    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if event is signal nue CC inclusive."""
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)

        return {}
        
