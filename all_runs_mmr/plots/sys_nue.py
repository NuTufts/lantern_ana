#!/usr/bin/env python3
"""
Overlay systematic error histograms from multiple ROOT files,
producing one canvas per uncertainty type (flux, stats, xsec, reint, detector).

Supports three extraction modes for systematic canvases:
  - "total"   : find the histogram whose name/title contains 'total' (case-insensitive)
  - "param"   : find a specific named histogram, e.g. 'xsr_scc_Fa3_SCC'
  - "first"   : legacy behaviour — take the first TH1 found in the canvas

Also overlays purity and efficiency canvases across runs.
"""

import ROOT
import sys

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

lantern_dir = "/exp/uboone/app/users/imani/lantern_ana/"

files_info = [
    {"path": f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run1_hists.root",          "label": "Run 1", "color": ROOT.kYellow+1, "run_num": 1},
    {"path": f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run3_hists.root",          "label": "Run 3", "color": ROOT.kRed,       "run_num": 3},
    {"path": f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run4_combined_hists.root", "label": "Run 4", "color": ROOT.kBlue,      "run_num": 4},
    {"path": f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run5_hists.root",          "label": "Run 5", "color": ROOT.kGreen+2,   "run_num": 5},
]

# ── Systematic uncertainty extraction ────────────────────────────────────────
# Mode options:
#   "total"  → histogram whose name/title contains 'total' (case-insensitive)
#   "param"  → histogram matching PARAM_NAME exactly (name or title)
#   "first"  → first TH1 found (legacy)
EXTRACT_MODE = "total"
PARAM_NAME   = "xsr_scc_Fa3_SCC"   # only used when EXTRACT_MODE == "param"

uncertainty_types = ["flux", "stats", "xsec", "reint", "detector", "stat"]
SYS_HIST_PATTERN  = "c_neutrino_energy_{{run_num}}_frac_{utype};1"

# Histogram names inside each systematic canvas.
# stat uses the _draw histogram; all others use the _agg aggregate.
SYS_AGG_PATTERN  = "h_frac_{utype}_neutrino_energy_agg"   # total/aggregate line
SYS_DRAW_PATTERN = "h_frac_{utype}_neutrino_energy_draw"  # used for stat only

# Human-readable names for canvas titles
UTYPE_DISPLAY = {
    "flux":     "Flux",
    "stats":    "Statistical",
    "stat":     "Statistical",
    "xsec":     "Cross Section",
    "reint":    "Reinteraction",
    "detector": "Detector",
}

# ── Purity / efficiency canvases ─────────────────────────────────────────────
# Set to None to skip that section entirely.
PURITY_CANVAS_NAME     = "c_neutrino_energy_{run_num}_purity;1"
EFFICIENCY_CANVAS_NAME = "c_neutrino_energy_{run_num}_efficiency;1"

# ── Data / prediction ratio ───────────────────────────────────────────────────
# Subplot canvas that already contains the precomputed ratio and its uncertainty.
DATAPRED_CANVAS_NAME = "c_neutrino_energy_{run_num};1"
RATIO_HIST_NAME      = "h_ratio_neutrino_energy"      # central ratio values
RATIO_UNC_HIST_NAME  = "h_ratio_unc_neutrino_energy"  # uncertainty envelope

X_TITLE_RATIO = "True Neutrino Energy (GeV)"
Y_TITLE_RATIO = "Data / Pred"
Y_MIN_RATIO   = 0.5
Y_MAX_RATIO   = 1.5

# ── Axis / style ─────────────────────────────────────────────────────────────
X_TITLE_SYS  = "Reco Nue Energy (GeV)"
Y_TITLE_SYS  = "Fractional Uncertainty"
Y_MAX_SYS    = 0.2          # None → data-driven

X_TITLE_PUR  = "Reco Nue Energy (GeV)"
Y_TITLE_PUR  = "Purity"
Y_MAX_PUR    = 1.05         # None → data-driven

X_TITLE_EFF  = "True Nue Energy (GeV)"
Y_TITLE_EFF  = "Efficiency"
Y_MAX_EFF    = 1.05         # None → data-driven

# ── Output ────────────────────────────────────────────────────────────────────
output_dir  = f"{lantern_dir}/all_runs_mmr/plots/nue/"
output_root = f"{output_dir}/sys_comp_nue.root"


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def primitives_of_type(canvas, root_class="TH1"):
    """Yield all primitives in *canvas* that inherit from *root_class*."""
    for prim in canvas.GetListOfPrimitives():
        if prim.InheritsFrom(root_class):
            yield prim


def find_hist_total(canvas):
    """Return the first TH1 whose name or title contains 'total' (case-insensitive).
    Only warns if there are multiple histograms and none matches 'total'."""
    for h in primitives_of_type(canvas):
        if "total" in h.GetName().lower() or "total" in h.GetTitle().lower():
            return h
    histograms = list(primitives_of_type(canvas))
    if not histograms:
        return None
    # Single histogram — use it silently (no 'total' label expected)
    if len(histograms) == 1:
        return histograms[0]
    # Multiple histograms but none named 'total' — warn and take the last
    print(f"    WARNING: No 'total' histogram found among {len(histograms)} — "
          f"falling back to last TH1 '{histograms[-1].GetName()}'")
    return histograms[-1]


def find_hist_param(canvas, param_name):
    """Return the TH1 whose name or title matches *param_name* exactly."""
    for h in primitives_of_type(canvas):
        if h.GetName() == param_name or h.GetTitle() == param_name:
            return h
    print(f"    WARNING: Parameter '{param_name}' not found in canvas '{canvas.GetName()}'")
    print(f"    Available histograms:")
    for h in primitives_of_type(canvas):
        print(f"      name='{h.GetName()}'  title='{h.GetTitle()}'")
    return None


def find_hist_first(canvas):
    """Return the first TH1 in the canvas (legacy behaviour)."""
    for h in primitives_of_type(canvas):
        return h
    return None


def find_hist_by_name(canvas, hist_name):
    """Return the TH1 matching *hist_name* exactly, with a helpful fallback."""
    for h in primitives_of_type(canvas):
        if h.GetName() == hist_name:
            return h
    # Not found — print available names to aid debugging
    available = [h.GetName() for h in primitives_of_type(canvas)]
    print(f"    WARNING: '{hist_name}' not found in canvas '{canvas.GetName()}'")
    print(f"    Available: {available}")
    return None


def merge_overflow(h):
    """
    Add the overflow bin's content and error into the last visible bin,
    then zero the overflow bin.  Call this after cloning and before drawing.
    """
    n = h.GetNbinsX()
    last_content  = h.GetBinContent(n) + h.GetBinContent(n + 1)
    last_error    = (h.GetBinError(n)**2 + h.GetBinError(n + 1)**2) ** 0.5
    h.SetBinContent(n,     last_content)
    h.SetBinError(n,       last_error)
    h.SetBinContent(n + 1, 0.0)
    h.SetBinError(n + 1,   0.0)


def extract_hist_from_canvas(canvas, mode, param_name=None):
    """
    Dispatch to the appropriate extractor based on *mode*.
    Returns a TH1 or None.
    """
    if mode == "total":
        return find_hist_total(canvas)
    elif mode == "param":
        return find_hist_param(canvas, param_name)
    elif mode == "first":
        return find_hist_first(canvas)
    else:
        raise ValueError(f"Unknown EXTRACT_MODE '{mode}'. Choose 'total', 'param', or 'first'.")


def load_hists_from_canvas_name(canvas_name, extract_fn, label_suffix=""):
    """
    For each entry in *files_info*, open the file, find *canvas_name*,
    extract a histogram via *extract_fn(canvas)*, clone it, and style it.

    Returns list of (hist_clone, file_info).
    """
    histograms = []
    for i, file_info in enumerate(files_info):
        resolved_canvas_name = canvas_name.format(run_num=file_info.get('run_num', ''))

        tfile = ROOT.TFile.Open(file_info["path"])
        if not tfile or tfile.IsZombie():
            print(f"  ERROR: Cannot open '{file_info['path']}' — skipping {file_info['label']}")
            continue

        obj = tfile.Get(resolved_canvas_name)
        if not obj:
            print(f"  ERROR: Object '{resolved_canvas_name}' not found in {file_info['label']} — skipping")
            tfile.Close()
            continue

        # Unwrap TCanvas
        if obj.InheritsFrom("TCanvas"):
            hist = extract_fn(obj)
        elif obj.InheritsFrom("TH1"):
            hist = obj
        else:
            print(f"  ERROR: Object '{resolved_canvas_name}' is neither TCanvas nor TH1 — skipping {file_info['label']}")
            tfile.Close()
            continue

        if hist is None:
            tfile.Close()
            continue

        clone_name = f"h_{resolved_canvas_name.split(';')[0]}_{label_suffix}_{i}"
        hist_clone = hist.Clone(clone_name)
        hist_clone.SetDirectory(0)
        hist_clone.SetLineColor(file_info["color"])
        hist_clone.SetLineWidth(3)
        hist_clone.SetMarkerSize(0)

        histograms.append((hist_clone, file_info))
        print(f"  Loaded '{hist.GetName()}' ({hist_clone.GetNbinsX()} bins) from {file_info['label']}")
        tfile.Close()

    return histograms


def extract_average_from_latex(canvas):
    """
    Scan all primitives in *canvas* for a TLatex object whose text contains
    a trailing float (e.g. "Average Purity: 0.847" or "Average Efficiency: 0.234").
    Returns the float, or None if no matching TLatex is found.
    """
    import re
    for prim in canvas.GetListOfPrimitives():
        if prim.InheritsFrom("TLatex"):
            m = re.search(r"[-+]?\d*\.\d+", prim.GetTitle())
            if m:
                return float(m.group())
    return None


def integral_average(hist):
    """
    Fallback average: simple mean of per-bin ratio values over filled bins.
    Used only when the canvas does not contain pre-stored integral components.
    """
    n_filled     = sum(1 for b in range(1, hist.GetNbinsX() + 1)
                       if hist.GetBinContent(b) > 0)
    total_signal = hist.Integral()
    if n_filled == 0:
        return None
    return total_signal / n_filled


def make_overlay_canvas(histograms, canvas_name, canvas_title,
                        x_title, y_title, y_max=None,
                        draw_mode="HIST", averages=None):
    """
    Build and return a styled TCanvas overlaying all histograms in *histograms*.
    *histograms* is a list of (TH1, file_info) pairs.

    draw_mode : "HIST"   → solid lines (systematics)
                "PE"     → dots with error bars (purity / efficiency)
    averages  : optional list of floats (one per histogram) providing pre-computed
                event-weighted averages for the legend.  When None, falls back to
                integral_average(hist).  Pass when the canvas stores _numer_int /
                _denom_int histograms written by plot_nue_hists.py.
    """
    canvas = ROOT.TCanvas(canvas_name, canvas_title, 800, 600)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.05)
    canvas.SetBottomMargin(0.12)
    canvas.cd()

    legend = ROOT.TLegend(0.6, 0.7, 0.88, 0.88)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)

    y_max_data = max(h.GetMaximum() for h, _ in histograms) * 1.2
    y_limit    = y_max if y_max is not None else y_max_data

    for i, (hist, file_info) in enumerate(histograms):

        if draw_mode == "PE":
            # Style for dots-with-error-bars
            hist.SetMarkerColor(file_info["color"])
            hist.SetMarkerStyle(20)   # filled circle
            hist.SetMarkerSize(0.7)
            hist.SetLineColor(file_info["color"])
            hist.SetLineWidth(2)

            # Compute average and append to legend label
            avg = (averages[i] if averages is not None and averages[i] is not None
                   else integral_average(hist))
            avg_str = f"{avg:.3f}" if avg is not None else "n/a"
            legend_label = f"{file_info['label']} ({avg_str})"
            legend.AddEntry(hist, legend_label, "lep")

            first_opt = "PE"
            rest_opt  = "PE SAME"
        else:
            legend.AddEntry(hist, file_info["label"], "l")
            first_opt = "HIST"
            rest_opt  = "HIST SAME"

        if i == 0:
            hist.SetTitle(canvas_title)
            hist.GetXaxis().SetTitle(x_title)
            hist.GetYaxis().SetTitle(y_title)
            hist.SetMinimum(0)
            hist.SetMaximum(y_limit)
            hist.Draw(first_opt)
        else:
            hist.Draw(rest_opt)

    # HIST mode: autoscale y to actual data max after all histograms are drawn
    if draw_mode == "HIST":
        canvas.Update()
        y_auto = max(h.GetMaximum() for h, _ in histograms) * 1.15
        histograms[0][0].SetMaximum(y_auto)

    # PE mode: dotted reference line at y = 1
    ref_line = None
    if draw_mode == "PE":
        x_min = histograms[0][0].GetXaxis().GetXmin()
        x_max = histograms[0][0].GetXaxis().GetXmax()
        ref_line = ROOT.TLine(x_min, 1.0, x_max, 1.0)
        ref_line.SetLineStyle(2)    # dashed/dotted
        ref_line.SetLineWidth(2)
        ref_line.SetLineColor(ROOT.kBlack)
        ref_line.Draw("SAME")

    legend.Draw()
    canvas.Update()
    return canvas, legend, ref_line   # return ref_line to prevent GC


def make_datapred_canvas(files_info, canvas_name_in_file,
                         ratio_hist_name, ratio_unc_hist_name):
    """
    For each run, load *ratio_hist_name* (central data/MC values) and
    *ratio_unc_hist_name* (total uncertainty envelope) from the precomputed
    ratio subplot canvas, then overlay all runs on one canvas with a dotted
    reference line at y=1.

    The uncertainty histogram's bin errors are used directly as the error bars;
    its bin contents supply the symmetric ± band width if bin errors are zero.

    Returns (canvas, legend, ref_line, ratio_hists) or None if nothing loaded.
    """
    ratio_hists = []

    for i, file_info in enumerate(files_info):
        resolved_canvas_name = canvas_name_in_file.format(run_num=file_info.get('run_num', ''))

        tfile = ROOT.TFile.Open(file_info["path"])
        if not tfile or tfile.IsZombie():
            print(f"  ERROR: Cannot open '{file_info['path']}' — skipping {file_info['label']}")
            continue

        obj = tfile.Get(resolved_canvas_name)
        if not obj:
            print(f"  ERROR: '{resolved_canvas_name}' not found in {file_info['label']} — skipping")
            tfile.Close()
            continue

        if not obj.InheritsFrom("TCanvas"):
            print(f"  ERROR: '{resolved_canvas_name}' is not a TCanvas in {file_info['label']} — skipping")
            tfile.Close()
            continue

        # Ratio histograms live in the second TPad primitive of the canvas
        pads = [p for p in obj.GetListOfPrimitives() if p.InheritsFrom("TPad")]
        if len(pads) < 2:
            print(f"  ERROR: expected at least 2 pads, found {len(pads)} in {file_info['label']} — skipping")
            tfile.Close()
            continue

        pad1 = pads[0]   # first pad — main energy spectrum
        pad2 = pads[1]   # second pad — ratio subplot

        h_data_raw  = find_hist_by_name(pad1, "h_neutrino_energy_data")
        h_ratio_raw = find_hist_by_name(pad2, ratio_hist_name)
        h_unc_raw   = find_hist_by_name(pad2, ratio_unc_hist_name)

        if h_ratio_raw is None:
            print(f"  ERROR: '{ratio_hist_name}' not found in {file_info['label']} — skipping")
            tfile.Close()
            continue

        # Clone before closing; data and uncertainty histograms are optional
        h_ratio = h_ratio_raw.Clone(f"h_datapred_{i}")
        h_ratio.SetDirectory(0)
        h_unc = h_unc_raw.Clone(f"h_datapred_unc_{i}") if h_unc_raw else None
        if h_unc:
            h_unc.SetDirectory(0)
        h_data_counts = h_data_raw.Clone(f"h_data_counts_{i}") if h_data_raw else None
        if h_data_counts:
            h_data_counts.SetDirectory(0)
        tfile.Close()

        # Apply uncertainty as bin errors on the ratio histogram.
        # Prefer GetBinError on the unc histogram; fall back to its bin content
        # (which some frameworks store as the absolute uncertainty value).
        if h_unc is not None:
            for b in range(1, h_ratio.GetNbinsX() + 1):
                unc_err  = h_unc.GetBinError(b)
                unc_cont = h_unc.GetBinContent(b)
                unc = unc_err if unc_err > 0 else unc_cont
                h_ratio.SetBinError(b, unc)

        # Style: coloured dots with error bars
        h_ratio.SetMarkerColor(file_info["color"])
        h_ratio.SetMarkerStyle(20)
        h_ratio.SetMarkerSize(0.7)
        h_ratio.SetLineColor(file_info["color"])
        h_ratio.SetLineWidth(2)

        ratio_hists.append((h_ratio, h_data_counts, file_info))
        print(f"  Loaded data/pred for {file_info['label']}  "
              f"(ratio integral={h_ratio.Integral():.3f}, "
              f"unc hist {'found' if h_unc else 'NOT FOUND'}, "
              f"data counts {'found' if h_data_counts else 'NOT FOUND'})")

    if not ratio_hists:
        return None

    # ── Canvas ────────────────────────────────────────────────────────────────
    canvas = ROOT.TCanvas("c_comparison_datapred", "Data / Prediction", 800, 600)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.05)
    canvas.SetBottomMargin(0.12)
    canvas.cd()

    legend = ROOT.TLegend(0.6, 0.7, 0.88, 0.88)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)

    for i, (h_ratio, _h_data_counts, file_info) in enumerate(ratio_hists):
        legend.AddEntry(h_ratio, file_info["label"], "lep")
        if i == 0:
            h_ratio.SetTitle("Data / Prediction")
            h_ratio.GetXaxis().SetTitle(X_TITLE_RATIO)
            h_ratio.GetYaxis().SetTitle(Y_TITLE_RATIO)
            h_ratio.SetMinimum(Y_MIN_RATIO)
            h_ratio.SetMaximum(Y_MAX_RATIO)
            h_ratio.Draw("PE")
        else:
            h_ratio.Draw("PE SAME")

    # Dotted reference line at y = 1
    x_min = ratio_hists[0][0].GetXaxis().GetXmin()
    x_max = ratio_hists[0][0].GetXaxis().GetXmax()
    ref_line = ROOT.TLine(x_min, 1.0, x_max, 1.0)
    ref_line.SetLineStyle(2)
    ref_line.SetLineWidth(2)
    ref_line.SetLineColor(ROOT.kBlack)
    ref_line.Draw("SAME")

    legend.Draw()
    canvas.Update()
    return canvas, legend, ref_line, ratio_hists


