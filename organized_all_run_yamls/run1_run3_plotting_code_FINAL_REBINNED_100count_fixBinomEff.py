# To run: python3 plot_tki_rebinned.py <run_number> [contained|uncontained]
# e.g.    python3 plot_tki_rebinned.py 1
#         python3 plot_tki_rebinned.py 3 uncontained
#         python3 plot_tki_rebinned.py 3 contained   (default)
#
# Uses final adaptive bin edges (Run 3 Contained as reference bottleneck).
# Uses rebinned xsecflux files for systematic uncertainty bands.

import os, sys
import array
import ROOT as rt
from math import sqrt
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

rt.gROOT.SetBatch(True)
rt.gStyle.SetOptStat(0)

lantern_dir = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana"

# ══════════════════════════════════════════════════════════════════════════════
# FINAL BIN EDGES (Run 3 Contained as bottleneck reference)
# ══════════════════════════════════════════════════════════════════════════════
# Final bin edges (Run 3 Contained, >=100 raw MC counts per bin)
BIN_EDGES = {
    "numuCC1piNpReco_delAlphaT":   [0.0, 18.0, 36.0, 54.0, 72.0, 90.0, 108.0, 126.0, 144.0, 162.0, 180.0],
    "numuCC1piNpReco_pN":          [0.0, 0.128, 0.192, 0.256, 0.32, 0.384, 0.448, 0.512, 0.576, 0.64, 0.768, 1.6],
    "numuCC1piNpReco_delPTT":      [-1.0, -0.36, -0.28, -0.2, -0.12, -0.04, 0.04, 0.12, 0.2, 0.28, 0.36, 1.0],
    "numuCC1piNpReco_muKE":        [0.0, 60.0, 120.0, 180.0, 240.0, 300.0, 360.0, 420.0, 480.0, 540.0, 660.0, 1500.0],
    "numuCC1piNpReco_pionKE":      [0.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 220.0, 260.0, 500.0],
    "numuCC1piNpReco_maxprotonKE": [0.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 320.0, 360.0, 500.0],
}

def make_th1d(name, title, varname):
    """Create a TH1D with the correct (possibly variable) binning for varname."""
    edges     = BIN_EDGES[varname]
    edges_arr = array.array('d', edges)
    h = rt.TH1D(name, title, len(edges) - 1, edges_arr)
    h.Sumw2()
    return h

# ══════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATIONS
# ══════════════════════════════════════════════════════════════════════════════

run_num   = int(sys.argv[1]) if len(sys.argv) > 1 else 1
contained = (sys.argv[2].lower() != "uncontained") if len(sys.argv) > 2 else True
print(f"run_num = {run_num},  contained = {contained}")

if run_num == 1:
    targetpot  = 4.446e+19
    scaling = {
        "numu_sig": targetpot / 4.67569e+20,
        "numu_bg":  targetpot / 4.67569e+20,
        "extbnb":   10375708.0 / 34202767.0,
        "data":     1.0
    }
    files = {
        "numu_sig": f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_bnb_nu_overlay_20260316_164839.root",
        "numu_bg":  f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_bnb_nu_overlay_20260316_164839.root",
        "extbnb":   f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_extbnb_mcc9_v29e_20260227_171017.root",
        "data":     f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_data_bnb5e19_20260227_171123.root",
    }
    data_legend     = "Run1 Data"
    sel_label       = "contained" if contained else "uncontained"
    plot_title      = f"Run 1 {sel_label.capitalize()}"
    out_name        = f"{lantern_dir}/organized_all_run_yamls/plots_run1/tki_run1_{sel_label}_rebinned_100count_{timestamp}.root"
    xsecflux_sample = "run1_bnb_nu_overlay_mcc9_v28_wctagger"
    detsys_params   = [
        "wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ",
        "LYAtt", "LYDown", "LYRayleigh", "recomb2", "SCE"
    ]
    if contained:
        xsecflux_file = f"{lantern_dir}/studies/xsecfluxsys/systematics_output_run1_march2026_contained/output_xsecflux_tki_run1_march2026_contained_rebinned_100count.root"
        detsys_files  = [
            f"{lantern_dir}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_contained.root",
            f"{lantern_dir}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV_contained.root",
        ]
    else:
        xsecflux_file = f"{lantern_dir}/studies/xsecfluxsys/systematics_output_run1_march2026_uncontained/output_xsecflux_tki_run1_march2026_uncontained_rebinned_100count.root"
        detsys_files  = [
            f"{lantern_dir}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_uncontained.root",
            f"{lantern_dir}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV_uncontained.root",
        ]

