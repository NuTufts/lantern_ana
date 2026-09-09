import os,sys
import ROOT as rt
import array
import ctypes
from math import sqrt

################################################
# final state particles (inc, pi0, 0p, 1p, Np)
fsp_channel = "pi0"

# List of runs (1,3,4,5)
# runs = [1,3,4,5]
runs = [4]

use_truth = True 

use_surprise_numu = False 

use_fully_contained = False 

plot_nue = False

################################################

def run_plots(run_num, truth_mode=False, fully_contained=False, show_pc=True, debug=False,
              fsp_channel='inc'):

	dprint = print if debug else lambda *args, **kwargs: None
	# lantern_dir = "/cluster/tufts/wongjiradlabnu/zimani01/lantern/lantern_ana/"
	lantern_dir = "/exp/uboone/app/users/imani/lantern_ana/"

	show_cut_flow = True
	cut_flow_cuts = [
		("numuIncCC_cut1_vertex_fiducial",        "1"),
		("numuIncCC_cut2_cosmic_rejection",        "1,2"),
		("numuIncCC_cut3_has_muon",         	 "All"),
	]

	## Run 1 
	if run_num == 1: 
		targetpot = 4.4e19
		scaling = {
				"numu":targetpot/4.675690535431973e+20,
				"nue":targetpot/9.662529168587103e+22,
				"extbnb":(176153.0)/(433446.0),
				"data":1.0}
		files = {
				"numu": f"{lantern_dir}/all_runs_mmr/run1/root_files/selection_testing_v4/run1_nu_20260601_152723.root",
				"nue":f"{lantern_dir}/all_runs_mmr/run1/root_files/selection_testing_v4/run1_nue_20260601_153328.root", 
				"extbnb":f"{lantern_dir}/all_runs_mmr/run1/root_files/selection_testing_v4/run1_extbnb_20260601_154124.root",
				"data":f"{lantern_dir}/all_runs_mmr/run1/root_files/selection_testing_v4/run1_data_5e19_20260601_154504.root"}
		xsecflux_files = {
			"nue": f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_numu_bnb_nue.root",
			"numu": f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_numu_bnb_nu.root"
		}
		detsys_file = f"{lantern_dir}/all_runs_mmr/run3/root_files/detsys_final/combined_run3mil_nu_CV.root"
		show_data = True 
		data_legend = "Run1 5e19 Data"
		title_run      = "Run 1:"
		title_channel  = "CC Inclusive Numu"
		title_modifier = ""
		out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run1_hists.root"
		xsecflux_sample_map = {
			'numu': 'run1_nu',
			'nue': 'run1_nue'
		}
		if use_surprise_numu:
			scaling['numu'] = targetpot/5.928455889220508e+20
			xsecflux_files['numu'] = f"{lantern_dir}/all_runs_mmr/run1_surprise/root_files/xsecflux/xsecflux_numu_nu.root"
			xsecflux_sample_map['numu'] = 'run1surp_nu'
			# files['numu'] = f"{lantern_dir}/all_runs_mmr/run1_surprise/root_files/selection/run1surp_nu_20260507_213935.root"
			files['numu'] = f"{lantern_dir}/all_runs_mmr/run1/root_files/selection_testing_v4/run1surp_nu_weightSplineTimesTune_20260601_230604.root"
			title_modifier += " (Surprise Numu)"
			out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run1_hists_surpriseNU.root"

	## Run 3 (one million MC)
	if run_num == 3: 
		targetpot = 8.806e18
		scaling = {
				"numu":targetpot/1.346689484233034e+21,
				"nue":targetpot/2.891774385462469e+22,
				# "extbnb": (2263559.0)/(19214565.0),
				"extbnb": (2263559.0)/(150523663.0),
				"data":1.0}
		files = {
				"numu": f"{lantern_dir}/all_runs_mmr/run3/root_files/selection_v3/run3_nu_20260724_160048.root",
				"nue":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection_v3/run3_nue_20260724_162721.root", 
				"extbnb":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection_v3/run3_extbnb_20260724_163050.root",
				"data":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection_v3/run3_data_20260724_164310.root"}
		xsecflux_files = {
			"nue": f"{lantern_dir}/all_runs_mmr/run3/root_files/xsecflux/xsecflux_run3mil_numu_bnb_nue.root",
			"numu": f"{lantern_dir}/all_runs_mmr/run3/root_files/xsecflux/xsecflux_run3mil_numu_bnb_nu.root"
		}
		detsys_file = f"{lantern_dir}/all_runs_mmr/run3/root_files/detsys_final/combined_run3mil_nu_CV.root"
		detsys_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
		show_data = True 
		data_legend = "Run3 1e19 Data"
		title_run      = "Run 3:"
		title_channel  = "CC Inclusive Numu"
		title_modifier = ""
		out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run3_hists.root"
		xsecflux_variables = ['visible_energy', 'reco_muon_momentum', 'reco_cos_theta']
		xsecflux_sample_map = {
			'nue': 'run3mil_nue',
			'numu': 'run3mil_nu'  
		}
		if use_surprise_numu:
			scaling['numu'] = targetpot/8.628601378515997e+20
			xsecflux_sample_map['numu'] = 'run3surp_nu'
			xsecflux_files['numu'] = f"{lantern_dir}/all_runs_mmr/run3_surprise/root_files/xsecflux/xsecflux_numu_nu.root"
			files['numu'] = f"{lantern_dir}/all_runs_mmr/run3_surprise/root_files/selection_v2/run3surp_nu_20260727_122115.root"
			title_modifier += " (Surprise Numu)"
			out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run3_hists_surpriseNU.root"

	## Combined Run 4 (4b + 4c + 4d)
	if run_num == 4:
		# Calculate total target POT from all sub-runs
		run4bpot = 1.45e+20
		run4cpot = 9.106e+19
		run4dpot = 5.015e+19
		targetpot = run4bpot + run4cpot + run4dpot
		# targetpot = 1.45e+20
		# # targetpot = 3.936e+19
		# run4bpot = targetpot
		# run4cpot = targetpot
		# run4dpot = targetpot

		# ## Lantern POTs
		run4bpot_nu = 7.881656209241413e+20
		run4cpot_nu = 2.8777157789184374e+20
		run4dpot_nu = 4.029820515210945e+20

		## Wirecell 
		# run4cpot_nu = 4.6945731836947293798400e+20

		# targetpot = 

		run4bpot = 3.936e+19

		scaling_4b = {
			"numu": run4bpot/run4bpot_nu,
			"nue": run4bpot/1.1785765118473412e+23,
			# "extbnb": 34317881.0/96638186.0,
			"extbnb": 8985142.0/96638186.0,
			"data": 1.0
		}
	
		scaling_4c = {
			"numu": run4cpot/run4cpot_nu,
			"nue": run4cpot/7.160248800041886e+22,
			# "extbnb": 20644587.0/54566891.0,
			"extbnb": 8985142.0/54566891.0,
			"data": 1.0
		}
	
		scaling_4d = {
			"numu": run4dpot/run4dpot_nu, 
			"nue": run4dpot/1.3740045183260529e+23,
			# "extbnb": 11403578.0/78224187.0,
			"extbnb": 8985142.0/78224187.0,
			"data": 1.0
		}
	
		# Set to use a single sub-run or combine all three.
		run4_single_dataset = 42
		if run4_single_dataset == 42: 
			run4_labels = ['4b']
		elif run4_single_dataset == 43:
			run4_labels = ['4c']
		elif run4_single_dataset == 44:
			run4_labels = ['4d']
		else:
			run4_labels = ['4b', '4c', '4d']

		scaling = {
			'4b': scaling_4b,
			'4c': scaling_4c,
			'4d': scaling_4d
		}
	
		files_4b = {
			"extbnb": f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection_v8/run4b_extbnb_20260722_175349.root",
			"numu": f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection_v8/run4b_nu_20260722_164523.root",
			"nue": f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection_v8/run4b_nue_20260722_173017.root",
			"data": f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection_v8/run4b_open_data_20260722_181058.root"
		}
	
		files_4c = {
			"numu": f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nu_20260406_211847.root",
			"nue": f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_nue_20260406_213242.root",
			"extbnb": f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_extbnb_20260406_215448.root",
			"data": f"{lantern_dir}/all_runs_mmr/run4c/root_files/selection/run4c_data_20260406_221702.root"
		}
	
		files_4d = {
			"numu": f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nu_20260406_212137.root",
			"nue": f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_nue_20260406_214755.root",
			"extbnb": f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_extbnb_20260406_225937.root",
			"data": f"{lantern_dir}/all_runs_mmr/run4d/root_files/selection/run4d_data_20260406_233631.root"
		}
	
		files = {'4b': files_4b, '4c': files_4c, '4d': files_4d}

		xsecflux_files = {
			# "numu_4b": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_numu_combined_run4b.root",
			# "nue_4b":  f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_numu_combined_run4b.root",
			"numu_4b": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_numu_nu.root",
			"nue_4b":  f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_numu_nue.root",
			"numu_4c": f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_numu_nu.root",
			"nue_4c": f"{lantern_dir}/all_runs_mmr/run4c/root_files/xsecflux/xsecflux_numu_nue.root",
			"numu_4d": f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_numu_nu.root",
			"nue_4d": f"{lantern_dir}/all_runs_mmr/run4d/root_files/xsecflux/xsecflux_numu_nue.root"
		}
	
		xsecflux_sample_map = {
			'4b': {'nue': 'run4b_nue', 'numu': 'run4b_nu'},
			'4c': {'nue': 'run4c_nue', 'numu': 'run4c_nu'},
			'4d': {'nue': 'run4d_nue', 'numu': 'run4d_nu'}
		}
	
		detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nu_cv.root"
	
		show_data = True
		data_legend = f"Run4b Open Data"
		title_run      = "Run 4:"
		title_channel  = "CC Inclusive Numu"
		title_modifier = ""
		out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run4_combined_hists.root"
		
	## Run 4a
	if run_num == 41: 
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
		title_run      = "Run 4a:"
		title_channel  = "CC Inclusive Numu"
		title_modifier = ""
		out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run4a_hists.root"
		xsecflux_sample_map = {
			'nue': 'run4a_nue',
			'numu': 'run4a_nu'  
		}

	## Run 5 
	if run_num == 5: 
		targetpot = 3.936e+19
		scaling = {"numu":targetpot/9.976307163316628e+20,
				"nue":targetpot/1.5178517202061622e+23,
				"extbnb":8985142.0/120139886.0,			
				"data":1.0}
		files = {"numu": f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_nu_20260406_212614.root",
				"nue":f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_nue_20260406_231158.root", 
				"extbnb":f"{lantern_dir}/all_runs_mmr/run5/root_files/selection/run5_extbnb_20260406_232657.root",
				"data":f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_open_data_20260406_221504.root"}
		xsecflux_files = {
			"numu": f"{lantern_dir}/all_runs_mmr/run5/root_files/xsecflux/xsecflux_numu_nu.root",
			"nue": f"{lantern_dir}/all_runs_mmr/run5/root_files/xsecflux/xsecflux_numu_nue.root"
			}
		# detsys_file = f"{lantern_dir}/all_runs_mmr/run5/root_files/detsys/detsys_cv_run5_nu_cv.root"
		detsys_file = f"{lantern_dir}/all_runs_mmr/run5/root_files/detsys_v2/detsys_cv_run5_nu_cv.root"
		show_data = True 
		data_legend = "Run4b Open Data"
		title_run      = "Run 5:"
		title_channel  = "CC Inclusive Numu"
		title_modifier = ""
		out_name = f"{lantern_dir}/all_runs_mmr/plots/numu/numu_run5_hists.root"
		xsecflux_sample_map = {
			'nue': 'run5_nue',
			'numu': 'run5_nu'  
		}

	## Same for all runs 
	xsecflux_variables = ['visible_energy']#, 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	detsys_variables = ['visible_energy']#, 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	detsys_params = [
		"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ", 
		"LYAtt", "LYDown", "LYRayleigh",
		"recomb2", "SCE",
	]


	# ---------------------------------------------------------------------------
	# Systematic parameter lists 
	# ---------------------------------------------------------------------------

	if run_num in [1, 3] and not use_surprise_numu:
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
			"piminus_PrimaryHadronSWCentralSplineVariation",
			"piplus_PrimaryHadronSWCentralSplineVariation"
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
		]
		reint_params = [
			"reinteractions_piminus_Geant4",
			"reinteractions_piplus_Geant4",
			"reinteractions_proton_Geant4"
		]

	if run_num in [4, 41, 42, 43, 44, 5] or use_surprise_numu: 
		flux_params = [
			"flux_all"
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
			"ThetaDelta2NRad_UBGenie", # <0.01
			"Theta_Delta2Npi_UBGenie" # <0.01
		]
		reint_params = [
			"reint_all"
		]
		# detector_params from xsecflux file (distinct from detsys_params which come from detsys file)
		xsecflux_detector_params = [
			"detvar_all"
		]

	# Build a lookup: parname -> category, derived purely from the lists above
	param_category = {}
	for p in flux_params:  param_category[p] = 'flux'
	for p in xsec_params:  param_category[p] = 'xsec'
	for p in reint_params: param_category[p] = 'reint'
	if run_num in [4, 41, 42, 43, 44, 5]:
		for p in xsecflux_detector_params: param_category[p] = 'detector'


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
			h_temp = rfile.Get(cv_name)
			if h_temp and not h_temp.IsZombie():
				h_reference = h_temp
				break

		if h_reference is None:
			print(f"  Warning: Could not find reference histogram for {varname}")
			return None

		# Combined fractional variance histogram
		h_frac_var = h_reference.Clone(f"h{varname}__detector_frac_variance")
		h_frac_var.Reset()

		n_loaded = 0
		for param in detsys_params:
			cv_name = f"h{varname}__{param}__cv"
			var_name = f"h{varname}__{param}__var"

			h_cv  = rfile.Get(cv_name)
			h_var = rfile.Get(var_name)

			if not h_cv or h_cv.IsZombie():
				dprint(f"    Skipping {param} - CV histogram not found")
				continue
			if not h_var or h_var.IsZombie():
				dprint(f"    Skipping {param} - variation histogram not found")
				continue

			n_loaded += 1
			dprint(f"    Loaded {param}")

			for ibin in range(0, h_frac_var.GetNbinsX() + 2):
				cv_val  = h_cv.GetBinContent(ibin)
				var_val = h_var.GetBinContent(ibin)
				if cv_val > 0:
					frac_diff   = (var_val - cv_val) / cv_val
					current_var = h_frac_var.GetBinContent(ibin)
					h_frac_var.SetBinContent(ibin, current_var + frac_diff**2)

		dprint(f"  Loaded {n_loaded}/{len(detsys_params)} detector variations for {varname}")
		detector_hists['frac_variance'] = h_frac_var
		detector_hists['n_params']      = n_loaded
		return detector_hists


	def make_hist_w_errors(rfile, varname, sample,
						   flux_params, xsec_params, reint_params,
						   detector_params=None):
		"""
		Load xsecflux variance histograms and separate them into per-parameter
		and per-category (flux / xsec / reint / detector) variance histograms.

		Parameters use the explicit category lists — no string-matching heuristics.

		Returns a dict with keys:
		  'cv'          - central-value histogram with total sys error set
		  'mean2'       - mean-of-means histogram
		  'totvar'      - total variance histogram
		  'fluxvar'     - aggregated flux variance
		  'xsecvar'     - aggregated xsec variance
		  'reintvar'    - aggregated reint variance
		  'detectorvar' - aggregated detector variance
		  'param_vars'  - dict of {parname: per-parameter variance histogram}
		"""
		if detector_params is None:
			detector_params = []

		all_params = flux_params + xsec_params + reint_params + detector_params

		# Build category lookup from the explicit lists
		cat_lookup = {}
		for p in flux_params:     cat_lookup[p] = 'flux'
		for p in xsec_params:     cat_lookup[p] = 'xsec'
		for p in reint_params:    cat_lookup[p] = 'reint'
		for p in detector_params: cat_lookup[p] = 'detector'

		hists = {}

		# Locate the CV histogram
		possible_cv_names = [
			f"h{varname}_{sample}_cv",
			f"{varname}_{sample}_cv",
			f"h_{varname}_{sample}_cv"
		]
		hcv = None
		for cv_name in possible_cv_names:
			hcv = rfile.Get(cv_name)
			if hcv and not hcv.IsZombie():
				dprint(f"  Found CV histogram: {cv_name}")
				break

		if not hcv or hcv.IsZombie():
			print(f"  Warning: Could not find CV histogram for {varname}_{sample}")
			return None

		# Aggregate variance histograms
		hvar_flux     = hcv.Clone(f"h{varname}__{sample}_flux_variance");     hvar_flux.Reset()
		hvar_xsec     = hcv.Clone(f"h{varname}__{sample}_xsec_variance");     hvar_xsec.Reset()
		hvar_reint    = hcv.Clone(f"h{varname}__{sample}_reint_variance");    hvar_reint.Reset()
		hvar_detector = hcv.Clone(f"h{varname}__{sample}_detector_variance"); hvar_detector.Reset()
		hvar_tot      = hcv.Clone(f"h{varname}__{sample}_totvariance");       hvar_tot.Reset()
		hmeans2       = hcv.Clone(f"h{varname}__{sample}_meanofmeans");       hmeans2.Reset()

		# Per-parameter variance histograms
		param_vars = {}

		n_pars = len(all_params)

		for parname in all_params:
			# Try standard naming patterns for variance and mean histograms
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

			hvar = None
			for vn in possible_var_names:
				hvar = rfile.Get(vn)
				if hvar and not hvar.IsZombie():
					break

			hmean = None
			for mn in possible_mean_names:
				hmean = rfile.Get(mn)
				if hmean and not hmean.IsZombie():
					break

			if not hvar or hvar.IsZombie():
				dprint(f"    Skipping {parname} - variance histogram not found")
				continue
			if not hmean or hmean.IsZombie():
				dprint(f"    Skipping {parname} - mean histogram not found")
				continue

			# Per-parameter scaled variance histogram
			h_par_var = hcv.Clone(f"h{varname}__{sample}__{parname}_cv_variance")
			h_par_var.Reset()

			syst_type = cat_lookup.get(parname, 'xsec')

			for ibin in range(0, hvar_tot.GetXaxis().GetNbins() + 1):
				xvar  = hvar.GetBinContent(ibin)
				xmean = hmean.GetBinContent(ibin)

				if xmean > 0:
					scale_factor = hcv.GetBinContent(ibin) / xmean
					cv_var = xvar * scale_factor * scale_factor
				else:
					cv_var = 0.0

				# Accumulate into total variance
				hvar_tot.SetBinContent(ibin, hvar_tot.GetBinContent(ibin) + cv_var)

				# Accumulate into per-parameter histogram
				h_par_var.SetBinContent(ibin, h_par_var.GetBinContent(ibin) + cv_var)

				# Accumulate into category-specific variance
				if syst_type == 'flux':
					hvar_flux.SetBinContent(ibin, hvar_flux.GetBinContent(ibin) + cv_var)
				elif syst_type == 'xsec':
					hvar_xsec.SetBinContent(ibin, hvar_xsec.GetBinContent(ibin) + cv_var)
				elif syst_type == 'reint':
					hvar_reint.SetBinContent(ibin, hvar_reint.GetBinContent(ibin) + cv_var)
				elif syst_type == 'detector':
					hvar_detector.SetBinContent(ibin, hvar_detector.GetBinContent(ibin) + cv_var)

				# Accumulate mean-of-means
				hmeans2.SetBinContent(ibin, hmeans2.GetBinContent(ibin) + xmean / n_pars)

			param_vars[parname] = h_par_var

		# Set total systematic error on CV histogram
		for ibin in range(0, hvar_tot.GetXaxis().GetNbins() + 1):
			hcv.SetBinError(ibin, sqrt(hvar_tot.GetBinContent(ibin)))

		# Debug summary
		n_flux     = sum(1 for p in all_params if cat_lookup.get(p) == 'flux')
		n_xsec     = sum(1 for p in all_params if cat_lookup.get(p) == 'xsec')
		n_reint    = sum(1 for p in all_params if cat_lookup.get(p) == 'reint')
		n_detector = sum(1 for p in all_params if cat_lookup.get(p) == 'detector')
		dprint(f"  Systematic breakdown: {n_flux} flux, {n_xsec} xsec, "
			  f"{n_reint} reint, {n_detector} detector (total {len(all_params)})")

		hists['cv']          = hcv
		hists['mean2']       = hmeans2
		hists['totvar']      = hvar_tot
		hists['fluxvar']     = hvar_flux
		hists['xsecvar']     = hvar_xsec
		hists['reintvar']    = hvar_reint
		hists['detectorvar'] = hvar_detector
		hists['param_vars']  = param_vars
		return hists

	rt.gStyle.SetOptStat(0)

	tfiles = {}
	trees  = {}

	# Handle combined run 4 differently
	if run_num == 4:
		samples = ['nue', 'numu', 'extbnb', 'data']
		for run_label in run4_labels:
			tfiles[run_label] = {}
			trees[run_label]  = {}
			for sample in samples:
				tfiles[run_label][sample] = rt.TFile(files[run_label][sample])
				trees[run_label][sample]  = tfiles[run_label][sample].Get("analysis_tree")
				nentries = trees[run_label][sample].GetEntries()
				dprint(f"Run {run_label} sample={sample} has {nentries} entries")
	else:
		samples = ['nue', 'numu', 'extbnb', 'data']
		for sample in samples:
			tfiles[sample] = rt.TFile(files[sample])
			trees[sample]  = tfiles[sample].Get("analysis_tree")
			nentries = trees[sample].GetEntries()
			dprint(f"sample={sample} has {nentries} entries")

	# ---------------------------------------------------------------------------
	# FSP channel cut
	# ---------------------------------------------------------------------------
	_valid_channels = ('inc', 'pi0', '0p', '1p', 'Np')
	if fsp_channel not in _valid_channels:
		raise ValueError(f"fsp_channel must be one of {_valid_channels}, got '{fsp_channel}'")

	if fsp_channel == 'pi0':
		# Select events where the pi0Properties producer found >= 2 PID==22 showers.
		# reco_inv_mass > 0 is the sentinel for this: it is filled whenever two
		# valid photon directions exist, with no box cuts applied.
		fsp_reco_cut  = "(pi0Properties_reco_inv_mass > 0)"
		# Require >= 2 true photons that are not from eBrem/annihilation,
		# have E > 20 MeV, and deposit energy inside the WireCell fiducial.
		fsp_truth_cut = "(pi0Properties_true_n_photons_fid_ecut >= 2)"
		fsp_label     = "Pi0"
	elif fsp_channel == '0p':
		fsp_reco_cut  = ("(Sum$(finalStateParticles_reco_shower_pid==2212)==0"
		                 " && Sum$(finalStateParticles_reco_track_pid==2212)==0)")
		fsp_truth_cut = "(Sum$(finalStateParticles_true_fsp_pdg==2212)==0)"
		fsp_label     = "0p"
	elif fsp_channel == '1p':
		fsp_reco_cut  = ("(Sum$(finalStateParticles_reco_shower_pid==2212)"
		                 " + Sum$(finalStateParticles_reco_track_pid==2212)==1)")
		fsp_truth_cut = "(Sum$(finalStateParticles_true_fsp_pdg==2212)==1)"
		fsp_label     = "1p"
	elif fsp_channel == 'Np':
		fsp_reco_cut  = ("(Sum$(finalStateParticles_reco_shower_pid==2212)>0"
		                 " || Sum$(finalStateParticles_reco_track_pid==2212)>0)")
		fsp_truth_cut = "(Sum$(finalStateParticles_true_fsp_pdg==2212)>0)"
		fsp_label     = "Np"
	else:
		fsp_reco_cut  = ""
		fsp_truth_cut = ""
		fsp_label     = ""

	if fsp_label:
		title_channel = f"{fsp_channel} channel"
		out_name = out_name.replace('.root', f'_{fsp_channel}.root')

	## Create output directory if it doesn't exist
	out_dir = os.path.dirname(out_name)
	if out_dir and not os.path.exists(out_dir):
		os.makedirs(out_dir)
		dprint(f"Created output directory: {out_dir}")

	dprint(f"\nOutput file: {out_name}")

	out = rt.TFile(out_name, "recreate")

	# Use the combined cut from the producer
	if truth_mode:
		if fsp_channel == 'pi0':
			# Match pi0_invmass_plot: dwall only, no flavor/CC requirement.
			# The inv-mass cut (> 0) is applied via cut_suffix on the variable.
			base_cut = "(true_vertex_properties_dwall > 3.0)"
			if fsp_truth_cut:
					base_cut += f" && {fsp_truth_cut}"
		else:
			# Select true CC νμ in fiducial volume; no reco requirement
			base_cut = ("(numuIncCC_true_nu_pdg==14 && nueIncCC_true_ccnc==0"
						" && true_vertex_properties_dwall > 3.0)")
			if fsp_truth_cut:
				base_cut += f" && {fsp_truth_cut}"
	else:
		base_cut = "(numuIncCC_passes_all_cuts==1)"
		if fsp_reco_cut:
			base_cut += f" && {fsp_reco_cut}"
	if fully_contained:
		title_modifier += " FC Only"
		fc_branch = "numuIncCC_true_is_fully_contained" if truth_mode else "numuIncCC_is_fully_contained"
		base_cut += f" && ({fc_branch}==1)"
	plot_title = f"{title_run} {title_channel}{title_modifier}"

	# Define sample categories with ROOT standard colors
	categories = {
		'cosmic': {
			'samples': ['extbnb'],
			'truth_cut': f' ',
			'color': rt.kGray+2,
			'fill_style': 1001,
			'legend': 'BNB EXT'
		},
		'nc_nue': {
			'samples': ['nue'],
			'truth_cut': f' && (numuIncCC_is_cc_interaction==0)',
			'color': rt.kViolet-1,
			'fill_style': 1001,
			'legend': 'NC nue'
		},
		'cc_nue': {
			'samples': ['nue'], 
			'truth_cut': f' && (numuIncCC_is_cc_interaction==1)',
			'color': rt.kRed-4,
			'fill_style': 1001,
			'legend': 'CC nue'
		},
		'nc_numu': {
			'samples': ['numu'],
			'truth_cut': f' && (numuIncCC_is_cc_interaction==0)', 
			'color': rt.kGreen+1,
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

	# ---------------------------------------------------------------------------
	# Pi0-channel category override
	# For fsp_channel=='pi0', replace the generic CC/NC numu categories with
	# four physics-motivated categories that distinguish whether the true
	# final state contains a pi0 (PDG 111) or not:
	#   CC π0  — CC interaction, true pi0 present  (main signal topology)
	#   NC π0  — NC interaction, true pi0 present  (second topology)
	#   CC no-π0 — CC without true pi0 (charge-exchange, mis-ID background)
	#   NC no-π0 — NC without true pi0
	# The nue sample is kept as a single combined background.
	# ---------------------------------------------------------------------------
	if fsp_channel == 'pi0':
		_pi0_cut    = '(pi0Properties_true_n_photons_fid_ecut >= 2)'
		_no_pi0_cut = '(pi0Properties_true_n_photons_fid_ecut < 2)'
		_is_cc      = '(numuIncCC_is_cc_interaction==1)'
		_is_nc      = '(numuIncCC_is_cc_interaction==0)'

		categories = {
			'cosmic': {
				'samples':    ['extbnb'],
				'truth_cut':  ' ',
				'color':      rt.kGray+2,
				'fill_style': 1001,
				'legend':     'BNB EXT',
			},
			'cc_pi0': {
				'samples':    ['numu'],
				'truth_cut':  f' && {_is_cc} && {_pi0_cut}',
				'color':      rt.kAzure+1,
				'fill_style': 1001,
				'legend':     'CC #pi^{0}',
			},
			'nc_pi0': {
				'samples':    ['numu'],
				'truth_cut':  f' && {_is_nc} && {_pi0_cut}',
				'color':      rt.kGreen+1,
				'fill_style': 1001,
				'legend':     'NC #pi^{0}',
			},
			'cc_no_pi0': {
				'samples':    ['numu'],
				'truth_cut':  f' && {_is_cc} && {_no_pi0_cut}',
				'color':      rt.kOrange+1,
				'fill_style': 1001,
				'legend':     'CC no-#pi^{0}',
			},
			'nc_no_pi0': {
				'samples':    ['numu'],
				'truth_cut':  f' && {_is_nc} && {_no_pi0_cut}',
				'color':      rt.kYellow+1,
				'fill_style': 1001,
				'legend':     'NC no-#pi^{0}',
			},
			'nue_bkg': {
				'samples':    ['nue'],
				'truth_cut':  ' ',
				'color':      rt.kRed-4,
				'fill_style': 1001,
				'legend':     '#nu_{e} bkg',
			},
		}
		if show_data:
			categories['data'] = {
				'samples':   ['data'],
				'truth_cut': '',
				'color':     rt.kBlack,
				'legend':    data_legend,
			}

	legend_POT_string = " Events Per " + str(targetpot) + " POT"

	# ---------------------------------------------------------------------------
	# Variables to plot
	# 'xsecflux_var' is the histogram name used inside the xsecflux ROOT files.
	# ---------------------------------------------------------------------------
	variables = {
		'neutrino_energy': {
			'var':          'numuIncCC_reco_nu_energy',
			'true_var':     'numuIncCC_true_nu_energy',
			'xsecflux_var': 'visible_energy',
			'nbins': 20,
			'xmin':  0.0,
			'xmax':  2.0,
			'title': plot_title + '; Reconstructed Neutrino Energy (GeV); ' + legend_POT_string,
			'cut_suffix': '',
			'has_overflow': True,
			'show_ratio': True
		# },
		# 'muon_momentum': {
		# 	'var':          'numuIncCC_reco_muon_momentum',
		# 	'true_var':     'numuIncCC_true_muon_momentum',
		# 	'xsecflux_var': 'reco_muon_momentum',
		# 	'nbins': 25,
		# 	'xmin':  0.0,
		# 	'xmax':  1.5,
		# 	'title': plot_title + '; Reconstructed Muon Momentum (GeV); ' + legend_POT_string,
		# 	'cut_suffix': '&& (numuIncCC_reco_muon_momentum>0)'
		# },
		# 'muon_costheta': {
		# 	'var':          'numuIncCC_reco_muon_costheta',
		# 	'true_var':     'numuIncCC_true_muon_costheta',
		# 	'xsecflux_var': 'reco_cos_theta',
		# 	'nbins': 20,
		# 	'xmin': -1.0,
		# 	'xmax':  1.0,
		# 	'title': plot_title + '; Reconstructed Muon cos(#theta); ' + legend_POT_string,
		# 	'cut_suffix': '&& (numuIncCC_reco_muon_costheta>-900)'
		}
	}


	if truth_mode:
		# Replace reco neutrino energy with the true version
		variables.pop('neutrino_energy', None)
		variables['neutrino_energy'] = {
			'var':          'numuIncCC_true_nu_energy',
			'true_var':     'numuIncCC_true_nu_energy',
			'xsecflux_var': 'visible_energy',
			'nbins':        20,
			'xmin':         0.0,
			'xmax':         2.0,
			'title':        plot_title + '; True Neutrino Energy (GeV); ' + legend_POT_string,
			'cut_suffix':   '',
			'has_overflow': True,
			'show_ratio':   False,   # no data to ratio against in truth mode
		}

	if fsp_channel == 'pi0':
		# Di-photon invariant mass from the two leading PID==22 showers.
		# M² = (E1+E2)² − |p1+p2|²  (no box cuts applied in the producer).
		# Reco variable in MeV; true variable from pi0 decay-photon four-vectors (MC only).
		pi0_mass_reco_var = 'pi0Properties_reco_inv_mass'
		pi0_mass_true_var = 'pi0Properties_true_inv_mass'
		pi0_mass_cut      = f'&& ({pi0_mass_reco_var}>0)'

		variables['pi0_inv_mass'] = {
			'var':          pi0_mass_reco_var if not truth_mode else pi0_mass_true_var,
			'true_var':     pi0_mass_true_var,
			'xsecflux_var': None,
			'nbins': 17,
			'xmin':  0.0,
			'xmax':  340.0,
			'title': plot_title + '; Reconstructed #pi^{0} Invariant Mass (MeV); ' + legend_POT_string,
			'cut_suffix': '' if truth_mode else pi0_mass_cut,
			'has_overflow': True,
			'show_ratio': True and show_data and not truth_mode,
		}

		if truth_mode:
			variables['pi0_inv_mass']['title'] = plot_title + '; True #pi^{0} Invariant Mass (MeV); ' + legend_POT_string
			variables['pi0_inv_mass']['cut_suffix'] = f'&& ({pi0_mass_true_var}>0)'
			variables['pi0_inv_mass']['show_ratio'] = False

	# ---------------------------------------------------------------------------
	# Load xsecflux uncertainties
	# ---------------------------------------------------------------------------
	xsecflux_hists = {}

	# Determine xsecflux detector params (only for run4/5 where detvar_all is in the file)
	_xsec_detector = xsecflux_detector_params if run_num in [4, 41, 42, 43, 44, 5] else []

	if run_num == 4:
		for xsample_name in ['numu', 'nue']:
			xsecflux_hists[xsample_name] = {}

			for var in xsecflux_variables:
				dprint(f"\nCombining xsecflux uncertainties for {xsample_name}, variable {var}")

				combined_cv          = None
				combined_flux_var    = None
				combined_xsec_var    = None
				combined_reint_var   = None
				combined_param_vars  = {}   # parname -> combined variance hist

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

					# Detach histograms from file before closing
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

					dprint(f"  Added {run_label} to combined uncertainties")
					xfile.Close()

				if combined_cv is not None:
					xsecflux_hists[xsample_name][var] = {
						'cv':         combined_cv,
						'fluxvar':    combined_flux_var,
						'xsecvar':    combined_xsec_var,
						'reintvar':   combined_reint_var,
						'param_vars': combined_param_vars
					}
					dprint(f"  Successfully combined uncertainties for {xsample_name}, variable {var}")
				else:
					print(f"  Warning: No valid xsecflux files found for {xsample_name}, variable {var}")

	else:
		for xsample_name in ['numu', 'nue']:
			xsecflux_hists[xsample_name] = {}

			for var in xsecflux_variables:
				dprint(f"\nLoading xsecflux uncertainties for {xsample_name}, variable {var}")

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

				# Detach histograms from file before closing
				hists_with_errors['cv'].SetDirectory(0)
				hists_with_errors['fluxvar'].SetDirectory(0)
				hists_with_errors['xsecvar'].SetDirectory(0)
				hists_with_errors['reintvar'].SetDirectory(0)
				for pname, h in hists_with_errors['param_vars'].items():
					h.SetDirectory(0)

				xsecflux_hists[xsample_name][var] = hists_with_errors
				dprint(f"  Successfully loaded uncertainties for {xsample_name}, variable {var}")
				xfile.Close()

	# Load detector variations
	detsys_hists = {}
	if detsys_file is not None:
		dprint(f"\nLoading detector variations from {detsys_file}")
		if os.path.exists(detsys_file):
			dfile = rt.TFile(detsys_file)
			if not dfile.IsZombie():
				for var in detsys_variables:
					det_hists = load_detector_variations(dfile, var, detsys_params)
					if det_hists:
						detsys_hists[var] = det_hists
						dprint(f"  Loaded detector variations for {var}")
			else:
				print(f"  Warning: Could not open detector file")
		else:
			print(f"  Warning: Detector file not found")


	# ---------------------------------------------------------------------------
	# Create histograms for each variable
	# ---------------------------------------------------------------------------
	for var_name, var_info in variables.items():
		dprint(f"\n=== Creating {var_name} histogram ===")

		show_ratio = var_info.get('show_ratio', False) and show_data
		chi_rebin  = True   # rebin x2 before chi2 test to avoid low-stats bin warnings; set False to disable
		show_chi2  = False   # set False to hide chi²/ndf label on plot

		# Canvas with optional ratio panel
		if show_ratio:
			canvas = rt.TCanvas(f"c_{var_name}_{run_num}", f"{var_name} Distribution", 1000, 1000)

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

			pad1.cd()
		else:
			canvas = rt.TCanvas(f"c_{var_name}_{run_num}", f"{var_name} Distribution", 1000, 800)
			canvas.Draw()

		hists          = {}
		hists_unscaled = {}
		total_events   = {}

		# Fill histograms for each category
		for cat_name, cat_info in categories.items():
			total_events[cat_name] = 0

			for sample in cat_info['samples']:
				full_cut    = f"({base_cut}){cat_info['truth_cut']}{var_info['cut_suffix']}"
				hname       = f'h_{var_name}_{cat_name}_{sample}'
				hname_unscaled = f'h_{var_name}_{cat_name}_{sample}_unscaled'

				hist          = rt.TH1D(hname,          "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
				hist_unscaled = rt.TH1D(hname_unscaled, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
				hist.Sumw2()
				hist_unscaled.Sumw2()

				if run_num == 4:
					hist_temp          = rt.TH1D(f"{hname}_temp",          "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
					hist_unscaled_temp = rt.TH1D(f"{hname_unscaled}_temp", "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
					hist_temp.Sumw2()
					hist_unscaled_temp.Sumw2()

					for run_label in run4_labels:
						# Data comes from run4b only: files_4c and files_4d both point to the
						# same run4b_open_data file, so iterating all labels would triple-count it.
						# EXT is combined across 4b/4c/4d for better statistics.
						### HERE
						if sample == 'data' and run_label != '4b' and '4b' in run4_labels:
							continue

						hist_temp.Reset()
						hist_unscaled_temp.Reset()

						trees[run_label][sample].Draw(f"{var_info['var']}>>{hname}_temp",
													  f"({full_cut})*eventweight_weight", "goff")
						trees[run_label][sample].Draw(f"{var_info['var']}>>{hname_unscaled}_temp",
													  f"({full_cut})*eventweight_weight", "goff")

						hist_temp.Scale(scaling[run_label][sample])
						hist.Add(hist_temp)
						hist_unscaled.Add(hist_unscaled_temp)
				else:
					trees[sample].Draw(f"{var_info['var']}>>{hname}",
									   f"({full_cut})*eventweight_weight", "goff")
					trees[sample].Draw(f"{var_info['var']}>>{hname_unscaled}",
									   f"({full_cut})*eventweight_weight", "goff")
					hist.Scale(scaling[sample])

				if cat_name not in hists:
					hists[cat_name] = hist.Clone(f"h_{var_name}_{cat_name}")
					hists[cat_name].Reset()
				if cat_name not in hists_unscaled:
					hists_unscaled[cat_name] = hist_unscaled.Clone(f"h_{var_name}_{cat_name}_unscaled")
					hists_unscaled[cat_name].Reset()

				hists[cat_name].Add(hist)
				hists_unscaled[cat_name].Add(hist_unscaled)
				total_events[cat_name] += hist.Integral()

				dprint(f"{cat_name}-{sample}: {hist.Integral():.2f} events")

				if "(" not in categories[cat_name]['legend']:
					categories[cat_name]['legend'] += f" ({hist.Integral():.1f})"

		# Histogram styles
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

		# Build MC stack
		if fsp_channel == 'pi0':
			stack_order = ['cosmic', 'nue_bkg', 'nc_no_pi0', 'cc_no_pi0', 'nc_pi0', 'cc_pi0']
		else:
			stack_order = ['cosmic', 'nc_nue', 'cc_nue', 'nc_numu', 'cc_numu']
		hstack = rt.THStack(f"hs_{var_name}", "")

		h_total_mc          = None
		h_total_mc_unscaled = None
		for cat_name in stack_order:
			if cat_name in hists and cat_name != 'data':
				hstack.Add(hists[cat_name])
				if h_total_mc is None:
					h_total_mc          = hists[cat_name].Clone(f"h_total_mc_{var_name}")
					h_total_mc_unscaled = hists_unscaled[cat_name].Clone(f"h_total_mc_unscaled_{var_name}")
				else:
					h_total_mc.Add(hists[cat_name])
					h_total_mc_unscaled.Add(hists_unscaled[cat_name])

		# -----------------------------------------------------------------------
		# Build uncertainty histograms (total, per-category, per-parameter)
		# -----------------------------------------------------------------------
		h_uncertainty_total    = None
		h_uncertainty_flux     = None
		h_uncertainty_xsec     = None
		h_uncertainty_reint    = None
		h_uncertainty_detector = None
		# Per-parameter uncertainty histograms: {parname: TH1D with bin errors set}
		h_uncertainty_params   = {}

		xsecflux_var = var_info['xsecflux_var']   # Direct lookup — no var_name_map needed

		if h_total_mc is not None:
			h_uncertainty_total    = h_total_mc.Clone(f"h_uncertainty_total_{var_name}")
			h_uncertainty_flux     = h_total_mc.Clone(f"h_uncertainty_flux_{var_name}")
			h_uncertainty_xsec     = h_total_mc.Clone(f"h_uncertainty_xsec_{var_name}")
			h_uncertainty_reint    = h_total_mc.Clone(f"h_uncertainty_reint_{var_name}")
			h_uncertainty_detector = h_total_mc.Clone(f"h_uncertainty_detector_{var_name}")

			# Initialise per-parameter uncertainty histograms from the loaded hists
			for xsample_name in ['nue', 'numu']:
				if (xsample_name in xsecflux_hists
						and xsecflux_var in xsecflux_hists[xsample_name]
						and 'param_vars' in xsecflux_hists[xsample_name][xsecflux_var]):
					for pname in xsecflux_hists[xsample_name][xsecflux_var]['param_vars']:
						if pname not in h_uncertainty_params:
							h_uncertainty_params[pname] = h_total_mc.Clone(
								f"h_uncertainty_{pname}_{var_name}")

			for ibin in range(0, h_uncertainty_total.GetNbinsX() + 2):
				central = h_total_mc.GetBinContent(ibin)

				if central <= 0:
					for h in [h_uncertainty_total, h_uncertainty_flux,
							  h_uncertainty_xsec, h_uncertainty_reint, h_uncertainty_detector]:
						h.SetBinError(ibin, 0.0)
					for h in h_uncertainty_params.values():
						h.SetBinError(ibin, 0.0)
					continue

				abs_var_flux       = 0.0
				abs_var_xsec       = 0.0
				abs_var_reint      = 0.0
				abs_var_params     = {pname: 0.0 for pname in h_uncertainty_params}
				frac_var_detector  = 0.0
				frac_var_params    = {pname: 0.0 for pname in h_uncertainty_params}

				# Accumulate fractional variances from each neutrino sample
				for xsample_name in ['nue', 'numu']:
					try:
						if (xsample_name not in xsecflux_hists
								or xsecflux_var not in xsecflux_hists[xsample_name]):
							continue
						xsec_hists = xsecflux_hists[xsample_name][xsecflux_var]
						cv_xf = xsec_hists['cv'].GetBinContent(ibin) if 'cv' in xsec_hists else 0.0
					
						if cv_xf <= 0:
							continue

						# Scaled contribution of this xsample to total MC (targetpot units).
						# Sum all categories whose samples list includes this xsample_name,
						# excluding the data category.
						cv_scaled = sum(
							hists[cat].GetBinContent(ibin)
							for cat, info in categories.items()
							if cat != 'data'
							and xsample_name in info['samples']
							and cat in hists
						)

						# Weight converts xsecflux absolute variance → targetpot absolute variance
						weight = (cv_scaled / cv_xf) ** 2

						if 'fluxvar' in xsec_hists:
							abs_var_flux  += xsec_hists['fluxvar'].GetBinContent(ibin)  * weight
						if 'xsecvar' in xsec_hists:
							abs_var_xsec  += xsec_hists['xsecvar'].GetBinContent(ibin)  * weight
						if 'reintvar' in xsec_hists:
							abs_var_reint += xsec_hists['reintvar'].GetBinContent(ibin) * weight

						# Per-parameter absolute variances
						# Skip detector-type params in truth_mode: pure truth selection
						# is unaffected by detector conditions.
						if 'param_vars' in xsec_hists:
							for pname, h_pv in xsec_hists['param_vars'].items():
								if pname in abs_var_params:
									if truth_mode and param_category.get(pname) == 'detector':
										continue
									abs_var_params[pname] += h_pv.GetBinContent(ibin) * weight

					except (AttributeError, ReferenceError):
						continue

				# Convert accumulated absolute variances → fractional variances
				frac_var_flux  = abs_var_flux  / (central ** 2) if central > 0 else 0.0
				frac_var_xsec  = abs_var_xsec  / (central ** 2) if central > 0 else 0.0
				frac_var_reint = abs_var_reint / (central ** 2) if central > 0 else 0.0
				for pname in frac_var_params:
					frac_var_params[pname] = abs_var_params.get(pname, 0.0) / (central ** 2)

				# Detector fractional variance from detsys file: zero in truth_mode
				# because a pure truth selection cannot change under detector variations.
				if not truth_mode and xsecflux_var in detsys_hists and 'frac_variance' in detsys_hists[xsecflux_var]:
					frac_var_detector = detsys_hists[xsecflux_var]['frac_variance'].GetBinContent(ibin)

				# Statistical fractional uncertainty
				n_unscaled   = h_total_mc_unscaled.GetBinContent(ibin)
				frac_var_stat = (1.0 / n_unscaled) if n_unscaled > 0 else 0.0

				# Total fractional variance (quadrature sum)
				frac_var_total = (frac_var_stat + frac_var_flux + frac_var_xsec
								  + frac_var_reint + frac_var_detector)

				# Set bin errors
				h_uncertainty_total.SetBinError(ibin,    central * sqrt(frac_var_total))
				h_uncertainty_flux.SetBinError(ibin,     central * sqrt(frac_var_flux))
				h_uncertainty_xsec.SetBinError(ibin,     central * sqrt(frac_var_xsec))
				h_uncertainty_reint.SetBinError(ibin,    central * sqrt(frac_var_reint))
				h_uncertainty_detector.SetBinError(ibin, central * sqrt(frac_var_detector))

				for pname in h_uncertainty_params:
					fv = frac_var_params.get(pname, 0.0)
					h_uncertainty_params[pname].SetBinError(ibin, central * sqrt(fv))

			# Style total uncertainty band
			h_uncertainty_total.SetFillColor(rt.kGray+1)
			h_uncertainty_total.SetFillStyle(3002)
			h_uncertainty_total.SetLineColor(rt.kGray+1)
			h_uncertainty_total.SetLineWidth(1)
			h_uncertainty_total.SetMarkerSize(0)

		# -----------------------------------------------------------------------
		# Draw main distribution
		# -----------------------------------------------------------------------
		stack_max = hstack.GetMaximum() if hstack.GetHists() else 0
		data_max  = hists['data'].GetMaximum() if 'data' in hists else 0
		y_max     = max(stack_max, data_max) * 1.5

		if show_ratio:
			title_parts     = var_info['title'].split(';')
			title_no_xlabel = (title_parts[0] + ';' + '; ' + title_parts[2]
							   if len(title_parts) > 2 else title_parts[0])
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

		if h_uncertainty_total is not None:
			h_uncertainty_total.Draw("E2same")

		if 'data' in hists:
			hists['data'].Draw("E1same")

		# Legend
		if show_ratio:
			legend = rt.TLegend(0.65, 0.40, 0.89, 0.89)
		else:
			legend = rt.TLegend(0.65, 0.50, 0.89, 0.89)
		legend.SetTextSize(0.03)
		legend.SetFillStyle(0)
		legend.SetBorderSize(1)

		for cat_name in stack_order:
			if cat_name in hists and cat_name in categories:
				legend.AddEntry(hists[cat_name], categories[cat_name]['legend'], "f")
		if 'data' in hists and not truth_mode:
			legend.AddEntry(hists['data'], categories['data']['legend'], "lep")
		if h_uncertainty_total is not None:
			legend.AddEntry(h_uncertainty_total, "Sys. uncertainty", "f")
		legend.Draw()

		if 'data' in hists and h_total_mc is not None:
			if chi_rebin:
				h_data_chi2 = hists['data'].Rebin(2, f"h_data_chi2_{var_name}")
				h_mc_chi2   = h_total_mc.Rebin(2, f"h_mc_chi2_{var_name}")
			else:
				h_data_chi2 = hists['data']
				h_mc_chi2   = h_total_mc
			chi2_val = ctypes.c_double(0)
			ndf_val  = ctypes.c_int(0)
			igood    = ctypes.c_int(0)
			h_data_chi2.Chi2TestX(h_mc_chi2, chi2_val, ndf_val, igood, "UW")
			chi2_ndf = chi2_val.value / ndf_val.value if ndf_val.value > 0 else 0.0
			chi2_latex = rt.TLatex()
			chi2_latex.SetNDC()
			chi2_latex.SetTextSize(0.030)
			chi2_latex.SetTextFont(42)
			chi2_latex.SetTextAlign(22)
			chi2_y = 0.34 if show_ratio else 0.47
			if show_chi2:
				chi2_latex.DrawLatex(0.77, chi2_y, f"\chi^2 = {chi2_ndf:.2f}")

		# Ratio panel
		if show_ratio and 'data' in hists and h_total_mc is not None:
			pad2.cd()

			h_ratio = hists['data'].Clone(f"h_ratio_{var_name}")
			h_ratio.Divide(h_total_mc)

			h_ratio_unc = h_total_mc.Clone(f"h_ratio_unc_{var_name}")
			for ibin in range(0, h_ratio_unc.GetNbinsX() + 2):
				mc_val = h_total_mc.GetBinContent(ibin)
				if mc_val > 0:
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
			h_ratio.GetYaxis().SetTitle("Data / Pred")
			h_ratio.GetXaxis().SetLabelSize(0.09)
			h_ratio.GetXaxis().SetTitleSize(0.1)
			h_ratio.GetXaxis().SetTitleOffset(1.1)
			h_ratio.GetXaxis().SetLabelOffset(0.01)
			h_ratio.GetYaxis().SetLabelSize(0.09)
			h_ratio.GetYaxis().SetTitleSize(0.1)
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

			line = rt.TLine(var_info['xmin'], 1.0, var_info['xmax'], 1.0)
			line.SetLineStyle(2)
			line.SetLineColor(rt.kBlack)
			line.SetLineWidth(2)
			line.Draw("same")

			pad2.Modified()
			pad2.Update()
			canvas.cd()

		if not show_ratio:
			canvas.SetTickx(1)
			canvas.SetTicky(1)
		canvas.Update()

		out.cd()
		canvas.Write()

		# -----------------------------------------------------------------------
		# Fractional error plots
		# -----------------------------------------------------------------------
		title_parts  = var_info['title'].split(';')
		x_axis_title = title_parts[1].strip() if len(title_parts) > 1 else ""

		canvas_frac = rt.TCanvas(f"c_{var_name}_{run_num}_frac_total", f"{var_name} Fractional Error", 1000, 600)
		canvas_frac.Draw()
		canvas_frac.SetTickx(1)
		canvas_frac.SetTicky(1)
		canvas_frac.SetRightMargin(0.05)

		h_frac_stat     = None
		h_frac_flux     = None
		h_frac_xsec     = None
		h_frac_reint    = None
		h_frac_detector = None
		h_frac_total    = None

		if h_total_mc is not None and h_uncertainty_total is not None:
			h_frac_stat     = h_total_mc.Clone(f"h_frac_stat_{var_name}");     h_frac_stat.Reset()
			h_frac_flux     = h_total_mc.Clone(f"h_frac_flux_{var_name}");     h_frac_flux.Reset()
			h_frac_xsec     = h_total_mc.Clone(f"h_frac_xsec_{var_name}");     h_frac_xsec.Reset()
			h_frac_reint    = h_total_mc.Clone(f"h_frac_reint_{var_name}");    h_frac_reint.Reset()
			h_frac_detector = h_total_mc.Clone(f"h_frac_detector_{var_name}"); h_frac_detector.Reset()
			h_frac_total    = h_total_mc.Clone(f"h_frac_total_{var_name}");    h_frac_total.Reset()

			# Per-parameter fractional error histograms
			h_frac_params = {
				pname: h_total_mc.Clone(f"h_frac_{pname}_{var_name}")
				for pname in h_uncertainty_params
			}
			for h in h_frac_params.values():
				h.Reset()

			for ibin in range(0, h_total_mc.GetNbinsX() + 2):
				central = h_total_mc.GetBinContent(ibin)
				if central <= 0:
					continue

				n_unscaled = h_total_mc_unscaled.GetBinContent(ibin)
				stat_frac  = 1.0 / sqrt(n_unscaled) if n_unscaled > 0 else 0.0

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

				for pname, h_fp in h_frac_params.items():
					par_frac = h_uncertainty_params[pname].GetBinError(ibin) / central
					h_fp.SetBinContent(ibin, par_frac)

			# Style aggregate fractional histograms
			def _style_frac(h, color, lw=2, ls=1):
				h.SetLineColor(color); h.SetLineWidth(lw); h.SetLineStyle(ls)
				h.SetFillStyle(0);     h.SetMarkerSize(0)

			_style_frac(h_frac_stat,     rt.kGray+2)
			_style_frac(h_frac_flux,     rt.kGreen+2)
			_style_frac(h_frac_xsec,     rt.kRed)
			_style_frac(h_frac_reint,    rt.kMagenta+1)
			_style_frac(h_frac_detector, rt.kBlue)
			_style_frac(h_frac_total,    rt.kBlack, lw=3)

			max_val = max(h_frac_stat.GetMaximum(), h_frac_flux.GetMaximum(),
						  h_frac_xsec.GetMaximum(), h_frac_reint.GetMaximum(),
						  h_frac_detector.GetMaximum(), h_frac_total.GetMaximum())

			frac_title = f"{plot_title}; {x_axis_title}; Fractional Uncertainty"
			h_frac_total.SetTitle(frac_title)
			h_frac_total.SetMaximum(max_val * 1.2)
			h_frac_total.SetMinimum(0.0)

			h_frac_total.Draw("hist")
			h_frac_stat.Draw("hist same")
			h_frac_flux.Draw("hist same")
			h_frac_xsec.Draw("hist same")
			h_frac_reint.Draw("hist same")
			h_frac_detector.Draw("hist same")

			h_frac_total.GetXaxis().SetLabelSize(0.04)
			h_frac_total.GetXaxis().SetTitleSize(0.04)
			h_frac_total.GetYaxis().SetLabelSize(0.04)
			h_frac_total.GetYaxis().SetTitleSize(0.04)
			h_frac_total.GetYaxis().SetTitle("Fractional Uncertainty")
			h_frac_total.GetYaxis().SetTitleOffset(1.2)

			leg_frac = rt.TLegend(0.60, 0.58, 0.94, 0.88)
			leg_frac.SetTextSize(0.032)
			leg_frac.SetTextFont(42)
			leg_frac.SetFillStyle(0)
			leg_frac.SetBorderSize(1)
			leg_frac.AddEntry(h_frac_total,    "Total",         "l")
			leg_frac.AddEntry(h_frac_stat,     "Statistical",   "l")
			leg_frac.AddEntry(h_frac_flux,     "Flux",          "l")
			leg_frac.AddEntry(h_frac_xsec,     "Cross Section", "l")
			leg_frac.AddEntry(h_frac_reint,    "Reinteraction", "l")
			leg_frac.AddEntry(h_frac_detector, "Detector",      "l")
			leg_frac.Draw()

			canvas_frac.Update()
			canvas_frac.RedrawAxis()
			out.cd()
			canvas_frac.Write()

			# -----------------------------------------------------------------------
			# Per-category fractional canvases: one canvas per category,
			# showing the aggregate total line (thick) + optional per-parameter
			# lines (thin gradient of the same hue). stat gets its own simple canvas.
			# -----------------------------------------------------------------------

			# Hard-coded flag: set False to hide individual parameter lines
			SHOW_PER_PARAM_LINES = True

			# Right margin used on all fractional canvases — legend is pinned inside it
			FRAC_RIGHT_MARGIN = 0.05

			def _make_legend(n_entries):
				"""
				Return a TLegend that sits inside the plot frame (respects FRAC_RIGHT_MARGIN).
				Height and font scale dynamically with entry count.
				"""
				if n_entries <= 4:
					text_size = 0.034
				elif n_entries <= 8:
					text_size = 0.028
				elif n_entries <= 14:
					text_size = 0.022
				else:
					text_size = 0.018

				row_height = text_size * 1.45
				leg_height = row_height * n_entries + 0.02
				leg_height = min(leg_height, 0.82)

				# Width grows slightly for many long entries
				leg_width = 0.30 if n_entries <= 4 else 0.38

				# Anchor right edge just inside the frame (account for right margin)
				x2 = 1.0 - FRAC_RIGHT_MARGIN - 0.01
				x1 = x2 - leg_width
				y2 = 0.88
				y1 = y2 - leg_height

				leg = rt.TLegend(x1, y1, x2, y2)
				leg.SetTextSize(text_size)
				leg.SetTextFont(42)
				leg.SetFillStyle(0)
				leg.SetBorderSize(1)
				return leg

			# Stat canvas — no per-parameter breakdown
			if h_frac_stat is not None:
				c_stat = rt.TCanvas(f"c_{var_name}_{run_num}_frac_stat",
									f"{var_name} Statistical Fractional Error", 1000, 600)
				c_stat.Draw()
				c_stat.SetTickx(1)
				c_stat.SetTicky(1)
				c_stat.SetRightMargin(FRAC_RIGHT_MARGIN)

				h_draw = h_frac_stat.Clone(f"h_frac_stat_{var_name}_draw")
				h_draw.SetTitle(f"{plot_title}; {x_axis_title}; Statistical Fractional Uncertainty")
				h_draw.SetLineColor(rt.kGray+2)
				h_draw.SetLineWidth(3)
				h_draw.SetLineStyle(1)
				h_draw.SetFillStyle(0)
				h_draw.SetMarkerSize(0)
				h_draw.SetMinimum(0.0)
				h_draw.SetMaximum(max(h_draw.GetMaximum() * 1.3, 0.01))
				h_draw.GetXaxis().SetLabelSize(0.04)
				h_draw.GetXaxis().SetTitleSize(0.04)
				h_draw.GetYaxis().SetLabelSize(0.04)
				h_draw.GetYaxis().SetTitleSize(0.04)
				h_draw.GetYaxis().SetTitleOffset(1.2)
				h_draw.Draw("hist")

				leg_s = _make_legend(1)
				leg_s.AddEntry(h_draw, "Statistical", "l")
				leg_s.Draw()

				c_stat.Update()
				c_stat.RedrawAxis()
				out.cd()
				c_stat.Write()

			# Systematic category canvases
			cat_tag_to_info = [
				('flux',     'Flux',          h_frac_flux,     rt.kGreen+2),
				('xsec',     'Cross Section', h_frac_xsec,     rt.kRed),
				('reint',    'Reinteraction', h_frac_reint,    rt.kMagenta+1),
				('detector', 'Detector',      h_frac_detector, rt.kBlue),
			]

			for cat_key, cat_label, h_frac_agg, base_color in cat_tag_to_info:
				if h_frac_agg is None:
					continue

				pnames_in_cat = [p for p in h_frac_params
								 if param_category.get(p) == cat_key]

				# Build per-parameter histograms with gradient colors
				par_draws = []
				max_cat   = h_frac_agg.GetMaximum()
				n_pars    = len(pnames_in_cat)

				if SHOW_PER_PARAM_LINES:
					# Rank parameters by their integrated fractional uncertainty
					# (sum of bin contents as a simple proxy for overall contribution)
					par_integrals = []
					for pname in pnames_in_cat:
						h_fp = h_frac_params.get(pname)
						if h_fp is None:
							continue
						par_integrals.append((pname, h_fp.Integral()))
					par_integrals.sort(key=lambda x: x[1], reverse=True)
					rank = {pname: i for i, (pname, _) in enumerate(par_integrals)}

					for pname in pnames_in_cat:
						h_fp = h_frac_params.get(pname)
						if h_fp is None:
							continue
						r = rank.get(pname, 99)
						if r == 0:
							par_color = base_color + 1
						elif r == 1:
							par_color = base_color - 1
						else:
							par_color = rt.kGray + 1

						h_draw = h_fp.Clone(f"h_frac_par_{pname}_{var_name}_catoverlay")
						h_draw.SetLineColor(par_color)
						h_draw.SetLineWidth(2)
						h_draw.SetLineStyle(1)
						h_draw.SetFillStyle(0)
						h_draw.SetMarkerSize(0)
						max_cat = max(max_cat, h_draw.GetMaximum())
						par_draws.append((h_draw, pname))

				# Aggregate total line for this category
				h_agg_draw = h_frac_agg.Clone(f"h_frac_{cat_key}_{var_name}_agg")
				h_agg_draw.SetTitle(
					f"{plot_title}; {x_axis_title}; {cat_label} Fractional Uncertainty")
				h_agg_draw.SetLineColor(base_color)
				h_agg_draw.SetLineWidth(4)
				h_agg_draw.SetLineStyle(1)
				h_agg_draw.SetFillStyle(0)
				h_agg_draw.SetMarkerSize(0)
				h_agg_draw.SetMinimum(0.0)
				h_agg_draw.SetMaximum(max_cat * 1.3 if max_cat > 0 else 0.1)
				h_agg_draw.GetXaxis().SetLabelSize(0.04)
				h_agg_draw.GetXaxis().SetTitleSize(0.04)
				h_agg_draw.GetYaxis().SetLabelSize(0.04)
				h_agg_draw.GetYaxis().SetTitleSize(0.04)
				h_agg_draw.GetYaxis().SetTitleOffset(1.2)

				c_cat = rt.TCanvas(f"c_{var_name}_{run_num}_frac_{cat_key}",
								   f"{var_name} {cat_label} Fractional Error", 1000, 600)
				c_cat.Draw()
				c_cat.SetTickx(1)
				c_cat.SetTicky(1)
				c_cat.SetRightMargin(FRAC_RIGHT_MARGIN)

				# Draw aggregate axes first to set range, then per-param, then agg on top
				h_agg_draw.Draw("hist")
				for h_draw, pname in par_draws:
					h_draw.Draw("hist same")
				h_agg_draw.Draw("hist same")

				# Dynamic legend
				n_leg_entries = 1 + len(par_draws)
				leg_cat = _make_legend(n_leg_entries)
				leg_cat.AddEntry(h_agg_draw, f"Total {cat_label}", "l")
				for h_draw, pname in par_draws:
					leg_cat.AddEntry(h_draw, pname, "l")
				leg_cat.Draw()

				c_cat.Update()
				c_cat.RedrawAxis()
				out.cd()
				c_cat.Write()

		# -----------------------------------------------------------------------
		# Purity plot
		# -----------------------------------------------------------------------
		dprint(f"\n=== Creating purity and efficiency plots for {var_name} ===")

		# Define which category represents "signal" for purity purposes.
		# In the pi0 channel the signal is all true-pi0 events (CC + NC).
		if fsp_channel == 'pi0':
			_signal_cats  = ['cc_pi0', 'nc_pi0']
			_purity_label = '#pi^{0} Purity'
		else:
			_signal_cats  = ['cc_numu']
			_purity_label = 'CC #nu_{#mu} Purity'

		_signal_hists = [hists[c] for c in _signal_cats if c in hists]

		if _signal_hists and h_total_mc is not None:
			h_purity = _signal_hists[0].Clone(f"h_purity_{var_name}")
			if len(_signal_hists) > 1:
				for _sh in _signal_hists[1:]:
					h_purity.Add(_sh)

			total_signal = h_purity.Integral()
			for ibin in range(0, h_purity.GetNbinsX() + 2):
				signal = h_purity.GetBinContent(ibin)
				total  = h_total_mc.GetBinContent(ibin)
				if total > 0:
					purity = signal / total
					h_purity.SetBinContent(ibin, purity)
					n_total_unscaled = h_total_mc_unscaled.GetBinContent(ibin)
					if n_total_unscaled > 0:
						h_purity.SetBinError(ibin, sqrt(purity * (1 - purity) / n_total_unscaled))
					else:
						h_purity.SetBinError(ibin, 0.0)
				else:
					h_purity.SetBinContent(ibin, 0.0)
					h_purity.SetBinError(ibin, 0.0)

			canvas_purity = rt.TCanvas(f"c_{var_name}_{run_num}_purity", f"{var_name} Purity", 1000, 600)
			canvas_purity.Draw()
			canvas_purity.SetTickx(1)
			canvas_purity.SetTicky(1)

			h_purity.SetTitle(f"{plot_title}; {x_axis_title}; ")
			h_purity.SetLineColor(rt.kBlue+1)
			h_purity.SetLineWidth(3)
			h_purity.SetMarkerStyle(20)
			h_purity.SetMarkerColor(rt.kBlue+1)
			h_purity.SetMarkerSize(1.0)
			h_purity.SetMinimum(0.0)
			h_purity.SetMaximum(1.1)
			h_purity.Draw("E1")

			line_purity = rt.TLine(var_info['xmin'], 1.0, var_info['xmax'], 1.0)
			line_purity.SetLineStyle(2)
			line_purity.SetLineColor(rt.kGray+2)
			line_purity.Draw("same")

			total_all    = h_total_mc.Integral()
			avg_purity   = total_signal / total_all if total_all > 0 else 0.0

			text_purity = rt.TLatex()
			text_purity.SetNDC()
			text_purity.SetTextSize(0.04)
			text_purity.DrawLatex(0.15, 0.85, f"Average Purity: {avg_purity:.3f}")

			canvas_purity.Update()
			out.cd()
			canvas_purity.Write()
			dprint(f"  Average purity: {avg_purity:.3f}")

		# -----------------------------------------------------------------------
		# Efficiency plot
		# -----------------------------------------------------------------------
		if 'true_var' in var_info:
			hname_denom = f'h_eff_denom_{var_name}'
			h_eff_denom = rt.TH1D(hname_denom, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
			h_eff_denom.Sumw2()

			truth_cut = "(numuIncCC_is_cc_interaction==1) && (true_vertex_properties_dwall > 3.0)"

			if run_num == 4:
				h_eff_denom_temp = rt.TH1D(f"{hname_denom}_temp", "",
										   var_info['nbins'], var_info['xmin'], var_info['xmax'])
				h_eff_denom_temp.Sumw2()
				for run_label in run4_labels:
					h_eff_denom_temp.Reset()
					trees[run_label]['numu'].Draw(f"{var_info['true_var']}>>{hname_denom}_temp",
												 f"({truth_cut})*eventweight_weight", "goff")
					h_eff_denom_temp.Scale(scaling[run_label]['numu'])
					h_eff_denom.Add(h_eff_denom_temp)
			else:
				trees['numu'].Draw(f"{var_info['true_var']}>>{hname_denom}",
								   f"({truth_cut})*eventweight_weight", "goff")
				h_eff_denom.Scale(scaling['numu'])

			hname_numer = f'h_eff_numer_{var_name}'
			h_eff_numer = rt.TH1D(hname_numer, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
			h_eff_numer.Sumw2()

			full_cut_eff = f"({base_cut}) && ({truth_cut}){var_info['cut_suffix']}"

			if run_num == 4:
				h_eff_numer_temp = rt.TH1D(f"{hname_numer}_temp", "",
										   var_info['nbins'], var_info['xmin'], var_info['xmax'])
				h_eff_numer_temp.Sumw2()
				for run_label in run4_labels:
					h_eff_numer_temp.Reset()
					trees[run_label]['numu'].Draw(f"{var_info['true_var']}>>{hname_numer}_temp",
												 f"({full_cut_eff})*eventweight_weight", "goff")
					h_eff_numer_temp.Scale(scaling[run_label]['numu'])
					h_eff_numer.Add(h_eff_numer_temp)
			else:
				trees['numu'].Draw(f"{var_info['true_var']}>>{hname_numer}",
								   f"({full_cut_eff})*eventweight_weight", "goff")
				h_eff_numer.Scale(scaling['numu'])

			h_efficiency = h_eff_numer.Clone(f"h_efficiency_{var_name}")
			h_efficiency.Divide(h_eff_denom)

			canvas_eff = rt.TCanvas(f"c_{var_name}_{run_num}_efficiency", f"{var_name} Efficiency", 1000, 600)
			canvas_eff.Draw()
			canvas_eff.SetTickx(1)
			canvas_eff.SetTicky(1)

			x_axis_title_eff = x_axis_title.replace("Reconstructed", "True")
			h_efficiency.SetTitle(f"{plot_title}; {x_axis_title_eff}; ")
			h_efficiency.SetLineColor(rt.kRed+1)
			h_efficiency.SetLineWidth(3)
			h_efficiency.SetMarkerStyle(21)
			h_efficiency.SetMarkerColor(rt.kRed+1)
			h_efficiency.SetMarkerSize(1.0)
			h_efficiency.SetMinimum(0.0)
			h_efficiency.SetMaximum(1.1)
			h_efficiency.Draw("E1")

			line_eff = rt.TLine(var_info['xmin'], 1.0, var_info['xmax'], 1.0)
			line_eff.SetLineStyle(2)
			line_eff.SetLineColor(rt.kGray+2)
			line_eff.Draw("same")

			total_selected  = h_eff_numer.Integral()
			total_true      = h_eff_denom.Integral()
			avg_efficiency  = total_selected / total_true if total_true > 0 else 0.0

			text_eff = rt.TLatex()
			text_eff.SetNDC()
			text_eff.SetTextSize(0.04)
			text_eff.DrawLatex(0.15, 0.85, f"Average Efficiency: {avg_efficiency:.3f}")

			canvas_eff.Update()
			out.cd()
			canvas_eff.Write()
			dprint(f"  Average efficiency: {avg_efficiency:.3f}")

		# Summary
		if fsp_channel == 'pi0':
			cc_numu_events = total_events.get('cc_pi0', 0) + total_events.get('nc_pi0', 0)
			cc_nue_events  = total_events.get('nue_bkg', 0)
			nc_events      = total_events.get('nc_no_pi0', 0)
		else:
			cc_numu_events = total_events.get('cc_numu', 0)
			cc_nue_events  = total_events.get('cc_nue', 0)
			nc_events      = total_events.get('nc_nue', 0) + total_events.get('nc_numu', 0)
		cosmic_events  = total_events.get('cosmic', 0)

	# ---------------------------------------------------------------------------
	# Cut flow efficiency and purity plot
	# ---------------------------------------------------------------------------
	if show_cut_flow:
		dprint("\n=== Creating cut flow efficiency/purity plot ===")

		truth_cut_eff = "(nueIncCC_true_ccnc==0 && true_vertex_properties_dwall>3.0)"

		# --- Fixed efficiency denominator: true CC nue in FV ---
		h_cf_denom = rt.TH1D("h_cf_denom", "", 1, 0, 1)
		h_cf_denom.Sumw2()

		if run_num == 4:
			h_cf_denom_tmp = rt.TH1D("h_cf_denom_tmp", "", 1, 0, 1)
			h_cf_denom_tmp.Sumw2()
			for run_label in run4_labels:
				h_cf_denom_tmp.Reset()
				trees[run_label]['numu'].Draw(
					"0.5>>h_cf_denom_tmp",
					f"({truth_cut_eff})*eventweight_weight", "goff")
				h_cf_denom_tmp.Scale(scaling[run_label]['numu'])
				h_cf_denom.Add(h_cf_denom_tmp)
		else:
			trees['numu'].Draw(
				"0.5>>h_cf_denom",
				f"({truth_cut_eff})*eventweight_weight", "goff")
			h_cf_denom.Scale(scaling['numu'])

		n_true_total = h_cf_denom.GetBinContent(1)
		dprint(f"  Efficiency denominator (true CC numu in FV): {n_true_total:.2f}")

		# --- Per-cut calculations ---
		efficiencies = []
		purities     = []
		n_tots       = []
		n_tots_fc    = []
		n_sig_effs   = []
		n_sigs       = []
		nue_veto     = " && (remove_true_nue_cc_flag==0)"

		# Pre-cut total (before any selection cut applied)
		h_tot_pre = rt.TH1D("h_numu_cf_tot_precut", "", 1, 0, 1)
		h_tot_pre.Sumw2()
		if run_num == 4:
			h_tot_pre_tmp = rt.TH1D("h_numu_cf_tot_precut_tmp", "", 1, 0, 1); h_tot_pre_tmp.Sumw2()
			for run_label in run4_labels:
				for sample in ['nue', 'numu', 'extbnb']:
					h_tot_pre_tmp.Reset()
					veto_pre = nue_veto if sample == 'numu' else ""
					trees[run_label][sample].Draw("0.5>>h_numu_cf_tot_precut_tmp", f"(1{veto_pre})*eventweight_weight", "goff")
					h_tot_pre_tmp.Scale(scaling[run_label][sample])
					h_tot_pre.Add(h_tot_pre_tmp)
		else:
			for sample in ['nue', 'numu', 'extbnb']:
				h_tmp_pre = rt.TH1D(f"h_numu_cf_tot_precut_{sample}", "", 1, 0, 1); h_tmp_pre.Sumw2()
				veto_pre = nue_veto if sample == 'numu' else ""
				trees[sample].Draw(f"0.5>>h_numu_cf_tot_precut_{sample}", f"(1{veto_pre})*eventweight_weight", "goff")
				h_tmp_pre.Scale(scaling[sample])
				h_tot_pre.Add(h_tmp_pre)
		n_tot_precut = h_tot_pre.GetBinContent(1)
		dprint(f"  Pre-cut total: {n_tot_precut:.2f}")

		if run_num == 4:
			h_sig_tmp     = rt.TH1D("h_cf_sig_tmp",     "", 1, 0, 1); h_sig_tmp.Sumw2()
			h_sig_eff_tmp = rt.TH1D("h_cf_sigeff_tmp",  "", 1, 0, 1); h_sig_eff_tmp.Sumw2()
			h_tot_tmp     = rt.TH1D("h_cf_tot_tmp",     "", 1, 0, 1); h_tot_tmp.Sumw2()
			h_fc_tmp      = rt.TH1D("h_numu_cf_fc_tmp", "", 1, 0, 1); h_fc_tmp.Sumw2()

		cumulative_cuts = []
		for cut_branch, cut_label in cut_flow_cuts:
			cumulative_cuts.append(f"({cut_branch}==1)")
			cut_str  = " && ".join(cumulative_cuts)

			# Purity numerator: CC nue from nue sample passing reco cut
			h_sig = rt.TH1D(f"h_cf_sig_{cut_branch}",  "", 1, 0, 1)
			h_sig.Sumw2()

			# Efficiency numerator: CC nue passing reco cut AND truth cut
			h_sig_eff = rt.TH1D(f"h_cf_sigeff_{cut_branch}", "", 1, 0, 1)
			h_sig_eff.Sumw2()

			# Purity denominator: all MC (nue + numu + extbnb) passing reco cut
			h_tot = rt.TH1D(f"h_cf_tot_{cut_branch}", "", 1, 0, 1)
			h_tot.Sumw2()

			cc_cut      = f"({cut_str}) && (numuIncCC_is_cc_interaction==1)"
			cc_cut_eff  = f"({cut_str}) && (numuIncCC_is_cc_interaction==1) && ({truth_cut_eff})"

			if run_num == 4:
				for run_label in run4_labels:
					h_sig_tmp.Reset()
					h_sig_eff_tmp.Reset()
					trees[run_label]['numu'].Draw(
						f"0.5>>h_cf_sig_tmp",
						f"({cc_cut})*eventweight_weight", "goff")
					trees[run_label]['numu'].Draw(
						f"0.5>>h_cf_sigeff_tmp",
						f"({cc_cut_eff})*eventweight_weight", "goff")
					h_sig_tmp.Scale(scaling[run_label]['numu'])
					h_sig_eff_tmp.Scale(scaling[run_label]['numu'])
					h_sig.Add(h_sig_tmp)
					h_sig_eff.Add(h_sig_eff_tmp)

					for sample in ['nue', 'numu', 'extbnb']:
						h_tot_tmp.Reset()
						veto = nue_veto if sample == 'numu' else ""
						trees[run_label][sample].Draw(
							f"0.5>>h_cf_tot_tmp",
							f"({cut_str}{veto})*eventweight_weight", "goff")
						h_tot_tmp.Scale(scaling[run_label][sample])
						h_tot.Add(h_tot_tmp)
			else:
				trees['numu'].Draw(
					f"0.5>>h_cf_sig_{cut_branch}",
					f"({cc_cut})*eventweight_weight", "goff")
				trees['numu'].Draw(
					f"0.5>>h_cf_sigeff_{cut_branch}",
					f"({cc_cut_eff})*eventweight_weight", "goff")
				h_sig.Scale(scaling['numu'])
				h_sig_eff.Scale(scaling['numu'])

				for sample in ['nue', 'numu', 'extbnb']:
					h_tmp = rt.TH1D(f"h_cf_tot_{cut_branch}_{sample}", "", 1, 0, 1)
					h_tmp.Sumw2()
					veto = nue_veto if sample == 'numu' else ""
					trees[sample].Draw(
						f"0.5>>h_cf_tot_{cut_branch}_{sample}",
						f"({cut_str}{veto})*eventweight_weight", "goff")
					h_tmp.Scale(scaling[sample])
					h_tot.Add(h_tmp)

			n_sig     = h_sig.GetBinContent(1)
			n_sig_eff = h_sig_eff.GetBinContent(1)
			n_tot     = h_tot.GetBinContent(1)

			eff = n_sig_eff / n_true_total if n_true_total > 0 else 0.0
			pur = n_sig     / n_tot        if n_tot > 0        else 0.0

			efficiencies.append(eff)
			purities.append(pur)
			if fully_contained or show_pc:
				h_fc = rt.TH1D(f"h_numu_cf_fc_{cut_branch}", "", 1, 0, 1)
				h_fc.Sumw2()
				fc_branch = "numuIncCC_true_is_fully_contained" if truth_mode else "numuIncCC_is_fully_contained"
				fc_str = f"{cut_str} && ({fc_branch}==1)"
				if run_num == 4:
					for run_label in run4_labels:
						for sample in ['nue', 'numu', 'extbnb']:
							h_fc_tmp.Reset()
							veto = nue_veto if sample == 'numu' else ""
							trees[run_label][sample].Draw(f"0.5>>h_numu_cf_fc_tmp", f"({fc_str}{veto})*eventweight_weight", "goff")
							h_fc_tmp.Scale(scaling[run_label][sample])
							h_fc.Add(h_fc_tmp)
				else:
					for sample in ['nue', 'numu', 'extbnb']:
						h_fc_s = rt.TH1D(f"h_numu_cf_fc_{cut_branch}_{sample}", "", 1, 0, 1)
						h_fc_s.Sumw2()
						veto = nue_veto if sample == 'numu' else ""
						trees[sample].Draw(f"0.5>>h_numu_cf_fc_{cut_branch}_{sample}", f"({fc_str}{veto})*eventweight_weight", "goff")
						h_fc_s.Scale(scaling[sample])
						h_fc.Add(h_fc_s)
				n_tots_fc.append(h_fc.GetBinContent(1))
			else:
				n_tots_fc.append(0.0)
			n_tots.append(n_tot)
			n_sig_effs.append(n_sig_eff)
			n_sigs.append(n_sig)
			dprint(f"  {cut_label.replace(chr(10), ' ')}: "
				  f"eff={eff:.3f}  pur={pur:.3f}  "
				  f"sig={n_sig:.1f}  tot={n_tot:.1f}")

		# --- Build labeled histograms ---
		n_cuts = len(cut_flow_cuts)

		h_eff_cf = rt.TH1D("h_numu_cutflow_efficiency", "", n_cuts, -0.5, n_cuts - 0.5)
		h_pur_cf = rt.TH1D("h_numu_cutflow_purity",     "", n_cuts, -0.5, n_cuts - 0.5)

		eff_errs = []
		pur_errs = []
		for i, (eff, pur, n_se, n_s, n_t) in enumerate(zip(efficiencies, purities, n_sig_effs, n_sigs, n_tots)):
			e_err = sqrt(max(0.0, n_se)) / n_true_total if n_true_total > 0 else 0.0
			p_err = sqrt(max(0.0, n_s))  / n_t          if n_t > 0          else 0.0
			h_eff_cf.SetBinContent(i + 1, eff)
			h_pur_cf.SetBinContent(i + 1, pur)
			h_eff_cf.SetBinError(i + 1, e_err)
			h_pur_cf.SetBinError(i + 1, p_err)
			eff_errs.append(e_err)
			pur_errs.append(p_err)

		for i, (_, cut_label) in enumerate(cut_flow_cuts):
			label_single_line = cut_label.replace('\n', ' ')
			h_eff_cf.GetXaxis().SetBinLabel(i + 1, label_single_line)
			h_pur_cf.GetXaxis().SetBinLabel(i + 1, label_single_line)

		# --- Build TGraphErrors for straight point-to-point lines ---
		xs     = array.array('d', range(n_cuts))
		xerrs  = array.array('d', [0.0] * n_cuts)
		g_eff_cf = rt.TGraphErrors(n_cuts, xs, array.array('d', efficiencies), xerrs, array.array('d', eff_errs))
		g_pur_cf = rt.TGraphErrors(n_cuts, xs, array.array('d', purities),     xerrs, array.array('d', pur_errs))

		# --- Style ---
		g_eff_cf.SetLineColor(rt.kRed + 1)
		g_eff_cf.SetLineWidth(3)
		g_eff_cf.SetMarkerStyle(21)
		g_eff_cf.SetMarkerColor(rt.kRed + 1)
		g_eff_cf.SetMarkerSize(1.3)

		g_pur_cf.SetLineColor(rt.kBlue + 1)
		g_pur_cf.SetLineWidth(3)
		g_pur_cf.SetMarkerStyle(20)
		g_pur_cf.SetMarkerColor(rt.kBlue + 1)
		g_pur_cf.SetMarkerSize(1.3)

		# --- Canvas ---
		canvas_cf = rt.TCanvas(f"c_numu_cutflow_{run_num}", "Cut Flow Efficiency and Purity", 1200, 650)
		canvas_cf.Draw()
		canvas_cf.cd()
		canvas_cf.SetBottomMargin(0.15)
		canvas_cf.SetLeftMargin(0.10)
		canvas_cf.SetRightMargin(0.05)

		# h_eff_cf used only as axis frame with bin labels
		h_eff_cf.SetTitle(f";Cuts;Efficiency & Purity")
		h_eff_cf.SetMinimum(0.0)
		h_eff_cf.SetMaximum(1.15)
		h_eff_cf.GetXaxis().SetLabelSize(0.042)
		h_eff_cf.GetXaxis().SetLabelOffset(0.008)
		h_eff_cf.GetXaxis().SetTickLength(0)
		h_eff_cf.GetYaxis().SetLabelSize(0.040)
		h_eff_cf.GetYaxis().SetTitleSize(0.042)
		h_eff_cf.GetYaxis().SetTitleOffset(1.0)

		h_eff_cf.Draw("AXIS")
		g_eff_cf.Draw("PL same")
		g_pur_cf.Draw("PL same")

		title_cf = rt.TLatex()
		title_cf.SetNDC()
		title_cf.SetTextSize(0.045)
		title_cf.SetTextAlign(21)
		title_cf.SetTextFont(42)
		title_cf.DrawLatex(0.525, 0.93, f"Run {run_num}: CC Inclusive Numu Selection Cuts")

		# Annotate each point above the error bar top
		text_cf = rt.TLatex()
		text_cf.SetTextSize(0.028)
		text_cf.SetTextAlign(21)  # centre-bottom
		text_cf.SetTextColor(rt.kBlack)
		for i, (eff, pur, e_err, p_err) in enumerate(zip(efficiencies, purities, eff_errs, pur_errs)):
			x = i
			text_cf.DrawLatex(x, eff + e_err + 0.03, f"{eff:.2f}")
			text_cf.DrawLatex(x, pur + p_err + 0.03, f"{pur:.2f}")

		leg_cf = rt.TLegend(0.12, 0.20, 0.42, 0.27)
		leg_cf.SetNColumns(2)
		leg_cf.SetTextSize(0.036)
		leg_cf.SetFillStyle(1001)
		leg_cf.SetFillColor(rt.kWhite)
		leg_cf.SetBorderSize(0)
		leg_cf.AddEntry(g_eff_cf, "Efficiency", "lp")
		leg_cf.AddEntry(g_pur_cf, "Purity",     "lp")
		leg_cf.Draw()

		canvas_cf.Update()
		canvas_cf.RedrawAxis()
		out.cd()
		canvas_cf.Write()
		dprint("  Cut flow plot saved.")

		# --- Events-removed stacked plot ---
		n_tots_all     = [n_tot_precut] + n_tots
		n_removed_list = [n_tots_all[i] - n_tots_all[i + 1] for i in range(n_cuts)]

		h_removed_cf = rt.TH1D("h_numu_cutflow_removed", "", n_cuts, 0, n_cuts)
		h_removed_cf.SetFillColor(rt.kOrange + 7)
		h_removed_cf.SetLineColor(rt.kOrange + 9)

		stack_rem = rt.THStack("stack_numu_cutflow_removed", "")

		if show_pc:
			h_kept_fc_cf = rt.TH1D("h_numu_cutflow_kept_fc", "", n_cuts, 0, n_cuts)
			h_kept_pc_cf = rt.TH1D("h_numu_cutflow_kept_pc", "", n_cuts, 0, n_cuts)
			for i in range(n_cuts):
				h_kept_fc_cf.SetBinContent(i + 1, n_tots_fc[i])
				h_kept_pc_cf.SetBinContent(i + 1, n_tots[i] - n_tots_fc[i])
				h_removed_cf.SetBinContent(i + 1, n_removed_list[i])
			for i, (_, cut_label) in enumerate(cut_flow_cuts):
				lbl = cut_label.replace('\n', ' ')
				h_kept_fc_cf.GetXaxis().SetBinLabel(i + 1, lbl)
				h_kept_pc_cf.GetXaxis().SetBinLabel(i + 1, lbl)
				h_removed_cf.GetXaxis().SetBinLabel(i + 1, lbl)
			h_kept_fc_cf.SetFillColor(rt.kGreen + 2)
			h_kept_fc_cf.SetLineColor(rt.kGreen + 4)
			h_kept_pc_cf.SetFillColor(rt.kAzure + 1)
			h_kept_pc_cf.SetLineColor(rt.kAzure + 3)
			stack_rem.Add(h_kept_fc_cf)
			stack_rem.Add(h_kept_pc_cf)
		else:
			h_kept_cf = rt.TH1D("h_numu_cutflow_kept", "", n_cuts, 0, n_cuts)
			for i in range(n_cuts):
				h_kept_cf.SetBinContent(i + 1, n_tots[i])
				h_removed_cf.SetBinContent(i + 1, n_removed_list[i])
			for i, (_, cut_label) in enumerate(cut_flow_cuts):
				lbl = cut_label.replace('\n', ' ')
				h_kept_cf.GetXaxis().SetBinLabel(i + 1, lbl)
				h_removed_cf.GetXaxis().SetBinLabel(i + 1, lbl)
			h_kept_cf.SetFillColor(rt.kAzure + 1)
			h_kept_cf.SetLineColor(rt.kAzure + 3)
			stack_rem.Add(h_kept_cf)
		stack_rem.Add(h_removed_cf)

		canvas_rem = rt.TCanvas(f"c_numu_cutflow_removed_{run_num}", "Events Cut and Kept at Each Cut", 1200, 650)
		canvas_rem.Draw()
		canvas_rem.cd()
		canvas_rem.SetLogy(1)
		canvas_rem.SetBottomMargin(0.25)
		canvas_rem.SetLeftMargin(0.14)
		canvas_rem.SetRightMargin(0.05)
		canvas_rem.SetTickx(1)
		canvas_rem.SetTicky(1)

		max_total = max(n_tots_all[:-1]) if len(n_tots_all) > 1 else 1.0
		stack_rem.SetMaximum(max_total * 8)
		stack_rem.SetMinimum(0.5)
		stack_rem.SetTitle(f"Numu Run {run_num}: Number of Events by Cut")
		stack_rem.Draw("HIST")
		stack_rem.GetHistogram().GetXaxis().SetLabelSize(0.048)
		stack_rem.GetHistogram().GetXaxis().SetLabelOffset(0.005)
		stack_rem.GetHistogram().GetXaxis().SetTitle("Cuts")
		stack_rem.GetHistogram().GetXaxis().SetTitleSize(0.042)
		stack_rem.GetHistogram().GetXaxis().SetTitleOffset(1.5)
		stack_rem.GetHistogram().GetYaxis().SetTitle("Events")
		stack_rem.GetHistogram().GetYaxis().SetLabelSize(0.040)
		stack_rem.GetHistogram().GetYaxis().SetTitleSize(0.042)
		stack_rem.GetHistogram().GetYaxis().SetTitleOffset(1.4)

		text_rem = rt.TLatex()
		text_rem.SetTextSize(0.028)
		text_rem.SetTextAlign(21)
		text_rem.SetTextColor(rt.kBlack)
		if show_pc:
			for i in range(n_cuts):
				fc_val  = n_tots_fc[i]
				pc_val  = n_tots[i] - n_tots_fc[i]
				rem_val = n_removed_list[i]
				if fc_val > 0.5:
					text_rem.DrawLatex(i + 0.5, (0.5 * fc_val) ** 0.5, f"{fc_val:.1f}")
				if pc_val > 0.5 and fc_val > 0.5:
					text_rem.DrawLatex(i + 0.5, (fc_val * n_tots[i]) ** 0.5, f"{pc_val:.1f}")
				elif pc_val > 0.5:
					text_rem.DrawLatex(i + 0.5, (0.5 * n_tots[i]) ** 0.5, f"{pc_val:.1f}")
				if rem_val > 0.5:
					bot = n_tots[i] if n_tots[i] > 0.5 else 0.5
					text_rem.DrawLatex(i + 0.5, (bot * (n_tots[i] + rem_val)) ** 0.5, f"{rem_val:.1f}")
		else:
			for i in range(n_cuts):
				kept_val = n_tots[i]
				rem_val  = n_removed_list[i]
				if kept_val > 0.5:
					text_rem.DrawLatex(i + 0.5, (0.5 * kept_val) ** 0.5, f"{kept_val:.1f}")
				if rem_val > 0.5:
					bot = kept_val if kept_val > 0.5 else 0.5
					text_rem.DrawLatex(i + 0.5, (bot * (kept_val + rem_val)) ** 0.5, f"{rem_val:.1f}")

		if show_pc:
			leg_rem = rt.TLegend(0.30, 0.88, 0.92, 0.96)
			leg_rem.SetNColumns(3)
			leg_rem.SetTextSize(0.034)
			leg_rem.SetFillStyle(0)
			leg_rem.SetBorderSize(1)
			leg_rem.AddEntry(h_kept_fc_cf, "Fully Contained",    "f")
			leg_rem.AddEntry(h_kept_pc_cf, "Partially Contained","f")
			leg_rem.AddEntry(h_removed_cf, "Removed",            "f")
		else:
			leg_rem = rt.TLegend(0.55, 0.88, 0.92, 0.96)
			leg_rem.SetNColumns(2)
			leg_rem.SetTextSize(0.034)
			leg_rem.SetFillStyle(0)
			leg_rem.SetBorderSize(1)
			leg_rem.AddEntry(h_kept_cf,    "Kept",    "f")
			leg_rem.AddEntry(h_removed_cf, "Removed", "f")
		leg_rem.Draw()

		canvas_rem.Update()
		canvas_rem.RedrawAxis()
		out.cd()
		canvas_rem.Write()
		dprint("  Events-removed stacked cut flow plot saved.")

	print("Saved:", out_name)
	out.Close()

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug output")
	args = parser.parse_args()

	run_string = " Default"
	if use_truth: 
		run_string = " Truth"
	if use_fully_contained:
		run_string += " Fully_contained"
	print(f"Selection:{run_string}")

	for n in runs:
		run_plots(n, truth_mode = use_truth, fully_contained = use_fully_contained,
		show_pc = True, fsp_channel=fsp_channel, debug = args.verbose)

	if plot_nue:
		print("\nRunning nue plots...")
		import sys as _sys, os as _os
		_script_dir = _os.path.dirname(_os.path.abspath(__file__))
		if _script_dir not in _sys.path:
			_sys.path.insert(0, _script_dir)
		import plot_nue
		_nue_fsp_map = {'inc': 'inc', 'pi0': 'pi0', '0p': '0p', '1p': '1p', 'Np': 'Np'}
		_nue_fsp = _nue_fsp_map.get(fsp_channel, 'inc')
		for n in runs:
			plot_nue.run_plots(n, truth_mode=use_truth, fully_contained=use_fully_contained,
							show_pc=True, fsp_channel=_nue_fsp, debug=args.verbose)
