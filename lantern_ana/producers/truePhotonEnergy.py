# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array
import sys

@register
class truePhotonEnergyProducer(ProducerBaseClass):
    """
    Producer that tracks the location and energy of all photons.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        #We get these variables from the config
        self._maxnphotons = 20

        #These variables are what we're interested in passing to the ntuple
        self.nTruePhotons = array('i',[0]) #This tells us if the event is useful for our analysis
        self.nMatchedPhotons = array('i',[0])

        #These variables are just for other producers
        self.matchedPhotonEnergiesTrue = array('f',[0.0]*self._maxnphotons)
        self.matchedPhotonEnergiesVisible = array('f',[0.0]*self._maxnphotons)

    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"nMatchedPhotons", self.nMatchedPhotons, f"nMatchedPhotons/I")
        output.Branch(f"matchedPhotonEnergiesTrue", self.matchedPhotonEnergiesTrue, f"matchedPhotonEnergiesTrue[{self._maxnphotons}]/F")
        output.Branch(f"matchedPhotonEnergiesVisible", self.matchedPhotonEnergiesVisible, f"matchedPhotonEnergiesVisible[{self._maxnphotons}]/F")

        
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]

    def setDefaultValues(self): #Not clear what to do here?
        self.nMatchedPhotons[0] = 0
        for x in range(20):
            self.matchedPhotonEnergiesTrue[x] = -1.0
            self.matchedPhotonEnergiesVisible[x] = -1.0
    
    def processEvent(self, data, params):        
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]

        #Only run this on Montecarlo files
        ismc = params.get('ismc',False)
        if not ismc:
            truePhotonEnergyDict = {}
            return truePhotonEnergyDict


        # Find and store data on showers ID'd as photons

        #Set/Reset Variables
        numPhotons = 0
        self.setDefaultValues()
 
        for i in range(ntuple.nShowers):
            #Find true photons
            if ntuple.showerTruePID[i] == 22:
                photonTID = ntuple.showerTrueTID[i]
                for x in range(ntuple.nTrueSimParts):
                    if ntuple.trueSimPartTID[x] == photonTID:
                        self.matchedPhotonEnergiesVisible[numPhotons] = ntuple.showerRecoE[i]
                        self.matchedPhotonEnergiesTrue[numPhotons] = ntuple.trueSimPartE[x]
                        numPhotons += 1

        for i in range(ntuple.nTracks):
            #Find true photons
            if ntuple.trackTruePID[i] == 22:
                photonTID = ntuple.trackTrueTID[i]
                for x in range(ntuple.nTrueSimParts):
                    if ntuple.trueSimPartTID[x] == photonTID:
                        self.matchedPhotonEnergiesVisible[numPhotons] = ntuple.trackRecoE[i]
                        self.matchedPhotonEnergiesTrue[numPhotons] = ntuple.trueSimPartE[x]
                        numPhotons += 1

        #Store the data as a dictionary:
        truePhotonEnergyDict = {}

        return truePhotonEnergyDict