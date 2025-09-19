# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array
import sys

@register
class runSubrunProducer(ProducerBaseClass):
    """
    Producer that tracks the location and energy of all photons.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        #We get these variables from the config
        self.event = array('i',[0])
        self.run = array('i',[0])
        self.subrun = array('i',[0])

    def setDefaultValues(self): #Not clear what to do here?
        self.event[0] = 0
        self.run[0] = 0
        self.subrun[0] = 0


    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"event", self.event, f"event/I")
        output.Branch(f"run", self.run, f"run/I")
        output.Branch(f"subrun", self.subrun, f"subrun/I")

    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):        
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]

        # Simply store the event, run, and subrun for each event
        self.event[0] = ntuple.event
        self.run[0] = ntuple.run
        self.subrun[0] = ntuple.subrun

        returnDict = {"event":self.event[0], "run":self.run[0], "subrun":self.subrun[0]}

        #print(returnDict)

        return returnDict