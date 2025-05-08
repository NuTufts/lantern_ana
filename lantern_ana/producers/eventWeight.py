import os,sys

# lantern_ana/producers/numu_cc_producers.py
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory

@register
class eventWeightProducer(ProducerBaseClass):
    """
    Producer that transfers true info about the Neutrino.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.eventweight = array('f', [0.0])

    def setDefaultValues(self):
        super().setDefaultValues()
        self.eventweight[0] = 0.0
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"{self.name}_weight", self.eventweight, f"{self.name}_weight/F")
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Calculate total visible energy from all primary tracks and showers."""
        ntuple = data["gen2ntuple"]
        
        # Reset output variable
        self.eventweight[0] = ntuple.xsecWeight
        
        return {"weight":self.eventweight[0]}