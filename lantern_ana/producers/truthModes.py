# lantern_ana/producers/numu_cc_producers.py
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory

@register
class TruthModeProducer(ProducerBaseClass):
    """
    Producer that applies truth mode tagging to events.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.truth_mode = ROOT.std.string()
        self.tag_factory = TagFactory()
        
        # Add the truth mode tag with given parameters
        tag_params = config.get('tag_params', {})
        self.tag_factory.add_tag('tag_truth_finalstate_mode', tag_params)
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"{self.name}", self.truth_mode)
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Apply truth mode tagging."""
        ntuple = data["gen2ntuple"]
        
        # Reset output variable
        self.truth_mode.clear()
        
        # Apply tags
        event_tags = self.tag_factory.apply_tags(ntuple)
        
        # If tags found, concatenate them
        if event_tags:
            self.truth_mode.assign(",".join(event_tags))
        else:
            self.truth_mode.assign("unknown")
        
        return self.truth_mode