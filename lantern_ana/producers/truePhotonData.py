# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array
import sys

@register
class truePhotonDataProducer(ProducerBaseClass):
    """
    Producer that tracks the location and energy of all photons.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        #We get these variables from the config
        self._maxnphotons = 5
        self.fiducial = config.get('fiducialData', {"xMin":0, "xMax":256, "yMin":-116.5, "yMax":116.5, "zMin":0, "zMax":1036, "width":10})


        #These variables are what we're interested in passing to the ntuple
        self.nTruePhotons = array('i',[0]) #This tells us if the event is useful for our analysis
        self.nTrueFiducialPhotons = array('i',[0]) #Useful extra data
        self.trueLeadingPhotonEnergy = array('f',[0.0]) #This will be our graphing variable
        self.EDepSumU = array('f',[0.0]) #EDep determines if a given photon is elligible to be counted
        self.EDepSumV = array('f',[0.0])
        self.EDepSumY = array('f',[0.0])
        #self.EDepSumMax = array('f',[0.0])
        self.MaxPlaneList = array('f',[0.0]*self._maxnphotons)

        #These variables are just for other producers
        self.truePhotonEnergies = array('f',[0.0]*self._maxnphotons)
        self.truePhotonPositionX = array('f',[0.0]*self._maxnphotons)
        self.truePhotonPositionY = array('f',[0.0]*self._maxnphotons)
        self.truePhotonPositionZ = array('f',[0.0]*self._maxnphotons)

    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"nTruePhotons", self.nTruePhotons, f"nTruePhotons/I")
        output.Branch(f"nTrueFiducialPhotons", self.nTrueFiducialPhotons, f"nTrueFiducialPhotons/I")
        output.Branch(f"trueLeadingPhotonE", self.trueLeadingPhotonEnergy, f"trueLeadingPhotonE/F")
        output.Branch(f"eDepSumU", self.EDepSumU, f"eDepSumU/F")
        output.Branch(f"eDepSumV", self.EDepSumV, f"eDepSumV/F")
        output.Branch(f"eDepSumY", self.EDepSumY, f"eDepSumY/F")
        #output.Branch(f"EDepSumMax", self.EDepSumMax, f"EDepSumMax/F")
  
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]

    def setDefaultValues(self): #Not clear what to do here?
        self.nTruePhotons[0] = 0
        self.nTrueFiducialPhotons[0] = 0
        self.trueLeadingPhotonEnergy[0] = 0.0
        for x in range(5):
            self.truePhotonEnergies[x] = 0.0
            self.truePhotonPositionX[x] = 0.0
            self.truePhotonPositionY[x] = 0.0
            self.truePhotonPositionZ[x] = 0.0
            self.MaxPlaneList[x] = 0.0


        self.EDepSumU[0] = 0.0
        self.EDepSumV[0] = 0.0
        self.EDepSumY[0] = 0.0
        #self.EDepSumMax[0] = 0.0

    
    def processEvent(self, data, params):        
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]

        #Only run this on Montecarlo files
        ismc = params.get('ismc',False)
        if not ismc:
            truePhotonDataDict = {
                "ntruePhotons":self.nTruePhotons[0], 
                "energy":self.truePhotonEnergies[0], 
                "posX":self.truePhotonPositionX[0], 
                "posY":self.truePhotonPositionY[0], 
                "posZ": self.truePhotonPositionZ[0]
                }
            return truePhotonDataDict


        # Find and store data on showers ID'd as photons

        #Set/Reset Variables
        numPhotons = 0
        self.setDefaultValues()
        photonEList = []

        for i in range(ntuple.nTrueSimParts):
            #Make sure reco thinks we have a photon
            if ntuple.trueSimPartPDG[i] != 22:
                continue

            #See if the photon exceeds the energy threshold
            pixelList = [ntuple.trueSimPartPixelSumUplane[i], ntuple.trueSimPartPixelSumVplane[i], ntuple.trueSimPartPixelSumYplane[i]]
            self.EDepSumU[0] = ntuple.trueSimPartPixelSumUplane[i]
            self.EDepSumV[0] = ntuple.trueSimPartPixelSumVplane[i]
            self.EDepSumY[0] = ntuple.trueSimPartPixelSumYplane[i]            
            self.MaxPlaneList[numPhotons] = np.max(pixelList) * 0.0126


            nplanes = 0
            for pixsum in pixelList:
                if pixsum*0.0126>5.0:
                    nplanes += 1
                if nplanes<=2:
                    continue

                
            #Now that we know it passes inspection, we store the photon's data in our arrays
            photonPX = ntuple.trueSimPartPx[i]
            photonPY = ntuple.trueSimPartPy[i]
            photonPZ = ntuple.trueSimPartPz[i]

            photonE = np.sqrt(photonPX**2 + photonPY**2 + photonPZ**2)

            self.truePhotonEnergies[numPhotons] = photonE
            self.truePhotonPositionX[numPhotons] = ntuple.trueSimPartEDepX[i]
            self.truePhotonPositionY[numPhotons] = ntuple.trueSimPartEDepY[i]
            self.truePhotonPositionZ[numPhotons] = ntuple.trueSimPartEDepZ[i]
            #Track that we've found a detectable photon

            self.nTruePhotons[0] += 1

            #See if the photon falls into the fiducial
            if ((self.fiducial["xMin"] + self.fiducial["width"] < ntuple.trueSimPartEDepX[i]) and
                    (self.fiducial["xMax"] - self.fiducial["width"] > ntuple.trueSimPartEDepX[i]) and
                    (self.fiducial["yMin"] + self.fiducial["width"] < ntuple.trueSimPartEDepY[i]) and
                    (self.fiducial["yMax"] - self.fiducial["width"] > ntuple.trueSimPartEDepY[i]) and
                    (self.fiducial["zMin"] + self.fiducial["width"] < ntuple.trueSimPartEDepZ[i]) and
                    (self.fiducial["zMax"] - self.fiducial["width"] > ntuple.trueSimPartEDepZ[i])
                    ):
                #print(ntuple.trueSimPartEDepX[i], ntuple.trueSimPartEDepY[i], ntuple.trueSimPartEDepZ[i])
                self.nTrueFiducialPhotons[0] += 1


            #print(self.nTruePhotons[0], self.nTrueFiducialPhotons[0])

            #Occasionally we get more than 5 photons, but we shouldn't need to worry about storing those
            if self.nTruePhotons[0] < 5:
                numPhotons += 1
            else:
                break

 
        #Store the energy of the leading photon
        if numPhotons == 0:
            truePhotonDataDict = {
                "ntruePhotons":self.nTruePhotons[0], 
                "energy":self.truePhotonEnergies[0],
                "posX":self.truePhotonPositionX[0], 
                "posY":self.truePhotonPositionY[0], 
                "posZ":self.truePhotonPositionZ[0],
                #"EDepMax":self.EDepSumMax[0],
                "LeadingPhoton":self.trueLeadingPhotonEnergy[0],
                }

            return truePhotonDataDict

        maxEIndex = 0
        for x in range(len(self.truePhotonEnergies)):
            if self.truePhotonEnergies[x] > self.truePhotonEnergies[maxEIndex]:
                maxEIndex = x
            

        maxPhotonE = self.truePhotonEnergies[maxEIndex]
        maxPlaneE = self.MaxPlaneList[maxEIndex]
        self.trueLeadingPhotonEnergy[0] = maxPhotonE
        #self.EDepSumMax[0] = maxPlaneE

        #print(self.trueLeadingPhotonEnergy[0], self.EDepSumMax[0])

        #if self.nTruePhotons[0] > 0 and self.nTruePhotons[0] == 1:
            #print(self.trueLeadingPhotonEnergy[0])


        #Store the data as a dictionary:
        truePhotonDataDict = {
            "ntruePhotons":self.nTruePhotons[0], 
            "energy":self.truePhotonEnergies[0],
            "posX":self.truePhotonPositionX[0], 
            "posY":self.truePhotonPositionY[0], 
            "posZ":self.truePhotonPositionZ[0],
            #"EDepMax":self.EDepSumMax[0],
            "LeadingPhoton":self.trueLeadingPhotonEnergy[0],
            }

        return truePhotonDataDict