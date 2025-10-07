import os,sys

# lantern_ana/producers/numu_cc_producers.py
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory

@register
class trueNuPropertiesProducer(ProducerBaseClass):
    """
    Producer that transfers true info about the Neutrino.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.Enu = array('f', [0.0])

    def setDefaultValues(self):
        super().setDefaultValues()
        self.Enu[0] = 0.0
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"{self.name}_Enu", self.Enu, f"{self.name}_Enu/F")
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Calculate total visible energy from all primary tracks and showers."""
        self.setDefaultValues()
        ismc = params.get('ismc',False)
        if not ismc:
            return {'Enu':self.Enu[0]}

        ntuple = data["gen2ntuple"]
        
        # Reset output variable
        self.Enu[0] = ntuple.trueNuE
        
        return {"Enu":self.Enu[0]}
    
    def finalize(self):
        """ Nothing to do after event loop. """
        return