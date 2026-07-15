import os, sys
import numpy as np
import ROOT as rt
from scipy import stats

# ── File paths ────────────────────────────────────────────────────────────────
DATA_FILE   = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki/output_master_tki_run1/run1_data_bnb5e19_20260227_171123.root"
COVAR_FILE  = "output_covariance.root"   # output of make_covar_matrices.py
XSECFLUX_FILE = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/systematics_output_run1_march2026_contained/output_xsecflux_tki_run1_march2026_contained.root"

SAMPLE = "run1_bnb_nu_overlay_mcc9_v28_wctagger"

# ── Bin configuration (must match what was used to make the covariance matrices)
BIN_CONFIG = {
    "numuCC1piNpReco_delAlphaT":   {"nbins": 10,  "lo": 0.0,    "hi": 180.0},
    "numuCC1piNpReco_pN":          {"nbins": 25,  "lo": 0.0,    "hi": 1.6},
    "numuCC1piNpReco_delPTT":      {"nbins": 25,  "lo": -1.0,   "hi": 1.0},
    "numuCC1piNpReco_muKE":        {"nbins": 25,  "lo": 0.0,    "hi": 1500.0},
    "numuCC1piNpReco_pionKE":      {"nbins": 25,  "lo": 0.0,    "hi": 500.0},
    "numuCC1piNpReco_maxprotonKE": {"nbins": 25,  "lo": 0.0,    "hi": 500.0},
}

# ── Selection cuts applied to the data TTree ─────────────────────────────────
# Require reconstructed 1mu1piNp topology + all 3 particles contained
SELECTION = (
    "numuCC1piNpReco_is_target_1mu1piNproton == 1 && "
    "numuCC1piNpReco_event_is_contained == 1"
)

# ─────────────────────────────────────────────────────────────────────────────
def fill_data_histograms(data_rootfile, bin_config, selection):
    """
    Fill one TH1D per variable from the data TTree using TTree::Draw.
    Returns dict: varname -> TH1D
    """
    tree = data_rootfile.Get("analysis_tree")
    if not tree:
        raise RuntimeError("Could not find 'analysis_tree' in data file.")

    data_hists = {}
    for var, cfg in bin_config.items():
        hname = f"hdata_{var}"
        h = rt.TH1D(hname, f"Data: {var}", cfg["nbins"], cfg["lo"], cfg["hi"])
        h.Sumw2()
        # Draw with selection cut into our histogram
        tree.Draw(f"{var}>>{hname}", selection, "goff")
        h.SetDirectory(0)   # detach from ROOT's global ownership
        data_hists[var] = h
        print(f"  {var}: {h.GetEntries():.0f} data events selected")

    return data_hists


# ─────────────────────────────────────────────────────────────────────────────
def load_cv_histograms(xsecflux_rootfile, bin_config, sample):
    """
    Load the MC central-value histograms from the xsecflux file.
    Naming: h{varname}_{sample}_cv
    """
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
    """
    Load the total absolute covariance matrix for a variable.
    Returns a numpy array (nbins x nbins).
    """
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
def compute_chi2(variable, data_hist, cv_hist, V_xsecflux):
    """
    Compute chi2 for one variable.

    Total covariance = V_xsecflux + V_stat
    V_stat is diagonal: data stat (Poisson) + MC stat (from CV bin error)

    Returns (chi2, ndof, pvalue)
    """
    nbins = V_xsecflux.shape[0]

    # ── Build data and MC vectors ─────────────────────────────────────────
    data = np.array([data_hist.GetBinContent(i+1) for i in range(nbins)])
    mc   = np.array([cv_hist.GetBinContent(i+1)   for i in range(nbins)])
    # MC stat uncertainty from Sumw2 stored in CV histogram bin errors
    mc_err = np.array([cv_hist.GetBinError(i+1)   for i in range(nbins)])

    # ── Build total covariance matrix ─────────────────────────────────────
    V_total = V_xsecflux.copy()
    for i in range(nbins):
        V_total[i, i] += data[i]           # data Poisson stat: sigma^2 = N
        V_total[i, i] += mc_err[i]**2      # MC stat from bin error

    # ── Mask out empty bins (no MC prediction) ────────────────────────────
    mask = mc > 0
    n_active = np.sum(mask)
    if n_active == 0:
        print(f"  [{variable}] ERROR: no active bins — skipping.")
        return None, None, None

    data_m = data[mask]
    mc_m   = mc[mask]
    V_m    = V_total[np.ix_(mask, mask)]

    # ── Check condition number ────────────────────────────────────────────
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
    ndof   = int(n_active)          # no free parameters fitted
    pvalue = stats.chi2.sf(chi2, ndof)

    return chi2, ndof, pvalue


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n=== Opening files ===")
    rdata    = rt.TFile(DATA_FILE)
    rxsec    = rt.TFile(XSECFLUX_FILE)
    rcovar   = rt.TFile(COVAR_FILE)

    for f, name in [(rdata, DATA_FILE), (rxsec, XSECFLUX_FILE), (rcovar, COVAR_FILE)]:
        if not f or f.IsZombie():
            print(f"ERROR: could not open {name}")
            sys.exit(1)

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

        V = load_covariance_matrix(rcovar, var)
        chi2, ndof, pval = compute_chi2(var, data_hists[var], cv_hists[var], V)

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

    rdata.Close()
    rxsec.Close()
    rcovar.Close()