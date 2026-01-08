import numpy as np
from typing import Dict, Any, List
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.utils.get_primary_electron_candidates import get_primary_electron_candidates
from lantern_ana.cuts.fiducial_cuts import fiducial_cut
from lantern_ana.utils.true_particle_counts import get_true_primary_particle_counts 
from lantern_ana.utils.kinematics import KE_from_fourmom
from lantern_ana.utils import transverse_kinematic_imbalance as tki
import math
import ROOT

@register
class signalDefinitionCCnumuPiPlusNProton(ProducerBaseClass):
    """
    Producer that creates a flag indicating if the event is in the signal definition
    for CC numu 1 charged pion + N proton.

    This is the target final state channel for Polina's TKI analysis.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Configuration
        self.particle_count_params = config.get('part_count_params',self.get_default_particle_thresholds())
        self.fv_params  = config.get('fv_params',{'width':10.0,'apply_scc':False,'ismc':True})
        self.fv_params['usetruevtx'] = True

        # mass values
        self.mp  = 938.27209 # MeV
        self.mpi = 139.57039 # MeV
        self.mmu = 105.66 # MeV
        
        # Output variables 
        self._vars = {
            'is_target_cc_numu_1pi_nproton':array('i',[0]),
            'is_infv':array('i',[0]),
            'is_muon_contained':array('i',[0]),
            'is_pion_contained':array('i',[0]),
            'is_maxproton_contained':array('i',[0]),
            'muonKE':array('f',[0.0]),
            'protonKE':array('f',[0.0]),
            'pionKE':array('f',[0.0]), 
            'delPTT':array('f',[0.0]),
            'pN':array('f',[0.0]),
            'delAlphaT':array('f',[0.0]),
            'hadronicM':array('f',[0.0]),
            'debug_eNu':array('f',[0.0]),
            'debug_zX':array('f',[0.0]),
            'debug_zY':array('f',[0.0]),
            'debug_zZ':array('f',[0.0]),
            'debug_muMomFromDirX':array('f',[0.0]),
            'debug_muMomFromDirY':array('f',[0.0]),
            'debug_muMomFromDirZ':array('f',[0.0]),
            'debug_piMomFromDirX':array('f',[0.0]),
            'debug_piMomFromDirY':array('f',[0.0]),
            'debug_piMomFromDirZ':array('f',[0.0]),
            'debug_pMomFromDirX':array('f',[0.0]),
            'debug_pMomFromDirY':array('f',[0.0]),
            'debug_pMomFromDirZ':array('f',[0.0]),
            'debug_delPTX':array('f',[0.0]),
            'debug_delPTY':array('f',[0.0]),
            'debug_delPTZ':array('f',[0.0]),
            'debug_pL':array('f',[0.0]),
            'debug_energyMu':array('f',[0.0]),
            'debug_energyPi':array('f',[0.0]),
            'debug_energyP':array('f',[0.0])
        }

    def get_default_particle_thresholds(self):
        """Get default particle energy thresholds."""
        true_part_cfg = {}

        # min thresholds (MeV)
        true_part_cfg['eKE']  = float('inf') # don't want any primary electrons
        true_part_cfg['muKE'] = 0.0
        true_part_cfg['piKE'] = 16.62
        true_part_cfg['pKE']  = 46.8
        true_part_cfg['gKE']  = float('inf') # don't want any primary photons
        true_part_cfg['nKE']  = 0.0 # any neutrons allowed
        true_part_cfg['xKE']  = float('inf') # don't want any other primary particles

        # max thresholds (MeV)
        true_part_cfg['eKE_max']  = float('inf')
        true_part_cfg['muKE_max'] = 1398.06
        true_part_cfg['piKE_max'] = float('inf')
        true_part_cfg['pKE_max']  = 433.01
        true_part_cfg['gKE_max']  = float('inf')
        true_part_cfg['nKE_max']  = float('inf')
        true_part_cfg['xKE_max']  = float('inf')

        return true_part_cfg


    def setDefaultValues(self):
        super().setDefaultValues()
        for varname in self._vars:
            if self._vars[varname].typecode == 'i':
                self._vars[varname][0] = 0
            elif self._vars[varname].typecode == 'f':
                self._vars[varname][0] = 0.0
    
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
        """Determine if event is signal numu CC charged pion + N proton"""
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)
        self.fv_params['ismc'] = ismc
        
        # Reset to default
        self.setDefaultValues()
        
        # Only evaluate for MC data
        if not ismc:
            return self._get_results()
        
        # Check if it's from a numu and CC interaction
        if ntuple.trueNuCCNC != 0 or abs(ntuple.trueNuPDG) != 14:
            return self._get_results()
        
        # Check fiducial volume using true vertex
        pass_fv = fiducial_cut(ntuple, self.fv_params)
        #print("fv pars: ",self.fv_params," result=",pass_fv)
        if pass_fv:
            self._vars['is_infv'][0] = 1
        else:
            self._vars['is_infv'][0] = 0

        # Count primary particles that pass thresholds
        counts = get_true_primary_particle_counts(ntuple, self.particle_count_params)
        indices = counts['indices']

        
        
        # get number of primary particles
        nprim_mu = counts.get(13,0)
        nprim_proton = counts.get(2212,0)
        nprim_charged_pi = counts.get(211,0) + counts.get(-211,0)
        nprim_npi = counts.get(111,0) # neutral pions
        #print("nprim_mu: ",nprim_mu)

        if nprim_npi > 0: # kick out events with primary neutral pions, according to genie
            return self._get_results()
        
        # Note if there is a geant-tracked primary particle that is NOT a muon, proton, charged pion, 
        # or neutron, this event is not included. This is because the min and max energy thresholds
        # for xKE ("all other particles") is (inf, inf), meaning none of these events are 
        # included in the counts. 

        if nprim_mu>0:
            for pid in [13]:
                if pid in indices:
                    for idx in indices[pid]:
                        if ntuple.trueSimPartContained[idx]==1:
                            self._vars['is_muon_contained'][0] = 1

                        muKE = KE_from_fourmom( ntuple.trueSimPartPx[idx],
                                                ntuple.trueSimPartPy[idx],
                                                ntuple.trueSimPartPz[idx],
                                                ntuple.trueSimPartE[idx] )

                        self._vars['muonKE'][0] = muKE
                        muMomFromDir = np.array([ntuple.trueSimPartPx[idx]/1000., ntuple.trueSimPartPy[idx]/1000., ntuple.trueSimPartPz[idx]/1000.]) # convert to GeV
                        energyMu = ntuple.trueSimPartE[idx]/1000. # convert to GeV

        if nprim_charged_pi>0:
            self._vars['is_pion_contained'][0] = 1
            maxpionidx = -1
            maxpionE = 0.0
            for pid in [-211,211]:
                if pid in indices:
                    for idx in indices[pid]:
                        if ntuple.trueSimPartE[idx]>maxpionE:
                            maxpionE = ntuple.trueSimPartE[idx]
                            maxpionidx = idx
                        if ntuple.trueSimPartContained[idx]==0:
                            # if any uncontained, make flag as uncontained
                            self._vars['is_pion_contained'][0] = 0
            if maxpionidx>=0:
                piKE = KE_from_fourmom( ntuple.trueSimPartPx[maxpionidx],
                                        ntuple.trueSimPartPy[maxpionidx],
                                        ntuple.trueSimPartPz[maxpionidx],
                                        ntuple.trueSimPartE[ maxpionidx] )
                self._vars['pionKE'][0] = piKE
                piMomFromDir = np.array([ntuple.trueSimPartPx[maxpionidx]/1000., ntuple.trueSimPartPy[maxpionidx]/1000., ntuple.trueSimPartPz[maxpionidx]/1000.]) # convert to GeV
                energyPi = ntuple.trueSimPartE[idx]/1000. # convert to GeV
                
        if nprim_proton>0:
            # find max proton energy
            maxidx = -1
            maxprotonE = 0.0
            if 2212 in indices:
                for idx in indices[2212]:
                    if ntuple.trueSimPartE[idx]>maxprotonE:
                        maxprotonE = ntuple.trueSimPartE[idx]
                        maxidx = idx
                if maxidx>=0 and ntuple.trueSimPartContained[maxidx]==1:
                    self._vars['is_maxproton_contained'][0] = 1
                pKE = KE_from_fourmom( ntuple.trueSimPartPx[maxidx],
                                       ntuple.trueSimPartPy[maxidx],
                                       ntuple.trueSimPartPz[maxidx],
                                       ntuple.trueSimPartE[ maxidx] )
                self._vars['protonKE'][0] = pKE
                pMomFromDir = np.array([ntuple.trueSimPartPx[maxidx]/1000., ntuple.trueSimPartPy[maxidx]/1000., ntuple.trueSimPartPz[maxidx]/1000.]) # convert to GeV
                energyP = ntuple.trueSimPartE[idx]/1000. # convert to GeV
            
        # if signal, grab tki variables
        if nprim_mu==1 and nprim_charged_pi==1 and nprim_proton>=1:
            self._vars['is_target_cc_numu_1pi_nproton'][0] = 1
            
            eNu = ntuple.trueNuE # already in GeV

            z = tki.getTransverseAxis( eNu, muMomFromDir[0], muMomFromDir[1], muMomFromDir[2] )
            delPTT = tki.delPTT(z, piMomFromDir, pMomFromDir)
            self._vars['delPTT'][0] = delPTT

            delPT = tki.delPT(piMomFromDir[0], pMomFromDir[0], muMomFromDir[0], piMomFromDir[1], pMomFromDir[1], muMomFromDir[1])
            pL = tki.pL(pMomFromDir[2], muMomFromDir[2], piMomFromDir[2], energyP, energyMu, energyPi, delPT)
            pN = np.sqrt( np.dot(delPT, delPT) + np.dot(pL, pL) )
            self._vars['pN'][0] = pN

            delAlphaT = tki.delAlphaT(muMomFromDir[0], muMomFromDir[1], delPT) 
            self._vars['delAlphaT'][0] = math.degrees(delAlphaT)

            self._vars['hadronicM'][0] = self._calc_hadronic_invariant_mass( piMomFromDir, pMomFromDir, muMomFromDir )

            # debug save vars
            self._vars['debug_eNu'][0] = eNu
            self._vars['debug_zX'][0] = z[0]
            self._vars['debug_zY'][0] = z[1]
            self._vars['debug_zZ'][0] = z[2]
            self._vars['debug_muMomFromDirX'][0] = muMomFromDir[0]
            self._vars['debug_muMomFromDirY'][0] = muMomFromDir[1]
            self._vars['debug_muMomFromDirZ'][0] = muMomFromDir[2]
            self._vars['debug_piMomFromDirX'][0] = piMomFromDir[0]
            self._vars['debug_piMomFromDirY'][0] = piMomFromDir[1]
            self._vars['debug_piMomFromDirZ'][0] = piMomFromDir[2]
            self._vars['debug_pMomFromDirX'][0] = pMomFromDir[0]
            self._vars['debug_pMomFromDirY'][0] = pMomFromDir[1]
            self._vars['debug_pMomFromDirZ'][0] = pMomFromDir[2]
            self._vars['debug_delPTX'][0] = delPT[0]
            self._vars['debug_delPTY'][0] = delPT[1]
            self._vars['debug_delPTZ'][0] = delPT[2]
            self._vars['debug_pL'][0] = pL
            self._vars['debug_energyMu'][0] = energyMu
            self._vars['debug_energyPi'][0] = energyPi
            self._vars['debug_energyP'][0] = energyP


        return self._get_results()

    
    def _get_results(self) -> Dict[str, Any]:
        """Convert array values to a results dictionary."""
        results = {}
        for var_name, var_array in self._vars.items():
            results[var_name] = var_array[0]
        return results

    def _calc_hadronic_invariant_mass( self, p_pion, p_proton, p_muon ):

        # make the 4-mom of the proton and pion using the KE and 3-momentum dir
        E_p  = np.sqrt( (p_proton*p_proton).sum() + self.mp*self.mp ) 
        E_pi = np.sqrt( (p_pion*p_pion).sum() + self.mpi*self.mpi ) 
        E_mu = np.sqrt( (p_muon*p_muon).sum() + self.mmu*self.mmu ) 

        mom4 = np.zeros(4)
        mom4[0] = E_p + E_pi + E_mu
        for i in range(3):
            mom4[i+1] = p_proton[i]+p_pion[i]+p_muon[i]
        gii = np.array((1.0,-1.0,-1.0,-1.0))
        W2 = (mom4*mom4*gii).sum()

        return np.sqrt(W2)

    def finalize(self):
        """ Nothing to do after event loop. """
        return