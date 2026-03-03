import os,sys
import ROOT as rt
import array
from math import sqrt

run_num = 3

# lantern_dir = "/cluster/tufts/wongjiradlabnu/zimani01/lantern/lantern_ana/"
lantern_dir = "/exp/uboone/app/users/imani/lantern_ana/"

## Run 1 
if run_num == 1: 
	targetpot = 4.4e19
	scaling = {"numu":targetpot/4.675690535431973e+20,
			"nue":targetpot/9.662529168587103e+22,
			"extbnb":(176153.0)/(433446.0),
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_bnb_nu_overlay_mcc9_v28_wctagger.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_bnb_nue_overlay_mcc9_v28_wctagger.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_extbnb_mcc9_v29e_C1.root",
			"data":f"{lantern_dir}/all_runs_mmr/run1/root_files/selection/run1_bnb5e19.root"}
	xsecflux_files = {
		"nue": f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_nue_intrinsic_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_nue_overlay_nu.root"
	}
	detsys_file = None
	detsys_params = []
	detsys_variables = []
	show_data = True 
	data_legend = "Run1 5e19"
	plot_title = "Run 1: CC Inclusive Nue"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/nue_run1_hists.root"
	remove_cut = ""
	hist_vars = ["nueIncCC_reco_nu_energy",]
	xsecflux_variables = ['visible_energy', 'electron_momentum', 'electron_angle']
	var_name_map = {
	'neutrino_energy': 'visible_energy',
	'electron_momentum': 'electron_momentum',
	'electron_costheta': 'electron_angle'
	}
	xsecflux_sample_map = {
		'numu': 'run1_bnb_nu_overlay_mcc9_v28_wctagger',
		'nue': 'run1_bnb_nue_overlay_mcc9_v28_wctagger'
	}

## Run 3b 
if run_num == 3: 
	targetpot = 5e19
	scaling = {"numu":targetpot/8.98323351831587e+20,
			"nue":targetpot/4.702159572049976e+22,
			"extbnb":(176153)/(223580),  # Trigger ratio
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_bnb_nu_overlay_20260112_154048.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_bnb_nue_overlay_20260112_155555.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_extbnb_20260112_160141.root",
			"data":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_data_20260112_175802.root"}
	xsecflux_files = {
		"nue": f"{lantern_dir}/all_runs_mmr/run3/root_files/xsecflux/run3b_nue_covar_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run3/root_files/xsecflux/run3b_nue_covar_nu.root"
	}
	detsys_file = None
	detsys_params = []
	detsys_variables = []
	show_data = True 
	data_legend = "Run1 5e19"
	plot_title = "Run 3: CC Inclusive Nue"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/nue_run3_hists.root"
	remove_cut = "&& (remove_true_nue_cc_flag==0)"
	# remove_cut = ""
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_electron_energy', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'reco_neutrino_energy',
	'electron_momentum': 'reco_electron_energy',
	'electron_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'numu': 'run3b_nu',
		'nue': 'run3b_nue'  # Not used, but keeping for consistency
	}


## Run 3mil
if run_num == 30: 
	targetpot = 8.806e18
	scaling = {"numu":targetpot/1.346689484233034e+21,
			"nue":targetpot/2.891774385462469e+22,
			"extbnb": (2263559.0)/(19214565.0),
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_nu_20260122_162913.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_nue_20260123_181343.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run3/root_files/selection/run3b_extbnb_20260123_164522.root",
			"data":f"{lantern_dir}/all_runs_mmr/run3mil/root_files/selection/run3mil_data_20260126_180100.root"}
	xsecflux_files = {
		"nue": f"{lantern_dir}/all_runs_mmr/run3mil/root_files/xsecflux/xsecflux_run3mil_nue_bnb_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run3mil/root_files/xsecflux/xsecflux_run3mil_nue_bnb_nu.root"
	}
	detsys_file = None
	detsys_params = []
	detsys_variables = []
	show_data = True 
	data_legend = "Run3 1e19"
	plot_title = "Run 3 1mil: CC Inclusive Nue"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/nue_run3mil_hists.root"
	remove_cut = "&& (remove_true_nue_cc_flag==0)"
	xsecflux_variables = ['visible_energy', 'reco_electron_energy', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'visible_energy',
	'electron_momentum': 'reco_electron_energy',
	'electron_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'nue': 'run3mil_nue', # Not used, but keeping for consistency
		'numu': 'run3mil_nu'  
	}


