"""
find_adaptive_bins.py

Checks whether the Run 3 Contained adaptive bin edges give >= MIN_COUNTS
raw MC events for other run/containment combinations.

Usage:
    python3 find_adaptive_bins.py --run 1 --contained
    python3 find_adaptive_bins.py --run 1 --uncontained
    python3 find_adaptive_bins.py --run 3 --contained
    python3 find_adaptive_bins.py --run 3 --uncontained

If run/containment is Run 3 Contained, it recomputes the adaptive binning.
For all others, it checks the fixed Run 3 Contained bin edges against that
combination's CV histogram and reports whether all bins have >= MIN_COUNTS.
"""

import sys
import array
import argparse
import ROOT as rt

rt.gROOT.SetBatch(True)

MIN_COUNTS  = 10.0
LANTERN_DIR = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana"

# ── Run configurations ────────────────────────────────────────────────────────
RUN_CONFIGS = {
    (1, True): {
        "xsecflux": f"{LANTERN_DIR}/studies/xsecfluxsys/systematics_output_run1_march2026_contained/output_xsecflux_tki_run1_march2026_contained.root",
        "sample":   "run1_bnb_nu_overlay_mcc9_v28_wctagger",
    },
    (1, False): {
        "xsecflux": f"{LANTERN_DIR}/studies/xsecfluxsys/systematics_output_run1_march2026_uncontained/output_xsecflux_tki_run1_march2026_uncontained.root",
        "sample":   "run1_bnb_nu_overlay_mcc9_v28_wctagger",
    },
    (3, True): {
        "xsecflux": f"{LANTERN_DIR}/studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux_contained/output_xsecflux_tki_run3b_1mil_contained.root",
        "sample":   "mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil",
    },
    (3, False): {
        "xsecflux": f"{LANTERN_DIR}/studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux_uncontained/output_xsecflux_tki_run3b_1mil_uncontained.root",
        "sample":   "mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil",
    },
}

# ── Original uniform bin config (for adaptive rebinning of Run 1 Contained) ──
VARS_UNIFORM = [
    ("numuCC1piNpReco_delAlphaT",   10,   0.0,  180.0, "delAlphaT (deg)"),
    ("numuCC1piNpReco_pN",          25,   0.0,    1.6, "pN (GeV/c)"),
    ("numuCC1piNpReco_delPTT",      25,  -1.0,    1.0, "delPTT (GeV/c)"),
    ("numuCC1piNpReco_muKE",        25,   0.0, 1500.0, "muKE (MeV)"),
    ("numuCC1piNpReco_pionKE",      25,   0.0,  500.0, "pionKE (MeV)"),
    ("numuCC1piNpReco_maxprotonKE", 25,   0.0,  500.0, "maxprotonKE (MeV)"),
]

# ── Fixed Run 3 Contained adaptive bin edges (reference/bottleneck) ────────────
RUN3_CONTAINED_EDGES = {
    "numuCC1piNpReco_delAlphaT":   [0.0, 18.0, 36.0, 54.0, 72.0, 90.0, 108.0, 126.0, 144.0, 162.0, 180.0],
    "numuCC1piNpReco_pN":          [0.0, 0.064, 0.128, 0.192, 0.256, 0.32, 0.384, 0.448, 0.512, 0.576, 0.64, 0.704, 0.768, 0.832, 0.96, 1.024, 1.6],
    "numuCC1piNpReco_delPTT":      [-1.0, -0.44, -0.36, -0.28, -0.2, -0.12, -0.04, 0.04, 0.12, 0.2, 0.28, 0.36, 0.44, 0.52, 1.0],
    "numuCC1piNpReco_muKE":        [0.0, 60.0, 120.0, 180.0, 240.0, 300.0, 360.0, 420.0, 480.0, 540.0, 600.0, 660.0, 720.0, 780.0, 840.0, 900.0, 960.0, 1200.0, 1500.0],
    "numuCC1piNpReco_pionKE":      [0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 500.0],
    "numuCC1piNpReco_maxprotonKE": [0.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 300.0, 320.0, 340.0, 360.0, 380.0, 400.0, 500.0],
}


# ─────────────────────────────────────────────────────────────────────────────
def get_bin_edges(h):
    return [h.GetXaxis().GetBinLowEdge(i) for i in range(1, h.GetNbinsX() + 2)]


