# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array
import sys

@register
class invariantmassproducer(ProducerBaseClass):
    """
    Producer that tracks the location and energy of all photons.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        #We get these variables from the config
        self.nphotons= array('i',[0])
        self.invariantmass=array('f',[0])
        #These variables are what we're interested in passing to the ntuple
       

    def setDefaultValues(self): 
        self.nphotons[0] = 0
        self.invariantmass[0]=0
    
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch("invariantmass", self.invariantmass, "invariantmass/F")

    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        ntuple = data["gen2ntuple"]
        self.setDefaultValues()
    
        photonIDList = []
        photonEnergiesList = []
        photonDirectionXList = []
        photonDirectionYList = []
        photonDirectionZList = []

        for i in range(ntuple.n_true_showers):
            if ntuple.true_shower_pdg[i] != 22:
                continue  # Not a photon

            self.nphotons[0] += 1
            photonIDList.append(i)
            photonEnergiesList.append(ntuple.true_shower_energy[i])
            photonDirectionXList.append(ntuple.true_shower_dir_x[i])
            photonDirectionYList.append(ntuple.true_shower_dir_y[i])
            photonDirectionZList.append(ntuple.true_shower_dir_z[i])

        if self.nphotons[0] < 2:
            return 0  # Need at least 2 photons to compute invariant mass

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

        return {"invariantmass": self.invariantmass[0]}

