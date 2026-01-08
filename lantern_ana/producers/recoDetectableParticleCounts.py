# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array


@register
class recoDetectableParticleCountsProducer(ProducerBaseClass):
    """
    Producer that find the reconstructed energy  of all electrons, muons, pions, and protons.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.protonsOverThreshold = array('i',[0])
        self.pionsOverThreshold = array('i',[0])
        self.muonsOverThreshold = array('i',[0])
        self.electronsOverThreshold = array('i',[0])

        self.muonsBarelyOverThreshold = array('i',[0])
        self.pionsBarelyOverThreshold = array('i',[0])

    def setDefaultValues(self): #Not clear what to do here?
        self.protonsOverThreshold[0] = 0
        self.pionsOverThreshold[0] = 0
        self.muonsOverThreshold[0] = 0
        self.electronsOverThreshold[0] = 0

        self.muonsBarelyOverThreshold[0] = 0
        self.pionsBarelyOverThreshold[0] = 0
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch("nProtons", self.protonsOverThreshold, "nProtons/I")
        output.Branch("nPions", self.pionsOverThreshold, "nPions/I")
        output.Branch("nMuons", self.muonsOverThreshold, "nMuons/I")
        output.Branch("nElectrons", self.electronsOverThreshold, "nElectrons/I")

        output.Branch("nJustOverMuons", self.muonsBarelyOverThreshold, "nJustOverMuons/I")
        output.Branch("nJustOverPions", self.pionsBarelyOverThreshold, "nJustOverPions/I")

    
    def requiredInputs(self):
        """Specify required inputs."""

        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]
        
        self.setDefaultValues()


        #Store the numbers of relevant particles over threshold in showers:
        for i in range(ntuple.nShowers):
            #Check for protons
            if ntuple.showerPID[i] == 2212:
                if ntuple.showerRecoE[i] >= 60:
                    self.protonsOverThreshold[0] += 1

            #Check for pions
            elif abs(ntuple.showerPID[i]) == 211:
                if ntuple.showerRecoE[i] >= 30:
                    self.pionsOverThreshold[0] += 1
                    if ntuple.showerRecoE[i] <= 45:
                        self.pionsBarelyOverThreshold[0] += 1
            
            #Check for muons
            elif ntuple.showerPID[i] == 13:
                if ntuple.showerRecoE[i] >= 100:
                    self.muonsOverThreshold[0] += 1
                    if ntuple.showerRecoE[i] <= 120:
                        self.muonsBarelyOverThreshold[0] += 1

            #Check for electrons
            elif ntuple.showerPID[i] == 11: 
                if ntuple.showerRecoE[i] >= 10:
                    self.muonsOverThreshold[0] += 1
                
        #Now we do the same for tracks:
        for i in range(ntuple.nTracks):
            #Check for protons
            if ntuple.trackPID[i] == 2212:
                if ntuple.trackRecoE[i] >= 60:
                    self.protonsOverThreshold[0] += 1

            #Check for pions
            elif abs(ntuple.trackPID[i]) == 211:
                if ntuple.trackRecoE[i] >= 30:
                    self.pionsOverThreshold[0] += 1
                    if ntuple.trackRecoE[i] <= 45:
                        self.pionsBarelyOverThreshold[0] += 1

            #Check for muons
            elif ntuple.trackPID[i] == 13:
                if ntuple.trackRecoE[i] >= 100:
                    self.muonsOverThreshold[0] += 1
                    if ntuple.trackRecoE[i] <= 120:
                        self.muonsBarelyOverThreshold[0] += 1

            #Check for electrons
            elif ntuple.trackPID[i] == 11:
                if ntuple.trackRecoE[i] >= 10:
                    self.electronsOverThreshold[0] += 1

        #Store the data as an array:
        detectableParticleDict = {"protons": self.protonsOverThreshold[0], "pions": self.pionsOverThreshold[0], "muons": self.muonsOverThreshold[0], "electrons": self.electronsOverThreshold[0], "justOverMuons": self.muonsBarelyOverThreshold[0], "justOverPions": self.pionsBarelyOverThreshold[0]}

        return detectableParticleDict

    def finalize(self):
        """
        nothing to do after the event loop
        """
        super().finalize()
        return