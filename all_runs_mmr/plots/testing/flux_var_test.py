#!/usr/bin/env python3
"""
plot_flux_universes.py

Test script: for each run, draw the stacked CC-inclusive numuIncCC histogram,
overlay the xsecflux CV, and overlay N universes of a chosen flux parameter.

Scaling consistency check
-------------------------
The xsecflux CV is filled by ArboristXsecFluxSysProducer from the numu overlay
with eventweight_weight, using the same selection cut as the analysis tree.
When scaled identically (targetpot / numu_pot), it should sit on top of the
total-MC stack.  This script overlays both so you can verify that visually,
and prints integrals for a numerical check.

Run numbers match plot_numu.py conventions:
  1   = Run 1        3  = Run 3b    30 = Run 3mil
  4   = Combined Run 4 (4b+4c+4d, or single sub-run via _run4_single_dataset)
  41  = Run 4a       42 = Run 4b    43 = Run 4c    44 = Run 4d
  5   = Run 5

Usage:
  python plot_flux_universes.py [run_num ...]   (default: 1 3 30 4 5)
"""

import os, sys
import ROOT as rt
from math import sqrt

rt.TH1.SetDefaultSumw2(rt.kTRUE)
rt.gStyle.SetOptStat(0)
rt.gStyle.SetPadBottomMargin(0.13)
rt.gStyle.SetPadLeftMargin(0.12)
rt.gStyle.SetPadRightMargin(0.05)
rt.gStyle.SetPadTopMargin(0.10)

# ============================================================
# GLOBAL KNOBS
# ============================================================
lantern_dir = "/exp/uboone/app/users/imani/lantern_ana"

# Flux parameter to draw universes for.
# Runs 1/3/3mil: individual flux params; Runs 4x/5: "flux_all".
FLUX_PAR_RUNS_135 = "horncurrent_FluxUnisim"
FLUX_PAR_RUNS_45  = "flux_all"

FLUX_PAR_RUNS_135 = "All_UBGenie"
FLUX_PAR_RUNS_45  = "All_UBGenie"


N_UNIVERSES = 10   # max universes to overlay

# Set to False to plot the CV mean and throws with no POT scaling applied
# (useful to diagnose whether a scaling mismatch is causing the CV position problem)
SCALE_CV_AND_THROWS = True

# Set to True to show only numu categories (cc_numu + nc_numu) in the stack,
# matching the scope of the xsecflux CV for a cleaner comparison.
NUMU_ONLY_STACK = True

# Set to True to suppress verbose per-file / per-bin print messages.
# Per-run summary output (CV integral, throw fractional differences) is always printed.
DEBUG = False

# Selection branch — must match what ArboristXsecFluxSysProducer used
SEL_VAR           = "numuIncCC_reco_nu_energy"
NBINS, XMIN, XMAX = 20, 0.0, 2.0

# xsecflux variable name inside each xsecflux ROOT file
XSEC_VAR_BY_RUN = {
    1:  "visible_energy",
    3:  "reco_neutrino_energy",
    30: "visible_energy",
    4:  "reco_neutrino_energy",
    41: "reco_neutrino_energy",
    42: "reco_neutrino_energy",
    43: "reco_neutrino_energy",
    44: "reco_neutrino_energy",
    5:  "visible_energy",
}

OUTDIR = f"{lantern_dir}/all_runs_mmr/plots/numu/flux_universes"
os.makedirs(OUTDIR, exist_ok=True)

# ============================================================
# SYSTEMATIC PARAMETER LISTS
# ============================================================
flux_params_135 = [
    "expskin_FluxUnisim", "horncurrent_FluxUnisim",
    "nucleoninexsec_FluxUnisim", "nucleonqexsec_FluxUnisim",
    "nucleontotxsec_FluxUnisim", "pioninexsec_FluxUnisim",
    "pionqexsec_FluxUnisim", "piontotxsec_FluxUnisim",
    "kminus_PrimaryHadronNormalization", "kplus_PrimaryHadronFeynmanScaling",
    "kzero_PrimaryHadronSanfordWang",
]
flux_params_45 = ["flux_all"]

flux_params_135 = ["All_UBGenie"]
flux_params_45 = ["All_UBGenie"]

# ============================================================
# SELECTION CATEGORIES  (mirrors plot_numu.py)
# ============================================================
base_cut = "(numuIncCC_passes_all_cuts==1)"

categories = {
    'cosmic':  dict(samples=['extbnb'], truth_cut='',
                    color=rt.kGray+2,    fill_style=1001, legend='BNB EXT'),
    'nc_nue':  dict(samples=['nue'],    truth_cut=' && (numuIncCC_is_nc_interaction==1)',
                    color=rt.kViolet-1, fill_style=1001, legend='NC nue'),
    'cc_nue':  dict(samples=['nue'],    truth_cut=' && (numuIncCC_is_cc_interaction==1)',
                    color=rt.kRed-4,    fill_style=1001, legend='CC nue'),
    'nc_numu': dict(samples=['numu'],   truth_cut=' && (numuIncCC_is_nc_interaction==1)',
                    color=rt.kGreen+1,  fill_style=1001, legend='NC numu'),
    'cc_numu': dict(samples=['numu'],   truth_cut=' && (numuIncCC_is_cc_interaction==1)',
                    color=rt.kAzure+1,  fill_style=1001, legend='CC numu'),
}
stack_order = ['cosmic', 'nc_nue', 'cc_nue', 'nc_numu', 'cc_numu']

# ============================================================
# PER-RUN CONFIGURATIONS  (mirrors plot_numu.py exactly)
# ============================================================

