# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array


@register
class oneGxPEventSortingProducer(ProducerBaseClass):
    """
    Producer that find the reconstructed energy  of all electrons, muons, pions, and protons.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        #Central particles:
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
        self.isBackground = array('i',[0])
        self.isWrongSideband = array('i',[0])
        self.isSignal = array('i',[0])

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

        #Background tags - explain why the event is background
        self.overThresholdMuon = array('i',[0])
        self.tooManyProtons = array('i',[0])
        self.overThresholdElectron = array('i',[0])
        self.overThresholdPion = array('i',[0])
        self.noPhotons = array('i',[0])
        self.tooManyPhotons = array('i',[0])

        #Mixup tags - what sideband should the event have been in?
        #self.notOneGnoX = array('i',[0])
        #self.notOneGoneP = array('i',[0])
        #self.notOneGtwoP = array('i',[0])
        #self.notOneGoneMu = array('i',[0])
        #self.notOneGxPi = array('i',[0])
        #self.notTwoGnoX = array('i',[0])
        #self.notTwoGoneP = array('i',[0])
        #self.notTwoGtwoP = array('i',[0])
        #self.notTwoGoneMu = array('i',[0])
        #self.notTwoGxPi = array('i',[0])


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

        #Reco success (ie. was the reco correct? Was the event in a different sideband?)
        self.isBackground[0] = 0
        self.isWrongSideband[0] = 0
        self.isSignal[0] = 0

        #Reco categories - that is, what sideband we reconstruct the event in
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

        self.overThresholdMuon[0] = 0
        self.tooManyProtons[0] = 0
        self.overThresholdElectron[0] = 0
        self.overThresholdPion[0] = 0
        self.noPhotons[0] = 0
        self.tooManyPhotons[0] = 0

    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch("oneGnoX", self.oneGnoX, "oneGnoX/I")
        output.Branch("oneGoneP", self.oneGoneP, "oneGoneP/I")
        output.Branch("oneGtwoP", self.oneGtwoP, "oneGtwoP/I")
        output.Branch("oneGoneMu", self.oneGoneMu, "oneGoneMu/I")
        output.Branch("oneGxPi", self.oneGxPi, "oneGxPi/I")

        output.Branch("twoGnoX", self.twoGnoX, "twoGnoX/I")
        output.Branch("twoGoneP", self.twoGoneP, "twoGoneP/I")
        output.Branch("twoGtwoP", self.twoGtwoP, "twoGtwoP/I")
        output.Branch("twoGoneMu", self.twoGoneMu, "twoGoneMu/I")
        output.Branch("twoGxPi", self.twoGxPi, "twoGxPi/I")

        output.Branch("isBackground", self.isBackground, "isBackground/I")
        output.Branch("isWrongSideband", self.isWrongSideband, "isWrongSideband/I")
        output.Branch("isSignal", self.isSignal, "isSignal/I")

        output.Branch("overThresholdMuon", self.overThresholdMuon, "overThresholdMuon/I")
        output.Branch("tooManyProtons", self.tooManyProtons, "tooManyProtons/I")
        output.Branch("overThresholdElectron", self.overThresholdElectron, "overThresholdElectron/I")
        output.Branch("overThresholdPion", self.overThresholdPion, "overThresholdPion/I")
        output.Branch("noPhotons", self.noPhotons, "noPhotons/I")
        output.Branch("tooManyPhotons", self.tooManyPhotons, "tooManyPhotons/I")


    
    def requiredInputs(self):
        """Specify required inputs."""
        
        return ["gen2ntuple", "photon_data", "detectable_particle_data", "true_photon_data", "true_detectable_particle_data"]
        

    def processEvent(self, data, params):
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]
        
        self.setDefaultValues()

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

        #Now we filter out events reconstructed as background:
        if (self.recoMuonCount[0] > self.recoJustOverMuons[0] 
                or self.recoJustOverMuons[0] > 1 
                or self.recoElectronCount[0] > 0 
                or self.recoPionCount[0] > self.recoJustOverPions[0] 
                or self.recoProtonCount[0] > 2 
                or self.recoPhotonCount[0] > 2 
                or self.recoPhotonCount[0] == 0):

            return {"outcome":0}

        #Next we determine what sideband the particle belongs to:
        #SIDEBANDS WITH ONE PHOTON
        if self.recoPhotonCount[0] == 1:
            if (self.recoProtonCount[0] == 0 
                    and self.recoJustOverMuons[0] == 0 
                    and self.recoJustOverPions[0] == 0):
                self.oneGnoX[0] = 1 #One photon, nothing else

            elif (self.recoProtonCount[0] == 1 
                    and self.recoJustOverMuons[0] == 0 
                    and self.recoJustOverPions[0] == 0):
                self.oneGoneP[0] = 1 #One photon, one proton, nothing else

            elif (self.recoProtonCount[0] == 2 
                    and self.recoJustOverMuons[0] == 0 
                    and self.recoJustOverPions[0] == 0):
                self.oneGtwoP[0] = 1 #One photon, two protons, nothing else

            elif (self.recoProtonCount[0] == 0 
                    and self.recoJustOverMuons[0] == 1 
                    and self.recoJustOverPions[0] == 0):
                self.oneGoneMu[0] = 1 #One photon, one muon between 100 MeV and 120 MeV, nothing else

            elif (self.recoProtonCount[0] == 0 
                    and self.recoJustOverMuons[0] == 0 
                    and self.recoJustOverPions[0] > 0):
                self.oneGxPi[0] = 1 #One photon, X pions between 30 and 45 MeV, nothing else

        #SIDEBANDS WITH TWO PHOTONS
        elif self.recoPhotonCount[0] == 2:

            if (self.recoProtonCount[0] == 0 
                    and self.recoJustOverMuons[0] == 0 
                    and self.recoJustOverPions[0] == 0):
                self.twoGnoX[0] = 1 #Two photons, nothing else

            elif (self.recoProtonCount[0] == 1 
                    and self.recoJustOverMuons[0] == 0 
                    and self.recoJustOverPions[0] == 0):
                self.twoGoneP[0] = 1 #Two photons, one proton, nothing else

            elif (self.recoProtonCount[0] == 2 
                    and self.recoJustOverMuons[0] == 0 
                    and self.recoJustOverPions[0] == 0):
                self.twoGtwoP[0] = 1 #Two photons, two protons nothing else

            elif (self.recoProtonCount[0] == 0 
                    and self.recoJustOverMuons[0] == 1 
                    and self.recoJustOverPions[0] == 0):
                self.twoGoneMu[0] = 1 #Two photons, one muon between 100 and 120 MeV, nothing else

            elif (self.recoProtonCount[0] == 0 
                    and self.recoJustOverMuons[0] == 0 
                    and self.recoJustOverPions[0] > 0):
                self.twoGxPi[0] = 1 #Two photons, X pions between 30 and 45 MeV, nothing else

        #MC ONLY: Determine if the event is background based on disqualifying values:
        #Ignore files that aren't Montecarlo:
        ismc = params.get('ismc',False)
        if ismc:
            if self.trueMuonCount[0] > self.trueJustOverMuons[0] or self.trueJustOverMuons[0] > 1:
                self.isBackground[0] = 1
                self.overThresholdMuon[0] = 1

            elif self.trueElectronCount[0] > 0:
                self.isBackground[0] = 1
                self.overThresholdElectron[0] = 1

            elif self.truePionCount[0] > self.trueJustOverPions[0]:
                self.isBackground[0] = 1
                self.overThresholdPion[0] = 1

            elif self.trueProtonCount[0] > 2:
                self.isBackground[0] = 1
                self.tooManyProtons[0] = 1

            elif self.truePhotonCount[0] > 2:
                self.isBackground[0] = 1
                self.tooManyPhotons[0] = 1

            elif self.truePhotonCount[0] == 0:
                self.isBackground[0] = 1
                self.noPhotons[0] = 1

            #If it's not background, determine if we got all of our counts right:
            elif (self.truePhotonCount[0] != self.recoPhotonCount[0]
                    or self.trueProtonCount[0] != self.recoProtonCount[0]
                    or self.trueJustOverPions[0] != self.recoJustOverPions[0]
                    or self.trueJustOverMuons[0] != self.recoJustOverMuons[0]):
                self.isWrongSideband[0] = 1
                #print("NEW EVENT FAILS SIDEBAND:")
                #if self.truePhotonCount[0] != self.recoPhotonCount[0]:
                #    print("Photon count incorrect:", self.truePhotonCount[0], "true vs", self.recoPhotonCount[0], "reco.")
                #if self.trueProtonCount[0] != self.recoProtonCount[0]:
                #    print("Proton count incorrect:", self.trueProtonCount[0], "true vs", self.recoProtonCount[0], "reco.")
                #if self.trueJustOverPions[0] != self.recoJustOverPions[0]:
                #    print("Pion count incorrect:", self.truePionCount[0], "true vs", self.recoPionCount[0], "reco.")
                #if self.trueJustOverMuons[0] != self.recoJustOverMuons[0]:
                #    print("Muon count incorrect:", self.trueMuonCount[0], "true vs", self.recoMuonCount[0], "reco.")


            #If our counts are right and it's not background, it must be signal
            else:
                self.isSignal[0] = 1

        return {"Result":0}


        {"Key": value, "key"}