if run_num == 3:
    targetpot  = 8.806e+18
    scaling = {
        "numu_sig": targetpot / 1.34669e+21,
        "numu_bg":  targetpot / 1.34669e+21,
        "extbnb":   2263559.0 / 111328485.0,
        "data":     1.0
    }
    files = {
        "numu_sig": f"{lantern_dir}/studies/numu_cc_tki/output_tki_run3b_1mil/mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_20260122_154228.root",
        "numu_bg":  f"{lantern_dir}/studies/numu_cc_tki/output_tki_run3b_1mil/mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_20260122_154228.root",
        "extbnb":   f"{lantern_dir}/studies/numu_cc_tki/output_split_tki_run3/run3_extbnb_mcc9_v29e_hadded_20260303_200450.root",
        "data":     f"{lantern_dir}/studies/numu_cc_tki/output_split_tki_run3/run3_data_bnb1e19_20260308_175632.root",
    }
    data_legend     = "Run3 Data"
    sel_label       = "contained" if contained else "uncontained"
    plot_title      = f"Run 3 {sel_label.capitalize()}"
    out_name        = f"{lantern_dir}/organized_all_run_yamls/plots_run3/tki_run3_{sel_label}_rebinned_100count_{timestamp}.root"
    xsecflux_sample = "mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil"
    detsys_params   = [
        "wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ",
        "LYAtt", "LYDown", "LYRayleigh", "recomb2", "SCE"
    ]
    if contained:
        xsecflux_file = f"{lantern_dir}/studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux_contained/output_xsecflux_tki_run3b_1mil_contained_rebinned_100count.root"
        detsys_files  = [
            f"{lantern_dir}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_contained.root",
            f"{lantern_dir}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV_contained.root",
        ]
    else:
        xsecflux_file = f"{lantern_dir}/studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux_uncontained/output_xsecflux_tki_run3b_1mil_uncontained_rebinned_100count.root"
        detsys_files  = [
            f"{lantern_dir}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_uncontained.root",
            f"{lantern_dir}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV_uncontained.root",
        ]

# ══════════════════════════════════════════════════════════════════════════════
# SYSTEMATICS PARAMETER LISTS
# ══════════════════════════════════════════════════════════════════════════════

flux_params = [
    "expskin_FluxUnisim", "horncurrent_FluxUnisim",
    "nucleoninexsec_FluxUnisim", "nucleonqexsec_FluxUnisim",
    "nucleontotxsec_FluxUnisim", "pioninexsec_FluxUnisim",
    "pionqexsec_FluxUnisim", "piontotxsec_FluxUnisim",
    "kminus_PrimaryHadronNormalization", "kplus_PrimaryHadronFeynmanScaling",
    "kzero_PrimaryHadronSanfordWang",
    "piminus_PrimaryHadronSWCentralSplineVariation",
    "piplus_PrimaryHadronSWCentralSplineVariation"
]
xsec_params = [
    "All_UBGenie", "XSecShape_CCMEC_UBGenie", "RPA_CCQE_UBGenie",
    "AxFFCCQEshape_UBGenie", "VecFFCCQEshape_UBGenie", "DecayAngMEC_UBGenie",
    "xsr_scc_Fa3_SCC", "xsr_scc_Fv3_SCC", "NormCCCOH_UBGenie",
    "NormNCCOH_UBGenie", "ThetaDelta2NRad_UBGenie", "Theta_Delta2Npi_UBGenie",
    "reinteractions_piminus_Geant4", "reinteractions_piplus_Geant4",
    "reinteractions_proton_Geant4"
]
all_xsecflux_pars = flux_params + xsec_params

# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def identify_systematic_type(syst_name):
    syst_lower = syst_name.lower()
    flux_kw  = ['flux','horn','beam','kminus','kplus','kzero','nucleon','expskin','pion']
    reint_kw = ['reint','fsi','absorption','charge_exchange','elastic','inelastic','geant4']
    for kw in flux_kw:
        if kw in syst_lower:
            return 'flux'
    for kw in reint_kw:
        if kw in syst_lower:
            return 'reint'
    return 'xsec'