def make_run_summary_canvas(ratio_hists):
    """
    Collapse each run's ratio histogram into a single event-weighted average
    and plot one point per run on a TGraphErrors vs. run label.

    Weights are the data event counts from h_neutrino_energy_data (pad 1).
    Falls back to equal weighting if the data histogram was not found.

    The error bar is the event-weighted mean of the per-bin uncertainties,
    matching the scale visible in the per-energy ratio overlay.

    ratio_hists : list of (TH1 ratio, TH1 data_counts, file_info)
    Returns (canvas, graph, ref_line) or None.
    """
    import array

    run_labels = []
    y_vals     = []
    y_errs     = []

    for h_ratio, h_data_counts, file_info in ratio_hists:
        sum_w    = 0.0
        sum_wy   = 0.0
        sum_werr = 0.0

        for b in range(1, h_ratio.GetNbinsX() + 1):
            val = h_ratio.GetBinContent(b)
            err = h_ratio.GetBinError(b)
            if val == 0.0:
                continue

            # Event count from data histogram as weight; fall back to 1
            if h_data_counts is not None:
                w = h_data_counts.GetBinContent(b)
                if w <= 0:
                    w = 1.0
            else:
                w = 1.0

            sum_w    += w
            sum_wy   += w * val
            sum_werr += w * err   # event-weighted sum of uncertainties

        if sum_w == 0:
            print(f"  WARNING: no filled bins for {file_info['label']} — skipping run point")
            continue

        combined_val = sum_wy   / sum_w   # event-weighted mean ratio
        combined_err = sum_werr / sum_w   # event-weighted mean uncertainty

        run_labels.append(file_info["label"])
        y_vals.append(combined_val)
        y_errs.append(combined_err)
        print(f"  {file_info['label']:6s}  ratio = {combined_val:.4f} ± {combined_err:.4f}")

    if not run_labels:
        return None

    n = len(run_labels)
    xs         = array.array("d", [i + 1 for i in range(n)])
    x_errs     = array.array("d", [0.0   for _ in range(n)])
    ys         = array.array("d", y_vals)
    y_errs_arr = array.array("d", y_errs)

    graph = ROOT.TGraphErrors(n, xs, ys, x_errs, y_errs_arr)
    graph.SetName("g_datapred_per_run")
    graph.SetTitle("")
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(1.2)
    graph.SetMarkerColor(ROOT.kBlack)
    graph.SetLineColor(ROOT.kBlack)
    graph.SetLineWidth(2)

    canvas = ROOT.TCanvas("c_datapred_per_run", "Data / Prediction per Run", 800, 600)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.08)
    canvas.SetBottomMargin(0.15)
    canvas.cd()

    # Use a TH1 frame so SetBinLabel works for x-axis run names
    frame = ROOT.TH1F("frame_datapred", "Data / Prediction per Run",
                      n + 2, 0.0, n + 2.0)
    frame.SetMinimum(Y_MIN_RATIO)
    frame.SetMaximum(Y_MAX_RATIO)
    frame.GetYaxis().SetTitle(Y_TITLE_RATIO)
    frame.GetXaxis().SetTitle("")
    frame.SetStats(0)
    # Blank out non-run bins; label the run bins
    for i in range(1, n + 3):
        frame.GetXaxis().SetBinLabel(i, "")
    for i, label in enumerate(run_labels):
        frame.GetXaxis().SetBinLabel(i + 2, label)   # bins are 1-indexed; bin i+2 centres on x=i+1.5
    frame.GetXaxis().SetLabelSize(0.055)
    frame.GetXaxis().LabelsOption("h")
    frame.Draw("AXIS")

    graph.Draw("P SAME")

    # Dotted reference line at y = 1
    ref_line = ROOT.TLine(0.0, 1.0, n + 2.0, 1.0)
    ref_line.SetLineStyle(2)
    ref_line.SetLineWidth(2)
    ref_line.SetLineColor(ROOT.kBlack)
    ref_line.Draw("SAME")

    # TLatex labels above each point: "val ± err"
    latex = ROOT.TLatex()
    latex.SetTextSize(0.032)
    latex.SetTextAlign(21)   # centred horizontally, bottom-aligned vertically
    latex.SetTextColor(ROOT.kBlack)
    y_range   = Y_MAX_RATIO - Y_MIN_RATIO
    label_offset = y_range * 0.06   # nudge above the error bar cap
    text_objects = []
    for i, (val, err, label) in enumerate(zip(y_vals, y_errs, run_labels)):
        x_pos   = xs[i]
        y_top   = val + y_errs_arr[i] + label_offset
        txt = latex.DrawLatex(x_pos, y_top, f"{val:.3f} #pm {err:.3f}")
        text_objects.append(txt)

    canvas.Update()
    return canvas, graph, ref_line, frame, latex, text_objects


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

