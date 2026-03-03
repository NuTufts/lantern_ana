import os,sys
import ROOT as rt
import array
from math import sqrt

run_num = 1

# lantern_dir = "/cluster/tufts/wongjiradlabnu/zimani01/lantern/lantern_ana/"
lantern_dir = "/exp/uboone/app/users/imani/lantern_ana/"

## Run 1 
if run_num == 1: 
	targetpot = 4.4e19
	scaling = {"numu":targetpot/4.675690535431973e+20,
			"nue":targetpot/9.662529168587103e+22,
			"extbnb":(176153.0)/(433446.0),
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_nu_20260302_163929.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_nue_20260302_164813.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_extbnb_20260302_165918.root",
			"data":f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_data_5e19_20260302_170325.root"}
	xsecflux_files = {
		"nue": f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_numu_bnb_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_numu_bnb_nu.root"
	}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run3mil/root_files/detsys_final/combined_run3mil_nu_CV.root"
	detsys_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	show_data = True 
	data_legend = "Run1 5e19"
	plot_title = "Run 1: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run1_hists.root"
	xsecflux_variables = ['visible_energy', 'muon_momentum', 'muon_angle']
	var_name_map = {
	'neutrino_energy': 'visible_energy',
	'muon_momentum': 'muon_momentum',
	'muon_costheta': 'muon_angle'
	}
	xsecflux_sample_map = {
		'numu': 'run1_nu',
		'nue': 'run1_nue'
	}
	detsys_params = [
		"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ", 
		"LYAtt", "LYDown", "LYRayleigh",
		"recomb2", "SCE",
		"wiremodeThetaXZ", "wiremodeThetaYZ"
	]


## Run 3b
if run_num == 3: 
	# targetpot =  6.67e20
	targetpot = 4.4e19
	scaling = {"numu":targetpot/8.98323351831587e+20,
			"nue":targetpot/4.702159572049976e+22,
			"extbnb":(176153)/(223580),  # Trigger ratio
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_bnb_nu_overlay_20260112_154048.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_bnb_nue_overlay_20260112_155555.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_extbnb_20260112_160141.root",
			"data":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_data_20260112_175802.root"}
	xsecflux_files = {
		"nue": f"{lantern_dir}/all_runs_mmr/run3/root_files/xsecflux/run3b_numu_covar_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run3/root_files/xsecflux/run3b_numu_covar_nu.root"
	}
	detsys_file = None
	detsys_params = []
	detsys_variables = []
	show_data = True 
	data_legend = "Run1 5e19"
	plot_title = "Run 3: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu_run3_hists.root"
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'reco_neutrino_energy',
	'muon_momentum': 'reco_muon_momentum',
	'muon_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'numu': 'run3b_nu',
		'nue': 'run3b_nue'
	}

## Run 3mil
if run_num == 30: 
	targetpot = 8.806e18
	scaling = {"numu":targetpot/1.346689484233034e+21,
			"nue":targetpot/2.891774385462469e+22,
			# "extbnb":(176153)/(223580),  # Trigger ratio 3b
			"extbnb": (2263559.0)/(19214565.0),
			# "extbnb":(176153.0)/(19214565),  # Trigger ratio 3b
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_nu_20260211_143930.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_nue_20260123_181343.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_extbnb_20260112_160141.root",
			"data":f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_data_20260126_180100.root"}
	xsecflux_files = {
		"nue": f"{lantern_dir}/all_runs_mmr/run3mil/root_files/xsecflux/xsecflux_run3mil_numu_bnb_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run3mil/root_files/xsecflux/xsecflux_run3mil_numu_bnb_nu.root"
	}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run3mil/root_files/detsys_final/combined_run3mil_nu_CV.root"
	detsys_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	show_data = False 
	data_legend = "Run3 Data"
	plot_title = "Run 3: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run3mil_hists.root"
	xsecflux_variables = ['visible_energy', 'reco_muon_momentum', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'visible_energy',
	'muon_momentum': 'reco_muon_momentum',
	'muon_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'nue': 'run3mil_nue', # Not used, but keeping for consistency
		'numu': 'run3mil_nu'  
	}
	detsys_params = [
		"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ", 
		"LYAtt", "LYDown", "LYRayleigh",
		"recomb2", "SCE",
		"wiremodeThetaXZ", "wiremodeThetaYZ"
	]


## Combined Run 4 (4a + 4b + 4c + 4d)
if run_num == 4:
	# Calculate total target POT from all sub-runs
	# 4a: 4.483e+19, 4b: 1.45e+20, 4c: 9.106e+19, 4d: 5.015e+19
	# targetpot = 4.483e+19 + 1.45e+20 + 9.106e+19 + 5.015e+19 
	targetpot = 1.45e+20 + 9.106e+19 + 5.015e+19 

	
	# Define scaling factors for each sub-run
	# scaling_4a = {
	# 	"numu": 4.483e+19/2.34925e+20,
	# 	"nue": 4.483e+19/3.68033e+22,
	# 	"extbnb": 9867464.0/27940007.0,
	# 	"data": 1.0
	# }
	
	scaling_4b = {
		"numu": 1.45e+20/7.881656209241413e+20,
		"nue": 1.45e+20/1.1785765118473412e+23,
		"extbnb": 34317881.0/96638186.0,
		"data": 1.0
	}
	
	scaling_4c = {
		"numu": 0.65 * 9.106e+19/2.8777157789184374e+20, # HACK
		"nue": 9.106e+19/7.160248800041886e+22,
		"extbnb": 20644587.0/54566891.0,
		"data": 1.0
	}
	
	scaling_4d = {
		"numu": 0.5 * 5.015e+19/4.029820515210945e+20,  # HACK
		"nue": 5.015e+19/1.3740045183260529e+23,
		"extbnb": 11403578.0/78224187.0,
		"data": 1.0
	}
	
	# Store scaling factors for each sub-run
	scaling = {
		# '4a': scaling_4a,
		'4b': scaling_4b,
		'4c': scaling_4c,
		'4d': scaling_4d
	}
	
	# Define files for all sub-runs
	# files_4a = {
	# 	"numu": f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_nu_20260211_004950.root",
	# 	"nue": f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_nue_20260211_005826.root",
	# 	"extbnb": f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_extbnb_20260211_010851.root",
	# 	"data": f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_data_20260211_010300.root"
	# }
	
	files_4b = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nu_overlay_20260210_180525.root",
		"nue": f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nue_overlay_20260114_205851.root",
		"extbnb": f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_extbnb_20260114_212008.root",
		"data": f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_data_20260114_212707.root"
	}
	
	files_4c = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nu_20260210_183615.root",
		"nue": f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nue_20260210_185504.root",
		"extbnb": f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_extbnb_20260210_190529.root",
		"data": f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_data_20260210_192923.root"
	}
	
	files_4d = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nu_20260210_184026.root",
		"nue": f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nue_20260210_191735.root",
		"extbnb": f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_extbnb_20260210_193818.root",
		"data": f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_data_20260210_201556.root"
	}
	
	# Store all file sets
	# files = {'4a': files_4a, '4b': files_4b, '4c': files_4c, '4d': files_4d}
	files = {'4b': files_4b, '4c': files_4c, '4d': files_4d}

	
	# Xsecflux files from all runs
	xsecflux_files = {
		# "numu_4a": f"{lantern_dir}/all_runs_mmr/run4a/root_files/xsecflux/xsecflux_numu_nu.root",
		# "nue_4a": f"{lantern_dir}/all_runs_mmr/run4a/root_files/xsecflux/xsecflux_numu_nue.root",
		"numu_4b": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_run4b_numu_nu.root",
		"nue_4b": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_run4b_numu_nue.root",
		"numu_4c": f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_numu_nu.root",
		"nue_4c": f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_numu_nue.root",
		"numu_4d": f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_numu_nu.root",
		"nue_4d": f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_numu_nue.root"
	}
	
	# Xsecflux sample name mapping for each sub-run
	xsecflux_sample_map = {
		# '4a': {'nue': 'run4a_nue', 'numu': 'run4a_nu'},
		'4b': {'nue': 'run4b_nue', 'numu': 'run4b_nu'},
		'4c': {'nue': 'run4c_nue', 'numu': 'run4c_nu'},
		'4d': {'nue': 'run4d_nue', 'numu': 'run4d_nu'}
	}
	
	# Use run4b detector systematics (applied to all sub-runs)
	detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nu_cv.root"
	
	show_data = False
	data_legend = f"Run4 Data"
	plot_title = "Run 4: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run4_combined_hists.root"
	
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	detsys_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	
	var_name_map = {
		'neutrino_energy': 'reco_neutrino_energy',
		'muon_momentum': 'reco_muon_momentum',
		'muon_costheta': 'reco_cos_theta'
	}
	
	# Detector variation parameters
	detsys_params = [
		"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ", 
		"LYAtt", "LYDown", "LYRayleigh",
		"recomb2", "SCE"
	]