## Run 4b (Suprise Files) 
if run_num == 4: 
	targetpot = 1.45e+20
	scaling = {"numu":targetpot/7.881656209241413e+20,
			"nue":targetpot/1.1785765118473412e+23,
			"extbnb":34317881.0/96638186.0,
			"data":1.0}
	files = {"numu": f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nu_overlay_20260114_214914.root",
			"nue":f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_bnb_nue_overlay_20260114_205851.root", 
			"extbnb":f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_extbnb_20260114_212008.root",
			"data":f"{lantern_dir}/all_runs_mmr/run4b/root_files/selection/run4b_data_20260114_212707.root"}
	xsecflux_files = {
		"numu": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_run4b_nue_nu.root",
		"nue": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/xsecflux_run4b_nue_nue.root"
		}
	detsys_file = f"{lantern_dir}/all_runs_mmr/run4b/root_files/detsys_final/detsys_cv_run4b_nue_cv.root"
	show_data = False 
	data_legend = "Run1 5e19"
	plot_title = "Run 4b: CC Inclusive Nue"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/nue_run4b_hists.root"
	remove_cut = "&& (remove_true_nue_cc_flag==0)"
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_electron_energy', 'reco_cos_theta']
	detsys_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_electron_energy', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'reco_neutrino_energy',
	'electron_momentum': 'reco_electron_energy',
	'electron_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'nue': 'run4b_nue', # Not used, but keeping for consistency
		'numu': 'run4b_nu'  
	}
	# Detector variation parameters
	detsys_params = [
		"wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ",
		"wiremodAngleXZ", "wiremodAngleYZ", "recomb2", "SCE", "LArG4BugFix"
	]

# Function to identify systematic type based on name
def identify_systematic_type(syst_name):
	"""Identify if systematic is flux, xsec, reinteraction, or detector based on name"""
	syst_lower = syst_name.lower()
	
	# Flux keywords
	flux_keywords = ['flux', 'horn', 'beam', 'kminus', 'kplus', 'kzero', 
					 'piminus', 'piplus', 'nucleon', 'expskin']
	
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
		"piminus_PrimaryHadronSWCentralSplineVariation",
		"piplus_PrimaryHadronSWCentralSplineVariation"
	]
	genie_params = [
		"All_UBGenie"
	]
	other_xsec = [
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
		"reinteractions_piminus_Geant4",
		"reinteractions_piplus_Geant4",
		"reinteractions_proton_Geant4"
	]
	all_pars = flux_params+genie_params+other_xsec

if run_num == 4: 
	flux_params = [
		"flux_all"
	] 

	genie_params = [
		"All_UBGenie"
	]

	other_xsec = [
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
		# Note: reinteraction systematics not included in run4b
	]

	reint = [
    	"reint_all"
	]
	
	detector = [
		"detvar_all"
	]

	# - RootinoFix_UBGenie        # Ignore? 
	# - TunedCentralValue_UBGenie # Ignore?
	# - ppfx_all                  # Ignore? 
	# - splines_general_Spline    # Ignore?

	all_pars = flux_params + genie_params + other_xsec + reint + detector


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
		if n_loaded <= 3:
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
		
		# print(f"    Loaded {parname}")
		hists[parname] = hvar
		
		# Identify the type of systematic
		syst_type = identify_systematic_type(parname)
				
		# Add variance to appropriate category
		for ibin in range(0, hvar_tot.GetXaxis().GetNbins()+1):
			xvar = hvar.GetBinContent(ibin)
			xmean = hmean.GetBinContent(ibin)
			
			## uncertianty scaling 
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
base_cut = f"(nueIncCC_passes_all_cuts==1)"

