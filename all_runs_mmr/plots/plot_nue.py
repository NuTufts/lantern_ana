import os, sys
import ROOT as rt
from math import sqrt

# ===========================================================================
# plot_nue_hists.py
#
# CC inclusive νe stacked-histogram plotter.
# Methodology mirrors plot_numu.py exactly; nue-specific details
# (cut variable names, file paths, xsecflux paths) taken from plot_nue.py.
#
# Run numbers:
#   1   = Run 1
#   3   = Run 3b
#   30  = Run 3 (~1M events sub-sample)
#   4   = Run 4 combined  (4b + 4c + 4d, governed by run4_single_dataset)
#   41  = Run 4a standalone
#   42  = Run 4b standalone
#   43  = Run 4c standalone
#   44  = Run 4d standalone
#   5   = Run 5
# ===========================================================================

run_num = 5

lantern_dir = "/exp/uboone/app/users/imani/lantern_ana/"

# ---------------------------------------------------------------------------
# Run-specific configuration
# ---------------------------------------------------------------------------

## Run 1
if run_num == 1:
	targetpot = 4.4e19
	scaling = {
		"numu": targetpot / 4.675690535431973e+20,
		"nue":  targetpot / 9.662529168587103e+22,
		"extbnb": 176153.0 / 433446.0,
		"data": 1.0
	}
	files = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_nu_20260302_163929.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_nue_20260302_164813.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_extbnb_20260302_165918.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_data_5e19_20260302_170325.root"
	}
	xsecflux_files = {
		"nue":  f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_nue_intrinsic_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_nue_overlay_nu.root"
	}
	xsecflux_sample_map = {
		'nue':  'run1_bnb_nue_overlay_mcc9_v28_wctagger',
		'numu': 'run1_bnb_nu_overlay_mcc9_v28_wctagger'
	}
	detsys_file = None
	detsys_params = []
	detsys_variables = []
	show_data  = True
	data_legend = "Run1 5e19"
	plot_title  = "Run 1: CC Inclusive Nue"
	out_name    = f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run1_hists.root"
	remove_cut  = ""
	# xsecflux variable names inside the xsecflux ROOT files
	var_name_map = {
		'neutrino_energy':   'visible_energy',
		'electron_momentum': 'electron_momentum',
		'electron_costheta': 'electron_angle'
	}

## Run 3b
if run_num == 3:
	targetpot = 5e19
	scaling = {
		"numu": targetpot / 8.98323351831587e+20,
		"nue":  targetpot / 4.702159572049976e+22,
		"extbnb": 176153.0 / 223580.0,
		"data": 1.0
	}
	files = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3mil_nu_20260211_143930.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3mil_nue_20260123_181343.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_extbnb_20260112_160141.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3mil_data_20260126_180100.root"
	}
	xsecflux_files = {
		"nue":  f"{lantern_dir}/all_runs_mmr/run3/root_files/xsecflux/xsecflux_run3mil_nue_bnb_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run3/root_files/xsecflux/xsecflux_run3mil_nue_bnb_nu.root"
	}
	xsecflux_sample_map = {
		'nue':  'run3mil_nue',
		'numu': 'run3mil_nu'
	}
	detsys_file = None
	detsys_params = []
	detsys_variables = []
	show_data   = True
	data_legend = "Run3 5e19"
	plot_title  = "Run 3: CC Inclusive Nue"
	out_name    = f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run3_hists.root"
	remove_cut  = "&& (remove_true_nue_cc_flag==0)"
	var_name_map = {
		'neutrino_energy':   'visible_energy',
		'electron_momentum': 'reco_electron_energy',
		'electron_costheta': 'reco_cos_theta'
	}

## Run 3mil
if run_num == 30:
	targetpot = 8.806e18
	scaling = {
		"numu": targetpot / 1.346689484233034e+21,
		"nue":  targetpot / 2.891774385462469e+22,
		"extbnb": 2263559.0 / 19214565.0,
		"data": 1.0
	}
	files = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_nu_20260122_162913.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_nue_20260123_181343.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_extbnb_20260123_164522.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_data_20260126_180100.root"
	}
	xsecflux_files = {
		"nue":  f"{lantern_dir}/all_runs_mmr/run3mil/root_files/xsecflux/xsecflux_run3mil_nue_bnb_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run3mil/root_files/xsecflux/xsecflux_run3mil_nue_bnb_nu.root"
	}
	xsecflux_sample_map = {
		'nue':  'run3mil_nue',
		'numu': 'run3mil_nu'
	}
	detsys_file = None
	detsys_params = []
	detsys_variables = []
	show_data   = True
	data_legend = "Run3 1e19"
	plot_title  = "Run 3 1mil: CC Inclusive Nue"
	out_name    = f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run3mil_hists.root"
	remove_cut  = "&& (remove_true_nue_cc_flag==0)"
	var_name_map = {
		'neutrino_energy':   'visible_energy',
		'electron_momentum': 'reco_electron_energy',
		'electron_costheta': 'reco_cos_theta'
	}

## Combined Run 4 (4b + 4c + 4d)
if run_num == 4:
	targetpot = 3.936e+19

	scaling_4b = {
		"numu": targetpot / 7.881656209241413e+20,
		"nue":  targetpot / 1.1785765118473412e+23,
		"extbnb": 8985142.0 / 96638186.0,
		"data": 1.0
	}
	scaling_4c = {
		"numu": targetpot / 2.8777157789184374e+20,
		"nue":  targetpot / 7.160248800041886e+22,
		"extbnb": 8985142.0 / 54566891.0,
		"data": 1.0
	}
	scaling_4d = {
		"numu": targetpot / 4.029820515210945e+20,
		"nue":  targetpot / 1.3740045183260529e+23,
		"extbnb": 8985142.0 / 78224187.0,
		"data": 1.0
	}

	# Set to '4b', '4c', or '4d' to use a single sub-run; None to combine all three.
	run4_single_dataset = '4b'

	_all_run4_labels = ['4b', '4c', '4d']
	run4_labels = [run4_single_dataset] if run4_single_dataset else _all_run4_labels

	scaling = {
		'4b': scaling_4b,
		'4c': scaling_4c,
		'4d': scaling_4d
	}

	files_4b = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nu_overlay_20260210_180525.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nue_overlay_20260114_205851.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_extbnb_20260114_212008.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_open_data_20260305_183735.root"
	}
	files_4c = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nu_20260210_183615.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nue_20260210_185504.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_extbnb_20260210_190529.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_data_20260210_192923.root"
	}
	files_4d = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nu_20260210_184026.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nue_20260210_191735.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_extbnb_20260210_193818.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_data_20260210_201556.root"
	}
	files = {'4b': files_4b, '4c': files_4c, '4d': files_4d}

	# Nue-specific xsecflux files (analogous to xsecflux_numu_*.root for the numu analysis)
	xsecflux_files = {
		"numu_4b": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_nue_nu.root",
		"nue_4b":  f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_nue_nue.root",
		"numu_4c": f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_nue_nu.root",
		"nue_4c":  f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_nue_nue.root",
		"numu_4d": f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_nue_nu.root",
		"nue_4d":  f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_nue_nue.root"
	}
	xsecflux_sample_map = {
		'4b': {'nue': 'run4b_nue', 'numu': 'run4b_nu'},
		'4c': {'nue': 'run4c_nue', 'numu': 'run4c_nu'},
		'4d': {'nue': 'run4d_nue', 'numu': 'run4d_nu'}
	}

	detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nue_cv.root"

	show_data   = True
	data_legend = "Run4b Open Data"
	plot_title  = "Run 4: CC Inclusive Nue"
	out_name    = f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run4_combined_hists.root"
	remove_cut  = "&& (remove_true_nue_cc_flag==0)"
	var_name_map = {
		'neutrino_energy':   'reco_neutrino_energy',
		'electron_momentum': 'reco_electron_energy',
		'electron_costheta': 'reco_cos_theta'
	}

