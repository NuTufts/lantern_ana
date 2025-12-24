# lantern_ana/producers/numu_cc_producers.py
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory
from lantern_ana.utils.fiducial_volume import dwall
from ctypes import c_bool

@register
class MuonPropertiesProducer(ProducerBaseClass):
    """
    Producer that extracts muon properties for CC numu events.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.muon_angle = array('f', [-1.0])
        self.muon_energy = array('f', [-1.0])
        self.muon_pid_score = array('f', [-1.0])
        self.muon_primary_true_completeness = array('f',[-1.0])
        self.muon_containment = array('i',[-1])
        self.muon_endpt_dwall = array('f',[-1.0])

        try:
            from larlite import larlite
            from ROOT import larutil
            self.reverse_sce = larutil.SpaceChargeMicroBooNE( larutil.SpaceChargeMicroBooNE.kMCC9_Backward )
            self.has_larutil = True
            print("[MuonPropertiesProducer] larutil setup.")
        except:
            self.has_larutil = False
            print("[MuonPropertiesProducer] LArUtil NOT SETUP.")
        
    def prepareStorage(self, output):
        """Set up branches in the output ROOT TTree."""
        output.Branch(f"{self.name}_angle", self.muon_angle, f"{self.name}_angle/F")
        output.Branch(f"{self.name}_energy", self.muon_energy, f"{self.name}_energy/F")
        output.Branch(f"{self.name}_pid_score", self.muon_pid_score, f"{self.name}_pid_score/F")
        output.Branch(f"{self.name}_primary_true_completeness", self.muon_primary_true_completeness, f"{self.name}_primary_true_completeness/F")
        output.Branch(f"{self.name}_containment", self.muon_containment, f"{self.name}_containment/I")
        output.Branch(f"{self.name}_endpt_dwall", self.muon_endpt_dwall, f"{self.name}_endpt_dwall/F")

    def setDefaultValues(self):
        self.muon_angle[0] = -1.0
        self.muon_energy[0] = -1.0
        self.muon_pid_score[0] = -1.0
        self.muon_primary_true_completeness[0] = -1.0
        self.muon_containment[0] = -1
        self.muon_endpt_dwall[0] = -1.0
        return 
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Extract muon properties."""
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)
        
        # Reset output variables
        self.muon_angle[0] = -1.0
        self.muon_energy[0] = -1.0
        self.muon_pid_score[0] = -1.0
        
        # Variables to keep track of highest energy muon
        highest_energy = -1.0
        muon_index = -1
        
        # Find highest energy muon track
        for i in range(ntuple.nTracks):
            if (ntuple.trackClassified[i] == 1 and 
                ntuple.trackPID[i] == 13 and 
                ntuple.trackIsSecondary[i] == 0):
                
                # Compare energy to find highest energy muon
                if ntuple.trackRecoE[i] > highest_energy:
                    highest_energy = ntuple.trackRecoE[i]
                    muon_index = i
        
        # If muon found, extract properties
        if muon_index >= 0:
            # Calculate cosine of angle between muon direction and beam
            beam_dir = np.array([0.0, 0.0, 1.0])
            muon_dir = np.array([
                ntuple.trackStartDirX[muon_index],
                ntuple.trackStartDirY[muon_index],
                ntuple.trackStartDirZ[muon_index]
            ])
            
            # Normalize muon direction vector
            norm = np.linalg.norm(muon_dir)
            if norm > 0:
                muon_dir = muon_dir / norm
                self.muon_angle[0] = np.dot(muon_dir, beam_dir)
            
            # Record muon energy
            self.muon_energy[0] = ntuple.trackRecoE[muon_index]
            
            # Record muon PID score
            self.muon_pid_score[0] = ntuple.trackMuScore[muon_index]

            # get muon end point
            muon_endpt = (ntuple.trackEndPosX[muon_index],ntuple.trackEndPosY[muon_index],ntuple.trackEndPosZ[muon_index])
            muon_dwall = -1.0
            if self.has_larutil:
                applied = c_bool(0)
                muon_endpt_sce = self.reverse_sce.ApplySpaceChargeEffect( muon_endpt[0], muon_endpt[1], muon_endpt[2], applied )
                #print("reverse sce applied: reco=",muon_endpt," sce-corrected=",muon_endpt_sce)
                muon_dwall = dwall(muon_endpt_sce[0], muon_endpt_sce[1], muon_endpt_sce[2] )
            else:
                muon_dwall = dwall(muon_endpt[0], muon_endpt[1], muon_endpt[2] )
            self.muon_endpt_dwall[0] = muon_dwall
            if muon_dwall>5.0:
                self.muon_containment[0] = 1
            else:
                self.muon_containment[0] = 0

            # truth check of reconstructed muon
            if ismc:
                # get particle truth-matched pid
                true_trackid = -1
                true_pid = -1
                true_completeness = 0.0
                true_trackid = ntuple.trackTrueTID[ muon_index ]
                true_pid     = ntuple.trackTruePID[ muon_index ]
                true_completeness = ntuple.trackTrueComp[ muon_index ]
                
                if true_trackid>=0 and abs(true_pid)==13:
                    # was truth-matched to a muon. check if it is a primary
                    for isim in range( ntuple.nTrueSimParts ):
                        if ntuple.trueSimPartTID[isim]==true_trackid:
                            if ntuple.trueSimPartProcess[isim]==0:
                                # is a primary lepton
                                self.muon_primary_true_completeness[0] = true_completeness

        
        return {
            "angle": self.muon_angle[0],
            "energy": self.muon_energy[0],
            "pid_score": self.muon_pid_score[0],
            "primary_true_completeness": self.muon_primary_true_completeness[0],
            "containment": self.muon_containment[0],
            "endpt_dwall": self.muon_endpt_dwall[0],
        }

    def finalize(self):
        """
        nothing to do after the event loop
        """
        super().finalize()
        return
