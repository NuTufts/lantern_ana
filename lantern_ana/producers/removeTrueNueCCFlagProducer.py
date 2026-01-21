import os, sys
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory

@register
class RemoveTrueNueCCFlagProducer(ProducerBaseClass):
    """
    Producer that flags true electron neutrino CC events.
    
    Creates a flag variable (0 or 1) indicating whether an event is a 
    true νe CC interaction that would typically be removed from νμ analyses.
    
    Flag = 1: True νe CC event (would be cut)
    Flag = 0: Not true νe CC (would be kept)
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.truenuccflag = array('i', [0])

    def setDefaultValues(self):
        super().setDefaultValues()
        self.truenuccflag[0] = 0
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(self.name, self.truenuccflag, f"{self.name}/I")
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Flag events that are true nue CC interactions."""
        self.setDefaultValues()
        
        # Data events always get flag = 0 (no truth info)
        ismc = params.get('ismc', False)
        if not ismc:
            return {self.name: self.truenuccflag[0]}

        ntuple = data["gen2ntuple"]
        
        # Check if truth variables exist
        if hasattr(ntuple, 'trueNuCCNC') and hasattr(ntuple, 'trueNuPDG'):
            # Flag true nue CC: CC interaction (0) and nue PDG (±12)
            if ntuple.trueNuCCNC == 0 and abs(ntuple.trueNuPDG) == 12:
                self.truenuccflag[0] = 1

        return {self.name: self.truenuccflag[0]}

    def finalize(self):
        """Nothing to do after event loop."""
        return