## Run 4a standalone
if run_num == 41:
	targetpot = 4.483e+19
	scaling = {
		"numu": targetpot / 2.34925e+20,
		"nue":  targetpot / 3.68033e+22,
		"extbnb": 9867464.0 / 27940007.0,
		"data": 1.0
	}
	files = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_nu_20260211_004950.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_nue_20260211_005826.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_extbnb_20260211_010851.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_data_20260211_010300.root"
	}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4a/root_files/xsecflux/xsecflux_nue_nu.root",
		"nue":  f"{lantern_dir}/all_runs_mmr/run4a/root_files/xsecflux/xsecflux_nue_nue.root"
	}
	xsecflux_sample_map = {'nue': 'run4a_nue', 'numu': 'run4a_nu'}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nue_cv.root"
	show_data   = True
	data_legend = "Run4a Data"
	plot_title  = "Run 4a: CC Inclusive Nue"
	out_name    = f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run4a_hists.root"
	remove_cut  = "&& (remove_true_nue_cc_flag==0)"
	var_name_map = {
		'neutrino_energy':   'reco_neutrino_energy',
		'electron_momentum': 'reco_electron_energy',
		'electron_costheta': 'reco_cos_theta'
	}

## Run 4b standalone
if run_num == 42:
	targetpot = 1.45e+20
	scaling = {
		"numu": targetpot / 7.881656209241413e+20,
		"nue":  targetpot / 1.1785765118473412e+23,
		"extbnb": 34317881.0 / 96638186.0,
		"data": 1.0
	}
	files = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nu_overlay_20260210_180525.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nue_overlay_20260114_205851.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_extbnb_20260114_212008.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_open_data_20260305_183735.root"
	}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_nue_nu.root",
		"nue":  f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_nue_nue.root"
	}
	xsecflux_sample_map = {'nue': 'run4b_nue', 'numu': 'run4b_nu'}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nue_cv.root"
	show_data   = True
	data_legend = "Run4b Open Data"
	plot_title  = "Run 4b: CC Inclusive Nue"
	out_name    = f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run4b_hists.root"
	remove_cut  = "&& (remove_true_nue_cc_flag==0)"
	var_name_map = {
		'neutrino_energy':   'reco_neutrino_energy',
		'electron_momentum': 'reco_electron_energy',
		'electron_costheta': 'reco_cos_theta'
	}

## Run 4c standalone
if run_num == 43:
	targetpot = 9.106e+19
	scaling = {
		"numu": targetpot / 2.8777157789184374e+20,
		"nue":  targetpot / 7.160248800041886e+22,
		"extbnb": 20644587.0 / 54566891.0,
		"data": 1.0
	}
	files = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nu_20260210_183615.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nue_20260210_185504.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_extbnb_20260210_190529.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_data_20260210_192923.root"
	}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_nue_nu.root",
		"nue":  f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_nue_nue.root"
	}
	xsecflux_sample_map = {'nue': 'run4c_nue', 'numu': 'run4c_nu'}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nue_cv.root"
	show_data   = True
	data_legend = "Run4c Data"
	plot_title  = "Run 4c: CC Inclusive Nue"
	out_name    = f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run4c_hists.root"
	remove_cut  = "&& (remove_true_nue_cc_flag==0)"
	var_name_map = {
		'neutrino_energy':   'reco_neutrino_energy',
		'electron_momentum': 'reco_electron_energy',
		'electron_costheta': 'reco_cos_theta'
	}

## Run 4d standalone
if run_num == 44:
	targetpot = 5.015e+19
	scaling = {
		"numu": targetpot / 4.029820515210945e+20,
		"nue":  targetpot / 1.3740045183260529e+23,
		"extbnb": 11403578.0 / 78224187.0,
		"data": 1.0
	}
	files = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nu_20260210_184026.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nue_20260210_191735.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_extbnb_20260210_193818.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_data_20260210_201556.root"
	}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_nue_nu.root",
		"nue":  f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_nue_nue.root"
	}
	xsecflux_sample_map = {'nue': 'run4d_nue', 'numu': 'run4d_nu'}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nue_cv.root"
	show_data   = True
	data_legend = "Run4d Data"
	plot_title  = "Run 4d: CC Inclusive Nue"
	out_name    = f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run4d_hists.root"
	remove_cut  = "&& (remove_true_nue_cc_flag==0)"
	var_name_map = {
		'neutrino_energy':   'reco_neutrino_energy',
		'electron_momentum': 'reco_electron_energy',
		'electron_costheta': 'reco_cos_theta'
	}

## Run 5
if run_num == 5:
	targetpot = 3.936e+19
	scaling = {
		"numu": targetpot / 9.976307163316628e+20,
		"nue":  targetpot / 1.5178517202061622e+23,
		"extbnb": 8985142.0 / 120139886.0,
		"data": 1.0
	}
	files = {
		"numu":  f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_nu_20260210_182946.root",
		"nue":   f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_nue_20260210_191318.root",
		"extbnb":f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_extbnb_20260210_193703.root",
		"data":  f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_open_data_20260305_183735.root"
	}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run5/root_files/xsecflux/xsecflux_nue_nu.root",
		"nue":  f"{lantern_dir}/all_runs_mmr/run5/root_files/xsecflux/xsecflux_nue_nue.root"
	}
	xsecflux_sample_map = {'nue': 'run5_nue', 'numu': 'run5_nu'}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run5/root_files/detsys/detsys_cv_run5_nue_cv.root"
	show_data   = True
	data_legend = "Run4b Open Data"
	plot_title  = "Run 5: CC Inclusive Nue"
	out_name    = f"{lantern_dir}/all_runs_mmr/plots/nue/nue_run5_hists.root"
	remove_cut  = "&& (remove_true_nue_cc_flag==0)"
	var_name_map = {
		'neutrino_energy':   'reco_neutrino_energy',
		'electron_momentum': 'reco_electron_energy',
		'electron_costheta': 'reco_cos_theta'
	}

## Same for all runs
xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_electron_energy', 'reco_cos_theta']
detsys_variables   = ['visible_energy', 'reco_neutrino_energy', 'reco_electron_energy', 'reco_cos_theta']
detsys_params = [
	"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ",
	"LYAtt", "LYDown", "LYRayleigh",
	"recomb2", "SCE",
	"wiremodeThetaXZ", "wiremodeThetaYZ"
]
show_ratio = True

# ---------------------------------------------------------------------------
# Systematic parameter lists
# ---------------------------------------------------------------------------

