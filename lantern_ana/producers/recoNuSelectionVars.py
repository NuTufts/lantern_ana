import numpy as np
from typing import Dict, Any, List
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
import ROOT

@register
class RecoNuSelectionVariablesProducer(ProducerBaseClass):
    """
    This is a collection of possible variables for selecting true neutrino
    vertices from cosmic backgrounds.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self._track_min_len = config.get("track_min_len", 5.0)  # Minimum energy to consider
        
        # Output variables
        self.n_tracks = array('i',[0]) # number of above threshold tracks
        self.e_primary_score = array('f',[0.0])

        # For the array, we need a numpy array with a fixed memory location
        # that won't be garbage collected
        self.energy_array_np = np.zeros(self.max_tracks, dtype=np.float32)
        # Convert to a ROOT-compatible array
        self._energy_array = array('f', [0.0]*self.max_tracks)
    
    def prepareStorage(self, output: Any) -> None:
        """Set up branches in the output ROOT TTree."""
        # Assuming output is a ROOT TTree or similar interface
        # output.Branch(f"{self.name}_total_energy", self.total_energy, f"{self.name}_total_energy/F")
        # output.Branch(f"{self.name}_n_tracks", self.n_tracks, f"{self.name}_n_tracks/I")
        # output.Branch(f"{self.name}_energy_array", self._energy_array, f"{self.name}_energy_array[{self.max_tracks}]/F")

    def setDefaultValues(self):
        super().setDefaultValues()
    
    def productType(self) -> type:
        """Return the type of product (a dictionary in this case)."""
        return dict
    
    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple",'reco_nue_CCinc']  # We need the ntuple and the cutdata
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Process an event by calculating track energy statistics."""
        # Get gen2ntuple from input data
        ntuple = data["gen2ntuple"]
        cutdata = data['cutdata_reco_nue_CCinc']
        
        # Return results
        return {}