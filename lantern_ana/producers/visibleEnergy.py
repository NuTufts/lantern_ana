# lantern_ana/producers/numu_cc_producers.py
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory

@register
class VisibleEnergyProducer(ProducerBaseClass):
    """
    Producer that calculates the total visible energy from all primary tracks and showers.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.total_visible_energy = array('f', [0.0])
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"{self.name}", self.total_visible_energy, f"{self.name}/F")
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Calculate total visible energy from all primary tracks and showers."""
        ntuple = data["gen2ntuple"]
        
        # Reset output variable
        self.total_visible_energy[0] = 0.0
        
        # Sum track energies
        for i in range(ntuple.nTracks):
            if ntuple.trackIsSecondary[i] == 0:  # Only primary tracks
                self.total_visible_energy[0] += ntuple.trackRecoE[i]
        
        # Sum shower energies
        for i in range(ntuple.nShowers):
            if ntuple.showerIsSecondary[i] == 0:  # Only primary showers
                self.total_visible_energy[0] += ntuple.showerRecoE[i]
        
        return self.total_visible_energy[0]
