# lantern_ana/producers/numu_cc_producers.py
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory


@register
class VertexPropertiesProducer(ProducerBaseClass):
    """
    Producer that extracts vertex properties.

    params:
    - apply_scc: apply space charge 
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.vertex_x = array('f', [-999.0])
        self.vertex_y = array('f', [-999.0])
        self.vertex_z = array('f', [-999.0])
        self.vertex_score = array('f', [0.0])

    def setDefaultValues(self):
        super().setDefaultValues()
        self.vertex_x[0] = -999.0
        self.vertex_y[0] = -999.0
        self.vertex_z[0] = -999.0
        self.vertex_score[0] = 0.0
        
    def prepareStorage(self, output):
        """Set up branches in the output ROOT TTree."""
        output.Branch(f"{self.name}_x", self.vertex_x, f"{self.name}_x/F")
        output.Branch(f"{self.name}_y", self.vertex_y, f"{self.name}_y/F")
        output.Branch(f"{self.name}_z", self.vertex_z, f"{self.name}_z/F")
        output.Branch(f"{self.name}_score", self.vertex_score, f"{self.name}_score/F")
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Extract vertex properties."""
        ntuple = data["gen2ntuple"]
        
        # Reset output variables
        self.vertex_x[0] = -999.0
        self.vertex_y[0] = -999.0
        self.vertex_z[0] = -999.0
        self.vertex_score[0] = -1.0
        
        # If vertex found, record properties
        if ntuple.foundVertex == 1:
            self.vertex_x[0] = ntuple.vtxX
            self.vertex_y[0] = ntuple.vtxY
            self.vertex_z[0] = ntuple.vtxZ
            self.vertex_score[0] = ntuple.vtxScore
        
        return {
            "x": self.vertex_x[0],
            "y": self.vertex_y[0],
            "z": self.vertex_z[0],
            "score": self.vertex_score[0]
        }

