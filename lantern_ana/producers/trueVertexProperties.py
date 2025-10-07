import numpy as np
import ROOT
from array import array
from typing import Dict, Any, List
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.utils.fiducial_volume import dwall

@register
class TrueVertexPropertiesProducer(ProducerBaseClass):
    """
    Producer that calculates comprehensive vertex properties.
    This combines basic vertex info with additional analysis variables.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        
        # Output variables for vertex properties
        self.vertex_vars = {
            'x': array('f', [-999.0]),
            'y': array('f', [-999.0]),
            'z': array('f', [-999.0]),
            'score': array('f', [0.0]),
            'infiducial': array('i', [0]),
            'cosmicfrac': array('f', [0.0]),
            'dwall': array('f', [0.0]),
            'frac_outoftime_pixels': array('f', [0.0]),
            'frac_intime_unreco_pixels': array('f', [0.0]),
            'mc_dist2true': array('f', [10000.0])
        }
        
    def prepareStorage(self, output):
        """Set up branches in the output ROOT TTree."""
        for var_name, var_array in self.vertex_vars.items():
            if var_array.typecode == 'i':
                branch_type = f"{self.name}_{var_name}/I"
            else:
                branch_type = f"{self.name}_{var_name}/F"
            output.Branch(f"{self.name}_{var_name}", var_array, branch_type)
    
    def setDefaultValues(self):
        super().setDefaultValues()
        self.vertex_vars['x'][0] = -999.0
        self.vertex_vars['y'][0] = -999.0
        self.vertex_vars['z'][0] = -999.0
        self.vertex_vars['infiducial'][0] = 0
        self.vertex_vars['cosmicfrac'][0] = 0.0
        self.vertex_vars['dwall'][0] = -999.0
        self.vertex_vars['frac_outoftime_pixels'][0] = 0.0
        self.vertex_vars['frac_intime_unreco_pixels'][0] = 0.0
        self.vertex_vars['mc_dist2true'][0] = 10000.0
    
    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate true vertex properties."""
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)
        if not ismc:
            return self._get_results()
        
        # Reset output variables
        self.setDefaultValues()
        
        # Check if vertex was found (reco vertex?)
        self.vertex_vars['dwall'][0] = dwall(ntuple.trueVtxX, ntuple.trueVtxY, ntuple.trueVtxZ)
        self.vertex_vars['x'][0] = ntuple.trueVtxX
        self.vertex_vars['y'][0] = ntuple.trueVtxY
        self.vertex_vars['z'][0] = ntuple.trueVtxZ
        
        return self._get_results()
    
    def _get_results(self) -> Dict[str, Any]:
        """Convert array values to a results dictionary."""
        results = {}
        for var_name, var_array in self.vertex_vars.items():
            results[var_name] = var_array[0]
        return results
        
    def finalize(self):
        """ Nothing to do after event loop. """
        return