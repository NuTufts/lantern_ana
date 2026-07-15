"""
plot_xsecflux_fracunc.py

Plots the combined xsec+flux fractional uncertainty for each TKI variable,
derived TWO ways so you can cross-check them:

  (1) DIRECT: from the per-parameter variance histograms in the xsecflux file
              sqrt(sum_p frac_var_p) -- same method as plot_tki.py
  (2) COVAR:  from the diagonal of the total covariance matrix
              sqrt(V_ii / mu_i^2)

These two curves should agree bin-by-bin. Any discrepancy indicates a bug
in one of the two code paths.

No POT scaling -- raw MC counts throughout.

Usage:
    python3 plot_xsecflux_fracunc.py
"""

import os, sys
from math import sqrt
import ROOT as rt

rt.gROOT.SetBatch(True)
rt.gStyle.SetOptStat(0)

# ── File paths ────────────────────────────────────────────────────────────────
XSECFLUX_FILE = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/systematics_output_run1_march2026_contained/output_xsecflux_tki_run1_march2026_contained.root"
COVAR_FILE    = "output_covariance.root"   # output of make_covar_matrices.py
OUTPUT_FILE   = "output_xsecflux_fracunc_check.root"

SAMPLE = "run1_bnb_nu_overlay_mcc9_v28_wctagger"

# ── Variables ─────────────────────────────────────────────────────────────────
VARS = [
    ("numuCC1piNpReco_delAlphaT",   10,   0.0,  180.0, "#Delta#alpha_{T} (deg)"),
    ("numuCC1piNpReco_pN",          25,   0.0,    1.6, "p_{N} (GeV/c)"),
    ("numuCC1piNpReco_delPTT",      25,  -1.0,    1.0, "#Delta p_{TT} (GeV/c)"),
    ("numuCC1piNpReco_muKE",        25,   0.0, 1500.0, "Muon KE (MeV)"),
    ("numuCC1piNpReco_pionKE",      25,   0.0,  500.0, "Pion KE (MeV)"),
    ("numuCC1piNpReco_maxprotonKE", 25,   0.0,  500.0, "Max Proton KE (MeV)"),
]

# ── All xsecflux parameters (same list as plot_tki.py) ───────────────────────
FLUX_PARAMS = [
    "expskin_FluxUnisim", "horncurrent_FluxUnisim",
    "nucleoninexsec_FluxUnisim", "nucleonqexsec_FluxUnisim",
    "nucleontotxsec_FluxUnisim", "pioninexsec_FluxUnisim",
    "pionqexsec_FluxUnisim", "piontotxsec_FluxUnisim",
    "kminus_PrimaryHadronNormalization", "kplus_PrimaryHadronFeynmanScaling",
    "kzero_PrimaryHadronSanfordWang",
    "piminus_PrimaryHadronSWCentralSplineVariation",
    "piplus_PrimaryHadronSWCentralSplineVariation",
]
XSEC_PARAMS = [
    "All_UBGenie", "XSecShape_CCMEC_UBGenie", "RPA_CCQE_UBGenie",
    "AxFFCCQEshape_UBGenie", "VecFFCCQEshape_UBGenie", "DecayAngMEC_UBGenie",
    "xsr_scc_Fa3_SCC", "xsr_scc_Fv3_SCC", "NormCCCOH_UBGenie",
    "NormNCCOH_UBGenie", "ThetaDelta2NRad_UBGenie", "Theta_Delta2Npi_UBGenie",
    "reinteractions_piminus_Geant4", "reinteractions_piplus_Geant4",
    "reinteractions_proton_Geant4",
]
ALL_PARAMS = FLUX_PARAMS + XSEC_PARAMS


