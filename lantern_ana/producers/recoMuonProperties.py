# lantern_ana/producers/numu_cc_producers.py
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory

@register
class MuonPropertiesProducer(ProducerBaseClass):
    """
    Producer that extracts muon properties for CC numu events.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.muon_angle = array('f', [-1.0])
        self.muon_energy = array('f', [-1.0])
        self.muon_pid_score = array('f', [-1.0])
        
    def prepareStorage(self, output):
        """Set up branches in the output ROOT TTree."""
        output.Branch(f"{self.name}_angle", self.muon_angle, f"{self.name}_angle/F")
        output.Branch(f"{self.name}_energy", self.muon_energy, f"{self.name}_energy/F")
        output.Branch(f"{self.name}_pid_score", self.muon_pid_score, f"{self.name}_pid_score/F")
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Extract muon properties."""
        ntuple = data["gen2ntuple"]
        
        # Reset output variables
        self.muon_angle[0] = -1.0
        self.muon_energy[0] = -1.0
        self.muon_pid_score[0] = -1.0
        
        # Variables to keep track of highest energy muon
        highest_energy = -1.0
        muon_index = -1
        
        # Find highest energy muon track
        for i in range(ntuple.nTracks):
            if (ntuple.trackClassified[i] == 1 and 
                ntuple.trackPID[i] == 13 and 
                ntuple.trackIsSecondary[i] == 0):
                
                # Compare energy to find highest energy muon
                if ntuple.trackRecoE[i] > highest_energy:
                    highest_energy = ntuple.trackRecoE[i]
                    muon_index = i
        
        # If muon found, extract properties
        if muon_index >= 0:
            # Calculate cosine of angle between muon direction and beam
            beam_dir = np.array([0.0, 0.0, 1.0])
            muon_dir = np.array([
                ntuple.trackStartDirX[muon_index],
                ntuple.trackStartDirY[muon_index],
                ntuple.trackStartDirZ[muon_index]
            ])
            
            # Normalize muon direction vector
            norm = np.linalg.norm(muon_dir)
            if norm > 0:
                muon_dir = muon_dir / norm
                self.muon_angle[0] = np.dot(muon_dir, beam_dir)
            
            # Record muon energy
            self.muon_energy[0] = ntuple.trackRecoE[muon_index]
            
            # Record muon PID score
            self.muon_pid_score[0] = ntuple.trackMuScore[muon_index]
        
        return {
            "angle": self.muon_angle[0],
            "energy": self.muon_energy[0],
            "pid_score": self.muon_pid_score[0]
        }
