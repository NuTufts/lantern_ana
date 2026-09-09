#!/usr/bin/env python3
"""
convert_covar_for_profit.py

PROfit's external_covariance systematic type requires TMatrixD objects and
counts bins at the SUBCHANNEL level.  Channels now use heterogeneous reco
binning:
  mmr_numu, mmr_pi0, mmr_0p, mmr_Np : 21 bins (20 × 0.1 GeV [0–2 GeV] + overflow [2–5 GeV])
  mmr_nue                             : 13 bins (12 × 0.2 GeV [0–2.4 GeV] + overflow [2.4–5 GeV])

Channel-level total : 4×21 + 13 = 97 bins
Subchannel-level    : 97 × 5 subchannels = 485 bins  (matrix is 485×485)

The lantern_ana covariance pipeline produces TH2D histograms at the CHANNEL
level, one per systematic parameter.  This script supports two input formats:
  - 97×97  (current heterogeneous format)
  - 150×150 (legacy 30-bin uniform format — rebinned automatically using hNN)

This script:
  1. Reads each hfrac_covar_* TH2D (channel-level fractional covariance)
  2. Groups parameters by type (flux / xsec / reint) according to PARAM_GROUPS
  3. Sums fractional covariance matrices within each type group
  4. If input is 150×150, rebins to 97×97 using per-channel aggregation groups
     and the hNN histogram (N_i×N_j) from the input file for CV recovery.
  5. Expands each 97×97 group sum to 485×485 by replicating each channel-pair
     element across all subchannel pairs in that channel pair
  6. Zeroes out rows/cols belonging to EXT subchannels (incl_systematics=false)
  7. Writes four TMatrixD objects to a new file for PROfit:
       fracCOV_flux   — BNB flux
       fracCOV_xsec   — cross-section (UBGenie + SCC)
       fracCOV_reint  — hadronic re-interactions (Geant4)
       fracCOV_sys    — total (flux + xsec + reint combined)

Channel/subchannel ordering matches lantern_run4b_allchannels.xml:
  ch 0: mmr_numu  → sub 0:numuCC  1:nueCCbg  2:NC 3:ext(zero) 4:dirt
  ch 1: mmr_nue   → sub 0:nueCC   1:numuCCbg 2:NC 3:ext(zero) 4:dirt
  ch 2: mmr_pi0   → sub 0:numuCC  1:nueCCbg  2:NC 3:ext(zero) 4:dirt
  ch 3: mmr_0p    → sub 0:numuCC  1:nueCCbg  2:NC 3:ext(zero) 4:dirt
  ch 4: mmr_Np    → sub 0:numuCC  1:nueCCbg  2:NC 3:ext(zero) 4:dirt

The channel-level input matrix is ordered: ch_numu | ch_nue | ch_pi0 | ch_0p | ch_Np
matching the xsecflux YAML bin_config order.

Usage:
  source /cvmfs/larsoft.opensciencegrid.org/setup_larsoft.sh
  setup root v6_28_12 -q e26:p3915:prof
  python3 convert_covar_for_profit.py
"""

import sys
import numpy as np
import ROOT

INPUT_FILE  = "/exp/uboone/app/users/imani/lantern_ana/studies/xsecfluxsys/output_covariance_run4b_allchannels.root"
OUTPUT_FILE = "/exp/uboone/app/users/imani/lantern_ana/studies/xsecfluxsys/output_covariance_run4b_allchannels_tmatrix.root"

# ─── Per-channel configuration ────────────────────────────────────────────────
CHANNEL_NAMES       = ["mmr_numu", "mmr_nue", "mmr_pi0", "mmr_0p", "mmr_Np"]
CHANNEL_N_RECO_BINS = [21, 13, 21, 21, 21]   # matches lantern_run4b_allchannels.xml

N_CHANNELS         = len(CHANNEL_NAMES)
N_SUBCHANNELS      = 5    # numuCC/nueCC, nueCCbg/numuCCbg, NC, ext, dirt
EXT_SUBCHANNEL_IDX = 3    # zero-indexed position of 'ext' in each channel's subchannel list

