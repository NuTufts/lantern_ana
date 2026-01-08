# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array


@register
class oneGxPEventCategorizingProducer(ProducerBaseClass):
    """
    Producer that produces our graphing variables based on data
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        #Vertex variables:
        self.VertexFound = array('i',[0])
        self.inFiducial = array('i',[0])
        self.fiducial = config.get('fiducialData', {"xMin":0, "xMax":256, "yMin":-116.5, "yMax":116.5, "zMin":0, "zMax":1036, "width":0})
        self.flashPred = config.get('flashpred')

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

        self.sinkhornDiv = array('f',[0])
        self.observedPE = array('f',[0])
        self.minComp = array('f',[0])

        #Reco success (ie. was the reco correct? Was the event in a different sideband?)
        self.isBackground = array('i',[0])
        self.isWrongSideband = array('i',[0])
        self.isSignal = array('i',[0])

        #Reco categories - that is, what sideband we reconstruct the event in
        self.suspectedCosmic = array('i',[0])
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

        #True categories
        self.oneGnoXtrue = array('i',[0])
        self.oneGonePtrue = array('i',[0])
        self.oneGtwoPtrue = array('i',[0])
        self.oneGoneMutrue = array('i',[0])
        self.oneGxPitrue = array('i',[0])
        self.twoGnoXtrue = array('i',[0])
        self.twoGonePtrue = array('i',[0])
        self.twoGtwoPtrue = array('i',[0])
        self.twoGoneMutrue = array('i',[0])
        self.twoGxPitrue = array('i',[0])

        #Background tags, for later
        self.trueBackground = array('i',[0])
        self.recoBackground = array('i',[0])

        #Inclusive tags
        self.trueOnePhotonInclusive = array('i',[0])
        self.trueTwoPhotonInclusive = array('i',[0])
        self.recoOnePhotonInclusive = array('i',[0])
        self.recoTwoPhotonInclusive = array('i',[0])


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
        self.sinkhornDiv[0] = 0
        self.observedPE[0] = 0

        self.trueMuonCount[0] = 0
        self.truePionCount[0] = 0
        self.trueElectronCount[0] = 0
        
        self.minComp[0] = 9999

        #Reco categories - that is, what sideband we reconstruct the event in
        self.suspectedCosmic[0] = 0

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

        self.oneGnoXtrue[0] = 0
        self.oneGonePtrue[0] = 0
        self.oneGtwoPtrue[0] = 0
        self.oneGoneMutrue[0] = 0
        self.oneGxPitrue[0] = 0
        self.twoGnoXtrue[0] = 0
        self.twoGonePtrue[0] = 0
        self.twoGtwoPtrue[0] = 0
        self.twoGoneMutrue[0] = 0
        self.twoGxPitrue[0] = 0

        self.trueBackground[0] = 0
        self.recoBackground[0] = 0

        self.trueOnePhotonInclusive[0] = 0
        self.trueTwoPhotonInclusive[0] = 0
        self.recoOnePhotonInclusive[0] = 0
        self.recoTwoPhotonInclusive[0] = 0



    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        #Reconstructed sideband assignment
        output.Branch("recoOnePhotonInclusive", self.recoOnePhotonInclusive, "recoOnePhotonInclusive/I")
        output.Branch("recoTwoPhotonInclusive", self.recoTwoPhotonInclusive, "recoTwoPhotonInclusive/I")
        output.Branch("trueOnePhotonInclusive", self.trueOnePhotonInclusive, "trueOnePhotonInclusive/I")
        output.Branch("trueTwoPhotonInclusive", self.trueTwoPhotonInclusive, "trueTwoPhotonInclusive/I")

        output.Branch("suspectedCosmic", self.suspectedCosmic, "suspectedCosmic/I")
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

        #True sideband assignment
        output.Branch("oneGnoXtrue", self.oneGnoXtrue, "oneGnoXtrue/I")
        output.Branch("oneGonePtrue", self.oneGonePtrue, "oneGonePtrue/I")
        output.Branch("oneGtwoPtrue", self.oneGtwoPtrue, "oneGtwoPtrue/I")
        output.Branch("oneGoneMutrue", self.oneGoneMutrue, "oneGoneMutrue/I")
        output.Branch("oneGxPitrue", self.oneGxPitrue, "oneGxPitrue/I")

        output.Branch("twoGnoXtrue", self.twoGnoXtrue, "twoGnoXtrue/I")
        output.Branch("twoGonePtrue", self.twoGonePtrue, "twoGonePtrue/I")
        output.Branch("twoGtwoPtrue", self.twoGtwoPtrue, "twoGtwoPtrue/I")
        output.Branch("twoGoneMutrue", self.twoGoneMutrue, "twoGoneMutrue/I")
        output.Branch("twoGxPitrue", self.twoGxPitrue, "twoGxPitrue/I")

        output.Branch("inFiducial", self.inFiducial, "inFiducial/I")


    
    def requiredInputs(self):
        """Specify required inputs."""
        
        return ["gen2ntuple", 
            "photon_data", 
            "detectable_particle_data", 
            "true_photon_data", 
            "true_detectable_particle_data",
            "vertex_properties"
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
        flashpred = data.get("flashpred", {})

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

        if self.flashPred == True:
            self.sinkhornDiv[0] = flashpred["sinkhorn_div"]
            self.observedPE[0] = flashpred["observedpe"]

        self.minComp[0] = recoPhotonData["minComp"]

        #See if the event vertex is reconstructed in the fiducial:
        if ( ntuple.vtxX > (self.fiducial["xMin"] + self.fiducial["width"])
                    and ntuple.vtxX < (self.fiducial["xMax"] - self.fiducial["width"])
                    and ntuple.vtxY > (self.fiducial["yMin"] + self.fiducial["width"])
                    and ntuple.vtxY < (self.fiducial["yMax"] - self.fiducial["width"])
                    and ntuple.vtxZ > (self.fiducial["zMin"] + self.fiducial["width"])
                    and ntuple.vtxZ < (self.fiducial["zMax"] - self.fiducial["width"])):
                self.inFiducial[0] = 1


        #Now we filter out events reconstructed as background:
        if (self.VertexFound[0] != 1
                or self.inFiducial[0] != 1
                or self.cosmicFraction[0] > 0.15
                or self.fracUnreconstructedPixels[0] > 0.9
                or self.recoMuonCount[0] > self.recoJustOverMuons[0] 
                or self.recoJustOverMuons[0] > 1
                or self.recoElectronCount[0] > 0 
                or self.recoPionCount[0] > self.recoJustOverPions[0] 
                or self.recoProtonCount[0] > 2 
                or self.recoPhotonCount[0] > 2 
                or self.recoPhotonCount[0] == 0
                or self.photonFromCharged[0] < 5
                or self.minComp[0] < 0.3
                ):

            self.recoBackground[0] = 1
        
        if self.flashPred == True:
            if self.observedPE[0] < 250 or self.sinkhornDiv[0] > 40:
                self.recoBackground[0] = 1

        #Next we determine what sideband the particle belongs to:
        #SIDEBANDS WITH ONE PHOTON
        if self.recoPhotonCount[0] == 1 and self.recoBackground[0] == 0:
            self.recoOnePhotonInclusive[0] = 1
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
        elif self.recoPhotonCount[0] == 2 and self.recoBackground[0] == 0:
            self.recoTwoPhotonInclusive[0] = 1
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
        if not ismc:
            return {"recoBackground":self.recoBackground[0],
                "oneGnoX": self.oneGnoX[0],
                "oneGoneP": self.oneGoneP[0],
                "oneGtwoP": self.oneGtwoP[0],
                "oneGoneMu": self.oneGoneMu[0],
                "oneGxPi": self.oneGxPi[0],
                "twoGnoX": self.twoGnoX[0],
                "twoGoneP": self.twoGoneP[0],
                "twoGtwoP": self.twoGtwoP[0],
                "twoGoneMu": self.twoGoneMu[0],
                "twoGxPi": self.twoGxPi[0],
                "trueBackground": self.trueBackground[0],
                "oneGnoXtrue": self.oneGnoXtrue[0],
                "oneGonePtrue": self.oneGonePtrue[0],
                "oneGtwoPtrue": self.oneGtwoPtrue[0],
                "oneGoneMutrue": self.oneGoneMutrue[0],
                "oneGxPitrue": self.oneGxPitrue[0],
                "twoGnoXtrue": self.twoGnoXtrue[0],
                "twoGonePtrue": self.twoGonePtrue[0],
                "twoGtwoPtrue": self.twoGtwoPtrue[0],
                "twoGoneMutrue": self.twoGoneMutrue[0],
                "twoGxPitrue": self.twoGxPitrue[0],
                "inFiducial": self.inFiducial[0]
                }

        if (self.trueMuonCount[0] > self.trueJustOverMuons[0] or self.trueMuonCount[0] > 1
                or self.trueElectronCount[0] != 0
                or self.trueProtonCount[0] > 2
                or self.truePionCount[0] > self.trueJustOverPions[0]
                or self.truePhotonCount[0] == 0
                or self.truePhotonCount[0] > 2):
            self.trueBackground[0] = 1

        if self.truePhotonCount[0] == 1 and self.trueBackground[0] == 0:
            self.trueOnePhotonInclusive[0] = 1
            
            if (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.oneGnoXtrue[0] = 1 #One photon, nothing else

            elif (self.trueProtonCount[0] == 1 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.oneGonePtrue[0] = 1 #One photon, one proton, nothing else

            elif (self.trueProtonCount[0] == 2 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.oneGtwoPtrue[0] = 1 #One photon, two protons, nothing else

            elif (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 1 
                    and self.trueJustOverPions[0] == 0):
                self.oneGoneMutrue[0] = 1 #One photon, one muon between 100 MeV and 120 MeV, nothing else

            elif (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] > 0):
                self.oneGxPitrue[0] = 1 #One photon, X pions between 30 and 45 MeV, nothing else

        #SIDEBANDS WITH TWO PHOTONS
        elif self.truePhotonCount[0] == 2 and self.trueBackground[0] == 0:
            self.trueTwoPhotonInclusive[0] = 1
            if (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.twoGnoXtrue[0] = 1 #Two photons, nothing else

            elif (self.trueProtonCount[0] == 1 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.twoGonePtrue[0] = 1 #Two photons, one proton, nothing else

            elif (self.trueProtonCount[0] == 2 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] == 0):
                self.twoGtwoPtrue[0] = 1 #Two photons, two protons nothing else

            elif (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 1 
                    and self.trueJustOverPions[0] == 0):
                self.twoGoneMutrue[0] = 1 #Two photons, one muon between 100 and 120 MeV, nothing else

            elif (self.trueProtonCount[0] == 0 
                    and self.trueJustOverMuons[0] == 0 
                    and self.trueJustOverPions[0] > 0):
                self.twoGxPitrue[0] = 1 #Two photons, X pions between 30 and 45 MeV, nothing else


        return {"recoBackground":self.recoBackground[0],
            "oneGnoX": self.oneGnoX[0],
            "oneGoneP": self.oneGoneP[0],
            "oneGtwoP": self.oneGtwoP[0],
            "oneGoneMu": self.oneGoneMu[0],
            "oneGxPi": self.oneGxPi[0],
            "twoGnoX": self.twoGnoX[0],
            "twoGoneP": self.twoGoneP[0],
            "twoGtwoP": self.twoGtwoP[0],
            "twoGoneMu": self.twoGoneMu[0],
            "twoGxPi": self.twoGxPi[0],
            "trueBackground": self.trueBackground[0],
            "oneGnoXtrue": self.oneGnoXtrue[0],
            "oneGonePtrue": self.oneGonePtrue[0],
            "oneGtwoPtrue": self.oneGtwoPtrue[0],
            "oneGoneMutrue": self.oneGoneMutrue[0],
            "oneGxPitrue": self.oneGxPitrue[0],
            "twoGnoXtrue": self.twoGnoXtrue[0],
            "twoGonePtrue": self.twoGonePtrue[0],
            "twoGtwoPtrue": self.twoGtwoPtrue[0],
            "twoGoneMutrue": self.twoGoneMutrue[0],
            "twoGxPitrue": self.twoGxPitrue[0],
            "inFiducial": self.inFiducial[0],
            "sinkhornDiv": self.sinkhornDiv[0],
            "observedPE": self.observedPE[0]
            }

    def finalize(self):
        """
        nothing to do after the event loop
        """
        super().finalize()
        return