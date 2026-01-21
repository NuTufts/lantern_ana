"""
This producer implements the 6 selection cuts for neutrino events and flags
whether events are charge current (CC) or neutral current (NC) interactions.

The 6 cuts are:
1) LArMatch-identified neutrino candidate vertex found inside the fiducial volume
2) 3D spacepoints of prongs attached to neutrino candidate do not all overlap with Wire-Cell-tagged cosmics
3) No LArPID-identified muon tracks are attached to neutrino candidate
4) At least one LArPID-identified electron shower is attached to neutrino candidate, 
   the largest (in visible energy) of which is also classified as a primary final state particle
5) No tracks attached to neutrino candidate have a high LArPID muon score: max log(muon score) < −3.7
6) The largest identified electron was classified by LArPID as an electron with high confidence: 
   log(electron score) - (log(pion score) + log(photon score))/2 > 7.1
"""

import numpy as np
from typing import Dict, Any, List
from array import array
from math import log, exp, sqrt
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.utils.get_primary_electron_candidates import get_primary_electron_candidates

@register
class nueIncCCProducer(ProducerBaseClass):
    """
    Producer that implements neutrino event selection cuts and CC/NC classification.
    
    This producer evaluates all 6 selection cuts and determines if the event
    passes the selection criteria. It also flags whether the event is a 
    charge current (CC) or neutral current (NC) interaction based on truth info.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Configuration parameters
        self._muon_score_threshold = config.get("muon_score_threshold", -3.7)
        self._electron_confidence_threshold = config.get("electron_confidence_threshold", 7.1)
        self._cosmic_fraction_threshold = config.get("cosmic_fraction_threshold", 1.0)
        
        # Quality cuts for electron candidates
        self._electron_quality_cuts = config.get("electron_quality_cuts", {
            'min_charge': 0.0,
            'min_completeness': 0.0,
            'min_purity': 0.0
        })
        
        # Output variables for the 6 cuts
        self.cut_variables = {
            'cut1_vertex_fiducial': array('i', [0]),        # Cut 1: Vertex in fiducial volume
            'cut2_cosmic_rejection': array('i', [0]),       # Cut 2: Cosmic ray rejection
            'cut3_no_muon_tracks': array('i', [0]),         # Cut 3: No muon tracks
            'cut4_has_electron': array('i', [0]),           # Cut 4: Has primary electron
            'cut5_low_muon_score': array('i', [0]),         # Cut 5: Low muon scores
            'cut6_electron_confidence': array('i', [0]),    # Cut 6: High electron confidence
            'passes_all_cuts': array('i', [0]),             # Combined selection
            'is_charge_current': array('i', [0]),           # CC vs NC flag
            'is_neutral_current': array('i', [0])           # NC flag (inverse of CC)
        }
        
        # Additional diagnostic variables
        self.diagnostic_variables = {
            'max_track_muon_score': array('f', [-99.0]),    # Highest muon score among tracks
            'electron_confidence': array('f', [-99.0]),     # Electron confidence value
            'cosmic_hit_fraction': array('f', [1.0]),       # Fraction of hits on cosmics
            'n_muon_tracks': array('i', [0]),               # Number of identified muon tracks
            'n_electron_showers': array('i', [0]),          # Number of identified electron showers
            'largest_electron_energy': array('f', [0.0]),   # Energy of largest electron
            'largest_electron_is_primary': array('i', [0]), # Is largest electron primary?
            'reco_nu_energy': array('f', [-1.0]),
            'reco_electron_momentum': array('f', [-1.0]),   # Momentum magnitude of largest electron
            'reco_electron_costheta': array('f', [-999.0])  # Cos theta of largest electron w.r.t. beam
        }
        
        # Truth information (for MC)
        self.truth_variables = {
            'true_nu_pdg': array('i', [0]),                 # True neutrino PDG
            'true_ccnc': array('i', [-1]),                 # True CC/NC (0=CC, 1=NC)
            'true_interaction_mode': array('i', [-1])       # True interaction mode
        }
    
    def prepareStorage(self, output: Any) -> None:
        """Set up branches in the output ROOT TTree."""
        
        # Cut result branches
        for var_name, var_array in self.cut_variables.items():
            branch_type = f"{self.name}_{var_name}/I"
            output.Branch(f"{self.name}_{var_name}", var_array, branch_type)
        
        # Diagnostic branches
        for var_name, var_array in self.diagnostic_variables.items():
            if var_array.typecode == 'i':
                branch_type = f"{self.name}_{var_name}/I"
            else:
                branch_type = f"{self.name}_{var_name}/F"
            output.Branch(f"{self.name}_{var_name}", var_array, branch_type)
        
        # Truth branches
        for var_name, var_array in self.truth_variables.items():
            branch_type = f"{self.name}_{var_name}/I"
            output.Branch(f"{self.name}_{var_name}", var_array, branch_type)
    
    def setDefaultValues(self) -> None:
        """Reset all variables to default values."""
        
        # Reset cut variables to 0 (fail)
        for var_array in self.cut_variables.values():
            var_array[0] = 0
        
        # Reset diagnostic variables
        self.diagnostic_variables['max_track_muon_score'][0] = -99.0
        self.diagnostic_variables['electron_confidence'][0] = -99.0
        self.diagnostic_variables['cosmic_hit_fraction'][0] = 1.0
        self.diagnostic_variables['n_muon_tracks'][0] = 0
        self.diagnostic_variables['n_electron_showers'][0] = 0
        self.diagnostic_variables['largest_electron_energy'][0] = 0.0
        self.diagnostic_variables['largest_electron_is_primary'][0] = 0
        self.diagnostic_variables['reco_nu_energy'][0] = -1.0
        self.diagnostic_variables['reco_electron_momentum'][0] = -1.0
        self.diagnostic_variables['reco_electron_costheta'][0] = -999.0
        
        # Reset truth variables
        self.truth_variables['true_nu_pdg'][0] = 0
        self.truth_variables['true_ccnc'][0] = -1
        self.truth_variables['true_interaction_mode'][0] = -1
    
    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single event and evaluate all selection cuts.
        
        Args:
            data: Dictionary containing ntuple data
            params: Additional parameters (not used currently)
            
        Returns:
            Dictionary with cut results and diagnostic information
        """
        ntuple = data["gen2ntuple"]
        
        ## 
        producer_data = params.get('producer_data', {})
        vertex_data = producer_data.get('vertex_properties', {})
        electron_data = producer_data.get('recoElectron', {})
        muon_data = producer_data.get('recoMuonTrack', {})

        # Reset all variables
        self.setDefaultValues()
        
        # Fill truth information if available
        self._fill_truth_info(ntuple)
        
        # Fill basic reco neutrino energy if available
        if hasattr(ntuple, 'recoNuE'):
            self.diagnostic_variables['reco_nu_energy'][0] = ntuple.recoNuE / 1000.0  # Convert to GeV

        # ===== CUT 1: LArMatch-identified neutrino candidate vertex found inside the fiducial volume =====
        cut1_pass = self._evaluate_cut1_vertex_fiducial(ntuple)
        self.cut_variables['cut1_vertex_fiducial'][0] = int(cut1_pass)
        
        # ===== CUT 2: 3D spacepoints of prongs do not all overlap with Wire-Cell-tagged cosmics =====
        cut2_pass = self._evaluate_cut2_cosmic_rejection(ntuple)
        self.cut_variables['cut2_cosmic_rejection'][0] = int(cut2_pass)
        
        # ===== GET ELECTRON CANDIDATES =====
        electron_candidates = get_primary_electron_candidates(ntuple, self._electron_quality_cuts)
        
        # ===== CUT 3: No LArPID-identified muon tracks attached to neutrino candidate =====
        cut3_pass = self._evaluate_cut3_no_muon_tracks(ntuple)
        self.cut_variables['cut3_no_muon_tracks'][0] = int(cut3_pass)
        
        # ===== CUT 4: At least one LArPID-identified electron shower attached to neutrino candidate =====
        cut4_pass, electron_info = self._evaluate_cut4_has_electron(electron_candidates)
        self.cut_variables['cut4_has_electron'][0] = int(cut4_pass)
        
        # ===== EXTRACT ELECTRON MOMENTUM AND COS THETA =====
        self._extract_electron_kinematics(ntuple, electron_info)
        
        # ===== CUT 5: No tracks have high LArPID muon score (max log(muon score) < −3.7) =====
        cut5_pass = self._evaluate_cut5_low_muon_score(ntuple)
        self.cut_variables['cut5_low_muon_score'][0] = int(cut5_pass)
        
        # ===== CUT 6: Largest electron has high confidence =====
        cut6_pass = self._evaluate_cut6_electron_confidence(electron_candidates, electron_info)
        self.cut_variables['cut6_electron_confidence'][0] = int(cut6_pass)
        
        # ===== COMBINED SELECTION =====
        all_cuts_pass = cut1_pass and cut2_pass and cut3_pass and cut4_pass and cut5_pass and cut6_pass
        self.cut_variables['passes_all_cuts'][0] = int(all_cuts_pass)
        
        # ===== CC/NC CLASSIFICATION =====
        self._classify_cc_nc(ntuple)
        
        return self._get_results()
    
    def _fill_truth_info(self, ntuple) -> None:
        """Fill truth information if available (MC only)."""
        try:
            # Check if truth variables exist (MC only)
            if hasattr(ntuple, 'trueNuPDG'):
                self.truth_variables['true_nu_pdg'][0] = ntuple.trueNuPDG
            if hasattr(ntuple, 'trueNuCCNC'):
                self.truth_variables['true_ccnc'][0] = ntuple.trueNuCCNC
            if hasattr(ntuple, 'trueNuMode'):
                self.truth_variables['true_interaction_mode'][0] = ntuple.trueNuMode
        except AttributeError:
            # Data event - truth info not available
            pass
    
    def _evaluate_cut1_vertex_fiducial(self, ntuple) -> bool:
        """
        Cut 1: LArMatch-identified neutrino candidate vertex found inside the fiducial volume.
        
        Returns True if vertex is found and is in fiducial volume.
        """
        # Check if vertex was found by LArMatch
        vertex_found = getattr(ntuple, 'foundVertex', 0) == 1
        
        # Check if vertex is in fiducial volume
        vertex_fiducial = getattr(ntuple, 'vtxIsFiducial', 0) == 1
        
        return vertex_found and vertex_fiducial
    
    def _evaluate_cut2_cosmic_rejection(self, ntuple) -> bool:
        """
        Cut 2: 3D spacepoints of prongs attached to neutrino candidate do not all overlap 
        with Wire-Cell-tagged cosmics.
        
        Returns True if cosmic hit fraction is below threshold.
        """
        # Get fraction of hits that overlap with tagged cosmic rays
        cosmic_fraction = getattr(ntuple, 'vtxFracHitsOnCosmic', 1.0)
        self.diagnostic_variables['cosmic_hit_fraction'][0] = cosmic_fraction
        
        # Pass if not ALL hits overlap with cosmics (cosmic_fraction < 1.0)
        return cosmic_fraction < (self._cosmic_fraction_threshold - 1e-6) 
    
    def _evaluate_cut3_no_muon_tracks(self, ntuple) -> bool:
        """
        Cut 3: No LArPID-identified muon tracks are attached to neutrino candidate.
        
        Returns True if no muon tracks are identified.
        """
        n_muon_tracks = 0
        
        # Loop through all tracks directly from ntuple
        for i in range(getattr(ntuple, 'nTracks', 0)):
            
            # Skip secondary tracks
            if getattr(ntuple, 'trackIsSecondary', [1])[i] != 0:
                continue
            
            # Skip unclassified tracks
            if getattr(ntuple, 'trackClassified', [0])[i] != 1:
                continue
            
            # Check if track is identified as muon (PDG = 13)
            track_pid = getattr(ntuple, 'trackPID', [0])[i]
            if abs(track_pid) == 13:
                n_muon_tracks += 1
        
        self.diagnostic_variables['n_muon_tracks'][0] = n_muon_tracks
        
        # Pass if no muon tracks found
        return n_muon_tracks == 0
    
    def _evaluate_cut4_has_electron(self, electron_candidates) -> tuple:
        """
        Cut 4: At least one LArPID-identified electron shower is attached to neutrino candidate,
        the largest (in visible energy) of which is also classified as a primary final state particle.
        
        Uses electron candidates from get_primary_electron_candidates function.
        Returns (pass_status, electron_info_dict)
        """
        # Extract electron candidate information
        electron_idx_list = electron_candidates.get('idxlist', [])
        electron_data = electron_candidates.get('prongDict', {})
        elMaxIdx = electron_candidates.get('elMaxIdx', -1)
        
        # Count electron showers and check for primary electrons
        electron_showers = []
        largest_primary_electron_idx = -1
        largest_primary_electron_energy = 0.0
        
        for idx in electron_idx_list:
            if idx in electron_data:
                shower_data = electron_data[idx]
                shower_energy = shower_data.get('showerQ', 0.0)  # Using charge as energy proxy
                shower_process = shower_data.get('process', -1)
                
                # Check if this is identified as an electron
                larpid = shower_data.get('larpid', 0)
                if abs(larpid) == 11:
                    electron_showers.append({
                        'idx': idx,
                        'energy': shower_energy,
                        'process': shower_process,
                        'is_primary': shower_process == 0
                    })
                    
                    # Check if this is the largest primary electron
                    if shower_process == 0 and shower_energy > largest_primary_electron_energy:
                        largest_primary_electron_energy = shower_energy
                        largest_primary_electron_idx = idx
        
        # Store diagnostic information
        self.diagnostic_variables['n_electron_showers'][0] = len(electron_showers)
        self.diagnostic_variables['largest_electron_energy'][0] = largest_primary_electron_energy
        self.diagnostic_variables['largest_electron_is_primary'][0] = int(largest_primary_electron_idx >= 0)
        
        # Cut passes if we have at least one primary electron
        pass_cut = largest_primary_electron_idx >= 0
        
        # Create electron info dictionary
        electron_info = {
            'largest_primary_idx': largest_primary_electron_idx,
            'elMaxIdx': elMaxIdx,
            'all_electrons': electron_showers,
            'electron_data': electron_data
        }
        
        return pass_cut, electron_info
    
    def _extract_electron_kinematics(self, ntuple, electron_info) -> None:
        """
        Extract electron momentum and cos theta from the largest primary electron shower.
        
        This function calculates:
        - Electron momentum magnitude (assuming massless electron for EM showers)
        - Cos theta with respect to the beam direction (z-axis)
        """
        # Get electron information from cut 4
        largest_primary_idx = electron_info['largest_primary_idx']
        
        if largest_primary_idx < 0:
            # No primary electron found - keep default values
            return
        
        try:
            # Extract energy from ntuple (convert from MeV to GeV)
            if hasattr(ntuple, 'showerRecoE') and largest_primary_idx < len(ntuple.showerRecoE):
                electron_energy_mev = ntuple.showerRecoE[largest_primary_idx]
                electron_energy_gev = electron_energy_mev / 1000.0  # Convert MeV to GeV
                
                # For electromagnetic showers, assume massless particle: p = E
                electron_momentum = electron_energy_gev
                self.diagnostic_variables['reco_electron_momentum'][0] = electron_momentum
            
            # Extract cos theta from ntuple
            if hasattr(ntuple, 'showerCosTheta') and largest_primary_idx < len(ntuple.showerCosTheta):
                cos_theta = ntuple.showerCosTheta[largest_primary_idx]
                self.diagnostic_variables['reco_electron_costheta'][0] = cos_theta
            
        except (IndexError, AttributeError) as e:
            # Handle missing data gracefully - keep default values
            pass
    
    def _evaluate_cut5_low_muon_score(self, ntuple) -> bool:
        """
        Cut 5: No tracks attached to neutrino candidate have a high LArPID muon score.
        Requirement: max log(muon score) < −3.7
        
        Returns True if all track muon scores are below threshold.
        """
        max_muon_score = -99.0
        
        # Loop through all tracks directly from ntuple
        for i in range(getattr(ntuple, 'nTracks', 0)):
            # Skip secondary tracks
            if getattr(ntuple, 'trackIsSecondary', [1])[i] != 0:
                continue
            
            # Skip unclassified tracks
            if getattr(ntuple, 'trackClassified', [0])[i] != 1:
                continue
            
            # Get muon score (already in log scale from LArPID)
            muon_score = getattr(ntuple, 'trackMuScore', [-99.0])[i]
            
            if muon_score > max_muon_score:
                max_muon_score = muon_score
        
        self.diagnostic_variables['max_track_muon_score'][0] = max_muon_score
        
        # Pass if max muon score is below threshold
        return max_muon_score < self._muon_score_threshold
    
    def _evaluate_cut6_electron_confidence(self, electron_candidates, electron_info) -> bool:
        """
        Cut 6: The largest identified electron was classified by LArPID as an electron with high confidence.
        Requirement: log(electron score) − (log(pion score) + log(photon score))/2 > 7.1
        
        Uses electron candidates from get_primary_electron_candidates function.
        Returns True if electron confidence is above threshold.
        """
        # Get electron information from cut 4
        largest_primary_idx = electron_info['largest_primary_idx']
        electron_data = electron_info['electron_data']
        
        if largest_primary_idx < 0 or largest_primary_idx not in electron_data:
            # No primary electron found
            return False
        
        try:
            # Get LArPID scores from candidate data
            candidate_data = electron_data[largest_primary_idx]
            
            electron_score = candidate_data.get('larpid[electron]', -99.0)
            pion_score = candidate_data.get('larpid[pion]', -99.0)
            photon_score = candidate_data.get('larpid[photon]', -99.0)
            
            # Check if scores are valid
            if electron_score == -99.0 or pion_score == -99.0 or photon_score == -99.0:
                return False
            
            # Confidence formula: log(e) - (log(pi) + log(ph))/2
            electron_confidence = electron_score - (pion_score + photon_score) / 2.0
            
            self.diagnostic_variables['electron_confidence'][0] = electron_confidence
            
            # Pass if confidence is above threshold
            return electron_confidence > self._electron_confidence_threshold
            
        except (KeyError, AttributeError):
            return False
    
    def _classify_cc_nc(self, ntuple) -> None:
        """
        Classify event as charge current (CC) or neutral current (NC).
        
        For MC: Use truth information
        For data: Use reconstructed information (presence of charged lepton)
        """
        try:
            # Try to use truth information first (MC)
            if self.truth_variables['true_ccnc'][0] != -1:
                true_ccnc = self.truth_variables['true_ccnc'][0]
                self.cut_variables['is_charge_current'][0] = int(true_ccnc == 0)
                self.cut_variables['is_neutral_current'][0] = int(true_ccnc == 1)
                return
        except:
            pass
        
        # For data or when truth not available, use reconstructed information
        # CC: presence of charged lepton (muon or electron)
        # NC: no charged leptons
        
        has_muon = self.diagnostic_variables['n_muon_tracks'][0] > 0
        has_electron = self.diagnostic_variables['n_electron_showers'][0] > 0
        
        # Classify as CC if we have either muon or electron
        is_cc = has_muon or has_electron
        
        self.cut_variables['is_charge_current'][0] = int(is_cc)
        self.cut_variables['is_neutral_current'][0] = int(not is_cc)
    
    def _get_results(self) -> Dict[str, Any]:
        """Convert array values to a results dictionary."""
        results = {}
        
        # Add cut results
        for var_name, var_array in self.cut_variables.items():
            results[var_name] = var_array[0]
        
        # Add diagnostic variables
        for var_name, var_array in self.diagnostic_variables.items():
            results[var_name] = var_array[0]
        
        # Add truth variables
        for var_name, var_array in self.truth_variables.items():
            results[var_name] = var_array[0]
        
        return results
    
    def finalize(self):
        """Nothing to do after event loop."""
        return