# Flat-index offsets into the channel-level (no-subchannel) matrix
CH_CHAN_OFFSETS: list[int] = []
_off = 0
for _n in CHANNEL_N_RECO_BINS:
    CH_CHAN_OFFSETS.append(_off)
    _off += _n
N_CH_TOTAL = _off   # 97

# Flat-index offsets into the subchannel-level matrix
CH_SUB_OFFSETS: list[int] = []
_off = 0
for _n in CHANNEL_N_RECO_BINS:
    CH_SUB_OFFSETS.append(_off)
    _off += N_SUBCHANNELS * _n
N_TOTAL_BINS = _off   # 485

# Precomputed lookup: flat subchannel index → (channel_idx, subchannel_idx, reco_bin)
_FLAT_TO_CSB: list[tuple[int, int, int]] = []
for _ch, _n in enumerate(CHANNEL_N_RECO_BINS):
    for _sc in range(N_SUBCHANNELS):
        for _b in range(_n):
            _FLAT_TO_CSB.append((_ch, _sc, _b))
assert len(_FLAT_TO_CSB) == N_TOTAL_BINS

# ─── Legacy rebinning (150×150 → 97×97) ──────────────────────────────────────
_OLD_N_RECO_BINS = 30   # legacy uniform 30-bin format

# Per-channel aggregation groups: old 30 uniform 0.1 GeV bins → new per-channel bins.
#   numu/pi0/0p/Np (30→21): bins 0–19 stay 1:1; bins 20–29 merge into overflow bin 20.
#   nue           (30→13): pairs of 2 for old bins 0–23 (→ 0.2 GeV each);
#                           old bins 24–29 merge into overflow bin 12.
_GROUPS_21 = [[b] for b in range(20)] + [list(range(20, 30))]
_GROUPS_13 = [[2 * b, 2 * b + 1] for b in range(12)] + [list(range(24, 30))]

OLD_CH_GROUPS: dict[str, list[list[int]]] = {
    "mmr_numu": _GROUPS_21,
    "mmr_nue":  _GROUPS_13,
    "mmr_pi0":  _GROUPS_21,
    "mmr_0p":   _GROUPS_21,
    "mmr_Np":   _GROUPS_21,
}

# ─── Parameter → type mapping ─────────────────────────────────────────────────
PARAM_GROUPS = {
    "flux": [
        "flux_all",
    ],
    "xsec": [
        "All_UBGenie",
        "XSecShape_CCMEC_UBGenie",
        "RPA_CCQE_UBGenie",
        "AxFFCCQEshape_UBGenie",
        "VecFFCCQEshape_UBGenie",
        "DecayAngMEC_UBGenie",
        "xsr_scc_Fa3_SCC",
        "xsr_scc_Fv3_SCC",
        "NormCCCOH_UBGenie",
        "NormNCCOH_UBGenie",
        "ThetaDelta2NRad_UBGenie",
        "Theta_Delta2Npi_UBGenie",
    ],
    "reint": [
        "reint_all",
    ],
}

PARAM_TO_GROUP = {
    par: group
    for group, params in PARAM_GROUPS.items()
    for par in params
}

ROOT.gROOT.SetBatch(True)


def th2d_to_numpy(h2):
    """Read a TH2D (no-overflow) into a numpy array."""
    nx, ny = h2.GetNbinsX(), h2.GetNbinsY()
    a = np.zeros((nx, ny), dtype=np.float64)
    for i in range(nx):
        for j in range(ny):
            a[i, j] = h2.GetBinContent(i + 1, j + 1)
    return a


