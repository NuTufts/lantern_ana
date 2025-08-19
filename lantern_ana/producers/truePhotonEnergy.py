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
        self.fiducial = config.get('fiducialData', {"xMin":0, "xMax":256, "yMin":-116.5, "yMax":116.5, "zMin":0, "zMax":1036, "width":10})
        #We get these variables from the config
        self._maxnphotons = 20

        #These variables are what we're interested in passing to the ntuple
        self.nTruePhotons = array('i',[0]) #This tells us if the event is useful for our analysis
        self.nMatchedPhotons = array('i',[0])
        self.nMatchedFiducialPhotons = array('i',[0])

        #These variables are just for other producers
        self.matchedPhotonEnergiesTrue = array('f',[0.0]*self._maxnphotons)
        self.matchedPhotonEnergiesVisible = array('f',[0.0]*self._maxnphotons)
        self.EDepSumMax = array('f',[0.0]*self._maxnphotons)
        self.photonCompleteness = array('f',[0.0]*self._maxnphotons)
        self.photonPurity = array('f',[0.0]*self._maxnphotons)
        self.truePhotonCompleteness = array('f',[0.0]*self._maxnphotons)
        self.truePhotonPurity = array('f',[0.0]*self._maxnphotons)


    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"nMatchedPhotons", self.nMatchedPhotons, f"nMatchedPhotons/I")
        output.Branch(f"nMatchedFiducialPhotons", self.nMatchedFiducialPhotons, f"nMatchedFiducialPhotons/I")
        output.Branch(f"matchedPhotonEnergiesTrue", self.matchedPhotonEnergiesTrue, f"matchedPhotonEnergiesTrue[{self._maxnphotons}]/F")
        output.Branch(f"matchedPhotonEnergiesVisible", self.matchedPhotonEnergiesVisible, f"matchedPhotonEnergiesVisible[{self._maxnphotons}]/F")
        output.Branch(f"EDepSumMax", self.EDepSumMax, f"EDepSumMax[{self._maxnphotons}]/F")
        output.Branch(f"photonCompleteness", self.photonCompleteness, f"photonCompleteness[{self._maxnphotons}]/F")
        output.Branch(f"photonPurity", self.photonPurity, f"photonPurity[{self._maxnphotons}]/F")
        output.Branch(f"truePhotonCompleteness", self.truePhotonCompleteness, f"truePhotonCompleteness[{self._maxnphotons}]/F")
        output.Branch(f"truePhotonPurity", self.truePhotonPurity, f"truePhotonPurity[{self._maxnphotons}]/F")

        
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]

    def setDefaultValues(self): #Not clear what to do here?
        self.nMatchedPhotons[0] = 0
        self.nMatchedFiducialPhotons[0] = 0
        for x in range(20):
            self.matchedPhotonEnergiesTrue[x] = -1.0
            self.matchedPhotonEnergiesVisible[x] = -1.0
            self.EDepSumMax[x] = -1.0
            self.photonCompleteness[x] = -1.0
            self.photonPurity[x] = -1.0
            self.truePhotonCompleteness[x] = -1.0
            self.truePhotonPurity[x] = -1.0
    
    def processEvent(self, data, params):        
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]

        #Only run this on Montecarlo files
        ismc = params.get('ismc',False)
        if not ismc:
            truePhotonEnergyDict = {}
            return truePhotonEnergyDict

        #Set/Reset Variables
        numPhotons = 0
        numInFiducial = 0
        self.setDefaultValues()
 
        for i in range(ntuple.nShowers):
            #Find true photons
            if ntuple.showerTruePID[i] == 22:
                photonTID = ntuple.showerTrueTID[i] #Match reco photon to a true photon for true variables
                for x in range(ntuple.nTrueSimParts):
                    if ntuple.trueSimPartTID[x] == photonTID:
                        #Find true/visible energies
                        self.matchedPhotonEnergiesVisible[numPhotons] = ntuple.showerRecoE[i]
                        self.matchedPhotonEnergiesTrue[numPhotons] = ntuple.trueSimPartE[x]

                        #Find deposited energies
                        pixelList = [ntuple.trueSimPartPixelSumUplane[x], ntuple.trueSimPartPixelSumVplane[x], ntuple.trueSimPartPixelSumYplane[x]]
                        self.EDepSumMax[numPhotons] = np.max(pixelList) * 0.0126
                        
                        #Completeness, purity, etc.
                        self.photonCompleteness[numPhotons] = ntuple.showerComp[i]
                        self.photonPurity[numPhotons] = ntuple.showerPurity[i]
                        self.truePhotonCompleteness[numPhotons] = ntuple.showerTruePurity[i]
                        self.truePhotonPurity[numPhotons] = ntuple.showerTruePurity[i]

                        numPhotons += 1 #Iterate the index of the array we'll be filling

                        if ((self.fiducial["xMin"] + self.fiducial["width"] < ntuple.showerStartPosX[i]),
                            (self.fiducial["xMax"] - self.fiducial["width"] > ntuple.showerStartPosX[i]),
                            (self.fiducial["yMin"] + self.fiducial["width"] < ntuple.showerStartPosY[i]),
                            (self.fiducial["yMax"] - self.fiducial["width"] > ntuple.showerStartPosY[i]),
                            (self.fiducial["zMin"] + self.fiducial["width"] < ntuple.showerStartPosZ[i]),
                            (self.fiducial["zMax"] - self.fiducial["width"] > ntuple.showerStartPosZ[i])
                            ):
                            self.nMatchedFiducialPhotons[0] += 1

                        #We don't need more data than this, and we don't want the program to break if we find it
                        if numPhotons >= 20:
                            break

        for i in range(ntuple.nTracks):
            if numPhotons >= 20: #This goes at the top now, since we could theoretically be going in with 20 photons
                break
            #Find true photons
            if ntuple.trackTruePID[i] == 22:
                photonTID = ntuple.trackTrueTID[i]
                for x in range(ntuple.nTrueSimParts):
                    if ntuple.trueSimPartTID[x] == photonTID: #Match reco photon to a true photon for true variables
                        #Find true/visible energies
                        self.matchedPhotonEnergiesVisible[numPhotons] = ntuple.trackRecoE[i]
                        self.matchedPhotonEnergiesTrue[numPhotons] = ntuple.trueSimPartE[x]

                        #Find deposited energies
                        pixelList = [ntuple.trueSimPartPixelSumUplane[x], ntuple.trueSimPartPixelSumVplane[x], ntuple.trueSimPartPixelSumYplane[x]]
                        self.EDepSumMax[numPhotons] = np.max(pixelList) * 0.0126

                        #Reco completeness
                        self.photonCompleteness[numPhotons] = ntuple.trackComp[i]
                        self.photonPurity[numPhotons] = ntuple.trackPurity[i]
                        self.truePhotonCompleteness[numPhotons] = ntuple.trackTruePurity[i]
                        self.truePhotonPurity[numPhotons] = ntuple.trackTruePurity[i]

                        numPhotons += 1 #Iterate the index of the array we'll be filling

        #Store the data as a dictionary:
        truePhotonEnergyDict = {}

        return truePhotonEnergyDict