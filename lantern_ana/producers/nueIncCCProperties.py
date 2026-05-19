"""
This producer implements the 6 selection cuts for neutrino events and flags
whether events are charge current (CC) or neutral current (NC) interactions.

The 6 cuts are:
1) LArMatch-identified neutrino candidate vertex found inside the fiducial volume
2) 3D spacepoints of prongs attached to neutrino candidate do not all overlap with Wire-Cell-tagged cosmics
3) No LArPID-identified muon tracks are attached to neutrino candidate
4) At least one LArPID-identified electron shower is attached to neutrino candidate,
   the largest (in visible energy) of which is also classified as a primary final state particle
5) No tracks attached to neutrino candidate have a high LArPID muon score: max log(muon score) < -3.7
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
    passes the selection criteria. It also stores truth CC/NC info from the ntuple.
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

        self._vars = {
            # Cut flags
            'cut1_vertex_fiducial':   array('i', [0]),
            'cut2_cosmic_rejection':  array('i', [0]),
            'cut3_no_muon_tracks':    array('i', [0]),
            'cut4_has_electron':      array('i', [0]),
            'cut5_low_muon_score':    array('i', [0]),
            'cut6_electron_confidence': array('i', [0]),
            'passes_all_cuts':        array('i', [0]),

            # Diagnostics
            'vtx_cosmic_fraction':    array('f', [1.0]),
            'is_fully_contained':     array('i', [0]),
            'n_muon_tracks':          array('i', [0]),
            'n_electron_showers':     array('i', [0]),
            'max_track_muon_score':   array('f', [-99.0]),
            'electron_confidence':    array('f', [-99.0]),
            'largest_electron_energy': array('f', [0.0]),
            'reco_nu_energy':         array('f', [-1.0]),
            'reco_electron_momentum': array('f', [-1.0]),
            'reco_electron_costheta': array('f', [-999.0]),

            # Truth (MC only)
            'true_nu_pdg':            array('i', [0]),
            'true_is_cc':              array('i', [-1]), # 0=NC, 1=CC
            'true_ccnc':               array('i', [-1]), # backwards compatibility
            'true_interaction_mode':  array('i', [-1]),
        }

    def prepareStorage(self, output: Any) -> None:
        """Set up branches in the output ROOT TTree."""
        for var_name, var_array in self._vars.items():
            if var_array.typecode == 'i':
                branch_type = f"{self.name}_{var_name}/I"
            else:
                branch_type = f"{self.name}_{var_name}/F"
            output.Branch(f"{self.name}_{var_name}", var_array, branch_type)

    def setDefaultValues(self) -> None:
        """Reset all variables to default values."""
        super().setDefaultValues()

        for var_name, var_array in self._vars.items():
            if var_array.typecode == 'i':
                var_array[0] = 0
            else:
                var_array[0] = -1.0

        # Non-zero float defaults
        self._vars['vtx_cosmic_fraction'][0] = 1.0
        self._vars['max_track_muon_score'][0] = -99.0
        self._vars['electron_confidence'][0] = -99.0
        self._vars['largest_electron_energy'][0] = 0.0
        self._vars['reco_electron_costheta'][0] = -999.0

        # Non-zero int defaults
        self._vars['true_is_cc'][0] = -1
        self._vars['true_ccnc'][0] = -1
        self._vars['true_interaction_mode'][0] = -1

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
        self.setDefaultValues()

        # =================================================================
        # TRUTH INFORMATION (MC only)
        # =================================================================

        if hasattr(ntuple, 'trueNuPDG'):
            self._vars['true_nu_pdg'][0] = ntuple.trueNuPDG
        if hasattr(ntuple, 'trueNuCCNC'):
            self._vars['true_is_cc'][0] = int(1 - ntuple.trueNuCCNC) # 0=NC, 1=CC
            self._vars['true_ccnc'][0] = ntuple.trueNuCCNC # backwards compatibility
        if hasattr(ntuple, 'trueNuMode'):
            self._vars['true_interaction_mode'][0] = ntuple.trueNuMode
        if hasattr(ntuple, 'recoNuE'):
            self._vars['reco_nu_energy'][0] = ntuple.recoNuE / 1000.0  # MeV -> GeV

        # =================================================================
        # CUT 1: LArMatch-identified vertex inside the fiducial volume
        # =================================================================

        cut1_pass = (getattr(ntuple, 'foundVertex', 0) == 1 and
                     getattr(ntuple, 'vtxIsFiducial', 0) == 1)
        self._vars['cut1_vertex_fiducial'][0] = int(cut1_pass)

        # =================================================================
        # CUT 2: Prong spacepoints do not all overlap with WC-tagged cosmics
        # =================================================================

        cosmic_fraction = getattr(ntuple, 'vtxFracHitsOnCosmic', 1.0)
        self._vars['vtx_cosmic_fraction'][0] = cosmic_fraction
        self._vars['is_fully_contained'][0] = int(getattr(ntuple, 'vtxContainment', -1) == 2)

        cut2_pass = cosmic_fraction < (self._cosmic_fraction_threshold - 1e-6)
        self._vars['cut2_cosmic_rejection'][0] = int(cut2_pass)

        # =================================================================
        # ELECTRON CANDIDATES (used by cuts 4 and 6)
        # =================================================================

        electron_candidates = get_primary_electron_candidates(ntuple, self._electron_quality_cuts)

        # =================================================================
        # CUT 3: No LArPID-identified muon tracks attached to vertex
        # =================================================================

        cut3_pass, _ = self._evaluate_cut3_no_muon_tracks(ntuple)
        self._vars['cut3_no_muon_tracks'][0] = int(cut3_pass)

        # =================================================================
        # CUT 4: At least one primary electron shower attached to vertex
        # =================================================================

        cut4_pass, electron_info = self._evaluate_cut4_has_electron(electron_candidates)
        cut4_pass = cut3_pass and cut4_pass
        self._vars['cut4_has_electron'][0] = int(cut4_pass)

        self._extract_electron_kinematics(ntuple, electron_info)

        # =================================================================
        # CUT 5: No tracks have high muon score (max log(muon score) < -3.7)
        # =================================================================

        cut5_pass = self._evaluate_cut5_low_muon_score(ntuple)
        cut5_pass = cut4_pass and cut5_pass
        self._vars['cut5_low_muon_score'][0] = int(cut5_pass)

        # =================================================================
        # CUT 6: Largest electron classified with high confidence
        # =================================================================

        cut6_pass = self._evaluate_cut6_electron_confidence(electron_candidates, electron_info)
        cut6_pass = cut5_pass and cut6_pass
        self._vars['cut6_electron_confidence'][0] = int(cut6_pass)

        # =================================================================
        # COMBINED SELECTION
        # =================================================================

        passes_all = cut1_pass and cut2_pass and cut3_pass and cut4_pass and cut5_pass and cut6_pass
        self._vars['passes_all_cuts'][0] = int(passes_all)

        return {k: v[0] for k, v in self._vars.items()}

    def _evaluate_cut3_no_muon_tracks(self, ntuple) -> tuple:
        """Cut 3: No LArPID-identified muon tracks attached to neutrino candidate."""
        n_muon_tracks = 0

        for i in range(getattr(ntuple, 'nTracks', 0)):
            if getattr(ntuple, 'trackIsSecondary', [1])[i] != 0:
                continue
            if getattr(ntuple, 'trackClassified', [0])[i] != 1:
                continue
            if getattr(ntuple, 'trackPID', [0])[i] == 13:
                n_muon_tracks += 1

        self._vars['n_muon_tracks'][0] = n_muon_tracks
        return n_muon_tracks == 0, n_muon_tracks

    def _evaluate_cut4_has_electron(self, electron_candidates) -> tuple:
        """
        Cut 4: At least one primary electron shower attached to vertex.
        Returns (pass_status, electron_info_dict).
        """
        electron_idx_list = electron_candidates.get('idxlist', [])
        electron_data = electron_candidates.get('prongDict', {})

        electron_showers = []
        largest_primary_idx = -1
        largest_primary_energy = 0.0

        for idx in electron_idx_list:
            if idx >= 100:  # skip track-based candidates (idx+100 convention)
                continue
            if idx not in electron_data:
                continue

            shower_data = electron_data[idx]
            shower_energy = shower_data.get('showerQ', 0.0)
            shower_process = shower_data.get('process', -1)

            if abs(shower_data.get('larpid', 0)) == 11:
                electron_showers.append({'idx': idx, 'energy': shower_energy, 'process': shower_process})

                if shower_process == 0 and shower_energy > largest_primary_energy:
                    largest_primary_energy = shower_energy
                    largest_primary_idx = idx

        self._vars['n_electron_showers'][0] = len(electron_showers)
        self._vars['largest_electron_energy'][0] = largest_primary_energy

        electron_info = {
            'largest_primary_idx': largest_primary_idx,
            'electron_data': electron_data,
        }

        return largest_primary_idx >= 0, electron_info

    def _extract_electron_kinematics(self, ntuple, electron_info) -> None:
        """Extract momentum and cos theta for the largest primary electron shower."""
        idx = electron_info['largest_primary_idx']
        if idx < 0:
            return

        try:
            if hasattr(ntuple, 'showerRecoE') and idx < len(ntuple.showerRecoE):
                self._vars['reco_electron_momentum'][0] = ntuple.showerRecoE[idx] / 1000.0  # MeV -> GeV

            if hasattr(ntuple, 'showerCosTheta') and idx < len(ntuple.showerCosTheta):
                self._vars['reco_electron_costheta'][0] = ntuple.showerCosTheta[idx]
        except (IndexError, AttributeError):
            pass

    def _evaluate_cut5_low_muon_score(self, ntuple) -> bool:
        """Cut 5: max log(muon score) across all primary classified tracks < -3.7."""
        max_muon_score = -99.0

        for i in range(getattr(ntuple, 'nTracks', 0)):
            if getattr(ntuple, 'trackIsSecondary', [1])[i] != 0:
                continue
            if getattr(ntuple, 'trackClassified', [0])[i] != 1:
                continue
            muon_score = getattr(ntuple, 'trackMuScore', [-99.0])[i]
            if muon_score > max_muon_score:
                max_muon_score = muon_score

        self._vars['max_track_muon_score'][0] = max_muon_score
        return max_muon_score < self._muon_score_threshold

    def _evaluate_cut6_electron_confidence(self, electron_candidates, electron_info) -> bool:
        """
        Cut 6: log(e) - (log(pi) + log(ph))/2 > 7.1 for the largest primary electron.
        """
        idx = electron_info['largest_primary_idx']
        electron_data = electron_info['electron_data']

        if idx < 0 or idx >= 100 or idx not in electron_data:
            return False

        try:
            candidate = electron_data[idx]
            electron_score = candidate.get('larpid[electron]', -99.0)
            pion_score = candidate.get('larpid[pion]', -99.0)
            photon_score = candidate.get('larpid[photon]', -99.0)

            if -99.0 in (electron_score, pion_score, photon_score):
                return False

            confidence = electron_score - (pion_score + photon_score) / 2.0
            self._vars['electron_confidence'][0] = confidence
            return confidence > self._electron_confidence_threshold

        except (KeyError, AttributeError):
            return False

    def finalize(self):
        """Nothing to do after event loop."""
        return