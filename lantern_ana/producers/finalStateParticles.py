"""
Producer that stores final state particle (FSP) information for both reco and truth.

Truth FSPs: primary particles from the neutrino interaction vertex
            (trueSimPartProcess == 0).
Reco FSPs:  primary prongs attached to the neutrino candidate vertex
            (not secondary, classified).
"""

import numpy as np
from typing import Dict, Any, List
from array import array
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register


@register
class finalStateParticlesProducer(ProducerBaseClass):
    """
    Stores per-particle kinematics for final state particles (reco and truth).

    Reco: primary showers and tracks attached to the neutrino vertex candidate.
    Truth (MC only): primary particles from the neutrino interaction
                     (trueSimPartProcess == 0).

    Per-particle data is stored as ROOT vectors so the branch length varies
    event-by-event. Scalar count branches are also written for convenience.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

        # ── scalar counters ────────────────────────────────────────────────
        self._n_reco_showers  = array('i', [0])
        self._n_reco_tracks   = array('i', [0])
        self._n_true_fsp      = array('i', [0])

        # ── reco shower vectors ────────────────────────────────────────────
        self._reco_shower_pid      = ROOT.vector('int')()
        self._reco_shower_E        = ROOT.vector('float')()   # MeV
        self._reco_shower_costheta = ROOT.vector('float')()

        # ── reco track vectors ─────────────────────────────────────────────
        self._reco_track_pid      = ROOT.vector('int')()
        self._reco_track_E        = ROOT.vector('float')()    # MeV
        self._reco_track_costheta = ROOT.vector('float')()
        self._reco_track_length   = ROOT.vector('float')()    # cm

        # ── truth FSP vectors (MC only) ────────────────────────────────────
        self._true_fsp_pdg = ROOT.vector('int')()
        self._true_fsp_E   = ROOT.vector('float')()           # MeV
        self._true_fsp_px  = ROOT.vector('float')()           # MeV/c
        self._true_fsp_py  = ROOT.vector('float')()
        self._true_fsp_pz  = ROOT.vector('float')()
        self._true_fsp_ke  = ROOT.vector('float')()

        # ── truth pi0 / photon scalars (any process, not just primary) ─────
        self._true_n_any_pi0          = array('i', [0])
        self._true_n_photons_from_pi0 = array('i', [0])           # MeV

    # ──────────────────────────────────────────────────────────────────────
    def setDefaultValues(self) -> None:
        self._n_reco_showers[0] = 0
        self._n_reco_tracks[0]  = 0
        self._n_true_fsp[0]     = 0

        self._reco_shower_pid.clear()
        self._reco_shower_E.clear()
        self._reco_shower_costheta.clear()

        self._reco_track_pid.clear()
        self._reco_track_E.clear()
        self._reco_track_costheta.clear()
        self._reco_track_length.clear()

        self._true_fsp_pdg.clear()
        self._true_fsp_E.clear()
        self._true_fsp_px.clear()
        self._true_fsp_py.clear()
        self._true_fsp_pz.clear()
        self._true_fsp_ke.clear()

        self._true_n_any_pi0[0]          = 0
        self._true_n_photons_from_pi0[0] = 0

    # ──────────────────────────────────────────────────────────────────────
    def prepareStorage(self, output: Any) -> None:
        p = self.name

        output.Branch(f"{p}_n_reco_showers",  self._n_reco_showers,  f"{p}_n_reco_showers/I")
        output.Branch(f"{p}_n_reco_tracks",   self._n_reco_tracks,   f"{p}_n_reco_tracks/I")
        output.Branch(f"{p}_n_true_fsp",      self._n_true_fsp,      f"{p}_n_true_fsp/I")

        output.Branch(f"{p}_reco_shower_pid",      self._reco_shower_pid)
        output.Branch(f"{p}_reco_shower_E",        self._reco_shower_E)
        output.Branch(f"{p}_reco_shower_costheta", self._reco_shower_costheta)

        output.Branch(f"{p}_reco_track_pid",      self._reco_track_pid)
        output.Branch(f"{p}_reco_track_E",        self._reco_track_E)
        output.Branch(f"{p}_reco_track_costheta", self._reco_track_costheta)
        output.Branch(f"{p}_reco_track_length",   self._reco_track_length)

        output.Branch(f"{p}_true_fsp_pdg", self._true_fsp_pdg)
        output.Branch(f"{p}_true_fsp_E",   self._true_fsp_E)
        output.Branch(f"{p}_true_fsp_px",  self._true_fsp_px)
        output.Branch(f"{p}_true_fsp_py",  self._true_fsp_py)
        output.Branch(f"{p}_true_fsp_pz",  self._true_fsp_pz)
        output.Branch(f"{p}_true_fsp_ke",  self._true_fsp_ke)

        output.Branch(f"{p}_true_n_any_pi0",          self._true_n_any_pi0,          f"{p}_true_n_any_pi0/I")
        output.Branch(f"{p}_true_n_photons_from_pi0", self._true_n_photons_from_pi0, f"{p}_true_n_photons_from_pi0/I")

    # ──────────────────────────────────────────────────────────────────────
    def requiredInputs(self) -> List[str]:
        return ["gen2ntuple"]

    # ──────────────────────────────────────────────────────────────────────
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        ntuple = data["gen2ntuple"]
        ismc   = params.get('ismc', False)

        self.setDefaultValues()

        self._fill_reco_showers(ntuple)
        self._fill_reco_tracks(ntuple)

        if ismc:
            self._fill_true_fsp(ntuple)

        return {
            'n_reco_showers':          self._n_reco_showers[0],
            'n_reco_tracks':           self._n_reco_tracks[0],
            'n_true_fsp':              self._n_true_fsp[0],
            'true_n_any_pi0':          self._true_n_any_pi0[0],
            'true_n_photons_from_pi0': self._true_n_photons_from_pi0[0],
        }

    # ──────────────────────────────────────────────────────────────────────
    def _fill_reco_showers(self, ntuple) -> None:
        n_showers = getattr(ntuple, 'nShowers', 0)
        has_secondary  = hasattr(ntuple, 'showerIsSecondary')
        has_classified = hasattr(ntuple, 'showerClassified')
        has_pid        = hasattr(ntuple, 'showerPID')
        has_E          = hasattr(ntuple, 'showerRecoE')
        has_costheta   = hasattr(ntuple, 'showerCosTheta')
        count = 0
        for i in range(n_showers):
            if has_secondary and ntuple.showerIsSecondary[i] != 0:
                continue
            if has_classified and ntuple.showerClassified[i] != 1:
                continue

            self._reco_shower_pid.push_back(int(ntuple.showerPID[i]) if has_pid else 0)
            self._reco_shower_E.push_back(float(ntuple.showerRecoE[i]) if has_E else 0.0)
            self._reco_shower_costheta.push_back(float(ntuple.showerCosTheta[i]) if has_costheta else -999.0)
            count += 1

        self._n_reco_showers[0] = count

    # ──────────────────────────────────────────────────────────────────────
    def _fill_reco_tracks(self, ntuple) -> None:
        n_tracks = getattr(ntuple, 'nTracks', 0)
        has_secondary  = hasattr(ntuple, 'trackIsSecondary')
        has_classified = hasattr(ntuple, 'trackClassified')
        has_pid        = hasattr(ntuple, 'trackPID')
        has_E          = hasattr(ntuple, 'trackRecoE')
        has_costheta   = hasattr(ntuple, 'trackCosTheta')
        has_dirZ       = hasattr(ntuple, 'trackStartDirZ')
        has_dirX       = hasattr(ntuple, 'trackStartDirX')
        has_length     = hasattr(ntuple, 'trackLength')
        count = 0
        for i in range(n_tracks):
            if has_secondary and ntuple.trackIsSecondary[i] != 0:
                continue
            if has_classified and ntuple.trackClassified[i] != 1:
                continue

            self._reco_track_pid.push_back(int(ntuple.trackPID[i]) if has_pid else 0)
            self._reco_track_E.push_back(float(ntuple.trackRecoE[i]) if has_E else 0.0)

            cos_theta = -999.0
            if has_costheta:
                cos_theta = ntuple.trackCosTheta[i]
            elif has_dirZ and has_dirX and abs(ntuple.trackStartDirX[i]) < 900:
                cos_theta = ntuple.trackStartDirZ[i]
            self._reco_track_costheta.push_back(float(cos_theta))

            self._reco_track_length.push_back(float(ntuple.trackLength[i]) if has_length else -1.0)
            count += 1

        self._n_reco_tracks[0] = count

    # ──────────────────────────────────────────────────────────────────────
    def _fill_true_fsp(self, ntuple) -> None:
        n_sim       = getattr(ntuple, 'nTrueSimParts', 0)
        has_process = hasattr(ntuple, 'trueSimPartProcess')
        has_tid     = hasattr(ntuple, 'trueSimPartTID')
        has_mid     = hasattr(ntuple, 'trueSimPartMID')

        # First pass: count all pi0s by PDG (process-agnostic) and collect their TIDs.
        n_pi0    = 0
        pi0_tids = set()
        for i in range(n_sim):
            if int(ntuple.trueSimPartPDG[i]) == 111:
                n_pi0 += 1
                if has_tid:
                    pi0_tids.add(int(ntuple.trueSimPartTID[i]))

        self._true_n_any_pi0[0] = n_pi0

        # Count true photons whose parent TID is any pi0.
        n_photons = 0
        if has_mid and pi0_tids:
            for i in range(n_sim):
                if (int(ntuple.trueSimPartPDG[i]) == 22
                        and int(ntuple.trueSimPartMID[i]) in pi0_tids):
                    n_photons += 1
        self._true_n_photons_from_pi0[0] = n_photons

        # Second pass: fill FSP vector with primary particles only (process==0).
        count = 0
        for i in range(n_sim):
            if has_process and ntuple.trueSimPartProcess[i] != 0:
                continue  # only primary particles

            pdg = int(ntuple.trueSimPartPDG[i])
            E   = float(ntuple.trueSimPartE[i])
            px  = float(ntuple.trueSimPartPx[i])
            py  = float(ntuple.trueSimPartPy[i])
            pz  = float(ntuple.trueSimPartPz[i])

            p2 = px*px + py*py + pz*pz
            ke = E - np.sqrt(max(E*E - p2, 0.0))

            self._true_fsp_pdg.push_back(pdg)
            self._true_fsp_E.push_back(E)
            self._true_fsp_px.push_back(px)
            self._true_fsp_py.push_back(py)
            self._true_fsp_pz.push_back(pz)
            self._true_fsp_ke.push_back(float(ke))
            count += 1

        self._n_true_fsp[0] = count

    # ──────────────────────────────────────────────────────────────────────
    def finalize(self) -> None:
        return
