import os, sys
import argparse
import numpy as np
import ROOT as rt
from scipy import stats

LANTERN_DIR = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana"

# ── Run configurations ────────────────────────────────────────────────────────
RUN_CONFIGS = {
    (1, True): {
        "xsecflux": f"{LANTERN_DIR}/studies/xsecfluxsys/systematics_output_run1_march2026_contained/output_xsecflux_tki_run1_march2026_contained_rebinned_100count.root",
        "sample":   "run1_bnb_nu_overlay_mcc9_v28_wctagger",
        "data":     f"{LANTERN_DIR}/studies/numu_cc_tki/output_master_tki_run1/run1_data_bnb5e19_20260227_171123.root",
        "covar":    "output_covariance_run1_contained_100count.root",
        "detsys":   [
            f"{LANTERN_DIR}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_contained.root",
            f"{LANTERN_DIR}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV_contained.root",
        ],
        "selection": "numuCC1piNpReco_is_target_1mu1piNproton==1 && numuCC1piNpReco_event_is_contained==2",
        "label":    "Run 1 Contained",
    },
    (1, False): {
        "xsecflux": f"{LANTERN_DIR}/studies/xsecfluxsys/systematics_output_run1_march2026_uncontained/output_xsecflux_tki_run1_march2026_uncontained_rebinned_100count.root",
        "sample":   "run1_bnb_nu_overlay_mcc9_v28_wctagger",
        "data":     f"{LANTERN_DIR}/studies/numu_cc_tki/output_master_tki_run1/run1_data_bnb5e19_20260227_171123.root",
        "covar":    "output_covariance_run1_uncontained_100count.root",
        "detsys":   [
            f"{LANTERN_DIR}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_uncontained.root",
            f"{LANTERN_DIR}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV_uncontained.root",
        ],
        "selection": "numuCC1piNpReco_is_target_1mu1piNproton==1",
        "label":    "Run 1 Uncontained",
    },
    (3, True): {
        "xsecflux": f"{LANTERN_DIR}/studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux_contained/output_xsecflux_tki_run3b_1mil_contained_rebinned_100count.root",
        "sample":   "mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil",
        "data":     f"{LANTERN_DIR}/studies/numu_cc_tki/output_split_tki_run3/run3_data_bnb1e19_20260308_175632.root",
        "covar":    "output_covariance_run3_contained_100count.root",
        "detsys":   [
            f"{LANTERN_DIR}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_contained.root",
            f"{LANTERN_DIR}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV_contained.root",
        ],
        "selection": "numuCC1piNpReco_is_target_1mu1piNproton==1 && numuCC1piNpReco_event_is_contained==2",
        "label":    "Run 3 Contained",
    },
    (3, False): {
        "xsecflux": f"{LANTERN_DIR}/studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux_uncontained/output_xsecflux_tki_run3b_1mil_uncontained_rebinned_100count.root",
        "sample":   "mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil",
        "data":     f"{LANTERN_DIR}/studies/numu_cc_tki/output_split_tki_run3/run3_data_bnb1e19_20260308_175632.root",
        "covar":    "output_covariance_run3_uncontained_100count.root",
        "detsys":   [
            f"{LANTERN_DIR}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_uncontained.root",
            f"{LANTERN_DIR}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV_uncontained.root",
        ],
        "selection": "numuCC1piNpReco_is_target_1mu1piNproton==1",
        "label":    "Run 3 Uncontained",
    },
}

# ── Final bin edges (Run 3 Contained, >=100 raw MC counts per bin) ───────────
BIN_CONFIG = {
    "numuCC1piNpReco_delAlphaT":   {"edges": [0.0, 18.0, 36.0, 54.0, 72.0, 90.0, 108.0, 126.0, 144.0, 162.0, 180.0]},
    "numuCC1piNpReco_pN":          {"edges": [0.0, 0.128, 0.192, 0.256, 0.32, 0.384, 0.448, 0.512, 0.576, 0.64, 0.768, 1.6]},
    "numuCC1piNpReco_delPTT":      {"edges": [-1.0, -0.36, -0.28, -0.2, -0.12, -0.04, 0.04, 0.12, 0.2, 0.28, 0.36, 1.0]},
    "numuCC1piNpReco_muKE":        {"edges": [0.0, 60.0, 120.0, 180.0, 240.0, 300.0, 360.0, 420.0, 480.0, 540.0, 660.0, 1500.0]},
    "numuCC1piNpReco_pionKE":      {"edges": [0.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 220.0, 260.0, 500.0]},
    "numuCC1piNpReco_maxprotonKE": {"edges": [0.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 320.0, 360.0, 500.0]},
}

