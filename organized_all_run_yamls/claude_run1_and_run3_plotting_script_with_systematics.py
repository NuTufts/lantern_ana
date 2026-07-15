# To run: python3 plot_tki.py <run_number>
# e.g.    python3 plot_tki.py 1
#         python3 plot_tki.py 3

import os, sys
import ROOT as rt
from math import sqrt
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

rt.gROOT.SetBatch(True)
rt.gStyle.SetOptStat(0)

lantern_dir = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana"

# ══════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATIONS
# ══════════════════════════════════════════════════════════════════════════════

run_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
print(f"run_num = {run_num}")

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
    data_legend  = "Run1 Data"
    plot_title   = "Run 1: TKI (Contained)"
    out_name     = f"{lantern_dir}/organized_all_run_yamls/plots_run1/tki_run1_contained_withsys_{timestamp}.root"
    # Systematics
    xsecflux_file   = f"{lantern_dir}/studies/xsecfluxsys/systematics_output_run1_march2026/output_xsecflux_tki_run1_march2026.root"
    xsecflux_sample = "run1_bnb_nu_overlay_mcc9_v28_wctagger"
    detsys_files    = [
        f"{lantern_dir}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil.root",  # 7 params (using Run 3 detsys)
        f"{lantern_dir}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV.root",                 # SCE + recomb2
    ]
    detsys_params   = [
        "wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ",
        "LYAtt", "LYDown", "LYRayleigh",
        "recomb2", "SCE"
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
    data_legend  = "Run3 Data"
    plot_title   = "Run 3: TKI (Contained)"
    out_name     = f"{lantern_dir}/organized_all_run_yamls/plots_run3/tki_run3_contained_withsys_{timestamp}.root"
    # Systematics
    xsecflux_file   = f"{lantern_dir}/studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux/output_xsecflux_tki_run3b_1mil.root"
    xsecflux_sample = "mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil"
    detsys_files    = [
        f"{lantern_dir}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil.root",  # 7 params
        f"{lantern_dir}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV.root",                 # SCE + recomb2
    ]
    detsys_params   = [
        "wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ",
        "LYAtt", "LYDown", "LYRayleigh",
        "recomb2", "SCE"
    ]

# ══════════════════════════════════════════════════════════════════════════════
# SYSTEMATICS PARAMETER LISTS (used for Run 3; ignored if files are None)
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
    Returns dict with keys: cv, totvar, fluxvar, xsecvar, reintvar.
    Histogram naming convention from the xsecflux file:
      CV:       hnumuCC1piNpReco_{var}_{sample}_cv
      variance: hnumuCC1piNpReco_{var}__{sample}__{par}_variance
      mean:     hnumuCC1piNpReco_{var}__{sample}__{par}_mean
    """
    cv_name = f"hnumuCC1piNpReco_{varname}_{sample}_cv"
    hcv = rfile.Get(cv_name)
    if not hcv or hcv.IsZombie():
        print(f"  Warning: could not find CV histogram {cv_name}")
        return None
    print(f"  Found CV: {cv_name}")

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
            xvar  = hvar.GetBinContent(ibin)
            xmean = hmean.GetBinContent(ibin)
            cv_val = hcv.GetBinContent(ibin)
            if xmean > 0:
                cv_var = xvar * (cv_val / xmean) ** 2
            else:
                cv_var = 0.0
            hvar_tot.SetBinContent(ibin, hvar_tot.GetBinContent(ibin) + cv_var)
            if syst_type == 'flux':
                hvar_flux.SetBinContent(ibin, hvar_flux.GetBinContent(ibin) + cv_var)
            elif syst_type == 'xsec':
                hvar_xsec.SetBinContent(ibin, hvar_xsec.GetBinContent(ibin) + cv_var)
            elif syst_type == 'reint':
                hvar_reint.SetBinContent(ibin, hvar_reint.GetBinContent(ibin) + cv_var)

    print(f"  Loaded {n_loaded}/{len(parlist)} xsecflux parameters for {varname}")
    return {'cv': hcv, 'totvar': hvar_tot,
            'fluxvar': hvar_flux, 'xsecvar': hvar_xsec, 'reintvar': hvar_reint}


def load_detector_variations(rfiles, varname, detsys_params):
    """Load detsys CV+var histograms from a list of files and build a
    combined fractional-variance histogram.
    Naming: hnumuCC1piNpReco_{var}__{param}__cv  /  __var
    """
    # Find a reference histogram for binning
    h_ref = None
    for rfile in rfiles:
        for param in detsys_params:
            h_temp = rfile.Get(f"hnumuCC1piNpReco_{varname}__{param}__cv")
            if h_temp and not h_temp.IsZombie():
                h_ref = h_temp
                break
        if h_ref:
            break
    if h_ref is None:
        print(f"  Warning: no detsys reference histogram found for {varname}")
        return None

    h_frac_var = h_ref.Clone(f"h{varname}__detector_frac_variance")
    h_frac_var.Reset()

    n_loaded = 0
    for param in detsys_params:
        for rfile in rfiles:
            h_cv  = rfile.Get(f"hnumuCC1piNpReco_{varname}__{param}__cv")
            h_var = rfile.Get(f"hnumuCC1piNpReco_{varname}__{param}__var")
            if not h_cv or h_cv.IsZombie() or not h_var or h_var.IsZombie():
                continue
            n_loaded += 1
            for ibin in range(0, h_frac_var.GetNbinsX() + 2):
                cv_val  = h_cv.GetBinContent(ibin)
                var_val = h_var.GetBinContent(ibin)
                if cv_val > 0:
                    frac_diff = (var_val - cv_val) / cv_val
                    h_frac_var.SetBinContent(ibin, h_frac_var.GetBinContent(ibin) + frac_diff**2)
            break  # found this param, move on

    print(f"  Loaded {n_loaded}/{len(detsys_params)} detector variations for {varname}")
    return {'frac_variance': h_frac_var}

# ══════════════════════════════════════════════════════════════════════════════
# CUTS (contained selection)
# ══════════════════════════════════════════════════════════════════════════════

reco_cut   = "(numuCC1piNpReco_is_target_1mu1piNproton==1 && numuCC1piNpReco_event_is_contained==2)"
signal_cut = "(numuCC1piNp_is_infv==1 && numuCC1piNp_is_target_cc_numu_1pi_nproton==1 && numuCC1piNp_is_muon_contained==1 && numuCC1piNp_is_pion_contained==1 && numuCC1piNp_is_maxproton_contained==1)"
misid_cut  = "(numuCC1piNp_is_infv==0 || numuCC1piNp_is_target_cc_numu_1pi_nproton==0)"

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

# Variables: (branch, nbins, xmin, xmax, "title;xtitle")
# The short name (after stripping prefix) must match what's in the syst files
vars = [
    ("numuCC1piNpReco_delPTT",      25, -1.0,    1.0,   f"Reco #Delta p_{{TT}} ({targetpot:.2e} POT);#Delta p_{{TT}} (GeV/c)"),
    ("numuCC1piNpReco_pN",          25,  0.0,    1.6,   f"Reco p_{{N}} ({targetpot:.2e} POT);p_{{N}} (GeV/c)"),
    ("numuCC1piNpReco_delAlphaT",   10,  0.0,  180.0,   f"Reco #Delta#alpha_{{T}} ({targetpot:.2e} POT);#Delta#alpha_{{T}} (deg)"),
    ("numuCC1piNpReco_muKE",        25,  0.0, 1500.0,   f"Reco Muon KE ({targetpot:.2e} POT);Muon KE (MeV)"),
    ("numuCC1piNpReco_maxprotonKE", 25,  0.0,  500.0,   f"Reco Max Proton KE ({targetpot:.2e} POT);Proton KE (MeV)"),
    ("numuCC1piNpReco_pionKE",      25,  0.0,  500.0,   f"Reco Pion KE ({targetpot:.2e} POT);Pion KE (MeV)"),
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

xsecflux_hists = {}  # keyed by short var name
detsys_hists   = {}  # keyed by short var name

if xsecflux_file is not None and os.path.exists(xsecflux_file):
    print(f"\nLoading xsecflux uncertainties from {xsecflux_file}")
    xfile = rt.TFile(xsecflux_file)
    if not xfile.IsZombie():
        for var, *_ in vars:
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
        for var, *_ in vars:
            short = var.replace("numuCC1piNpReco_", "")
            result = load_detector_variations(dfiles, short, detsys_params)
            if result:
                detsys_hists[short] = result

# ══════════════════════════════════════════════════════════════════════════════
# MAIN PLOT LOOP
# ══════════════════════════════════════════════════════════════════════════════

for var, nbins, xmin, xmax, htitle in vars:

    short       = var.replace("numuCC1piNpReco_", "")
    title_parts = htitle.split(";")
    xtitle      = title_parts[1] if len(title_parts) > 1 else ""

    print(f"\n{'='*80}\n=== {short} ===")
    temp.cd()

    hists          = {}
    hists_unscaled = {}

    # ── Efficiency denominator: all true signal, no reco cut ──────────────────
    hname_denom = f"h_{short}_effdenom"
    h_denom = rt.TH1D(hname_denom, htitle, nbins, xmin, xmax)
    h_denom.Sumw2()
    trees["numu_sig"].Draw(
        f"{truth_var[var]}>>{hname_denom}",
        f"({signal_cut})*eventweight_weight", "goff"
    )
    h_denom.Scale(scaling["numu_sig"])
    hists["effdenom"] = h_denom

    # ── Fill each sample (scaled) + unscaled copy ─────────────────────────────
    for sample in samples:
        hname          = f"h_{short}_{sample}"
        hname_unscaled = f"h_{short}_{sample}_unscaled"

        h          = rt.TH1D(hname,          htitle, nbins, xmin, xmax)
        h_unscaled = rt.TH1D(hname_unscaled, htitle, nbins, xmin, xmax)
        h.Sumw2()
        h_unscaled.Sumw2()

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

    # ── Efficiency numerator: true signal passing reco cut ────────────────────
    hname_num = f"h_{short}_effnum"
    h_num = rt.TH1D(hname_num, htitle, nbins, xmin, xmax)
    h_num.Sumw2()
    trees["numu_sig"].Draw(
        f"{truth_var[var]}>>{hname_num}",
        f"({reco_cut} && {signal_cut})*eventweight_weight", "goff"
    )
    h_num.Scale(scaling["numu_sig"])
    hists["effnum"] = h_num

    # ── Total MC (sig + bg) for uncertainty calculations ──────────────────────
    h_total_mc = hists["numu_sig"].Clone(f"h_{short}_total_mc")
    h_total_mc.Add(hists["numu_bg"])
    h_total_mc_unscaled = hists_unscaled["numu_sig"].Clone(f"h_{short}_total_mc_unscaled")
    h_total_mc_unscaled.Add(hists_unscaled["numu_bg"])

    # ── Build uncertainty band (Run 3 only; otherwise all zeros) ─────────────
    h_unc_total    = h_total_mc.Clone(f"h_{short}_unc_total");    h_unc_total.Reset()
    h_unc_flux     = h_total_mc.Clone(f"h_{short}_unc_flux");     h_unc_flux.Reset()
    h_unc_xsec     = h_total_mc.Clone(f"h_{short}_unc_xsec");     h_unc_xsec.Reset()
    h_unc_reint    = h_total_mc.Clone(f"h_{short}_unc_reint");    h_unc_reint.Reset()
    h_unc_detector = h_total_mc.Clone(f"h_{short}_unc_detector"); h_unc_detector.Reset()

    # Copy central values into uncertainty histograms (errors will be set below)
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

        # Statistical: use unscaled event count
        n_unscaled    = h_total_mc_unscaled.GetBinContent(ibin)
        frac_var_stat = (1.0 / n_unscaled) if n_unscaled > 0 else 0.0

        # xsecflux fractional variances
        frac_var_flux  = 0.0
        frac_var_xsec  = 0.0
        frac_var_reint = 0.0
        if short in xsecflux_hists:
            xs = xsecflux_hists[short]
            cv_xs = xs['cv'].GetBinContent(ibin)
            if cv_xs > 0:
                frac_var_flux  = xs['fluxvar'].GetBinContent(ibin)  / cv_xs**2
                frac_var_xsec  = xs['xsecvar'].GetBinContent(ibin)  / cv_xs**2
                frac_var_reint = xs['reintvar'].GetBinContent(ibin)  / cv_xs**2

        # Detector fractional variance
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

    # ── Canvas 1: stacked data/MC plot with uncertainty band ──────────────────
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
    legend1.AddEntry(hists["extbnb"],   f"BNB EXT ({hists['extbnb'].Integral():.1f})",    "f")
    legend1.AddEntry(hists["numu_bg"],  f"MC bkg ({hists['numu_bg'].Integral():.1f})",     "f")
    legend1.AddEntry(hists["numu_sig"], f"MC signal ({hists['numu_sig'].Integral():.1f})", "f")
    legend1.AddEntry(hists["data"],     f"{data_legend} ({int(hists['data'].Integral())})", "lep")
    legend1.AddEntry(h_unc_total,       "Sys. unc.", "f")
    legend1.Draw()

    canvas1.Update()
    out_file.cd()
    canvas1.Write(cname1)

    # ── Canvas 2: purity vs Reco <var> ────────────────────────────────────────
    # Numerator:   reco-selected signal (numu_sig, already in hists)
    # Denominator: all reco-selected events (sig + bg + EXT), binned in reco var
    cname2  = f"c_{short}_purity"
    canvas2 = rt.TCanvas(cname2, cname2, 800, 600)
    canvas2.SetTickx(1)
    canvas2.SetTicky(1)
    canvas2.SetGridx(1)
    canvas2.SetGridy(1)

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

    # x-axis label: "Reco <xtitle>" — strip any existing "Reco " prefix first
    reco_xtitle = xtitle.lstrip()
    if not reco_xtitle.startswith("Reco "):
        reco_xtitle = f"Reco {reco_xtitle}"
    h_purity.SetTitle(f"{plot_title};{reco_xtitle};Purity")
    h_purity.GetYaxis().SetRangeUser(0.0, 1.1)
    h_purity.Draw("E1")

    line_p = rt.TLine(xmin, 1.0, xmax, 1.0)
    line_p.SetLineStyle(2)
    line_p.SetLineColor(rt.kGray + 2)
    line_p.Draw()

    leg_purity = rt.TLegend(0.35, 0.78, 0.65, 0.88)
    leg_purity.SetTextSize(0.028)
    leg_purity.SetFillStyle(0)
    leg_purity.SetBorderSize(1)
    leg_purity.AddEntry(h_purity, f"Purity (avg: {overall_purity:.3f})", "lep")
    leg_purity.Draw()

    print(f"  Overall purity: {overall_purity:.3f}")

    canvas2.Update()
    out_file.cd()
    canvas2.Write(cname2)

    # ── Canvas 3: efficiency vs True <var> ────────────────────────────────────
    # Numerator:   true signal passing reco+contained cut, binned in truth var
    # Denominator: all true signal (no reco cut), binned in truth var
    cname3  = f"c_{short}_efficiency"
    canvas3 = rt.TCanvas(cname3, cname3, 800, 600)
    canvas3.SetTickx(1)
    canvas3.SetTicky(1)
    canvas3.SetGridx(1)
    canvas3.SetGridy(1)

    h_eff = hists["effnum"].Clone(f"h_{short}_eff")
    overall_eff = hists["effnum"].Integral() / hists["effdenom"].Integral() if hists["effdenom"].Integral() > 0 else 0
    h_eff.Divide(hists["effdenom"])

    h_eff.SetLineColor(rt.kRed)
    h_eff.SetMarkerColor(rt.kRed)
    h_eff.SetMarkerStyle(21)
    h_eff.SetMarkerSize(0.8)
    h_eff.SetLineWidth(2)

    # x-axis label: "True <xtitle>" — strip any existing "Reco " prefix first
    base_xtitle = xtitle.lstrip()
    if base_xtitle.startswith("Reco "):
        base_xtitle = base_xtitle[5:]
    true_xtitle = f"True {base_xtitle}"
    h_eff.SetTitle(f"{plot_title};{true_xtitle};Efficiency")
    h_eff.GetYaxis().SetRangeUser(0.0, 1.1)
    h_eff.Draw("E1")

    line_e = rt.TLine(xmin, 1.0, xmax, 1.0)
    line_e.SetLineStyle(2)
    line_e.SetLineColor(rt.kGray + 2)
    line_e.Draw()

    leg_eff = rt.TLegend(0.35, 0.78, 0.65, 0.88)
    leg_eff.SetTextSize(0.028)
    leg_eff.SetFillStyle(0)
    leg_eff.SetBorderSize(1)
    leg_eff.AddEntry(h_eff, f"Efficiency (avg: {overall_eff:.3f})", "lep")
    leg_eff.Draw()

    print(f"  Overall efficiency: {overall_eff:.3f}")

    canvas3.Update()
    out_file.cd()
    canvas3.Write(cname3)

    # ── Canvas 4: fractional uncertainty breakdown (Run 3 only) ───────────────
    if xsecflux_hists or detsys_hists:
        cname4  = f"c_{short}_fracunc"
        canvas4 = rt.TCanvas(cname4, cname4, 800, 600)
        canvas4.SetTickx(1)
        canvas4.SetTicky(1)

        h_frac_stat = h_total_mc.Clone(f"h_{short}_frac_stat"); h_frac_stat.Reset()
        h_frac_flux = h_total_mc.Clone(f"h_{short}_frac_flux"); h_frac_flux.Reset()
        h_frac_xsec = h_total_mc.Clone(f"h_{short}_frac_xsec"); h_frac_xsec.Reset()
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

        h_frac_stat.SetLineColor(rt.kGray + 1);  h_frac_stat.SetLineWidth(2);     h_frac_stat.SetFillStyle(0)
        h_frac_flux.SetLineColor(rt.kGreen + 2); h_frac_flux.SetLineWidth(2);     h_frac_flux.SetFillStyle(0)
        h_frac_xsec.SetLineColor(rt.kRed);       h_frac_xsec.SetLineWidth(2);     h_frac_xsec.SetFillStyle(0)
        h_frac_reint.SetLineColor(rt.kMagenta + 1); h_frac_reint.SetLineWidth(2); h_frac_reint.SetFillStyle(0)
        h_frac_detector.SetLineColor(rt.kBlue);  h_frac_detector.SetLineWidth(2); h_frac_detector.SetFillStyle(0)
        h_frac_total.SetLineColor(rt.kBlack);    h_frac_total.SetLineWidth(3);     h_frac_total.SetFillStyle(0)

        max_val = max(h_frac_stat.GetMaximum(), h_frac_flux.GetMaximum(),
                      h_frac_xsec.GetMaximum(), h_frac_reint.GetMaximum(),
                      h_frac_detector.GetMaximum(), h_frac_total.GetMaximum())
        max_val = min(max_val, 2.0)  # cap at 200% to avoid outlier-dominated axes

        h_frac_total.SetTitle(f"{plot_title};{xtitle};Fractional Uncertainty")
        h_frac_total.SetMaximum(max_val * 1.2)
        h_frac_total.SetMinimum(0.0)
        h_frac_total.Draw("hist")
        h_frac_stat.Draw("hist same")
        h_frac_flux.Draw("hist same")
        h_frac_xsec.Draw("hist same")
        h_frac_reint.Draw("hist same")
        h_frac_detector.Draw("hist same")

        leg3 = rt.TLegend(0.12, 0.60, 0.38, 0.88)
        leg3.SetTextSize(0.026)
        leg3.SetFillStyle(0)
        leg3.SetBorderSize(1)
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