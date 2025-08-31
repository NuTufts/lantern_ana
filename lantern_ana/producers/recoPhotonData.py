# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array
import sys

@register
class recoPhotonDataProducer(ProducerBaseClass):
    """
    Producer that tracks the location and energy of all photons.
    """

    def __init__(self, name, config):
        super().__init__(name, config)
        #We get these variables from the config
        self.fiducial = config.get('fiducialData', {"xMin":0, "xMax":256, "yMin":-116.5, "yMax":116.5, "zMin":0, "zMax":1036, "width":15})
        self._maxnphotons = 5

        #These variables are what we're interested in passing to the ntuple
        self.nphotons = array('i',[0]) #This tells us if the event is useful for our analysis
        self.leadingPhotonEnergy = array('f',[0.0]) #This will be our graphing variable

        #These variables are just for other producers
        self.photonEnergies = array('f',[0.0]*self._maxnphotons)
        self.photonPositionX = array('f',[0.0]*self._maxnphotons)
        self.photonPositionY = array('f',[0.0]*self._maxnphotons)
        self.photonPositionZ = array('f',[0.0]*self._maxnphotons)

        #These variables help us identify cosmic background events
        self.photonFromCharged = array('f',[0])
        self.visibleEnergy = array('f',[0])

        self.recoPur = array('f',[0.0]*self._maxnphotons)
        self.recoComp = array('f',[0.0]*self._maxnphotons)
        self.minComp = array('f',[0.0])
        self.minPur = array('f',[0.0])

    def setDefaultValues(self): #Not clear what to do here?
        self.nphotons[0] = 0
        self.leadingPhotonEnergy[0] = 0.0
        self.photonFromCharged[0] = 0.0
        self.visibleEnergy[0] = -1
        self.minComp[0] = 9999
        self.minPur[0] = 9999
       
        #These variables are here for photons that lack truth matching

        for x in range(5):
            self.photonEnergies[x] = 0.0
            self.photonPositionX[x] = 0.0
            self.photonPositionY[x] = 0.0
            self.photonPositionZ[x] = 0.0
            self.recoPur[x] = 9999
            self.recoComp[x] = 9999

    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"nphotons", self.nphotons, f"nphotons/I")
        output.Branch(f"leadingPhotonE", self.leadingPhotonEnergy, f"leadingPhotonE/F")
        output.Branch(f"photonFromCharged", self.leadingPhotonEnergy, f"photonFromCharged/F")
        output.Branch(f"visibleEnergy", self.visibleEnergy, f"visibleEnergy/F")
        output.Branch(f"recoPur", self.recoPur, f"recoPur[{self._maxnphotons}]/F")
        output.Branch(f"recoComp", self.recoComp, f"recoComp[{self._maxnphotons}]/F")


    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]
        
        self.setDefaultValues()


        photonEList = []
        numPhotons = 0
        photonFromChargedScores = []

        ismc = params.get('ismc',False)

        for i in range(ntuple.nShowers):
            #Determine the reconstructed energy for all true photons (even if we mis-ID them)
            if ismc:
                if ntuple.showerTruePID[i] == 22:
                    self.visibleEnergy[0] = ntuple.showerRecoE[i]

            #Make sure reco thinks we have a photon
            if ntuple.showerPID[i] != 22:
                continue

            if ntuple.showerIsSecondary[i]==1:
                continue

            #See if the photon exceeds the energy threshold
            if ntuple.showerRecoE[i] < 10: #MeV
                continue

            #Check if the photon started depositing within our fiducial volume
            if (ntuple.showerStartPosX[i] > (self.fiducial["xMin"] + self.fiducial["width"])
                    and ntuple.showerStartPosX[i] < (self.fiducial["xMax"] - self.fiducial["width"])
                    and ntuple.showerStartPosY[i] > (self.fiducial["yMin"] + self.fiducial["width"])
                    and ntuple.showerStartPosY[i] < (self.fiducial["yMax"] - self.fiducial["width"])
                    and ntuple.showerStartPosZ[i] > (self.fiducial["zMin"] + self.fiducial["width"])
                    and ntuple.showerStartPosZ[i] < (self.fiducial["zMax"] - self.fiducial["width"])):
                inFiducial = True
            else:
                continue

            #Now we store the photon's data in our arrays
            self.photonEnergies[numPhotons] = ntuple.showerRecoE[i]
            self.photonPositionX[numPhotons] = ntuple.showerStartPosX[i]
            self.photonPositionY[numPhotons] = ntuple.showerStartPosY[i]
            self.photonPositionZ[numPhotons] = ntuple.showerStartPosZ[i]

            #Some information for potential cuts
            photonFromChargedScores.append(abs(ntuple.showerFromChargedScore[i]))
            self.recoPur[numPhotons] = ntuple.showerPurity[i]
            self.recoComp[numPhotons] = ntuple.showerComp[i]


            #Track that we've found a detectable photon
            self.nphotons[0] += 1
            numPhotons += 1
            #Occasionally we get more than 5 photons, but we shouldn't need to worry about storing those
            if self.nphotons[0] >= 5:
                break

        # Find and store data on tracks ID'd as photons
        # First we make sure we're actually looking at something reco thinks is a photon
        for i in range(ntuple.nTracks):
            if ismc:
                if ntuple.trackTruePID[i] == 22:
                    self.visibleEnergy[0] = ntuple.trackRecoE[i]

            if numPhotons >= 5:
                break

            if ntuple.trackPID[i] != 22:
                continue

            if ntuple.trackIsSecondary[i]==1:
                continue

            #See if the photon exceeds the energy threshold
            if ntuple.trackRecoE[i] < 10: #MeV
                continue

            #Check if the photon started depositing within our fiducial volume
            if ( ntuple.trackStartPosX[i] > (self.fiducial["xMin"] + self.fiducial["width"])
                    and ntuple.trackStartPosX[i] < (self.fiducial["xMax"] - self.fiducial["width"])
                    and ntuple.trackStartPosY[i] > (self.fiducial["yMin"] + self.fiducial["width"])
                    and ntuple.trackStartPosY[i] < (self.fiducial["yMax"] - self.fiducial["width"])
                    and ntuple.trackStartPosZ[i] > (self.fiducial["zMin"] + self.fiducial["width"])
                    and ntuple.trackStartPosZ[i] < (self.fiducial["zMax"] - self.fiducial["width"])):
                inFiducial = True
            else:
                continue

            #Store data for any photons that pass our criteria
            self.photonEnergies[numPhotons] = ntuple.trackRecoE[i]
            self.photonPositionX[numPhotons] = ntuple.trackStartPosX[i]
            self.photonPositionY[numPhotons] = ntuple.trackStartPosY[i]
            self.photonPositionZ[numPhotons] = ntuple.trackStartPosZ[i]
            photonEList.append(ntuple.trackRecoE[i])


            #Store some info for potential cuts
            photonFromChargedScores.append(abs(ntuple.trackFromChargedScore[i]))
            self.recoPur[numPhotons] = ntuple.trackPurity[i]
            self.recoComp[numPhotons] = ntuple.trackComp[i]

            self.nphotons[0] += 1
            numPhotons += 1
            if self.nphotons[0] >= 5:
                break

        #Store the energy of the leading photon
        maxPhotonE = np.max(self.photonEnergies)
        imaxPhotonE = np.argmax(self.photonEnergies)
        self.leadingPhotonEnergy[0] = maxPhotonE
        #print("Photon Energies:", self.photonEnergies, flush=True)

        minRecoComp = np.min(self.recoComp)
        self.minComp[0] = minRecoComp

        minRecoPur = np.min(self.recoPur)
        self.minPur[0] = minRecoPur

        if len(photonFromChargedScores) > 0:
            self.photonFromCharged[0] = min(photonFromChargedScores)

        #Store the data as a dictionary:
        photonDataDict = {"nphotons":self.nphotons[0], 
            "energy":self.photonEnergies[0], 
            "posX":self.photonPositionX[0], 
            "posY":self.photonPositionY[0], 
            "posZ": self.photonPositionZ[0], 
            "photonFromCharged": self.photonFromCharged[0],
            "minComp": self.minComp[0],
            "minPur": self.minPur[0]
        }

        return photonDataDict