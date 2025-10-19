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
        self.include_tracks = config.get('include_tracks',True)
        self._maxnphotons = 5

        #These variables are what we're interested in passing to the ntuple
        self.nphotons = array('i',[0]) #This tells us if the event is useful for our analysis
        self.leadingPhotonEnergy = array('f',[0.0]) #This will be our graphing variable

        #These variables are just for other producers
        self.photonEnergies = array('f',[0.0]*self._maxnphotons)
        self.photonPositionX = array('f',[0.0]*self._maxnphotons)
        self.photonPositionY = array('f',[0.0]*self._maxnphotons)
        self.photonPositionZ = array('f',[0.0]*self._maxnphotons)
        self.entryused = array('i',[0]*self._maxnphotons)

        #These variables help us identify cosmic background events
        self.photonFromCharged = array('f',[0])
        self.visibleEnergy = array('f',[0])

        self.recoPur = array('f',[0.0]*self._maxnphotons)
        self.recoComp = array('f',[0.0]*self._maxnphotons)
        self.recoPhScore = array('f',[0.0]*self._maxnphotons)
        self.minComp = array('f',[0.0])
        self.minPur = array('f',[0.0])
        #self.max

        # These variables pass through the reco-truth matching
        self.recophoton_truepid = array('i',[0]*self._maxnphotons)
        self.recophoton_truepurity = array('f',[0.0]*self._maxnphotons)
        self.recophoton_truecomp = array('f',[0.0]*self._maxnphotons)



    def setDefaultValues(self): #Not clear what to do here?
        self.nphotons[0] = 0
        self.leadingPhotonEnergy[0] = 0.0
        self.photonFromCharged[0] = 0.0
        self.visibleEnergy[0] = -1
        self.minComp[0] = 9999
        self.minPur[0] = 9999
       
        #These variables are here for photons that lack truth matching

        for x in range(5):
            self.entryused[x] = 0
            self.photonEnergies[x] = 0.0
            self.photonPositionX[x] = 0.0
            self.photonPositionY[x] = 0.0
            self.photonPositionZ[x] = 0.0
            self.recoPur[x] = -1
            self.recoComp[x] = -1
            self.recophoton_truepid[x] = -1
            self.recophoton_truepurity[x] = 0.0
            self.recophoton_truecomp[x] = 0.0


    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"{self.name}_nphotons",       self.nphotons,              f"{self.name}_nphotons/I")
        output.Branch(f"{self.name}_leadingPhotonE", self.leadingPhotonEnergy,   f"{self.name}_leadingPhotonE/F")
        output.Branch(f"{self.name}_photonFromCharged", self.photonFromCharged,  f"{self.name}_photonFromCharged/F")
        #output.Branch(f"{self.name}_photonFromNeutral", self.photonFromNeutral,  f"{self.name}_photonFromNeutral/F")
        #output.Branch(f"{self.name}_photonFromPrimary", self.photonFromPrimary,  f"{self.name}_photonFromPrimary/F")
        output.Branch(f"{self.name}_visibleEnergy", self.visibleEnergy,          f"{self.name}_visibleEnergy/F")
        output.Branch(f"{self.name}_entryused", self.entryused,                  f"{self.name}_entryused[{self._maxnphotons}]/I")
        output.Branch(f"{self.name}_recoPur", self.recoPur,                      f"{self.name}_recoPur[{self._maxnphotons}]/F")
        output.Branch(f"{self.name}_recoComp", self.recoComp,                    f"{self.name}_recoComp[{self._maxnphotons}]/F")
        output.Branch(f"{self.name}_recoPhScore", self.recoPhScore,              f"{self.name}_recoPhScore[{self._maxnphotons}]/F")
        output.Branch(f"{self.name}_truepid", self.recophoton_truepid,           f"{self.name}_truepid[{self._maxnphotons}]/I")
        output.Branch(f"{self.name}_truepurity", self.recophoton_truepurity,     f"{self.name}_truepurity[{self._maxnphotons}]/F")
        output.Branch(f"{self.name}_truecompleteness", self.recophoton_truecomp, f"{self.name}_truecompleteness[{self._maxnphotons}]/F")


    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def interpretPID(self,ntuplepid):
        """
        output the following categories
        0: cosmic overlay - no monte carlo PID
        1: photon
        2: electron
        3: muon
        4: pion+meson
        5: proton
        6: vertex activity
        7: other
        """
        if ntuplepid==0:
            return 0 # cosmic
        if ntuplepid==22:
            return 1 # photon
        elif abs(ntuplepid)==11:
            return 2 # electron
        elif abs(ntuplepid)==13:
            return 3 # muon
        elif abs(ntuplepid)>100 and abs(ntuplepid)<2000:
            return 4 # pion, other mesons
        elif abs(ntuplepid)==2212 or abs(ntuplepid)==2112:
            return 5 # proton or proton from neutron
        elif abs(ntuplepid)>10000:
            return 6 # this will be the recoil nucleus or nuclear fragment
        else:
            return 7 # catch alll or the rest


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
            self.entryused[numPhotons] = 1
            self.photonEnergies[numPhotons] = ntuple.showerRecoE[i]
            self.photonPositionX[numPhotons] = ntuple.showerStartPosX[i]
            self.photonPositionY[numPhotons] = ntuple.showerStartPosY[i]
            self.photonPositionZ[numPhotons] = ntuple.showerStartPosZ[i]

            #Some information for potential cuts
            photonFromChargedScores.append(abs(ntuple.showerFromChargedScore[i]))
            self.recoPur[numPhotons] = ntuple.showerPurity[i]
            self.recoComp[numPhotons] = ntuple.showerComp[i]
            self.recoPhScore[numPhotons] = ntuple.showerPhScore[i]

            if ismc:
                self.recophoton_truepid[numPhotons] = self.interpretPID( ntuple.showerTruePID[i] )
                self.recophoton_truepurity[numPhotons] = ntuple.showerTruePurity[i]
                self.recophoton_truecomp[numPhotons] = ntuple.showerTrueComp[i]

            #Track that we've found a detectable photon
            self.nphotons[0] += 1
            numPhotons += 1
            #Occasionally we get more than 5 photons, but we shouldn't need to worry about storing those
            if self.nphotons[0] >= 5:
                break

        # Find and store data on tracks ID'd as photons
        # First we make sure we're actually looking at something reco thinks is a photon
        for i in range(ntuple.nTracks):
            if not self.include_tracks:
                break

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

    def finalize(self):
        """
        nothing to do after the event loop
        """
        super().finalize()
        return