DETSYS_PARAMS = [
    "wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ",
    "LYAtt", "LYDown", "LYRayleigh",
    "recomb2", "SCE",
]


# ─────────────────────────────────────────────────────────────────────────────
def fill_data_histograms(data_rootfile, bin_config, selection):
    tree = data_rootfile.Get("analysis_tree")
    if not tree:
        raise RuntimeError("Could not find 'analysis_tree' in data file.")
    data_hists = {}
    for var, cfg in bin_config.items():
        hname     = f"hdata_{var}"
        edges_arr = np.array(cfg["edges"], dtype=float)
        h         = rt.TH1D(hname, f"Data: {var}", len(edges_arr)-1, edges_arr)
        h.Sumw2()
        tree.Draw(f"{var}>>{hname}", selection, "goff")
        h.SetDirectory(0)
        data_hists[var] = h
        print(f"  {var}: {h.GetEntries():.0f} data events selected")
    return data_hists


def load_cv_histograms(xsecflux_rootfile, bin_config, sample):
    cv_hists = {}
    for var in bin_config:
        hname = f"h{var}_{sample}_cv"
        h     = xsecflux_rootfile.Get(hname)
        if not h:
            print(f"  WARNING: CV hist not found: {hname}")
            continue
        h.SetDirectory(0)
        cv_hists[var] = h
        print(f"  {var}: CV integral = {h.Integral():.1f}")
    return cv_hists


def load_covariance_matrix(covar_rootfile, variable):
    hname = f"hcovar_total_{variable}"
    h     = covar_rootfile.Get(hname)
    if not h:
        raise RuntimeError(f"Could not find covariance matrix: {hname}")
    nbins = h.GetNbinsX()
    V     = np.zeros((nbins, nbins))
    for i in range(nbins):
        for j in range(nbins):
            V[i, j] = h.GetBinContent(i+1, j+1)
    return V


def load_detector_abs_unc(detsys_files, variable, cv_hist):
    """
    Absolute detector uncertainty per bin, summed in quadrature over parameters.
    For each parameter p and merged analysis bin i:
      sigma_i^(p) = sum_k x_k^var - sum_k x_k^cv
    where k runs over original detsys bins inside analysis bin i.
    Returns sqrt(sum_p sigma_i^(p)^2) in absolute event counts.
    """
    nbins    = cv_hist.GetNbinsX()
    short    = variable.replace("numuCC1piNpReco_", "")
    abs_var  = np.zeros(nbins)
    n_loaded = 0

    for param in DETSYS_PARAMS:
        for rfile in detsys_files:
            hcv_det  = rfile.Get(f"hnumuCC1piNpReco_{short}__{param}__cv")
            hvar_det = rfile.Get(f"hnumuCC1piNpReco_{short}__{param}__var")
            if not hcv_det or hcv_det.IsZombie() or \
               not hvar_det or hvar_det.IsZombie():
                continue
            n_loaded    += 1
            n_det_bins   = hcv_det.GetNbinsX()
            for ibin in range(1, nbins + 1):
                lo      = cv_hist.GetXaxis().GetBinLowEdge(ibin)
                hi      = cv_hist.GetXaxis().GetBinUpEdge(ibin)
                sum_cv  = sum(hcv_det.GetBinContent(b)  for b in range(1, n_det_bins+1)
                              if lo <= hcv_det.GetXaxis().GetBinCenter(b) < hi)
                sum_var = sum(hvar_det.GetBinContent(b) for b in range(1, n_det_bins+1)
                              if lo <= hcv_det.GetXaxis().GetBinCenter(b) < hi)
                abs_var[ibin-1] += (sum_var - sum_cv)**2
            break

    print(f"  [{short}] detector: loaded {n_loaded}/{len(DETSYS_PARAMS)} parameters")
    return np.sqrt(abs_var)


