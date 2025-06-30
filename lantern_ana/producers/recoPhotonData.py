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
        self._maxnphotons = 100

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

    def setDefaultValues(self): #Not clear what to do here?
        self.nphotons[0] = 0
        self.leadingPhotonEnergy[0] = 0.0
        self.photonFromCharged[0] = 0.0
        for x in range(5):
            self.photonEnergies[x] = 0.0
            self.photonPositionX[x] = 0.0
            self.photonPositionY[x] = 0.0
            self.photonPositionZ[x] = 0.0

    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"nphotons", self.nphotons, f"nphotons/I")
        output.Branch(f"leadingPhotonE", self.leadingPhotonEnergy, f"leadingPhotonE/F")
        output.Branch(f"photonFromCharged", self.leadingPhotonEnergy, f"photonFromCharged/F")

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

        for i in range(ntuple.nShowers):
            #Make sure reco thinks we have a photon
            if ntuple.showerPID[i] != 22:
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
            photonFromChargedScores.append(abs(ntuple.showerFromChargedScore[i]))
            self.photonPositionX[numPhotons] = ntuple.showerStartPosX[i]
            self.photonPositionY[numPhotons] = ntuple.showerStartPosY[i]
            self.photonPositionZ[numPhotons] = ntuple.showerStartPosZ[i]
            #Track that we've found a detectable photon
            
            self.nphotons[0] += 1
            #Occasionally we get more than 5 photons, but we shouldn't need to worry about storing those
            if self.nphotons[0] < 5:
                numPhotons += 1
            else:
                break

        # Find and store data on tracks ID'd as photons
        # First we make sure we're actually looking at something reco thinks is a photon
        for i in range(ntuple.nTracks):
            if numPhotons >= 5:
                break

            if ntuple.trackPID[i] != 22:
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
            photonFromChargedScores.append(abs(ntuple.trackFromChargedScore[i]))
            self.photonPositionX[numPhotons] = ntuple.trackStartPosX[i]
            self.photonPositionY[numPhotons] = ntuple.trackStartPosY[i]
            self.photonPositionZ[numPhotons] = ntuple.trackStartPosZ[i]
            photonEList.append(ntuple.trackRecoE[i])

            self.nphotons[0] += 1
            if self.nphotons[0] < 5:
                numPhotons += 1
            else:
                break

        #Store the energy of the leading photon
        maxPhotonE = np.max(self.photonEnergies)
        self.leadingPhotonEnergy[0] = maxPhotonE
        #print("Photon Energies:", self.photonEnergies, flush=True)

        if len(photonFromChargedScores) > 0:
            self.photonFromCharged[0] = min(photonFromChargedScores)

        #Store the data as a dictionary:
        photonDataDict = {"nphotons":self.nphotons[0], 
            "energy":self.photonEnergies[0], 
            "posX":self.photonPositionX[0], 
            "posY":self.photonPositionY[0], 
            "posZ": self.photonPositionZ[0], 
            "photonFromCharged": self.photonFromCharged[0]
            }

        return photonDataDict