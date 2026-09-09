#!/usr/bin/env python3
"""
convert_detsys_for_profit.py

Converts detector variation histogram pairs (CV + variation) from
detsys_cv_run4b_nu_cv.root into a fractional covariance TMatrixD
suitable for PROfit's external_covariance systematic type.

Histogram naming convention (from ubdetsys_producer.py):
  hreco_neutrino_energy__{param}__cv
  hreco_neutrino_energy__{param}__var

For each variation k, the per-bin fractional shift is:
  delta^k_b = (var^k_b - cv^k_b) / cv^k_b

The fractional covariance is the sum of outer products over all variations:
  C_ij = sum_k  delta^k_i * delta^k_j

Native detsys histograms have 60 bins at 0.05 GeV/bin (0–3 GeV). Each
channel is rebinned independently to its PROfit reco binning (see
DETSYS_BIN_GROUPS):
  mmr_numu/pi0/0p/Np (21 bins): pairs of 2 native bins → 0.1 GeV each
                                  (0–2 GeV), then native bins 40–59 → overflow.
  mmr_nue            (13 bins): groups of 4 native bins → 0.2 GeV each
                                  (0–2.4 GeV), then native bins 48–59 → overflow.

Per-channel delta vectors are computed from the same underlying numu-channel
detsys histograms but with channel-appropriate bin groupings — the standard
approximation when per-channel DetVar histograms are not available.

The 97×97 channel-level matrix (4×21 + 13 bins) is expanded to 485×485
(subchannel-level), zeroing EXT subchannel rows/cols (beam-off data, not MC).

Channel/subchannel ordering (must match lantern_run4b_allchannels.xml):
  ch 0: mmr_numu  -> sub 0:numuCC  1:nueCCbg  2:NC 3:ext(zero) 4:dirt  [21 bins]
  ch 1: mmr_nue   -> sub 0:nueCC   1:numuCCbg 2:NC 3:ext(zero) 4:dirt  [13 bins]
  ch 2: mmr_pi0   -> sub 0:numuCC  1:nueCCbg  2:NC 3:ext(zero) 4:dirt  [21 bins]
  ch 3: mmr_0p    -> sub 0:numuCC  1:nueCCbg  2:NC 3:ext(zero) 4:dirt  [21 bins]
  ch 4: mmr_Np    -> sub 0:numuCC  1:nueCCbg  2:NC 3:ext(zero) 4:dirt  [21 bins]

Usage:
  setup root (e.g. v6_28_12 -q e26:p3915:prof, same as convert_covar_for_profit.py)
  python3 convert_detsys_for_profit.py
"""

import sys
import numpy as np
import ROOT

DETSYS_FILE = "/exp/uboone/app/users/imani/lantern_ana/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nu_cv.root"
OUTPUT_FILE = "/exp/uboone/app/users/imani/lantern_ana/all_runs_mmr/run4b/root_files/detsys_final/detsys_covariance_run4b_tmatrix.root"

VARNAME = "reco_neutrino_energy"

DETSYS_PARAMS = [
    "LYAtt", "LYDown", "LYRayleigh",
    "wiremodX", "wiremodYZ",
    "recomb2", "SCE",
]

# ─── Per-channel configuration ────────────────────────────────────────────────
CHANNEL_NAMES       = ["mmr_numu", "mmr_nue", "mmr_pi0", "mmr_0p", "mmr_Np"]
CHANNEL_N_RECO_BINS = [21, 13, 21, 21, 21]   # matches lantern_run4b_allchannels.xml

N_CHANNELS         = len(CHANNEL_NAMES)
N_SUBCHANNELS      = 5
N_DETSYS_BINS      = 60   # native bin count in detsys histograms (0.05 GeV/bin, 0–3 GeV)
EXT_SUBCHANNEL_IDX = 3    # 0-indexed; 'ext' is the 4th subchannel in each channel

# Flat-index offsets into the channel-level (no-subchannel) matrix
CH_CHAN_OFFSETS: list[int] = []
_off = 0
for _n in CHANNEL_N_RECO_BINS:
    CH_CHAN_OFFSETS.append(_off)
    _off += _n
N_CH_TOTAL = _off   # 97

# Flat-index offsets into the subchannel-level matrix
_off = 0
for _n in CHANNEL_N_RECO_BINS:
    _off += N_SUBCHANNELS * _n
N_TOTAL_BINS = _off   # 485

