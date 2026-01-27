# numuIncCCProducer.py
"""
Producer for neutrino candidate selection implementing three key cuts:
1. LArMatch-identified neutrino candidate vertex found inside the fiducial volume
2. 3D space points of prongs attached to neutrino candidate do not all overlap with Wire-Cell-tagged cosmics
3. At least one track attached to the candidate neutrino vertex was identified by LArPID as a muon

Created for neutrino event selection in the Lantern Analysis Framework.
"""

import numpy as np
from typing import Dict, Any, List
from array import array
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.cuts.fiducial_cuts import fiducial_cut

@register
class numuIncCCProducer(ProducerBaseClass):
    """
    Producer that implements the three-cut neutrino candidate selection.
    
    This producer evaluates:
    1. Vertex finding and fiducial volume containment
    2. Cosmic ray rejection based on Wire-Cell tagging
    3. Muon identification using LArPID scores
    
    The producer stores boolean flags and relevant quantities for each cut,
    allowing downstream cuts to make selection decisions.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Configuration parameters
        self.fv_params = config.get('fv_params', {
            'width': 10.0,
            'apply_scc': True,
            'usetruevtx': False,
            'useWCvolume': True  # Use Wire-Cell fiducial volume definition
        })
        
        self.cosmic_rejection_threshold = config.get('cosmic_rejection_threshold', 1.0)
        self.muon_score_threshold = config.get('muon_score_threshold', -3.7)
        
        # Output variables for the three cuts
        self._vars = {
            # Cut 1: Vertex finding and fiducial volume
            'has_vertex_in_fv': array('i', [0]),
            'found_vertex': array('i', [0]),
            'vertex_is_fiducial': array('i', [0]),
            'vertex_x': array('f', [-999.0]),
            'vertex_y': array('f', [-999.0]),
            'vertex_z': array('f', [-999.0]),
            'vertex_score': array('f', [-1.0]),
            
            # Cut 2: Cosmic ray rejection
            'passes_cosmic_rejection': array('i', [0]),
            'vtx_cosmic_fraction': array('f', [0.0]),
            'vtx_containment': array('i', [-1]),
            
            # Cut 3: Muon identification
            'has_muon_track': array('i', [0]),
            'n_muon_tracks': array('i', [0]),
            'max_muon_score': array('f', [-200.0]),
            'max_muon_charge': array('f', [0.0]),
            'best_muon_track_idx': array('i', [-1]),
            
            # Reconstructed muon kinematics
            'reco_muon_momentum': array('f', [-1.0]),     # GeV/c
            'reco_muon_costheta': array('f', [-999.0]),   # cos(theta) w.r.t. beam
            'reco_muon_energy': array('f', [-1.0]),       # GeV
            'reco_muon_length': array('f', [-1.0]),       # cm
            
            # Neutrino classification (MC truth when available)
            'is_cc_interaction': array('i', [-1]),  # -1: unknown, 0: NC, 1: CC
            'is_nc_interaction': array('i', [-1]),  # -1: unknown, 0: CC, 1: NC
            'true_nu_pdg': array('i', [0]),         # Neutrino PDG code
            'true_nu_energy': array('f', [-1.0]),  # True neutrino energy (GeV)
            'true_nu_mode': array('i', [-1]),       # Interaction mode
            'reco_nu_energy': array('f', [-1.0]),  # Reconstructed neutrino energy
            
            # Event-level information
            'n_tracks_total': array('i', [0]),
            'n_showers_total': array('i', [0]),
            
            # Combined selection
            'passes_all_cuts': array('i', [0])
        }

    def setDefaultValues(self):
        """Reset all variables to default values."""
        super().setDefaultValues()
        
        # Cut 1 defaults
        self._vars['has_vertex_in_fv'][0] = 0
        self._vars['found_vertex'][0] = 0
        self._vars['vertex_is_fiducial'][0] = 0
        self._vars['vertex_x'][0] = -999.0
        self._vars['vertex_y'][0] = -999.0
        self._vars['vertex_z'][0] = -999.0
        self._vars['vertex_score'][0] = -1.0
        
        # Cut 2 defaults
        self._vars['passes_cosmic_rejection'][0] = 0
        self._vars['vtx_cosmic_fraction'][0] = 0.0
        self._vars['vtx_containment'][0] = -1
        
        # Cut 3 defaults
        self._vars['has_muon_track'][0] = 0
        self._vars['n_muon_tracks'][0] = 0
        self._vars['max_muon_score'][0] = -200.0
        self._vars['max_muon_charge'][0] = 0.0
        self._vars['best_muon_track_idx'][0] = -1
        
        # Muon kinematics defaults
        self._vars['reco_muon_momentum'][0] = -1.0
        self._vars['reco_muon_costheta'][0] = -999.0
        self._vars['reco_muon_energy'][0] = -1.0
        self._vars['reco_muon_length'][0] = -1.0
        
        # Neutrino classification defaults
        self._vars['is_cc_interaction'][0] = -1
        self._vars['is_nc_interaction'][0] = -1
        self._vars['true_nu_pdg'][0] = 0
        self._vars['true_nu_energy'][0] = -1.0
        self._vars['true_nu_mode'][0] = -1
        self._vars['reco_nu_energy'][0] = -1.0
        
        # Event-level defaults
        self._vars['n_tracks_total'][0] = 0
        self._vars['n_showers_total'][0] = 0
        
        # Combined result
        self._vars['passes_all_cuts'][0] = 0
    
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
        """
        Process one event and evaluate the three cuts.
        
        Args:
            data: Dictionary containing input data (must have 'gen2ntuple')
            params: Processing parameters
            
        Returns:
            Dictionary containing calculated quantities
        """
        ntuple = data["gen2ntuple"]
        
        # =================================================================
        # EXTRACT NEUTRINO CLASSIFICATION (MC truth when available)
        # =================================================================
        
        # Check if this is MC data and extract truth information
        if hasattr(ntuple, 'trueNuCCNC'):
            # trueNuCCNC: 0 for CC, 1 for NC
            is_cc = int(ntuple.trueNuCCNC == 0)
            is_nc = int(ntuple.trueNuCCNC == 1)
            self._vars['is_cc_interaction'][0] = is_cc
            self._vars['is_nc_interaction'][0] = is_nc
        
        if hasattr(ntuple, 'trueNuPDG'):
            self._vars['true_nu_pdg'][0] = ntuple.trueNuPDG
            
        if hasattr(ntuple, 'trueNuE'):
            self._vars['true_nu_energy'][0] = ntuple.trueNuE  # Already in GeV
            
        if hasattr(ntuple, 'trueNuMode'):
            # trueNuMode: 0=QE, 1=Res, 2=DIS, 3=Coh, 10=MEC
            self._vars['true_nu_mode'][0] = ntuple.trueNuMode
        
        # Extract reconstructed neutrino energy (convert from MeV to GeV if needed)
        if hasattr(ntuple, 'recoNuE'):
            # recoNuE is in MeV according to documentation
            self._vars['reco_nu_energy'][0] = ntuple.recoNuE / 1000.0  # Convert to GeV
        
        # Extract event-level track/shower counts
        if hasattr(ntuple, 'nTracks'):
            self._vars['n_tracks_total'][0] = ntuple.nTracks
        if hasattr(ntuple, 'nShowers'):
            self._vars['n_showers_total'][0] = ntuple.nShowers
        
        # =================================================================
        # CUT 1: LArMatch-identified neutrino candidate vertex found inside 
        #        the fiducial volume
        # =================================================================
        
        # Check if a vertex was found by LArMatch
        has_vertex = hasattr(ntuple, 'foundVertex') and ntuple.foundVertex == 1
        self._vars['found_vertex'][0] = int(has_vertex)
        
        if has_vertex:
            # Store vertex properties from ntuple
            self._vars['vertex_x'][0] = ntuple.vtxX
            self._vars['vertex_y'][0] = ntuple.vtxY  
            self._vars['vertex_z'][0] = ntuple.vtxZ
            self._vars['vertex_score'][0] = ntuple.vtxScore
            
            # Check fiducial volume using the configured method
            # We can use either Wire-Cell definition or custom fiducial cut
            if self.fv_params.get('useWCvolume', True):
                # Use the pre-computed Wire-Cell fiducial volume flag
                is_fiducial = ntuple.vtxIsFiducial == 1
            else:
                # Use custom fiducial volume calculation
                is_fiducial = fiducial_cut(ntuple, self.fv_params)
            
            self._vars['vertex_is_fiducial'][0] = int(is_fiducial)
            self._vars['has_vertex_in_fv'][0] = int(has_vertex and is_fiducial)
        else:
            self._vars['vertex_is_fiducial'][0] = 0
            self._vars['has_vertex_in_fv'][0] = 0
        
        # =================================================================
        # CUT 2: 3D space points of prongs attached to neutrino candidate 
        #        do not all overlap with Wire-Cell-tagged cosmics
        # =================================================================
        
        if has_vertex:
            # Get cosmic overlap fraction for vertex-associated hits
            # vtxFracHitsOnCosmic: fraction of all hits associated with reco neutrino vertex 
            # that match cosmic-tagged pixels
            cosmic_fraction = ntuple.vtxFracHitsOnCosmic
            self._vars['vtx_cosmic_fraction'][0] = cosmic_fraction
            
            # Get containment information (relates to cosmic rejection)
            # vtxContainment: 2=fully contained, 1=vertex in FV but some hits outside, 0=vertex outside FV
            self._vars['vtx_containment'][0] = ntuple.vtxContainment
            
            # Passes cosmic rejection if not all hits overlap with cosmics
            # (i.e., cosmic_fraction < 1.0 means some hits are not cosmic-tagged)
            passes_cosmic = cosmic_fraction < self.cosmic_rejection_threshold
            self._vars['passes_cosmic_rejection'][0] = int(passes_cosmic)
        else:
            self._vars['vtx_cosmic_fraction'][0] = 0.0
            self._vars['vtx_containment'][0] = -1
            self._vars['passes_cosmic_rejection'][0] = 0
        
        # =================================================================
        # CUT 3: At least one track attached to the candidate neutrino vertex 
        #        was identified by LArPID as a muon
        # =================================================================
        
        # Reset muon-related variables
        max_muon_score = -200.0
        max_muon_charge = 0.0
        n_muon_tracks = 0
        best_muon_idx = -1
        
        if has_vertex and hasattr(ntuple, 'nTracks') and ntuple.nTracks > 0:
            # Loop through all tracks associated with the vertex
            for iTrack in range(ntuple.nTracks):
                # Skip secondary tracks (only consider primary tracks from vertex)
                # trackIsSecondary: 1 if track was attached as secondary particle
                if (hasattr(ntuple, 'trackIsSecondary') and 
                    ntuple.trackIsSecondary[iTrack] != 0):
                    continue
                
                # Skip unclassified tracks (LArPID didn't process them)
                # trackClassified: 1 if track was classified by LArPID
                if (hasattr(ntuple, 'trackClassified') and 
                    ntuple.trackClassified[iTrack] != 1):
                    continue
                
                # Check if track was identified as a muon by LArPID
                # trackPID: Predicted PDG code from LArPID (13 = muon, -13 = antimuon)
                if (hasattr(ntuple, 'trackPID') and 
                    abs(ntuple.trackPID[iTrack]) == 13):  # PDG code for muon
                    n_muon_tracks += 1
                
                # Track the highest muon score
                # trackMuScore: Track's muon score from LArPID
                if hasattr(ntuple, 'trackMuScore'):
                    muon_score = ntuple.trackMuScore[iTrack]
                    if muon_score > max_muon_score:
                        max_muon_score = muon_score
                        best_muon_idx = iTrack
                        # trackCharge: Sum of pixel values for pixels associated with track hits
                        if hasattr(ntuple, 'trackCharge'):
                            max_muon_charge = ntuple.trackCharge[iTrack]
        
        # Store muon identification results
        self._vars['n_muon_tracks'][0] = n_muon_tracks
        self._vars['max_muon_score'][0] = max_muon_score
        self._vars['max_muon_charge'][0] = max_muon_charge
        self._vars['best_muon_track_idx'][0] = best_muon_idx
        
        # A track is considered a muon if it has a high enough muon score
        # (alternative to strict PID assignment)
        has_muon = (n_muon_tracks > 0) or (max_muon_score > self.muon_score_threshold)
        self._vars['has_muon_track'][0] = int(has_muon)
        
        # =================================================================
        # CALCULATE MUON KINEMATICS for the best muon candidate
        # =================================================================
        
        if best_muon_idx >= 0 and has_muon:
            # Get muon track properties from ntuple
            muon_idx = best_muon_idx
            
            # Calculate muon momentum and kinetic energy from trackRecoE
            if hasattr(ntuple, 'trackRecoE'):
                # trackRecoE: reconstructed kinetic energy in MeV
                muon_ke_mev = ntuple.trackRecoE[muon_idx]  
                muon_ke_gev = muon_ke_mev / 1000.0  # Convert to GeV
                
                # Calculate momentum using muon mass (105.66 MeV/c²)
                muon_mass_gev = 0.10566  # GeV/c²
                muon_total_energy = muon_ke_gev + muon_mass_gev
                
                # Relativistic momentum calculation: p = sqrt(E_total² - m²)
                if muon_total_energy > muon_mass_gev:  # Ensure physical result
                    muon_momentum = ((muon_total_energy**2 - muon_mass_gev**2)**0.5)
                    self._vars['reco_muon_momentum'][0] = muon_momentum
                    self._vars['reco_muon_energy'][0] = muon_ke_gev
                else:
                    # If energy is unphysical, set to invalid values
                    self._vars['reco_muon_momentum'][0] = -1.0
                    self._vars['reco_muon_energy'][0] = -1.0
            
            # Fallback: try trackRangeE if trackRecoE is not available
            elif hasattr(ntuple, 'trackRangeE'):
                print("Warning: trackRecoE not found, falling back to trackRangeE")
                muon_ke_mev = ntuple.trackRangeE[muon_idx]  
                muon_ke_gev = muon_ke_mev / 1000.0
                
                muon_mass_gev = 0.10566
                muon_total_energy = muon_ke_gev + muon_mass_gev
                
                if muon_total_energy > muon_mass_gev:
                    muon_momentum = ((muon_total_energy**2 - muon_mass_gev**2)**0.5)
                    self._vars['reco_muon_momentum'][0] = muon_momentum
                    self._vars['reco_muon_energy'][0] = muon_ke_gev
                else:
                    self._vars['reco_muon_momentum'][0] = -1.0
                    self._vars['reco_muon_energy'][0] = -1.0
            
            # Calculate cos(theta) from track direction
            if (hasattr(ntuple, 'trackStartDirX') and 
                hasattr(ntuple, 'trackStartDirY') and 
                hasattr(ntuple, 'trackStartDirZ')):
                
                # Get track direction vector (should be unit vector)
                dir_x = ntuple.trackStartDirX[muon_idx]
                dir_y = ntuple.trackStartDirY[muon_idx]
                dir_z = ntuple.trackStartDirZ[muon_idx]
                
                # Verify we have valid direction components
                if (abs(dir_x) < 900 and abs(dir_y) < 900 and abs(dir_z) < 900):
                    # Beam direction is along z-axis (0, 0, 1)
                    # cos(theta) = dir_z (since beam is unit vector along z)
                    cos_theta = dir_z
                    self._vars['reco_muon_costheta'][0] = cos_theta
            
            # Alternative: use trackCosTheta if available directly
            elif hasattr(ntuple, 'trackCosTheta'):
                cos_theta = ntuple.trackCosTheta[muon_idx]
                if abs(cos_theta) <= 1.0:  # Valid cos(theta) range
                    self._vars['reco_muon_costheta'][0] = cos_theta
            
            # Get track length if available
            if hasattr(ntuple, 'trackLength'):
                track_length = ntuple.trackLength[muon_idx]
                if track_length > 0:  # Valid length
                    self._vars['reco_muon_length'][0] = track_length
        
        # =================================================================
        # COMBINED SELECTION: All three cuts must pass
        # =================================================================
        
        cut1_pass = self._vars['has_vertex_in_fv'][0] == 1
        cut2_pass = self._vars['passes_cosmic_rejection'][0] == 1
        cut3_pass = self._vars['has_muon_track'][0] == 1
        
        passes_all = cut1_pass and cut2_pass and cut3_pass
        self._vars['passes_all_cuts'][0] = int(passes_all)
        
        # =================================================================
        # RETURN RESULTS
        # =================================================================
        
        return {
            # Cut 1 results
            'has_vertex_in_fv': self._vars['has_vertex_in_fv'][0],
            'found_vertex': self._vars['found_vertex'][0],
            'vertex_is_fiducial': self._vars['vertex_is_fiducial'][0],
            
            # Cut 2 results  
            'passes_cosmic_rejection': self._vars['passes_cosmic_rejection'][0],
            'vtx_cosmic_fraction': self._vars['vtx_cosmic_fraction'][0],
            
            # Cut 3 results
            'has_muon_track': self._vars['has_muon_track'][0],
            'n_muon_tracks': self._vars['n_muon_tracks'][0],
            'max_muon_score': self._vars['max_muon_score'][0],
            
            # Neutrino classification
            'is_cc_interaction': self._vars['is_cc_interaction'][0],
            'is_nc_interaction': self._vars['is_nc_interaction'][0],
            'true_nu_pdg': self._vars['true_nu_pdg'][0],
            'true_nu_energy': self._vars['true_nu_energy'][0],
            'reco_nu_energy': self._vars['reco_nu_energy'][0],
            
            # Event-level info
            'n_tracks_total': self._vars['n_tracks_total'][0],
            'n_showers_total': self._vars['n_showers_total'][0],
            
            # Muon kinematics
            'reco_muon_momentum': self._vars['reco_muon_momentum'][0],
            'reco_muon_costheta': self._vars['reco_muon_costheta'][0],
            'reco_muon_energy': self._vars['reco_muon_energy'][0],
            'reco_muon_length': self._vars['reco_muon_length'][0],
            
            # Combined result
            'passes_all_cuts': self._vars['passes_all_cuts'][0]
        }

    def finalize(self):
        """Nothing to do after event loop."""
        return