if run_num in [1, 3, 30]:
	flux_params = [
		"expskin_FluxUnisim",
		"horncurrent_FluxUnisim",
		"nucleoninexsec_FluxUnisim",
		"nucleonqexsec_FluxUnisim",
		"nucleontotxsec_FluxUnisim",
		"pioninexsec_FluxUnisim",
		"pionqexsec_FluxUnisim",
		"piontotxsec_FluxUnisim",
		"kminus_PrimaryHadronNormalization",
		"kplus_PrimaryHadronFeynmanScaling",
		"kzero_PrimaryHadronSanfordWang",
	]
	xsec_params = [
		"All_UBGenie",
		"XSecShape_CCMEC_UBGenie",
		"RPA_CCQE_UBGenie",
		"AxFFCCQEshape_UBGenie",
		"VecFFCCQEshape_UBGenie",
		"DecayAngMEC_UBGenie",
		"xsr_scc_Fa3_SCC",
		"xsr_scc_Fv3_SCC",
		"NormCCCOH_UBGenie",
		"NormNCCOH_UBGenie",
		"ThetaDelta2NRad_UBGenie",
		"Theta_Delta2Npi_UBGenie",
		"piminus_PrimaryHadronSWCentralSplineVariation",
		"piplus_PrimaryHadronSWCentralSplineVariation"
	]
	reint_params = [
		"reinteractions_piminus_Geant4",
		"reinteractions_piplus_Geant4",
		"reinteractions_proton_Geant4"
	]
	_xsec_detector = []

if run_num in [4, 41, 42, 43, 44, 5]:
	flux_params = ["flux_all"]
	xsec_params = [
		"All_UBGenie",
		"XSecShape_CCMEC_UBGenie",
		"RPA_CCQE_UBGenie",
		"AxFFCCQEshape_UBGenie",
		"VecFFCCQEshape_UBGenie",
		"DecayAngMEC_UBGenie",
		"xsr_scc_Fa3_SCC",
		"xsr_scc_Fv3_SCC",
		"NormCCCOH_UBGenie",
		"NormNCCOH_UBGenie",
		"ThetaDelta2NRad_UBGenie",
		"Theta_Delta2Npi_UBGenie"
	]
	reint_params = ["reint_all"]
	# Detector params embedded in the xsecflux file (distinct from detsys_file params)
	xsecflux_detector_params = ["detvar_all"]
	_xsec_detector = xsecflux_detector_params

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def load_detector_variations(rfile, varname, detsys_params):
	"""Load detector variation histograms and calculate fractional uncertainties."""
	if rfile is None or rfile.IsZombie():
		print(f"  Warning: Invalid detector systematics file")
		return None

	detector_hists = {}

	# Find a reference CV histogram for binning
	h_reference = None
	for param in detsys_params:
		cv_name = f"h{varname}__{param}__cv"
		h_temp  = rfile.Get(cv_name)
		if h_temp and not h_temp.IsZombie():
			h_reference = h_temp
			break

	if h_reference is None:
		print(f"  Warning: Could not find reference histogram for {varname}")
		return None

	# Combined fractional variance histogram
	h_frac_var = h_reference.Clone(f"h{varname}__detector_frac_variance")
	h_frac_var.SetDirectory(0)
	h_frac_var.Reset()

	n_loaded = 0
	for param in detsys_params:
		cv_name  = f"h{varname}__{param}__cv"
		var_name = f"h{varname}__{param}__var"

		h_cv  = rfile.Get(cv_name)
		h_var = rfile.Get(var_name)

		if not h_cv or h_cv.IsZombie():
			print(f"    Skipping {param} - CV histogram not found")
			continue
		if not h_var or h_var.IsZombie():
			print(f"    Skipping {param} - variation histogram not found")
			continue

		n_loaded += 1
		print(f"    Loaded {param}")

		for ibin in range(0, h_frac_var.GetNbinsX() + 2):
			cv_val  = h_cv.GetBinContent(ibin)
			var_val = h_var.GetBinContent(ibin)
			if cv_val > 0:
				frac_diff   = (var_val - cv_val) / cv_val
				current_var = h_frac_var.GetBinContent(ibin)
				h_frac_var.SetBinContent(ibin, current_var + frac_diff**2)

	print(f"  Loaded {n_loaded}/{len(detsys_params)} detector variations for {varname}")
	detector_hists['frac_variance'] = h_frac_var
	detector_hists['n_params']      = n_loaded
	return detector_hists


def make_hist_w_errors(rfile, varname, sample,
                       flux_params, xsec_params, reint_params,
                       detector_params=None):
	"""
	Load xsecflux variance histograms and separate them into per-parameter
	and per-category (flux / xsec / reint / detector) variance histograms.

	All returned histograms are POT-scaled (variance histograms already store
	target-POT-scaled variances from the producer).  Do NOT apply an additional
	POT scaling factor externally.

	Returns a dict with keys:
	  'cv', 'fluxvar', 'xsecvar', 'reintvar', 'detectorvar', 'param_vars'
	or None if the CV histogram cannot be found.
	"""
	if detector_params is None:
		detector_params = []

	hcv_name = f"h{varname}_{sample}_cv"
	hcv = rfile.Get(hcv_name)
	if not hcv or hcv.IsZombie():
		print(f"  Warning: CV histogram '{hcv_name}' not found")
		return None
	hcv.SetDirectory(0)

	hvar_flux     = hcv.Clone(f"h{varname}__{sample}__flux_variance");    hvar_flux.SetDirectory(0);     hvar_flux.Reset()
	hvar_xsec     = hcv.Clone(f"h{varname}__{sample}__xsec_variance");    hvar_xsec.SetDirectory(0);     hvar_xsec.Reset()
	hvar_reint    = hcv.Clone(f"h{varname}__{sample}__reint_variance");   hvar_reint.SetDirectory(0);    hvar_reint.Reset()
	hvar_detector = hcv.Clone(f"h{varname}__{sample}__detector_variance"); hvar_detector.SetDirectory(0); hvar_detector.Reset()
	hmeans2       = hcv.Clone(f"h{varname}__{sample}__meanofmeans");       hmeans2.SetDirectory(0);       hmeans2.Reset()

	all_params = (
		[(p, 'flux')     for p in flux_params] +
		[(p, 'xsec')     for p in xsec_params] +
		[(p, 'reint')    for p in reint_params] +
		[(p, 'detector') for p in detector_params]
	)

	param_var_hists = {}

	for parname, category in all_params:
		hname_mean = f"h{varname}__{sample}__{parname}_mean"
		hname_var  = f"h{varname}__{sample}__{parname}_variance"

		hmean = rfile.Get(hname_mean)
		hvar  = rfile.Get(hname_var)

		if not hmean or hmean.IsZombie():
			print(f"    Skipping {parname} - mean histogram not found")
			continue
		if not hvar or hvar.IsZombie():
			print(f"    Skipping {parname} - variance histogram not found")
			continue

		h_param_var = hcv.Clone(f"h{varname}__{sample}__{parname}_variance_cv")
		h_param_var.SetDirectory(0)
		h_param_var.Reset()

		for ibin in range(0, hcv.GetNbinsX() + 2):
			xvar  = hvar.GetBinContent(ibin)
			xmean = hmean.GetBinContent(ibin)
			cv_val = hcv.GetBinContent(ibin)

			if xmean > 0:
				frac_var = xvar / (xmean * xmean)
			else:
				frac_var = 0.0

			cv_var = frac_var * cv_val * cv_val

			h_param_var.SetBinContent(ibin, cv_var)

			if category == 'flux':
				hvar_flux.SetBinContent(ibin, hvar_flux.GetBinContent(ibin) + cv_var)
			elif category == 'xsec':
				hvar_xsec.SetBinContent(ibin, hvar_xsec.GetBinContent(ibin) + cv_var)
			elif category == 'reint':
				hvar_reint.SetBinContent(ibin, hvar_reint.GetBinContent(ibin) + cv_var)
			elif category == 'detector':
				hvar_detector.SetBinContent(ibin, hvar_detector.GetBinContent(ibin) + cv_var)

			xmean2 = hmeans2.GetBinContent(ibin)
			hmeans2.SetBinContent(ibin, xmean2 + xmean / len(all_params))

		param_var_hists[parname] = h_param_var

	return {
		'cv':          hcv,
		'mean2':       hmeans2,
		'fluxvar':     hvar_flux,
		'xsecvar':     hvar_xsec,
		'reintvar':    hvar_reint,
		'detectorvar': hvar_detector,
		'param_vars':  param_var_hists
	}