out_file      = ROOT.TFile(output_root, "RECREATE")
all_objects   = []   # keep everything alive until out_file.Close()

# ── 1. Systematic uncertainty overlays ───────────────────────────────────────
print("\n" + "="*70)
print("SYSTEMATIC UNCERTAINTY OVERLAYS")
print("="*70)

mode_label = PARAM_NAME if EXTRACT_MODE == "param" else EXTRACT_MODE

for utype in uncertainty_types:
    hist_name    = SYS_HIST_PATTERN.format(utype=utype)
    display_name = UTYPE_DISPLAY.get(utype, utype.capitalize())

    # Choose the right histogram name inside the canvas
    if utype in ("stat", "stats"):
        inner_hist_name = SYS_DRAW_PATTERN.format(utype=utype)
    else:
        inner_hist_name = SYS_AGG_PATTERN.format(utype=utype)

    print(f"\n{'='*60}")
    print(f"  Uncertainty type : {utype}  ({display_name})")
    print(f"  Canvas name      : {hist_name}")
    print(f"  Histogram        : {inner_hist_name}")
    print(f"{'='*60}")

    def _extract(canvas, _hname=inner_hist_name, _mode=EXTRACT_MODE, _param=PARAM_NAME):
        if _mode == "param":
            return find_hist_param(canvas, _param)
        return find_hist_by_name(canvas, _hname)

    histograms = load_hists_from_canvas_name(hist_name, _extract, label_suffix=utype)

    if not histograms:
        print(f"  WARNING: No histograms loaded for '{utype}' — skipping")
        continue

    canvas_name  = f"c_comparison_{utype}"
    canvas_title = f"Fractional Uncertainty: {display_name}"
    canvas, legend, ref_line = make_overlay_canvas(
        histograms, canvas_name, canvas_title,
        X_TITLE_SYS, Y_TITLE_SYS, Y_MAX_SYS,
        draw_mode="HIST",
    )

    out_file.cd()
    canvas.Write()
    all_objects.append((canvas, legend, ref_line, histograms))
    print(f"  Written: '{canvas_name}'")