def adaptive_rebin(h, min_counts):
    """Merge bins left-to-right until each has >= min_counts."""
    nbins     = h.GetNbinsX()
    old_edges = get_bin_edges(h)
    counts    = [h.GetBinContent(i) for i in range(1, nbins + 1)]

    new_edges   = [old_edges[0]]
    accumulated = 0.0

    for i in range(nbins):
        accumulated += counts[i]
        if accumulated >= min_counts:
            new_edges.append(old_edges[i + 1])
            accumulated = 0.0

    # If last group didn't reach min_counts (including zero count), merge into previous
    if accumulated < min_counts and len(new_edges) > 1:
        # Drop the last internal edge so the last two groups merge
        new_edges[-1] = old_edges[nbins]
    else:
        if new_edges[-1] != old_edges[nbins]:
            new_edges.append(old_edges[nbins])

    return new_edges


def check_bin_counts(hcv, edges, varname):
    """
    For each new bin defined by edges, sum the CV counts over all original
    bins whose centres fall inside, and report whether >= MIN_COUNTS.
    """
    n_new   = len(edges) - 1
    results = []
    n_orig  = hcv.GetNbinsX()

    for i in range(n_new):
        lo    = edges[i]
        hi    = edges[i + 1]
        total = 0.0
        for orig_bin in range(1, n_orig + 1):
            centre = hcv.GetXaxis().GetBinCenter(orig_bin)
            if lo <= centre < hi or (i == n_new - 1 and abs(centre - hi) < 1e-9):
                total += hcv.GetBinContent(orig_bin)
        results.append((i + 1, lo, hi, total))

    return results


def print_bin_table(results, label):
    all_ok = True
    print(f"\n  {label}:")
    print(f"  {'bin':>4}  {'lo':>10}  {'hi':>10}  {'count':>10}  {'ok?':>6}")
    for binnum, lo, hi, count in results:
        ok = "OK" if count >= MIN_COUNTS else "LOW !"
        if count < MIN_COUNTS:
            all_ok = False
        print(f"  {binnum:>4}  {lo:>10.4f}  {hi:>10.4f}  {count:>10.2f}  {ok:>6}")
    if all_ok:
        print(f"  All bins >= {MIN_COUNTS} counts. ✓")
    else:
        print(f"  WARNING: some bins below {MIN_COUNTS}!")
    return all_ok


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=int, choices=[1, 3], default=1)
    parser.add_argument("--contained", dest="contained", action="store_true", default=True)
    parser.add_argument("--uncontained", dest="contained", action="store_false")
    args = parser.parse_args()

    run       = args.run
    contained = args.contained
    key       = (run, contained)
    cfg       = RUN_CONFIGS[key]
    label     = f"Run {run} {'Contained' if contained else 'Uncontained'}"

    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  xsecflux: {cfg['xsecflux']}")
    print(f"{'='*60}")

    xfile = rt.TFile(cfg["xsecflux"])
    if not xfile or xfile.IsZombie():
        print(f"ERROR: cannot open {cfg['xsecflux']}")
        sys.exit(1)

    is_run3_contained = (run == 3 and contained)
    yaml_output = {}
    overall_ok  = True

    for varname, nbins, xlo, xhi, xtitle in VARS_UNIFORM:
        cv_name = f"h{varname}_{cfg['sample']}_cv"
        hcv     = xfile.Get(cv_name)
        if not hcv or hcv.IsZombie():
            print(f"\nERROR: CV not found: {cv_name}")
            continue

        print(f"\n{'='*60}")
        print(f"  {varname}  (CV integral = {hcv.Integral():.1f})")

        if is_run3_contained:
            # Compute adaptive binning from scratch
            edges = adaptive_rebin(hcv, MIN_COUNTS)
            print(f"  Computing adaptive bins for Run 3 Contained (reference)...")
        else:
            # Use fixed Run 3 Contained edges
            edges = RUN3_CONTAINED_EDGES[varname]
            print(f"  Checking Run 3 Contained bin edges against {label}...")

        results = check_bin_counts(hcv, edges, varname)
        ok      = print_bin_table(results, label)
        if not ok:
            overall_ok = False

        edges_rounded = [round(e, 4) for e in edges]
        yaml_output[varname] = edges_rounded
        print(f"\n  edges: {edges_rounded}")

    # ── YAML summary ──────────────────────────────────────────────────────────
    print(f"\n\n{'='*60}")
    print(f"YAML OUTPUT for {label}:")
    print(f"{'='*60}\n")
    for varname, edges in yaml_output.items():
        edges_str = ", ".join(str(e) for e in edges)
        print(f"        {varname}:")
        print(f"          formula: {varname}")
        print(f"          binedges: [{edges_str}]")
        print(f"          apply_to_datasets: ['{cfg['sample']}']")
        print(f"          criteria: []")
        print()

    if overall_ok:
        print(f"✓ All bins >= {MIN_COUNTS} counts for {label} with Run 3 Contained edges.")
    else:
        print(f"✗ Some bins below {MIN_COUNTS} counts — may need separate adaptive binning for {label} (Run 3 Contained edges used as reference).")

    xfile.Close()
    print("\nDone.")