def rebin_old_to_new(frac_old, hNN_arr):
    """
    Rebin a 150×150 (30 bins/channel uniform) fractional covariance to the
    current heterogeneous 97×97 layout using OLD_CH_GROUPS.

    Uses hNN (N_i×N_j matrix written by make_covar_matrices.py) to recover
    per-bin CV values for the frac → abs → rebin → frac conversion.
    """
    old_size = N_CHANNELS * _OLD_N_RECO_BINS   # 150

    cv_old = np.sqrt(np.maximum(np.diag(hNN_arr), 0.0))

    # Build 97×150 aggregation matrix A
    A = np.zeros((N_CH_TOTAL, old_size), dtype=np.float64)
    old_off = 0
    for ch, name in enumerate(CHANNEL_NAMES):
        new_off = CH_CHAN_OFFSETS[ch]
        for nb, old_bins in enumerate(OLD_CH_GROUPS[name]):
            for ob in old_bins:
                A[new_off + nb, old_off + ob] = 1.0
        old_off += _OLD_N_RECO_BINS

    abs_old = frac_old * np.outer(cv_old, cv_old)
    abs_new = A @ abs_old @ A.T
    cv_new  = A @ cv_old
    denom   = np.outer(cv_new, cv_new)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(denom > 0, abs_new / denom, 0.0)


def expand_channel_to_subchannel(frac_ch):
    """
    Expand a N_CH_TOTAL×N_CH_TOTAL channel-level fractional covariance to
    N_TOTAL_BINS×N_TOTAL_BINS subchannel-level, zeroing EXT rows/cols.

    For each flat subchannel index r → (channel_r, subchannel_r, reco_bin_r)
    via _FLAT_TO_CSB.  The channel-level source element is:
      frac_ch[CH_CHAN_OFFSETS[ch_r] + bin_r, CH_CHAN_OFFSETS[ch_c] + bin_c]
    """
    assert frac_ch.shape == (N_CH_TOTAL, N_CH_TOTAL), \
        f"Expected {N_CH_TOTAL}×{N_CH_TOTAL}, got {frac_ch.shape}"

    frac_total = np.zeros((N_TOTAL_BINS, N_TOTAL_BINS), dtype=np.float64)

    for r, (ch_r, sc_r, bin_r) in enumerate(_FLAT_TO_CSB):
        if sc_r == EXT_SUBCHANNEL_IDX:
            continue
        chan_r = CH_CHAN_OFFSETS[ch_r] + bin_r
        for c, (ch_c, sc_c, bin_c) in enumerate(_FLAT_TO_CSB):
            if sc_c == EXT_SUBCHANNEL_IDX:
                continue
            chan_c = CH_CHAN_OFFSETS[ch_c] + bin_c
            frac_total[r, c] = frac_ch[chan_r, chan_c]

    return frac_total


def numpy_to_tmatrixd(a):
    """Convert a 2-D numpy array to a ROOT TMatrixD."""
    n, m = a.shape
    mat = ROOT.TMatrixD(n, m)
    for i in range(n):
        for j in range(m):
            mat[i][j] = float(a[i, j])
    return mat