# ── 2. Purity overlays ────────────────────────────────────────────────────────
if PURITY_CANVAS_NAME is not None:
    print("\n" + "="*70)
    print("PURITY OVERLAYS")
    print("="*70)

    def _extract_pur(canvas):
        return find_hist_total(canvas)

    histograms = load_hists_from_canvas_name(
        PURITY_CANVAS_NAME, _extract_pur, label_suffix="purity"
    )

    # Merge overflow bin into the last visible bin for each run
    for h, _ in histograms:
        merge_overflow(h)

    # Read the average directly from the TLatex already on each run's canvas.
    pur_averages = []
    for file_info in [fi for fi in files_info
                      if any(fi is fi2 for _, fi2 in histograms)]:
        tfile = ROOT.TFile.Open(file_info["path"])
        avg = None
        if tfile and not tfile.IsZombie():
            resolved_name = PURITY_CANVAS_NAME.format(run_num=file_info.get('run_num', ''))
            obj = tfile.Get(resolved_name)
            if obj and obj.InheritsFrom("TCanvas"):
                avg = extract_average_from_latex(obj)
                if avg is None:
                    print(f"  NOTE: no TLatex average found in purity canvas for "
                          f"{file_info['label']} — falling back to bin-mean average")
            tfile.Close()
        pur_averages.append(avg)

    if histograms:
        canvas, legend, ref_line = make_overlay_canvas(
            histograms,
            canvas_name  = "c_comparison_purity",
            canvas_title = "CC Inclusive Nue Purity",
            x_title      = X_TITLE_PUR,
            y_title      = Y_TITLE_PUR,
            y_max        = Y_MAX_PUR,
            draw_mode    = "PE",
            averages     = pur_averages,
        )
        out_file.cd()
        canvas.Write()
        all_objects.append((canvas, legend, ref_line, histograms))
        print("  Written: 'c_comparison_purity'")
    else:
        print("  WARNING: No purity histograms found — skipping")