# ─────────────────────────────────────────────────────────────────────────────
def build_direct_fracunc(xfile, varname, sample, parlist, nbins, xlo, xhi):
    """
    Method (1): sum per-parameter fractional variances from the variance
    and mean histograms, exactly as plot_tki.py does.
    Returns a TH1D of fractional uncertainty (not variance) per bin.
    """
    short   = varname.replace("numuCC1piNpReco_", "")
    cv_name = f"h{varname}_{sample}_cv"
    hcv     = xfile.Get(cv_name)
    if not hcv or hcv.IsZombie():
        print(f"  ERROR: CV not found: {cv_name}")
        return None

    # Accumulate fractional variance bin-by-bin
    h_frac_var = rt.TH1D(f"h_{short}_direct_fracvar", "", nbins, xlo, xhi)
    h_frac_var.Reset()

    n_loaded = 0
    for par in parlist:
        hvar  = xfile.Get(f"h{varname}__{sample}__{par}_variance")
        hmean = xfile.Get(f"h{varname}__{sample}__{par}_mean")
        if not hvar or hvar.IsZombie() or not hmean or hmean.IsZombie():
            continue
        n_loaded += 1
        for ibin in range(0, nbins + 2):
            xvar  = hvar.GetBinContent(ibin)
            xmean = hmean.GetBinContent(ibin)
            if xmean > 0:
                frac_var = xvar / (xmean ** 2)   # (sigma/mean)^2
            else:
                frac_var = 0.0
            h_frac_var.SetBinContent(ibin, h_frac_var.GetBinContent(ibin) + frac_var)

    print(f"  [{short}] direct: loaded {n_loaded}/{len(parlist)} parameters")

    # Convert fractional variance -> fractional uncertainty
    h_frac_unc = rt.TH1D(f"h_{short}_direct_fracunc", "", nbins, xlo, xhi)
    for ibin in range(0, nbins + 2):
        h_frac_unc.SetBinContent(ibin, sqrt(h_frac_var.GetBinContent(ibin)))

    return h_frac_unc, hcv


# ─────────────────────────────────────────────────────────────────────────────
def build_covar_fracunc(covar_file, xfile, varname, sample, nbins, xlo, xhi):
    """
    Method (2): extract fractional uncertainty from covariance matrix diagonal.
    sqrt(V_ii / mu_i^2)
    """
    short   = varname.replace("numuCC1piNpReco_", "")
    hcovar  = covar_file.Get(f"hcovar_total_{varname}")
    if not hcovar:
        print(f"  ERROR: covariance matrix not found: hcovar_total_{varname}")
        return None

    cv_name = f"h{varname}_{sample}_cv"
    hcv     = xfile.Get(cv_name)
    if not hcv or hcv.IsZombie():
        print(f"  ERROR: CV not found: {cv_name}")
        return None

    h_frac_unc = rt.TH1D(f"h_{short}_covar_fracunc", "", nbins, xlo, xhi)
    for ibin in range(1, nbins + 1):
        mu  = hcv.GetBinContent(ibin)
        Vii = hcovar.GetBinContent(ibin, ibin)
        if mu > 0 and Vii >= 0:
            h_frac_unc.SetBinContent(ibin, sqrt(Vii) / mu)
        else:
            h_frac_unc.SetBinContent(ibin, 0.0)

    return h_frac_unc


