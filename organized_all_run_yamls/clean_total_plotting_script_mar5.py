import os, sys
import ROOT as rt
from math import sqrt

rt.gStyle.SetOptStat(0)

run_num = 1
lantern_dir = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana"

## Run 1
if run_num == 1:
    targetpot = 4.446e+19
    scaling = {
        "numu":   targetpot / 4.675690535431973e+20,
        "extbnb": 10375708.0 / 34202767.0,
        "data":   1.0
    }
    files = {
        "numu":   f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_bnb_nu_overlay_20260227_170113.root",
        "extbnb": f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_extbnb_mcc9_v29e_20260227_171017.root",
        "data":   f"{lantern_dir}/studies/numu_cc_tki/output_master_tki_run1/run1_data_bnb5e19_20260227_171123.root",
    }
    show_data   = True
    data_legend = "Run1 5e19"
    plot_title  = "Run 1: TKI"
    out_name    = f"{lantern_dir}/organized_all_run_yamls/plots_run1/tki_run1_hists.root"

TREE     = "analysis_tree"
base_cut = "numuCC1piNpReco_is_target_1mu1piNproton == 1"
legend_POT_string = f"Events per {targetpot:.3e} POT"

# ── Variables ──────────────────────────────────────────────────────────────────
# branch  →  (nbins, xmin, xmax, x-axis title)
variables = {
    "numuCC1piNpReco_delPTT":      (25,  -1.0,    1.0,  "#delta p_{TT} [GeV/c]"),
    "numuCC1piNpReco_pN":          (25,   0.0,    1.6,  "p_{N} [GeV/c]"),
    "numuCC1piNpReco_delAlphaT":   (10,   0.0,  180.0,  "#delta#alpha_{T} [deg]"),
    "numuCC1piNpReco_muKE":        (25,   0.0, 1500.0,  "Muon KE [MeV]"),
    "numuCC1piNpReco_maxprotonKE": (25,   0.0,  500.0,  "Max-proton KE [MeV]"),
    "numuCC1piNpReco_pionKE":      (25,   0.0,  500.0,  "Pion KE [MeV]"),
}

# ── Open files & trees ─────────────────────────────────────────────────────────
tfiles = {}
trees  = {}
samples = ["numu", "extbnb", "data"]
for sample in samples:
    tfiles[sample] = rt.TFile(files[sample])
    if tfiles[sample].IsZombie():
        raise RuntimeError(f"Could not open {files[sample]}")
    trees[sample] = tfiles[sample].Get(TREE)
    print(f"{sample}: {trees[sample].GetEntries()} entries")

# ── Output ROOT file ───────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(out_name), exist_ok=True)
out_file = rt.TFile(out_name, "recreate")

# ── Loop over variables ────────────────────────────────────────────────────────
for branch, (nbins, xmin, xmax, xtitle) in variables.items():

    short = branch.replace("numuCC1piNpReco_", "")
    print(f"\n=== {short} ===")

    hists = {}
    for sample in samples:
        hname = f"h_{short}_{sample}"

        h = rt.TH1D(hname, "", nbins, xmin, xmax)
        h.Sumw2()

        trees[sample].Draw(f"{branch}>>{hname}", base_cut, "goff")
        h.Scale(scaling[sample])

        print(f"  {sample}: {h.Integral():.1f} events")
        hists[sample] = h

    # ── Style ──────────────────────────────────────────────────────────────────
    hists["extbnb"].SetFillColor(rt.kGray + 2)
    hists["extbnb"].SetFillStyle(1001)
    hists["extbnb"].SetLineColor(rt.kGray + 2)

    hists["numu"].SetFillColor(rt.kAzure + 1)
    hists["numu"].SetFillStyle(1001)
    hists["numu"].SetLineColor(rt.kAzure + 1)

    hists["data"].SetMarkerStyle(20)
    hists["data"].SetMarkerSize(0.8)
    hists["data"].SetMarkerColor(rt.kBlack)
    hists["data"].SetLineColor(rt.kBlack)
    hists["data"].SetLineWidth(2)

    # ── Stack ──────────────────────────────────────────────────────────────────
    hstack = rt.THStack(f"hs_{short}", "")
    hstack.Add(hists["extbnb"])  # bottom
    hstack.Add(hists["numu"])    # top

    # ── Canvas ─────────────────────────────────────────────────────────────────
    canvas = rt.TCanvas(f"c_{short}", short, 800, 600)
    canvas.SetTickx(1)
    canvas.SetTicky(1)

    stack_max = hstack.GetMaximum()
    data_max  = hists["data"].GetMaximum() if show_data else 0
    y_max     = max(stack_max, data_max) * 1.5

    if stack_max >= data_max:
        hstack.Draw("hist")
        hstack.SetMaximum(y_max)
        hstack.GetXaxis().SetTitle(xtitle)
        hstack.GetYaxis().SetTitle(legend_POT_string)
        if show_data:
            hists["data"].Draw("E1 same")
    else:
        hists["data"].SetMaximum(y_max)
        hists["data"].GetXaxis().SetTitle(xtitle)
        hists["data"].GetYaxis().SetTitle(legend_POT_string)
        hists["data"].Draw("E1")
        hstack.Draw("hist same")
        hists["data"].Draw("E1 same")

    # ── Legend ─────────────────────────────────────────────────────────────────
    legend = rt.TLegend(0.65, 0.60, 0.89, 0.88)
    legend.SetTextSize(0.032)
    legend.SetFillStyle(0)
    legend.SetBorderSize(1)
    legend.AddEntry(hists["extbnb"], f"BNB EXT ({hists['extbnb'].Integral():.1f})", "f")
    legend.AddEntry(hists["numu"],   f"MC overlay ({hists['numu'].Integral():.1f})", "f")
    if show_data:
        legend.AddEntry(hists["data"], f"{data_legend} ({int(hists['data'].Integral())})", "lep")
    legend.Draw()

    canvas.Update()

    # Write canvas + histograms to ROOT file
    out_file.cd()
    canvas.Write()
    for h in hists.values():
        h.Write()

print(f"\nSaved ROOT file → {out_name}")
out_file.Close()

for f in tfiles.values():
    f.Close()