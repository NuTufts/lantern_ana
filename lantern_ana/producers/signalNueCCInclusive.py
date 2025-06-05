import numpy as np
from typing import Dict, Any, List
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.utils.get_primary_electron_candidates import get_primary_electron_candidates
from lantern_ana.cuts.fiducial_cuts import fiducial_cut
from lantern_ana.utils.true_particle_counts import get_true_primary_particle_counts 
from math import exp
import ROOT

@register
class signalNueCCInclusive(ProducerBaseClass):
    """
    Producer that creates a flag indicating if event is part of the NueCC inclusive signal
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Configuration
        self.particle_count_params = config.get('part_count_params',self.get_default_particle_thresholds())
        self.fv_params  = config.get('fv_params',{'width':10.0,'apply_scc':False})
        self.fv_params['usetruevtx'] = True
        
        # Output variables 
        self._vars = {
            'is_target_nuecc_inclusive':array('i',[0])
        }

    def get_default_particle_thresholds(self):
        """Get default particle energy thresholds."""
        true_part_cfg = {}
        true_part_cfg['eKE']  = 30.0
        true_part_cfg['muKE'] = 30.0
        true_part_cfg['piKE'] = 30.0
        true_part_cfg['pKE']  = 60.0
        true_part_cfg['gKE']  = 10.0
        true_part_cfg['xKE']  = 60.0

        return true_part_cfg


    def setDefaultValues(self):
        super().setDefaultValues()
        self._vars['is_target_nuecc_inclusive'][0] = 0
    
    def prepareStorage(self, output: Any) -> None:
        """Set up branches in the output ROOT TTree."""
        for var_name, var_array in self._vars.items():
            if var_array.typecode == 'i':
                branch_type = f"{self.name}_{var_name}/I"
            else:
                branch_type = f"{self.name}_{var_name}/F"
            output.Branch(f"{self.name}_{var_name}", var_array, branch_type)
    
    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if event is signal nue CC inclusive."""
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)
        
        # Reset to default
        self.setDefaultValues()
        
        # Only evaluate for MC data
        if not ismc:
            return self._get_results()
        
        # Check if it's from a nue neutrino and CC interaction
        if ntuple.trueNuCCNC != 0 or abs(ntuple.trueNuPDG) != 12:
            return self._get_results()
        
        # Check fiducial volume using true vertex
        pass_fv = fiducial_cut(ntuple, self.fv_params)
        if not pass_fv:
            return self._get_results()
    
        # Check for primary electrons
        counts = get_true_primary_particle_counts(ntuple, self.particle_count_params)
        nprim_e = counts.get(11, 0) + counts.get(-11, 0)
        
        if nprim_e >= 1:
            self._vars['is_target_nuecc_inclusive'][0] = 1

        return self._get_results()

    
    def _get_results(self) -> Dict[str, Any]:
        """Convert array values to a results dictionary."""
        results = {}
        for var_name, var_array in self._vars.items():
            results[var_name] = var_array[0]
        return results