# Precomputed lookup: flat subchannel index → (channel_idx, subchannel_idx, reco_bin)
_FLAT_TO_CSB: list[tuple[int, int, int]] = []
for _ch, _n in enumerate(CHANNEL_N_RECO_BINS):
    for _sc in range(N_SUBCHANNELS):
        for _b in range(_n):
            _FLAT_TO_CSB.append((_ch, _sc, _b))
assert len(_FLAT_TO_CSB) == N_TOTAL_BINS

# ─── Per-channel detsys bin groups ───────────────────────────────────────────
# Maps 60 native 0.05 GeV detsys bins to each channel's PROfit reco bins.
#
# numu/pi0/0p/Np (21 bins):
#   bins 0–19: pairs of adjacent native bins → 0.1 GeV each (0–2 GeV)
#   bin 20:    native bins 40–59 → overflow (2–3 GeV native; labeled 2–5 GeV)
#
# nue (13 bins):
#   bins 0–11: groups of 4 native bins → 0.2 GeV each (0–2.4 GeV)
#   bin 12:    native bins 48–59 → overflow (2.4–3 GeV native; labeled 2.4–5 GeV)
_DETSYS_GROUPS_21 = [[2 * b, 2 * b + 1] for b in range(20)] + [list(range(40, 60))]
_DETSYS_GROUPS_13 = [[4 * b, 4 * b + 1, 4 * b + 2, 4 * b + 3] for b in range(12)] + [list(range(48, 60))]

DETSYS_BIN_GROUPS: dict[str, list[list[int]]] = {
    "mmr_numu": _DETSYS_GROUPS_21,
    "mmr_nue":  _DETSYS_GROUPS_13,
    "mmr_pi0":  _DETSYS_GROUPS_21,
    "mmr_0p":   _DETSYS_GROUPS_21,
    "mmr_Np":   _DETSYS_GROUPS_21,
}

ROOT.gROOT.SetBatch(True)


def th1_to_array(h):
    """Read a TH1 (no overflow) into a numpy array."""
    return np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])


def rebin_channel(arr, channel_name):
    """Rebin a 60-bin detsys array to PROfit bins for the given channel."""
    groups = DETSYS_BIN_GROUPS[channel_name]
    return np.array([arr[g].sum() for g in groups])