# Define sample categories with ROOT standard colors
categories = {
	'cosmic': {
		'samples': ['extbnb'],
		'truth_cut': f' ',  # No truth cut for cosmic background
		'color': rt.kGray+2,
		'fill_style': 1001,
		'legend': 'BNB EXT'
	},
	'nc_numu': {
		'samples': ['numu'],
		'truth_cut': f' && (nueIncCC_is_neutral_current==1)', 
		'color': rt.kGreen+1,  # Green  
		'fill_style': 1001,
		'legend': 'NC numu'
	},
	'nc_nue': {
		'samples': ['nue'],
		'truth_cut': f' && (nueIncCC_is_neutral_current==1)',
		'color':  rt.kViolet-1,  # Purple
		'fill_style': 1001,
		'legend': 'NC nue'
	},
	'cc_numu': {
		'samples': ['numu'],
		'truth_cut': f' && (nueIncCC_is_charge_current==1)'+remove_cut,
		'color': rt.kAzure+1,  # Blue
		'fill_style': 1001,
		'legend': 'CC numu'
	},
	'cc_nue': {
		'samples': ['nue'], 
		'truth_cut': f' && (nueIncCC_is_charge_current==1)',
		'color': rt.kRed-4,  # Red/orange
		'fill_style': 1001,
		'legend': 'CC nue'
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

# Define variables to plot
variables = {
	'neutrino_energy': {
		'var': 'nueIncCC_reco_nu_energy',
		'nbins': 30,
		'xmin': 0.0,
		'xmax': 3.0,
		'title': plot_title+'; Reconstructed Neutrino Energy (GeV); '+legend_POT_string,
		'cut_suffix': '',
		'y_max': 30,
		'rebin_config': {
			'type': 'variable',
			'bins': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
			'overflow': True
		}
	},
	'electron_momentum': {
		'var': 'nueIncCC_reco_electron_momentum',
		'nbins': 25,
		'xmin': 0.0,
		'xmax': 1.5,
		'title': plot_title+'; Reconstructed Electron Momentum (GeV); '+legend_POT_string,
		'cut_suffix': '&& (nueIncCC_reco_electron_momentum>0)',
		'rebin_config': {
			'type': 'constant',
			'factor': 2,
			'overflow': True
		}
	},
	'electron_costheta': {
		'var': 'nueIncCC_reco_electron_costheta',
		'nbins': 20,
		'xmin': -1.0,
		'xmax': 1.0,
		'title': plot_title+'; Reconstructed Electron cos(#theta); '+legend_POT_string,
		'cut_suffix': '&& (nueIncCC_reco_electron_costheta>-900)',
		'rebin_config': {
			'type': 'range',
			'xmin': 0.0,
			'xmax': 1.0,
			'underflow': True
		}
	}
}

# Load xsecflux uncertainties for each sample
xsecflux_hists = {}
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

# Load detector variations for run 4b
detsys_hists = {}
if run_num == 4 and detsys_file is not None:
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
	
	# Create canvas for main histogram
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
	stack_order = ['cosmic', 'nc_numu', 'nc_nue', 'cc_numu', 'cc_nue']
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

	# Apply rebinning if configured
	rebin_config = var_info.get('rebin_config', {})
	
	if rebin_config:
		rebin_type = rebin_config.get('type', 'constant')
		
		if rebin_type == 'variable':
			new_bins = array.array('d', rebin_config['bins'])
			for cat_name in hists:
				hists[cat_name] = hists[cat_name].Rebin(len(new_bins)-1, hists[cat_name].GetName()+"_rebin", new_bins)
			if h_total_mc is not None:
				h_total_mc = h_total_mc.Rebin(len(new_bins)-1, h_total_mc.GetName()+"_rebin", new_bins)
			if h_total_mc_unscaled is not None:
				h_total_mc_unscaled = h_total_mc_unscaled.Rebin(len(new_bins)-1, h_total_mc_unscaled.GetName()+"_rebin", new_bins)
		
		elif rebin_type == 'constant':
			rebin_factor = rebin_config.get('factor', 2)
			for cat_name in hists:
				hists[cat_name].Rebin(rebin_factor)
			if h_total_mc is not None:
				h_total_mc.Rebin(rebin_factor)
			if h_total_mc_unscaled is not None:
				h_total_mc_unscaled.Rebin(rebin_factor)
		
		# Rebuild stack with rebinned histograms
		hstack = rt.THStack(f"hs_{var_name}", "")
		for cat_name in stack_order:
			if cat_name in hists and cat_name != 'data':
				hstack.Add(hists[cat_name])

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
			# Note: detector variations come from separate detsys file with CV and variation histograms
			# Fractional variance is already calculated as ((var - cv) / cv)^2 and combined in quadrature
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

	if stack_max > data_max:
		hstack.SetTitle(var_info['title'])
		hstack.Draw("hist")
		hstack.SetMaximum(y_max)
	else:
		hists['data'].SetTitle(var_info['title'])
		hists['data'].Draw("E1")
		hists['data'].SetMaximum(y_max)
		hstack.Draw("histsame")

	# Draw uncertainty band
	if h_uncertainty_total is not None:
		h_uncertainty_total.Draw("E2same")

	# Draw data on top
	if 'data' in hists:
		hists['data'].Draw("E1same")
	
	# Set x-axis range for cos theta
	if var_name == 'electron_costheta':
		if hstack.GetHists():
			hstack.GetXaxis().SetRangeUser(0.0, 1.0)
		else:
			hists['data'].GetXaxis().SetRangeUser(0.0, 1.0)


	# Create legend
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

	canvas.SetTickx(1)
	canvas.SetTicky(1)
	canvas.SetLogy(0)
	canvas.Update()

	out.cd()
	canvas.Write()

	# === Create SEPARATE canvas for fractional error plot ===
	canvas_frac = rt.TCanvas(f"c_{var_name}_frac_error", f"{var_name} Fractional Error", 1000, 600)
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
				# Statistical uncertainty: 1/sqrt(N) using UNSCALED event count
				n_unscaled = h_total_mc_unscaled.GetBinContent(ibin)
				if n_unscaled > 0:
					# Fractional error = 1/sqrt(n_unscaled)
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
		
		# Set range
		if var_name == 'electron_costheta':
			h_frac_total.GetXaxis().SetRangeUser(0.0, 1.0)
		
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
		
		print(f"  Fractional error plot saved for {var_name}")

	# CC νe purity
	cc_nue_events = total_events.get('cc_nue', 0)
	
	# Background breakdown
	cosmic_events = total_events.get('cosmic', 0)
	cc_numu_events = total_events.get('cc_numu', 0)
	nc_events = total_events.get('nc_nue', 0) + total_events.get('nc_numu', 0)

	print(f"Plot saved for {var_name}")

print("\nSaved to", out_name)
out.Close()