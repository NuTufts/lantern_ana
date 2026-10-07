#!/usr/bin/env python3
# cross_generator_tki.py
#
# Standalone script to process NUISANCE-format flat-tree files (GENIE, GiBUU,
# NEUT, NuWro) into TKI variables using the same naming convention as
# signalDefinitionCCnumuPiPlusNproton's output branches (numuCC1piNp_*), for
# cross-generator comparison plots. Truth-level only.
#
# IMPORTANT: writes EXACTLY ONE OUTPUT ROW PER INPUT EVENT, in the same
# order, with no skipping -- output row i always corresponds to input
# event i, for every event including non-CC / non-numu / failed-selection
# events. This is required for event-by-event lookup/debugging.
#
# Signal definition:
#   - CC interaction, incoming neutrino is muon neutrino ONLY (PDGnu==14,
#     NOT numubar/-14) -- tracked via numuCC1piNp_is_ccnumu, does NOT skip
#     the row if false
#   - Primary vertex whitelist (pre-FSI, pdg_vert): ONLY mu-, proton,
#     pi+/pi-, and any number of neutrons are allowed as outgoing vertex
#     particles. The incoming neutrino itself and the struck nuclear
#     target are excluded from this check (they aren't outgoing
#     particles) -- everything else present vetoes the event outright.
#   - exactly 1 mu- in the post-FSI final state, KE in [0, 1398.06] MeV
#   - exactly 1 charged pion (+ or -) in the post-FSI final state,
#     KE in [16.62, inf) MeV
#   - >= 1 proton in the post-FSI final state, KE in [46.8, 433.01] MeV
#
# WEIGHTS: both per-event "Weight" (should be 1 for GENIE/NEUT/NuWro,
# meaningful for GiBUU) and "fScaleFactor" (the file-level normalization
# double, constant per file but written per-row for convenience) are read
# from the input NUISANCE tree and passed through unchanged to the output
# tree under their original branch names, for EVERY row including
# non-CC/non-numu events.
#
# NOTE ON KE CALCULATION: ke_from_fourmom() below is a direct, verified
# port of lantern_ana.utils.kinematics.KE_from_fourmom (confirmed
# line-for-line identical formula) -- not imported, just re-implemented
# with numpy for vectorization. No dependency on that module needed.

import os
import time
import importlib.util
import numpy as np
import uproot


def _load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load transverse_kinematic_imbalance.py directly by file path, bypassing
# the lantern_ana package __init__ entirely (which pulls in the whole
# framework, including a currently-broken tag module unrelated to this
# script). This file has zero dependency on the rest of lantern_ana --
# only numpy/scipy -- so this is safe.
LANTERN_ANA_ROOT = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/lantern_ana"
tki = _load_module_from_path(
    "transverse_kinematic_imbalance",
    os.path.join(LANTERN_ANA_ROOT, "utils", "transverse_kinematic_imbalance.py")
)

MASTER_PATH = "/cluster/tufts/wongjiradlabnu/zimani01/transfer/Polina_stuff"
FILES = {
    "GENIE": "GENIE_v3_6_2_AR23_20i_00_000_uB_numu_CC.flat.root",
    "GiBUU": "GiBUU_2025.flat_250files.root",
    "NEUT":  "NEUT_v5_6_2_uB_numu_CC.flat.root",
    "NuWro": "NuWro_v25_11_uB_numu_CC.flat.root",
}

PROGRESS_EVERY = 50000

# KE thresholds in MeV for post-FSI final-state particles.
# NOTE: only pdg==13 (mu-), NOT -13 (mu+/antimuon).
THRESH = {
    13:   (0.0,   1398.06),
    2212: (46.8,  433.01),
    211:  (16.62, float("inf")),
    -211: (16.62, float("inf")),
}

# Primary vertex whitelist: ONLY these species may appear as outgoing
# vertex particles at the pre-FSI GENIE vertex. Neutrons (2112) are
# allowed in any number.
ALLOWED_VERTEX_PDG = {13, 2212, 211, -211, 2112}


def ke_from_fourmom(px, py, pz, E):
    # KE = E - m, mass recovered from on-shell relation E^2 - p^2.
    # px, py, pz, E in GeV; returns KE in GeV.
    # Verified identical to lantern_ana.utils.kinematics.KE_from_fourmom.
    p2 = px * px + py * py + pz * pz
    m2 = np.maximum(E * E - p2, 0.0)
    return E - np.sqrt(m2)


