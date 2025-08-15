# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array
import sys
from math import sqrt

@register
class invariantmassproducer(ProducerBaseClass):
    """
    Producer that tracks the location and energy of all photons.
    Cuts events that don't have at least 2 photons and 1 proton.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        #We get these variables from the config
        self.nphotons= array('i',[0])
        self.invariantmass=array('f',[0])
        #These variables are what we're interested in passing to the ntuple
        self.nphotons_reco= array('i',[0])
        self.invariantmass_reco=array('f',[0])
        self.proton=array('i',[0])
        self.proton_truth=array('i',[0])

    def setDefaultValues(self): #Not clear what to do here?
        self.nphotons[0] = 0
        self.invariantmass[0]=0
        self.nphotons_reco[0] = 0
        self.invariantmass_reco[0]=0
        self.proton[0]=0
        self.proton_truth[0]=0

    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch("invariantmass", self.invariantmass, "invariantmass/F")
        output.Branch("invariantmass_reco", self.invariantmass_reco, "invariantmass_reco/F")
        output.Branch("proton", self.proton, "proton/i")
        output.Branch("proton_truth", self.proton_truth, "proton_truth/i")

    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        ntuple = data["gen2ntuple"]
        self.setDefaultValues()
    
        # truth loop
        photonIDList = []
        photonEnergiesList = []
        photonDirectionXList = []
        photonDirectionYList = []
        photonDirectionZList = []

        for i in range(ntuple.nTrueSimParts):
            if ntuple.trueSimPartPDG[i] != 22:
                continue  # Not a photon

            self.nphotons[0] += 1
            photonIDList.append(i)
            photonEnergiesList.append(ntuple.trueSimPartE[i])
            px = ntuple.trueSimPartPx[i]
            py = ntuple.trueSimPartPy[i]
            pz = ntuple.trueSimPartPz[i]
            pnorm = sqrt(px*px+py*py+pz*pz)
            photonDirectionXList.append(ntuple.trueSimPartPx[i]/pnorm)
            photonDirectionYList.append(ntuple.trueSimPartPy[i]/pnorm)
            photonDirectionZList.append(ntuple.trueSimPartPz[i]/pnorm)

        # Cut events with less than 2 true photons
        if self.nphotons[0] < 2:
            return 0  # Event cut: Need at least 2 photons

        ge1, ge2 = photonEnergiesList[0], photonEnergiesList[1]

        momentumX1 = ge1 * photonDirectionXList[0]
        momentumY1 = ge1 * photonDirectionYList[0]
        momentumZ1 = ge1 * photonDirectionZList[0]
        momentumX2 = ge2 * photonDirectionXList[1]
        momentumY2 = ge2 * photonDirectionYList[1]
        momentumZ2 = ge2 * photonDirectionZList[1]

        total_E = ge1 + ge2
        total_px = momentumX1 + momentumX2
        total_py = momentumY1 + momentumY2
        total_pz = momentumZ1 + momentumZ2

        self.invariantmass[0] = np.sqrt(max(0, total_E**2 - (total_px**2 + total_py**2 + total_pz**2)))

        # truth loop for protons
        for i in range(ntuple.nTrueSimParts):
            if ntuple.trueSimPartPDG[i] == 2212:  # Proton PDG code
                self.proton_truth[0] += 1

        # Cut events without at least 1 truth proton
        if self.proton_truth[0] < 1:
            return 0  # Event cut: Need at least 1 truth proton

        # reco loop
        photonIDList = []
        photonEnergiesList = []
        photonDirectionXList = []
        photonDirectionYList = []
        photonDirectionZList = []

        for i in range(ntuple.nShowers):
            #if ntuple.showerTruePID[i] != 22:
            #continue  # Not a photon

            if ntuple.showerIsSecondary[i]!=1:
                continue
            if ntuple.showerClassified[i]!=1:
                continue
            if ntuple.showerPID[i]!=22:
                continue

            self.nphotons_reco[0] += 1
            photonIDList.append(i)
            photonEnergiesList.append(ntuple.showerRecoE[i])
            py = ntuple.showerStartDirY[i]*ntuple.showerRecoE[i]
            px = ntuple.showerStartDirX[i]*ntuple.showerRecoE[i]
            pz = ntuple.showerStartDirZ[i]*ntuple.showerRecoE[i]
            pnorm = sqrt(px*px+py*py+pz*pz)
            photonDirectionXList.append(ntuple.showerStartDirX[i]/pnorm)
            photonDirectionYList.append(ntuple.showerStartDirY[i]/pnorm)
            photonDirectionZList.append(ntuple.showerStartDirZ[i]/pnorm)

        # Cut events with less than 2 reconstructed photons
        if self.nphotons_reco[0] < 2:
            return 0  # Event cut: Need at least 2 reconstructed photons

        ge1, ge2 = photonEnergiesList[0], photonEnergiesList[1]

        momentumX1 = ge1 * photonDirectionXList[0]
        momentumY1 = ge1 * photonDirectionYList[0]
        momentumZ1 = ge1 * photonDirectionZList[0]
        momentumX2 = ge2 * photonDirectionXList[1]
        momentumY2 = ge2 * photonDirectionYList[1]
        momentumZ2 = ge2 * photonDirectionZList[1]

        total_E = ge1 + ge2
        total_px = momentumX1 + momentumX2
        total_py = momentumY1 + momentumY2
        total_pz = momentumZ1 + momentumZ2

        self.invariantmass_reco[0] = np.sqrt(max(0, total_E**2 - (total_px**2 + total_py**2 + total_pz**2)))

        # look for proton
        self.proton[0]=0
        
        for i in range(ntuple.nTracks):
            if ntuple.trackIsSecondary[i]!=1:
                continue
            if ntuple.trackClassified[i]!=1:
                continue
            if ntuple.trackPID[i]==2212:
                self.proton[0]+=1

        # Cut events without at least 1 proton
        if self.proton[0] < 1:
            return 0  # Event cut: Need at least 1 proton

        return {"invariantmass": self.invariantmass[0],
                "invariantmass_reco": self.invariantmass_reco[0], 
                "proton": self.proton[0], 
                "proton_truth": self.proton_truth[0]}