def _make_cfg(label, plot_title, targetpot, scaling, files,
              xsecflux_files, xsecflux_sample_map, flux_params,
              is_run4_combo=False, **extra):
    d = dict(label=label, plot_title=plot_title, targetpot=targetpot,
             scaling=scaling, files=files, xsecflux_files=xsecflux_files,
             xsecflux_sample_map=xsecflux_sample_map, flux_params=flux_params,
             is_run4_combo=is_run4_combo)
    d.update(extra)
    return d

# ---- Run 1 ----
_cfg1 = _make_cfg(
    label="Run 1", plot_title="Run 1: CC Inclusive Numu",
    targetpot=4.4e19,
    scaling=dict(numu=4.4e19/4.675690535431973e+20,
                 nue =4.4e19/9.662529168587103e+22,
                 extbnb=176153.0/433446.0, data=1.0),
    files=dict(
        numu  =f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_nu_20260302_163929.root",
        nue   =f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_nue_20260302_164813.root",
        extbnb=f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_extbnb_20260302_165918.root",
        data  =f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_data_5e19_20260302_170325.root",
    ),
    xsecflux_files=dict(
        numu=f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_numu_bnb_nu.root",
        nue =f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_numu_bnb_nue.root",
    ),
    xsecflux_sample_map=dict(numu='run1_nu', nue='run1_nue'),
    flux_params=flux_params_135,
)

# ---- Run 3b ----
_cfg3 = _make_cfg(
    label="Run 3b", plot_title="Run 3: CC Inclusive Numu",
    targetpot=4.4e19,
    scaling=dict(numu=4.4e19/8.98323351831587e+20,
                 nue =4.4e19/4.702159572049976e+22,
                 extbnb=176153.0/223580.0, data=1.0),
    files=dict(
        numu  =f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_bnb_nu_overlay_20260112_154048.root",
        nue   =f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_bnb_nue_overlay_20260112_155555.root",
        extbnb=f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_extbnb_20260112_160141.root",
        data  =f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_data_20260112_175802.root",
    ),
    xsecflux_files=dict(
        numu=f"{lantern_dir}/all_runs_mmr/run3/root_files/xsecflux/run3b_numu_covar_nu.root",
        nue =f"{lantern_dir}/all_runs_mmr/run3/root_files/xsecflux/run3b_numu_covar_nue.root",
    ),
    xsecflux_sample_map=dict(numu='run3b_nu', nue='run3b_nue'),
    flux_params=flux_params_135,
)

# ---- Run 3mil ----
_cfg30 = _make_cfg(
    label="Run 3", plot_title="Run 3: CC Inclusive Numu",
    targetpot=8.806e18,
    scaling=dict(numu=8.806e18/1.346689484233034e+21,
                 nue =8.806e18/2.891774385462469e+22,
                 extbnb=2263559.0/19214565.0, data=1.0),
    files=dict(
        numu  =f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_nu_20260211_143930.root",
        nue   =f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_nue_20260123_181343.root",
        extbnb=f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3b_extbnb_20260112_160141.root",
        data  =f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_data_20260126_180100.root",
    ),
    xsecflux_files=dict(
        numu=f"{lantern_dir}/all_runs_mmr/run3mil/root_files/xsecflux/xsecflux_run3mil_numu_bnb_nu.root",
        nue =f"{lantern_dir}/all_runs_mmr/run3mil/root_files/xsecflux/xsecflux_run3mil_numu_bnb_nue.root",
    ),
    xsecflux_sample_map=dict(numu='run3mil_nu', nue='run3mil_nue'),
    flux_params=flux_params_135,
)

# ---- Run 4 combined (4b+4c+4d) ----
_run4_single_dataset = '4b'   # set None to combine all three
_run4_labels_all     = ['4b', '4c', '4d']
_run4_labels         = [_run4_single_dataset] if _run4_single_dataset else _run4_labels_all
_tp4                 = 3.936e+19

