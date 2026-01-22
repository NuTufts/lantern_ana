import numpy as np
from typing import Dict, Any, List
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
import ROOT

@register
class RecoMuonTrackPropertiesProducer(ProducerBaseClass):
    """
    Producer that calculates properties of reconstructed muon tracks.
    This replaces the muon analysis logic previously embedded in cuts.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Configuration
        self._track_min_energy = config.get("track_min_energy", 25.0)
        
        # Output variables for muon track properties
        self.muon_vars = {
            'max_muscore': array('f', [-200.0]),
            'max_mucharge': array('f', [0.0]),
            'nMuTracks': array('i', [0]),
            'ntracks_above_threshold': array('i', [0])
        }

    def setDefaultValues(self):
        super().setDefaultValues()
        self.muon_vars['max_muscore'][0] = -200.0
        self.muon_vars['max_mucharge'][0] = 0.0
        self.muon_vars['nMuTracks'][0] = 0
        self.muon_vars['ntracks_above_threshold'][0] = 0
    
    def prepareStorage(self, output: Any) -> None:
        """Set up branches in the output ROOT TTree."""
        for var_name, var_array in self.muon_vars.items():
            if var_array.typecode == 'i':
                branch_type = f"{self.name}_{var_name}/I"
            else:
                branch_type = f"{self.name}_{var_name}/F"
            output.Branch(f"{self.name}_{var_name}", var_array, branch_type)
    
    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate muon track properties."""
        ntuple = data["gen2ntuple"]
        
        # Reset to defaults
        self.setDefaultValues()
        
        # If no vertex found, return defaults
        if ntuple.foundVertex != 1:
            return self._get_results()
        
        # Initialize tracking variables
        maxMuScore = -200.0
        maxMuQ = 0.0
        maxmu_idx = -1
        num_tracks_above_threshold = 0
        nMuTracks = 0
        
        # Loop over tracks to find muon properties
        for iT in range(ntuple.nTracks):
            # Count number of primary tracks above energy threshold
            if ntuple.trackIsSecondary[iT] == 0:  # Primary tracks only
                if ntuple.trackRecoE[iT] > self._track_min_energy:
                    num_tracks_above_threshold += 1
            
            # Skip secondary or unclassified tracks for muon analysis
            if ntuple.trackIsSecondary[iT] != 0 or ntuple.trackClassified[iT] != 1:
                continue
            
            # Count muon tracks
            if abs(ntuple.trackPID[iT]) == 13:
                nMuTracks += 1
            
            # Find track with maximum muon score
            if ntuple.trackMuScore[iT] > maxMuScore:
                maxMuScore = ntuple.trackMuScore[iT]
                maxmu_idx = iT
                maxMuQ = ntuple.trackCharge[iT]
        
        # Store results
        self.muon_vars['max_muscore'][0] = maxMuScore
        self.muon_vars['max_mucharge'][0] = maxMuQ
        self.muon_vars['nMuTracks'][0] = nMuTracks
        self.muon_vars['ntracks_above_threshold'][0] = num_tracks_above_threshold
        
        return self._get_results()
    
    def _get_results(self) -> Dict[str, Any]:
        """Convert array values to a results dictionary."""
        results = {}
        for var_name, var_array in self.muon_vars.items():
            results[var_name] = var_array[0]
        return results

    def finalize(self):
        """
        nothing to do after the event loop
        """
        super().finalize()
        return