# ---------------------------------------------------------------------------
# Open ROOT files and trees
# ---------------------------------------------------------------------------

rt.gStyle.SetOptStat(0)

tfiles = {}
trees  = {}

if run_num == 4:
	# Run 4 combo: open one set of trees per sub-run label
	for run_label in run4_labels:
		tfiles[run_label] = {}
		trees[run_label]  = {}
		for sample in ['numu', 'nue', 'extbnb', 'data']:
			fpath = files[run_label][sample]
			tf = rt.TFile(fpath)
			if tf.IsZombie():
				print(f"Warning: could not open {fpath}")
				continue
			tfiles[run_label][sample] = tf
			trees[run_label][sample]  = tf.Get("analysis_tree")
			nentries = trees[run_label][sample].GetEntries()
			print(f"sample={run_label}/{sample} has {nentries} entries")
else:
	for sample in ['numu', 'nue', 'extbnb', 'data']:
		tf = rt.TFile(files[sample])
		if tf.IsZombie():
			print(f"Warning: could not open {files[sample]}")
			continue
		tfiles[sample] = tf
		trees[sample]  = tf.Get("analysis_tree")
		nentries = trees[sample].GetEntries()
		print(f"sample={sample} has {nentries} entries")

## Create output directory if it doesn't exist
out_dir = os.path.dirname(out_name)
if out_dir and not os.path.exists(out_dir):
	os.makedirs(out_dir)
	print(f"Created output directory: {out_dir}")

print(f"\nOutput file: {out_name}")
out = rt.TFile(out_name, "recreate")

# ---------------------------------------------------------------------------
# Selection cut
# ---------------------------------------------------------------------------

base_cut = "(nueIncCC_passes_all_cuts==1)"

# ---------------------------------------------------------------------------
# Sample categories
# nue signal is drawn on top of the stack.
# The remove_cut is applied to cc_numu to prevent double-counting true nue cc
# events in the numu overlay sample.
# ---------------------------------------------------------------------------

categories = {
	'cosmic': {
		'samples':    ['extbnb'],
		'truth_cut':  ' ',
		'color':      rt.kGray+2,
		'fill_style': 1001,
		'legend':     'BNB EXT'
	},
	'nc_numu': {
		'samples':    ['numu'],
		'truth_cut':  ' && (nueIncCC_is_neutral_current==1)',
		'color':      rt.kGreen+1,
		'fill_style': 1001,
		'legend':     'NC numu'
	},
	'cc_numu': {
		'samples':    ['numu'],
		'truth_cut':  f' && (nueIncCC_is_charge_current==1){remove_cut}',
		'color':      rt.kAzure+1,
		'fill_style': 1001,
		'legend':     'CC numu'
	},
	'nc_nue': {
		'samples':    ['nue'],
		'truth_cut':  ' && (nueIncCC_is_neutral_current==1)',
		'color':      rt.kViolet-1,
		'fill_style': 1001,
		'legend':     'NC nue'
	},
	'cc_nue': {
		'samples':    ['nue'],
		'truth_cut':  ' && (nueIncCC_is_charge_current==1)',
		'color':      rt.kRed-4,
		'fill_style': 1001,
		'legend':     'CC nue'
	},
	'data': {
		'samples':    ['data'],
		'truth_cut':  '',
		'color':      rt.kBlack,
		'fill_style': 0,
		'legend':     data_legend
	}
}

# Stack order: background at the bottom, nue signal on top
stack_order = ['cosmic', 'nc_numu', 'cc_numu', 'nc_nue', 'cc_nue']

if not show_data:
	del categories['data']

legend_POT_string = " Events Per " + str(targetpot) + " POT"

# ---------------------------------------------------------------------------
# Variables to plot
# 'xsecflux_var' is the histogram name used inside the xsecflux ROOT files.
# ---------------------------------------------------------------------------

# Run 3/3mil: branch names and binning match the ArboristXsecFluxSysProducer YAML config.
# visible_energy is in MeV in the tree (xmax=3000), electron momentum/costheta use
# the nueIncCC_ producer branches directly.
if run_num in [3, 4,30]:
	variables = {
		'neutrino_energy': {
			'var':          'visible_energy',
			'nbins':        30,
			'xmin':         0.0,
			'xmax':         3000.0,
			'title':        plot_title + '; Visible Energy (MeV); ' + legend_POT_string,
			'cut_suffix':   '',
			'xsecflux_var': var_name_map['neutrino_energy'],
		},
		# 'electron_momentum': {
		# 	'var':          'nueIncCC_reco_electron_momentum',
		# 	'nbins':        15,
		# 	'xmin':         0.0,
		# 	'xmax':         1.5,
		# 	'title':        plot_title + '; Reconstructed Electron Momentum (GeV); ' + legend_POT_string,
		# 	'cut_suffix':   '&& (nueIncCC_reco_electron_momentum>0)',
		# 	'xsecflux_var': var_name_map['electron_momentum'],
		# },
		# 'electron_costheta': {
		# 	'var':          'nueIncCC_reco_electron_costheta',
		# 	'nbins':        20,
		# 	'xmin':         -1.0,
		# 	'xmax':         1.0,
		# 	'title':        plot_title + '; Reconstructed Electron cos(#theta); ' + legend_POT_string,
		# 	'cut_suffix':   '&& (nueIncCC_reco_electron_costheta>-900)',
		# 	'xsecflux_var': var_name_map['electron_costheta'],
		# }
	}

# Run 1 and all run 4/5 variants use nueIncCC_ reco branches throughout.
else:
	variables = {
		'neutrino_energy': {
			'var':          'nueIncCC_reco_nu_energy',
			'nbins':        30,
			'xmin':         0.0,
			'xmax':         3.0,
			'title':        plot_title + '; Reconstructed Neutrino Energy (GeV); ' + legend_POT_string,
			'cut_suffix':   '',
			'xsecflux_var': var_name_map['neutrino_energy'],
			'rebin_config': {
				'type': 'variable',
				'bins': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
				'overflow': True
			}
		},
		'electron_momentum': {
			'var':          'nueIncCC_reco_electron_momentum',
			'nbins':        25,
			'xmin':         0.0,
			'xmax':         1.5,
			'title':        plot_title + '; Reconstructed Electron Momentum (GeV); ' + legend_POT_string,
			'cut_suffix':   '&& (nueIncCC_reco_electron_momentum>0)',
			'xsecflux_var': var_name_map['electron_momentum'],
			'rebin_config': {
				'type': 'constant',
				'factor': 2,
				'overflow': True
			}
		},
		'electron_costheta': {
			'var':          'nueIncCC_reco_electron_costheta',
			'nbins':        20,
			'xmin':         -1.0,
			'xmax':         1.0,
			'title':        plot_title + '; Reconstructed Electron cos(#theta); ' + legend_POT_string,
			'cut_suffix':   '&& (nueIncCC_reco_electron_costheta>-900)',
			'xsecflux_var': var_name_map['electron_costheta'],
			'rebin_config': {
				'type': 'range',
				'xmin': 0.0,
				'xmax': 1.0,
				'underflow': True
			}
		}
	}

