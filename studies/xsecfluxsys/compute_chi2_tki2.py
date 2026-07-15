import os, sys
import numpy as np
import ROOT as rt
from scipy import stats

# ── File paths ────────────────────────────────────────────────────────────────
LANTERN_DIR   = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana"
DATA_FILE     = f"{LANTERN_DIR}/studies/numu_cc_tki/output_master_tki_run1/run1_data_bnb5e19_20260227_171123.root"
COVAR_FILE    = "output_covariance.root"   # output of make_covar_matrices.py
XSECFLUX_FILE = f"{LANTERN_DIR}/studies/xsecfluxsys/systematics_output_run1_march2026_contained/output_xsecflux_tki_run1_march2026_contained_rebinned.root"

# Detector systematics files (Run 3, used for Run 1 as well)
DETSYS_FILES = [
    f"{LANTERN_DIR}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_contained.root",
    f"{LANTERN_DIR}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV_contained.root",
]
DETSYS_PARAMS = [
    "wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ",
    "LYAtt", "LYDown", "LYRayleigh",
    "recomb2", "SCE",
]

SAMPLE = "run1_bnb_nu_overlay_mcc9_v28_wctagger"

# ── Bin configuration (must match what was used to make the covariance matrices)
# For non-uniform bins, use "edges" key with a list of bin edges.
# For uniform bins, use "nbins"/"lo"/"hi".
BIN_CONFIG = {
    "numuCC1piNpReco_delAlphaT":   {"nbins": 10, "lo": 0.0, "hi": 180.0},
    "numuCC1piNpReco_pN":          {"edges": [0.0, 0.064, 0.128, 0.192, 0.256, 0.32, 0.384, 0.448, 0.512, 0.576, 0.64, 0.704, 0.768, 0.832, 0.96, 1.024, 1.6]},
    "numuCC1piNpReco_delPTT":      {"edges": [-1.0, -0.44, -0.36, -0.28, -0.2, -0.12, -0.04, 0.04, 0.12, 0.2, 0.28, 0.36, 0.44, 0.52, 1.0]},
    "numuCC1piNpReco_muKE":        {"edges": [0.0, 60.0, 120.0, 180.0, 240.0, 300.0, 360.0, 420.0, 480.0, 540.0, 600.0, 660.0, 720.0, 780.0, 840.0, 900.0, 960.0, 1200.0, 1380.0, 1500.0]},
    "numuCC1piNpReco_pionKE":      {"edges": [0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 500.0]},
    "numuCC1piNpReco_maxprotonKE": {"edges": [0.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 300.0, 320.0, 340.0, 360.0, 380.0, 400.0, 500.0]},
}

# ── Selection cuts applied to the data TTree ─────────────────────────────────
SELECTION = (
    "numuCC1piNpReco_is_target_1mu1piNproton == 1 && "
    "numuCC1piNpReco_event_is_contained == 1"
)


# ─────────────────────────────────────────────────────────────────────────────
def fill_data_histograms(data_rootfile, bin_config, selection):
    """Fill one TH1D per variable from the data TTree."""
    tree = data_rootfile.Get("analysis_tree")
    if not tree:
        raise RuntimeError("Could not find 'analysis_tree' in data file.")

    data_hists = {}
    for var, cfg in bin_config.items():
        hname = f"hdata_{var}"
        if "edges" in cfg:
            edges_arr = np.array(cfg["edges"], dtype=float)
            h = rt.TH1D(hname, f"Data: {var}", len(edges_arr)-1, edges_arr)
        else:
            h = rt.TH1D(hname, f"Data: {var}", cfg["nbins"], cfg["lo"], cfg["hi"])
        h.Sumw2()
        tree.Draw(f"{var}>>{hname}", selection, "goff")
        h.SetDirectory(0)
        data_hists[var] = h
        print(f"  {var}: {h.GetEntries():.0f} data events selected")

    return data_hists


