# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array


@register
class backgroundClassifyingProducer(ProducerBaseClass):
    """
    Producer that produces our graphing variables based on data
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        #Vertex variables:
        self.VertexFound = array('i',[0])
        self.inFiducial = array('i',[0])
        

        #Cosmic cut variables:
        self.cosmicFraction = array('f',[0])
        self.fracUnreconstructedPixels = array('f',[0])
        self.photonFromCharged = array('f',[0])


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

        self.sinkhornDiv[0] = array('i',[0])
        self.observedPE[0] = array('i',[0])

        #Reco success (ie. was the reco correct? Was the event in a different sideband?)
        self.isBackground = array('i',[0])
        self.isWrongSideband = array('i',[0])
        self.isSignal = array('i',[0])

        #Reco backgrounds - that is, what type of background we reconstruct the event in
        self.outOfFiducial = array('i',[0])
        self.cosmicFracCut = array('i',[0])
        self.unReconstructedPixelCut = array('i',[0])
        self.photonFromChargedCut = array('i',[0])
        self.overThresholdMuon = array('i',[0])
        self.manyJustOverMuons = array('i',[0])
        self.overThresholdElectron = array('i',[0])
        self.overThresholdPion = array('i',[0])
        self.tooManyProtons = array('i',[0])
        self.noPhotons = array('i',[0])
        self.manyPhotons = array('i',[0])

        #True backgrounds:
        #True background categories
        self.noVertex = array('i',[0])
        self.trueOverThresholdMuon = array('i',[0])
        self.trueManyJustOverMuons = array('i',[0])
        self.trueOverThresholdElectron = array('i',[0])
        self.trueOverThresholdPion = array('i',[0])
        self.trueTooManyProtons = array('i',[0])
        self.trueNoPhotons = array('i',[0])
        self.trueManyPhotons = array('i',[0])


        #Background tags, for later
        self.trueBackground = array('i',[0])
        self.recoBackground = array('i',[0])




    def setDefaultValues(self):
        self.VertexFound[0] = 0
        self.inFiducial[0] = 0
        self.cosmicFraction[0] = 0
        self.fracUnreconstructedPixels[0] = 0
        self.photonFromCharged[0] = 0

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

        #Reco background categories - that is, what sideband we reconstruct the event in
        self.noVertex[0] = 0
        self.outOfFiducial[0] = 0
        self.cosmicFracCut[0] = 0
        self.unReconstructedPixelCut[0] = 0
        self.photonFromChargedCut[0] = 0
        self.overThresholdMuon[0] = 0
        self.manyJustOverMuons[0] = 0
        self.overThresholdElectron[0] = 0
        self.overThresholdPion[0] = 0
        self.tooManyProtons[0] = 0
        self.noPhotons[0] = 0
        self.manyPhotons[0] = 0

        #True background categories
        self.trueOverThresholdMuon[0] = 0
        self.trueManyJustOverMuons[0] = 0
        self.trueOverThresholdElectron[0] = 0
        self.trueOverThresholdPion[0] = 0
        self.trueTooManyProtons[0] = 0
        self.trueNoPhotons[0] = 0
        self.trueManyPhotons[0] = 0


        self.trueBackground[0] = 0
        self.recoBackground[0] = 0



    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        #Assign reco background categories
        output.Branch("noVertex", self.noVertex, "noVertex/I")
        output.Branch("outOfFiducial", self.outOfFiducial, "outOfFiducial/I")
        output.Branch("cosmicFracCut", self.cosmicFracCut, "cosmicFracCut/I")
        output.Branch("unReconstructedPixelCut", self.unReconstructedPixelCut, "overThresholdMuon/I")
        output.Branch("photonFromChargedCut", self.photonFromChargedCut, "overThresholdMuon/I")
        output.Branch("overThresholdMuon", self.overThresholdMuon, "overThresholdMuon/I")
        output.Branch("manyJustOverMuons", self.manyJustOverMuons, "manyJustOverMuons/I")
        output.Branch("overThresholdElectron", self.overThresholdElectron, "overThresholdElectron/I")
        output.Branch("overThresholdPion", self.overThresholdPion, "overThresholdPion/I")
        output.Branch("tooManyProtons", self.tooManyProtons, "tooManyProtons/I")
        output.Branch("noPhotons", self.noPhotons, "noPhotons/I")
        output.Branch("manyPhotons", self.manyPhotons, "manyPhotons/I")

        #Assign true background categories
        output.Branch("trueOverThresholdMuon", self.trueOverThresholdMuon, "trueOverThresholdMuon/I")
        output.Branch("trueManyJustOverMuons", self.trueManyJustOverMuons, "trueManyJustOverMuons/I")
        output.Branch("trueOverThresholdElectron", self.trueOverThresholdElectron, "trueOverThresholdElectron/I")
        output.Branch("trueOverThresholdPion", self.trueOverThresholdPion, "trueOverThresholdPion/I")
        output.Branch("trueTooManyProtons", self.trueTooManyProtons, "trueTooManyProtons/I")
        output.Branch("trueNoPhotons", self.trueNoPhotons, "trueNoPhotons/I")
        output.Branch("trueManyPhotons", self.trueManyPhotons, "trueManyPhotons/I")

    
    def requiredInputs(self):
        """Specify required inputs."""
        
        return ["gen2ntuple", 
            "photon_data", 
            "detectable_particle_data",
            "true_photon_data", 
            "true_detectable_particle_data",
            "event_categorizer"
            ]
        

    def processEvent(self, data, params):
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]
        
        self.setDefaultValues()

        #First we get relevant data from other producers:
        vertexData = data.get("vertex_properties", {})
        recoPhotonData = data.get("photon_data", {})
        recoParticleData = data.get("detectable_particle_data", {})
        truePhotonData = data.get("true_photon_data", {})
        trueParticleData = data.get("true_detectable_particle_data", {})
        categoryData = data.get("event_categorizer", {})

        #Now we extract the values from those data:
        self.VertexFound[0] = vertexData["found"]
        self.cosmicFraction[0] = vertexData["cosmicfrac"]
        self.fracUnreconstructedPixels[0] = vertexData["frac_intime_unreco_pixels"]
        self.photonFromCharged[0] = recoPhotonData["photonFromCharged"]

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

        self.recoBackground[0] = categoryData["recoBackground"]
        self.trueBackground[0] = categoryData["trueBackground"]
        self.inFiducial[0] = categoryData["inFiducial"]


        #Now we filter out events reconstructed as background:
        if self.recoBackground[0] == 1:
            if self.VertexFound[0] != 1:
                self.noVertex[0] = 1

            elif self.inFiducial[0] != 1:
                self.outOfFiducial[0] = 1

            elif self.cosmicFraction[0] > 0.15:
                self.cosmicFracCut[0] = 1

            elif self.fracUnreconstructedPixels[0] > 0.9:
                self.unReconstructedPixelCut[0] = 1

            elif self.recoMuonCount[0] > self.recoJustOverMuons[0]:
                self.overThresholdMuon[0] = 1

            elif self.recoJustOverMuons[0] > 1:
                self.manyJustOverMuons[0] = 1
            
            elif self.recoElectronCount[0] > 0:
                self.overThresholdElectron[0] = 1
        
            elif self.recoPionCount[0] > self.recoJustOverPions[0]:
                self.overThresholdPion[0] = 1

            elif self.recoProtonCount[0] > 2:
                self.tooManyProtons[0] = 1
            
            elif self.recoPhotonCount[0] > 2:
                self.noPhotons[0] = 1
        
            elif self.recoPhotonCount[0] == 0:
                self.manyPhotons[0] = 1
            
            elif self.photonFromCharged[0] < 5:
                self.photonFromChargedCut[0] = 1



        #MC ONLY: Determine if the event is background based on disqualifying values:
        #Ignore files that aren't Montecarlo:
        ismc = params.get('ismc',False)
        if ismc and self.trueBackground[0] == 1:
            if self.trueMuonCount[0] > self.trueJustOverMuons[0]:
                self.trueOverThresholdMuon[0] = 1
         
            elif self.trueMuonCount[0] > 1:
                self.trueManyJustOverMuons[0] = 1
                
            elif self.trueElectronCount[0] != 0:
                self.trueOverThresholdElectron[0] = 1

            elif self.trueProtonCount[0] > 2:
               self.trueTooManyProtons[0] = 1

            elif self.truePionCount[0] > self.trueJustOverPions[0]:
                self.trueOverThresholdPion[0] = 1
                
            elif self.truePhotonCount[0] == 0:
                self.trueNoPhotons[0] = 1
                
            elif self.truePhotonCount[0] > 2:
                self.trueManyPhotons[0] = 1



        return {"Outcome": 0}