def make_hist_w_errors(rfile, varname, sample, parlist):
    """Load xsecflux CV + per-parameter variance/mean histograms.
    The rebinned xsecflux file already has the correct bin edges,
    so FindBin mapping works correctly.
    """
    cv_name = f"hnumuCC1piNpReco_{varname}_{sample}_cv"
    hcv = rfile.Get(cv_name)
    if not hcv or hcv.IsZombie():
        print(f"  Warning: could not find CV histogram {cv_name}")
        return None
    print(f"  Found CV: {cv_name}  ({hcv.GetNbinsX()} bins)")

    hvar_flux  = hcv.Clone(f"h{varname}__{sample}_fluxvar");  hvar_flux.Reset()
    hvar_xsec  = hcv.Clone(f"h{varname}__{sample}_xsecvar");  hvar_xsec.Reset()
    hvar_reint = hcv.Clone(f"h{varname}__{sample}_reintvar"); hvar_reint.Reset()
    hvar_tot   = hcv.Clone(f"h{varname}__{sample}_totvar");   hvar_tot.Reset()

    n_loaded = 0
    for parname in parlist:
        hvar  = rfile.Get(f"hnumuCC1piNpReco_{varname}__{sample}__{parname}_variance")
        hmean = rfile.Get(f"hnumuCC1piNpReco_{varname}__{sample}__{parname}_mean")
        if not hvar or hvar.IsZombie() or not hmean or hmean.IsZombie():
            continue
        n_loaded += 1
        syst_type = identify_systematic_type(parname)

        for ibin in range(0, hvar_tot.GetNbinsX() + 2):
            xvar   = hvar.GetBinContent(ibin)
            xmean  = hmean.GetBinContent(ibin)
            cv_val = hcv.GetBinContent(ibin)
            if xmean > 0 and cv_val > 0:
                frac_var = xvar / xmean**2
            else:
                frac_var = 0.0
            hvar_tot.SetBinContent(ibin, hvar_tot.GetBinContent(ibin) + frac_var)
            if syst_type == 'flux':
                hvar_flux.SetBinContent(ibin, hvar_flux.GetBinContent(ibin) + frac_var)
            elif syst_type == 'xsec':
                hvar_xsec.SetBinContent(ibin, hvar_xsec.GetBinContent(ibin) + frac_var)
            elif syst_type == 'reint':
                hvar_reint.SetBinContent(ibin, hvar_reint.GetBinContent(ibin) + frac_var)

    print(f"  Loaded {n_loaded}/{len(parlist)} xsecflux parameters for {varname}")
    return {'cv': hcv, 'totvar': hvar_tot,
            'fluxvar': hvar_flux, 'xsecvar': hvar_xsec, 'reintvar': hvar_reint}


def load_detector_variations(rfiles, varname, detsys_params, bin_edges):
    """Load detsys CV+var histograms and build combined fractional-variance
    histogram on the ANALYSIS binning (variable bin edges).
    Sums __cv and __var over original detsys bins inside each merged analysis bin.
    """
    edges_arr = array.array('d', bin_edges)
    n_bins    = len(bin_edges) - 1
    h_frac_var = rt.TH1D(f"h{varname}__detector_frac_variance",
                         f"{varname} detector frac variance",
                         n_bins, edges_arr)
    h_frac_var.Reset()

    n_loaded = 0
    for param in detsys_params:
        for rfile in rfiles:
            h_cv  = rfile.Get(f"hnumuCC1piNpReco_{varname}__{param}__cv")
            h_var = rfile.Get(f"hnumuCC1piNpReco_{varname}__{param}__var")
            if not h_cv or h_cv.IsZombie() or not h_var or h_var.IsZombie():
                continue
            n_loaded += 1
            n_det_bins = h_cv.GetNbinsX()
            for ibin in range(1, n_bins + 1):
                lo = h_frac_var.GetXaxis().GetBinLowEdge(ibin)
                hi = h_frac_var.GetXaxis().GetBinUpEdge(ibin)
                sum_cv  = sum(h_cv.GetBinContent(b)  for b in range(1, n_det_bins+1)
                              if lo <= h_cv.GetXaxis().GetBinCenter(b) < hi)
                sum_var = sum(h_var.GetBinContent(b) for b in range(1, n_det_bins+1)
                              if lo <= h_cv.GetXaxis().GetBinCenter(b) < hi)
                if sum_cv > 0:
                    frac_diff = (sum_var - sum_cv) / sum_cv
                    h_frac_var.SetBinContent(ibin, h_frac_var.GetBinContent(ibin) + frac_diff**2)
            break  # found this param, move on

    print(f"  Loaded {n_loaded}/{len(detsys_params)} detector variations for {varname}")
    return {'frac_variance': h_frac_var}

# ══════════════════════════════════════════════════════════════════════════════
# CUTS
# ══════════════════════════════════════════════════════════════════════════════

if contained:
    reco_cut   = "(numuCC1piNpReco_is_target_1mu1piNproton==1 && numuCC1piNpReco_event_is_contained==2)"
    signal_cut = "(numuCC1piNp_is_infv==1 && numuCC1piNp_is_target_cc_numu_1pi_nproton==1 && numuCC1piNp_is_muon_contained==1 && numuCC1piNp_is_pion_contained==1 && numuCC1piNp_is_maxproton_contained==1)"
else:
    reco_cut   = "(numuCC1piNpReco_is_target_1mu1piNproton==1)"
    signal_cut = "(numuCC1piNp_is_infv==1 && numuCC1piNp_is_target_cc_numu_1pi_nproton==1)"