## Run 4a
if run_num == 41: 
	# targetpot = 5.523e+19
	# scaling = {"numu":targetpot/2.34925e+20,
	# 		"nue":targetpot/3.680332404967062e+22,
	# 		"extbnb":12298682.0/36162921.0,
	# 		"data":1.0}
	targetpot = 4.483e+19
	scaling = {"numu":targetpot/2.34925e+20,
			"nue":targetpot/3.68033e+22,
			"extbnb":9867464.0/27940007.0,
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_nu_20260211_004950.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_nue_20260211_005826.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_extbnb_20260211_010851.root",
			"data":f"{lantern_dir}/all_runs_mmr/run4a/root_files/selection/run4a_data_20260211_010300.root"}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4a/root_files/xsecflux/xsecflux_numu_nu.root",
		"nue": f"{lantern_dir}/all_runs_mmr/run4a/root_files/xsecflux/xsecflux_numu_nue.root"
		}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nu_cv.root"
	show_data = True 
	data_legend = "Run4a Data"
	plot_title = "Run 4a: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run4a_hists.root"
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	detsys_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'reco_neutrino_energy',
	'muon_momentum': 'reco_muon_momentum',
	'muon_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'nue': 'run4a_nue', # Not used, but keeping for consistency
		'numu': 'run4a_nu'  
	}
	# Detector variation parameters
	detsys_params = [
		"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ", 
		"LYAtt", "LYDown", "LYRayleigh",
		"recomb2", "SCE"
	]

## Run 4b 
if run_num == 42: 
	targetpot = 1.45e+20
	scaling = {"numu":targetpot/7.881656209241413e+20,
			"nue":targetpot/1.1785765118473412e+23,
			"extbnb":34317881.0/96638186.0,
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nu_overlay_20260210_180525.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nue_overlay_20260114_205851.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_extbnb_20260114_212008.root",
			"data":f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_data_20260114_212707.root"}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_run4b_numu_nu.root",
		"nue": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_run4b_numu_nue.root"
		}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nu_cv.root"
	show_data = True 
	data_legend = "Run4b Data"
	plot_title = "Run 4b: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run4b_hists.root"
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	detsys_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'reco_neutrino_energy',
	'muon_momentum': 'reco_muon_momentum',
	'muon_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'nue': 'run4b_nue', # Not used, but keeping for consistency
		'numu': 'run4b_nu'  
	}
	# Detector variation parameters
	detsys_params = [
		"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ", 
		"LYAtt", "LYDown", "LYRayleigh",
		"recomb2", "SCE"
	]

## Run 4c
if run_num == 43: 
	targetpot = 9.106e+19
	scaling = {"numu":targetpot/2.8777157789184374e+20,
			"nue":targetpot/7.160248800041886e+22,
			"extbnb":20644587.0/54566891.0,
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nu_20260210_183615.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nue_20260210_185504.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_extbnb_20260210_190529.root",
			"data":f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_data_20260210_192923.root"}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_numu_nu.root",
		"nue": f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_numu_nue.root"
		}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run4c/root_files/detsys_final/detsys_cv_run4b_nu_cv.root"
	show_data = True 
	data_legend = "Run4c Data"
	plot_title = "Run 4c: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run4c_hists.root"
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	detsys_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'reco_neutrino_energy',
	'muon_momentum': 'reco_muon_momentum',
	'muon_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'nue': 'run4c_nue', # Not used, but keeping for consistency
		'numu': 'run4c_nu'  
	}
	# Detector variation parameters
	detsys_params = [
		"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ", 
		"LYAtt", "LYDown", "LYRayleigh",
		"recomb2", "SCE"
	]

## Run 4d
if run_num == 44: 
	targetpot =  5.015e+19 
	scaling = {"numu":0.5*targetpot/4.029820515210945e+20, # HACK  
			"nue":targetpot/1.3740045183260529e+23,
			"extbnb":11403578.0/78224187.0,
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nu_20260210_184026.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nue_20260210_191735.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_extbnb_20260210_193818.root",
			"data":f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_data_20260210_201556.root"}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_numu_nu.root",
		"nue": f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_numu_nue.root"
		}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nu_cv.root"
	show_data = True 
	data_legend = "Run4d Data"
	plot_title = "Run 4d: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run4d_hists.root"
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	detsys_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'reco_neutrino_energy',
	'muon_momentum': 'reco_muon_momentum',
	'muon_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'nue': 'run4d_nue', # Not used, but keeping for consistency
		'numu': 'run4d_nu'  
	}
	# Detector variation parameters
	detsys_params = [
		"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ", 
		"LYAtt", "LYDown", "LYRayleigh",
		"recomb2", "SCE"
	]

## Run 5 
if run_num == 5: 
	targetpot = 1.545e+20
	scaling = {"numu":targetpot/9.976307163316628e+20,
			"nue":targetpot/1.5178517202061622e+23,
			"extbnb":36991964.0/120139886.0,
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_nu_20260210_182946.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_nue_20260210_191318.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_extbnb_20260210_193703.root",
			"data":f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_data_20260210_202728.root"}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run5/root_files/xsecflux/xsecflux_numu_nu.root",
		"nue": f"{lantern_dir}/all_runs_mmr/run5/root_files/xsecflux/xsecflux_numu_nue.root"
		}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run5/root_files/detsys/detsys_cv_run5_nu_cv.root"
	show_data = True 
	data_legend = "Run5 "
	plot_title = "Run 5: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run5_hists.root"
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	detsys_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'reco_neutrino_energy',
	'muon_momentum': 'reco_muon_momentum',
	'muon_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'nue': 'run5_nue', # Not used, but keeping for consistency
		'numu': 'run5_nu'  
	}
	# Detector variation parameters
	detsys_params = [
		"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ", 
		"LYAtt", "LYDown", "LYRayleigh",
		"recomb2", "SCE"
	]


# Function to identify systematic type based on name
def identify_systematic_type(syst_name):
	"""Identify if systematic is flux, xsec, reinteraction, or detector based on name"""
	syst_lower = syst_name.lower()
	
	# Flux keywords
	flux_keywords = ['flux', 'horn', 'beam', 'kminus', 'kplus', 'kzero', 
					 'nucleon', 'expskin', 'pion']
	
	# Reinteraction keywords
	reint_keywords = ['reint', 'fsi', 'absorption', 'charge_exchange', 
					 'elastic', 'inelastic', 'pion_prod', 'geant4']
	
	# Detector keywords
	detector_keywords = ['detvar', 'wire', 'recomb', 'sce', 'lifetime', 
						 'diffusion', 'saturation', 'dedx', 'wiremod',
						 'x_', 'yz_']
	
	# Check flux first
	for keyword in flux_keywords:
		if keyword in syst_lower:
			return 'flux'
	
	# Check reinteraction
	for keyword in reint_keywords:
		if keyword in syst_lower:
			return 'reint'
	
	# Check detector
	for keyword in detector_keywords:
		if keyword in syst_lower:
			return 'detector'
	
	# Default to cross section
	return 'xsec'