def main():
    fin = ROOT.TFile.Open(INPUT_FILE, "READ")
    if not fin or fin.IsZombie():
        print(f"ERROR: Cannot open {INPUT_FILE}", file=sys.stderr)
        sys.exit(1)

    # Detect input matrix size: 97×97 (current) or 150×150 (legacy 30-bin)
    N_CH_OLD = N_CHANNELS * _OLD_N_RECO_BINS   # 150
    input_size = N_CH_TOTAL
    hNN_arr = None

    for key in fin.GetListOfKeys():
        name = key.GetName()
        if not name.startswith("hfrac_covar_"):
            continue
        obj = fin.Get(name)
        if not isinstance(obj, ROOT.TH2):
            continue
        sz = obj.GetNbinsX()
        if sz == N_CH_OLD:
            input_size = N_CH_OLD
            print(f"Input matrices are {N_CH_OLD}×{N_CH_OLD} (30-bin legacy) "
                  f"— will rebin to {N_CH_TOTAL}×{N_CH_TOTAL}.")
            hNN = fin.Get("hNN")
            if not hNN or hNN.IsZombie():
                print("ERROR: 'hNN' not found — cannot rebin. "
                      "Re-run make_covar_matrices.py.", file=sys.stderr)
                sys.exit(1)
            hNN_arr = th2d_to_numpy(hNN)
        elif sz == N_CH_TOTAL:
            print(f"Input matrices are {N_CH_TOTAL}×{N_CH_TOTAL} (current format).")
        else:
            print(f"ERROR: unexpected matrix size {sz}×{sz} in '{name}' "
                  f"(expected {N_CH_TOTAL} or {N_CH_OLD}).", file=sys.stderr)
            sys.exit(1)
        break

    # Accumulate channel-level fractional covariance sums per group
    group_sums = {g: np.zeros((input_size, input_size), dtype=np.float64)
                  for g in PARAM_GROUPS}
    group_counts = {g: 0 for g in PARAM_GROUPS}
    skipped = []

    for key in fin.GetListOfKeys():
        name = key.GetName()
        obj  = fin.Get(name)

        if not isinstance(obj, ROOT.TH2):
            continue
        if obj.GetNbinsX() != input_size or obj.GetNbinsY() != input_size:
            continue
        if not name.startswith("hfrac_covar_"):
            continue

        par   = name[len("hfrac_covar_"):]
        group = PARAM_TO_GROUP.get(par)
        if group is None:
            skipped.append(par)
            continue

        print(f"  [{group}] accumulating {name} ...")
        group_sums[group] += th2d_to_numpy(obj)
        group_counts[group] += 1

    fin.Close()

    if skipped:
        print(f"\nSkipped (not in any group): {skipped}")

    # Rebin 150×150 → 97×97 if legacy input was detected
    if hNN_arr is not None:
        print(f"\nRebinning {N_CH_OLD}×{N_CH_OLD} → {N_CH_TOTAL}×{N_CH_TOTAL} ...")
        for g in PARAM_GROUPS:
            group_sums[g] = rebin_old_to_new(group_sums[g], hNN_arr)
            print(f"  {g} done")

    total_sum = sum(group_sums.values())

    fout = ROOT.TFile.Open(OUTPUT_FILE, "RECREATE")
    if not fout or fout.IsZombie():
        print(f"ERROR: Cannot create {OUTPUT_FILE}", file=sys.stderr)
        sys.exit(1)

    output_matrices = list(PARAM_GROUPS.keys()) + ["sys"]

    for label in output_matrices:
        frac_ch  = group_sums[label] if label != "sys" else total_sum
        count    = group_counts.get(label, sum(group_counts.values()))
        tname    = f"fracCOV_{label}"

        if label != "sys" and count == 0:
            print(f"\nWARNING: no matrices found for group '{label}', {tname} will be all zeros")

        print(f"\n  Expanding {tname}  {N_CH_TOTAL}×{N_CH_TOTAL} → {N_TOTAL_BINS}×{N_TOTAL_BINS} ...",
              end=" ", flush=True)
        mat = numpy_to_tmatrixd(expand_channel_to_subchannel(frac_ch))
        fout.cd()
        mat.Write(tname)
        print("done")

    fout.Close()

    print(f"\nWrote {len(output_matrices)} TMatrixD objects ({N_TOTAL_BINS}×{N_TOTAL_BINS}) → {OUTPUT_FILE}")
    print("\nObjects written:")
    for label in output_matrices:
        print(f"  fracCOV_{label}  ({group_counts.get(label, sum(group_counts.values()))} input matrices summed)")
    print("\nQuick check:")
    print(f"  root -l -b -q -e 'TFile f(\"{OUTPUT_FILE}\"); f.ls();'")
    print("\nSuggested PROfit XML snippet:")
    for label in output_matrices:
        print(f'  <allowlist type="external_covariance" binning="var0" '
              f'filename="{OUTPUT_FILE}" tag="Covariance">fracCOV_{label}</allowlist>')


if __name__ == "__main__":
    main()
