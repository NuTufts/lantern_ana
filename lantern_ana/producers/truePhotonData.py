# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array
from lantern_ana.utils.fiducial_volume import dwall
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
        self.EDepMaxPlane = array('f',[0.0])
        self.LeadingEDepDwall = array('f',[-999.0])

        # These variables measure the distance of the selected vertex to both
        # the neutrino interaction vertex or the closest photon energy deposit location
        self.recovtxtonuvtx = array('f',[9999.0])
        self.recovtxtophotonedep = array('f',[9999.0])

        #These variables are just for other producers
        self.MaxPlaneList = array('f',[0.0]*self._maxnphotons)
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
        output.Branch(f"eDepMaxPlane", self.EDepMaxPlane, f"eDepMaxPlane/F")
        output.Branch(f"leadingEDepDwall",self.LeadingEDepDwall,f"leadingEDepDwall/F")
        output.Branch('recovtx_to_nuvtx',self.recovtxtonuvtx,'recovtx_to_nuvtx/F')
        output.Branch('recovtx_to_photonedep',self.recovtxtophotonedep,'recovtx_to_photonedep/F')
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
        self.EDepMaxPlane[0] = 0.0
        self.LeadingEDepDwall[0] = -999.0
        self.recovtxtonuvtx[0] = 9999.0
        self.recovtxtophotonedep[0] = 9999.0

    
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
                "posZ": self.truePhotonPositionZ[0],
                "LeadingPhoton":self.trueLeadingPhotonEnergy[0],
                }
            return truePhotonDataDict


        # Find and store data on showers ID'd as photons

        #Set/Reset Variables
        numPhotons = 0
        self.setDefaultValues()
        photonEList = []

        maxEdep = 0.0

        truevtx_pos = np.array([ntuple.trueVtxX,ntuple.trueVtxY,ntuple.trueVtxZ])
        min_edep2vtx_dist = 9999.0

        recovtx_pos = None
        if ntuple.foundVertex==1:
            recovtx_pos = np.array( [ntuple.vtxX,ntuple.vtxY,ntuple.vtxZ] )
            tru2vtx_dist = np.sqrt( np.power( (truevtx_pos-recovtx_pos), 2 ).sum() )
            self.recovtxtonuvtx[0] = tru2vtx_dist


        for i in range(ntuple.nTrueSimParts):
            #Make sure reco thinks we have a photon
            if ntuple.trueSimPartPDG[i] != 22:
                continue

            #See if the photon exceeds the energy threshold
            pixelList = [ntuple.trueSimPartPixelSumUplane[i]*0.0126, 
                        ntuple.trueSimPartPixelSumVplane[i]*0.0126, 
                        ntuple.trueSimPartPixelSumYplane[i]*0.0126]

            nplanes = 0
            for pixsum in pixelList:
                if pixsum>5.0:
                    nplanes += 1
                # this looks like a bug: this keeps nplanes==0 or nplanes==1 depending on U-plane value
                #if nplanes<=2:
                #    continue

            # I think we want to make sure photon deposits above threshold energy above 2 planes
            if nplanes<=2:
                continue

            self.MaxPlaneList[numPhotons] = np.max(pixelList)

            #Now that we know it passes inspection, we store the photon's data in our arrays
            photonPX = ntuple.trueSimPartPx[i]
            photonPY = ntuple.trueSimPartPy[i]
            photonPZ = ntuple.trueSimPartPz[i]

            photonE = np.sqrt(photonPX**2 + photonPY**2 + photonPZ**2)

            self.truePhotonEnergies[numPhotons] = photonE
            self.truePhotonPositionX[numPhotons] = ntuple.trueSimPartEDepX[i]
            self.truePhotonPositionY[numPhotons] = ntuple.trueSimPartEDepY[i]
            self.truePhotonPositionZ[numPhotons] = ntuple.trueSimPartEDepZ[i]

            if recovtx_pos is not None:
                edep_pos = np.array([ntuple.trueSimPartEDepX[i],ntuple.trueSimPartEDepY[i],ntuple.trueSimPartEDepZ[i]])
                edep2vtx_dist = np.sqrt( np.power( (edep_pos-recovtx_pos), 2 ).sum() )
                if edep2vtx_dist < min_edep2vtx_dist:
                    min_edep2vtx_dist = edep2vtx_dist

            if self.MaxPlaneList[numPhotons]>maxEdep:
                maxEdep = self.MaxPlaneList[numPhotons]
                self.LeadingEDepDwall[0] = dwall(ntuple.trueSimPartEDepX[i],ntuple.trueSimPartEDepY[i],ntuple.trueSimPartEDepZ[i])
                self.EDepSumU[0] = pixelList[0]
                self.EDepSumV[0] = pixelList[1]
                self.EDepSumY[0] = pixelList[2]
                self.EDepMaxPlane[0] = self.MaxPlaneList[numPhotons]

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
        # end of true sim particle loop

        if recovtx_pos is not None and self.nTruePhotons[0]>0:
            self.recovtxtophotonedep[0] = min_edep2vtx_dist
 
        #Store the energy of the leading photon
        if numPhotons == 0:
            truePhotonDataDict = {
                "ntruePhotons":self.nTruePhotons[0], 
                "energy":self.truePhotonEnergies[0],
                "posX":self.truePhotonPositionX[0], 
                "posY":self.truePhotonPositionY[0], 
                "posZ":self.truePhotonPositionZ[0],
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