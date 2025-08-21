# lantern_ana/producers/numu_cc_producers.py
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register

@register
class CutResultProducer(ProducerBaseClass):
    """
    Producer that passes cut result to the treaa.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.cut_result = array('i', [0])
        self.cut_name = config.get('cutname',None)
        if self.cut_name is None:
            raise ValueError(f'must specify cutname in CutResultProducer[{self.name}]')
        if self.cut_name==name:
            raise ValueError('Name of CutResultProducer instance cannot match the name of the cut (e.g. add _prod to name).')

    def setDefaultValues(self):
        super().setDefaultValues()
        self.cut_result[0] = 0
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"{self.cut_name}_cutresult", self.cut_result, f"{self.cut_name}_cutresult/I")
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple",self.cut_name]
    
    def processEvent(self, data, params):
        """Calculate total visible energy from all primary tracks and showers."""

        self.cut_result[0] = 0
        result = data.get(self.cut_name,None)
        if type(result) is not bool:
            raise TypeError(f"Cut result for name={self.cut_name} is not boolean as required: {result}")
        
        if result:
            self.cut_result[0] = 1
        
        return self.cut_result[0]