def compute_chi2(variable, data_hist, cv_hist, V_xsecflux, det_abs_unc):
    """
    chi2 = delta^T V_total^-1 delta
    V_total_ii = V_xsecflux_ii + N_data_i + (sigma_MC_i)^2 + (sigma_det_i)^2
    """
    nbins  = V_xsecflux.shape[0]
    data   = np.array([data_hist.GetBinContent(i+1) for i in range(nbins)])
    mc     = np.array([cv_hist.GetBinContent(i+1)   for i in range(nbins)])
    mc_err = np.array([cv_hist.GetBinError(i+1)     for i in range(nbins)])

    V_total = V_xsecflux.copy()
    for i in range(nbins):
        V_total[i, i] += data[i]
        V_total[i, i] += mc_err[i]**2
        V_total[i, i] += det_abs_unc[i]**2

    mask     = mc > 0
    n_active = int(np.sum(mask))
    if n_active == 0:
        print(f"  [{variable}] ERROR: no active bins.")
        return None, None, None

    data_m = data[mask]
    mc_m   = mc[mask]
    V_m    = V_total[np.ix_(mask, mask)]

    cond = np.linalg.cond(V_m)
    print(f"  [{variable}] condition number: {cond:.2e}")
    V_inv = np.linalg.pinv(V_m) if cond > 1e10 else np.linalg.inv(V_m)

    delta  = data_m - mc_m
    chi2   = float(delta @ V_inv @ delta)
    pvalue = stats.chi2.sf(chi2, n_active)
    return chi2, n_active, pvalue


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=int, choices=[1, 3], required=True)
    parser.add_argument("--contained",   dest="contained", action="store_true",  default=True)
    parser.add_argument("--uncontained", dest="contained", action="store_false")
    args = parser.parse_args()

    key = (args.run, args.contained)
    cfg = RUN_CONFIGS[key]
    print(f"\n=== {cfg['label']} ===")

    rdata  = rt.TFile(cfg["data"])
    rxsec  = rt.TFile(cfg["xsecflux"])
    rcovar = rt.TFile(cfg["covar"])
    for f, name in [(rdata, cfg["data"]), (rxsec, cfg["xsecflux"]), (rcovar, cfg["covar"])]:
        if not f or f.IsZombie():
            print(f"ERROR: could not open {name}")
            sys.exit(1)

    rdetsys = []
    for path in cfg["detsys"]:
        rf = rt.TFile(path)
        if rf and not rf.IsZombie():
            rdetsys.append(rf)
            print(f"  Opened detsys: {path}")
        else:
            print(f"  WARNING: could not open detsys: {path}")

    print("\n=== Filling data histograms ===")
    data_hists = fill_data_histograms(rdata, BIN_CONFIG, cfg["selection"])

    print("\n=== Loading CV histograms ===")
    cv_hists = load_cv_histograms(rxsec, BIN_CONFIG, cfg["sample"])

    print("\n=== Computing chi2 ===\n")
    results = {}
    for var in BIN_CONFIG:
        if var not in data_hists or var not in cv_hists:
            continue
        V            = load_covariance_matrix(rcovar, var)
        det_abs_unc  = load_detector_abs_unc(rdetsys, var, cv_hists[var])
        chi2, ndof, pval = compute_chi2(var, data_hists[var], cv_hists[var], V, det_abs_unc)
        if chi2 is not None:
            results[var] = {"chi2": chi2, "ndof": ndof, "pvalue": pval}

    print("\n" + "="*65)
    print(f"  {cfg['label']}")
    print(f"{'Variable':<35} {'chi2':>8} {'ndof':>6} {'chi2/ndof':>10} {'p-value':>10}")
    print("="*65)
    for var, r in results.items():
        short = var.replace("numuCC1piNpReco_", "")
        print(f"{short:<35} {r['chi2']:>8.2f} {r['ndof']:>6d} "
              f"{r['chi2']/r['ndof']:>10.2f} {r['pvalue']:>10.4f}")
    print("="*65)
    print("V_total = V_xsecflux + V_stat + V_det (diagonal)")

    rdata.Close()
    rxsec.Close()
    rcovar.Close()
    for rf in rdetsys:
        rf.Close()