_cfg4 = _make_cfg(
    label=f"Run 4", plot_title="Run 4: CC Inclusive Numu",
    targetpot=_tp4, is_run4_combo=True, run4_labels=_run4_labels,
    scaling={
        '4b': dict(numu=_tp4/7.881656209241413e+20,  nue=_tp4/1.1785765118473412e+23,
                   extbnb=8985142.0/96638186.0,        data=1.0),
        '4c': dict(numu=_tp4/2.8777157789184374e+20, nue=_tp4/7.160248800041886e+22,
                   extbnb=8985142.0/54566891.0,        data=1.0),
        '4d': dict(numu=_tp4/4.029820515210945e+20,  nue=_tp4/1.3740045183260529e+23,
                   extbnb=8985142.0/78224187.0,        data=1.0),
    },
    files={
        '4b': dict(numu  =f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nu_overlay_20260210_180525.root",
                   nue   =f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nue_overlay_20260114_205851.root",
                   extbnb=f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_extbnb_20260114_212008.root",
                   data  =f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_open_data_20260305_183735.root"),
        '4c': dict(numu  =f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nu_20260210_183615.root",
                   nue   =f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nue_20260210_185504.root",
                   extbnb=f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_extbnb_20260210_190529.root",
                   data  =f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_data_20260210_192923.root"),
        '4d': dict(numu  =f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nu_20260210_184026.root",
                   nue   =f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nue_20260210_191735.root",
                   extbnb=f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_extbnb_20260210_193818.root",
                   data  =f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_data_20260210_201556.root"),
    },
    xsecflux_files={
        'numu_4b': f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_run4b_numu_nu.root",
        'nue_4b' : f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_run4b_numu_nue.root",
        'numu_4c': f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_numu_nu.root",
        'nue_4c' : f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_numu_nue.root",
        'numu_4d': f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_numu_nu.root",
        'nue_4d' : f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_numu_nue.root",
    },
    xsecflux_sample_map={
        '4b': dict(nue='run4b_nue', numu='run4b_nu'),
        '4c': dict(nue='run4c_nue', numu='run4c_nu'),
        '4d': dict(nue='run4d_nue', numu='run4d_nu'),
    },
    flux_params=flux_params_45,
)

# ---- Run 4a ----
_cfg41 = _make_cfg(
    label="Run 4a", plot_title="Run 4a: CC Inclusive Numu",
    targetpot=4.483e+19,
    scaling=dict(numu=4.483e+19/2.34925e+20, nue=4.483e+19/3.68033e+22,
                 extbnb=9867464.0/27940007.0, data=1.0),
    files=dict(numu  =f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_nu_20260211_004950.root",
               nue   =f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_nue_20260211_005826.root",
               extbnb=f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_extbnb_20260211_010851.root",
               data  =f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_data_20260211_010300.root"),
    xsecflux_files=dict(numu=f"{lantern_dir}/all_runs_mmr/run4a/root_files/xsecflux/xsecflux_numu_nu.root",
                        nue =f"{lantern_dir}/all_runs_mmr/run4a/root_files/xsecflux/xsecflux_numu_nue.root"),
    xsecflux_sample_map=dict(numu='run4a_nu', nue='run4a_nue'),
    flux_params=flux_params_45,
)

# ---- Run 4b standalone ----
_cfg42 = _make_cfg(
    label="Run 4b", plot_title="Run 4b: CC Inclusive Numu",
    targetpot=1.45e+20,
    scaling=dict(numu=1.45e+20/7.881656209241413e+20, nue=1.45e+20/1.1785765118473412e+23,
                 extbnb=34317881.0/96638186.0, data=1.0),
    files=dict(numu  =f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nu_overlay_20260210_180525.root",
               nue   =f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nue_overlay_20260114_205851.root",
               extbnb=f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_extbnb_20260114_212008.root",
               data  =f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_data_20260114_212707.root"),
    xsecflux_files=dict(numu=f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_run4b_numu_nu.root",
                        nue =f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_run4b_numu_nue.root"),
    xsecflux_sample_map=dict(numu='run4b_nu', nue='run4b_nue'),
    flux_params=flux_params_45,
)

# ---- Run 4c standalone ----
_cfg43 = _make_cfg(
    label="Run 4c", plot_title="Run 4c: CC Inclusive Numu",
    targetpot=9.106e+19,
    scaling=dict(numu=9.106e+19/2.8777157789184374e+20, nue=9.106e+19/7.160248800041886e+22,
                 extbnb=20644587.0/54566891.0, data=1.0),
    files=dict(numu  =f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nu_20260210_183615.root",
               nue   =f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nue_20260210_185504.root",
               extbnb=f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_extbnb_20260210_190529.root",
               data  =f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_data_20260210_192923.root"),
    xsecflux_files=dict(numu=f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_numu_nu.root",
                        nue =f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_numu_nue.root"),
    xsecflux_sample_map=dict(numu='run4c_nu', nue='run4c_nue'),
    flux_params=flux_params_45,
)

# ---- Run 4d standalone ----
_cfg44 = _make_cfg(
    label="Run 4d", plot_title="Run 4d: CC Inclusive Numu",
    targetpot=5.015e+19,
    scaling=dict(numu=0.5*5.015e+19/4.029820515210945e+20,  # HACK as in plot_numu.py
                 nue=5.015e+19/1.3740045183260529e+23,
                 extbnb=11403578.0/78224187.0, data=1.0),
    files=dict(numu  =f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nu_20260210_184026.root",
               nue   =f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nue_20260210_191735.root",
               extbnb=f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_extbnb_20260210_193818.root",
               data  =f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_data_20260210_201556.root"),
    xsecflux_files=dict(numu=f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_numu_nu.root",
                        nue =f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_numu_nue.root"),
    xsecflux_sample_map=dict(numu='run4d_nu', nue='run4d_nue'),
    flux_params=flux_params_45,
)

# ---- Run 5 ----
_cfg5 = _make_cfg(
    label="Run 5", plot_title="Run 5: CC Inclusive Numu",
    targetpot=3.936e+19,
    scaling=dict(numu=3.936e+19/9.976307163316628e+20,
                 nue =3.936e+19/1.5178517202061622e+23,
                 extbnb=8985142.0/120139886.0, data=1.0),
    files=dict(numu  =f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_nu_20260210_182946.root",
               nue   =f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_nue_20260210_191318.root",
               extbnb=f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_extbnb_20260210_193703.root",
               data  =f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_open_data_20260305_183735.root"),
    xsecflux_files=dict(numu=f"{lantern_dir}/all_runs_mmr/run5/root_files/xsecflux/xsecflux_numu_nu.root",
                        nue =f"{lantern_dir}/all_runs_mmr/run5/root_files/xsecflux/xsecflux_numu_nue.root"),
    xsecflux_sample_map=dict(numu='run5_nu', nue='run5_nue'),
    flux_params=flux_params_45,
)

run_configs = {
    1: _cfg1, 3: _cfg3, 30: _cfg30, 4: _cfg4,
    41: _cfg41, 42: _cfg42, 43: _cfg43, 44: _cfg44, 5: _cfg5,
}

# ============================================================
# HELPERS
# ============================================================

def open_trees_simple(cfg):
    tfiles, trees = {}, {}
    for key, path in cfg['files'].items():
        if not os.path.exists(path):
            if DEBUG: print(f"  [WARN] missing: {path}")
            continue
        f = rt.TFile(path)
        if f.IsZombie():
            if DEBUG: print(f"  [WARN] zombie: {path}")
            continue
        t = f.Get("analysis_tree")
        if not t:
            if DEBUG: print(f"  [WARN] no analysis_tree in {path}")
            continue
        tfiles[key] = f
        trees[key]  = t
        if DEBUG: print(f"  {key}: {t.GetEntries()} entries")
    return tfiles, trees


def open_trees_run4(cfg):
    tfiles, trees = {}, {}
    for rl in cfg['run4_labels']:
        tfiles[rl], trees[rl] = {}, {}
        for key, path in cfg['files'][rl].items():
            if not os.path.exists(path):
                if DEBUG: print(f"  [WARN] {rl}/{key} missing: {path}")
                continue
            f = rt.TFile(path)
            if f.IsZombie():
                continue
            t = f.Get("analysis_tree")
            if not t:
                continue
            tfiles[rl][key] = f
            trees[rl][key]  = t
            if DEBUG: print(f"  run{rl}/{key}: {t.GetEntries()} entries")
    return tfiles, trees


def close_tfiles(tfiles, is_combo):
    if is_combo:
        for sub in tfiles.values():
            for f in sub.values():
                try:
                    f.Close()
                except Exception:
                    pass
    else:
        for f in tfiles.values():
            try:
                f.Close()
            except Exception:
                pass


def build_stacked_hist(cfg, trees, tag):
    """
    Fill per-category TH1Ds, return:
      hists       – dict cat_name -> scaled TH1D
      hstack      – THStack of MC categories
      h_total_mc  – sum of all MC categories
      h_numu_only – sum of numu-only categories (cc_numu + nc_numu) for CV comparison
      all_objects – list to keep alive against ROOT GC
    All returned histograms have SetDirectory(0).
    """
    hists, all_objects = {}, []
    is_combo = cfg['is_run4_combo']

    for cat_name, cat_info in categories.items():
        for sample in cat_info['samples']:
            full_cut = f"({base_cut}){cat_info['truth_cut']}"
            hname    = f"h_{tag}_{cat_name}_{sample}"
            h        = rt.TH1D(hname, "", NBINS, XMIN, XMAX)
            h.Sumw2()

            if is_combo:
                h_tmp = rt.TH1D(f"{hname}_tmp", "", NBINS, XMIN, XMAX)
                h_tmp.Sumw2()
                for rl in cfg['run4_labels']:
                    if sample not in trees.get(rl, {}):
                        continue
                    h_tmp.Reset()
                    trees[rl][sample].Draw(
                        f"{SEL_VAR}>>{hname}_tmp",
                        f"({full_cut})*eventweight_weight", "goff")
                    h_tmp.Scale(cfg['scaling'][rl][sample])
                    h.Add(h_tmp)
                h_tmp.SetDirectory(0)
                all_objects.append(h_tmp)
            else:
                if sample not in trees:
                    continue
                trees[sample].Draw(
                    f"{SEL_VAR}>>{hname}",
                    f"({full_cut})*eventweight_weight", "goff")
                h.Scale(cfg['scaling'][sample])

            h.SetDirectory(0)
            all_objects.append(h)

            if cat_name not in hists:
                hc = h.Clone(f"h_{tag}_{cat_name}_total")
                hc.Reset()
                hc.SetDirectory(0)
                hists[cat_name] = hc
                all_objects.append(hc)
            hists[cat_name].Add(h)

    # Style
    for cat_name, cat_info in categories.items():
        if cat_name not in hists:
            continue
        h = hists[cat_name]
        h.SetFillColor(cat_info['color'])
        h.SetFillStyle(cat_info['fill_style'])
        h.SetLineColor(cat_info['color'])
        h.SetLineWidth(1)

    # Stack + total MC + numu-only total
    hstack      = rt.THStack(f"hs_{tag}", "")
    h_total_mc  = None
    h_numu_only = None   # cc_numu + nc_numu: what the xsecflux CV should match

    active_stack = ([c for c in stack_order if c in ('cc_numu', 'nc_numu')]
                    if NUMU_ONLY_STACK else stack_order)

    for cat_name in active_stack:
        if cat_name not in hists:
            continue
        hstack.Add(hists[cat_name])

        if h_total_mc is None:
            h_total_mc = hists[cat_name].Clone(f"h_{tag}_total_mc")
            h_total_mc.SetDirectory(0)
        else:
            h_total_mc.Add(hists[cat_name])

        if cat_name in ('cc_numu', 'nc_numu'):
            if h_numu_only is None:
                h_numu_only = hists[cat_name].Clone(f"h_{tag}_numu_only")
                h_numu_only.SetDirectory(0)
            else:
                h_numu_only.Add(hists[cat_name])

    if h_total_mc:
        all_objects.append(h_total_mc)
    if h_numu_only:
        all_objects.append(h_numu_only)

    return hists, hstack, h_total_mc, h_numu_only, all_objects


def load_cv_and_universes(xsecflux_path, sample_name, varname, par_name,
                           n_univ, scale):
    """
    Load CV (TH1D) and up to n_univ universe projections from the TH2D
    h{varname}__{sample_name}__{par_name}, both scaled by `scale`.
    All objects are cloned with SetDirectory(0); file is closed before return.
    Returns (hcv, [huniv_0, ...]) — either can be None / empty on failure.
    """
    if not os.path.exists(xsecflux_path):
        if DEBUG: print(f"  [WARN] xsecflux not found: {xsecflux_path}")
        return None, []
    xf = rt.TFile(xsecflux_path)
    if xf.IsZombie():
        if DEBUG: print(f"  [WARN] zombie: {xsecflux_path}")
        return None, []

    # -- CV --
    hcv = None
    for cv_name in [f"h{varname}_{sample_name}_cv",
                    f"{varname}_{sample_name}_cv",
                    f"h_{varname}_{sample_name}_cv"]:
        hcv_raw = xf.Get(cv_name)
        if hcv_raw and not hcv_raw.IsZombie():
            hcv = hcv_raw.Clone(f"hcv_xsec_{sample_name}_{varname}")
            hcv.SetDirectory(0)
            if DEBUG: print(f"  CV: {cv_name}  integral(unscaled)={hcv.Integral():.1f}"
                            f"  scale={scale:.4e}")
            break
    if hcv is None:
        if DEBUG: print(f"  [WARN] CV not found for {varname}/{sample_name}")
        xf.Close()
        return None, []
    hcv.Scale(scale)
    if DEBUG: print(f"  CV: integral(scaled)={hcv.Integral():.2f}")

    # -- 2D universe histogram --
    h2d = None
    for h2d_name in [f"h{varname}__{sample_name}__{par_name}",
                     f"{varname}__{sample_name}__{par_name}",
                     f"h{varname}_{sample_name}_{par_name}"]:
        h2d_raw = xf.Get(h2d_name)
        if h2d_raw and not h2d_raw.IsZombie():
            h2d = h2d_raw
            if DEBUG: print(f"  2D hist: {h2d_name}  ({h2d.GetNbinsY()} universes)")
            break

    hunivs = []
    if h2d:
        for i in range(min(n_univ, h2d.GetNbinsY())):
            proj = h2d.ProjectionX(
                f"huniv_{sample_name}_{varname}_{par_name}_{i}", i+1, i+1)
            proj = proj.Clone(f"huniv_{sample_name}_{varname}_{par_name}_{i}_cl")
            proj.SetDirectory(0)
            proj.Scale(scale)
            hunivs.append(proj)
    else:
        if DEBUG: print(f"  [WARN] 2D universe hist not found for {par_name}")

    xf.Close()
    return hcv, hunivs


def load_cv_and_universes_run4(cfg, varname, par_name, n_univ):
    """Combined run4: sum CVs across sub-runs; universes from first valid sub-run."""
    hcv_combined, hunivs_out, got_univs = None, [], False
    for rl in cfg['run4_labels']:
        xfile_path  = cfg['xsecflux_files'].get(f"numu_{rl}", "")
        sample_name = cfg['xsecflux_sample_map'][rl]['numu']
        scale       = cfg['scaling'][rl]['numu']
        hcv, hunivs = load_cv_and_universes(
            xfile_path, sample_name, varname, par_name, n_univ, scale)
        if hcv is not None:
            if hcv_combined is None:
                hcv_combined = hcv.Clone(f"hcv_xsec_run4_{varname}")
                hcv_combined.Reset()
                hcv_combined.SetDirectory(0)
            hcv_combined.Add(hcv)
        if hunivs and not got_univs:
            hunivs_out = hunivs
            got_univs  = True
    return hcv_combined, hunivs_out


# ============================================================
# MAIN PLOT FUNCTION
# ============================================================

def mev_to_gev(h, name):
    """
    Return a new TH1D with the same bin contents as `h` but with the
    x-axis divided by 1000 (MeV -> GeV).  Bin errors are preserved.
    """
    n    = h.GetNbinsX()
    xlo  = h.GetXaxis().GetXmin() / 1000.0
    xhi  = h.GetXaxis().GetXmax() / 1000.0
    hnew = rt.TH1D(name, h.GetTitle(), n, xlo, xhi)
    hnew.SetDirectory(0)
    hnew.Sumw2()
    for ibin in range(0, n + 2):   # include under/overflow
        hnew.SetBinContent(ibin, h.GetBinContent(ibin))
        hnew.SetBinError(ibin,   h.GetBinError(ibin))
    return hnew

def plot_run(run_num, cfg, outfile):
    """
    Stacked MC histogram with:
      - CV line from h{var}_{sample}_cv, POT-scaled (and MeV->GeV if needed)
      - 10 randomly chosen throws from the TH2D, each remapped to CV space via
        throw_cv[bin] = throw_raw[bin] * (cv[bin] / mean[bin])
        following the same approach as make_hist_w_errors in the reference script.
    """
    import random

    label      = cfg['label']
    plot_title = cfg['plot_title']
    targetpot  = cfg['targetpot']
    tag        = f"run{run_num}"
    xsec_var   = XSEC_VAR_BY_RUN.get(run_num, "visible_energy")
    flux_pars  = cfg['flux_params']

    if DEBUG:
        print(f"\n{'='*60}")
        print(f"  {label}  |  xsec_var={xsec_var}")
        print(f"{'='*60}")

    # ---- 1. Open analysis trees ----
    if cfg['is_run4_combo']:
        tfiles, trees = open_trees_run4(cfg)
    else:
        tfiles, trees = open_trees_simple(cfg)

    if not trees:
        print(f"  [SKIP] no trees loaded for {label}"); return

    # ---- 2. Stacked MC histogram ----
    hists, hstack, h_total_mc, h_numu_only, all_objects = \
        build_stacked_hist(cfg, trees, tag)

    if h_total_mc is None:
        print(f"  [SKIP] no MC histograms produced for {label}")
        close_tfiles(tfiles, cfg['is_run4_combo']); return

    numu_stack = h_numu_only.Integral() if h_numu_only else 0.0
    if DEBUG: print(f"  Stack numu-only integral : {numu_stack:.2f}")

    # ---- 3. Load CV and rescaled throws from xsecflux file ----
    #
    # Reference script approach (make_hist_w_errors):
    #   cv_var[bin] = raw_var[bin] * (cv[bin] / mean[bin])^2
    # For individual throws the equivalent rescaling is:
    #   throw_cv[bin] = throw_raw[bin] * (cv[bin] / mean[bin])
    # This maps throws from the mean's normalisation into CV space so they
    # can be overlaid directly on the POT-scaled stack.

    def _to_gev_if_mev(h, name):
        """Return h with x-axis divided by 1000 if it appears to be in MeV."""
        if h.GetXaxis().GetXmax() > 10.0:
            return mev_to_gev(h, name)
        return h

    def _rebin_to_stack(h, name):
        """
        Return a new histogram with exactly the same binning as the stack
        (NBINS uniform bins from XMIN to XMAX, each (XMAX-XMIN)/NBINS wide).
        Uses ROOT's TH1.Rebin(n, name, xbins) with explicit edges so it works
        regardless of the original bin count or width.
        """
        import array as _array
        edges = _array.array('d', [XMIN + i * (XMAX - XMIN) / NBINS
                                   for i in range(NBINS + 1)])
        hnew = h.Rebin(NBINS, name, edges)
        hnew.SetDirectory(0)
        return hnew

    def _load_cv_mean_throws(xf_path, sample_name, scale, par_name, n_throws=10):
        """
        Returns (h_cv, [h_throw_0, ...]) where:
          h_cv     = h{xsec_var}_{sample_name}_cv  * scale  (MeV->GeV if needed)
          h_throw_i = throw_raw * (cv / mean)      * scale  (MeV->GeV if needed)
        All histograms have SetDirectory(0).  File is closed before return.
        """
        if not os.path.exists(xf_path):
            if DEBUG: print(f"  [WARN] missing: {xf_path}")
            return None, []
        xf = rt.TFile(xf_path)
        if xf.IsZombie():
            if DEBUG: print(f"  [WARN] zombie: {xf_path}")
            return None, []

        # -- CV --
        hcv_raw = None
        for cv_name in [f"h{xsec_var}_{sample_name}_cv",
                        f"{xsec_var}_{sample_name}_cv"]:
            raw = xf.Get(cv_name)
            if raw and not raw.IsZombie():
                hcv_raw = raw.Clone(f"hcv_{sample_name}_{tag}")
                hcv_raw.SetDirectory(0)
                if DEBUG: print(f"  CV: {cv_name}  integral(unscaled)={hcv_raw.Integral():.1f}"
                                f"  xrange=[{hcv_raw.GetXaxis().GetXmin():.1f},"
                                f"{hcv_raw.GetXaxis().GetXmax():.1f}]")
                break
        if hcv_raw is None:
            if DEBUG: print(f"  [WARN] CV not found for {xsec_var}/{sample_name}")
            xf.Close(); return None, []

        # -- Mean (needed to rescale throws into CV space) --
        hmean_raw = None
        for mean_name in [f"h{xsec_var}__{sample_name}__{par_name}_mean",
                          f"{xsec_var}__{sample_name}__{par_name}_mean"]:
            raw = xf.Get(mean_name)
            if raw and not raw.IsZombie():
                hmean_raw = raw.Clone(f"hmean_{sample_name}_{par_name}_{tag}")
                hmean_raw.SetDirectory(0)
                if DEBUG: print(f"  Mean: {mean_name}  integral(unscaled)={hmean_raw.Integral():.1f}")
                break
        if hmean_raw is None:
            if DEBUG: print(f"  [WARN] mean not found for {par_name}/{sample_name} — throws cannot be rescaled")

        # -- 2D throws histogram --
        h2d = None
        for h2d_name in [f"h{xsec_var}__{sample_name}__{par_name}",
                         f"{xsec_var}__{sample_name}__{par_name}"]:
            raw = xf.Get(h2d_name)
            if raw and not raw.IsZombie():
                h2d = raw
                if DEBUG: print(f"  Throws 2D: {h2d_name}  ({h2d.GetNbinsY()} total throws)")
                break
        if h2d is None:
            if DEBUG: print(f"  [WARN] 2D throw hist not found for {par_name}/{sample_name}")

        # Rescale throws into CV space: throw_cv[bin] = throw_raw[bin] * (cv[bin]/mean[bin])
        hthrows = []
        if h2d is not None and hmean_raw is not None:
            n_total = h2d.GetNbinsY()
            chosen  = sorted(random.sample(range(n_total), min(n_throws, n_total)))
            if DEBUG: print(f"  Using throw indices: {chosen}")
            for i in chosen:
                proj = h2d.ProjectionX(
                    f"hthrow_{sample_name}_{par_name}_{i}_{tag}", i+1, i+1)
                proj = proj.Clone(f"hthrow_{sample_name}_{par_name}_{i}_{tag}_cl")
                proj.SetDirectory(0)
                # Remap into CV space bin by bin
                for ibin in range(0, proj.GetNbinsX() + 2):
                    mean_val = hmean_raw.GetBinContent(ibin)
                    cv_val   = hcv_raw.GetBinContent(ibin)
                    if mean_val > 0:
                        proj.SetBinContent(ibin,
                            proj.GetBinContent(ibin) * cv_val / mean_val)
                    else:
                        proj.SetBinContent(ibin, 0.0)
                    proj.SetBinError(ibin, 0.0)
                if SCALE_CV_AND_THROWS:
                    proj.Scale(scale)
                proj = _to_gev_if_mev(proj,
                    f"hthrow_{sample_name}_{par_name}_{i}_{tag}_gev")
                proj = _rebin_to_stack(proj,
                    f"hthrow_{sample_name}_{par_name}_{i}_{tag}")
                hthrows.append(proj)

        # POT-scale and unit-convert the CV
        if SCALE_CV_AND_THROWS:
            hcv_raw.Scale(scale)
        hcv_out = _to_gev_if_mev(hcv_raw, f"hcv_{sample_name}_{tag}_gev")
        hcv_out = _rebin_to_stack(hcv_out, f"hcv_{sample_name}_{tag}")

        xf.Close()
        return hcv_out, hthrows

    # ---- Accumulate: two modes depending on number of flux parameters ----
    #
    # Runs 4/5  (flux_all only):  single CV + 10 random throw lines (unchanged)
    # Runs 1/30 (11 params):      single CV + 10 combined throw lines
    #   For throw index i, the combined line is built bin-by-bin as:
    #     combined_i[bin] = cv[bin] + sqrt( sum_p( (throw_p_i[bin] - cv[bin])^2 ) )
    #   i.e. the deviations from CV for each param are added in quadrature,
    #   giving 10 lines that show the spread of the total flux uncertainty.

    multi_param = (len(flux_pars) > 1)

    h_cv_total  = None
    hthrows_out = []

    if multi_param:
        # Collect throws per parameter: {par_name: [h_throw_0, ..., h_throw_9]}
        par_throws = {}   # par_name -> list of N_UNIVERSES throw histograms

        for par_name in flux_pars:
            xf_path     = cfg['xsecflux_files']['numu']
            sample_name = cfg['xsecflux_sample_map']['numu']
            scale       = cfg['scaling']['numu']
            hcv, hthrows = _load_cv_mean_throws(
                xf_path, sample_name, scale, par_name)

            if hcv is not None and h_cv_total is None:
                h_cv_total = hcv   # same CV for all params; keep once

            if hthrows:
                par_throws[par_name] = hthrows
                all_objects.extend(hthrows)

        if h_cv_total is None:
            print(f"  [WARN] no CV loaded, skipping {label}"); return

        nbins   = h_cv_total.GetNbinsX()
        n_throw = N_UNIVERSES

        # Build N_UNIVERSES combined throw lines.
        # For throw i, sum the signed deviations from each parameter linearly:
        #   combined_i[bin] = cv[bin] + Σ_p (throw_p_i[bin] - cv[bin])
        # This preserves the direction of each parameter's fluctuation so lines
        # appear both above and below the CV, matching the behaviour of flux_all.
        for i in range(n_throw):
            hcomb = h_cv_total.Clone(f"hcomb_throw_{i}_{tag}")
            hcomb.SetDirectory(0)
            for ibin in range(1, nbins + 1):
                cv_val    = h_cv_total.GetBinContent(ibin)
                total_dev = 0.0
                for par_name, throws in par_throws.items():
                    if i < len(throws):
                        total_dev += throws[i].GetBinContent(ibin) - cv_val
                hcomb.SetBinContent(ibin, cv_val + total_dev)
                hcomb.SetBinError(ibin, 0.0)
            hthrows_out.append(hcomb)
            all_objects.append(hcomb)

        if DEBUG: print(f"  Built {len(hthrows_out)} combined throw lines from "
                        f"{len(par_throws)} flux parameters")

    else:
        # Runs 4/5: single parameter — CV + 10 throw lines directly
        for par_name in flux_pars:
            if cfg['is_run4_combo']:
                for rl in cfg['run4_labels']:
                    xf_path     = cfg['xsecflux_files'].get(f"numu_{rl}", "")
                    sample_name = cfg['xsecflux_sample_map'][rl]['numu']
                    scale       = cfg['scaling'][rl]['numu']
                    hcv, hthrows = _load_cv_mean_throws(
                        xf_path, sample_name, scale, par_name)
                    if hcv is not None:
                        if h_cv_total is None:
                            h_cv_total = hcv.Clone(f"hcv_total_{tag}")
                            h_cv_total.Reset(); h_cv_total.SetDirectory(0)
                        h_cv_total.Add(hcv)
                    if hthrows and not hthrows_out:
                        hthrows_out = hthrows
            else:
                xf_path     = cfg['xsecflux_files']['numu']
                sample_name = cfg['xsecflux_sample_map']['numu']
                scale       = cfg['scaling']['numu']
                hcv, hthrows = _load_cv_mean_throws(
                    xf_path, sample_name, scale, par_name)
                if hcv is not None:
                    h_cv_total = hcv
                hthrows_out.extend(hthrows)

    if h_cv_total is None:
        print(f"  [WARN] no CV loaded, skipping {label}"); return

    all_objects += [h_cv_total] + hthrows_out

    # ---- Always-on summary ----
    cv_int = h_cv_total.Integral()
    if DEBUG:
        print(f"\n  CV integral (scaled)     : {cv_int:.2f}")
        print(f"  Stack numu-only integral : {numu_stack:.2f}")
        if numu_stack > 0:
            print(f"  CV / numu-stack ratio    : {cv_int/numu_stack:.4f}"
                  f"  ({'OK' if abs(cv_int/numu_stack - 1) < 0.05 else 'MISMATCH'})")

    throw_integrals = [ht.Integral() for ht in hthrows_out]

    print(f"\n{label}  —  fractional difference of each throw from CV (integral):")
    if cv_int > 0:
        for i, ti in enumerate(throw_integrals):
            frac = (ti - cv_int) / cv_int
            print(f"  throw {i:2d}:  integral={ti:.2f}  "
                  f"frac diff = {frac:+.4f}  ({frac*100:+.2f}%)")
    else:
        print("  (CV integral is zero — cannot compute fractional differences)")

    # ---- 4. Draw ----
    ymax = h_total_mc.GetMaximum() * 1.6
    ymax = max(ymax, h_cv_total.GetMaximum() * 1.4)
    for ht in hthrows_out:
        ymax = max(ymax, ht.GetMaximum() * 1.2)
    ymax *= 1.05

    canvas = rt.TCanvas(f"c_{tag}", f"Flux CV check - {label}", 1000, 700)
    canvas.cd()
    canvas.SetTickx(1)
    canvas.SetTicky(1)

    # Stacked MC (bottom layer)
    hstack.Draw("hist")
    hstack.SetTitle(f"{plot_title};Reco Neutrino Energy (GeV);Events / {targetpot:.1e} POT")
    hstack.SetMaximum(ymax)
    hstack.GetXaxis().SetTitleSize(0.05)
    hstack.GetYaxis().SetTitleSize(0.05)
    hstack.GetXaxis().SetLabelSize(0.04)
    hstack.GetYaxis().SetLabelSize(0.04)

    # 10 throw lines (quadrature-combined for runs 1/30, direct for runs 4/5)
    for ht in hthrows_out:
        ht.SetLineColor(rt.kGray + 1)
        ht.SetLineWidth(1)
        ht.SetFillStyle(0)
        ht.SetMarkerSize(0)
        ht.Draw("hist same")

    # CV on top
    h_cv_total.SetLineColor(rt.kBlack)
    h_cv_total.SetLineWidth(3)
    h_cv_total.SetFillStyle(0)
    h_cv_total.SetMarkerSize(0)
    h_cv_total.Draw("hist same")

    # Legend
    n_leg  = sum(1 for c in stack_order if c in hists
                 and (not NUMU_ONLY_STACK or c in ('cc_numu', 'nc_numu'))) + 2
    leg_h  = min(0.04 * n_leg + 0.04, 0.85)
    legend = rt.TLegend(0.55, 0.88 - leg_h, 0.92, 0.88)
    legend.SetTextSize(0.028)
    legend.SetFillStyle(0)
    legend.SetBorderSize(1)
    for cat_name in reversed(stack_order):
        if cat_name not in hists:
            continue
        if NUMU_ONLY_STACK and cat_name not in ('cc_numu', 'nc_numu'):
            continue
        legend.AddEntry(hists[cat_name], categories[cat_name]['legend'], "f")
    legend.AddEntry(h_cv_total, "All_UBGenie CV", "l")
    throw_label = (f"All_UBGenie ({len(hthrows_out)} throws)"
                   if multi_param else
                   f"All_UBGenie ({len(hthrows_out)} random)")
    if hthrows_out:
        legend.AddEntry(hthrows_out[0], throw_label, "l")
    legend.Draw()

    canvas.Update()

    # ---- 5. Write canvas flat into ROOT file ----
    outfile.cd()
    canvas.Write(f"c_{tag}")
    if DEBUG: print(f"  Written canvas c_{tag} to ROOT file")

    # ---- 6. Clean up ----
    close_tfiles(tfiles, cfg['is_run4_combo'])
    h_throw0 = hthrows_out[0] if hthrows_out else None
    return h_cv_total, h_throw0, label


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    default_runs = [1, 30, 4, 5]
    selected = ([int(a) for a in sys.argv[1:]] if len(sys.argv) > 1
                else default_runs)

    out_root_path = f"{OUTDIR}/flux_cv_check.root"
    outfile = rt.TFile(out_root_path, "recreate")
    print(f"Output ROOT file: {out_root_path}")

    run_results = {}   # run_num -> (h_cv, h_throw0, label)
    for rn in selected:
        if rn not in run_configs:
            print(f"Unknown run: {rn}. Available: {sorted(run_configs.keys())}")
            continue
        result = plot_run(rn, run_configs[rn], outfile)
        if result is not None:
            run_results[rn] = result

    # ---- Ratio canvas: throw[0] / CV, one line per run ----
    ratio_colors = {1: rt.kBlue+1, 30: rt.kRed+1, 4: rt.kGreen+2, 5: rt.kOrange+1}
    default_colors = [rt.kBlack, rt.kMagenta+1, rt.kCyan+2, rt.kGray+1]

    ratio_hists = []
    c_ratio = rt.TCanvas("c_throw0_cv_ratio", "One Throw / CV ratio per run", 1000, 700)
    c_ratio.cd()
    c_ratio.SetTickx(1); c_ratio.SetTicky(1)

    leg_ratio = rt.TLegend(0.55, 0.72, 0.92, 0.88)
    leg_ratio.SetTextSize(0.028)
    leg_ratio.SetFillStyle(0)
    leg_ratio.SetBorderSize(1)

    # Reference line at 1
    href = rt.TLine(XMIN, 1.0, XMAX, 1.0)
    href.SetLineColor(rt.kGray+2)
    href.SetLineStyle(2)
    href.SetLineWidth(1)

    frame = None
    color_idx = 0
    for rn, (h_cv, h_throw0, lbl) in run_results.items():
        if h_cv is None or h_throw0 is None:
            continue
        h_ratio = h_throw0.Clone(f"h_ratio_run{rn}")
        h_ratio.SetDirectory(0)
        h_ratio.Divide(h_cv)
        h_ratio.SetBinErrorOption(rt.TH1.kPoisson)

        col = ratio_colors.get(rn, default_colors[color_idx % len(default_colors)])
        color_idx += 1
        h_ratio.SetLineColor(col)
        h_ratio.SetLineWidth(2)
        h_ratio.SetFillStyle(0)
        h_ratio.SetMarkerSize(0)

        if frame is None:
            h_ratio.Draw("hist")
            h_ratio.SetTitle(";Reco Neutrino Energy (GeV); One Throw / CV")
            h_ratio.GetYaxis().SetRangeUser(0.7, 1.3)
            h_ratio.GetXaxis().SetTitleSize(0.05)
            h_ratio.GetYaxis().SetTitleSize(0.05)
            h_ratio.GetXaxis().SetLabelSize(0.04)
            h_ratio.GetYaxis().SetLabelSize(0.04)
            frame = h_ratio
        else:
            h_ratio.Draw("hist same")

        leg_ratio.AddEntry(h_ratio, lbl, "l")
        ratio_hists.append(h_ratio)

    if frame is not None:
        href.Draw("same")
        leg_ratio.Draw()
        c_ratio.Update()
        outfile.cd()
        c_ratio.Write("c_throw0_cv_ratio")

    outfile.Close()
    print(f"\nDone. ROOT file: {out_root_path}")