def expand_channel_to_subchannel(frac_ch):
    """
    Expand a N_CH_TOTAL×N_CH_TOTAL channel-level fractional covariance to
    N_TOTAL_BINS×N_TOTAL_BINS subchannel-level, zeroing EXT rows/cols.
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
    n, m = a.shape
    mat = ROOT.TMatrixD(n, m)
    for i in range(n):
        for j in range(m):
            mat[i][j] = float(a[i, j])
    return mat


def main():
    fin = ROOT.TFile.Open(DETSYS_FILE, "READ")
    if not fin or fin.IsZombie():
        print(f"ERROR: Cannot open {DETSYS_FILE}", file=sys.stderr)
        sys.exit(1)

    all_keys  = sorted(k.GetName() for k in fin.GetListOfKeys())
    reco_keys = [k for k in all_keys if VARNAME in k]
    print(f"Found {len(reco_keys)} histograms containing '{VARNAME}':")
    for k in reco_keys[:20]:
        print(f"  {k}")
    if len(reco_keys) > 20:
        print(f"  ... ({len(reco_keys)} total)")

    # Accumulate one 97×97 fractional covariance per parameter
    per_param_frac = {}    # param -> 97×97 numpy array
    frac_total     = np.zeros((N_CH_TOTAL, N_CH_TOTAL), dtype=np.float64)
    n_loaded       = 0

    for param in DETSYS_PARAMS:
        cv_name  = f"h{VARNAME}__{param}__cv"
        var_name = f"h{VARNAME}__{param}__var"

        h_cv  = fin.Get(cv_name)
        h_var = fin.Get(var_name)

        if not h_cv or h_cv.IsZombie():
            print(f"  WARNING: CV not found: '{cv_name}' — skipping {param}")
            continue
        if not h_var or h_var.IsZombie():
            print(f"  WARNING: var not found: '{var_name}' — skipping {param}")
            continue

        h_cv.SetDirectory(0)
        h_var.SetDirectory(0)

        cv_60  = th1_to_array(h_cv)
        var_60 = th1_to_array(h_var)

        if len(cv_60) != N_DETSYS_BINS:
            print(f"  WARNING: {param} has {len(cv_60)} bins, expected {N_DETSYS_BINS} — skipping")
            continue

        # Compute per-channel delta vectors using channel-specific bin groupings
        per_ch_delta = {}
        for name in CHANNEL_NAMES:
            cv_r  = rebin_channel(cv_60,  name)
            var_r = rebin_channel(var_60, name)
            per_ch_delta[name] = np.where(cv_r > 0, (var_r - cv_r) / cv_r, 0.0)

        # Build 97×97 channel-level fractional covariance as sum of outer products
        frac_97 = np.zeros((N_CH_TOTAL, N_CH_TOTAL), dtype=np.float64)
        for ch_r, name_r in enumerate(CHANNEL_NAMES):
            for ch_c, name_c in enumerate(CHANNEL_NAMES):
                r0 = CH_CHAN_OFFSETS[ch_r]
                c0 = CH_CHAN_OFFSETS[ch_c]
                nr = CHANNEL_N_RECO_BINS[ch_r]
                nc = CHANNEL_N_RECO_BINS[ch_c]
                frac_97[r0:r0 + nr, c0:c0 + nc] = np.outer(per_ch_delta[name_r],
                                                             per_ch_delta[name_c])

        per_param_frac[param] = frac_97
        frac_total += frac_97

        delta_numu = per_ch_delta["mmr_numu"]
        print(f"  [ok] {param:15s}  max|delta_numu|={np.max(np.abs(delta_numu)):.4f}  "
              f"rms|delta_numu|={np.sqrt(np.mean(delta_numu**2)):.4f}")
        n_loaded += 1

    fin.Close()
    print(f"\nLoaded {n_loaded}/{len(DETSYS_PARAMS)} variations "
          f"(rebinned {N_DETSYS_BINS} native bins → per-channel PROfit bins).")

    if n_loaded == 0:
        print("ERROR: No variations loaded. Check histogram names above vs VARNAME/DETSYS_PARAMS.")
        sys.exit(1)

    fout = ROOT.TFile.Open(OUTPUT_FILE, "RECREATE")
    if not fout or fout.IsZombie():
        print(f"ERROR: Cannot create {OUTPUT_FILE}", file=sys.stderr)
        sys.exit(1)
    fout.cd()

    matrices_written = []

    for param, frac_97 in per_param_frac.items():
        print(f"  Expanding {param:15s} {N_CH_TOTAL}×{N_CH_TOTAL} → {N_TOTAL_BINS}×{N_TOTAL_BINS} ...",
              end=" ", flush=True)
        mat_name = f"fracCOV_detsys_{param}"
        numpy_to_tmatrixd(expand_channel_to_subchannel(frac_97)).Write(mat_name)
        matrices_written.append(mat_name)
        print("done")

    print(f"  Expanding combined    {N_CH_TOTAL}×{N_CH_TOTAL} → {N_TOTAL_BINS}×{N_TOTAL_BINS} ...",
          end=" ", flush=True)
    frac_485_total = expand_channel_to_subchannel(frac_total)
    numpy_to_tmatrixd(frac_485_total).Write("fracCOV_detsys")
    matrices_written.append("fracCOV_detsys")
    print("done")

    fout.Close()

    diag = np.diag(frac_485_total)
    nonzero_diag = diag[diag > 0]
    print(f"\nCombined diagonal range: [{diag.min():.6f}, {diag.max():.6f}]")
    if len(nonzero_diag) > 0:
        print(f"Typical combined fractional unc: {np.sqrt(nonzero_diag.mean()):.4f} (mean sqrt of diag)")

    print(f"\nWrote {len(matrices_written)} TMatrixD objects → {OUTPUT_FILE}")
    print("\nReplace the <allowlist> entries in lantern_run4b_allchannels.xml with:")
    print("""
    <!-- Detector variation covariance — one entry per parameter so each appears  -->
    <!-- separately in fractional systematics plots. Built from                   -->
    <!-- detsys_cv_run4b_nu_cv.root. Re-run convert_detsys_for_profit.py if       -->
    <!-- the upstream detsys histograms change.                                   -->""")
    for param in per_param_frac:
        print(f'    <allowlist type="external_covariance" binning="var0"'
              f'\n               filename="{OUTPUT_FILE}"'
              f'\n               tag="DetVar">fracCOV_detsys_{param}</allowlist>')


if __name__ == "__main__":
    main()
