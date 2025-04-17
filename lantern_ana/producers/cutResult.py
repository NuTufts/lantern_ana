# lantern_ana/producers/numu_cc_producers.py
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register

@register
class cutResultProducer(ProducerBaseClass):
    """
    Producer that passes cut result to the treaa.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.cut_result = array('i', [0])
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"{self.name}_cutresult", self.cut_result, f"{self.name}_cutresult/I")
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Calculate total visible energy from all primary tracks and showers."""

        self.cut_result[0] = 0
        result = data.get(self.name,False)
        if type(result) is not bool:
            raise TypeError(f"Cut result for name={self.name} is not boolean as required.")
        
        if result:
            self.cut_result[0] = 1
        
        return self.cut_result[0]
