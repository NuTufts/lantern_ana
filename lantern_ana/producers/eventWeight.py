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
        self.eventweight = array('f', [1.0])
        self.goodweight  = array('i', [1])
        
        self.use_friendtree = config.get('use_friendtree',False)
        self.weight_branch  = config.get('weight_branch', 'xsecWeight' )        

    def setDefaultValues(self):
        super().setDefaultValues()
        self.eventweight[0] = 1.0
        self.goodweight[0] = 1
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"{self.name}_weight", self.eventweight, f"{self.name}_weight/F")
        output.Branch(f"{self.name}_weight_isgood", self.goodweight, f"{self.name}_weight_isgood/I")        
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Calculate total visible energy from all primary tracks and showers."""
        self.setDefaultValues()
        ismc = params.get('ismc',False)
        if not ismc:
            return {"weight":self.eventweight[0],"weight_is_good":self.goodweight[0]}

        ntuple = data["gen2ntuple"]
        
        self.eventweight[0] = eval( f'ntuple.{self.weight_branch}' )

        #Remove events with infinite event weights
        if self.eventweight[0] > 100000000000000 or self.eventweight[0]<0.0:
            self.eventweight[0] = 1.0
            self.goodweight[0]  = 0
        
        return {"weight":self.eventweight[0],"weight_is_good":self.goodweight[0]}

    def finalize(self):
        """ Nothing to do after event loop. """
        return