misid_cut = "(numuCC1piNp_is_infv==0 || numuCC1piNp_is_target_cc_numu_1pi_nproton==0)"

# ══════════════════════════════════════════════════════════════════════════════
# COMMON SETUP
# ══════════════════════════════════════════════════════════════════════════════

samples = ["numu_sig", "numu_bg", "extbnb", "data"]

tfiles = {}
trees  = {}
for sample in samples:
    tfiles[sample] = rt.TFile(files[sample])
    if tfiles[sample].IsZombie():
        raise RuntimeError(f"Could not open {files[sample]}")
    trees[sample] = tfiles[sample].Get("analysis_tree")
    print(f"sample={sample} has {trees[sample].GetEntries()} entries")

# Variables: (branch, xtitle)
# Binning comes from BIN_EDGES dict
vars = [
    ("numuCC1piNpReco_delPTT",      f"{plot_title} #delta p_{{TT}};#delta p_{{TT}} (GeV/c)"),
    ("numuCC1piNpReco_pN",          f"{plot_title} p_{{N}};p_{{N}} (GeV/c)"),
    ("numuCC1piNpReco_delAlphaT",   f"{plot_title} #delta#alpha_{{T}};#delta#alpha_{{T}} (deg)"),
    ("numuCC1piNpReco_muKE",        f"{plot_title} Muon Kinetic Energy;Muon KE (MeV)"),
    ("numuCC1piNpReco_maxprotonKE", f"{plot_title} Max Proton Kinetic Energy;Proton KE (MeV)"),
    ("numuCC1piNpReco_pionKE",      f"{plot_title} Pion Kinetic Energy;Pion KE (MeV)"),
]

truth_var = {
    "numuCC1piNpReco_delPTT":      "numuCC1piNp_delPTT",
    "numuCC1piNpReco_pN":          "numuCC1piNp_pN",
    "numuCC1piNpReco_delAlphaT":   "numuCC1piNp_delAlphaT",
    "numuCC1piNpReco_muKE":        "numuCC1piNp_muonKE",
    "numuCC1piNpReco_maxprotonKE": "numuCC1piNp_protonKE",
    "numuCC1piNpReco_pionKE":      "numuCC1piNp_pionKE",
}

os.makedirs(os.path.dirname(out_name), exist_ok=True)
temp     = rt.TFile("temp.root", "recreate")
out_file = rt.TFile(out_name, "recreate")

legend_POT_string = f"Events per {targetpot:.3e} POT"

# ══════════════════════════════════════════════════════════════════════════════
# LOAD SYSTEMATICS
# ══════════════════════════════════════════════════════════════════════════════

xsecflux_hists = {}
detsys_hists   = {}

if xsecflux_file is not None and os.path.exists(xsecflux_file):
    print(f"\nLoading xsecflux uncertainties from {xsecflux_file}")
    xfile = rt.TFile(xsecflux_file)
    if not xfile.IsZombie():
        for var, _ in vars:
            short = var.replace("numuCC1piNpReco_", "")
            result = make_hist_w_errors(xfile, short, xsecflux_sample, all_xsecflux_pars)
            if result:
                xsecflux_hists[short] = result
    else:
        print("  Warning: could not open xsecflux file")

dfiles = []
if detsys_files:
    print(f"\nLoading detector systematics")
    for path in detsys_files:
        if os.path.exists(path):
            df = rt.TFile(path)
            if not df.IsZombie():
                dfiles.append(df)
                print(f"  Opened {path}")
            else:
                print(f"  Warning: could not open {path}")
        else:
            print(f"  Warning: not found: {path}")

    if dfiles:
        for var, _ in vars:
            short     = var.replace("numuCC1piNpReco_", "")
            bin_edges = BIN_EDGES[var]
            result    = load_detector_variations(dfiles, short, detsys_params, bin_edges)
            if result:
                detsys_hists[short] = result

# ══════════════════════════════════════════════════════════════════════════════
# MAIN PLOT LOOP
# ══════════════════════════════════════════════════════════════════════════════

