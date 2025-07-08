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
       

    def setDefaultValues(self): #Not clear what to do here?
        self.nphotons[0] = 0
        self.invariantmass[0]=0
    
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch("invariantmass", self.invariantmass, "invariantmass/F")

    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]
        self.setDefaultValues()
        
        photonIDList=[]
        photonEnergiesList=[]
        photonStartPosXList=[]
        photonStartPosYList=[]
        photonStartPosZList=[]
        photonDirectionXList=[]
        photonDirectionYList=[]
        photonDirectionZList=[]

        for i in range(ntuple.nShowers):
            #Make sure reco thinks we have a photon
            if ntuple.showerPID[i] != 22:
                continue
            
           
            if ntuple.showerDistToVtx[i] <5:
                continue

            self.nphotons[0] += 1
            photonIDList.append(i)
            photonEnergiesList.append(ntuple.showerRecoE[i])
            photonStartPosXList.append(ntuple.showerStartPosX[i])
            photonStartPosYList.append(ntuple.showerStartPosY[i])
            photonStartPosZList.append(ntuple.showerStartPosZ[i])
            photonDirectionXList.append(ntuple.showerStartDirX[i])
            photonDirectionYList.append(ntuple.showerStartDirY[i])
            photonDirectionZList.append(ntuple.showerStartDirZ[i])


    
        if self.nphotons[0] != 2:
            return 0
        # print("found 2 photons")

        gi1, gi2 = photonIDList[0],photonIDList[1]
        ge1, ge2 = photonEnergiesList[0], photonEnergiesList[1]

        momentumX1 = ge1*photonDirectionXList[0]
        momentumY1 = ge1*photonDirectionYList[0]
        momentumZ1 = ge1*photonDirectionZList[0]
        momentumX2 = ge1*photonDirectionXList[1]
        momentumY2 = ge1*photonDirectionYList[1]
        momentumZ2 = ge1*photonDirectionZList[1]

        self.invariantmass[0] = np.sqrt((np.square(ge1+ge2))-((np.square(photonDirectionXList[0]+photonDirectionXList[1]))+(np.square(photonDirectionYList[0]+photonDirectionYList[1]))+(np.square(photonDirectionZList[0]+photonDirectionZList[1]))))
        # print("invariant mass:", self.invariantmass[0]) 

        return {"invariantmass":self.invariantmass[0]}