# ─────────────────────────────────────────────────────────────────────────────
def load_cv_histograms(xsecflux_rootfile, bin_config, sample):
    """Load MC central-value histograms from the xsecflux file."""
    cv_hists = {}
    for var in bin_config:
        hname = f"h{var}_{sample}_cv"
        h = xsecflux_rootfile.Get(hname)
        if not h:
            print(f"  WARNING: CV hist not found: {hname}")
            continue
        h.SetDirectory(0)
        cv_hists[var] = h
        print(f"  {var}: CV integral = {h.Integral():.1f}")
    return cv_hists


# ─────────────────────────────────────────────────────────────────────────────
def load_covariance_matrix(covar_rootfile, variable):
    """Load the total absolute xsecflux covariance matrix for a variable."""
    hname = f"hcovar_total_{variable}"
    h = covar_rootfile.Get(hname)
    if not h:
        raise RuntimeError(f"Could not find covariance matrix: {hname}")
    nbins = h.GetNbinsX()
    V = np.zeros((nbins, nbins))
    for i in range(nbins):
        for j in range(nbins):
            V[i, j] = h.GetBinContent(i+1, j+1)
    return V


# ─────────────────────────────────────────────────────────────────────────────
def load_detector_frac_unc(detsys_files, variable, cv_hist, bin_config):
    """
    Compute per-bin fractional detector uncertainty by summing in quadrature
    the fractional difference (var - cv) / cv for each detector parameter.

    The detsys files use the original uniform binning. For merged analysis bins
    (adaptive rebinning), we sum __cv and __var counts across all original bins
    that fall inside the merged bin before computing the fractional difference.
    This is the correct treatment — no _variance histograms used.

    Fractional difference for merged bin i, parameter p:
        f_i^p = (sum_k x_k^var - sum_k x_k^cv) / sum_k x_k^cv
    where k runs over all original detsys bins inside merged analysis bin i.

    Returns a numpy array of fractional uncertainties, one per bin.
    """
    nbins  = cv_hist.GetNbinsX()
    short  = variable.replace("numuCC1piNpReco_", "")
    frac_var = np.zeros(nbins)

    n_loaded = 0
    for param in DETSYS_PARAMS:
        for rfile in detsys_files:
            hcv_det  = rfile.Get(f"hnumuCC1piNpReco_{short}__{param}__cv")
            hvar_det = rfile.Get(f"hnumuCC1piNpReco_{short}__{param}__var")
            if not hcv_det or hcv_det.IsZombie() or \
               not hvar_det or hvar_det.IsZombie():
                continue
            n_loaded += 1

            n_det_bins = hcv_det.GetNbinsX()

            for ibin in range(1, nbins + 1):
                # Get the edges of this analysis bin
                lo = cv_hist.GetXaxis().GetBinLowEdge(ibin)
                hi = cv_hist.GetXaxis().GetBinUpEdge(ibin)

                # Sum __cv and __var over all original detsys bins
                # whose centres fall inside [lo, hi)
                sum_cv  = 0.0
                sum_var = 0.0
                for det_bin in range(1, n_det_bins + 1):
                    centre = hcv_det.GetXaxis().GetBinCenter(det_bin)
                    if lo <= centre < hi:
                        sum_cv  += hcv_det.GetBinContent(det_bin)
                        sum_var += hvar_det.GetBinContent(det_bin)

                if sum_cv > 0:
                    frac_diff = (sum_var - sum_cv) / sum_cv
                    frac_var[ibin-1] += frac_diff**2

            break   # found this param in this file, move on

    print(f"  [{short}] detector: loaded {n_loaded}/{len(DETSYS_PARAMS)} parameters")
    return np.sqrt(frac_var)   # fractional uncertainty per bin


