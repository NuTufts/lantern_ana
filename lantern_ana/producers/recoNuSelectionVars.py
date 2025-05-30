import numpy as np
from typing import Dict, Any, List
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.utils.get_primary_muon_candidates import get_primary_muon_candidates
from math import sqrt, exp
import ROOT

@register
class RecoNuSelectionVariablesProducer(ProducerBaseClass):
    """
    This is a collection of possible variables for selecting true neutrino
    vertices from cosmic backgrounds.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self._track_min_len = config.get("track_min_len", 5.0)  # Minimum energy to consider
        
        # Output variables
        # we use a list of sample vars to avoid boilerplate
        self.simple_varlist = [
            'has_primary_electron/I',
            'emax_primary_score/F',
            'emax_purity/F',
            'emax_completeness/F',
            'emax_fromneutral_score/F',
            'emax_fromcharged_score/F',
            'emax_charge/F',
            'emax_econfidence/F',
            'emax_fromdwall/F',
            'emax_nplaneabove/I',
            'emax_el_normedscore/F',
            'emax_fromshower/I',
            'has_primary_electron/I',
            'mumax_primary_score/F',
            'mumax_purity/F',
            'mumax_completeness/F',
            'mumax_fromneutral_score/F',
            'mumax_fromcharged_score/F',
            'mumax_charge/F',
            'mumax_fromdwall/F',
            'mumax_nplaneabove/I',
            'mumax_mu_normedscore/F',
            'mumax_fromshower/I',
            'has_primary_muon/I',
            'vtx_found/I',
            'vtx_infiducial/I',
            'vtx_kpscore/F',
            'vtx_dwall/F',
            'vtx_cosmicfrac/F',
            'frac_outoftime_pixels/F',
            'frac_intime_unreco_pixels/F',
            'nMuTracks/I',
            'max_muscore/F',
            'max_mucharge/F',
            'ntracks_above/I',
            'mc_dist2true/F'
        ]

        # add these
        # eventTree.Branch("vtxMaxIntimePixelSum", vtxMaxIntimePixelSum, "vtxMaxIntimePixelSum/F")
        # eventTree.Branch("vtxKPtype", vtxKPtype, 'vtxKPtype/I')
        # eventTree.Branch("vtxKPscore", vtxKPscore, 'vtxKPtype/F')
        # eventTree.Branch("vtxFracHitsOnCosmic", vtxFracHitsOnCosmic, 'vtxFracHitsOnCosmic/F')
        # eventTree.Branch("fracUnrecoIntimePixels", fracUnrecoIntimePixels, 'fracUnrecoIntimePixels[3]/F')
        # eventTree.Branch("fracRecoOuttimePixels", fracRecoOuttimePixels, 'fracRecoOuttimePixels[3]/F')

        for varname in self.simple_varlist:
            if varname[-1]=='F':
                self.__dict__[varname] = array('f',[0.0])
            elif varname[-1]=='I':
                self.__dict__[varname] = array('i',[0])

    
    def prepareStorage(self, output: Any) -> None:
        """Set up branches in the output ROOT TTree."""
        # Assuming output is a ROOT TTree or similar interface
        for varname in self.simple_varlist:
            output.Branch(f'{self.name}_{varname[:-2]}',self.__dict__[varname], f'{self.name}_{varname}')

    def setDefaultValues(self):
        super().setDefaultValues()
        for varname in self.simple_varlist:
            if varname[-1]=='F':
                self.__dict__[varname][0] = 0.0
            elif varname[-1]=='I':
                self.__dict__[varname][0] = 0
    
    def productType(self) -> type:
        """Return the type of product (a dictionary in this case)."""
        return dict
    
    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple", "recoElectron", "recoMuonTrack"]  # We need the ntuple and producer data
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Process an event by calculating track energy statistics."""
        # Get input data from producers
        ntuple = data["gen2ntuple"]
        electron_data = data.get("recoElectron", {})
        muon_data = data.get("recoMuonTrack", {})

        results = {}
        
        # Copy electron variables from electron producer
        electron_vars = [
            'has_primary_electron/I',
            'emax_primary_score/F',
            'emax_purity/F', 
            'emax_completeness/F',
            'emax_fromneutral_score/F',
            'emax_fromcharged_score/F',
            'emax_charge/F',
            'emax_econfidence/F',
            'emax_fromdwall/F',
            'emax_nplaneabove/I',
            'emax_el_normedscore/F',
            'emax_fromshower/I'
        ]
        
        for varname in electron_vars:
            var_key = varname[:-2]  # Remove /I or /F suffix
            if var_key in electron_data:
                self.__dict__[varname][0] = electron_data[var_key]
                results[varname] = electron_data[var_key]
        
        # Copy muon variables from muon producer  
        muon_vars = [
            'max_muscore/F',
            'max_mucharge/F',
            'nMuTracks/I'
        ]
        
        for varname in muon_vars:
            var_key = varname[:-2]  # Remove /I or /F suffix
            if var_key in muon_data:
                self.__dict__[varname][0] = muon_data[var_key]
                results[varname] = muon_data[var_key]

        # Copy vertex variables from vertex producer
        vertex_data = data.get("vertex_properties", {})
        vertex_vars = [
            'vtx_found/I',
            'vtx_infiducial/I',
            'vtx_kpscore/F',
            'vtx_dwall/F',
            'vtx_cosmicfrac/F',
            'frac_outoftime_pixels/F',
            'frac_intime_unreco_pixels/F',
            'mc_dist2true/F'
        ]
        
        vertex_map = {
            'vtx_found/I': 'found',
            'vtx_infiducial/I': 'infiducial', 
            'vtx_kpscore/F': 'score',
            'vtx_dwall/F': 'dwall',
            'vtx_cosmicfrac/F': 'cosmicfrac',
            'frac_outoftime_pixels/F': 'frac_outoftime_pixels',
            'frac_intime_unreco_pixels/F': 'frac_intime_unreco_pixels',
            'mc_dist2true/F': 'mc_dist2true'
        }
        
        for varname in vertex_vars:
            if varname in vertex_map and vertex_map[varname] in vertex_data:
                self.__dict__[varname][0] = vertex_data[vertex_map[varname]]
                results[varname] = vertex_data[vertex_map[varname]]
        
        # Copy remaining muon variables that weren't handled above
        if 'ntracks_above_threshold' in muon_data:
            self.__dict__['ntracks_above/I'][0] = muon_data['ntracks_above_threshold']
            results['ntracks_above/I'] = muon_data['ntracks_above_threshold']

        # Return results
        return results