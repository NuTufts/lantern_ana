"""
rebin_xsecflux.py
-----------------
Rebins an xsecflux ROOT file's universe histograms to new adaptive bin edges,
writing a new ROOT file that make_covar_matrices.py can consume unchanged.
 
Only variables that actually need rebinning are touched; all others are copied
as-is.  The rebinning is done by summing universe histogram contents over the
original bins that fall inside each new merged bin — correct for event counts.
For the CV and N histograms the same summation applies.
For the mean histogram, a weighted mean is computed (weighted by CV counts).
For the variance histogram, a weighted variance is computed:
  sigma^2_merged = sum(sigma_k^2 * N_k^2) / (sum N_k)^2
 
Usage:
    python3 rebin_xsecflux.py <input_xsecflux.root> [output.root]
 
Output defaults to:  input_xsecflux_rebinned.root
"""
 
import os
import sys
import array
import ROOT as rt
 
rt.gROOT.SetBatch(True)
 
# ── New bin edges for variables that need merging ─────────────────────────────
# delAlphaT is already fine — not listed here, will be copied unchanged.
 
NEW_EDGES = {
    "numuCC1piNpReco_pN": [
        0.0, 0.064, 0.128, 0.192, 0.256, 0.32, 0.384, 0.448, 0.512,
        0.576, 0.64, 0.704, 0.768, 0.832, 0.96, 1.024, 1.6
    ],
    "numuCC1piNpReco_delPTT": [
        -1.0, -0.44, -0.36, -0.28, -0.2, -0.12, -0.04,
        0.04, 0.12, 0.2, 0.28, 0.36, 0.44, 0.52, 1.0
    ],
    "numuCC1piNpReco_muKE": [
        0.0, 60.0, 120.0, 180.0, 240.0, 300.0, 360.0, 420.0, 480.0,
        540.0, 600.0, 660.0, 720.0, 780.0, 840.0, 900.0, 960.0,
        1200.0, 1500.0
    ],
    "numuCC1piNpReco_pionKE": [
        0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0,
        180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 500.0
    ],
    "numuCC1piNpReco_maxprotonKE": [
        0.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0,
        220.0, 240.0, 260.0, 280.0, 300.0, 320.0, 340.0, 360.0,
        380.0, 400.0, 500.0
    ],
}
 
 
# ── Helpers ───────────────────────────────────────────────────────────────────
 
def make_bin_map(old_hist, new_edges):
    """
    Return a list of length len(new_edges)-1.
    Each element is a list of 1-based OLD bin indices that fall inside that
    new bin.  Uses bin-centre matching so floating-point edge fuzz is handled.
    """
    n_new = len(new_edges) - 1
    mapping = [[] for _ in range(n_new)]
    n_old = old_hist.GetNbinsX()
    for old_bin in range(1, n_old + 1):
        centre = old_hist.GetXaxis().GetBinCenter(old_bin)
        for new_bin in range(n_new):
            lo = new_edges[new_bin]
            hi = new_edges[new_bin + 1]
            if lo <= centre < hi:
                mapping[new_bin].append(old_bin)
                break
        else:
            # catch the very last edge (centre == hi of last bin)
            if abs(centre - new_edges[-1]) < 1e-9:
                mapping[-1].append(old_bin)
    return mapping
 
 
def rebin_1d(old_hist, new_edges, new_name, bin_map, mode="sum", cv_hist=None):
    """
    Rebin a 1D histogram.
 
    mode:
      "sum"               - sum bin contents (CV, N, badweights)
      "weighted_mean"     - weighted mean, weights from cv_hist (mean histograms)
      "weighted_variance" - weighted variance: sum(sigma_k^2 * N_k^2) / (sum N_k)^2
                            requires cv_hist for the N_k weights
    """
    n_new  = len(new_edges) - 1
    edges  = array.array('d', new_edges)
    h_new  = rt.TH1D(new_name, old_hist.GetTitle(), n_new, edges)
    h_new.SetDirectory(0)
 
    for new_bin, old_bins in enumerate(bin_map, start=1):
        if not old_bins:
            h_new.SetBinContent(new_bin, 0.0)
            continue
 
        if mode == "sum":
            total = sum(old_hist.GetBinContent(b) for b in old_bins)
            h_new.SetBinContent(new_bin, total)
 
        elif mode == "weighted_mean":
            # weighted average: sum(w_i * mean_i) / sum(w_i)
            # weights = CV counts in the old bin
            weights = [cv_hist.GetBinContent(b) for b in old_bins]
            values  = [old_hist.GetBinContent(b) for b in old_bins]
            w_total = sum(weights)
            if w_total > 0:
                wmean = sum(w * v for w, v in zip(weights, values)) / w_total
            else:
                wmean = 0.0
            h_new.SetBinContent(new_bin, wmean)

        elif mode == "weighted_variance":
            # sigma^2_merged = sum(sigma_k^2 * N_k^2) / (sum N_k)^2
            # This correctly propagates variances when merging bins with
            # different CV counts.
            weights  = [cv_hist.GetBinContent(b) for b in old_bins]
            values   = [old_hist.GetBinContent(b) for b in old_bins]
            w_total  = sum(weights)
            if w_total > 0:
                merged_var = sum(v * w**2 for v, w in zip(values, weights)) / (w_total**2)
            else:
                merged_var = 0.0
            h_new.SetBinContent(new_bin, merged_var)
 
    return h_new
 
 