# ─────────────────────────────────────────────────────────────────────────────
def compute_chi2(variable, data_hist, cv_hist, V_xsecflux, det_frac_unc):
    """
    Compute chi2 for one variable.

    Total covariance = V_xsecflux + V_stat + V_det
    where V_stat and V_det are diagonal only:
      V_stat[i,i] = N_data[i] + (sigma_MC[i])^2
      V_det[i,i]  = (f_det[i] * mu_i)^2

    Returns (chi2, ndof, pvalue)
    """
    nbins = V_xsecflux.shape[0]

    data   = np.array([data_hist.GetBinContent(i+1) for i in range(nbins)])
    mc     = np.array([cv_hist.GetBinContent(i+1)   for i in range(nbins)])
    mc_err = np.array([cv_hist.GetBinError(i+1)     for i in range(nbins)])

    # ── Build total covariance matrix ─────────────────────────────────────
    V_total = V_xsecflux.copy()
    for i in range(nbins):
        V_total[i, i] += data[i]                        # data Poisson stat
        V_total[i, i] += mc_err[i]**2                   # MC stat
        V_total[i, i] += (det_frac_unc[i] * mc[i])**2  # detector systematic

    # ── Mask out empty bins ────────────────────────────────────────────────
    mask     = mc > 0
    n_active = int(np.sum(mask))
    if n_active == 0:
        print(f"  [{variable}] ERROR: no active bins — skipping.")
        return None, None, None

    data_m = data[mask]
    mc_m   = mc[mask]
    V_m    = V_total[np.ix_(mask, mask)]

    # ── Check condition number ─────────────────────────────────────────────
    cond = np.linalg.cond(V_m)
    print(f"  [{variable}] condition number: {cond:.2e}")
    if cond > 1e10:
        print(f"  [{variable}] WARNING: ill-conditioned — using pseudoinverse")
        V_inv = np.linalg.pinv(V_m)
    else:
        V_inv = np.linalg.inv(V_m)

    # ── Chi2 ──────────────────────────────────────────────────────────────
    delta  = data_m - mc_m
    chi2   = float(delta @ V_inv @ delta)
    ndof   = n_active
    pvalue = stats.chi2.sf(chi2, ndof)

    return chi2, ndof, pvalue


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n=== Opening files ===")
    rdata  = rt.TFile(DATA_FILE)
    rxsec  = rt.TFile(XSECFLUX_FILE)
    rcovar = rt.TFile(COVAR_FILE)

    for f, name in [(rdata, DATA_FILE), (rxsec, XSECFLUX_FILE), (rcovar, COVAR_FILE)]:
        if not f or f.IsZombie():
            print(f"ERROR: could not open {name}")
            sys.exit(1)

    # Open detector systematics files
    rdetsys = []
    for path in DETSYS_FILES:
        rf = rt.TFile(path)
        if not rf or rf.IsZombie():
            print(f"WARNING: could not open detsys file: {path}")
        else:
            rdetsys.append(rf)
            print(f"  Opened detsys: {path}")

    print("\n=== Filling data histograms from TTree ===")
    data_hists = fill_data_histograms(rdata, BIN_CONFIG, SELECTION)

    print("\n=== Loading MC CV histograms ===")
    cv_hists = load_cv_histograms(rxsec, BIN_CONFIG, SAMPLE)

    print("\n=== Computing chi2 ===\n")
    results = {}
    for var in BIN_CONFIG:
        if var not in data_hists:
            print(f"  [{var}] skipping — no data histogram")
            continue
        if var not in cv_hists:
            print(f"  [{var}] skipping — no CV histogram")
            continue

        V            = load_covariance_matrix(rcovar, var)
        det_frac_unc = load_detector_frac_unc(rdetsys, var, cv_hists[var], BIN_CONFIG)
        chi2, ndof, pval = compute_chi2(var, data_hists[var], cv_hists[var],
                                        V, det_frac_unc)

        if chi2 is not None:
            results[var] = {"chi2": chi2, "ndof": ndof, "pvalue": pval}

    # ── Summary table ─────────────────────────────────────────────────────
    print("\n" + "="*65)
    print(f"{'Variable':<35} {'chi2':>8} {'ndof':>6} {'chi2/ndof':>10} {'p-value':>10}")
    print("="*65)
    for var, r in results.items():
        shortname = var.replace("numuCC1piNpReco_", "")
        print(f"{shortname:<35} {r['chi2']:>8.2f} {r['ndof']:>6d} "
              f"{r['chi2']/r['ndof']:>10.2f} {r['pvalue']:>10.4f}")
    print("="*65)
    print("\nNote: V_total = V_xsecflux + V_stat + V_det (diagonal)")

    rdata.Close()
    rxsec.Close()
    rcovar.Close()
    for rf in rdetsys:
        rf.Close()