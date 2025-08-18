# lantern_ana/producers/1gXp_NC_producers.py
import numpy as np
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from array import array


@register
class trueDetectableParticleCountsProducer(ProducerBaseClass):
    """
    Producer that find the reconstructed energy  of all electrons, muons, pions, and protons.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.trueProtonsOverThreshold = array('i',[0])
        self.truePionsOverThreshold = array('i',[0])
        self.trueMuonsOverThreshold = array('i',[0])
        self.trueElectronsOverThreshold = array('i',[0])
        self.trueMuonsBarelyOverThreshold = array('i',[0])
        self.truePionsBarelyOverThreshold = array('i',[0])

    def setDefaultValues(self): #Not clear what to do here?
        self.trueProtonsOverThreshold[0] = 0
        self.truePionsOverThreshold[0] = 0
        self.trueMuonsOverThreshold[0] = 0
        self.trueElectronsOverThreshold[0] = 0

        self.trueMuonsBarelyOverThreshold[0] = 0
        self.truePionsBarelyOverThreshold[0] = 0
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"nTrueProtons", self.trueProtonsOverThreshold, f"nTrueProtons/I")
        output.Branch(f"nTruePions", self.truePionsOverThreshold, f"nTruePions/I")
        output.Branch(f"nTrueMuons", self.trueMuonsOverThreshold, f"nTrueMuons/I")
        output.Branch(f"nTrueElectrons", self.trueElectronsOverThreshold, f"nTrueElectrons/I")
        output.Branch(f"nTrueMuonsBarelyOver",  self.trueMuonsBarelyOverThreshold[0], "nTrueMuonsBarelyOver/I")
        output.Branch(f"nTruePionsBarelyOver",  self.truePionsBarelyOverThreshold[0], "nTruePionsBarelyOver/I")
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Get the energy and x, y, z coordinates of each photon."""
        ntuple = data["gen2ntuple"]

        #Manually reset all variables
        self.setDefaultValues()

        # Only evaluate for MC data
        ismc = params.get('ismc',False)
        if not ismc:
            return {"protons": -1, "pions": -1, "muons": -1, "electrons": -1, "justOverMuons": -1, "justOverPions": -1}


        #Store the numbers of relevant particles over threshold in showers:
        for i in range(ntuple.nTrueSimParts):
            #Check for protons
            if ntuple.trueSimPartPDG[i] == 2212:
                momentumVector = np.square(ntuple.trueSimPartPx[i]) + np.square(ntuple.trueSimPartPy[i]) + np.square(ntuple.trueSimPartPz[i])
                if (np.square(ntuple.trueSimPartE[i])) - momentumVector > 0:
                    kineticMeV = ntuple.trueSimPartE[i] - np.sqrt((np.square(ntuple.trueSimPartE[i])) - momentumVector)
                else:
                    kineticMeV = -999
                if kineticMeV >= 60:
                    self.trueProtonsOverThreshold[0] += 1

            #Check for pions
            elif abs(ntuple.trueSimPartPDG[i]) == 211:
                momentumVector = np.square(ntuple.trueSimPartPx[i]) + np.square(ntuple.trueSimPartPy[i]) + np.square(ntuple.trueSimPartPz[i])
                if (np.square(ntuple.trueSimPartE[i])) - momentumVector > 0:
                    kineticMeV = ntuple.trueSimPartE[i] - np.sqrt((np.square(ntuple.trueSimPartE[i])) - momentumVector)
                else:
                    kineticMeV = -999

                if kineticMeV >= 30:
                    self.truePionsOverThreshold[0] += 1

                    if kineticMeV <= 45:
                        self.truePionsBarelyOverThreshold[0] += 1
            
            #Check for muons
            elif ntuple.trueSimPartPDG[i] == 13:
                momentumVector = np.square(ntuple.trueSimPartPx[i]) + np.square(ntuple.trueSimPartPy[i]) + np.square(ntuple.trueSimPartPz[i])
                if (np.square(ntuple.trueSimPartE[i])) - momentumVector > 0:
                    kineticMeV = ntuple.trueSimPartE[i] - np.sqrt((np.square(ntuple.trueSimPartE[i])) - momentumVector)
                else:
                    kineticMeV = -999                
                
                if kineticMeV >= 100:                    
                    self.trueMuonsOverThreshold[0] += 1

                    if kineticMeV <= 120:
                        self.trueMuonsBarelyOverThreshold[0] += 1

            #Check for electrons
            elif ntuple.trueSimPartPDG[i] == 11: 
                momentumVector = np.square(ntuple.trueSimPartPx[i]) + np.square(ntuple.trueSimPartPy[i]) + np.square(ntuple.trueSimPartPz[i])
                if (np.square(ntuple.trueSimPartE[i])) - momentumVector > 0:
                    kineticMeV = ntuple.trueSimPartE[i] - np.sqrt((np.square(ntuple.trueSimPartE[i])) - momentumVector)
                else:
                    kineticMeV = -999                
                    
                if kineticMeV >= 10:                    
                    self.trueElectronsOverThreshold[0] += 1

        #Store the data as an array:
        trueDetectableParticleDict = {"protons": self.trueProtonsOverThreshold[0], 
            "pions": self.truePionsOverThreshold[0], 
            "muons": self.trueMuonsOverThreshold[0], 
            "electrons": self.trueElectronsOverThreshold[0], 
            "justOverMuons": self.trueMuonsBarelyOverThreshold[0], 
            "justOverPions": self.truePionsBarelyOverThreshold[0]
            }

        return trueDetectableParticleDict