"""
Producer that computes pi0 kinematics for the pi0 channel.

Reco: loops over all showers and selects those with PID==22 as photons.
      For events with >= 2 photon candidates (sorted by energy), stores
      start position, 4-momentum, and process for the leading two, then
      computes the di-photon invariant mass via M² = (E1+E2)² - |p1+p2|².

Truth (MC): locates the primary pi0 (PDG 111, TID==MID) and its two photon
            daughters, then computes invariant mass from their four-vectors.
            Falls back to -9999 if fewer than two photon daughters are found.
"""

import numpy as np
from typing import Dict, Any, List
from array import array
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register

_DEFAULT      = -9999.0
_PROTON_MASS  = 938.272   # MeV/c²


@register
class pi0PropertiesProducer(ProducerBaseClass):

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

        self._reco_inv_mass          = array('f', [_DEFAULT])
        self._reco_E1                = array('f', [_DEFAULT])
        self._reco_E2                = array('f', [_DEFAULT])
        self._reco_cos_opening_angle = array('f', [_DEFAULT])
        self._reco_cos_theta_beam    = array('f', [_DEFAULT])
        self._reco_delta_mass        = array('f', [_DEFAULT])
        self._true_inv_mass          = array('f', [_DEFAULT])

        # Per-photon data for the two leading PID==22 showers (index 0=leading, 1=subleading).
        self._ph_startX  = array('f', [_DEFAULT, _DEFAULT])
        self._ph_startY  = array('f', [_DEFAULT, _DEFAULT])
        self._ph_startZ  = array('f', [_DEFAULT, _DEFAULT])
        self._ph_E       = array('f', [_DEFAULT, _DEFAULT])
        self._ph_px      = array('f', [_DEFAULT, _DEFAULT])
        self._ph_py      = array('f', [_DEFAULT, _DEFAULT])
        self._ph_pz      = array('f', [_DEFAULT, _DEFAULT])
        self._ph_process = array('i', [-1, -1])

        # Diagnostic: total PID==22 showers found in this event.
        self._diag_n_photon_cands  = array('i', [0])
        self._diag_n_total_showers = array('i', [0])

        # True photons not from eBrem/annihilation, E > 20 MeV, inside WireCell fiducial.
        self._true_n_photons_fid_ecut = array('i', [0])

    def setDefaultValues(self) -> None:
        self._reco_inv_mass[0]          = _DEFAULT
        self._reco_E1[0]                = _DEFAULT
        self._reco_E2[0]                = _DEFAULT
        self._reco_cos_opening_angle[0] = _DEFAULT
        self._reco_cos_theta_beam[0]    = _DEFAULT
        self._reco_delta_mass[0]        = _DEFAULT
        self._true_inv_mass[0]          = _DEFAULT

        for k in range(2):
            self._ph_startX[k]  = _DEFAULT
            self._ph_startY[k]  = _DEFAULT
            self._ph_startZ[k]  = _DEFAULT
            self._ph_E[k]       = _DEFAULT
            self._ph_px[k]      = _DEFAULT
            self._ph_py[k]      = _DEFAULT
            self._ph_pz[k]      = _DEFAULT
            self._ph_process[k] = -1

        self._diag_n_photon_cands[0]  = 0
        self._diag_n_total_showers[0] = 0
        self._true_n_photons_fid_ecut[0] = 0

    def prepareStorage(self, output: Any) -> None:
        p = self.name
        output.Branch(f"{p}_reco_inv_mass",          self._reco_inv_mass,          f"{p}_reco_inv_mass/F")
        output.Branch(f"{p}_reco_E1",                self._reco_E1,                f"{p}_reco_E1/F")
        output.Branch(f"{p}_reco_E2",                self._reco_E2,                f"{p}_reco_E2/F")
        output.Branch(f"{p}_reco_cos_opening_angle", self._reco_cos_opening_angle, f"{p}_reco_cos_opening_angle/F")
        output.Branch(f"{p}_reco_cos_theta_beam",    self._reco_cos_theta_beam,    f"{p}_reco_cos_theta_beam/F")
        output.Branch(f"{p}_reco_delta_mass",        self._reco_delta_mass,        f"{p}_reco_delta_mass/F")
        output.Branch(f"{p}_true_inv_mass",          self._true_inv_mass,          f"{p}_true_inv_mass/F")

        output.Branch(f"{p}_ph_startX",  self._ph_startX,  f"{p}_ph_startX[2]/F")
        output.Branch(f"{p}_ph_startY",  self._ph_startY,  f"{p}_ph_startY[2]/F")
        output.Branch(f"{p}_ph_startZ",  self._ph_startZ,  f"{p}_ph_startZ[2]/F")
        output.Branch(f"{p}_ph_E",       self._ph_E,       f"{p}_ph_E[2]/F")
        output.Branch(f"{p}_ph_px",      self._ph_px,      f"{p}_ph_px[2]/F")
        output.Branch(f"{p}_ph_py",      self._ph_py,      f"{p}_ph_py[2]/F")
        output.Branch(f"{p}_ph_pz",      self._ph_pz,      f"{p}_ph_pz[2]/F")
        output.Branch(f"{p}_ph_process", self._ph_process, f"{p}_ph_process[2]/I")

        output.Branch(f"{p}_diag_n_photon_cands",  self._diag_n_photon_cands,  f"{p}_diag_n_photon_cands/I")
        output.Branch(f"{p}_diag_n_total_showers", self._diag_n_total_showers, f"{p}_diag_n_total_showers/I")
        output.Branch(f"{p}_true_n_photons_fid_ecut", self._true_n_photons_fid_ecut, f"{p}_true_n_photons_fid_ecut/I")

    def requiredInputs(self) -> List[str]:
        return ["gen2ntuple"]

    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        ntuple = data["gen2ntuple"]
        ismc   = params.get('ismc', False)

        self.setDefaultValues()
        self._fill_reco(ntuple)
        if ismc:
            self._fill_true(ntuple)

        return {}

    # ------------------------------------------------------------------
    def _fill_reco(self, ntuple) -> None:
        n_showers = getattr(ntuple, 'nShowers', 0)
        has_pid   = hasattr(ntuple, 'showerPID')
        has_E     = hasattr(ntuple, 'showerRecoE')
        has_dirX  = hasattr(ntuple, 'showerStartDirX')
        has_dirY  = hasattr(ntuple, 'showerStartDirY')
        has_dirZ  = hasattr(ntuple, 'showerStartDirZ')
        has_posX  = hasattr(ntuple, 'showerStartPosX')
        has_posY  = hasattr(ntuple, 'showerStartPosY')
        has_posZ  = hasattr(ntuple, 'showerStartPosZ')
        has_proc  = hasattr(ntuple, 'showerProcess')

        if not (has_pid and has_E and has_dirX and has_dirY and has_dirZ):
            return

        self._diag_n_total_showers[0] = n_showers

        # Collect the first two PID==22 showers in ntuple order (matching Erin's selection).
        photons = []  # (energy, dirX, dirY, dirZ, posX, posY, posZ, process)
        nphotons_lantern = 0
        for j in range(n_showers):
            if int(ntuple.showerPID[j]) == 22:
                nphotons_lantern += 1
                if len(photons) < 2:
                    e  = float(ntuple.showerRecoE[j])
                    dx = float(ntuple.showerStartDirX[j])
                    dy = float(ntuple.showerStartDirY[j])
                    dz = float(ntuple.showerStartDirZ[j])
                    posX = float(ntuple.showerStartPosX[j]) if has_posX else _DEFAULT
                    posY = float(ntuple.showerStartPosY[j]) if has_posY else _DEFAULT
                    posZ = float(ntuple.showerStartPosZ[j]) if has_posZ else _DEFAULT
                    proc = int(ntuple.showerProcess[j])     if has_proc else -1
                    photons.append((e, dx, dy, dz, posX, posY, posZ, proc))

        self._diag_n_photon_cands[0] = nphotons_lantern

        if len(photons) < 2:
            return

        e1, dx1, dy1, dz1, posX1, posY1, posZ1, proc1 = photons[0]
        e2, dx2, dy2, dz2, posX2, posY2, posZ2, proc2 = photons[1]

        norm1 = np.sqrt(dx1*dx1 + dy1*dy1 + dz1*dz1)
        norm2 = np.sqrt(dx2*dx2 + dy2*dy2 + dz2*dz2)
        if norm1 < 1e-9 or norm2 < 1e-9:
            return

        # 4-momenta (massless photons: |p| = E)
        px1 = e1 * dx1 / norm1;  py1 = e1 * dy1 / norm1;  pz1 = e1 * dz1 / norm1
        px2 = e2 * dx2 / norm2;  py2 = e2 * dy2 / norm2;  pz2 = e2 * dz2 / norm2

        # Store per-photon data.
        self._ph_startX[0]  = posX1;  self._ph_startX[1]  = posX2
        self._ph_startY[0]  = posY1;  self._ph_startY[1]  = posY2
        self._ph_startZ[0]  = posZ1;  self._ph_startZ[1]  = posZ2
        self._ph_E[0]       = e1;     self._ph_E[1]       = e2
        self._ph_px[0]      = px1;    self._ph_px[1]      = px2
        self._ph_py[0]      = py1;    self._ph_py[1]      = py2
        self._ph_pz[0]      = pz1;    self._ph_pz[1]      = pz2
        self._ph_process[0] = proc1;  self._ph_process[1] = proc2

        # Di-photon invariant mass from 4-vectors.
        E_tot  = e1  + e2
        px_tot = px1 + px2
        py_tot = py1 + py2
        pz_tot = pz1 + pz2
        m2 = E_tot*E_tot - px_tot*px_tot - py_tot*py_tot - pz_tot*pz_tot
        inv_mass = float(np.sqrt(max(m2, 0.0)))

        self._reco_inv_mass[0]          = inv_mass
        self._reco_E1[0]                = e1
        self._reco_E2[0]                = e2

        cos_alpha = (dx1*dx2 + dy1*dy2 + dz1*dz2) / (norm1 * norm2)
        self._reco_cos_opening_angle[0] = float(np.clip(cos_alpha, -1.0, 1.0))
        self._reco_cos_theta_beam[0]    = float(dz1 / norm1)

        self._fill_delta_mass(ntuple, e1, px1, py1, pz1, e2, px2, py2, pz2)

    # ------------------------------------------------------------------
    def _fill_delta_mass(self, ntuple,
                         e1, px1, py1, pz1,
                         e2, px2, py2, pz2) -> None:
        """Δ(1232) rest mass from the two photon showers + leading proton-like track."""
        n_tracks       = getattr(ntuple, 'nTracks', 0)
        has_classified = hasattr(ntuple, 'trackClassified')
        has_secondary  = hasattr(ntuple, 'trackIsSecondary')
        has_pid        = hasattr(ntuple, 'trackPID')
        has_E          = hasattr(ntuple, 'trackRecoE')
        has_prScore    = hasattr(ntuple, 'trackPrScore')
        has_dirX       = hasattr(ntuple, 'trackStartDirX')
        has_dirY       = hasattr(ntuple, 'trackStartDirY')
        has_dirZ       = hasattr(ntuple, 'trackStartDirZ')

        if not (has_E and has_dirX and has_dirY and has_dirZ):
            return

        best_idx   = -1
        best_score = -1.0
        for i in range(n_tracks):
            if has_secondary and ntuple.trackIsSecondary[i] != 0:
                continue
            if has_classified and ntuple.trackClassified[i] != 1:
                continue
            score = float(ntuple.trackPrScore[i]) if has_prScore else 0.0
            if has_pid and int(ntuple.trackPID[i]) == 2212:
                score += 1.0
            if score > best_score:
                best_score = score
                best_idx   = i

        if best_idx < 0:
            return

        ke_p  = float(ntuple.trackRecoE[best_idx])
        e_p   = ke_p + _PROTON_MASS
        p_mag = float(np.sqrt(max(e_p*e_p - _PROTON_MASS*_PROTON_MASS, 0.0)))

        tdx   = float(ntuple.trackStartDirX[best_idx])
        tdy   = float(ntuple.trackStartDirY[best_idx])
        tdz   = float(ntuple.trackStartDirZ[best_idx])
        tnorm = np.sqrt(tdx*tdx + tdy*tdy + tdz*tdz)
        if tnorm < 1e-9:
            return

        pxp = p_mag * tdx / tnorm
        pyp = p_mag * tdy / tnorm
        pzp = p_mag * tdz / tnorm

        e_tot  = e1  + e2  + e_p
        px_tot = px1 + px2 + pxp
        py_tot = py1 + py2 + pyp
        pz_tot = pz1 + pz2 + pzp
        m2     = e_tot*e_tot - px_tot*px_tot - py_tot*py_tot - pz_tot*pz_tot
        self._reco_delta_mass[0] = float(np.sqrt(max(m2, 0.0)))

    # ------------------------------------------------------------------
    def _fill_true(self, ntuple) -> None:
        n_sim   = getattr(ntuple, 'nTrueSimParts', 0)
        has_pdg = hasattr(ntuple, 'trueSimPartPDG')
        has_tid = hasattr(ntuple, 'trueSimPartTID')
        has_mid = hasattr(ntuple, 'trueSimPartMID')
        has_E   = hasattr(ntuple, 'trueSimPartE')
        has_px  = hasattr(ntuple, 'trueSimPartPx')
        has_py  = hasattr(ntuple, 'trueSimPartPy')
        has_pz  = hasattr(ntuple, 'trueSimPartPz')

        has_edep_x = hasattr(ntuple, 'trueSimPartEDepX')
        has_edep_y = hasattr(ntuple, 'trueSimPartEDepY')
        has_edep_z = hasattr(ntuple, 'trueSimPartEDepZ')

        if not (has_pdg and has_tid and has_mid and has_px and has_py and has_pz):
            return

        # Build TID → PDG map for mother-PDG lookup (used by both blocks below).
        tid_to_pdg = {}
        for i in range(n_sim):
            tid_to_pdg[int(ntuple.trueSimPartTID[i])] = int(ntuple.trueSimPartPDG[i])

        # --- true_inv_mass: pi0 decay photons ---
        # Find all pi0s: primary (TID==MID) first, then FSI-produced if none found.
        pi0_tids = set()
        for i in range(n_sim):
            if int(ntuple.trueSimPartPDG[i]) == 111:
                if ntuple.trueSimPartTID[i] == ntuple.trueSimPartMID[i]:
                    pi0_tids.add(int(ntuple.trueSimPartTID[i]))
        if not pi0_tids:
            # Fall back to any pi0 (e.g., from pion charge exchange in the nucleus).
            for i in range(n_sim):
                if int(ntuple.trueSimPartPDG[i]) == 111:
                    pi0_tids.add(int(ntuple.trueSimPartTID[i]))

        if pi0_tids:
            photon_daughters = []  # (E, px, py, pz)
            for i in range(n_sim):
                if (int(ntuple.trueSimPartPDG[i]) == 22
                        and int(ntuple.trueSimPartMID[i]) in pi0_tids):
                    px = float(ntuple.trueSimPartPx[i])
                    py = float(ntuple.trueSimPartPy[i])
                    pz = float(ntuple.trueSimPartPz[i])
                    e = (float(ntuple.trueSimPartE[i]) if has_E
                         else float(np.sqrt(px*px + py*py + pz*pz)))
                    photon_daughters.append((e, px, py, pz))

            if len(photon_daughters) >= 2:
                photon_daughters.sort(key=lambda x: x[0], reverse=True)
                e1, px1, py1, pz1 = photon_daughters[0]
                e2, px2, py2, pz2 = photon_daughters[1]
                m2 = ((e1+e2)**2
                      - (px1+px2)**2
                      - (py1+py2)**2
                      - (pz1+pz2)**2)
                self._true_inv_mass[0] = float(np.sqrt(max(m2, 0.0)))

        # --- true_n_photons_fid_ecut: all photons not from eBrem/annihilation ---
        # WireCell fiducial bounds (same as Erin's Get2Photons WC path).
        _WC_XMIN, _WC_XMAX = 3.0,    253.0
        _WC_YMIN, _WC_YMAX = -113.0, 114.0
        _WC_ZMIN, _WC_ZMAX = 3.0,    1034.0

        n_ph_pass = 0
        for i in range(n_sim):
            if int(ntuple.trueSimPartPDG[i]) != 22:
                continue
            # Exclude eBrem (mother = e-) and pair annihilation (mother = e+).
            mother_pdg = tid_to_pdg.get(int(ntuple.trueSimPartMID[i]), 0)
            if abs(mother_pdg) == 11:
                continue
            # Energy cut.
            px = float(ntuple.trueSimPartPx[i])
            py = float(ntuple.trueSimPartPy[i])
            pz = float(ntuple.trueSimPartPz[i])
            e  = (float(ntuple.trueSimPartE[i]) if has_E
                  else float(np.sqrt(px*px + py*py + pz*pz)))
            if e <= 20.0:
                continue
            # WireCell fiducial using energy-deposition position.
            if has_edep_x and has_edep_y and has_edep_z:
                ex = float(ntuple.trueSimPartEDepX[i])
                ey = float(ntuple.trueSimPartEDepY[i])
                ez = float(ntuple.trueSimPartEDepZ[i])
                if not (_WC_XMIN < ex < _WC_XMAX and
                        _WC_YMIN < ey < _WC_YMAX and
                        _WC_ZMIN < ez < _WC_ZMAX):
                    continue
            n_ph_pass += 1

        self._true_n_photons_fid_ecut[0] = n_ph_pass

    # ------------------------------------------------------------------
    def finalize(self) -> None:
        return
