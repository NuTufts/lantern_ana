import numpy as np
from typing import Dict, Any, List
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.utils.get_primary_electron_candidates import get_primary_electron_candidates
from math import exp
import ROOT

@register
class RecoElectronPropertiesProducer(ProducerBaseClass):
    """
    Producer that calculates properties of reconstructed electron candidates.
    This replaces the electron analysis logic previously embedded in cuts.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Configuration
        self._electron_quality_cuts = config.get("electron_quality_cuts", {})
        
        # Output variables for electron properties
        self.electron_vars = {
            'has_primary_electron': array('i', [0]),
            'emax_primary_score': array('f', [0.0]),
            'emax_purity': array('f', [0.0]),
            'emax_completeness': array('f', [0.0]),
            'emax_fromneutral_score': array('f', [0.0]),
            'emax_fromcharged_score': array('f', [0.0]),
            'emax_charge': array('f', [0.0]),
            'emax_econfidence': array('f', [0.0]),
            'emax_fromdwall': array('f', [0.0]),
            'emax_nplaneabove': array('i', [0]),
            'emax_el_normedscore': array('f', [0.0]),
            'emax_fromshower': array('i', [-1]),
            'ccnue_primary_true_completeness': array('f', [0.0]),
        }

    def setDefaultValues(self):
        super().setDefaultValues()
        self.electron_vars['has_primary_electron'][0] = 0
        self.electron_vars['emax_primary_score'][0] = 0.0
        self.electron_vars['emax_purity'][0] = 0.0
        self.electron_vars['emax_completeness'][0] = 0.0
        self.electron_vars['emax_fromneutral_score'][0] = 0.0
        self.electron_vars['emax_fromcharged_score'][0] = 0.0
        self.electron_vars['emax_charge'][0] = 0.0
        self.electron_vars['emax_econfidence'][0] = 0.0
        self.electron_vars['emax_fromdwall'][0] = 0.0
        self.electron_vars['emax_nplaneabove'][0] = 0
        self.electron_vars['emax_el_normedscore'][0] = 0.0
        self.electron_vars['emax_fromshower'][0] = -1
        self.electron_vars['ccnue_primary_true_completeness'][0] = 0.0
    
    def prepareStorage(self, output: Any) -> None:
        """Set up branches in the output ROOT TTree."""
        for var_name, var_array in self.electron_vars.items():
            if var_array.typecode == 'i':
                branch_type = f"{self.name}_{var_name}/I"
            else:
                branch_type = f"{self.name}_{var_name}/F"
            output.Branch(f"{self.name}_{var_name}", var_array, branch_type)
    
    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate electron candidate properties."""
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)
        
        # Reset to defaults
        self.setDefaultValues()
        
        # If no vertex found, return defaults
        if ntuple.foundVertex != 1:
            return self._get_results()
        
        # Get primary electron candidates
        el_candidate_info = get_primary_electron_candidates(ntuple, self._electron_quality_cuts)
        
        # Extract electron information
        elMaxIdx = el_candidate_info['elMaxIdx']
        prim_electron_data = el_candidate_info['prongDict']
        
        if elMaxIdx >= 0:
            self.electron_vars['has_primary_electron'][0] = 1
            emaxdata = prim_electron_data[elMaxIdx]
            
            # Calculate particle ID scores
            spid = [
                emaxdata['larpid[electron]'],
                emaxdata['larpid[photon]'],
                emaxdata['larpid[pion]'],
                emaxdata['larpid[muon]'],
                emaxdata['larpid[proton]']
            ]
            elnormscore = exp(spid[0]) / (exp(spid[0]) + exp(spid[1]) + exp(spid[2]) + exp(spid[3]) + exp(spid[4]))
            
            # Calculate primary/secondary scores
            ptype = [exp(emaxdata['primary']), exp(emaxdata['fromNeutralPrimary']), exp(emaxdata['fromChargedPrimary'])]
            pnorm = ptype[0] + ptype[1] + ptype[2]
            
            # Fill all electron variables
            self.electron_vars['emax_primary_score'][0] = ptype[0] / pnorm
            self.electron_vars['emax_purity'][0] = emaxdata['purity']
            self.electron_vars['emax_completeness'][0] = emaxdata['completeness']
            self.electron_vars['emax_fromneutral_score'][0] = ptype[1] / pnorm
            self.electron_vars['emax_fromcharged_score'][0] = ptype[2] / pnorm
            self.electron_vars['emax_charge'][0] = emaxdata['showerQ']
            self.electron_vars['emax_econfidence'][0] = emaxdata['elconfidence']
            self.electron_vars['emax_fromdwall'][0] = 0.0  # TODO: Calculate from wall distance
            self.electron_vars['emax_nplaneabove'][0] = 0  # TODO: Calculate plane information
            self.electron_vars['emax_el_normedscore'][0] = elnormscore
            
            # Determine if from shower or track
            if elMaxIdx >= 100:
                self.electron_vars['emax_fromshower'][0] = 0  # From track
            else:
                self.electron_vars['emax_fromshower'][0] = 1  # From shower

            # truth check
            if ismc:
                # get particle truth-matched pid
                true_trackid = -1
                true_pid = -1
                true_completeness = 0.0
                if elMaxIdx>=100:
                    true_trackid = ntuple.trackTrueTID[ elMaxIdx-100 ]
                    true_pid = ntuple.trackTruePID[ elMaxIdx-100 ]
                    true_completeness = ntuple.trackTrueComp[ elMaxIdx-100 ]
                else:
                    true_trackid = ntuple.showerTrueTID[ elMaxIdx ]
                    true_pid     = ntuple.showerTruePID[ elMaxIdx ]
                    true_completeness = ntuple.showerTrueComp[ elMaxIdx ]
                
                if true_trackid>=0 and abs(true_pid)==11:
                    # was truth-matched to an electron. check if it is a primary
                    for isim in range( ntuple.nTrueSimParts ):
                        if ntuple.trueSimPartTID[isim]==true_trackid:
                            if ntuple.trueSimPartProcess[isim]==0:
                                # is a primary lepton
                                self.electron_vars['ccnue_primary_true_completeness'][0] = true_completeness
        
        return self._get_results()
    
    def _get_results(self) -> Dict[str, Any]:
        """Convert array values to a results dictionary."""
        results = {}
        for var_name, var_array in self.electron_vars.items():
            results[var_name] = var_array[0]
        return results

    def finalize(self):
        """
        nothing to do after the event loop
        """
        super().finalize()
        return