def process_file(gen_name, fname):
    path = os.path.join(MASTER_PATH, fname)
    file_size_mb = os.path.getsize(path) / (1024 * 1024)
    print("\n[{}] opening {} ({:.0f} MB)".format(gen_name, path, file_size_mb))

    t0 = time.time()
    tree = uproot.open(path)["FlatTree_VARS"]
    n_total = tree.num_entries
    print("[{}] tree opened in {:.1f}s -- {} total entries".format(gen_name, time.time() - t0, n_total))

    branches = ["cc", "PDGnu", "Enu_true", "nfsp", "pdg", "px", "py", "pz", "E",
                "Weight", "fScaleFactor", "nvertp", "pdg_vert", "tgt"]

    t0 = time.time()
    print("[{}] loading branches into memory (this is the slow part for GiBUU)...".format(gen_name))
    arrs = tree.arrays(branches, library="ak")
    print("[{}] branches loaded in {:.1f}s".format(gen_name, time.time() - t0))

    out = {
        "numuCC1piNp_is_ccnumu": [],
        "numuCC1piNp_is_target_cc_numu_1pi_nproton": [],
        "numuCC1piNp_muonKE": [],
        "numuCC1piNp_protonKE": [],
        "numuCC1piNp_pionKE": [],
        "numuCC1piNp_delPTT": [],
        "numuCC1piNp_pN": [],
        "numuCC1piNp_delAlphaT": [],
        "numuCC1piNp_debug_eNu": [],
        "Weight": [],
        "fScaleFactor": [],
        "eventweight_weight": [],
        "numuCC1piNp_debug_nmu": [],
        "numuCC1piNp_debug_npi": [],
        "numuCC1piNp_debug_nproton": [],
        "numuCC1piNp_debug_nvertex_other": [],
    }

    n_ccnumu = 0
    n_pass = 0
    unknown_codes_seen = set()

    print("[{}] looping over {} events (writing a row for EVERY event, no skipping)...".format(gen_name, n_total))
    t_loop_start = time.time()

    for i in range(n_total):
        if i > 0 and i % PROGRESS_EVERY == 0:
            elapsed = time.time() - t_loop_start
            rate = i / elapsed
            remaining = (n_total - i) / rate if rate > 0 else float("inf")
            pct = 100.0 * i / n_total
            print("[{}] {}/{} ({:.1f}%) -- {:.0f} evt/s -- elapsed {:.0f}s -- "
                  "est. remaining {:.0f}s -- {} CC-numu so far, {} passing signal".format(
                      gen_name, i, n_total, pct, rate, elapsed, remaining, n_ccnumu, n_pass))

        ev = arrs[i]

        weight_val = float(ev.Weight)
        scalefactor_val = float(ev.fScaleFactor)
        eNu = float(ev.Enu_true)

        is_ccnumu = bool(ev.cc == 1 and int(ev.PDGnu) == 14)

        is_target = False
        muonKE = 0.0
        protonKE = 0.0
        pionKE = 0.0
        delPTT = 0.0
        pN = 0.0
        delAlphaT = 0.0
        n_mu = 0
        n_pi = 0
        n_p = 0
        n_vertex_other = 0

        if is_ccnumu:
            n_ccnumu += 1

            pdg = np.asarray(ev.pdg)
            px = np.asarray(ev.px)
            py = np.asarray(ev.py)
            pz = np.asarray(ev.pz)
            E = np.asarray(ev.E)  # GeV

            KE_MeV = ke_from_fourmom(px, py, pz, E) * 1000.0

            def passes(species_pdg):
                lo, hi = THRESH[species_pdg]
                mask = (pdg == species_pdg) & (KE_MeV >= lo) & (KE_MeV <= hi)
                return np.where(mask)[0]

            mu_idx = passes(13)  # mu- ONLY
            p_idx = passes(2212)
            pi_idx = np.concatenate([passes(211), passes(-211)])

            n_mu = len(mu_idx)
            n_pi = len(pi_idx)
            n_p = len(p_idx)

            # Primary vertex whitelist check (pre-FSI). Exclude the
            # incoming neutrino and the struck nuclear target from the
            # check -- everything else present must be in
            # ALLOWED_VERTEX_PDG or the event is vetoed.
            pdg_vert = np.asarray(ev.pdg_vert)
            nu_pdg = int(ev.PDGnu)
            tgt_pdg = int(ev.tgt)

            for v in pdg_vert:
                v = int(v)
                if v == nu_pdg or v == tgt_pdg:
                    continue
                if v in ALLOWED_VERTEX_PDG:
                    continue
                n_vertex_other += 1
                unknown_codes_seen.add(v)

            is_target = (n_vertex_other == 0 and n_mu == 1 and n_pi == 1 and n_p >= 1)

            if is_target:
                mu_i = mu_idx[0]
                muonKE = KE_MeV[mu_i]
                muMom = np.array([px[mu_i], py[mu_i], pz[mu_i]])
                energyMu = E[mu_i]

                pi_i = pi_idx[np.argmax(E[pi_idx])]
                pionKE = KE_MeV[pi_i]
                piMom = np.array([px[pi_i], py[pi_i], pz[pi_i]])
                energyPi = E[pi_i]

                p_i = p_idx[np.argmax(E[p_idx])]
                protonKE = KE_MeV[p_i]
                pMom = np.array([px[p_i], py[p_i], pz[p_i]])
                energyP = E[p_i]

                z = tki.getTransverseAxis(eNu, muMom[0], muMom[1], muMom[2])
                delPTT = tki.delPTT(z, piMom, pMom)

                delPT = tki.delPT(piMom[0], pMom[0], muMom[0], piMom[1], pMom[1], muMom[1])
                pLval = tki.pL(pMom[2], muMom[2], piMom[2], energyP, energyMu, energyPi, delPT)
                pN = np.sqrt(np.dot(delPT, delPT) + pLval ** 2)

                delAlphaT = np.degrees(tki.delAlphaT(muMom[0], muMom[1], delPT))

                n_pass += 1

        out["numuCC1piNp_is_ccnumu"].append(int(is_ccnumu))
        out["numuCC1piNp_is_target_cc_numu_1pi_nproton"].append(int(is_target))
        out["numuCC1piNp_muonKE"].append(muonKE)
        out["numuCC1piNp_protonKE"].append(protonKE)
        out["numuCC1piNp_pionKE"].append(pionKE)
        out["numuCC1piNp_delPTT"].append(delPTT)
        out["numuCC1piNp_pN"].append(pN)
        out["numuCC1piNp_delAlphaT"].append(delAlphaT)
        out["numuCC1piNp_debug_eNu"].append(eNu)
        out["Weight"].append(weight_val)
        out["fScaleFactor"].append(scalefactor_val)
        out["eventweight_weight"].append(weight_val)
        out["numuCC1piNp_debug_nmu"].append(n_mu)
        out["numuCC1piNp_debug_npi"].append(n_pi)
        out["numuCC1piNp_debug_nproton"].append(n_p)
        out["numuCC1piNp_debug_nvertex_other"].append(n_vertex_other)

    loop_elapsed = time.time() - t_loop_start
    rate_avg = n_total / loop_elapsed if loop_elapsed > 0 else 0.0
    print("[{}] loop finished in {:.0f}s ({:.0f} evt/s avg)".format(gen_name, loop_elapsed, rate_avg))
    print("[{}] {} total rows written -> {} CC-numu -> {} pass signal selection".format(
        gen_name, n_total, n_ccnumu, n_pass))
    if unknown_codes_seen:
        print("[{}] unknown vertex PDG codes encountered (triggered vetoes): {}".format(
            gen_name, sorted(unknown_codes_seen)))

    return {k: np.array(v) for k, v in out.items()}


def main():
    outdir = "cross_generator_tki_output"
    os.makedirs(outdir, exist_ok=True)

    t_start = time.time()
    for gen_name, fname in FILES.items():
        arrs = process_file(gen_name, fname)
        outpath = os.path.join(outdir, "{}_tki.root".format(gen_name))
        print("[{}] writing {}...".format(gen_name, outpath))
        with uproot.recreate(outpath) as f:
            f["analysis_tree"] = arrs
        print("[{}] saved.".format(gen_name))

    print("\nAll done in {:.0f}s total.".format(time.time() - t_start))


if __name__ == "__main__":
    main()