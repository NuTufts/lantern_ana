"""
find_adaptive_bins.py

Reads the unscaled MC CV histograms from the xsecflux file and finds
adaptive bin edges such that every bin has >= MIN_COUNTS MC events.

Merges from both tails inward so that the tails (which have few events)
get merged first, preserving resolution in the populated central region.

Prints new bin edges in yaml format ready to copy-paste.

Usage:
    python3 find_adaptive_bins.py
"""

import sys
import ROOT as rt

rt.gROOT.SetBatch(True)

# ── Config ────────────────────────────────────────────────────────────────────
XSECFLUX_FILE = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/systematics_output_run1_march2026_contained/output_xsecflux_tki_run1_march2026_contained.root"
SAMPLE        = "run1_bnb_nu_overlay_mcc9_v28_wctagger"
MIN_COUNTS    = 10.0   # minimum MC events per bin

# Current bin config (uniform binning)
VARS = [
    ("numuCC1piNpReco_delAlphaT",   10,   0.0,  180.0, "#Delta#alpha_{T} (deg)"),
    ("numuCC1piNpReco_pN",          25,   0.0,    1.6, "p_{N} (GeV/c)"),
    ("numuCC1piNpReco_delPTT",      25,  -1.0,    1.0, "#Delta p_{TT} (GeV/c)"),
    ("numuCC1piNpReco_muKE",        25,   0.0, 1500.0, "Muon KE (MeV)"),
    ("numuCC1piNpReco_pionKE",      25,   0.0,  500.0, "Pion KE (MeV)"),
    ("numuCC1piNpReco_maxprotonKE", 25,   0.0,  500.0, "Max Proton KE (MeV)"),
]


# ─────────────────────────────────────────────────────────────────────────────
def get_bin_edges(h):
    """Return list of all bin edges (nbins+1 values) from a TH1."""
    edges = []
    for i in range(1, h.GetNbinsX() + 2):
        edges.append(h.GetXaxis().GetBinLowEdge(i))
    return edges


def adaptive_rebin(h, min_counts):
    """
    Adaptive rebinning algorithm.
    Merges bins from left to right, accumulating until sum >= min_counts.
    If the last group is below min_counts, merges it into the previous group.

    Returns a list of new bin edges (floats).
    """
    nbins     = h.GetNbinsX()
    old_edges = get_bin_edges(h)
    counts    = [h.GetBinContent(i) for i in range(1, nbins + 1)]

    new_edges   = [old_edges[0]]   # always start from the left edge
    accumulated = 0.0
    group_start = 0

    for i in range(nbins):
        accumulated += counts[i]
        if accumulated >= min_counts:
            # This group has enough events — close it
            new_edges.append(old_edges[i + 1])
            accumulated = 0.0
            group_start = i + 1

    # If the last group didn't reach min_counts, merge into previous bin
    if accumulated > 0 and accumulated < min_counts and len(new_edges) > 1:
        # Remove the last internal edge to merge last two groups
        new_edges[-1] = old_edges[nbins]
    elif accumulated > 0:
        # Last group has enough events or is the only group
        if new_edges[-1] != old_edges[nbins]:
            new_edges[-1] = old_edges[nbins]

    # Ensure we always end at the histogram's right edge
    if new_edges[-1] != old_edges[nbins]:
        new_edges.append(old_edges[nbins])

    return new_edges


def verify_bins(h, new_edges):
    """
    Print the bin contents after rebinning so you can verify
    every bin meets the min_counts threshold.
    Returns list of (bin, lo_edge, hi_edge, count).
    """
    results = []
    for i in range(len(new_edges) - 1):
        lo  = new_edges[i]
        hi  = new_edges[i + 1]
        # Sum original bins that fall within [lo, hi)
        total = 0.0
        for orig_bin in range(1, h.GetNbinsX() + 1):
            edge_lo = h.GetXaxis().GetBinLowEdge(orig_bin)
            edge_hi = h.GetXaxis().GetBinUpEdge(orig_bin)
            # Include bin if its centre falls within the new bin
            centre = 0.5 * (edge_lo + edge_hi)
            if lo <= centre < hi or (i == len(new_edges) - 2 and centre == hi):
                total += h.GetBinContent(orig_bin)
        results.append((i + 1, lo, hi, total))
    return results


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    xfile = rt.TFile(XSECFLUX_FILE)
    if not xfile or xfile.IsZombie():
        print(f"ERROR: could not open {XSECFLUX_FILE}")
        sys.exit(1)

    yaml_output = {}

    for varname, nbins, xlo, xhi, xtitle in VARS:
        short   = varname.replace("numuCC1piNpReco_", "")
        cv_name = f"h{varname}_{SAMPLE}_cv"
        hcv     = xfile.Get(cv_name)

        if not hcv or hcv.IsZombie():
            print(f"ERROR: could not find {cv_name}")
            continue

        print(f"\n{'='*60}")
        print(f"  {short}  (total CV integral = {hcv.Integral():.1f})")
        print(f"{'='*60}")

        # Print original bin contents
        print(f"\n  Original bins ({nbins} uniform bins):")
        print(f"  {'bin':>4}  {'lo':>10}  {'hi':>10}  {'count':>10}  {'ok?':>6}")
        for i in range(1, nbins + 1):
            lo    = hcv.GetXaxis().GetBinLowEdge(i)
            hi    = hcv.GetXaxis().GetBinUpEdge(i)
            count = hcv.GetBinContent(i)
            ok    = "OK" if count >= MIN_COUNTS else "LOW"
            print(f"  {i:>4}  {lo:>10.3f}  {hi:>10.3f}  {count:>10.2f}  {ok:>6}")

        # Find new bin edges
        new_edges = adaptive_rebin(hcv, MIN_COUNTS)
        n_new     = len(new_edges) - 1

        # Verify
        verified = verify_bins(hcv, new_edges)

        print(f"\n  New adaptive bins ({n_new} bins, min={MIN_COUNTS} counts):")
        print(f"  {'bin':>4}  {'lo':>10}  {'hi':>10}  {'count':>10}  {'ok?':>6}")
        all_ok = True
        for binnum, lo, hi, count in verified:
            ok = "OK" if count >= MIN_COUNTS else "LOW !"
            if count < MIN_COUNTS:
                all_ok = False
            print(f"  {binnum:>4}  {lo:>10.3f}  {hi:>10.3f}  {count:>10.2f}  {ok:>6}")

        if all_ok:
            print(f"\n  All bins >= {MIN_COUNTS} counts. ✓")
        else:
            print(f"\n  WARNING: some bins still below {MIN_COUNTS} counts!")

        # Format edges nicely (round to 4 decimal places)
        edges_rounded = [round(e, 4) for e in new_edges]
        yaml_output[varname] = edges_rounded

        print(f"\n  yaml bin edges:")
        print(f"  {edges_rounded}")

    # ── Print full yaml block ready to copy-paste ─────────────────────────────
    print(f"\n\n{'='*60}")
    print("YAML OUTPUT — copy-paste into your bin config:")
    print(f"{'='*60}\n")

    for varname, edges in yaml_output.items():
        short = varname.replace("numuCC1piNpReco_", "")
        edges_str = ", ".join(str(e) for e in edges)
        print(f"        {varname}:")
        print(f"          formula: {varname}")
        print(f"          binedges: [{edges_str}]")
        print(f"          apply_to_datasets: ['run1_bnb_nu_overlay_mcc9_v28_wctagger']")
        print(f"          criteria: []")
        print()

    xfile.Close()
    print("Done.")