# ---------------------------------------------------------------------------
# Load xsecflux uncertainties
# ---------------------------------------------------------------------------

xsecflux_hists = {}

if run_num == 4:
	# Combine across 4b/4c/4d sub-runs for each neutrino sample
	for xsample_name in ['numu', 'nue']:
		xsecflux_hists[xsample_name] = {}

		for var in xsecflux_variables:
			print(f"\nCombining xsecflux uncertainties for {xsample_name}, variable {var}")

			combined_cv         = None
			combined_flux_var   = None
			combined_xsec_var   = None
			combined_reint_var  = None
			combined_param_vars = {}

			for run_label in run4_labels:
				xfile_key  = f"{xsample_name}_{run_label}"
				xfile_path = xsecflux_files.get(xfile_key)

				if not xfile_path or not os.path.exists(xfile_path):
					print(f"  Warning: File not found for {run_label}, skipping")
					continue

				xfile = rt.TFile(xfile_path)
				if xfile.IsZombie():
					print(f"  Warning: Could not open file for {run_label}, skipping")
					continue

				xsample = xsecflux_sample_map[run_label][xsample_name]
				hists_with_errors = make_hist_w_errors(
					xfile, var, xsample,
					flux_params, xsec_params, reint_params, _xsec_detector
				)
				if not hists_with_errors:
					print(f"  Warning: Could not load histograms for {run_label}")
					xfile.Close()
					continue

				# Detach from file before closing
				hists_with_errors['cv'].SetDirectory(0)
				hists_with_errors['fluxvar'].SetDirectory(0)
				hists_with_errors['xsecvar'].SetDirectory(0)
				hists_with_errors['reintvar'].SetDirectory(0)
				for pname, h in hists_with_errors['param_vars'].items():
					h.SetDirectory(0)

				# Initialise combined histograms on first successful load
				if combined_cv is None:
					combined_cv = hists_with_errors['cv'].Clone(
						f"h{var}_{xsample_name}_combined_cv")
					combined_cv.SetDirectory(0)
					combined_cv.Reset()

					combined_flux_var = hists_with_errors['fluxvar'].Clone(
						f"h{var}_{xsample_name}_combined_flux_variance")
					combined_flux_var.SetDirectory(0)
					combined_flux_var.Reset()

					combined_xsec_var = hists_with_errors['xsecvar'].Clone(
						f"h{var}_{xsample_name}_combined_xsec_variance")
					combined_xsec_var.SetDirectory(0)
					combined_xsec_var.Reset()

					combined_reint_var = hists_with_errors['reintvar'].Clone(
						f"h{var}_{xsample_name}_combined_reint_variance")
					combined_reint_var.SetDirectory(0)
					combined_reint_var.Reset()

					for pname, h in hists_with_errors['param_vars'].items():
						h_comb = h.Clone(f"h{var}_{xsample_name}_{pname}_combined_variance")
						h_comb.SetDirectory(0)
						h_comb.Reset()
						combined_param_vars[pname] = h_comb

				combined_cv.Add(hists_with_errors['cv'])
				combined_flux_var.Add(hists_with_errors['fluxvar'])
				combined_xsec_var.Add(hists_with_errors['xsecvar'])
				combined_reint_var.Add(hists_with_errors['reintvar'])
				for pname, h in hists_with_errors['param_vars'].items():
					if pname in combined_param_vars:
						combined_param_vars[pname].Add(h)

				print(f"  Added {run_label} to combined uncertainties")
				xfile.Close()

			if combined_cv is not None:
				xsecflux_hists[xsample_name][var] = {
					'cv':         combined_cv,
					'fluxvar':    combined_flux_var,
					'xsecvar':    combined_xsec_var,
					'reintvar':   combined_reint_var,
					'param_vars': combined_param_vars
				}
				print(f"  Successfully combined uncertainties for {xsample_name}, variable {var}")
			else:
				print(f"  Warning: No valid xsecflux files found for {xsample_name}, variable {var}")

else:
	for xsample_name in ['numu', 'nue']:
		xsecflux_hists[xsample_name] = {}

		for var in xsecflux_variables:
			print(f"\nLoading xsecflux uncertainties for {xsample_name}, variable {var}")

			xfile_path = xsecflux_files.get(xsample_name)

			if not xfile_path or not os.path.exists(xfile_path):
				print(f"  Warning: File not found for {xsample_name}, skipping")
				continue

			xfile = rt.TFile(xfile_path)
			if xfile.IsZombie():
				print(f"  Warning: Could not open file for {xsample_name}, skipping")
				continue

			xsample = xsecflux_sample_map[xsample_name]
			hists_with_errors = make_hist_w_errors(
				xfile, var, xsample,
				flux_params, xsec_params, reint_params, _xsec_detector
			)
			if not hists_with_errors:
				print(f"  Warning: Could not load histograms for {xsample_name}")
				xfile.Close()
				continue

			# Detach from file before closing
			hists_with_errors['cv'].SetDirectory(0)
			hists_with_errors['fluxvar'].SetDirectory(0)
			hists_with_errors['xsecvar'].SetDirectory(0)
			hists_with_errors['reintvar'].SetDirectory(0)
			for pname, h in hists_with_errors['param_vars'].items():
				h.SetDirectory(0)

			xsecflux_hists[xsample_name][var] = hists_with_errors
			print(f"  Successfully loaded uncertainties for {xsample_name}, variable {var}")
			xfile.Close()

# ---------------------------------------------------------------------------
# Load detector variations
# ---------------------------------------------------------------------------

detsys_hists = {}
if detsys_file is not None:
	print(f"\nLoading detector variations from {detsys_file}")
	if os.path.exists(detsys_file):
		dfile = rt.TFile(detsys_file)
		if not dfile.IsZombie():
			for var in detsys_variables:
				print(f"  Loading detector variations for {var}")
				result = load_detector_variations(dfile, var, detsys_params)
				if result is not None:
					detsys_hists[var] = result
			dfile.Close()
		else:
			print("  Warning: Could not open detector systematics file")
	else:
		print(f"  Warning: Detector systematics file not found: {detsys_file}")

# ---------------------------------------------------------------------------
# Main plotting loop
# ---------------------------------------------------------------------------