def rebin_2d_universe(old_hist, new_edges, new_name, bin_map):
    """
    Rebin a 2D universe histogram (x=bins, y=universes) by summing x-bins.
    The universe axis is kept unchanged.
    """
    n_new    = len(new_edges) - 1
    n_univs  = old_hist.GetYaxis().GetNbins()
    edges    = array.array('d', new_edges)
 
    h_new = rt.TH2D(new_name, old_hist.GetTitle(),
                    n_new, edges,
                    n_univs, 0, n_univs)
    h_new.SetDirectory(0)
 
    for new_bin, old_bins in enumerate(bin_map, start=1):
        for univ in range(1, n_univs + 1):
            total = sum(old_hist.GetBinContent(b, univ) for b in old_bins)
            h_new.SetBinContent(new_bin, univ, total)
 
    return h_new
 
 
# ── Main ──────────────────────────────────────────────────────────────────────
 
def rebin_xsecflux(input_path, output_path):
    rin = rt.TFile(input_path, "READ")
    if not rin or rin.IsZombie():
        print(f"ERROR: cannot open {input_path}")
        sys.exit(1)
 
    rout = rt.TFile(output_path, "RECREATE")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}\n")
 
    keys = rin.GetListOfKeys()
 
    # We need CV hists available for weighted rebinning of mean and variance hists.
    # Load them first in a pre-pass.
    cv_hists = {}
    for ikey in range(keys.GetEntries()):
        histname = str(keys.At(ikey)).split(" ")[1].strip()
        if histname.endswith("_cv") and "__" not in histname:
            h = rin.Get(histname)
            if h:
                h.SetDirectory(0)
                cv_hists[histname] = h
 
    # ── Main pass: copy or rebin every histogram ──────────────────────────────
    bin_maps = {}   # cache bin maps keyed by varname
 
    for ikey in range(keys.GetEntries()):
        raw_key  = str(keys.At(ikey)).split(" ")[1].strip()
        histname = raw_key
 
        h_old = rin.Get(histname)
        if not h_old:
            print(f"  SKIP (could not Get): {histname}")
            continue
 
        # ── Determine which variable this histogram belongs to ────────────────
        matched_var = None
        for var in NEW_EDGES:
            if histname.startswith("h" + var):
                matched_var = var
                break
 
        if matched_var is None:
            # No rebinning needed — just copy
            rout.cd()
            h_clone = h_old.Clone(histname)
            h_clone.SetDirectory(rout)
            h_clone.Write()
            print(f"  COPY  {histname}")
            continue
 
        # ── Build bin map for this variable (cached) ──────────────────────────
        if matched_var not in bin_maps:
            bin_maps[matched_var] = make_bin_map(h_old, NEW_EDGES[matched_var])
 
        bmap      = bin_maps[matched_var]
        new_edges = NEW_EDGES[matched_var]

        # Get the CV hist for this variable/sample (needed for mean + variance)
        parts  = histname.split("__")
        cv_h   = None
        if len(parts) == 3:
            sample = parts[1]
            cv_key = f"h{matched_var}_{sample}_cv"
            cv_h   = cv_hists.get(cv_key, None)
 
        rout.cd()
 
        # ── Dispatch by histogram dimensionality and type ─────────────────────
        is_2d = h_old.IsA().InheritsFrom("TH2")
 
        if is_2d:
            h_new = rebin_2d_universe(h_old, new_edges, histname, bmap)
            print(f"  REBIN2D {histname}  "
                  f"({h_old.GetNbinsX()} → {h_new.GetNbinsX()} x-bins, "
                  f"{h_old.GetNbinsY()} universes)")
        else:
            if histname.endswith("_mean"):
                if cv_h is None:
                    print(f"  WARNING: no CV hist for mean rebin of {histname}, "
                          f"falling back to simple sum")
                    h_new = rebin_1d(h_old, new_edges, histname, bmap, mode="sum")
                else:
                    h_new = rebin_1d(h_old, new_edges, histname, bmap,
                                     mode="weighted_mean", cv_hist=cv_h)
                print(f"  REBIN1D(mean)     {histname}  "
                      f"({h_old.GetNbinsX()} → {h_new.GetNbinsX()} bins)")

            elif histname.endswith("_variance"):
                if cv_h is None:
                    print(f"  WARNING: no CV hist for variance rebin of {histname}, "
                          f"falling back to simple sum")
                    h_new = rebin_1d(h_old, new_edges, histname, bmap, mode="sum")
                else:
                    h_new = rebin_1d(h_old, new_edges, histname, bmap,
                                     mode="weighted_variance", cv_hist=cv_h)
                print(f"  REBIN1D(variance) {histname}  "
                      f"({h_old.GetNbinsX()} → {h_new.GetNbinsX()} bins)")

            else:
                # sum mode: CV, N, badweights
                h_new = rebin_1d(h_old, new_edges, histname, bmap, mode="sum")
                print(f"  REBIN1D(sum)      {histname}  "
                      f"({h_old.GetNbinsX()} → {h_new.GetNbinsX()} bins)")
 
        h_new.SetDirectory(rout)
        h_new.Write()
 
    rout.Close()
    rin.Close()
    print(f"\nDone. Rebinned file written to: {output_path}")
 
 
# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("usage: python3 rebin_xsecflux.py <input_xsecflux.root> [output.root]")
        sys.exit(0)
 
    input_path  = sys.argv[1]
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        base        = os.path.splitext(input_path)[0]
        output_path = base + "_rebinned.root"
 
    rebin_xsecflux(input_path, output_path)