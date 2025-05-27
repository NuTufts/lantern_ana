import numpy as np
from typing import Dict, Any, List
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
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
            'vtx_kpscore/F',
            'vtx_dwall/F',
            'vtx_cosmicfrac/F',
            'nMuTracks/I',
            'max_muscore/F',
            'max_mucharge/F',
            'ntracks_above/I',
            'mc_dist2true/F'
        ]
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
        return ["gen2ntuple",'reco_nue_CCinc']  # We need the ntuple and the cutdata
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Process an event by calculating track energy statistics."""
        # Get gen2ntuple from input data
        ntuple = data["gen2ntuple"]
        cutdata = data['cutdata_reco_nue_CCinc']

        results = {}
        for varname in self.simple_varlist:
            if varname in cutdata:
                self.__dict__[varname][0] = cutdata[varname]
                results[varname] = cutdata[varname]

        # Return results
        return results