# ── 3. Efficiency overlays ────────────────────────────────────────────────────
if EFFICIENCY_CANVAS_NAME is not None:
    print("\n" + "="*70)
    print("EFFICIENCY OVERLAYS")
    print("="*70)

    def _extract_eff(canvas):
        return find_hist_total(canvas)

    histograms = load_hists_from_canvas_name(
        EFFICIENCY_CANVAS_NAME, _extract_eff, label_suffix="efficiency"
    )

    # Merge overflow bin into the last visible bin for each run
    for h, _ in histograms:
        merge_overflow(h)

    # Read the average directly from the TLatex already on each run's canvas.
    eff_averages = []
    for file_info in [fi for fi in files_info
                      if any(fi is fi2 for _, fi2 in histograms)]:
        tfile = ROOT.TFile.Open(file_info["path"])
        avg = None
        if tfile and not tfile.IsZombie():
            resolved_name = EFFICIENCY_CANVAS_NAME.format(run_num=file_info.get('run_num', ''))
            obj = tfile.Get(resolved_name)
            if obj and obj.InheritsFrom("TCanvas"):
                avg = extract_average_from_latex(obj)
                if avg is None:
                    print(f"  NOTE: no TLatex average found in efficiency canvas for "
                          f"{file_info['label']} — falling back to bin-mean average")
            tfile.Close()
        eff_averages.append(avg)

    if histograms:
        canvas, legend, ref_line = make_overlay_canvas(
            histograms,
            canvas_name  = "c_comparison_efficiency",
            canvas_title = "CC Inclusive Nue Efficiency",
            x_title      = X_TITLE_EFF,
            y_title      = Y_TITLE_EFF,
            y_max        = Y_MAX_EFF,
            draw_mode    = "PE",
            averages     = eff_averages,
        )
        out_file.cd()
        canvas.Write()
        all_objects.append((canvas, legend, ref_line, histograms))
        print("  Written: 'c_comparison_efficiency'")
    else:
        print("  WARNING: No efficiency histograms found — skipping")


