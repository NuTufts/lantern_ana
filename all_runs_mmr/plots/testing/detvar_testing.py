#!/usr/bin/env python3
"""
plot_detvar.py

Produces two ROOT canvases per variable for one run at a time, written to a
.root file in testing_detvar/:
  1. c_overlay_{varname}  — absolute detsys-variation overlays + Var/CV ratio panel
  2. c_frac_{varname}     — fractional error breakdown by source

Fractional variance is computed at native histogram resolution (mirroring
load_detector_variations in plot_numu.py), then rebinned to 0.1-GeV bins for
display.  No matplotlib, no PNG intermediates — pure ROOT TH1/TCanvas.

Usage: set run_num below, then run directly.
"""

import os
import sys
import numpy as np
import ROOT as rt
from math import sqrt

rt.gROOT.SetBatch(True)
rt.gStyle.SetOptStat(0)
rt.gStyle.SetPadTickX(1)
rt.gStyle.SetPadTickY(1)
rt.gErrorIgnoreLevel = rt.kWarning

# ─────────────────────────────────────────────────────────────────────────────
# RUN SELECTION  ← change this
# ─────────────────────────────────────────────────────────────────────────────
run_num = 5

lantern_dir = "/exp/uboone/app/users/imani/lantern_ana/all_runs_mmr"

# ─────────────────────────────────────────────────────────────────────────────
# DETSYS PARAM COLOR TABLE
# ─────────────────────────────────────────────────────────────────────────────
# Hex strings are unambiguous — avoid PyROOT float/UChar_t overload confusion
_PARAM_COLORS_HEX = {
	"LYAtt":          "#1f77b4",  # blue
	"LYDown":         "#ff7f0e",  # orange
	"LYRayleigh":     "#2ca02c",  # green
	"wiremodX":       "#d62728",  # red
	"wiremodYZ":      "#9467bd",  # purple
	"wiremodThetaXZ": "#8c564b",  # brown
	"wiremodThetaYZ": "#e377c2",  # pink
	"recomb2":        "#7f7f7f",  # gray
	"SCE":            "#bcbd22",  # yellow-green
}

PARAM_LABELS = {
	"LYAtt":          "LYAtt",
	"LYDown":         "LYDown",
	"LYRayleigh":     "LYRayleigh",
	"wiremodX":       "WireModX",
	"wiremodYZ":      "WireModYZ",
	"wiremodThetaXZ": "WireModThetaXZ",
	"wiremodThetaYZ": "WireModThetaYZ",
	"recomb2":        "Recomb2",
	"SCE":            "SCE",
}

# xsecflux category hex colors
_FLUX_COLOR  = "#1f77b4"  # blue
_REINT_COLOR = "#ff7f0e"  # orange
_GENIE_COLOR = "#2ca02c"  # green

def param_color(param):
	"""Return a ROOT color index for the given param name."""
	if param in _PARAM_COLORS_HEX:
		return rt.TColor.GetColor(_PARAM_COLORS_HEX[param])
	return rt.kBlack

# ─────────────────────────────────────────────────────────────────────────────
# XSECFLUX PARAMETER LISTS
# ─────────────────────────────────────────────────────────────────────────────
_flux_params_individual = [
	"expskin_FluxUnisim", "horncurrent_FluxUnisim",
	"nucleoninexsec_FluxUnisim", "nucleonqexsec_FluxUnisim",
	"nucleontotxsec_FluxUnisim", "pioninexsec_FluxUnisim",
	"pionqexsec_FluxUnisim", "piontotxsec_FluxUnisim",
	"kminus_PrimaryHadronNormalization", "kplus_PrimaryHadronFeynmanScaling",
	"kzero_PrimaryHadronSanfordWang",
	"piminus_PrimaryHadronSWCentralSplineVariation",
	"piplus_PrimaryHadronSWCentralSplineVariation",
]
_reint_params_individual = [
	"reinteractions_piminus_Geant4",
	"reinteractions_piplus_Geant4",
	"reinteractions_proton_Geant4",
]
_genie_params = [
	"All_UBGenie",
	"XSecShape_CCMEC_UBGenie", "RPA_CCQE_UBGenie",
	"AxFFCCQEshape_UBGenie", "VecFFCCQEshape_UBGenie",
	"DecayAngMEC_UBGenie", "xsr_scc_Fa3_SCC", "xsr_scc_Fv3_SCC",
	"NormCCCOH_UBGenie", "NormNCCOH_UBGenie",
	"ThetaDelta2NRad_UBGenie", "Theta_Delta2Npi_UBGenie",
]