if run_num in [1,3, 30]:
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
	xsec = [
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
	reint = [
		"reinteractions_piminus_Geant4",
		"reinteractions_piplus_Geant4",
		"reinteractions_proton_Geant4"
	]
	detector = []

	all_pars = flux_params+xsec+reint+detector

if run_num in [4, 41, 42, 43, 44, 5]: 
	flux_params = [
		"flux_all"
	] 
	xsec = [
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
	reint = [
    	"reint_all"
	]
	detector = [
		"detvar_all"
	]

	all_pars = flux_params + xsec + reint + detector

def load_detector_variations(rfile, varname, detsys_params):
	"""Load detector variation histograms and calculate fractional uncertainties"""
	
	if rfile is None or rfile.IsZombie():
		print(f"  Warning: Invalid detector systematics file")
		return None
	
	detector_hists = {}
	
	# Try to find a CV histogram to get binning
	h_reference = None
	for param in detsys_params:
		cv_name = f"h{varname}__{param}__cv"
		h_temp = rfile.Get(cv_name)
		if h_temp and not h_temp.IsZombie():
			h_reference = h_temp
			break
	
	if h_reference is None:
		print(f"  Warning: Could not find reference histogram for {varname}")
		return None
	
	# Create combined fractional variance histogram
	h_frac_var = h_reference.Clone(f"h{varname}__detector_frac_variance")
	h_frac_var.Reset()
	
	# Process each detector parameter
	n_loaded = 0
	for param in detsys_params:
		cv_name = f"h{varname}__{param}__cv"
		var_name = f"h{varname}__{param}__var"
		
		h_cv = rfile.Get(cv_name)
		h_var = rfile.Get(var_name)
		
		if not h_cv or h_cv.IsZombie():
			print(f"    Skipping {param} - CV histogram not found")
			continue
		
		if not h_var or h_var.IsZombie():
			print(f"    Skipping {param} - variation histogram not found")
			continue
		
		n_loaded += 1
		print(f"    Loaded {param}")
		
		# Calculate fractional variance for this parameter
		for ibin in range(0, h_frac_var.GetNbinsX() + 2):
			cv_val = h_cv.GetBinContent(ibin)
			var_val = h_var.GetBinContent(ibin)
			
			if cv_val > 0:
				# Fractional difference: (var - cv) / cv
				frac_diff = (var_val - cv_val) / cv_val
				# Add squared fractional difference to variance
				current_var = h_frac_var.GetBinContent(ibin)
				h_frac_var.SetBinContent(ibin, current_var + frac_diff**2)
	
	print(f"  Loaded {n_loaded}/{len(detsys_params)} detector variations for {varname}")
	
	detector_hists['frac_variance'] = h_frac_var
	detector_hists['n_params'] = n_loaded
	
	return detector_hists

def make_hist_w_errors(rfile, varname, sample, parlist):
	"""Load histograms and separate into flux, xsec, reinteraction, and detector"""
	hists = {}
	
	# Try to find the CV histogram with different naming patterns
	possible_cv_names = [
		f"h{varname}_{sample}_cv",
		f"{varname}_{sample}_cv",
		f"h_{varname}_{sample}_cv"
	]
	
	hcv = None
	for cv_name in possible_cv_names:
		hcv = rfile.Get(cv_name)
		if hcv and not hcv.IsZombie():
			print(f"  Found CV histogram: {cv_name}")
			break
	
	if not hcv or hcv.IsZombie():
		print(f"  Warning: Could not find CV histogram for {varname}_{sample}")
		return None
	
	# Create variance histograms for each category
	hvar_flux = hcv.Clone(f"h{varname}__{sample}_flux_variance")
	hvar_flux.Reset()
	hvar_xsec = hcv.Clone(f"h{varname}__{sample}_xsec_variance")
	hvar_xsec.Reset()
	hvar_reint = hcv.Clone(f"h{varname}__{sample}_reint_variance")
	hvar_reint.Reset()
	hvar_detector = hcv.Clone(f"h{varname}__{sample}_detector_variance")
	hvar_detector.Reset()
	hvar_tot = hcv.Clone(f"h{varname}__{sample}_totvariance")
	hvar_tot.Reset()
	
	hmeans2 = hcv.Clone(f"h{varname}__{sample}_meanofmeans")
	hmeans2.Reset()
	
	# Process each parameter
	for parname in parlist:
		# Try different naming patterns
		possible_var_names = [
			f"h{varname}__{sample}__{parname}_variance",
			f"{varname}_{sample}_variance_{parname}",
			f"{varname}_{sample}_{parname}_variance"
		]
		
		possible_mean_names = [
			f"h{varname}__{sample}__{parname}_mean",
			f"{varname}_{sample}_mean_{parname}",
			f"{varname}_{sample}_{parname}_mean"
		]
		
		hmean = None
		hvar = None
		
		# Try to find variance histogram
		for var_name in possible_var_names:
			hvar = rfile.Get(var_name)
			if hvar and not hvar.IsZombie():
				break
		
		# Try to find mean histogram
		for mean_name in possible_mean_names:
			hmean = rfile.Get(mean_name)
			if hmean and not hmean.IsZombie():
				break
		
		if not hvar or hvar.IsZombie():
			print(f"    Skipping {parname} - variance histogram not found")
			continue
		
		if not hmean or hmean.IsZombie():
			print(f"    Skipping {parname} - mean histogram not found")
			continue
		
		hists[parname] = hvar
		
		# Identify the type of systematic
		syst_type = identify_systematic_type(parname)
				
		# Add variance to appropriate category
		for ibin in range(0, hvar_tot.GetXaxis().GetNbins()+1):
			xvar = hvar.GetBinContent(ibin)
			xmean = hmean.GetBinContent(ibin)
			
			if xmean > 0:
				scale_factor = hcv.GetBinContent(ibin) / xmean
				cv_var = xvar * scale_factor * scale_factor
			else:
				cv_var = 0.0
						
			# Add to total variance
			xvar_tot = hvar_tot.GetBinContent(ibin)
			hvar_tot.SetBinContent(ibin, xvar_tot + cv_var)
			
			# Add to category-specific variance
			if syst_type == 'flux':
				xvar_flux_bin = hvar_flux.GetBinContent(ibin)
				hvar_flux.SetBinContent(ibin, xvar_flux_bin + cv_var)
			elif syst_type == 'xsec':
				xvar_xsec_bin = hvar_xsec.GetBinContent(ibin)
				hvar_xsec.SetBinContent(ibin, xvar_xsec_bin + cv_var)
			elif syst_type == 'reint':
				xvar_reint_bin = hvar_reint.GetBinContent(ibin)
				hvar_reint.SetBinContent(ibin, xvar_reint_bin + cv_var)
			elif syst_type == 'detector':
				xvar_detector_bin = hvar_detector.GetBinContent(ibin)
				hvar_detector.SetBinContent(ibin, xvar_detector_bin + cv_var)
			
			# Add to mean
			xmean2 = hmeans2.GetBinContent(ibin)
			hmeans2.SetBinContent(ibin, xmean2 + xmean/len(parlist))
	
	# Set std for CV error (total only)
	for ibin in range(0, hvar_tot.GetXaxis().GetNbins()+1):
		stddev = sqrt(hvar_tot.GetBinContent(ibin))
		hcv.SetBinError(ibin, stddev)
	
	# Debug: Print summary of systematic counts
	n_flux = sum(1 for p in parlist if identify_systematic_type(p) == 'flux')
	n_xsec = sum(1 for p in parlist if identify_systematic_type(p) == 'xsec')
	n_reint = sum(1 for p in parlist if identify_systematic_type(p) == 'reint')
	n_detector = sum(1 for p in parlist if identify_systematic_type(p) == 'detector')
	print(f"  Systematic breakdown: {n_flux} flux, {n_xsec} xsec, {n_reint} reint, {n_detector} detector (total {len(parlist)})")
	
	hists['cv'] = hcv
	hists['mean2'] = hmeans2
	hists['totvar'] = hvar_tot
	hists['fluxvar'] = hvar_flux
	hists['xsecvar'] = hvar_xsec
	hists['reintvar'] = hvar_reint
	hists['detectorvar'] = hvar_detector
	
	return hists

rt.gStyle.SetOptStat(0)

tfiles = {}
trees = {}

# Handle combined run 4 differently
if run_num == 4:
	samples = ['nue','numu','extbnb','data']
	
	# Load files for all run4 sub-runs
	for run_label in ['4b', '4c', '4d']:
		tfiles[run_label] = {}
		trees[run_label] = {}
		for sample in samples:
			tfiles[run_label][sample] = rt.TFile(files[run_label][sample])
			trees[run_label][sample] = tfiles[run_label][sample].Get("analysis_tree")
			nentries = trees[run_label][sample].GetEntries()
			print(f"Run {run_label} sample={sample} has {nentries} entries")
else:
	samples = ['nue','numu','extbnb','data']
	for sample in samples:
		tfiles[sample] = rt.TFile(files[sample])
		trees[sample] = tfiles[sample].Get("analysis_tree")
		nentries = trees[sample].GetEntries()
		print(f"sample={sample} has {nentries} entries")

## Create output directory if it doesn't exist
out_dir = os.path.dirname(out_name)
if out_dir and not os.path.exists(out_dir):
	os.makedirs(out_dir)
	print(f"Created output directory: {out_dir}")

print(f"\nOutput file: {out_name}")

## Output file (must be set after loading samples)
out = rt.TFile(out_name,"recreate")

# Use the combined cut from the producer
base_cut = f"(numuIncCC_passes_all_cuts==1)"

# Define sample categories with ROOT standard colors
categories = {
	'cosmic': {
		'samples': ['extbnb'],
		'truth_cut': f' ',  # No truth cut for cosmic background
		'color': rt.kGray+2,
		'fill_style': 1001,
		'legend': 'BNB EXT'
	},
	'nc_nue': {
		'samples': ['nue'],
		'truth_cut': f' && (numuIncCC_is_nc_interaction==1)',
		'color': rt.kViolet-1,  # Purple   
		'fill_style': 1001,
		'legend': 'NC nue'
	},
	'cc_nue': {
		'samples': ['nue'], 
		'truth_cut': f' && (numuIncCC_is_cc_interaction==1)',
		'color': rt.kRed-4,  # Red/orange
		'fill_style': 1001,
		'legend': 'CC nue'
	},
	'nc_numu': {
		'samples': ['numu'],
		'truth_cut': f' && (numuIncCC_is_nc_interaction==1)', 
		'color': rt.kGreen+1,  # Green 
		'fill_style': 1001,
		'legend': 'NC numu'
	},
	'cc_numu': {
		'samples': ['numu'],
		'truth_cut': f' && (numuIncCC_is_cc_interaction==1)',
		'color': rt.kAzure+1,
		'fill_style': 1001,
		'legend': 'CC numu'
	},
	'data': {
		'samples': ['data'],
		'truth_cut': '',
		'color': rt.kBlack,
		'legend': data_legend
	}
}

if not show_data: 
	del categories['data']

legend_POT_string = " Events Per "+str(targetpot)+" POT"

# Define variables to plot - for muon neutrino analysis
variables = {
	'neutrino_energy': {
		'var': 'numuIncCC_reco_nu_energy',
		'true_var': 'numuIncCC_true_nu_energy',  # For efficiency
		'nbins': 20,
		'xmin': 0.0,
		'xmax': 2.0,
		'title': plot_title+'; Reconstructed Neutrino Energy (GeV); '+legend_POT_string,
		'cut_suffix': '',
		'has_overflow': True,
		'show_ratio': True  # Enable ratio plot for this variable
	# },
	# 'muon_momentum': {
	# 	'var': 'numuIncCC_reco_muon_momentum',
	# 	'true_var': 'numuIncCC_true_muon_momentum',  # For efficiency
	# 	'nbins': 25,
	# 	'xmin': 0.0,
	# 	'xmax': 1.5,
	# 	'title': plot_title+'; Reconstructed Muon Momentum (GeV); '+legend_POT_string,
	# 	'cut_suffix': '&& (numuIncCC_reco_muon_momentum>0)'
	# },
	# 'muon_costheta': {
	# 	'var': 'numuIncCC_reco_muon_costheta',
	# 	'true_var': 'numuIncCC_true_muon_costheta',  # For efficiency
	# 	'nbins': 20,
	# 	'xmin': -1.0,
	# 	'xmax': 1.0,
	# 	'title': plot_title+'; Reconstructed Muon cos(#theta); '+legend_POT_string,
	# 	'cut_suffix': '&& (numuIncCC_reco_muon_costheta>-900)'
	}
}

# Load xsecflux uncertainties for each sample
xsecflux_hists = {}

# Load xsecflux uncertainties for each sample
xsecflux_hists = {}

# Load xsecflux uncertainties for each sample
xsecflux_hists = {}

if run_num == 4:
	# For combined run 4, load xsecflux from all sub-runs and combine them
	
	for xsample_name in ['numu', 'nue']:
		xsecflux_hists[xsample_name] = {}
		
		for var in xsecflux_variables:
			print(f"\nCombining xsecflux uncertainties for {xsample_name}, variable {var}")
			
			# Storage for combined histograms
			combined_cv = None
			combined_flux_var = None
			combined_xsec_var = None
			combined_reint_var = None
			
			# Load from each sub-run
			for run_label in ['4b', '4c', '4d']:
				xfile_key = f"{xsample_name}_{run_label}"
				xfile_path = xsecflux_files.get(xfile_key)
				
				if not xfile_path or not os.path.exists(xfile_path):
					print(f"  Warning: File not found for {run_label}, skipping")
					continue
				
				xfile = rt.TFile(xfile_path)
				if xfile.IsZombie():
					print(f"  Warning: Could not open file for {run_label}, skipping")
					continue
				
				# Get sample name for this run
				xsample = xsecflux_sample_map[run_label][xsample_name]
				
				# Load histograms
				hists_with_errors = make_hist_w_errors(xfile, var, xsample, all_pars)
				if not hists_with_errors:
					print(f"  Warning: Could not load histograms for {run_label}")
					xfile.Close()
					continue
				
				# Detach histograms from file
				hists_with_errors['cv'].SetDirectory(0)
				hists_with_errors['fluxvar'].SetDirectory(0)
				hists_with_errors['xsecvar'].SetDirectory(0)
				hists_with_errors['reintvar'].SetDirectory(0)
				
				# Initialize combined histograms on first successful load
				if combined_cv is None:
					combined_cv = hists_with_errors['cv'].Clone(f"h{var}_{xsample_name}_combined_cv")
					combined_cv.SetDirectory(0)
					combined_cv.Reset()
					
					combined_flux_var = hists_with_errors['fluxvar'].Clone(f"h{var}_{xsample_name}_combined_flux_variance")
					combined_flux_var.SetDirectory(0)
					combined_flux_var.Reset()
					
					combined_xsec_var = hists_with_errors['xsecvar'].Clone(f"h{var}_{xsample_name}_combined_xsec_variance")
					combined_xsec_var.SetDirectory(0)
					combined_xsec_var.Reset()
					
					combined_reint_var = hists_with_errors['reintvar'].Clone(f"h{var}_{xsample_name}_combined_reint_variance")
					combined_reint_var.SetDirectory(0)
					combined_reint_var.Reset()
				
				# Add to combined histograms (CV and variances)
				combined_cv.Add(hists_with_errors['cv'])
				combined_flux_var.Add(hists_with_errors['fluxvar'])
				combined_xsec_var.Add(hists_with_errors['xsecvar'])
				combined_reint_var.Add(hists_with_errors['reintvar'])
				
				print(f"  Added {run_label} to combined uncertainties")
				
				# Close the file after we're done with it
				xfile.Close()
			
			# Store combined histograms
			if combined_cv is not None:
				xsecflux_hists[xsample_name][var] = {
					'cv': combined_cv,
					'fluxvar': combined_flux_var,
					'xsecvar': combined_xsec_var,
					'reintvar': combined_reint_var
				}
				print(f"  Successfully combined uncertainties for {xsample_name}, variable {var}")
			else:
				print(f"  Warning: No valid xsecflux files found for {xsample_name}, variable {var}")
else:
	for xsample_name, xfile_path in xsecflux_files.items():
		print(f"\nLoading xsecflux uncertainties from {xfile_path}")
		if not os.path.exists(xfile_path):
			print(f"  Warning: File not found, skipping")
			continue
			
		xfile = rt.TFile(xfile_path)
		if xfile.IsZombie():
			print(f"  Warning: Could not open file, skipping")
			continue
			
		xsecflux_hists[xsample_name] = {}
		
		# Get the correct sample name for this neutrino type
		xsample = xsecflux_sample_map.get(xsample_name, xsample_name)
		
		for var in xsecflux_variables:
			hists_with_errors = make_hist_w_errors(xfile, var, xsample, all_pars)
			if hists_with_errors:
				xsecflux_hists[xsample_name][var] = hists_with_errors
				print(f"  Loaded uncertainties for {xsample_name}, variable {var}")

# Load detector variations
detsys_hists = {}
if detsys_file is not None:
	print(f"\nLoading detector variations from {detsys_file}")
	if os.path.exists(detsys_file):
		dfile = rt.TFile(detsys_file)
		if not dfile.IsZombie():
			for var in detsys_variables:
				det_hists = load_detector_variations(dfile, var, detsys_params)
				if det_hists:
					detsys_hists[var] = det_hists
					print(f"  Loaded detector variations for {var}")
		else:
			print(f"  Warning: Could not open detector file")
	else:
		print(f"  Warning: Detector file not found")


# Create histograms for each variable
for var_name, var_info in variables.items():
	print(f"\n=== Creating {var_name} histogram ===")
	
	# Determine if we need ratio plot
	show_ratio = var_info.get('show_ratio', False) and show_data
	
	# Create canvas with or without ratio panel
	if show_ratio:
		canvas = rt.TCanvas(f"c_{var_name}", f"{var_name} Distribution", 1000, 1000)
		
		# Create pads manually for better control
		pad1 = rt.TPad("pad1", "pad1", 0.0, 0.3, 1.0, 1.0)
		pad1.SetBottomMargin(0.02)
		pad1.SetTopMargin(0.08)
		pad1.SetLeftMargin(0.12)
		pad1.SetRightMargin(0.05)
		pad1.SetTickx(1)
		pad1.SetTicky(1)
		pad1.Draw()
		
		pad2 = rt.TPad("pad2", "pad2", 0.0, 0.0, 1.0, 0.3)
		pad2.SetTopMargin(0.02)
		pad2.SetBottomMargin(0.35)
		pad2.SetLeftMargin(0.12)
		pad2.SetRightMargin(0.05)
		pad2.SetTickx(1)
		pad2.SetTicky(1)
		pad2.SetGridy(1)
		pad2.Draw()
		
		# Switch to top pad for main plot
		pad1.cd()
	else:
		canvas = rt.TCanvas(f"c_{var_name}", f"{var_name} Distribution", 1000, 800)
		canvas.Draw()

	hists = {}
	hists_unscaled = {}  # Track unscaled histograms for statistical errors
	total_events = {}

	# Create histograms for each category
	for cat_name, cat_info in categories.items():
		total_events[cat_name] = 0
		
		for sample in cat_info['samples']:
			# Construct full cut string
			full_cut = f"({base_cut}){cat_info['truth_cut']}{var_info['cut_suffix']}"
						
			# Create histogram name
			hname = f'h_{var_name}_{cat_name}_{sample}'
			hname_unscaled = f'h_{var_name}_{cat_name}_{sample}_unscaled'
			
			# Create histogram 
			hist = rt.TH1D(hname, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
			hist.Sumw2()
			
			# Create unscaled histogram
			hist_unscaled = rt.TH1D(hname_unscaled, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
			hist_unscaled.Sumw2()
			
			# Handle combined run 4
			if run_num == 4:
				# Create temporary histograms for each sub-run
				hist_temp = rt.TH1D(f"{hname}_temp", "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
				hist_temp.Sumw2()
				hist_unscaled_temp = rt.TH1D(f"{hname_unscaled}_temp", "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
				hist_unscaled_temp.Sumw2()
				
				# Fill from all sub-runs
				for run_label in ['4b', '4c', '4d']:
					hist_temp.Reset()
					hist_unscaled_temp.Reset()
					
					trees[run_label][sample].Draw(f"{var_info['var']}>>{hname}_temp", f"({full_cut})*eventweight_weight", "goff")
					trees[run_label][sample].Draw(f"{var_info['var']}>>{hname_unscaled}_temp", f"({full_cut})*eventweight_weight", "goff")
					
					# Scale and add using sub-run specific scaling
					hist_temp.Scale(scaling[run_label][sample])
					hist.Add(hist_temp)
					hist_unscaled.Add(hist_unscaled_temp)
			else:
				# Standard filling (for both scaled and unscaled)
				trees[sample].Draw(f"{var_info['var']}>>{hname}", f"({full_cut})*eventweight_weight", "goff")
				trees[sample].Draw(f"{var_info['var']}>>{hname_unscaled}", f"({full_cut})*eventweight_weight", "goff")

				# Scale by POT/exposure (only the main histogram)
				hist.Scale(scaling[sample])
			
			# Store in dictionary
			if cat_name not in hists:
				hists[cat_name] = hist.Clone(f"h_{var_name}_{cat_name}")
				hists[cat_name].Reset()
			
			if cat_name not in hists_unscaled:
				hists_unscaled[cat_name] = hist_unscaled.Clone(f"h_{var_name}_{cat_name}_unscaled")
				hists_unscaled[cat_name].Reset()
			
			# Add to category total
			hists[cat_name].Add(hist)
			hists_unscaled[cat_name].Add(hist_unscaled)
			total_events[cat_name] += hist.Integral()
			
			print(f"{cat_name}-{sample}: {hist.Integral():.2f} events")

			# Add event count to legend (avoid duplicates)
			if "(" not in categories[cat_name]['legend']: 
				categories[cat_name]['legend'] += f" ({hist.Integral():.1f})"

	# Set histogram styles
	for cat_name, cat_info in categories.items():
		if cat_name in hists:
			hist = hists[cat_name]
			
			if cat_name == 'data':
				hist.SetLineColor(cat_info['color'])
				hist.SetLineWidth(2)
				hist.SetMarkerStyle(20)
				hist.SetMarkerColor(rt.kBlack)
				hist.SetMarkerSize(0.8)
			else:
				hist.SetFillColor(cat_info['color'])
				hist.SetFillStyle(cat_info['fill_style'])
				hist.SetLineColor(cat_info['color'])
				hist.SetLineWidth(1)

	# Create stack for MC components (exclude data)
	stack_order = ['cosmic', 'nc_nue', 'cc_nue', 'nc_numu', 'cc_numu']
	hstack = rt.THStack(f"hs_{var_name}", "")

	# Create total MC histogram and unscaled MC histogram for statistical errors
	h_total_mc = None
	h_total_mc_unscaled = None
	for cat_name in stack_order:
		if cat_name in hists and cat_name != 'data':
			hstack.Add(hists[cat_name])
			if h_total_mc is None:
				h_total_mc = hists[cat_name].Clone(f"h_total_mc_{var_name}")
				h_total_mc_unscaled = hists_unscaled[cat_name].Clone(f"h_total_mc_unscaled_{var_name}")
			else:
				h_total_mc.Add(hists[cat_name])
				h_total_mc_unscaled.Add(hists_unscaled[cat_name])

	# Create uncertainty histograms (total and by category)
	h_uncertainty_total = None
	h_uncertainty_flux = None
	h_uncertainty_xsec = None
	h_uncertainty_reint = None
	h_uncertainty_detector = None
	
	if h_total_mc is not None:
		h_uncertainty_total = h_total_mc.Clone(f"h_uncertainty_total_{var_name}")
		h_uncertainty_flux = h_total_mc.Clone(f"h_uncertainty_flux_{var_name}")
		h_uncertainty_xsec = h_total_mc.Clone(f"h_uncertainty_xsec_{var_name}")
		h_uncertainty_reint = h_total_mc.Clone(f"h_uncertainty_reint_{var_name}")
		h_uncertainty_detector = h_total_mc.Clone(f"h_uncertainty_detector_{var_name}")
		
		# Map variable name
		xsecflux_var = var_name_map.get(var_name, var_name)
		
		# Apply xsecflux uncertainties
		for ibin in range(0, h_uncertainty_total.GetNbinsX() + 2):
			central = h_total_mc.GetBinContent(ibin)
			
			if central <= 0:
				# No events, no uncertainty
				h_uncertainty_total.SetBinError(ibin, 0.0)
				h_uncertainty_flux.SetBinError(ibin, 0.0)
				h_uncertainty_xsec.SetBinError(ibin, 0.0)
				h_uncertainty_reint.SetBinError(ibin, 0.0)
				h_uncertainty_detector.SetBinError(ibin, 0.0)
				continue
			
			# Initialize fractional variances
			frac_var_flux = 0.0
			frac_var_xsec = 0.0
			frac_var_reint = 0.0
			frac_var_detector = 0.0
			
			# Get fractional variances from each neutrino sample (for xsecflux)
			for xsample_name in ['nue', 'numu']:
				try:
					if xsample_name in xsecflux_hists and xsecflux_var in xsecflux_hists[xsample_name]:
						xsec_hists = xsecflux_hists[xsample_name][xsecflux_var]
						
						# Get the CV value from xsecflux file for this bin
						cv_from_xsecflux = xsec_hists['cv'].GetBinContent(ibin) if 'cv' in xsec_hists else 0.0
						
						if cv_from_xsecflux > 0:
							# Convert absolute variances to fractional variances
							if 'fluxvar' in xsec_hists:
								abs_var_flux = xsec_hists['fluxvar'].GetBinContent(ibin)
								frac_var_flux += abs_var_flux / (cv_from_xsecflux ** 2)
							if 'xsecvar' in xsec_hists:
								abs_var_xsec = xsec_hists['xsecvar'].GetBinContent(ibin)
								frac_var_xsec += abs_var_xsec / (cv_from_xsecflux ** 2)
							if 'reintvar' in xsec_hists:
								abs_var_reint = xsec_hists['reintvar'].GetBinContent(ibin)
								frac_var_reint += abs_var_reint / (cv_from_xsecflux ** 2)
				except (AttributeError, ReferenceError):
					continue
			
			# Add detector fractional variance from detsys file
			if xsecflux_var in detsys_hists and 'frac_variance' in detsys_hists[xsecflux_var]:
				frac_var_detector = detsys_hists[xsecflux_var]['frac_variance'].GetBinContent(ibin)
			
			# Statistical fractional uncertainty: 1/sqrt(n_unscaled)
			n_unscaled = h_total_mc_unscaled.GetBinContent(ibin)
			frac_var_stat = (1.0 / n_unscaled) if n_unscaled > 0 else 0.0
			
			# Total fractional variance (add in quadrature)
			frac_var_total = frac_var_stat + frac_var_flux + frac_var_xsec + frac_var_reint + frac_var_detector
			
			# Convert fractional variances to absolute errors
			abs_error_stat = central * sqrt(frac_var_stat)
			abs_error_flux = central * sqrt(frac_var_flux)
			abs_error_xsec = central * sqrt(frac_var_xsec)
			abs_error_reint = central * sqrt(frac_var_reint)
			abs_error_detector = central * sqrt(frac_var_detector)
			abs_error_total = central * sqrt(frac_var_total)
			
			# Set bin errors
			h_uncertainty_total.SetBinError(ibin, abs_error_total)
			h_uncertainty_flux.SetBinError(ibin, abs_error_flux)
			h_uncertainty_xsec.SetBinError(ibin, abs_error_xsec)
			h_uncertainty_reint.SetBinError(ibin, abs_error_reint)
			h_uncertainty_detector.SetBinError(ibin, abs_error_detector)
		
		# Set style for total uncertainty band
		h_uncertainty_total.SetFillColor(rt.kGray+1)
		h_uncertainty_total.SetFillStyle(3002)
		h_uncertainty_total.SetLineColor(rt.kGray+1)
		h_uncertainty_total.SetLineWidth(1)
		h_uncertainty_total.SetMarkerSize(0)

	# Draw histograms
	stack_max = hstack.GetMaximum() if hstack.GetHists() else 0
	data_max = hists['data'].GetMaximum() if 'data' in hists else 0
	y_max = max(stack_max, data_max) * 1.5

	# Adjust title for ratio plot
	if show_ratio:
		title_parts = var_info['title'].split(';')
		title_no_xlabel = title_parts[0] + ';' + '; ' + title_parts[2] if len(title_parts) > 2 else title_parts[0]
	else:
		title_no_xlabel = var_info['title']

	if stack_max > data_max:
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

	# Draw uncertainty band
	if h_uncertainty_total is not None:
		h_uncertainty_total.Draw("E2same")

	# Draw data on top
	if 'data' in hists:
		hists['data'].Draw("E1same")
	
	# Add overflow text for neutrino energy plot
	if var_name == 'neutrino_energy' and var_info.get('has_overflow', False):
		hist_for_axis = hstack if hstack.GetHists() else hists['data']
		last_bin = hist_for_axis.GetXaxis().GetNbins()
		x_pos = hist_for_axis.GetXaxis().GetBinCenter(last_bin)
		y_pos = -0.8

	# Create legend
	if show_ratio:
		legend = rt.TLegend(0.65, 0.40, 0.89, 0.89)
	else:
		legend = rt.TLegend(0.65, 0.50, 0.89, 0.89)
	legend.SetTextSize(0.03)
	legend.SetFillStyle(0)
	legend.SetBorderSize(1)

	# Add entries to legend
	for cat_name in stack_order:
		if cat_name in hists and cat_name in categories:
			legend.AddEntry(hists[cat_name], categories[cat_name]['legend'], "f")

	if 'data' in hists:
		legend.AddEntry(hists['data'], categories['data']['legend'], "lep")

	if h_uncertainty_total is not None:
		legend.AddEntry(h_uncertainty_total, "Sys. unc.", "f")

	legend.Draw()

	# Draw ratio plot if requested
	if show_ratio and 'data' in hists and h_total_mc is not None:
		# Switch to bottom pad
		pad2.cd()
		
		# Create ratio histogram
		h_ratio = hists['data'].Clone(f"h_ratio_{var_name}")
		h_ratio.Divide(h_total_mc)
		
		# Create uncertainty band for ratio (fractional uncertainties)
		h_ratio_unc = h_total_mc.Clone(f"h_ratio_unc_{var_name}")
		for ibin in range(0, h_ratio_unc.GetNbinsX() + 2):
			mc_val = h_total_mc.GetBinContent(ibin)
			if mc_val > 0:
				# Fractional uncertainty
				frac_unc = h_uncertainty_total.GetBinError(ibin) / mc_val
				h_ratio_unc.SetBinContent(ibin, 1.0)
				h_ratio_unc.SetBinError(ibin, frac_unc)
			else:
				h_ratio_unc.SetBinContent(ibin, 1.0)
				h_ratio_unc.SetBinError(ibin, 0.0)
		
		# Get axis title from main plot
		title_parts = var_info['title'].split(';')
		x_axis_title = title_parts[1].strip() if len(title_parts) > 1 else ""
		
		# Set range BEFORE drawing
		h_ratio.SetMinimum(0.5)
		h_ratio.SetMaximum(1.5)
		
		# Set axis titles BEFORE drawing
		h_ratio.GetXaxis().SetTitle(x_axis_title)
		h_ratio.GetYaxis().SetTitle("Data / MC")
		
		
		# Set axis properties BEFORE drawing
		# X-axis
		h_ratio.GetXaxis().SetLabelSize(0.09)
		h_ratio.GetXaxis().SetTitleSize(0.1)
		h_ratio.GetXaxis().SetTitleOffset(1.1)
		h_ratio.GetXaxis().SetLabelOffset(0.01)
		
		# Y-axis
		h_ratio.GetYaxis().SetLabelSize(0.09)
		h_ratio.GetYaxis().SetTitleSize(0.1)
		h_ratio.GetYaxis().SetTitleOffset(0.3)
		h_ratio.GetYaxis().SetNdivisions(505)
		h_ratio.GetYaxis().CenterTitle(True)
		
		# Style the data points
		h_ratio.SetTitle("")
		h_ratio.SetMarkerStyle(20)
		h_ratio.SetMarkerSize(0.8)
		h_ratio.SetMarkerColor(rt.kBlack)
		h_ratio.SetLineColor(rt.kBlack)
		h_ratio.SetLineWidth(2)
		
		# Style uncertainty band
		h_ratio_unc.SetFillColor(rt.kGray+1)
		h_ratio_unc.SetFillStyle(3002)
		h_ratio_unc.SetLineColor(rt.kGray+1)
		h_ratio_unc.SetMarkerSize(0)

		# NOW draw the histograms with explicit axis option
		h_ratio.Draw("E1")
		h_ratio_unc.Draw("E2same")
		h_ratio.Draw("E1same")
		h_ratio.Draw("axissame")  # This forces axis redraw
		
		# Add line at ratio = 1
		line = rt.TLine(var_info['xmin'], 1.0, var_info['xmax'], 1.0)
		line.SetLineStyle(2)
		line.SetLineColor(rt.kBlack)
		line.SetLineWidth(2)
		line.Draw("same")
		
		# Force updates
		pad2.Modified()
		pad2.Update()
		
		# Switch back to main canvas
		canvas.cd()

	if not show_ratio:
		canvas.SetTickx(1)
		canvas.SetTicky(1)
		canvas.SetLogy(0)
	canvas.Update()

	out.cd()
	canvas.Write()

	# === Create SEPARATE canvas for fractional error plot ===
	canvas_frac = rt.TCanvas(f"c_{var_name}_frac_total", f"{var_name} Fractional Error", 1000, 600)
	canvas_frac.Draw()
	canvas_frac.SetTickx(1)
	canvas_frac.SetTicky(1)
	
	# Create fractional error histograms for each category
	h_frac_stat = None
	h_frac_flux = None
	h_frac_xsec = None
	h_frac_reint = None
	h_frac_detector = None
	h_frac_total = None
	
	if h_total_mc is not None and h_uncertainty_total is not None:
		h_frac_stat = h_total_mc.Clone(f"h_frac_stat_{var_name}")
		h_frac_flux = h_total_mc.Clone(f"h_frac_flux_{var_name}")
		h_frac_xsec = h_total_mc.Clone(f"h_frac_xsec_{var_name}")
		h_frac_reint = h_total_mc.Clone(f"h_frac_reint_{var_name}")
		h_frac_detector = h_total_mc.Clone(f"h_frac_detector_{var_name}")
		h_frac_total = h_total_mc.Clone(f"h_frac_total_{var_name}")
		
		h_frac_stat.Reset()
		h_frac_flux.Reset()
		h_frac_xsec.Reset()
		h_frac_reint.Reset()
		h_frac_detector.Reset()
		h_frac_total.Reset()
		
		# Calculate fractional errors
		for ibin in range(0, h_total_mc.GetNbinsX() + 2):
			central = h_total_mc.GetBinContent(ibin)
			
			if central > 0:
				# Statistical uncertainty: 1/sqrt(n_unscaled)
				n_unscaled = h_total_mc_unscaled.GetBinContent(ibin)
				if n_unscaled > 0:
					stat_frac = 1.0 / sqrt(n_unscaled)
				else:
					stat_frac = 0.0
				
				# Systematic uncertainties
				flux_frac = h_uncertainty_flux.GetBinError(ibin) / central
				xsec_frac = h_uncertainty_xsec.GetBinError(ibin) / central
				reint_frac = h_uncertainty_reint.GetBinError(ibin) / central
				detector_frac = h_uncertainty_detector.GetBinError(ibin) / central
				
				# Total uncertainty (quadrature sum)
				total_frac = sqrt(stat_frac**2 + flux_frac**2 + xsec_frac**2 + reint_frac**2 + detector_frac**2)
				
				# Fill fractional error histograms
				h_frac_stat.SetBinContent(ibin, stat_frac)
				h_frac_flux.SetBinContent(ibin, flux_frac)
				h_frac_xsec.SetBinContent(ibin, xsec_frac)
				h_frac_reint.SetBinContent(ibin, reint_frac)
				h_frac_detector.SetBinContent(ibin, detector_frac)
				h_frac_total.SetBinContent(ibin, total_frac)
		
		# Set line styles (no filling, lines only)
		h_frac_stat.SetLineColor(rt.kGray+2)
		h_frac_stat.SetLineWidth(2)
		h_frac_stat.SetLineStyle(1)
		h_frac_stat.SetFillStyle(0)
		h_frac_stat.SetMarkerSize(0)
		
		h_frac_flux.SetLineColor(rt.kGreen+2)
		h_frac_flux.SetLineWidth(2)
		h_frac_flux.SetLineStyle(1)
		h_frac_flux.SetFillStyle(0)
		h_frac_flux.SetMarkerSize(0)
		
		h_frac_xsec.SetLineColor(rt.kRed)
		h_frac_xsec.SetLineWidth(2)
		h_frac_xsec.SetLineStyle(1)
		h_frac_xsec.SetFillStyle(0)
		h_frac_xsec.SetMarkerSize(0)
		
		h_frac_reint.SetLineColor(rt.kMagenta+1)
		h_frac_reint.SetLineWidth(2)
		h_frac_reint.SetLineStyle(1)
		h_frac_reint.SetFillStyle(0)
		h_frac_reint.SetMarkerSize(0)
		
		h_frac_detector.SetLineColor(rt.kBlue)
		h_frac_detector.SetLineWidth(2)
		h_frac_detector.SetLineStyle(1)
		h_frac_detector.SetFillStyle(0)
		h_frac_detector.SetMarkerSize(0)
		
		h_frac_total.SetLineColor(rt.kBlack)
		h_frac_total.SetLineWidth(3)
		h_frac_total.SetLineStyle(1)
		h_frac_total.SetFillStyle(0)
		h_frac_total.SetMarkerSize(0)
		
		# Get title parts
		title_parts = var_info['title'].split(';')
		x_axis_title = title_parts[1].strip() if len(title_parts) > 1 else ""
		
		# Draw line plots (not stacked)
		frac_title = f"{plot_title}; {x_axis_title}; Fractional Uncertainty"
		h_frac_total.SetTitle(frac_title)
		
		# Find max for y-axis range
		max_val = max(h_frac_stat.GetMaximum(), h_frac_flux.GetMaximum(), 
					  h_frac_xsec.GetMaximum(), h_frac_reint.GetMaximum(),
					  h_frac_detector.GetMaximum(), h_frac_total.GetMaximum())
		h_frac_total.SetMaximum(max_val * 1.2)
		h_frac_total.SetMinimum(0.0)  # Start at 0
		
		# Draw total first to set up axes
		h_frac_total.Draw("hist")
		h_frac_stat.Draw("hist same")
		h_frac_flux.Draw("hist same")
		h_frac_xsec.Draw("hist same")
		h_frac_reint.Draw("hist same")
		h_frac_detector.Draw("hist same")
		
		# Set axis properties
		h_frac_total.GetXaxis().SetLabelSize(0.04)
		h_frac_total.GetXaxis().SetTitleSize(0.04)
		h_frac_total.GetYaxis().SetLabelSize(0.04)
		h_frac_total.GetYaxis().SetTitleSize(0.04)
		h_frac_total.GetYaxis().SetTitle("Fractional Uncertainty")
		h_frac_total.GetYaxis().SetTitleOffset(1.2)
		
		# Add legend for fractional plot
		leg_frac = rt.TLegend(0.15, 0.60, 0.40, 0.88)
		leg_frac.SetTextSize(0.035)
		leg_frac.SetFillStyle(0)
		leg_frac.SetBorderSize(1)
		leg_frac.AddEntry(h_frac_total, "Total", "l")
		leg_frac.AddEntry(h_frac_stat, "Statistical", "l")
		leg_frac.AddEntry(h_frac_flux, "Flux", "l")
		leg_frac.AddEntry(h_frac_xsec, "Cross Section", "l")
		leg_frac.AddEntry(h_frac_reint, "Reinteraction", "l")
		leg_frac.AddEntry(h_frac_detector, "Detector", "l")
		leg_frac.Draw()
		
		canvas_frac.Update()
		canvas_frac.RedrawAxis()
		
		out.cd()
		canvas_frac.Write()

		# === Create individual fractional error canvases ===
		frac_components = [
			(h_frac_stat,     "stat",     "Statistical",    rt.kGray+2),
			(h_frac_flux,     "flux",     "Flux",           rt.kGreen+2),
			(h_frac_xsec,     "xsec",     "Cross Section",  rt.kRed),
			(h_frac_reint,    "reint",    "Reinteraction",  rt.kMagenta+1),
			(h_frac_detector, "detector", "Detector",       rt.kBlue),
		]

		title_parts = var_info['title'].split(';')
		x_axis_title = title_parts[1].strip() if len(title_parts) > 1 else ""

		for h_frac, tag, label, color in frac_components:
			if h_frac is None:
				continue

			c_indiv = rt.TCanvas(f"c_{var_name}_frac_{tag}",
								 f"{var_name} {label} Fractional Error", 1000, 600)
			c_indiv.Draw()
			c_indiv.SetTickx(1)
			c_indiv.SetTicky(1)

			h_draw = h_frac.Clone(f"h_frac_{tag}_{var_name}_indiv")
			h_draw.SetTitle(f"{plot_title}; {x_axis_title}; {label} Fractional Uncertainty")
			h_draw.SetLineColor(color)
			h_draw.SetLineWidth(3)
			h_draw.SetLineStyle(1)
			h_draw.SetFillStyle(0)
			h_draw.SetMarkerSize(0)
			h_draw.SetMinimum(0.0)
			h_draw.SetMaximum(h_draw.GetMaximum() * 1.3)

			h_draw.GetXaxis().SetLabelSize(0.04)
			h_draw.GetXaxis().SetTitleSize(0.04)
			h_draw.GetYaxis().SetLabelSize(0.04)
			h_draw.GetYaxis().SetTitleSize(0.04)
			h_draw.GetYaxis().SetTitleOffset(1.2)

			h_draw.Draw("hist")

			leg_indiv = rt.TLegend(0.65, 0.75, 0.88, 0.88)
			leg_indiv.SetTextSize(0.035)
			leg_indiv.SetFillStyle(0)
			leg_indiv.SetBorderSize(1)
			leg_indiv.AddEntry(h_draw, label, "l")
			leg_indiv.Draw()

			c_indiv.Update()
			c_indiv.RedrawAxis()
			out.cd()
			c_indiv.Write()

	# ===================================================================
	# === PURITY AND EFFICIENCY PLOTS ===
	# ===================================================================
	
	print(f"\n=== Creating purity and efficiency plots for {var_name} ===")
	
	# --- PURITY PLOT (as function of RECONSTRUCTED variable) ---
	# Purity = Signal / (Signal + Background) in each bin
	
	if 'cc_numu' in hists and h_total_mc is not None:
		h_purity = hists['cc_numu'].Clone(f"h_purity_{var_name}")
		
		for ibin in range(0, h_purity.GetNbinsX() + 2):
			signal = hists['cc_numu'].GetBinContent(ibin)
			total = h_total_mc.GetBinContent(ibin)
			
			if total > 0:
				purity = signal / total
				h_purity.SetBinContent(ibin, purity)
				
				# Calculate purity uncertainty (binomial error)
				# σ_purity = sqrt(p*(1-p)/N) where p=purity, N=total events
				n_total_unscaled = h_total_mc_unscaled.GetBinContent(ibin)
				if n_total_unscaled > 0:
					purity_error = sqrt(purity * (1 - purity) / n_total_unscaled)
					h_purity.SetBinError(ibin, purity_error)
				else:
					h_purity.SetBinError(ibin, 0.0)
			else:
				h_purity.SetBinContent(ibin, 0.0)
				h_purity.SetBinError(ibin, 0.0)
		
		# Create purity canvas
		canvas_purity = rt.TCanvas(f"c_{var_name}_purity", f"{var_name} Purity", 1000, 600)
		canvas_purity.Draw()
		canvas_purity.SetTickx(1)
		canvas_purity.SetTicky(1)
		
		# Get title parts
		title_parts = var_info['title'].split(';')
		x_axis_title = title_parts[1].strip() if len(title_parts) > 1 else ""
		
		# Style purity histogram
		h_purity.SetTitle(f"{plot_title}; {x_axis_title}; CC #nu_{{#mu}} Purity")
		h_purity.SetLineColor(rt.kBlue+1)
		h_purity.SetLineWidth(3)
		h_purity.SetMarkerStyle(20)
		h_purity.SetMarkerColor(rt.kBlue+1)
		h_purity.SetMarkerSize(1.0)
		h_purity.SetMinimum(0.0)
		h_purity.SetMaximum(1.1)
		
		# Draw
		h_purity.Draw("E1")
		
		# Add reference line at purity = 1.0
		line_purity = rt.TLine(var_info['xmin'], 1.0, var_info['xmax'], 1.0)
		line_purity.SetLineStyle(2)
		line_purity.SetLineColor(rt.kGray+2)
		line_purity.Draw("same")
		
		# Calculate average purity (weighted by events)
		total_signal = hists['cc_numu'].Integral()
		total_all = h_total_mc.Integral()
		avg_purity = total_signal / total_all if total_all > 0 else 0.0
		
		# Add text box with average purity
		text_purity = rt.TLatex()
		text_purity.SetNDC()
		text_purity.SetTextSize(0.04)
		text_purity.DrawLatex(0.15, 0.85, f"Average Purity: {avg_purity:.3f}")
		
		canvas_purity.Update()
		out.cd()
		canvas_purity.Write()
		
		print(f"  Average purity: {avg_purity:.3f}")
	
	# --- EFFICIENCY PLOT (as function of TRUE variable) ---
	# Efficiency = (True CC νμ passing cuts) / (All true CC νμ)
	
	if 'true_var' in var_info:
		# Create histogram for denominator: all true CC νμ events (no selection cuts)
		hname_denom = f'h_eff_denom_{var_name}'
		h_eff_denom = rt.TH1D(hname_denom, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
		h_eff_denom.Sumw2()
		
		# Truth-level cut for CC νμ (no reconstruction cuts)
		truth_cut = "(numuIncCC_is_cc_interaction==1) && (true_vertex_properties_dwall > 3.0)"
		
		# Fill denominator with true variable
		if run_num == 4:
			h_eff_denom_temp = rt.TH1D(f"{hname_denom}_temp", "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
			h_eff_denom_temp.Sumw2()
			for run_label in ['4b', '4c', '4d']:
				h_eff_denom_temp.Reset()
				trees[run_label]['numu'].Draw(f"{var_info['true_var']}>>{hname_denom}_temp", 
											   f"({truth_cut})*eventweight_weight", "goff")
				h_eff_denom_temp.Scale(scaling[run_label]['numu'])
				h_eff_denom.Add(h_eff_denom_temp)
		else:
			trees['numu'].Draw(f"{var_info['true_var']}>>{hname_denom}", 
							   f"({truth_cut})*eventweight_weight", "goff")
			h_eff_denom.Scale(scaling['numu'])
		
		# Create histogram for numerator: true CC νμ passing selection
		hname_numer = f'h_eff_numer_{var_name}'
		h_eff_numer = rt.TH1D(hname_numer, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
		h_eff_numer.Sumw2()
		
		# Full selection cut (reconstruction + truth)
		full_cut = f"({base_cut}) && ({truth_cut}){var_info['cut_suffix']}"
		
		# Fill numerator with true variable
		if run_num == 4:
			h_eff_numer_temp = rt.TH1D(f"{hname_numer}_temp", "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
			h_eff_numer_temp.Sumw2()
			for run_label in ['4b', '4c', '4d']:
				h_eff_numer_temp.Reset()
				trees[run_label]['numu'].Draw(f"{var_info['true_var']}>>{hname_numer}_temp", 
											   f"({full_cut})*eventweight_weight", "goff")
				h_eff_numer_temp.Scale(scaling[run_label]['numu'])
				h_eff_numer.Add(h_eff_numer_temp)
		else:
			trees['numu'].Draw(f"{var_info['true_var']}>>{hname_numer}", 
							   f"({full_cut})*eventweight_weight", "goff")
			h_eff_numer.Scale(scaling['numu'])
		
		# Calculate efficiency
		h_efficiency = h_eff_numer.Clone(f"h_efficiency_{var_name}")
		h_efficiency.Divide(h_eff_denom)
		
		# Create efficiency canvas
		canvas_eff = rt.TCanvas(f"c_{var_name}_efficiency", f"{var_name} Efficiency", 1000, 600)
		canvas_eff.Draw()
		canvas_eff.SetTickx(1)
		canvas_eff.SetTicky(1)
		
		# Get axis title (use "True" instead of "Reconstructed")
		x_axis_title_eff = x_axis_title.replace("Reconstructed", "True")
		
		# Style efficiency histogram
		h_efficiency.SetTitle(f"{plot_title}; {x_axis_title_eff}; CC #nu_{{#mu}} Efficiency")
		h_efficiency.SetLineColor(rt.kRed+1)
		h_efficiency.SetLineWidth(3)
		h_efficiency.SetMarkerStyle(21)
		h_efficiency.SetMarkerColor(rt.kRed+1)
		h_efficiency.SetMarkerSize(1.0)
		h_efficiency.SetMinimum(0.0)
		h_efficiency.SetMaximum(1.1)
		
		# Draw
		h_efficiency.Draw("E1")
		
		# Add reference line at efficiency = 1.0
		line_eff = rt.TLine(var_info['xmin'], 1.0, var_info['xmax'], 1.0)
		line_eff.SetLineStyle(2)
		line_eff.SetLineColor(rt.kGray+2)
		line_eff.Draw("same")
		
		# Calculate average efficiency
		total_selected = h_eff_numer.Integral()
		total_true = h_eff_denom.Integral()
		avg_efficiency = total_selected / total_true if total_true > 0 else 0.0
		
		# Add text box with average efficiency
		text_eff = rt.TLatex()
		text_eff.SetNDC()
		text_eff.SetTextSize(0.04)
		text_eff.DrawLatex(0.15, 0.85, f"Average Efficiency: {avg_efficiency:.3f}")
		
		canvas_eff.Update()
		out.cd()
		canvas_eff.Write()
		
		print(f"  Average efficiency: {avg_efficiency:.3f}")
		
		# --- COMBINED PURITY AND EFFICIENCY PLOT ---
		canvas_both = rt.TCanvas(f"c_{var_name}_purity_efficiency", 
								 f"{var_name} Purity and Efficiency", 1000, 600)
		canvas_both.Draw()
		canvas_both.SetTickx(1)
		canvas_both.SetTicky(1)
		
		# Draw efficiency first
		h_efficiency_copy = h_efficiency.Clone(f"h_efficiency_{var_name}_copy")
		h_efficiency_copy.SetTitle(f"{plot_title}; Energy (GeV); Purity / Efficiency")
		h_efficiency_copy.Draw("E1")
		
		# Draw purity on same plot
		h_purity_copy = h_purity.Clone(f"h_purity_{var_name}_copy")
		h_purity_copy.Draw("E1 same")
		
		# Reference line
		line_both = rt.TLine(var_info['xmin'], 1.0, var_info['xmax'], 1.0)
		line_both.SetLineStyle(2)
		line_both.SetLineColor(rt.kGray+2)
		line_both.Draw("same")
		
		# Legend
		leg_both = rt.TLegend(0.15, 0.15, 0.45, 0.35)
		leg_both.SetTextSize(0.035)
		leg_both.SetFillStyle(0)
		leg_both.SetBorderSize(1)
		leg_both.AddEntry(h_purity_copy, f"Purity (avg: {avg_purity:.3f})", "lep")
		leg_both.AddEntry(h_efficiency_copy, f"Efficiency (avg: {avg_efficiency:.3f})", "lep")
		leg_both.Draw()
		
		canvas_both.Update()
		out.cd()
		canvas_both.Write()

	# CC νμ purity
	cc_numu_events = total_events.get('cc_numu', 0)
	
	# Background breakdown
	cosmic_events = total_events.get('cosmic', 0)
	cc_nue_events = total_events.get('cc_nue', 0)
	nc_events = total_events.get('nc_nue', 0) + total_events.get('nc_numu', 0)

print("\nSaved to", out_name)
out.Close()