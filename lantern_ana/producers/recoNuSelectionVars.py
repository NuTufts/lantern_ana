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
        self._cutname = config.get('cutname')
        
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
        return ["gen2ntuple",self._cutname]  # We need the ntuple and the cutdata
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Process an event by calculating track energy statistics."""
        # Get gen2ntuple from input data
        ntuple = data["gen2ntuple"]
        cutdata = data[f'cutdata_{self._cutname}']

        results = {}
        for varname in self.simple_varlist:
            if varname in cutdata:
                self.__dict__[varname][0] = cutdata[varname]
                results[varname] = cutdata[varname]

        # add vertex variables
        if ntuple.foundVertex==1:
            # for each we need to get max values
            max_outoftime = 0.0
            max_intime_unreco = 0.0
            for p in range(3):
                if ntuple.fracRecoOuttimePixels[p]>max_outoftime:
                    max_outoftime = ntuple.fracRecoOuttimePixels[p]
                if ntuple.fracUnrecoIntimePixels[p]>max_intime_unreco:
                    max_intime_unreco = ntuple.fracUnrecoIntimePixels[p]

            self.__dict__['frac_outoftime_pixels/F'][0] = max_outoftime
            self.__dict__['frac_intime_unreco_pixels/F'][0] = max_intime_unreco
            results['frac_outoftime_pixels/F'] = max_outoftime
            results['frac_intime_unreco_pixels/F'] = max_intime_unreco

            muon_candidates = get_primary_muon_candidates( ntuple, params )

            muMaxIdx = muon_candidates['muMaxIdx']
            if muMaxIdx>=0:
                prim_muon_data = muon_candidates['prongDict']
                mumaxdata = prim_muon_data[muMaxIdx]
                spid = [ mumaxdata['larpid[electron]'],
                         mumaxdata['larpid[photon]'],
                         mumaxdata['larpid[pion]'],
                         mumaxdata['larpid[muon]'],
                         mumaxdata['larpid[proton]']
                ]
                munormscore = exp(spid[3])/(exp(spid[0])+exp(spid[1])+exp(spid[2])+exp(spid[3])+exp(spid[4]))
        
                ptype = [exp(mumaxdata['primary']),exp(mumaxdata['fromNeutralPrimary']),exp(mumaxdata['fromChargedPrimary'])]
                pnorm = ptype[0]+ptype[1]+ptype[2]

                self.__dict__['mumax_primary_score/F'][0]     = ptype[0]/pnorm
                self.__dict__['mumax_purity/F'][0]            = mumaxdata['purity']
                self.__dict__['mumax_completeness/F'][0]      = mumaxdata['completeness']
                self.__dict__['mumax_fromneutral_score/F'][0] = ptype[1]/pnorm
                self.__dict__['mumax_fromcharged_score/F'][0] = ptype[2]/pnorm
                self.__dict__['mumax_charge/F'][0]            = mumaxdata['showerQ']      
                self.__dict__['mumax_fromdwall/F'][0]         = 0.0
                self.__dict__['mumax_nplaneabove/I'][0]       = 0
                self.__dict__['mumax_mu_normedscore/F'][0]    = munormscore
                self.__dict__['has_primary_muon/I'][0]        = 1

        # Return results
        return results