import numpy as np
from typing import Dict, Any, List
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
import ROOT

@register
class TrackEnergyProducer(ProducerBaseClass):
    """
    Example producer that calculates statistics about track energies.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.min_energy = config.get("min_energy", 0)  # Minimum energy to consider
        self.max_tracks = config.get("max_tracks", 10)  # Maximum number of tracks to process
        
        # Output variables
        self.total_energy = array('f',[0])
        self.n_tracks = array('i',[0])

        # For the array, we need a numpy array with a fixed memory location
        # that won't be garbage collected
        self.energy_array_np = np.zeros(self.max_tracks, dtype=np.float32)
        # Convert to a ROOT-compatible array
        self._energy_array = array('f', [0.0]*self.max_tracks)
    
    def prepareStorage(self, output: Any) -> None:
        """Set up branches in the output ROOT TTree."""
        # Assuming output is a ROOT TTree or similar interface
        output.Branch(f"{self.name}_total_energy", self.total_energy, f"{self.name}_total_energy/F")
        output.Branch(f"{self.name}_n_tracks", self.n_tracks, f"{self.name}_n_tracks/I")
        output.Branch(f"{self.name}_energy_array", self._energy_array, f"{self.name}_energy_array[{self.max_tracks}]/F")

    def setDefaultValues(self):
        super().setDefaultValues()
        self.total_energy[0] = 0.0
        self.n_tracks[0] = 0
        for i in range(self.max_tracks):
            self._energy_array[i] = 0.0
    
    def productType(self) -> type:
        """Return the type of product (a dictionary in this case)."""
        return dict
    
    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]  # We only need the gen2ntuple tree
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Process an event by calculating track energy statistics."""
        # Get gen2ntuple from input data
        ntuple = data["gen2ntuple"]
        
        # Reset output variables
        self.total_energy[0] = 0.0
        self.n_tracks[0] = 0
        self.energy_array_np.fill(0.0)
        # Reset the array to all zeros
        for i in range(len(self._energy_array)):
            self._energy_array[i] = 0.0
        
        # Process tracks if vertex was found
        if ntuple.foundVertex:
            # Calculate total energy and populate energy array
            for i in range(min(ntuple.nTracks, self.max_tracks)):
                # Skip tracks with energy below threshold
                if ntuple.trackRecoE[i] < self.min_energy:
                    continue
                
                # Add track energy to total
                self.total_energy[0] += ntuple.trackRecoE[i]
                
                # Store track energy in array
                self._energy_array[self.n_tracks[0]] = ntuple.trackRecoE[i]
                self.n_tracks[0] += 1
        
        # Return results
        return {
            "total_energy": self.total_energy,
            "n_tracks": self.n_tracks,
            "energy_array": self._energy_array
        }

    def finalize(self):
        """
        nothing to do after the event loop
        """
        super().finalize()
        return