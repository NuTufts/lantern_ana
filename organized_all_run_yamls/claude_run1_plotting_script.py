import os, sys
import ROOT as rt
from math import sqrt
from datetime import datetime

rt.gROOT.SetBatch(True)
rt.gStyle.SetOptStat(0)

run_num = 1
lantern_dir = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana"

targetpot = 4.446e+19

samples = ["numu_sig", "numu_bg", "extbnb", "data"]

scaling = {
    "numu_sig": targetpot / 8.98323351831587e+20,
    "numu_bg":  targetpot / 8.98323351831587e+20,
    "extbnb":   10375708.0 / 34202767.0,
    "data":     1.0
}

files = {
    "numu_sig": f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_bnb_nu_overlay_20260227_170113.root",
    "numu_bg":  f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_bnb_nu_overlay_20260227_170113.root",
    "extbnb":   f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_extbnb_mcc9_v29e_20260227_171017.root",
    "data":     f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_data_bnb5e19_20260227_171123.root",
}

# Open files & trees
tfiles = {}
trees  = {}
for sample in samples:
    tfiles[sample] = rt.TFile(files[sample])
    if tfiles[sample].IsZombie():
        raise RuntimeError(f"Could not open {files[sample]}")
    trees[sample] = tfiles[sample].Get("analysis_tree")
    print(f"sample={sample} has {trees[sample].GetEntries()} entries")

# Cuts
reco_cut   = "numuCC1piNpReco_is_target_1mu1piNproton==1"
signal_cut = "(numuCC1piNp_is_infv==1 && numuCC1piNp_is_target_cc_numu_1pi_nproton==1)"
misid_cut  = "(numuCC1piNp_is_infv==0 || numuCC1piNp_is_target_cc_numu_1pi_nproton==0)"

# Variables: (branch, nbins, xmin, xmax, "title;xtitle")
vars = [
    ("numuCC1piNpReco_delPTT",      25, -1.0,    1.0,   f"Reco #Delta p_{{TT}} ({targetpot:.2e} POT);#Delta p_{{TT}} (GeV/c)"),
    ("numuCC1piNpReco_pN",          25,  0.0,    1.6,   f"Reco p_{{N}} ({targetpot:.2e} POT);p_{{N}} (GeV/c)"),
    ("numuCC1piNpReco_delAlphaT",   10,  0.0,  180.0,   f"Reco #Delta#alpha_{{T}} ({targetpot:.2e} POT);#Delta#alpha_{{T}} (deg)"),
    ("numuCC1piNpReco_muKE",        25,  0.0, 1500.0,   f"Reco Muon KE ({targetpot:.2e} POT);Muon KE (MeV)"),
    ("numuCC1piNpReco_maxprotonKE", 25,  0.0,  500.0,   f"Reco Max Proton KE ({targetpot:.2e} POT);Proton KE (MeV)"),
    ("numuCC1piNpReco_pionKE",      25,  0.0,  500.0,   f"Reco Pion KE ({targetpot:.2e} POT);Pion KE (MeV)"),
]

# Truth branch for efficiency denominator
truth_var = {
    "numuCC1piNpReco_delPTT":      "numuCC1piNp_delPTT",
    "numuCC1piNpReco_pN":          "numuCC1piNp_pN",
    "numuCC1piNpReco_delAlphaT":   "numuCC1piNp_delAlphaT",
    "numuCC1piNpReco_muKE":        "numuCC1piNp_muonKE",
    "numuCC1piNpReco_maxprotonKE": "numuCC1piNp_protonKE",
    "numuCC1piNpReco_pionKE":      "numuCC1piNp_pionKE",
}

# Output
out_name = f"{lantern_dir}/organized_all_run_yamls/plots_run1/tki_run1_hists.root"
os.makedirs(os.path.dirname(out_name), exist_ok=True)
temp     = rt.TFile("temp.root", "recreate")
out_file = rt.TFile(out_name, "recreate")

legend_POT_string = f"Events per {targetpot:.3e} POT"

