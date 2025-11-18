# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array


@register
class oneGxPSignalTagProducer(ProducerBaseClass):
    """
    Producer that find the reconstructed energy  of all electrons, muons, pions, and protons.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.recoPhotonCount = array('i',[0])
        self.truePhotonCount = array('i',[0])
        self.recoProtonCount = array('i',[0])
        self.trueProtonCount = array('i',[0])

        #Sideband particles:
        self.recoJustOverMuons = array('i',[0])
        self.trueJustOverMuons = array('i',[0])
        self.recoJustOverPions = array('i',[0])
        self.trueJustOverPions = array('i',[0])

        #Disqualifying Particles:
        self.recoMuonCount = array('i',[0])
        self.recoPionCount = array('i',[0])
        self.recoElectronCount = array('i',[0])
        self.trueMuonCount = array('i',[0])
        self.truePionCount = array('i',[0])
        self.trueElectronCount = array('i',[0])

        #Reco success (ie. was the reco correct? Was the event in a different sideband?)
        self.isFound = array('i',[0])
        self.isMissed = array('i',[0])
        self.isMisclassified = array('i',[0])

        #Reco categories - that is, what sideband we reconstruct the event in
        self.oneGnoX = array('i',[0])
        self.oneGoneP = array('i',[0])
        self.oneGtwoP = array('i',[0])
        self.oneGoneMu = array('i',[0])
        self.oneGxPi = array('i',[0])
        self.twoGnoX = array('i',[0])
        self.twoGoneP = array('i',[0])
        self.twoGtwoP = array('i',[0])
        self.twoGoneMu = array('i',[0])
        self.twoGxPi = array('i',[0])
        self.onePhotonInclusive = array('i',[0])
        self.twoPhotonInclusive = array('i',[0])

        #Reasons for misses
        self.noPhotonsFound = array('i',[0])
        self.extraPhotonFound = array('i',[0])
        self.wrongMuon = array('i',[0])
        self.wrongOtherParticle = array('i',[0]) #ie. anything other than muons


    def setDefaultValues(self):
        self.recoPhotonCount[0] = 0
        self.truePhotonCount[0] = 0
        self.recoProtonCount[0] = 0
        self.trueProtonCount[0] = 0

        #Sideband particles:
        self.recoJustOverMuons[0] = 0
        self.trueJustOverMuons[0] = 0
        self.recoJustOverPions[0] = 0
        self.trueJustOverPions[0] = 0

        #Disqualifying Particles:
        self.recoMuonCount[0] = 0
        self.recoPionCount[0] = 0
        self.recoElectronCount[0] = 0

        self.trueMuonCount[0] = 0
        self.truePionCount[0] = 0
        self.trueElectronCount[0] = 0

        self.isFound[0] = 0
        self.isMissed[0] = 0
        self.isMisclassified[0] = 0

        self.noPhotonsFound[0] = 0
        self.extraPhotonFound[0] = 0
        self.wrongMuon[0] = 0
        self.wrongOtherParticle[0] = 0

        self.onePhotonInclusive[0] = 0
        self.twoPhotonInclusive[0] = 0


        self.oneGnoX[0] = 0
        self.oneGoneP[0] = 0
        self.oneGtwoP[0] = 0
        self.oneGoneMu[0] = 0
        self.oneGxPi[0] = 0
        self.twoGnoX[0] = 0
        self.twoGoneP[0] = 0
        self.twoGtwoP[0] = 0
        self.twoGoneMu[0] = 0
        self.twoGxPi[0] = 0

    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch("trueOneGnoX", self.oneGnoX, "trueOneGnoX/I")
        output.Branch("trueOneGoneP", self.oneGoneP, "trueOneGoneP/I")
        output.Branch("trueOneGtwoP", self.oneGtwoP, "trueOneGtwoP/I")
        output.Branch("trueOneGoneMu", self.oneGoneMu, "trueOneGoneMu/I")
        output.Branch("trueOneGxPi", self.oneGxPi, "trueOneGxPi/I")

        output.Branch("trueTwoGnoX", self.twoGnoX, "trueTwoGnoX/I")
        output.Branch("trueTwoGoneP", self.twoGoneP, "trueTwoGoneP/I")
        output.Branch("trueTwoGtwoP", self.twoGtwoP, "trueTwoGtwoP/I")
        output.Branch("trueTwoGoneMu", self.twoGoneMu, "trueTwoGoneMu/I")
        output.Branch("trueTwoGxPi", self.twoGxPi, "trueTwoGxPi/I")

        output.Branch("isFound", self.isFound, "isFound/I")
        output.Branch("isMissed", self.isMissed, "isMissed/I")
        output.Branch("isMisclassified", self.isMisclassified, "isMisclassified/I")

        output.Branch("onePhotonInclusive", self.onePhotonInclusive, "onePhotonInclusive/I")
        output.Branch("twoPhotonInclusive", self.twoPhotonInclusive, "twoPhotonInclusive/I")

        output.Branch("noPhotonsFound", self.noPhotonsFound, "noPhotonsFound/I")
        output.Branch("tooManyPhotonsFound", self.extraPhotonFound, "tooManyPhotonsFound/I")
        output.Branch("wrongMuon", self.wrongMuon, "wrongMuon/I")
        output.Branch("wrongOtherParticle", self.wrongOtherParticle, "wrongOtherParticle/I")

        
    
    def requiredInputs(self):
        """Specify required inputs."""
        
        return ["gen2ntuple", "true_photon_data", "true_detectable_particle_data"]
        

    def processEvent(self, data, params):
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]
        
        self.setDefaultValues()

        ismc = params.get('ismc',False)
        if not ismc:
            return {"outcome":0}

        #First we get relevant data from other producers:
        recoPhotonData = data.get("photon_data", {})
        recoParticleData = data.get("detectable_particle_data", {})
        truePhotonData = data.get("true_photon_data", {})
        trueParticleData = data.get("true_detectable_particle_data", {})

        #Now we extract the values from those data:
        self.recoPhotonCount[0] = recoPhotonData["nphotons"]
        self.truePhotonCount[0] = truePhotonData["ntruePhotons"]
        self.recoProtonCount[0] = recoParticleData["protons"]
        self.trueProtonCount[0] = trueParticleData["protons"]

        #Sideband particles:
        self.recoJustOverMuons[0] = recoParticleData["justOverMuons"]
        self.trueJustOverMuons[0] = trueParticleData["justOverMuons"]
        self.recoJustOverPions[0] = recoParticleData["justOverPions"]
        self.trueJustOverPions[0] = trueParticleData["justOverPions"]

        #Disqualifying Particles:
        self.trueMuonCount[0] = trueParticleData["muons"]
        self.truePionCount[0] = trueParticleData["pions"]
        self.trueElectronCount[0] = trueParticleData["electrons"]
        self.recoMuonCount[0] = recoParticleData["muons"]
        self.recoPionCount[0] = recoParticleData["pions"]
        self.recoElectronCount[0] = recoParticleData["electrons"]


        #Ensure that the particle contains no disqualifying particles:
        if (self.trueMuonCount[0] > self.trueJustOverMuons[0] or self.trueMuonCount[0] > 1
                or self.trueElectronCount[0] != 0
                or self.trueProtonCount[0] > 2
                or self.truePionCount[0] > self.trueJustOverPions[0]):
            return {"Result":0}
        
        #Next we determine what sideband the particle belongs to:
        #tagList = [self.oneGnoX[0], self.oneGoneP[0], self.oneGtwoP[0], self.oneGoneMu[0], self.oneGxPi[0], self.twoGnoX[0], self.twoGoneP[0], self.twoGtwoP[0], self.twoGoneMu[0], self.twoGxPi[0]]
        #SIDEBANDS WITH ONE PHOTON
        if self.truePhotonCount[0] == 1:
            self.onePhotonInclusive[0] = 1
            if (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.oneGnoX[0] = 1 #One photon, nothing else

            elif (self.trueProtonCount[0] == 1 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.oneGoneP[0] = 1 #One photon, one proton, nothing else

            elif (self.trueProtonCount[0] == 2 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.oneGtwoP[0] = 1 #One photon, two protons, nothing else

            elif (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 1 
                    and self.trueJustOverPions[0] == 0):
                self.oneGoneMu[0] = 1 #One photon, one muon between 100 MeV and 120 MeV, nothing else

            elif (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] > 0):
                self.oneGxPi[0] = 1 #One photon, X pions between 30 and 45 MeV, nothing else

        #SIDEBANDS WITH TWO PHOTONS
        elif self.truePhotonCount[0] == 2:
            self.twoPhotonInclusive[0] = 1
            if (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.twoGnoX[0] = 1 #Two photons, nothing else

            elif (self.trueProtonCount[0] == 1 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.twoGoneP[0] = 1 #Two photons, one proton, nothing else

            elif (self.trueProtonCount[0] == 2 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.twoGtwoP[0] = 1 #Two photons, two protons nothing else

            elif (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 1 
                    and self.trueJustOverPions[0] == 0):
                self.twoGoneMu[0] = 1 #Two photons, one muon between 100 and 120 MeV, nothing else

            elif (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] > 0):
                self.twoGxPi[0] = 1 #Two photons, X pions between 30 and 45 MeV, nothing else

        #print(tagList, self.recoPhotonCount, self.truePhotonCount)

        if self.recoMuonCount[0] > self.recoJustOverMuons[0] or self.recoJustOverMuons[0] > 1:
            self.isMissed[0] = 1
            self.wrongMuon[0] = 1

        elif self.recoElectronCount[0] > 0 or self.recoPionCount[0] > self.recoJustOverPions[0] or self.recoProtonCount[0] > 2:
            self.isMissed[0] = 1
            self.wrongOtherParticle[0] = 1

        elif self.recoPhotonCount[0] > 2:
            self.isMissed[0] = 1
            self.extraPhotonFound[0] = 1
        
        elif self.recoPhotonCount[0] == 0:
            self.isMissed[0] = 1
            self.noPhotonsFound[0] = 1

        #If it's not background, determine if we got all of our counts right:
        elif (self.truePhotonCount[0] != self.recoPhotonCount[0]
                or self.trueProtonCount[0] != self.recoProtonCount[0]
                or self.trueJustOverPions[0] != self.recoJustOverPions[0]
                or self.trueJustOverMuons[0] != self.recoJustOverMuons[0]
                or self.trueMuonCount[0] != self.recoMuonCount[0]):
            self.isMisclassified[0] = 1
            
        #If our counts are right and it's not background, it must be signal
        else:
            self.isFound[0] = 1

        #print(self.isMissed, self.isMisclassified, self.isFound)

        return {"Result":0}

    def finalize(self):
        """
        nothing to do after the event loop
        """
        super().finalize()
        return