for var_name, var_info in variables.items():
	print(f"\n{'='*60}")
	print(f"Plotting variable: {var_name}  ({var_info['var']})")
	print(f"{'='*60}")

	nbins = var_info['nbins']
	xmin  = var_info['xmin']
	xmax  = var_info['xmax']
	full_cut = base_cut + var_info['cut_suffix']

	hists       = {}
	all_objects = []  # keep ROOT objects alive

	# -----------------------------------------------------------------------
	# Fill histograms per category
	# -----------------------------------------------------------------------

	# Also keep an unscaled total MC for statistical uncertainty
	h_total_mc_unscaled = rt.TH1D(
		f"h_{var_name}_total_mc_unscaled", "", nbins, xmin, xmax)
	h_total_mc_unscaled.Sumw2()

	for cat_name, cat_info in categories.items():
		hname = f"h_{var_name}_{cat_name}"
		h = rt.TH1D(hname, var_info['title'], nbins, xmin, xmax)
		h.Sumw2()

		if cat_name == 'data':
			# Data: sum from all data files
			if run_num == 4:
				for run_label in run4_labels:
					if 'data' not in trees.get(run_label, {}):
						continue
					trees[run_label]['data'].Draw(
						f"{var_info['var']}>>+{hname}",
						f"({full_cut})"
					)
			else:
				trees['data'].Draw(
					f"{var_info['var']}>>+{hname}",
					f"({full_cut})"
				)
		else:
			# MC: loop over contributing samples for this category
			for sample in cat_info['samples']:
				cat_cut = full_cut + cat_info['truth_cut']
				hname_tmp = f"htmp_{var_name}_{cat_name}_{sample}"
				h_tmp = rt.TH1D(hname_tmp, "", nbins, xmin, xmax)
				h_tmp.Sumw2()

				if run_num == 4:
					for run_label in run4_labels:
						if sample not in trees.get(run_label, {}):
							continue
						trees[run_label][sample].Draw(
							f"{var_info['var']}>>+{hname_tmp}",
							f"({cat_cut})*eventweight_weight"
						)
						# Accumulate unscaled MC (before POT scaling)
						if cat_name != 'cosmic':
							trees[run_label][sample].Draw(
								f"{var_info['var']}>>+h_{var_name}_total_mc_unscaled",
								f"({cat_cut})"
							)
						# Scale this sub-run's contribution
						h_tmp_subrun = rt.TH1D(
							f"htmp_{var_name}_{cat_name}_{sample}_{run_label}",
							"", nbins, xmin, xmax)
						h_tmp_subrun.Sumw2()
						trees[run_label][sample].Draw(
							f"{var_info['var']}>>+{h_tmp_subrun.GetName()}",
							f"({cat_cut})*eventweight_weight"
						)
						h_tmp_subrun.Scale(scaling[run_label][sample])
						h.Add(h_tmp_subrun)
						all_objects.append(h_tmp_subrun)
				else:
					trees[sample].Draw(
						f"{var_info['var']}>>+{hname_tmp}",
						f"({cat_cut})*eventweight_weight"
					)
					# Accumulate unscaled MC for statistical uncertainty
					if cat_name != 'cosmic':
						trees[sample].Draw(
							f"{var_info['var']}>>+h_{var_name}_total_mc_unscaled",
							f"({cat_cut})"
						)
					h_tmp.Scale(scaling[sample])
					h.Add(h_tmp)

				all_objects.append(h_tmp)

		# Style
		h.SetFillColor(cat_info['color'])
		h.SetFillStyle(cat_info.get('fill_style', 1001))
		if cat_name == 'data':
			h.SetFillStyle(0)
			h.SetLineColor(rt.kBlack)
			h.SetLineWidth(2)
			h.SetMarkerStyle(20)
			h.SetMarkerColor(rt.kBlack)
			h.SetMarkerSize(0.8)

		print(f"  {cat_name}: {h.Integral():.2f} events")
		hists[cat_name] = h

	# Build total MC (sum of all stack categories)
	h_total_mc = None
	for cat_name in stack_order:
		if cat_name not in hists:
			continue
		if h_total_mc is None:
			h_total_mc = hists[cat_name].Clone(f"h_{var_name}_total_mc")
			h_total_mc.SetDirectory(0)
		else:
			h_total_mc.Add(hists[cat_name])

	# -----------------------------------------------------------------------
	# Build THStack
	# -----------------------------------------------------------------------

	hstack_name = f"hs_{var_name}"
	hstack = rt.THStack(hstack_name, "")
	for cat_name in stack_order:
		if cat_name in hists:
			hstack.Add(hists[cat_name])

	# -----------------------------------------------------------------------
	# Build uncertainty histograms (total, per-category)
	# -----------------------------------------------------------------------

	h_uncertainty_total    = None
	h_uncertainty_flux     = None
	h_uncertainty_xsec     = None
	h_uncertainty_reint    = None
	h_uncertainty_detector = None
	h_uncertainty_params   = {}

	xsecflux_var = var_info['xsecflux_var']

	if h_total_mc is not None:
		h_uncertainty_total    = h_total_mc.Clone(f"h_uncertainty_total_{var_name}")
		h_uncertainty_flux     = h_total_mc.Clone(f"h_uncertainty_flux_{var_name}")
		h_uncertainty_xsec     = h_total_mc.Clone(f"h_uncertainty_xsec_{var_name}")
		h_uncertainty_reint    = h_total_mc.Clone(f"h_uncertainty_reint_{var_name}")
		h_uncertainty_detector = h_total_mc.Clone(f"h_uncertainty_detector_{var_name}")

		for h in [h_uncertainty_total, h_uncertainty_flux, h_uncertainty_xsec,
		          h_uncertainty_reint, h_uncertainty_detector]:
			h.SetDirectory(0)

		# Initialise per-parameter uncertainty histograms
		for xsample_name in ['nue', 'numu']:
			if (xsample_name in xsecflux_hists
			        and xsecflux_var in xsecflux_hists[xsample_name]
			        and 'param_vars' in xsecflux_hists[xsample_name][xsecflux_var]):
				for pname in xsecflux_hists[xsample_name][xsecflux_var]['param_vars']:
					if pname not in h_uncertainty_params:
						hp = h_total_mc.Clone(f"h_uncertainty_{pname}_{var_name}")
						hp.SetDirectory(0)
						h_uncertainty_params[pname] = hp

		for ibin in range(0, h_uncertainty_total.GetNbinsX() + 2):
			central = h_total_mc.GetBinContent(ibin)

			if central <= 0:
				for h in [h_uncertainty_total, h_uncertainty_flux,
				          h_uncertainty_xsec, h_uncertainty_reint, h_uncertainty_detector]:
					h.SetBinError(ibin, 0.0)
				for h in h_uncertainty_params.values():
					h.SetBinError(ibin, 0.0)
				continue

			abs_var_flux   = 0.0
			abs_var_xsec   = 0.0
			abs_var_reint  = 0.0
			frac_var_xsec_detector = 0.0
			abs_var_params = {pname: 0.0 for pname in h_uncertainty_params}

			# Accumulate absolute variances from each neutrino sample
			for xsample_name in ['nue', 'numu']:
				try:
					if (xsample_name not in xsecflux_hists
					        or xsecflux_var not in xsecflux_hists[xsample_name]):
						continue
					xsec_data = xsecflux_hists[xsample_name][xsecflux_var]

					cv_xf = xsec_data['cv'].GetBinContent(ibin)
					if cv_xf <= 0:
						continue

					abs_var_flux  += xsec_data['fluxvar'].GetBinContent(ibin)
					abs_var_xsec  += xsec_data['xsecvar'].GetBinContent(ibin)
					abs_var_reint += xsec_data['reintvar'].GetBinContent(ibin)

					for pname, hpv in xsec_data['param_vars'].items():
						if pname in abs_var_params:
							abs_var_params[pname] += hpv.GetBinContent(ibin)
				except Exception as e:
					print(f"  Warning: error accessing xsecflux bin {ibin} for {xsample_name}: {e}")

			# Detector uncertainty: stored as fractional variance; convert to absolute
			frac_var_detector = 0.0
			if xsecflux_var in detsys_hists:
				frac_var_detector = detsys_hists[xsecflux_var]['frac_variance'].GetBinContent(ibin)

			# Detector contribution from xsecflux file (runs 4/5)
			for xsample_name in ['nue', 'numu']:
				try:
					if (xsample_name not in xsecflux_hists
					        or xsecflux_var not in xsecflux_hists[xsample_name]):
						continue
					xsec_data = xsecflux_hists[xsample_name][xsecflux_var]
					cv_xf = xsec_data['cv'].GetBinContent(ibin)
					if cv_xf > 0:
						frac_var_xsec_detector += (
							xsec_data['detectorvar'].GetBinContent(ibin) / (cv_xf * cv_xf))
				except Exception:
					pass

			abs_var_detector = central * central * (frac_var_detector + frac_var_xsec_detector)

			# Statistical fractional variance: 1/N_unscaled
			n_unscaled = h_total_mc_unscaled.GetBinContent(ibin)
			frac_var_stat = (1.0 / n_unscaled) if n_unscaled > 0 else 0.0
			abs_var_stat  = central * central * frac_var_stat

			abs_var_total = abs_var_stat + abs_var_flux + abs_var_xsec + abs_var_reint + abs_var_detector

			h_uncertainty_total.SetBinError(ibin,    central * sqrt(max(abs_var_total    / (central * central), 0.0)))
			h_uncertainty_flux.SetBinError(ibin,     central * sqrt(max(abs_var_flux     / (central * central), 0.0)))
			h_uncertainty_xsec.SetBinError(ibin,     central * sqrt(max(abs_var_xsec     / (central * central), 0.0)))
			h_uncertainty_reint.SetBinError(ibin,    central * sqrt(max(abs_var_reint    / (central * central), 0.0)))
			h_uncertainty_detector.SetBinError(ibin, central * sqrt(max(abs_var_detector / (central * central), 0.0)))

			for pname in h_uncertainty_params:
				av = abs_var_params.get(pname, 0.0)
				h_uncertainty_params[pname].SetBinError(ibin, central * sqrt(max(av / (central * central), 0.0)))

		# Style uncertainty band
		h_uncertainty_total.SetFillColor(rt.kGray+1)
		h_uncertainty_total.SetFillStyle(3002)
		h_uncertainty_total.SetLineColor(rt.kGray+1)
		h_uncertainty_total.SetLineWidth(1)
		h_uncertainty_total.SetMarkerSize(0)

	# -----------------------------------------------------------------------
	# Create canvas (split into main + ratio panels when show_ratio is True)
	# -----------------------------------------------------------------------

	if show_ratio:
		canvas = rt.TCanvas(f"c_{var_name}", f"{var_name}", 800, 900)
		canvas.Draw()
		pad1 = rt.TPad(f"pad1_{var_name}", "", 0.0, 0.28, 1.0, 1.0)
		pad2 = rt.TPad(f"pad2_{var_name}", "", 0.0, 0.0,  1.0, 0.28)
		pad1.SetBottomMargin(0.02)
		pad1.SetTopMargin(0.07)
		pad1.SetLeftMargin(0.12)
		pad1.SetRightMargin(0.05)
		pad2.SetTopMargin(0.02)
		pad2.SetBottomMargin(0.30)
		pad2.SetLeftMargin(0.12)
		pad2.SetRightMargin(0.05)
		pad1.Draw()
		pad2.Draw()
		pad1.cd()
	else:
		canvas = rt.TCanvas(f"c_{var_name}", f"{var_name}", 800, 700)
		canvas.SetLeftMargin(0.12)
		canvas.SetRightMargin(0.05)
		canvas.Draw()
		canvas.cd()

	# -----------------------------------------------------------------------
	# Draw main distribution
	# -----------------------------------------------------------------------

	stack_max = hstack.GetMaximum() if hstack.GetHists() else 0
	data_max  = hists['data'].GetMaximum() if 'data' in hists else 0
	y_max     = max(stack_max, data_max) * 1.5

	if show_ratio:
		title_parts     = var_info['title'].split(';')
		title_no_xlabel = (title_parts[0] + '; ; ' + title_parts[2]
		                   if len(title_parts) > 2 else title_parts[0])
	else:
		title_no_xlabel = var_info['title']

	if stack_max >= data_max:
		hstack.SetTitle(title_no_xlabel)
		hstack.Draw("hist")
		hstack.SetMaximum(y_max)
		if show_ratio:
			hstack.GetXaxis().SetLabelSize(0)
			hstack.GetXaxis().SetTitleSize(0)
	else:
		hists['data'].SetTitle(title_no_xlabel)
		hists['data'].Draw("E1")
		hists['data'].SetMaximum(y_max)
		if show_ratio:
			hists['data'].GetXaxis().SetLabelSize(0)
			hists['data'].GetXaxis().SetTitleSize(0)
		hstack.Draw("histsame")

	if h_uncertainty_total is not None:
		h_uncertainty_total.Draw("E2same")

	if 'data' in hists:
		hists['data'].Draw("E1same")

	# Set x-axis range for cos theta (show forward hemisphere only)
	if var_name == 'electron_costheta':
		if hstack.GetHists():
			hstack.GetXaxis().SetRangeUser(0.0, 1.0)
		elif 'data' in hists:
			hists['data'].GetXaxis().SetRangeUser(0.0, 1.0)

	# Legend
	legend = rt.TLegend(0.65, 0.40 if show_ratio else 0.50, 0.89, 0.89)
	legend.SetTextSize(0.03)
	legend.SetFillStyle(0)
	legend.SetBorderSize(1)

	for cat_name in stack_order:
		if cat_name in hists and cat_name in categories:
			legend.AddEntry(hists[cat_name], categories[cat_name]['legend'], "f")
	if 'data' in hists:
		legend.AddEntry(hists['data'], categories['data']['legend'], "lep")
	if h_uncertainty_total is not None:
		legend.AddEntry(h_uncertainty_total, "Sys. unc.", "f")
	legend.Draw()

	if show_ratio:
		pad1.SetTickx(1)
		pad1.SetTicky(1)
	else:
		canvas.SetTickx(1)
		canvas.SetTicky(1)

	# -----------------------------------------------------------------------
	# Ratio panel: data / MC
	# -----------------------------------------------------------------------

	if show_ratio and 'data' in hists and h_total_mc is not None:
		pad2.cd()

		h_ratio = hists['data'].Clone(f"h_ratio_{var_name}")
		h_ratio.SetDirectory(0)
		h_ratio.Divide(h_total_mc)

		h_ratio_unc = h_total_mc.Clone(f"h_ratio_unc_{var_name}")
		h_ratio_unc.SetDirectory(0)
		for ibin in range(0, h_ratio_unc.GetNbinsX() + 2):
			mc_val = h_total_mc.GetBinContent(ibin)
			if mc_val > 0 and h_uncertainty_total is not None:
				frac_unc = h_uncertainty_total.GetBinError(ibin) / mc_val
				h_ratio_unc.SetBinContent(ibin, 1.0)
				h_ratio_unc.SetBinError(ibin, frac_unc)
			else:
				h_ratio_unc.SetBinContent(ibin, 1.0)
				h_ratio_unc.SetBinError(ibin, 0.0)

		title_parts  = var_info['title'].split(';')
		x_axis_title = title_parts[1].strip() if len(title_parts) > 1 else ""

		h_ratio.SetMinimum(0.5)
		h_ratio.SetMaximum(1.5)
		h_ratio.GetXaxis().SetTitle(x_axis_title)
		h_ratio.GetYaxis().SetTitle("Data / MC")
		h_ratio.GetXaxis().SetLabelSize(0.09)
		h_ratio.GetXaxis().SetTitleSize(0.10)
		h_ratio.GetXaxis().SetTitleOffset(1.1)
		h_ratio.GetXaxis().SetLabelOffset(0.01)
		h_ratio.GetYaxis().SetLabelSize(0.09)
		h_ratio.GetYaxis().SetTitleSize(0.10)
		h_ratio.GetYaxis().SetTitleOffset(0.3)
		h_ratio.GetYaxis().SetNdivisions(505)
		h_ratio.GetYaxis().CenterTitle(True)
		h_ratio.SetTitle("")
		h_ratio.SetMarkerStyle(20)
		h_ratio.SetMarkerSize(0.8)
		h_ratio.SetMarkerColor(rt.kBlack)
		h_ratio.SetLineColor(rt.kBlack)
		h_ratio.SetLineWidth(2)

		h_ratio_unc.SetFillColor(rt.kGray+1)
		h_ratio_unc.SetFillStyle(3002)
		h_ratio_unc.SetLineColor(rt.kGray+1)
		h_ratio_unc.SetMarkerSize(0)

		h_ratio.Draw("E1")
		h_ratio_unc.Draw("E2same")
		h_ratio.Draw("E1same")
		h_ratio.Draw("axissame")

		ref_line = rt.TLine(xmin, 1.0, xmax, 1.0)
		ref_line.SetLineStyle(2)
		ref_line.SetLineWidth(2)
		ref_line.SetLineColor(rt.kBlack)
		ref_line.Draw()

		pad2.SetTickx(1)
		pad2.SetTicky(1)
		all_objects += [h_ratio, h_ratio_unc, ref_line]

	canvas.Update()
	out.cd()
	canvas.Write()

	# -----------------------------------------------------------------------
	# Separate canvas: fractional uncertainty breakdown by source
	# -----------------------------------------------------------------------

	if h_total_mc is not None and h_uncertainty_total is not None:
		canvas_frac = rt.TCanvas(
			f"c_{var_name}_frac_error", f"{var_name} Fractional Uncertainty", 1000, 600)
		canvas_frac.SetLeftMargin(0.12)
		canvas_frac.SetRightMargin(0.05)
		canvas_frac.Draw()
		canvas_frac.SetTickx(1)
		canvas_frac.SetTicky(1)

		h_frac_total    = h_total_mc.Clone(f"h_frac_total_{var_name}");    h_frac_total.SetDirectory(0);    h_frac_total.Reset()
		h_frac_stat     = h_total_mc.Clone(f"h_frac_stat_{var_name}");     h_frac_stat.SetDirectory(0);     h_frac_stat.Reset()
		h_frac_flux     = h_total_mc.Clone(f"h_frac_flux_{var_name}");     h_frac_flux.SetDirectory(0);     h_frac_flux.Reset()
		h_frac_xsec     = h_total_mc.Clone(f"h_frac_xsec_{var_name}");     h_frac_xsec.SetDirectory(0);     h_frac_xsec.Reset()
		h_frac_reint    = h_total_mc.Clone(f"h_frac_reint_{var_name}");    h_frac_reint.SetDirectory(0);    h_frac_reint.Reset()
		h_frac_detector = h_total_mc.Clone(f"h_frac_detector_{var_name}"); h_frac_detector.SetDirectory(0); h_frac_detector.Reset()

		for ibin in range(0, h_total_mc.GetNbinsX() + 2):
			central = h_total_mc.GetBinContent(ibin)
			if central <= 0:
				continue

			n_unscaled    = h_total_mc_unscaled.GetBinContent(ibin)
			stat_frac     = (1.0 / sqrt(n_unscaled)) if n_unscaled > 0 else 0.0
			flux_frac     = h_uncertainty_flux.GetBinError(ibin)     / central
			xsec_frac     = h_uncertainty_xsec.GetBinError(ibin)     / central
			reint_frac    = h_uncertainty_reint.GetBinError(ibin)    / central
			detector_frac = h_uncertainty_detector.GetBinError(ibin) / central
			total_frac    = sqrt(stat_frac**2 + flux_frac**2 + xsec_frac**2
			                     + reint_frac**2 + detector_frac**2)

			h_frac_stat.SetBinContent(ibin,     stat_frac)
			h_frac_flux.SetBinContent(ibin,     flux_frac)
			h_frac_xsec.SetBinContent(ibin,     xsec_frac)
			h_frac_reint.SetBinContent(ibin,    reint_frac)
			h_frac_detector.SetBinContent(ibin, detector_frac)
			h_frac_total.SetBinContent(ibin,    total_frac)

		h_frac_total.SetLineColor(rt.kBlack);       h_frac_total.SetLineWidth(3)
		h_frac_stat.SetLineColor(rt.kGray+1);       h_frac_stat.SetLineWidth(2);  h_frac_stat.SetLineStyle(2)
		h_frac_flux.SetLineColor(rt.kBlue+1);       h_frac_flux.SetLineWidth(2)
		h_frac_xsec.SetLineColor(rt.kRed-4);        h_frac_xsec.SetLineWidth(2)
		h_frac_reint.SetLineColor(rt.kGreen+2);     h_frac_reint.SetLineWidth(2)
		h_frac_detector.SetLineColor(rt.kOrange+1); h_frac_detector.SetLineWidth(2)

		ymax_frac = max(h_frac_total.GetMaximum() * 1.4, 0.5)
		h_frac_total.SetTitle(
			plot_title + "; " + var_info['title'].split(';')[1] + "; Fractional Uncertainty")
		h_frac_total.SetMinimum(0.0)
		h_frac_total.SetMaximum(ymax_frac)
		h_frac_total.Draw("hist")
		h_frac_stat.Draw("histsame")
		h_frac_flux.Draw("histsame")
		h_frac_xsec.Draw("histsame")
		h_frac_reint.Draw("histsame")
		h_frac_detector.Draw("histsame")

		legend_frac = rt.TLegend(0.65, 0.50, 0.89, 0.89)
		legend_frac.SetTextSize(0.03)
		legend_frac.SetFillStyle(0)
		legend_frac.SetBorderSize(1)
		legend_frac.AddEntry(h_frac_total,    "Total",       "l")
		legend_frac.AddEntry(h_frac_stat,     "Statistical", "l")
		legend_frac.AddEntry(h_frac_flux,     "Flux",        "l")
		legend_frac.AddEntry(h_frac_xsec,     "Cross-sec.",  "l")
		legend_frac.AddEntry(h_frac_reint,    "Reinteract.", "l")
		legend_frac.AddEntry(h_frac_detector, "Detector",    "l")
		legend_frac.Draw()

		canvas_frac.Update()
		out.cd()
		canvas_frac.Write()

		all_objects += [canvas_frac, h_frac_total, h_frac_stat, h_frac_flux,
		                h_frac_xsec, h_frac_reint, h_frac_detector, legend_frac]

	all_objects += [canvas, hstack, h_total_mc, h_total_mc_unscaled,
	                h_uncertainty_total, h_uncertainty_flux, h_uncertainty_xsec,
	                h_uncertainty_reint, h_uncertainty_detector]
	all_objects += list(h_uncertainty_params.values())
	all_objects += list(hists.values())

# ---------------------------------------------------------------------------
# Write and close
# ---------------------------------------------------------------------------

out.Write()
out.Close()
print(f"\nDone. Output written to: {out_name}")