# ─────────────────────────────────────────────────────────────────────────────
# PER-RUN CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
if run_num == 1:
	detsys_file     = f"{lantern_dir}/run1/root_files/detsys_final/combined_run1_nu_CV.root"
	xsecflux_file   = f"{lantern_dir}/run1/root_files/xsecflux/xsecflux_numu_nu.root"
	xsecflux_sample = "run1_nu"
	plot_title      = "Run 1: CC Inclusive #nu_{#mu}"
	use_agg_flux    = False
	use_agg_reint   = False

elif run_num == 3:
	detsys_file     = f"{lantern_dir}/run3mil/root_files/detsys_final/combined_run3mil_nu_CV.root"
	xsecflux_file   = f"{lantern_dir}/run3mil/root_files/xsecflux/xsecflux_numu_nu.root"
	xsecflux_sample = "run3mil_nu"
	plot_title      = "Run 3: CC Inclusive #nu_{#mu}"
	use_agg_flux    = False
	use_agg_reint   = False

elif run_num == 4:
	detsys_file     = f"{lantern_dir}/run4b/root_files/detsys_final/detsys_cv_run4b_nu_cv.root"
	xsecflux_file   = f"{lantern_dir}/run4b/root_files/xsecflux/xsecflux_numu_nu.root"
	xsecflux_sample = "run4b_nu"
	plot_title      = "Run 4b: CC Inclusive #nu_{#mu}"
	use_agg_flux    = True
	use_agg_reint   = True

elif run_num == 5:
	detsys_file     = f"{lantern_dir}/run5/root_files/detsys/detsys_cv_run5_nu_cv.root"
	xsecflux_file   = f"{lantern_dir}/run5/root_files/xsecflux/xsecflux_numu_nu.root"
	xsecflux_sample = "run5_nu"
	plot_title      = "Run 5: CC Inclusive #nu_{#mu}"
	use_agg_flux    = True
	use_agg_reint   = True

else:
	raise ValueError(f"Unsupported run_num={run_num}")

detsys_variables = ['reco_neutrino_energy']
detsys_params = [
	"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ",
	"LYAtt", "LYDown", "LYRayleigh", "recomb2", "SCE",
]