for var, nbins, xmin, xmax, htitle in vars:

    short       = var.replace("numuCC1piNpReco_", "")
    title_parts = htitle.split(";")
    xtitle      = title_parts[1] if len(title_parts) > 1 else ""

    print(f"\n{'='*80}\n=== {short} ===")
    temp.cd()

    hists          = {}
    hists_unscaled = {}  # unscaled copies for purity error — exactly as Zev does it

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

    # ── Fill each sample (scaled) + unscaled copy for MC samples ─────────────
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

        # Fill both scaled and unscaled from the same Draw call
        trees[sample].Draw(f"{var}>>{hname}",          weight_str, "goff")
        trees[sample].Draw(f"{var}>>{hname_unscaled}",  weight_str, "goff")

        # Scale only the main histogram — unscaled stays as raw weighted counts
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

    # ── Canvas 1: stacked data/MC plot ────────────────────────────────────────
    cname1  = f"c_{short}"
    canvas1 = rt.TCanvas(cname1, cname1, 800, 600)
    canvas1.SetTickx(1)
    canvas1.SetTicky(1)

    hstack = rt.THStack(f"hs_{short}", "")
    hstack.Add(hists["extbnb"])    # bottom
    hstack.Add(hists["numu_bg"])   # middle
    hstack.Add(hists["numu_sig"])  # top

    stack_max = hstack.GetMaximum()
    data_max  = hists["data"].GetMaximum()
    y_max     = max(stack_max, data_max) * 1.5

    if stack_max >= data_max:
        hstack.Draw("hist")
        hstack.SetMaximum(y_max)
        hstack.GetXaxis().SetTitle(xtitle)
        hstack.GetYaxis().SetTitle(legend_POT_string)
        hists["data"].Draw("E1 same")
    else:
        hists["data"].SetMaximum(y_max)
        hists["data"].GetXaxis().SetTitle(xtitle)
        hists["data"].GetYaxis().SetTitle(legend_POT_string)
        hists["data"].Draw("E1")
        hstack.Draw("hist same")
        hists["data"].Draw("E1 same")

    legend1 = rt.TLegend(0.55, 0.55, 0.89, 0.88)
    legend1.SetTextSize(0.032)
    legend1.SetFillStyle(0)
    legend1.SetBorderSize(1)
    legend1.AddEntry(hists["extbnb"],   f"BNB EXT ({hists['extbnb'].Integral():.1f})",    "f")
    legend1.AddEntry(hists["numu_bg"],  f"MC bkg ({hists['numu_bg'].Integral():.1f})",     "f")
    legend1.AddEntry(hists["numu_sig"], f"MC signal ({hists['numu_sig'].Integral():.1f})", "f")
    legend1.AddEntry(hists["data"],     f"Run1 Data ({int(hists['data'].Integral())})",    "lep")
    legend1.Draw()

    canvas1.Update()
    out_file.cd()
    canvas1.Write(cname1)

    # ── Canvas 2: purity + efficiency ─────────────────────────────────────────
    cname2  = f"c_{short}_pureff"
    canvas2 = rt.TCanvas(cname2, cname2, 800, 600)
    canvas2.SetTickx(1)
    canvas2.SetTicky(1)
    canvas2.SetGridx(1)
    canvas2.SetGridy(1)

    # Purity: numu_sig / (numu_sig + numu_bg + extbnb) per bin
    h_purity = hists["numu_sig"].Clone(f"h_{short}_purity")
    h_sum    = hists["numu_sig"].Clone(f"h_{short}_sum")
    h_sum.Add(hists["numu_bg"])
    h_sum.Add(hists["extbnb"])

    # Unscaled total MC for error calculation (Zev's approach)
    h_sum_unscaled = hists_unscaled["numu_sig"].Clone(f"h_{short}_sum_unscaled")
    h_sum_unscaled.Add(hists_unscaled["numu_bg"])

    overall_purity = hists["numu_sig"].Integral() / h_sum.Integral() if h_sum.Integral() > 0 else 0
    h_purity.Divide(h_sum)

    # Purity error: sqrt(p*(1-p)/N) where N = unscaled total MC count (Zev's formula)
    for ibin in range(1, h_purity.GetNbinsX() + 1):
        p               = h_purity.GetBinContent(ibin)
        n_total_unscaled = h_sum_unscaled.GetBinContent(ibin)
        if n_total_unscaled > 0:
            purity_error = sqrt(p * (1 - p) / n_total_unscaled)
        else:
            purity_error = 0.0
        h_purity.SetBinError(ibin, purity_error)

    # Efficiency: effnum / effdenom — ROOT handles errors via Sumw2
    h_eff = hists["effnum"].Clone(f"h_{short}_eff")
    overall_eff = hists["effnum"].Integral() / hists["effdenom"].Integral() if hists["effdenom"].Integral() > 0 else 0
    h_eff.Divide(hists["effdenom"])

    # Style: blue purity, red efficiency
    h_purity.SetLineColor(rt.kBlue)
    h_purity.SetMarkerColor(rt.kBlue)
    h_purity.SetMarkerStyle(20)
    h_purity.SetMarkerSize(0.8)
    h_purity.SetLineWidth(2)

    h_eff.SetLineColor(rt.kRed)
    h_eff.SetMarkerColor(rt.kRed)
    h_eff.SetMarkerStyle(21)
    h_eff.SetMarkerSize(0.8)
    h_eff.SetLineWidth(2)

    h_purity.SetTitle(f"Run 1: TKI;{xtitle};Purity / Efficiency")
    h_purity.GetYaxis().SetRangeUser(0.0, 1.1)
    h_purity.Draw("E1")
    h_eff.Draw("E1 same")

    # Dashed reference line at 1.0
    line = rt.TLine(xmin, 1.0, xmax, 1.0)
    line.SetLineStyle(2)
    line.SetLineColor(rt.kGray + 2)
    line.Draw()

    # Small legend, upper middle
    legend2 = rt.TLegend(0.35, 0.75, 0.65, 0.88)
    legend2.SetTextSize(0.025)
    legend2.SetFillStyle(0)
    legend2.SetBorderSize(1)
    legend2.AddEntry(h_purity, f"Purity (avg: {overall_purity:.3f})",  "lep")
    legend2.AddEntry(h_eff,    f"Efficiency (avg: {overall_eff:.3f})", "lep")
    legend2.Draw()

    print(f"  Overall purity: {overall_purity:.3f},  efficiency: {overall_eff:.3f}")

    canvas2.Update()
    out_file.cd()
    canvas2.Write(cname2)
    temp.cd()

out_file.Close()
temp.Close()
print(f"\nSaved -> {out_name}")

for f in tfiles.values():
    f.Close()