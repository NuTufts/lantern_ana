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

        # Output variables for the three cuts
        self._vars = {
            # Cut 1: Vertex finding and fiducial volume
            'cut1_vertex_fiducial': array('i', [0]),   # Cut 1 pass flag
            'found_vertex': array('i', [0]),
            'vertex_in_fv': array('i', [0]),
            'vertex_score': array('f', [-1.0]),

            # Cut 2: Cosmic ray rejection
            'cut2_cosmic_rejection': array('i', [0]),  # Cut 2 pass flag
            'vtx_cosmic_fraction': array('f', [0.0]),
            'vtx_containment': array('i', [-1]),

            # Cut 3: Muon identification
            'cut3_has_muon': array('i', [0]),          # Cut 3 pass flag
            'has_muon_track': array('i', [0]),
            'n_muon_tracks': array('i', [0]),
            'max_muon_score': array('f', [-200.0]),
            'max_muon_charge': array('f', [0.0]),
            'best_muon_track_idx': array('i', [-1]),

            # Containment
            'is_fully_contained': array('i', [0]),     # vtxContainment == 2

            # Reconstructed muon kinematics
            'reco_muon_momentum': array('f', [-1.0]),     # GeV/c
            'reco_muon_costheta': array('f', [-999.0]),   # cos(theta) w.r.t. beam
            'reco_muon_energy': array('f', [-1.0]),       # GeV
            'reco_muon_length': array('f', [-1.0]),       # cm

            # Neutrino classification (MC truth when available)
            'is_cc_interaction': array('i', [-1]),  # -1: unknown, 0: NC, 1: CC
            'true_nu_pdg': array('i', [0]),
            'true_nu_energy': array('f', [-1.0]),
            'true_nu_mode': array('i', [-1]),
            'reco_nu_energy': array('f', [-1.0]),

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
        self._vars['cut1_vertex_fiducial'][0] = 0
        self._vars['found_vertex'][0] = 0
        self._vars['vertex_in_fv'][0] = 0
        self._vars['vertex_score'][0] = -1.0

        # Cut 2 defaults
        self._vars['cut2_cosmic_rejection'][0] = 0
        self._vars['vtx_cosmic_fraction'][0] = 0.0
        self._vars['vtx_containment'][0] = -1

        # Cut 3 defaults
        self._vars['cut3_has_muon'][0] = 0
        self._vars['has_muon_track'][0] = 0
        self._vars['n_muon_tracks'][0] = 0
        self._vars['max_muon_score'][0] = -200.0
        self._vars['max_muon_charge'][0] = 0.0
        self._vars['best_muon_track_idx'][0] = -1

        # Containment default
        self._vars['is_fully_contained'][0] = 0

        # Muon kinematics defaults
        self._vars['reco_muon_momentum'][0] = -1.0
        self._vars['reco_muon_costheta'][0] = -999.0
        self._vars['reco_muon_energy'][0] = -1.0
        self._vars['reco_muon_length'][0] = -1.0

        # Neutrino classification defaults
        self._vars['is_cc_interaction'][0] = -1
        # self._vars['is_nc_interaction'][0] = -1
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

        if hasattr(ntuple, 'trueNuCCNC'):
            self._vars['is_cc_interaction'][0] = int(ntuple.trueNuCCNC == 0)
            # self._vars['is_nc_interaction'][0] = int(ntuple.trueNuCCNC == 1)

        if hasattr(ntuple, 'trueNuPDG'):
            self._vars['true_nu_pdg'][0] = ntuple.trueNuPDG

        if hasattr(ntuple, 'trueNuE'):
            self._vars['true_nu_energy'][0] = ntuple.trueNuE  # Already in GeV

        if hasattr(ntuple, 'trueNuMode'):
            self._vars['true_nu_mode'][0] = ntuple.trueNuMode

        if hasattr(ntuple, 'recoNuE'):
            self._vars['reco_nu_energy'][0] = ntuple.recoNuE / 1000.0  # Convert MeV -> GeV

        if hasattr(ntuple, 'nTracks'):
            self._vars['n_tracks_total'][0] = ntuple.nTracks
        if hasattr(ntuple, 'nShowers'):
            self._vars['n_showers_total'][0] = ntuple.nShowers

        # =================================================================
        # CUT 1: LArMatch-identified neutrino candidate vertex found inside
        #        the fiducial volume
        # =================================================================

        has_vertex = hasattr(ntuple, 'foundVertex') and ntuple.foundVertex == 1
        self._vars['found_vertex'][0] = int(has_vertex)

        if has_vertex:
            self._vars['vertex_score'][0] = ntuple.vtxScore

            if self.fv_params.get('useWCvolume', True):
                is_fiducial = ntuple.vtxIsFiducial == 1
            else:
                is_fiducial = fiducial_cut(ntuple, self.fv_params)

            self._vars['vertex_in_fv'][0] = int(is_fiducial)
        else:
            self._vars['vertex_in_fv'][0] = 0

        cut1_pass = self._vars['vertex_in_fv'][0] == 1
        self._vars['cut1_vertex_fiducial'][0] = int(cut1_pass)

        # =================================================================
        # CUT 2: 3D space points of prongs attached to neutrino candidate
        #        do not all overlap with Wire-Cell-tagged cosmics
        # =================================================================

        if has_vertex:
            cosmic_fraction = ntuple.vtxFracHitsOnCosmic
            self._vars['vtx_cosmic_fraction'][0] = cosmic_fraction

            vtx_containment = ntuple.vtxContainment
            self._vars['vtx_containment'][0] = vtx_containment

            cut2_pass = cosmic_fraction < (self.cosmic_rejection_threshold - 1e-6)
            self._vars['cut2_cosmic_rejection'][0] = int(cut2_pass)

            # Fully contained: all prong hits inside fiducial volume
            self._vars['is_fully_contained'][0] = int(vtx_containment == 2)
        else:
            self._vars['vtx_cosmic_fraction'][0] = 0.0
            self._vars['vtx_containment'][0] = -1
            self._vars['is_fully_contained'][0] = 0
            self._vars['cut2_cosmic_rejection'][0] = 0

        # =================================================================
        # CUT 3: At least one track attached to the candidate neutrino vertex
        #        was identified by LArPID as a muon (PDG == 13 only)
        # =================================================================

        max_muon_score = -200.0
        max_muon_charge = 0.0
        n_muon_tracks = 0
        best_muon_idx = -1

        if has_vertex and hasattr(ntuple, 'nTracks') and ntuple.nTracks > 0:
            for iTrack in range(ntuple.nTracks):
                # Skip secondary tracks
                if (hasattr(ntuple, 'trackIsSecondary') and
                        ntuple.trackIsSecondary[iTrack] != 0):
                    continue

                # Skip unclassified tracks
                if (hasattr(ntuple, 'trackClassified') and
                        ntuple.trackClassified[iTrack] != 1):
                    continue

                # Muon PID: PDG == 13 only
                if (hasattr(ntuple, 'trackPID') and
                        ntuple.trackPID[iTrack] == 13):
                    n_muon_tracks += 1

                # Track highest muon score across all primary classified tracks
                if hasattr(ntuple, 'trackMuScore'):
                    muon_score = ntuple.trackMuScore[iTrack]
                    if muon_score > max_muon_score:
                        max_muon_score = muon_score
                        best_muon_idx = iTrack
                        if hasattr(ntuple, 'trackCharge'):
                            max_muon_charge = ntuple.trackCharge[iTrack]

        self._vars['n_muon_tracks'][0] = n_muon_tracks
        self._vars['max_muon_score'][0] = max_muon_score
        self._vars['max_muon_charge'][0] = max_muon_charge
        self._vars['best_muon_track_idx'][0] = best_muon_idx

        # Muon presence: PID classification only
        has_muon = n_muon_tracks > 0
        self._vars['has_muon_track'][0] = int(has_muon)

        cut3_pass = has_muon
        self._vars['cut3_has_muon'][0] = int(cut3_pass)

        # =================================================================
        # CALCULATE MUON KINEMATICS for the best muon candidate
        # =================================================================

        if best_muon_idx >= 0 and has_muon:
            muon_idx = best_muon_idx

            if hasattr(ntuple, 'trackRecoE'):
                muon_ke_mev = ntuple.trackRecoE[muon_idx]
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
            elif hasattr(ntuple, 'trackRangeE'):
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

            if (hasattr(ntuple, 'trackStartDirX') and
                    hasattr(ntuple, 'trackStartDirY') and
                    hasattr(ntuple, 'trackStartDirZ')):
                dir_x = ntuple.trackStartDirX[muon_idx]
                dir_y = ntuple.trackStartDirY[muon_idx]
                dir_z = ntuple.trackStartDirZ[muon_idx]
                if abs(dir_x) < 900 and abs(dir_y) < 900 and abs(dir_z) < 900:
                    self._vars['reco_muon_costheta'][0] = dir_z
            elif hasattr(ntuple, 'trackCosTheta'):
                cos_theta = ntuple.trackCosTheta[muon_idx]
                if abs(cos_theta) <= 1.0:
                    self._vars['reco_muon_costheta'][0] = cos_theta

            if hasattr(ntuple, 'trackLength'):
                track_length = ntuple.trackLength[muon_idx]
                if track_length > 0:
                    self._vars['reco_muon_length'][0] = track_length

        # =================================================================
        # COMBINED SELECTION: All three cuts must pass
        # =================================================================

        passes_all = cut1_pass and cut2_pass and cut3_pass
        self._vars['passes_all_cuts'][0] = int(passes_all)

        # =================================================================
        # RETURN RESULTS
        # =================================================================

        return {
            'cut1_vertex_fiducial': self._vars['cut1_vertex_fiducial'][0],
            'cut2_cosmic_rejection': self._vars['cut2_cosmic_rejection'][0],
            'cut3_has_muon': self._vars['cut3_has_muon'][0],
            'found_vertex': self._vars['found_vertex'][0],
            'vertex_in_fv': self._vars['vertex_in_fv'][0],
            'vtx_cosmic_fraction': self._vars['vtx_cosmic_fraction'][0],
            'is_fully_contained': self._vars['is_fully_contained'][0],
            'has_muon_track': self._vars['has_muon_track'][0],
            'n_muon_tracks': self._vars['n_muon_tracks'][0],
            'max_muon_score': self._vars['max_muon_score'][0],
            'is_cc_interaction': self._vars['is_cc_interaction'][0],
            'true_nu_pdg': self._vars['true_nu_pdg'][0],
            'true_nu_energy': self._vars['true_nu_energy'][0],
            'reco_nu_energy': self._vars['reco_nu_energy'][0],
            'n_tracks_total': self._vars['n_tracks_total'][0],
            'n_showers_total': self._vars['n_showers_total'][0],
            'reco_muon_momentum': self._vars['reco_muon_momentum'][0],
            'reco_muon_costheta': self._vars['reco_muon_costheta'][0],
            'reco_muon_energy': self._vars['reco_muon_energy'][0],
            'reco_muon_length': self._vars['reco_muon_length'][0],
            'passes_all_cuts': self._vars['passes_all_cuts'][0]
        }

    def finalize(self):
        """Nothing to do after event loop."""
        return