# ── 4. Data / prediction ratio ────────────────────────────────────────────────
print("\n" + "="*70)
print("DATA / PREDICTION RATIO")
print("="*70)
print(f"  Canvas  : {DATAPRED_CANVAS_NAME}")
print(f"  Ratio   : {RATIO_HIST_NAME}")
print(f"  Uncert  : {RATIO_UNC_HIST_NAME}")

result = make_datapred_canvas(
    files_info,
    canvas_name_in_file = DATAPRED_CANVAS_NAME,
    ratio_hist_name     = RATIO_HIST_NAME,
    ratio_unc_hist_name = RATIO_UNC_HIST_NAME,
)

if result is not None:
    canvas, legend, ref_line, ratio_hists = result
    out_file.cd()
    canvas.Write()
    all_objects.append((canvas, legend, ref_line, ratio_hists))
    print("  Written: 'c_comparison_datapred'")

    # ── Per-run summary point ─────────────────────────────────────────────────
    print("\n  Building per-run summary...")
    summary = make_run_summary_canvas(ratio_hists)
    if summary is not None:
        s_canvas, s_graph, s_ref_line, s_frame, s_latex, s_texts = summary
        out_file.cd()
        s_canvas.Write()
        all_objects.append((s_canvas, s_graph, s_ref_line, s_frame, s_latex, s_texts))
        print("  Written: 'c_datapred_per_run'")
    else:
        print("  WARNING: Could not build per-run summary")
else:
    print("  WARNING: No data/pred ratios could be built — skipping")


out_file.Close()
print(f"\nDone. All canvases saved to '{output_root}'")