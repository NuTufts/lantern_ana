import numpy as np
import ROOT
from array import array
from typing import Dict, Any, List
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.utils.fiducial_volume import dwall

@register
class VertexPropertiesProducer(ProducerBaseClass):
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
            'found': array('i', [0]),
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
        self.vertex_vars['found'][0] = 0
        self.vertex_vars['score'][0] = 0.0
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
        """Calculate vertex properties."""
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)
        
        # Reset output variables
        self.setDefaultValues()
        
        # Check if vertex was found
        self.vertex_vars['found'][0] = ntuple.foundVertex
        self.vertex_vars['infiducial'][0] = ntuple.vtxIsFiducial
        
        if ntuple.foundVertex == 1:
            self.vertex_vars['x'][0] = ntuple.vtxX
            self.vertex_vars['y'][0] = ntuple.vtxY
            self.vertex_vars['z'][0] = ntuple.vtxZ
            self.vertex_vars['score'][0] = ntuple.vtxScore
            self.vertex_vars['cosmicfrac'][0] = ntuple.vtxFracHitsOnCosmic
            self.vertex_vars['dwall'][0] = dwall(ntuple.vtxX, ntuple.vtxY, ntuple.vtxZ)
            
            # Calculate pixel fractions
            max_outoftime = 0.0
            max_intime_unreco = 0.0
            for p in range(3):
                try:
                    if hasattr(ntuple, "fracRecoOuttimePixels") and ntuple.fracRecoOuttimePixels[p] > max_outoftime:
                        max_outoftime = ntuple.fracRecoOuttimePixels[p]
                    if hasattr(ntuple, "fracUnrecoIntimePixels") and ntuple.fracUnrecoIntimePixels[p] > max_intime_unreco:
                        max_intime_unreco = ntuple.fracUnrecoIntimePixels[p]
                except AttributeError: # set to -1 to indicate missing info
                    max_outoftime = -1.0
                    max_intime_unreco = -1.0
            
            self.vertex_vars['frac_outoftime_pixels'][0] = max_outoftime
            self.vertex_vars['frac_intime_unreco_pixels'][0] = max_intime_unreco
            
            # MC truth distance if available
            if ismc:
                self.vertex_vars['mc_dist2true'][0] = ntuple.vtxDistToTrue
        
        return self._get_results()
    
    def _get_results(self) -> Dict[str, Any]:
        """Convert array values to a results dictionary."""
        results = {}
        for var_name, var_array in self.vertex_vars.items():
            results[var_name] = var_array[0]
        return results

