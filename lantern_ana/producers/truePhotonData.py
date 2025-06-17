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

        #These variables are what we're interested in passing to the ntuple
        self.nTruePhotons = array('i',[0]) #This tells us if the event is useful for our analysis
        self.trueLeadingPhotonEnergy = array('f',[0.0]) #This will be our graphing variable

        #These variables are just for other producers
        self.truePhotonEnergies = array('f',[0.0]*self._maxnphotons)
        self.truePhotonPositionX = array('f',[0.0]*self._maxnphotons)
        self.truePhotonPositionY = array('f',[0.0]*self._maxnphotons)
        self.truePhotonPositionZ = array('f',[0.0]*self._maxnphotons)

    def setDefaultValues(self): #Not clear what to do here?
        self.nTruePhotons[0] = 0
        self.trueLeadingPhotonEnergy[0] = 0.0
        for x in range(5):
            self.truePhotonEnergies[x] = 0.0
            self.truePhotonPositionX[x] = 0.0
            self.truePhotonPositionY[x] = 0.0
            self.truePhotonPositionZ[x] = 0.0

    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"nTruePhotons", self.nTruePhotons, f"nTruePhotons/I")
        output.Branch(f"trueLeadingPhotonE", self.trueLeadingPhotonEnergy, f"trueLeadingPhotonE/F")

    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
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
            nplanes = 0
            for pixsum in pixelList:
                if pixsum*0.0126>5.0:
                    nplanes += 1
                if nplanes<=2:
                    continue

                
            #Now that we know it passes inspection, we store the photon's data in our arrays
            self.truePhotonEnergies[numPhotons] = ntuple.trueSimPartE[i]
            self.truePhotonPositionX[numPhotons] = ntuple.trueSimPartEDepX[i]
            self.truePhotonPositionY[numPhotons] = ntuple.trueSimPartEDepY[i]
            self.truePhotonPositionZ[numPhotons] = ntuple.trueSimPartEDepZ[i]
            #Track that we've found a detectable photon
            
            self.nTruePhotons[0] += 1
            #Occasionally we get more than 5 photons, but we shouldn't need to worry about storing those
            if self.nTruePhotons[0] < 5:
                numPhotons += 1
            else:
                break

 
        #Store the energy of the leading photon
        maxPhotonE = np.max(self.truePhotonEnergies)
        self.trueLeadingPhotonEnergy[0] = maxPhotonE
        #print("Photon Energies:", self.photonEnergies, flush=True)


        #Store the data as a dictionary:
        truePhotonDataDict = {
            "ntruePhotons":self.nTruePhotons[0], 
            "energy":self.truePhotonEnergies[0], 
            "posX":self.truePhotonPositionX[0], 
            "posY":self.truePhotonPositionY[0], 
            "posZ": self.truePhotonPositionZ[0]
            }

        return truePhotonDataDict