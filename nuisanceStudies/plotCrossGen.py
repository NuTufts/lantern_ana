"""
plot_crossgen_comparison.py

Cross-generator comparison of the 3 TKI variables (delPTT, pN, delAlphaT)
for GENIE, GiBUU, NEUT, NuWro. Truth-level only.

Usage:
    python3 plot_crossgen_comparison.py
"""

import array
import ROOT as rt

rt.gROOT.SetBatch(True)
rt.gStyle.SetOptStat(0)

# ── Bin edges (same as plot_tki_rebinned.py) ──────────────────────────────────
BIN_EDGES = {
    "numuCC1piNpReco_pN":          [0.0, 0.128, 0.192, 0.256, 0.32, 0.384, 0.448, 0.512, 0.576, 0.64, 0.768, 1.6],
    "numuCC1piNpReco_delPTT":      [-1.0, -0.36, -0.28, -0.2, -0.12, -0.04, 0.04, 0.12, 0.2, 0.28, 0.36, 1.0],
    "numuCC1piNpReco_delAlphaT":   [0.0, 18.0, 36.0, 54.0, 72.0, 90.0, 108.0, 126.0, 144.0, 162.0, 180.0],
    "numuCC1piNpReco_muKE":        [0.0, 60.0, 120.0, 180.0, 240.0, 300.0, 360.0, 420.0, 480.0, 540.0, 660.0, 1500.0],
    "numuCC1piNpReco_pionKE":      [0.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 220.0, 260.0, 500.0],
    "numuCC1piNpReco_maxprotonKE": [0.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 320.0, 360.0, 500.0],
}


def make_th1d(name, title, varname):
    edges     = BIN_EDGES[varname]
    edges_arr = array.array('d', edges)
    h = rt.TH1D(name, title, len(edges) - 1, edges_arr)
    h.SetDirectory(0)   # detach from any TFile so it survives tf.Close()
    h.Sumw2()
    return h


# ── Input files ────────────────────────────────────────────────────────────────
CROSSGEN_PATH = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/nuisanceStudies/cross_generator_tki_output"

CROSSGEN_FILES = {
    "GENIE": {"file": f"{CROSSGEN_PATH}/GENIE_tki.root", "color": rt.kRed,        "extra_scale": 1.0},
    "GiBUU": {"file": f"{CROSSGEN_PATH}/GiBUU_tki.root", "color": rt.kBlue,       "extra_scale": 1.0/250.0},
    "NEUT":  {"file": f"{CROSSGEN_PATH}/NEUT_tki.root",  "color": rt.kGreen + 2,  "extra_scale": 1.0},
    "NuWro": {"file": f"{CROSSGEN_PATH}/NuWro_tki.root", "color": rt.kMagenta + 1,"extra_scale": 1.0},
}

TRUTH_FLAG_BRANCH = "numuCC1piNp_is_target_cc_numu_1pi_nproton"

CROSSGEN_VARS = {
    "numuCC1piNpReco_delPTT":      ("numuCC1piNp_delPTT",    "#delta p_{TT}"),
    "numuCC1piNpReco_pN":          ("numuCC1piNp_pN",        "p_{N}"),
    "numuCC1piNpReco_delAlphaT":   ("numuCC1piNp_delAlphaT", "#delta#alpha_{T}"),
    "numuCC1piNpReco_muKE":        ("numuCC1piNp_muonKE",    "Muon Kinetic Energy"),
    "numuCC1piNpReco_maxprotonKE": ("numuCC1piNp_protonKE",  "Leading Proton Kinetic Energy"),
    "numuCC1piNpReco_pionKE":      ("numuCC1piNp_pionKE",    "Pion Kinetic Energy"),
}


# ─────────────────────────────────────────────────────────────────────────────
def fill_generator_histograms(label, cfg):
    tf = rt.TFile(cfg["file"])
    if not tf or tf.IsZombie():
        print(f"  ERROR: could not open {cfg['file']}")
        return None
    tree = tf.Get("analysis_tree")
    if not tree:
        print(f"  ERROR: no analysis_tree in {cfg['file']}")
        tf.Close()
        return None

    n_entries = tree.GetEntries()
    print(f"\n[{label}] {cfg['file']}  ({n_entries} entries)")

    hists = {}
    for bin_key in CROSSGEN_VARS:
        hists[bin_key] = make_th1d(f"h_crossgen_{label}_{bin_key}", "", bin_key)

    n_passed = 0
    for ientry in range(n_entries):
        tree.GetEntry(ientry)

        if getattr(tree, TRUTH_FLAG_BRANCH) != 1:
            continue
        n_passed += 1

        weight = tree.fScaleFactor * tree.Weight * cfg["extra_scale"]

        for bin_key, (branch, _) in CROSSGEN_VARS.items():
            hists[bin_key].Fill(getattr(tree, branch), weight)

    print(f"  {n_passed}/{n_entries} events passed signal selection")

    tf.Close()
    return hists


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    all_hists = {}
    for label, cfg in CROSSGEN_FILES.items():
        hists = fill_generator_histograms(label, cfg)
        if hists is not None:
            all_hists[label] = hists

    out_file = rt.TFile("output_crossgen_comparison.root", "recreate")

    for bin_key, (_, label_name) in CROSSGEN_VARS.items():
        short = bin_key.replace("numuCC1piNpReco_", "")

        canvas = rt.TCanvas(f"c_crossgen_{short}", f"c_crossgen_{short}", 800, 600)
        canvas.SetTickx(1)
        canvas.SetTicky(1)

        legend = rt.TLegend(0.60, 0.65, 0.89, 0.88)
        legend.SetTextSize(0.03)
        legend.SetFillStyle(1001)
        legend.SetFillColor(rt.kWhite)
        legend.SetBorderSize(1)

        drawn_hists = []
        max_val     = 0.0

        for label, cfg in CROSSGEN_FILES.items():
            if label not in all_hists:
                continue
            h = all_hists[label][bin_key]

            h.SetLineColor(cfg["color"])
            h.SetLineWidth(2)
            h.SetFillStyle(0)
            h.SetTitle(f"Cross-Generator Comparison: {label_name};{label_name};d#sigma/dX")

            drawn_hists.append(h)
            legend.AddEntry(h, label, "l")
            max_val = max(max_val, h.GetMaximum())

        if not drawn_hists:
            continue

        drawn_hists[0].SetMaximum(max_val * 1.3)
        drawn_hists[0].SetMinimum(0.0)
        drawn_hists[0].Draw("hist")
        for h in drawn_hists[1:]:
            h.Draw("hist same")

        legend.Draw()
        canvas.Update()

        out_file.cd()
        canvas.Write(f"c_crossgen_{short}")
        for h in drawn_hists:
            h.Write()

    out_file.Close()
    print(f"\nDone. Output written to: output_crossgen_comparison.root")