# Output ROOT file in testing_detvar/
out_dir = f"{lantern_dir}/plots/numu/testing_detvar"
os.makedirs(out_dir, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY: TH1 → numpy (MeV → GeV on edges)
# ─────────────────────────────────────────────────────────────────────────────
def th1_to_arrays(h):
	"""Return (bin_edges_GeV, bin_contents). X-axis divided by 1000 (MeV→GeV)."""
	nb = h.GetNbinsX()
	edges    = np.array([h.GetBinLowEdge(i) for i in range(1, nb + 2)]) / 1000.0
	contents = np.array([h.GetBinContent(i) for i in range(1, nb + 1)])
	return edges, contents

# ─────────────────────────────────────────────────────────────────────────────
# TARGET BINNING: 20 bins × 0.1 GeV = 0–2 GeV
# ─────────────────────────────────────────────────────────────────────────────
_NBINS = 20
_XMIN  = 0.0
_XMAX  = 2.0

def _make_target_th1(name, title=""):
	"""Allocate an empty TH1D with the standard 0–2 GeV, 0.1-GeV binning."""
	h = rt.TH1D(name, title, _NBINS, _XMIN, _XMAX)
	h.SetDirectory(0)
	h.GetXaxis().SetTitle("Reco Neutrino Energy (GeV)")
	return h

def rebin_into_th1(name, src_edges, src_vals, mode='sum', title=""):
	"""
	Create a TH1D in the target binning filled from (src_edges, src_vals).
	mode='sum'  — sum source bin contents per target bin  (counts, variances)
	mode='mean' — average source bin contents per target bin (fractional quantities)
	"""
	h = _make_target_th1(name, title)
	src_centers = 0.5 * (src_edges[:-1] + src_edges[1:])
	for ibin in range(1, _NBINS + 1):
		lo   = h.GetBinLowEdge(ibin)
		hi   = lo + h.GetBinWidth(ibin)
		mask = (src_centers >= lo) & (src_centers < hi)
		if mask.any():
			val = src_vals[mask].sum() if mode == 'sum' else src_vals[mask].mean()
			h.SetBinContent(ibin, val)
	return h

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DETSYS — mirrors load_detector_variations in plot_numu.py
#
# Key: compute frac_diff = (var - cv) / cv at *native* resolution, accumulate
# frac_diff² in quadrature, THEN rebin to the target GeV binning.
# ─────────────────────────────────────────────────────────────────────────────
def load_detsys(detsys_file, varname, params):
	"""
	Returns dict:
	  'h_cv'        — TH1D, detsys CV in target GeV binning (sum-rebinned)
	  'h_vars'      — {param: TH1D}, variation counts in target GeV binning
	  'h_frac_var'  — TH1D, total fractional variance (sum of frac_diff²),
	                  target GeV binning; take sqrt per bin for fractional unc.
	  'h_frac_each' — {param: TH1D}, |frac_diff| per param, target GeV binning
	"""
	f = rt.TFile(detsys_file)
	if f.IsZombie():
		print(f"ERROR: Cannot open {detsys_file}")
		return {}

	# Find a reference CV histogram at native resolution
	h_ref_raw = None
	for param in params:
		h_temp = f.Get(f"h{varname}__{param}__cv")
		if h_temp and not h_temp.IsZombie():
			h_temp.SetDirectory(0)
			h_ref_raw = h_temp
			break

	if h_ref_raw is None:
		print(f"  WARNING: No CV histogram found for '{varname}' in {detsys_file}")
		f.Close()
		return {}

	ref_edges, ref_cv = th1_to_arrays(h_ref_raw)
	nb_native = len(ref_cv)

	# Accumulate fractional variance at native resolution (bin-by-bin, quadrature)
	frac_var_native = np.zeros(nb_native)

	h_vars_rebinned = {}
	h_frac_each     = {}
	n_loaded = 0

	for param in params:
		h_cv  = f.Get(f"h{varname}__{param}__cv")
		h_var = f.Get(f"h{varname}__{param}__var")

		if not h_cv or h_cv.IsZombie():
			print(f"    Skipping {param} — CV not found")
			continue
		if not h_var or h_var.IsZombie():
			print(f"    Skipping {param} — var not found")
			continue

		h_cv.SetDirectory(0)
		h_var.SetDirectory(0)
		_, cv_vals  = th1_to_arrays(h_cv)
		_, var_vals = th1_to_arrays(h_var)

		# frac_diff at native resolution — matches plot_numu.py formula exactly
		with np.errstate(divide='ignore', invalid='ignore'):
			frac_diff = np.where(cv_vals > 0, (var_vals - cv_vals) / cv_vals, 0.0)

		frac_var_native += frac_diff ** 2

		# Rebin variation counts (sum) and per-param |frac_diff| (mean)
		h_vars_rebinned[param] = rebin_into_th1(
			f"h{varname}__{param}__var_gev", ref_edges, var_vals, mode='sum')
		h_frac_each[param] = rebin_into_th1(
			f"h{varname}__{param}__frac_gev", ref_edges, np.abs(frac_diff), mode='mean')

		n_loaded += 1
		print(f"    Loaded {param}")

	print(f"  Loaded {n_loaded}/{len(params)} detsys variations for {varname}")
	f.Close()

	h_cv_rebinned       = rebin_into_th1(f"h{varname}__cv_gev",       ref_edges, ref_cv,         mode='sum')
	h_frac_var_rebinned = rebin_into_th1(f"h{varname}__frac_var_gev", ref_edges, frac_var_native, mode='mean')

	return {
		'h_cv':        h_cv_rebinned,
		'h_vars':      h_vars_rebinned,
		'h_frac_var':  h_frac_var_rebinned,
		'h_frac_each': h_frac_each,
	}

# ─────────────────────────────────────────────────────────────────────────────
# LOAD XSECFLUX FRACTIONAL UNCERTAINTIES
#
# Computes sqrt(abs_variance) / cv at native resolution, then rebins with mean.
# ─────────────────────────────────────────────────────────────────────────────
def load_xsecflux_frac(xsecflux_file, varname, sample, use_agg_flux, use_agg_reint):
	"""
	Returns dict with TH1D fractional uncertainties in the target GeV binning:
	  'h_flux', 'h_reint', 'h_genie'
	"""
	f = rt.TFile(xsecflux_file)
	if f.IsZombie():
		print(f"ERROR: Cannot open {xsecflux_file}")
		return {}

	hcv = f.Get(f"h{varname}_{sample}_cv")
	if not hcv or hcv.IsZombie():
		print(f"  WARNING: CV not found: h{varname}_{sample}_cv")
		f.Close()
		return {}
	hcv.SetDirectory(0)
	edges, cv_vals = th1_to_arrays(hcv)
	nbins = len(cv_vals)

	def sum_variances(param_list, agg_name=None):
		total = np.zeros(nbins)
		names = [agg_name] if agg_name is not None else param_list
		for par in names:
			h = f.Get(f"h{varname}__{sample}__{par}_variance")
			if h and not h.IsZombie():
				h.SetDirectory(0)
				_, v = th1_to_arrays(h)
				total += v
			elif agg_name is not None:
				print(f"  WARNING: not found: h{varname}__{sample}__{par}_variance")
		return total

	flux_var  = sum_variances(_flux_params_individual, "flux_all"  if use_agg_flux  else None)
	reint_var = sum_variances(_reint_params_individual,"reint_all" if use_agg_reint else None)
	genie_var = sum_variances(_genie_params)

	# fractional uncertainty at native resolution: sqrt(abs_var) / cv
	with np.errstate(divide='ignore', invalid='ignore'):
		frac_flux  = np.where(cv_vals > 0, np.sqrt(np.maximum(flux_var,  0.0)) / cv_vals, 0.0)
		frac_reint = np.where(cv_vals > 0, np.sqrt(np.maximum(reint_var, 0.0)) / cv_vals, 0.0)
		frac_genie = np.where(cv_vals > 0, np.sqrt(np.maximum(genie_var, 0.0)) / cv_vals, 0.0)

	f.Close()

	return {
		'h_flux':  rebin_into_th1(f"h{varname}__flux_frac_gev",  edges, frac_flux,  mode='mean'),
		'h_reint': rebin_into_th1(f"h{varname}__reint_frac_gev", edges, frac_reint, mode='mean'),
		'h_genie': rebin_into_th1(f"h{varname}__genie_frac_gev", edges, frac_genie, mode='mean'),
	}

# ─────────────────────────────────────────────────────────────────────────────
# STYLE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def style_hist(h, color, linewidth=1, linestyle=1):
	h.SetLineColor(color)
	h.SetLineWidth(linewidth)
	h.SetLineStyle(linestyle)
	h.SetFillStyle(0)

def make_legend(x1, y1, x2, y2):
	leg = rt.TLegend(x1, y1, x2, y2)
	leg.SetBorderSize(1)
	leg.SetFillStyle(0)
	leg.SetTextSize(0.040)
	return leg

# ─────────────────────────────────────────────────────────────────────────────
# CANVAS 1: Detector variation overlays + Var/CV ratio
# ─────────────────────────────────────────────────────────────────────────────
def make_overlay_canvas(detsys_data, varname, title):
	if 'h_cv' not in detsys_data:
		print(f"  Skipping overlay: no CV for {varname}")
		return None

	cname = f"c_overlay_{varname}"
	c = rt.TCanvas(cname, title, 800, 700)
	# Attach a list to the canvas that will hold every ROOT object we create,
	# preventing Python GC from freeing them before Write() is called.
	c._keep = []

	c.cd()
	c.Draw()

	pad_top = rt.TPad(f"pad_top_{varname}", "", 0.0, 0.30, 1.0, 1.0)
	pad_top.SetBottomMargin(0.02)
	pad_top.SetTopMargin(0.08)
	pad_top.SetLeftMargin(0.12)
	pad_top.SetRightMargin(0.05)
	pad_top.SetTickx(1); pad_top.SetTicky(1)
	pad_top.Draw()
	c._keep.append(pad_top)

	pad_bot = rt.TPad(f"pad_bot_{varname}", "", 0.0, 0.00, 1.0, 0.30)
	pad_bot.SetTopMargin(0.02)
	pad_bot.SetBottomMargin(0.32)
	pad_bot.SetLeftMargin(0.12)
	pad_bot.SetRightMargin(0.05)
	pad_bot.SetTickx(1); pad_bot.SetTicky(1)
	pad_bot.SetGridy(1)
	pad_bot.Draw()
	c._keep.append(pad_bot)

	# ── Top pad ───────────────────────────────────────────────────────────────
	pad_top.cd()

	h_cv = detsys_data['h_cv']
	style_hist(h_cv, rt.kBlack, linewidth=2)
	h_cv.SetTitle(title)
	h_cv.GetXaxis().SetLabelSize(0)
	h_cv.GetYaxis().SetTitle("MC Pred counts (no Dirt/EXT)")
	h_cv.GetYaxis().SetTitleSize(0.055)
	h_cv.GetYaxis().SetTitleOffset(1.0)
	h_cv.SetMinimum(0)
	h_cv.Draw("HIST")
	c._keep.append(h_cv)

	leg_top = make_legend(0.60, 0.45, 0.93, 0.90)
	leg_top.AddEntry(h_cv, "CV", "l")

	for param in detsys_params:
		if param not in detsys_data['h_vars']:
			continue
		h_var = detsys_data['h_vars'][param]
		style_hist(h_var, param_color(param), linewidth=1)
		h_var.Draw("HIST SAME")
		leg_top.AddEntry(h_var, PARAM_LABELS.get(param, param), "l")
		c._keep.append(h_var)

	h_cv.Draw("HIST SAME")   # redraw CV on top
	leg_top.Draw()
	c._keep.append(leg_top)

	# ── Bottom pad: Var/CV ratio ───────────────────────────────────────────────
	pad_bot.cd()

	h_one = _make_target_th1(f"h_one_{varname}")
	for i in range(1, _NBINS + 1):
		h_one.SetBinContent(i, 1.0)
	style_hist(h_one, rt.kBlack, linewidth=1, linestyle=2)
	h_one.SetTitle("")
	h_one.GetXaxis().SetTitle("Reco Neutrino Energy (GeV)")
	h_one.GetXaxis().SetTitleSize(0.12)
	h_one.GetXaxis().SetTitleOffset(1.05)
	h_one.GetXaxis().SetLabelSize(0.10)
	h_one.GetYaxis().SetTitle("Var/CV")
	h_one.GetYaxis().SetTitleSize(0.11)
	h_one.GetYaxis().SetTitleOffset(0.45)
	h_one.GetYaxis().SetLabelSize(0.09)
	h_one.SetMinimum(0.80)
	h_one.SetMaximum(1.25)
	h_one.Draw("HIST")
	c._keep.append(h_one)

	for param in detsys_params:
		if param not in detsys_data['h_vars']:
			continue
		h_var = detsys_data['h_vars'][param]
		h_ratio = h_var.Clone(f"h_ratio_{param}_{varname}")
		h_ratio.SetDirectory(0)
		for ibin in range(1, _NBINS + 1):
			cv_val = h_cv.GetBinContent(ibin)
			if cv_val > 0:
				h_ratio.SetBinContent(ibin, h_var.GetBinContent(ibin) / cv_val)
			else:
				h_ratio.SetBinContent(ibin, 1.0)
		style_hist(h_ratio, param_color(param), linewidth=1)
		h_ratio.Draw("HIST SAME")
		c._keep.append(h_ratio)

	h_one.Draw("HIST SAME")  # unity line on top

	c.Update()
	return c

# ─────────────────────────────────────────────────────────────────────────────
# CANVAS 2: Fractional error breakdown
# ─────────────────────────────────────────────────────────────────────────────
def make_frac_canvas(detsys_data, xsec_data, varname, title):
	if 'h_frac_var' not in detsys_data or not xsec_data:
		print(f"  Skipping frac breakdown: missing data for {varname}")
		return None

def make_frac_canvas(detsys_data, xsec_data, varname, title):
	if 'h_frac_var' not in detsys_data or not xsec_data:
		print(f"  Skipping frac breakdown: missing data for {varname}")
		return None

	cname = f"c_frac_{varname}"
	c = rt.TCanvas(cname, f"Systematic Breakdown", 900, 600)
	c._keep = []
	c.cd()
	c.SetLeftMargin(0.11)
	c.SetRightMargin(0.05)
	c.SetBottomMargin(0.13)
	c.SetTopMargin(0.07)

	# Total detsys fractional uncertainty = sqrt(frac_var) bin-by-bin
	h_total_det = detsys_data['h_frac_var'].Clone(f"h_total_det_{varname}")
	h_total_det.SetDirectory(0)
	for ibin in range(1, _NBINS + 1):
		fv = h_total_det.GetBinContent(ibin)
		h_total_det.SetBinContent(ibin, sqrt(max(fv, 0.0)))
	c._keep.append(h_total_det)

	# y-axis maximum
	ymax = 0.0
	for h in [h_total_det,
	          xsec_data.get('h_flux'), xsec_data.get('h_reint'), xsec_data.get('h_genie')]:
		if h:
			ymax = max(ymax, h.GetMaximum())
	for param in detsys_params:
		h = detsys_data['h_frac_each'].get(param)
		if h:
			ymax = max(ymax, h.GetMaximum())
	ymax = ymax * 1.25 if ymax > 0 else 0.5

	# Ordered draw list: (hist, hex_color, linewidth, label)
	draw_items = [
		(xsec_data.get('h_flux'),  _FLUX_COLOR,  2, "Flux"),
		(xsec_data.get('h_reint'), _REINT_COLOR, 2, "Reinteraction"),
		(xsec_data.get('h_genie'), _GENIE_COLOR, 2, "Total GENIE"),
	]
	for param in detsys_params:
		h = detsys_data['h_frac_each'].get(param)
		if h is not None:
			draw_items.append((h, _PARAM_COLORS_HEX.get(param, "#000000"), 1,
			                   PARAM_LABELS.get(param, param)))
	draw_items.append((h_total_det, "#000000", 2, "Total Detvar"))

	# Filter out None hists
	draw_items = [(h, col, lw, lbl) for h, col, lw, lbl in draw_items if h is not None]

	leg = make_legend(0.55, 0.38, 0.93, 0.92)

	for idx, (h, hex_col, lw, label) in enumerate(draw_items):
		color = rt.TColor.GetColor(hex_col)
		style_hist(h, color, linewidth=lw)
		if idx == 0:
			h.SetTitle("Systematic Breakdown")
			h.GetXaxis().SetTitle("Reco Neutrino Energy (GeV)")
			h.GetXaxis().SetTitleSize(0.055)
			h.GetXaxis().SetTitleOffset(1.0)
			h.GetXaxis().SetLabelSize(0.045)
			h.GetYaxis().SetTitle("Fractional Error")
			h.GetYaxis().SetTitleSize(0.055)
			h.GetYaxis().SetTitleOffset(0.95)
			h.GetYaxis().SetLabelSize(0.045)
			h.SetMinimum(0.0)
			h.SetMaximum(ymax)
			h.Draw("HIST")
		else:
			h.Draw("HIST SAME")
		leg.AddEntry(h, label, "l")
		c._keep.append(h)

	leg.Draw()
	c._keep.append(leg)
	c.Update()
	return c

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
	print(f"Run {run_num} detector variation plots")
	print(f"  detsys file  : {detsys_file}")
	print(f"  xsecflux     : {xsecflux_file}")
	print(f"  output dir   : {out_dir}")

	run_label = f"run{run_num}"
	out_root  = os.path.join(out_dir, f"detvar_{run_label}.root")
	rout      = rt.TFile(out_root, "RECREATE")
	print(f"  ROOT output  : {out_root}")

	for varname in detsys_variables:
		print(f"\n── Variable: {varname} ──")

		detsys_data = load_detsys(detsys_file, varname, detsys_params)
		xsec_data   = load_xsecflux_frac(
			xsecflux_file, varname, xsecflux_sample,
			use_agg_flux, use_agg_reint)

		c1 = make_overlay_canvas(detsys_data, varname, plot_title)
		if c1:
			rout.cd()
			c1.Write()
			print(f"  Wrote {c1.GetName()}")

		c2 = make_frac_canvas(detsys_data, xsec_data, varname, plot_title)
		if c2:
			rout.cd()
			c2.Write()
			print(f"  Wrote {c2.GetName()}")

	rout.Close()
	print(f"\nSaved to {out_root}")
	print("Done.")