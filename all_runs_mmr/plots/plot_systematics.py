#!/usr/bin/env python3
"""
Overlay systematic error histograms from multiple ROOT files,
producing one canvas per uncertainty type (flux, stats, xsec, reint, detector).
"""

import ROOT
import sys

# Configure ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

# Define your ROOT files and labels
lantern_dir = "/exp/uboone/app/users/imani/lantern_ana/"
files_info = [
    {"path": f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run1_hists.root",         "label": "Run 1", "color": ROOT.kYellow+1},
    {"path": f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run3mil_hists.root",      "label": "Run 3", "color": ROOT.kRed},
    {"path": f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run4_combined_hists.root", "label": "Run 4", "color": ROOT.kBlue},
    {"path": f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run5_hists.root",          "label": "Run 5", "color": ROOT.kGreen+2},
]

# Uncertainty types to loop over
uncertainty_types = ["flux", "stats", "xsec", "reint", "detector", "stat"]

# Histogram name pattern — one canvas object per type in each ROOT file
HIST_PATTERN = "c_neutrino_energy_frac_{utype};1"

# Axis labels and titles
X_TITLE = "Neutrino Energy (GeV)"
Y_TITLE = "Fractional Uncertainty"
Y_MAX   = 0.2   # fixed upper y-axis limit; set to None to use data-driven maximum

# Output ROOT file
output_dir = f"{lantern_dir}/all_runs_mmr/plots/numu/"
output_root = f"{output_dir}/systematic_comparison_by_type.root"
out_file = ROOT.TFile(output_root, "RECREATE")

all_canvases = []  # keep alive until written

for utype in uncertainty_types:
    tmp_name = utype
    hist_name = HIST_PATTERN.format(utype=utype)
    print(f"\n{'='*60}")
    print(f"Processing uncertainty type: {utype}  ({hist_name})")
    print(f"{'='*60}")

    histograms  = []   # (hist_clone, file_info) pairs
    open_files  = []   # TFile handles — closed after cloning

    # ── Load histograms ──────────────────────────────────────────
    for i, file_info in enumerate(files_info):
        print(f"  Opening {file_info['path']}")
        tfile = ROOT.TFile.Open(file_info['path'])

        if not tfile or tfile.IsZombie():
            print(f"  ERROR: Cannot open file — skipping {file_info['label']}")
            continue

        obj = tfile.Get(hist_name)

        if not obj:
            print(f"  ERROR: Cannot find '{hist_name}' — skipping {file_info['label']}")
            tfile.Close()
            continue

        # Unwrap TCanvas if needed
        if obj.InheritsFrom("TCanvas"):
            print(f"  Found TCanvas, extracting histogram...")
            hist = None
            for primitive in obj.GetListOfPrimitives():
                if primitive.InheritsFrom("TH1"):
                    hist = primitive
                    break
            if not hist:
                print(f"  ERROR: No TH1 found inside canvas — skipping {file_info['label']}")
                tfile.Close()
                continue
        else:
            hist = obj

        # Clone so it survives after the file closes
        clone_name = f"h_{utype}_{i}"
        hist_clone = hist.Clone(clone_name)
        hist_clone.SetDirectory(0)

        # Style
        hist_clone.SetLineColor(file_info['color'])
        hist_clone.SetLineWidth(3)
        hist_clone.SetMarkerSize(0)

        histograms.append((hist_clone, file_info))
        tfile.Close()
        print(f"  Loaded: {hist_clone.GetNbinsX()} bins")

    if not histograms:
        print(f"  WARNING: No histograms loaded for '{utype}' — skipping canvas")
        continue

    # ── Build canvas ─────────────────────────────────────────────
    canvas_name  = f"c_comparison_{utype}"
    canvas_title = f"Fractional Uncertainty: {tmp_name}"
    canvas = ROOT.TCanvas(canvas_name, canvas_title, 800, 600)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.05)
    canvas.SetBottomMargin(0.12)
    canvas.cd()

    # Legend
    legend = ROOT.TLegend(0.6, 0.7, 0.88, 0.88)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)

    # Data-driven y-max (used when Y_MAX is None)
    y_max_data = max(h.GetMaximum() for h, _ in histograms) * 1.2

    for i, (hist, file_info) in enumerate(histograms):
        legend.AddEntry(hist, file_info['label'], "l")

        if i == 0:
            hist.SetTitle(canvas_title)
            hist.GetXaxis().SetTitle(X_TITLE)
            hist.GetYaxis().SetTitle(Y_TITLE)
            hist.SetMinimum(0)
            hist.SetMaximum(Y_MAX if Y_MAX is not None else y_max_data)
            hist.Draw("HIST")
        else:
            hist.Draw("HIST SAME")

    legend.Draw()
    canvas.Update()

    # Write canvas + individual histograms into output ROOT file
    out_file.cd()
    canvas.Write()
    for hist, _ in histograms:
        hist.Write()

    all_canvases.append((canvas, histograms))  # prevent GC
    print(f"  Written canvas '{canvas_name}' to {output_root}")

out_file.Close()
print(f"\nDone. All canvases saved to '{output_root}'")