for var, htitle in vars:

    short       = var.replace("numuCC1piNpReco_", "")
    bin_edges   = BIN_EDGES[var]
    xmin        = bin_edges[0]
    xmax        = bin_edges[-1]
    title_parts = htitle.split(";")
    xtitle      = title_parts[1] if len(title_parts) > 1 else ""

    print(f"\n{'='*80}\n=== {short} ({len(bin_edges)-1} bins) ===")
    temp.cd()

    hists          = {}
    hists_unscaled = {}

    # ── Efficiency denominator ────────────────────────────────────────────────
    hname_denom = f"h_{short}_effdenom"
    h_denom = make_th1d(hname_denom, htitle, var)
    trees["numu_sig"].Draw(
        f"{truth_var[var]}>>{hname_denom}",
        f"({signal_cut})*eventweight_weight", "goff"
    )
    h_denom.Scale(scaling["numu_sig"])
    hists["effdenom"] = h_denom

    # ── Fill each sample ──────────────────────────────────────────────────────
    for sample in samples:
        hname          = f"h_{short}_{sample}"
        hname_unscaled = f"h_{short}_{sample}_unscaled"

        h          = make_th1d(hname,          htitle, var)
        h_unscaled = make_th1d(hname_unscaled, htitle, var)

        if sample == "numu_sig":
            samplecut  = f"({reco_cut}) && {signal_cut}"
            weight_str = f"({samplecut})*eventweight_weight"
        elif sample == "numu_bg":
            samplecut  = f"({reco_cut}) && {misid_cut}"
            weight_str = f"({samplecut})*eventweight_weight"
        else:
            weight_str = reco_cut

        trees[sample].Draw(f"{var}>>{hname}",          weight_str, "goff")
        trees[sample].Draw(f"{var}>>{hname_unscaled}",  weight_str, "goff")

        h.Scale(scaling[sample])

        hists[sample]          = h
        hists_unscaled[sample] = h_unscaled
        print(f"  {sample}: {h.Integral():.1f} events  (scale={scaling[sample]:.4e})")

    # ── Efficiency numerator ──────────────────────────────────────────────────
    hname_num = f"h_{short}_effnum"
    h_num = make_th1d(hname_num, htitle, var)
    trees["numu_sig"].Draw(
        f"{truth_var[var]}>>{hname_num}",
        f"({reco_cut} && {signal_cut})*eventweight_weight", "goff"
    )
    h_num.Scale(scaling["numu_sig"])
    hists["effnum"] = h_num

    # ── Total MC ──────────────────────────────────────────────────────────────
    h_total_mc = hists["numu_sig"].Clone(f"h_{short}_total_mc")
    h_total_mc.Add(hists["numu_bg"])
    h_total_mc_unscaled = hists_unscaled["numu_sig"].Clone(f"h_{short}_total_mc_unscaled")
    h_total_mc_unscaled.Add(hists_unscaled["numu_bg"])

    # ── Build uncertainty band ────────────────────────────────────────────────
    h_unc_total    = h_total_mc.Clone(f"h_{short}_unc_total");    h_unc_total.Reset()
    h_unc_flux     = h_total_mc.Clone(f"h_{short}_unc_flux");     h_unc_flux.Reset()
    h_unc_xsec     = h_total_mc.Clone(f"h_{short}_unc_xsec");     h_unc_xsec.Reset()
    h_unc_reint    = h_total_mc.Clone(f"h_{short}_unc_reint");    h_unc_reint.Reset()
    h_unc_detector = h_total_mc.Clone(f"h_{short}_unc_detector"); h_unc_detector.Reset()

    for ibin in range(0, h_total_mc.GetNbinsX() + 2):
        h_unc_total.SetBinContent(ibin,    h_total_mc.GetBinContent(ibin))
        h_unc_flux.SetBinContent(ibin,     h_total_mc.GetBinContent(ibin))
        h_unc_xsec.SetBinContent(ibin,     h_total_mc.GetBinContent(ibin))
        h_unc_reint.SetBinContent(ibin,    h_total_mc.GetBinContent(ibin))
        h_unc_detector.SetBinContent(ibin, h_total_mc.GetBinContent(ibin))

    for ibin in range(0, h_total_mc.GetNbinsX() + 2):
        central = h_total_mc.GetBinContent(ibin)
        if central <= 0:
            continue

        n_unscaled    = h_total_mc_unscaled.GetBinContent(ibin)
        frac_var_stat = (1.0 / n_unscaled) if n_unscaled > 0 else 0.0

        frac_var_flux  = 0.0
        frac_var_xsec  = 0.0
        frac_var_reint = 0.0
        if short in xsecflux_hists:
            xs         = xsecflux_hists[short]
            hcv_xs     = xs['cv']
            bin_centre = h_total_mc.GetXaxis().GetBinCenter(ibin)
            xs_ibin    = hcv_xs.GetXaxis().FindBin(bin_centre)
            frac_var_flux  = xs['fluxvar'].GetBinContent(xs_ibin)
            frac_var_xsec  = xs['xsecvar'].GetBinContent(xs_ibin)
            frac_var_reint = xs['reintvar'].GetBinContent(xs_ibin)

        frac_var_det = 0.0
        if short in detsys_hists:
            frac_var_det = detsys_hists[short]['frac_variance'].GetBinContent(ibin)

        frac_var_total = frac_var_stat + frac_var_flux + frac_var_xsec + frac_var_reint + frac_var_det

        h_unc_total.SetBinError(ibin,    central * sqrt(frac_var_total))
        h_unc_flux.SetBinError(ibin,     central * sqrt(frac_var_flux))
        h_unc_xsec.SetBinError(ibin,     central * sqrt(frac_var_xsec))
        h_unc_reint.SetBinError(ibin,    central * sqrt(frac_var_reint))
        h_unc_detector.SetBinError(ibin, central * sqrt(frac_var_det))

    # ── Styles ────────────────────────────────────────────────────────────────
    hists["extbnb"].SetFillColor(rt.kGray + 2)
    hists["extbnb"].SetFillStyle(1001)
    hists["extbnb"].SetLineColor(rt.kGray + 2)

    hists["numu_bg"].SetFillColor(rt.kAzure + 1)
    hists["numu_bg"].SetFillStyle(1001)
    hists["numu_bg"].SetLineColor(rt.kAzure + 1)

    hists["numu_sig"].SetFillColor(rt.kRed - 3)
    hists["numu_sig"].SetFillStyle(1001)
    hists["numu_sig"].SetLineColor(rt.kRed - 3)

    hists["data"].SetMarkerStyle(20)
    hists["data"].SetMarkerSize(0.8)
    hists["data"].SetMarkerColor(rt.kBlack)
    hists["data"].SetLineColor(rt.kBlack)
    hists["data"].SetLineWidth(2)

    gray_color = rt.TColor.GetColor(150, 150, 150)
    h_unc_total.SetFillColor(gray_color)
    h_unc_total.SetFillStyle(3013)
    h_unc_total.SetLineColor(gray_color)
    h_unc_total.SetLineWidth(0)
    h_unc_total.SetMarkerSize(0)
    h_unc_total.SetMarkerColor(gray_color)

    # ── Canvas 1: stacked data/MC plot ────────────────────────────────────────
    cname1  = f"c_{short}"
    canvas1 = rt.TCanvas(cname1, cname1, 800, 600)
    canvas1.SetTickx(1)
    canvas1.SetTicky(1)

    hstack = rt.THStack(f"hs_{short}", "")
    hstack.Add(hists["extbnb"])
    hstack.Add(hists["numu_bg"])
    hstack.Add(hists["numu_sig"])

    stack_max = hstack.GetMaximum()
    data_max  = hists["data"].GetMaximum()
    y_max     = max(stack_max, data_max) * 1.5

    if stack_max >= data_max:
        hstack.Draw("hist")
        hstack.SetMaximum(y_max)
        hstack.GetXaxis().SetTitle(xtitle)
        hstack.GetYaxis().SetTitle(legend_POT_string)
    else:
        hists["data"].SetMaximum(y_max)
        hists["data"].GetXaxis().SetTitle(xtitle)
        hists["data"].GetYaxis().SetTitle(legend_POT_string)
        hists["data"].Draw("E1")
        hstack.Draw("hist same")

    h_unc_total.Draw("E2 same")
    hists["data"].Draw("E1 same")

    legend1 = rt.TLegend(0.55, 0.50, 0.89, 0.88)
    legend1.SetTextSize(0.032)
    legend1.SetFillStyle(0)
    legend1.SetBorderSize(1)
    legend1.AddEntry(hists["extbnb"],   "BNB EXT",    "f")
    legend1.AddEntry(hists["numu_bg"],  "MC Bkg",     "f")
    legend1.AddEntry(hists["numu_sig"], "MC Signal", "f")
    legend1.AddEntry(hists["data"],     f"{data_legend}", "lep")
    legend1.AddEntry(h_unc_total,       "Sys. Unc.", "f")
    legend1.Draw()

    canvas1.Update()
    out_file.cd()
    canvas1.Write(cname1)

    # ── Canvas 2: purity ──────────────────────────────────────────────────────
    cname2  = f"c_{short}_purity"
    canvas2 = rt.TCanvas(cname2, cname2, 800, 600)
    canvas2.SetTickx(1); canvas2.SetTicky(1)
    canvas2.SetGridx(1); canvas2.SetGridy(1)

    h_purity = hists["numu_sig"].Clone(f"h_{short}_purity")
    h_sum    = hists["numu_sig"].Clone(f"h_{short}_sum")
    h_sum.Add(hists["numu_bg"])
    h_sum.Add(hists["extbnb"])

    h_sum_unscaled = hists_unscaled["numu_sig"].Clone(f"h_{short}_sum_unscaled")
    h_sum_unscaled.Add(hists_unscaled["numu_bg"])

    overall_purity = hists["numu_sig"].Integral() / h_sum.Integral() if h_sum.Integral() > 0 else 0
    h_purity.Divide(h_sum)

    for ibin in range(1, h_purity.GetNbinsX() + 1):
        p                = h_purity.GetBinContent(ibin)
        n_total_unscaled = h_sum_unscaled.GetBinContent(ibin)
        purity_error     = sqrt(p * (1 - p) / n_total_unscaled) if n_total_unscaled > 0 else 0.0
        h_purity.SetBinError(ibin, purity_error)

    h_purity.SetLineColor(rt.kBlue)
    h_purity.SetMarkerColor(rt.kBlue)
    h_purity.SetMarkerStyle(20)
    h_purity.SetMarkerSize(0.8)
    h_purity.SetLineWidth(2)

    reco_xtitle = xtitle.lstrip()
    if not reco_xtitle.startswith("Reco "):
        reco_xtitle = f"Reco {reco_xtitle}"
    h_purity.SetTitle(f"{plot_title} Purity;{reco_xtitle};Purity")
    h_purity.GetYaxis().SetRangeUser(0.0, 1.1)
    h_purity.Draw("E1")

    line_p = rt.TLine(xmin, 1.0, xmax, 1.0)
    line_p.SetLineStyle(2); line_p.SetLineColor(rt.kGray + 2); line_p.Draw()

    leg_purity = rt.TLegend(0.25, 0.78, 0.75, 0.88)
    leg_purity.SetTextSize(0.028); leg_purity.SetFillStyle(1001); leg_purity.SetFillColor(rt.kWhite); leg_purity.SetBorderSize(1)
    leg_purity.AddEntry(h_purity, f"Purity (avg: {overall_purity:.3f})", "lep")
    leg_purity.Draw()
    print(f"  Overall purity: {overall_purity:.3f}")

    canvas2.Update()
    out_file.cd()
    canvas2.Write(cname2)

    # ── Canvas 3: efficiency ──────────────────────────────────────────────────
    cname3  = f"c_{short}_efficiency"
    canvas3 = rt.TCanvas(cname3, cname3, 800, 600)
    canvas3.SetTickx(1); canvas3.SetTicky(1)
    canvas3.SetGridx(1); canvas3.SetGridy(1)

    h_eff = hists["effnum"].Clone(f"h_{short}_eff")
    overall_eff = hists["effnum"].Integral() / hists["effdenom"].Integral() if hists["effdenom"].Integral() > 0 else 0
    h_eff.Divide(hists["effdenom"])

    # Override with binomial errors (numerator is a subset of denominator),
    # consistent with the purity error treatment above.
    for ibin in range(1, h_eff.GetNbinsX() + 1):
        eff        = h_eff.GetBinContent(ibin)
        n_denom_unscaled = h_denom.GetBinContent(ibin) / scaling["numu_sig"] if scaling["numu_sig"] > 0 else 0.0
        eff_error  = sqrt(eff * (1 - eff) / n_denom_unscaled) if n_denom_unscaled > 0 else 0.0
        h_eff.SetBinError(ibin, eff_error)

    h_eff.SetLineColor(rt.kRed); h_eff.SetMarkerColor(rt.kRed)
    h_eff.SetMarkerStyle(21); h_eff.SetMarkerSize(0.8); h_eff.SetLineWidth(2)

    base_xtitle = xtitle.lstrip()
    if base_xtitle.startswith("Reco "):
        base_xtitle = base_xtitle[5:]
    h_eff.SetTitle(f"{plot_title} Efficiency;True {base_xtitle};Efficiency")
    h_eff.GetYaxis().SetRangeUser(0.0, 1.1)
    h_eff.Draw("E1")

    line_e = rt.TLine(xmin, 1.0, xmax, 1.0)
    line_e.SetLineStyle(2); line_e.SetLineColor(rt.kGray + 2); line_e.Draw()

    leg_eff = rt.TLegend(0.25, 0.78, 0.75, 0.88)
    leg_eff.SetTextSize(0.028); leg_eff.SetFillStyle(1001); leg_eff.SetFillColor(rt.kWhite); leg_eff.SetBorderSize(1)
    leg_eff.AddEntry(h_eff, f"Efficiency (avg: {overall_eff:.3f})", "lep")
    leg_eff.Draw()
    print(f"  Overall efficiency: {overall_eff:.3f}")

    canvas3.Update()
    out_file.cd()
    canvas3.Write(cname3)

    # ── Canvas 4: fractional uncertainty breakdown ────────────────────────────
    if xsecflux_hists or detsys_hists:
        cname4  = f"c_{short}_fracunc"
        canvas4 = rt.TCanvas(cname4, cname4, 800, 600)
        canvas4.SetTickx(1); canvas4.SetTicky(1)

        h_frac_stat     = h_total_mc.Clone(f"h_{short}_frac_stat");     h_frac_stat.Reset()
        h_frac_flux     = h_total_mc.Clone(f"h_{short}_frac_flux");     h_frac_flux.Reset()
        h_frac_xsec     = h_total_mc.Clone(f"h_{short}_frac_xsec");     h_frac_xsec.Reset()
        h_frac_reint    = h_total_mc.Clone(f"h_{short}_frac_reint");    h_frac_reint.Reset()
        h_frac_detector = h_total_mc.Clone(f"h_{short}_frac_detector"); h_frac_detector.Reset()
        h_frac_total    = h_total_mc.Clone(f"h_{short}_frac_total");    h_frac_total.Reset()

        for ibin in range(0, h_total_mc.GetNbinsX() + 2):
            central = h_total_mc.GetBinContent(ibin)
            if central <= 0:
                continue
            n_unscaled = h_total_mc_unscaled.GetBinContent(ibin)
            stat_frac  = (1.0 / sqrt(n_unscaled)) if n_unscaled > 0 else 0.0
            flux_frac  = h_unc_flux.GetBinError(ibin)     / central
            xsec_frac  = h_unc_xsec.GetBinError(ibin)     / central
            reint_frac = h_unc_reint.GetBinError(ibin)    / central
            det_frac   = h_unc_detector.GetBinError(ibin) / central
            tot_frac   = sqrt(stat_frac**2 + flux_frac**2 + xsec_frac**2 + reint_frac**2 + det_frac**2)

            h_frac_stat.SetBinContent(ibin,     stat_frac)
            h_frac_flux.SetBinContent(ibin,     flux_frac)
            h_frac_xsec.SetBinContent(ibin,     xsec_frac)
            h_frac_reint.SetBinContent(ibin,    reint_frac)
            h_frac_detector.SetBinContent(ibin, det_frac)
            h_frac_total.SetBinContent(ibin,    tot_frac)

        h_frac_stat.SetLineColor(rt.kGray + 1);     h_frac_stat.SetLineWidth(2);     h_frac_stat.SetFillStyle(0)
        h_frac_flux.SetLineColor(rt.kGreen + 2);    h_frac_flux.SetLineWidth(2);     h_frac_flux.SetFillStyle(0)
        h_frac_xsec.SetLineColor(rt.kRed);          h_frac_xsec.SetLineWidth(2);     h_frac_xsec.SetFillStyle(0)
        h_frac_reint.SetLineColor(rt.kMagenta + 1); h_frac_reint.SetLineWidth(2);    h_frac_reint.SetFillStyle(0)
        h_frac_detector.SetLineColor(rt.kBlue);     h_frac_detector.SetLineWidth(2); h_frac_detector.SetFillStyle(0)
        h_frac_total.SetLineColor(rt.kBlack);       h_frac_total.SetLineWidth(3);    h_frac_total.SetFillStyle(0)

        max_val = max(h_frac_stat.GetMaximum(), h_frac_flux.GetMaximum(),
                      h_frac_xsec.GetMaximum(), h_frac_reint.GetMaximum(),
                      h_frac_detector.GetMaximum(), h_frac_total.GetMaximum())
        max_val = min(max_val, 2.0)

        h_frac_total.SetTitle(f"{plot_title} Fractional Uncertainty;{xtitle};Fractional Uncertainty")
        h_frac_total.SetMaximum(max_val * 1.2)
        h_frac_total.SetMinimum(0.0)
        h_frac_total.Draw("hist")
        h_frac_stat.Draw("hist same")
        h_frac_flux.Draw("hist same")
        h_frac_xsec.Draw("hist same")
        h_frac_reint.Draw("hist same")
        h_frac_detector.Draw("hist same")

        leg3 = rt.TLegend(0.12, 0.60, 0.38, 0.88)
        leg3.SetTextSize(0.026); leg3.SetFillStyle(0); leg3.SetBorderSize(1)
        leg3.AddEntry(h_frac_total,    "Total",         "l")
        leg3.AddEntry(h_frac_stat,     "Stat.",         "l")
        leg3.AddEntry(h_frac_flux,     "Flux",          "l")
        leg3.AddEntry(h_frac_xsec,     "Cross sec.",    "l")
        leg3.AddEntry(h_frac_reint,    "Reinteraction", "l")
        leg3.AddEntry(h_frac_detector, "Detector",      "l")
        leg3.Draw()

        canvas4.Update()
        out_file.cd()
        canvas4.Write(cname4)

    temp.cd()

out_file.Close()
temp.Close()
print(f"\nSaved -> {out_name}")

for f in tfiles.values():
    f.Close()
for df in dfiles:
    df.Close()