# ─────────────────────────────────────────────────────────────────────────────
def make_plot(varname, nbins, xlo, xhi, xtitle,
              h_direct, h_covar, hcv, out_file):
    """
    Draw both fractional uncertainty curves on one canvas.
    Also draw the CV histogram on a second pad so you can see
    where the distribution actually has events.
    """
    short = varname.replace("numuCC1piNpReco_", "")

    cname  = f"c_{short}_fracunc_check"
    canvas = rt.TCanvas(cname, cname, 800, 700)
    canvas.Divide(1, 2)

    # ── Top pad: fractional uncertainty comparison ────────────────────────
    pad1 = canvas.cd(1)
    pad1.SetPad(0.0, 0.35, 1.0, 1.0)
    pad1.SetTickx(1); pad1.SetTicky(1)
    pad1.SetBottomMargin(0.02)

    ymax = max(h_direct.GetMaximum(), h_covar.GetMaximum()) * 1.3
    ymax = min(ymax, 2.0)   # cap at 200%

    h_direct.SetLineColor(rt.kRed)
    h_direct.SetLineWidth(2)
    h_direct.SetFillStyle(0)
    h_direct.SetTitle(f"xsec+flux frac. unc. check: {short}")
    h_direct.GetYaxis().SetTitle("Fractional Uncertainty")
    h_direct.GetYaxis().SetTitleSize(0.07)
    h_direct.GetYaxis().SetLabelSize(0.06)
    h_direct.GetXaxis().SetLabelSize(0)
    h_direct.SetMaximum(ymax)
    h_direct.SetMinimum(0.0)
    h_direct.Draw("hist")

    h_covar.SetLineColor(rt.kBlue)
    h_covar.SetLineWidth(2)
    h_covar.SetLineStyle(2)
    h_covar.SetFillStyle(0)
    h_covar.Draw("hist same")

    leg = rt.TLegend(0.55, 0.65, 0.88, 0.88)
    leg.SetTextSize(0.06)
    leg.SetFillStyle(0)
    leg.SetBorderSize(1)
    leg.AddEntry(h_direct, "Direct (variance hists)", "l")
    leg.AddEntry(h_covar,  "Covar diagonal",          "l")
    leg.Draw()

    # ── Bottom pad: CV histogram (raw counts, no POT scaling) ────────────
    pad2 = canvas.cd(2)
    pad2.SetPad(0.0, 0.0, 1.0, 0.35)
    pad2.SetTickx(1); pad2.SetTicky(1)
    pad2.SetTopMargin(0.02)
    pad2.SetBottomMargin(0.25)

    hcv_draw = hcv.Clone(f"h_{short}_cv_draw")
    hcv_draw.SetLineColor(rt.kBlack)
    hcv_draw.SetLineWidth(2)
    hcv_draw.SetFillColor(rt.kAzure - 9)
    hcv_draw.SetFillStyle(1001)
    hcv_draw.SetTitle("")
    hcv_draw.GetXaxis().SetTitle(xtitle)
    hcv_draw.GetXaxis().SetTitleSize(0.10)
    hcv_draw.GetXaxis().SetLabelSize(0.09)
    hcv_draw.GetYaxis().SetTitle("MC counts (raw)")
    hcv_draw.GetYaxis().SetTitleSize(0.08)
    hcv_draw.GetYaxis().SetLabelSize(0.07)
    hcv_draw.Draw("hist")

    canvas.Update()
    out_file.cd()
    canvas.Write(cname)
    print(f"  [{short}] wrote canvas: {cname}")

    return canvas   # keep in scope


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n=== Opening files ===")
    xfile      = rt.TFile(XSECFLUX_FILE)
    covar_file = rt.TFile(COVAR_FILE)
    out_file   = rt.TFile(OUTPUT_FILE, "recreate")

    for f, name in [(xfile, XSECFLUX_FILE), (covar_file, COVAR_FILE)]:
        if not f or f.IsZombie():
            print(f"ERROR: could not open {name}")
            sys.exit(1)

    canvases = []   # keep canvases in scope until file is closed

    for varname, nbins, xlo, xhi, xtitle in VARS:
        short = varname.replace("numuCC1piNpReco_", "")
        print(f"\n{'='*60}\n  {short}")

        result = build_direct_fracunc(xfile, varname, SAMPLE, ALL_PARAMS,
                                      nbins, xlo, xhi)
        if result is None:
            continue
        h_direct, hcv = result

        h_covar = build_covar_fracunc(covar_file, xfile, varname, SAMPLE,
                                      nbins, xlo, xhi)
        if h_covar is None:
            continue

        # Print bin-by-bin comparison for quick numerical check
        print(f"  {'bin':>4}  {'direct':>10}  {'covar':>10}  {'ratio':>8}")
        for ibin in range(1, nbins + 1):
            d = h_direct.GetBinContent(ibin)
            c = h_covar.GetBinContent(ibin)
            ratio = (c / d) if d > 0 else 0.0
            print(f"  {ibin:>4}  {d:>10.4f}  {c:>10.4f}  {ratio:>8.4f}")

        c = make_plot(varname, nbins, xlo, xhi, xtitle,
                      h_direct, h_covar, hcv, out_file)
        canvases.append(c)

    out_file.Close()
    xfile.Close()
    covar_file.Close()
    print(f"\nDone. Output: {OUTPUT_FILE}")