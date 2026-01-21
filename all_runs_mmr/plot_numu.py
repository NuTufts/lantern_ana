import os,sys
import ROOT as rt
import array
from math import sqrt

run_num = 3

lantern_dir = "/exp/uboone/app/users/imani/lantern_ana"

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
		"nue": f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_numu_intrinsic_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run1/root_files/xsecflux/xsecflux_run1_numu_overlay_nu.root"
	}
	show_data = True 
	plot_title = "Run 1: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu_run1_hists.root"
	xsecflux_variables = ['visible_energy', 'muon_momentum', 'muon_angle']
	var_name_map = {
	'neutrino_energy': 'visible_energy',
	'muon_momentum': 'muon_momentum',
	'muon_costheta': 'muon_angle'
}


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
	show_data = True 
	plot_title = "Run 3: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu_run3_hists.root"
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'reco_neutrino_energy',
	'muon_momentum': 'reco_muon_momentum',
	'muon_costheta': 'reco_cos_theta'
	}


## Run 4b 
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
		"nue": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/run4b_numu_covar_nue.root",
		"numu": f"{lantern_dir}/all_runs_mmr/run4b/root_files/xsecflux/run4b_numu_covar_nu.root"
		}
	show_data = True 
	plot_title = "Run 4b: CC Inclusive Numu"
	out_name = f"{lantern_dir}/all_runs_mmr/plots/numu_run4b_hists.root"
	xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_momentum', 'reco_cos_theta']
	var_name_map = {
	'neutrino_energy': 'reco_neutrino_energy',
	'muon_momentum': 'reco_muon_momentum',
	'muon_costheta': 'reco_cos_theta'
	}
	xsecflux_sample_map = {
		'nue': 'run4b_nue', # Not used, but keeping for consistency
		'numu': 'run4b_nu'  
	}


# Function to identify systematic type based on name
def identify_systematic_type(syst_name):
	"""Identify if systematic is flux, xsec, or reinteraction based on name"""
	syst_lower = syst_name.lower()
	
	# Flux keywords
	flux_keywords = ['flux', 'horn', 'beam', 'kminus', 'kplus', 'kzero', 
					 'piminus', 'piplus', 'nucleon', 'expskin']
	
	# Reinteraction keywords
	reint_keywords = ['reint', 'fsi', 'absorption', 'charge_exchange', 
					 'elastic', 'inelastic', 'pion_prod', 'geant4']
	
	# Check flux first
	for keyword in flux_keywords:
		if keyword in syst_lower:
			return 'flux'
	
	# Check reinteraction
	for keyword in reint_keywords:
		if keyword in syst_lower:
			return 'reint'
	
	# Default to cross section
	return 'xsec'

## Cross Section & Flux Uncertainties
# xsecflux_variables = ['visible_energy', 'reco_neutrino_energy', 'reco_muon_energy', 'reco_cos_theta']

# Map neutrino type to the sample name in the xsecflux file
if run_num == 1:
	xsecflux_sample_map = {
		'numu': 'run1_bnb_nu_overlay_mcc9_v28_wctagger',
		'nue': 'run1_bnb_nue_overlay_mcc9_v28_wctagger'
	}
elif run_num == 3:
	xsecflux_sample_map = {
		'numu': 'run3b_nu',
		'nue': 'run3b_nue'
	}


if run_num in [1,3]:
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
	flux_params = []  # No flux systematics in run4b

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

	all_pars = flux_params + genie_params + other_xsec

def make_hist_w_errors(rfile, varname, sample, parlist):
	"""Load histograms and separate into flux, xsec, and reinteraction"""
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
		
		# Debug: Print categorization for first few parameters
		if len(hists) <= 5:
			print(f"    {parname} → {syst_type}")
		
		# Add variance to appropriate category
		for ibin in range(0, hvar_tot.GetXaxis().GetNbins()+1):
			xvar = hvar.GetBinContent(ibin)
			xmean = hmean.GetBinContent(ibin)
			
			# if xmean > 0:
			# 	xfracvar = xvar/xmean
			# else:
			# 	xfracvar = 0.0

			# cv_var = xfracvar * hcv.GetBinContent(ibin)

			if xmean > 0:
				# xfracvar = xvar/xmean
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
	print(f"  Systematic breakdown: {n_flux} flux, {n_xsec} xsec, {n_reint} reint (total {len(parlist)})")
	
	hists['cv'] = hcv
	hists['mean2'] = hmeans2
	hists['totvar'] = hvar_tot
	hists['fluxvar'] = hvar_flux
	hists['xsecvar'] = hvar_xsec
	hists['reintvar'] = hvar_reint
	
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
		'legend': 'Run1 Data'
	}
}

if not show_data: 
	del categories['data']

legend_POT_string = " Events Per "+str(targetpot)+" POT"

# Define variables to plot - for muon neutrino analysis
variables = {
	'neutrino_energy': {
		'var': 'numuIncCC_reco_nu_energy',
		'nbins': 20,
		'xmin': 0.0,
		'xmax': 2.0,
		'title': plot_title+'; Reconstructed Neutrino Energy (GeV); '+legend_POT_string,
		'cut_suffix': '',
		'has_overflow': True
	},
	'muon_momentum': {
		'var': 'numuIncCC_reco_muon_momentum',
		'nbins': 25,
		'xmin': 0.0,
		'xmax': 1.5,
		'title': plot_title+'; Reconstructed Muon Momentum (GeV); '+legend_POT_string,
		'cut_suffix': '&& (numuIncCC_reco_muon_momentum>0)'
	},
	'muon_costheta': {
		'var': 'numuIncCC_reco_muon_costheta',
		'nbins': 20,
		'xmin': -1.0,
		'xmax': 1.0,
		'title': plot_title+'; Reconstructed Muon cos(#theta); '+legend_POT_string,
		'cut_suffix': '&& (numuIncCC_reco_muon_costheta>-900)'
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
			
			# Debug: Print cut for cc_numu to verify it includes numuIncCC_passes_all_cuts
			if cat_name == 'cc_numu':
				print(f"\nDEBUG - CC numu full cut string:")
				print(f"  {full_cut}")
			
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
	
	if h_total_mc is not None:
		h_uncertainty_total = h_total_mc.Clone(f"h_uncertainty_total_{var_name}")
		h_uncertainty_flux = h_total_mc.Clone(f"h_uncertainty_flux_{var_name}")
		h_uncertainty_xsec = h_total_mc.Clone(f"h_uncertainty_xsec_{var_name}")
		h_uncertainty_reint = h_total_mc.Clone(f"h_uncertainty_reint_{var_name}")
		
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
				continue
			
			# Initialize fractional variances
			frac_var_flux = 0.0
			frac_var_xsec = 0.0
			frac_var_reint = 0.0
			
			# Get fractional variances from each neutrino sample
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
								# Debug: print flux variance for first bin
								if ibin == 1 and abs_var_flux > 0:
									print(f"  DEBUG: {xsample_name} bin {ibin}: abs_var_flux={abs_var_flux:.4e}, cv={cv_from_xsecflux:.4e}, frac_var_flux={frac_var_flux:.4e}")
							if 'xsecvar' in xsec_hists:
								abs_var_xsec = xsec_hists['xsecvar'].GetBinContent(ibin)
								frac_var_xsec += abs_var_xsec / (cv_from_xsecflux ** 2)
							if 'reintvar' in xsec_hists:
								abs_var_reint = xsec_hists['reintvar'].GetBinContent(ibin)
								frac_var_reint += abs_var_reint / (cv_from_xsecflux ** 2)
				except (AttributeError, ReferenceError):
					continue
			
			# Statistical fractional uncertainty: 1/sqrt(n_unscaled)
			n_unscaled = h_total_mc_unscaled.GetBinContent(ibin)
			frac_var_stat = (1.0 / n_unscaled) if n_unscaled > 0 else 0.0
			
			# Debug: Print variance breakdown for bin 1
			if ibin == 1 and central > 0:
				print(f"\n  DEBUG Variance Breakdown for bin {ibin}:")
				print(f"    frac_var_stat:  {frac_var_stat:.6e}")
				print(f"    frac_var_flux:  {frac_var_flux:.6e}")
				print(f"    frac_var_xsec:  {frac_var_xsec:.6e}")
				print(f"    frac_var_reint: {frac_var_reint:.6e}")
			
			# Total fractional variance (add in quadrature)
			frac_var_total = frac_var_stat + frac_var_flux + frac_var_xsec + frac_var_reint
			
			# Convert fractional variances to absolute errors
			abs_error_stat = central * sqrt(frac_var_stat)
			abs_error_flux = central * sqrt(frac_var_flux)
			abs_error_xsec = central * sqrt(frac_var_xsec)
			abs_error_reint = central * sqrt(frac_var_reint)
			abs_error_total = central * sqrt(frac_var_total)
			
			# Set bin errors
			h_uncertainty_total.SetBinError(ibin, abs_error_total)
			h_uncertainty_flux.SetBinError(ibin, abs_error_flux)
			h_uncertainty_xsec.SetBinError(ibin, abs_error_xsec)
			h_uncertainty_reint.SetBinError(ibin, abs_error_reint)
		
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
	
	# Add overflow text for neutrino energy plot
	if var_name == 'neutrino_energy' and var_info.get('has_overflow', False):
		# overflow_text = rt.TText()
		# overflow_text.SetTextSize(0.03)
		# overflow_text.SetTextAlign(22)
		# overflow_text.SetTextColor(rt.kBlack)
		
		hist_for_axis = hstack if hstack.GetHists() else hists['data']
		last_bin = hist_for_axis.GetXaxis().GetNbins()
		x_pos = hist_for_axis.GetXaxis().GetBinCenter(last_bin)
		y_pos = -0.8
		
		# overflow_text.DrawText(x_pos, y_pos, "overflow")

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
	h_frac_total = None
	
	if h_total_mc is not None and h_uncertainty_total is not None:
		h_frac_stat = h_total_mc.Clone(f"h_frac_stat_{var_name}")
		h_frac_flux = h_total_mc.Clone(f"h_frac_flux_{var_name}")
		h_frac_xsec = h_total_mc.Clone(f"h_frac_xsec_{var_name}")
		h_frac_reint = h_total_mc.Clone(f"h_frac_reint_{var_name}")
		h_frac_total = h_total_mc.Clone(f"h_frac_total_{var_name}")
		
		h_frac_stat.Reset()
		h_frac_flux.Reset()
		h_frac_xsec.Reset()
		h_frac_reint.Reset()
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
				
				# Total uncertainty (quadrature sum)
				total_frac = sqrt(stat_frac**2 + flux_frac**2 + xsec_frac**2 + reint_frac**2)
				
				# Fill fractional error histograms
				h_frac_stat.SetBinContent(ibin, stat_frac)
				h_frac_flux.SetBinContent(ibin, flux_frac)
				h_frac_xsec.SetBinContent(ibin, xsec_frac)
				h_frac_reint.SetBinContent(ibin, reint_frac)
				h_frac_total.SetBinContent(ibin, total_frac)
		
		# Debug: Print max fractional uncertainties
		print(f"\n  Fractional Uncertainty Summary for {var_name}:")
		print(f"    Max stat:   {h_frac_stat.GetMaximum():.4f}")
		print(f"    Max flux:   {h_frac_flux.GetMaximum():.4f}")
		print(f"    Max xsec:   {h_frac_xsec.GetMaximum():.4f}")
		print(f"    Max reint:  {h_frac_reint.GetMaximum():.4f}")
		print(f"    Max total:  {h_frac_total.GetMaximum():.4f}")
		
		# Verify no stacking - check a few bins
		print(f"\n  Bin-by-bin check (first 3 bins with events):")
		bins_checked = 0
		for ibin in range(1, h_frac_total.GetNbinsX() + 1):
			if h_total_mc.GetBinContent(ibin) > 0 and bins_checked < 3:
				stat = h_frac_stat.GetBinContent(ibin)
				flux = h_frac_flux.GetBinContent(ibin)
				xsec = h_frac_xsec.GetBinContent(ibin)
				reint = h_frac_reint.GetBinContent(ibin)
				total = h_frac_total.GetBinContent(ibin)
				sum_quad = sqrt(stat**2 + flux**2 + xsec**2 + reint**2)
				print(f"    Bin {ibin}: stat={stat:.4f}, flux={flux:.4f}, xsec={xsec:.4f}, reint={reint:.4f}")
				print(f"            total={total:.4f}, sqrt(sum^2)={sum_quad:.4f} (should match)")
				bins_checked += 1
		
		# Set line styles (no filling, lines only)
		h_frac_stat.SetLineColor(rt.kGray+2)
		h_frac_stat.SetLineWidth(2)
		h_frac_stat.SetLineStyle(1)
		h_frac_stat.SetFillStyle(0)
		h_frac_stat.SetMarkerSize(0)
		
		h_frac_flux.SetLineColor(rt.kRed)
		h_frac_flux.SetLineWidth(2)
		h_frac_flux.SetLineStyle(1)
		h_frac_flux.SetFillStyle(0)
		h_frac_flux.SetMarkerSize(0)
		
		h_frac_xsec.SetLineColor(rt.kBlue)
		h_frac_xsec.SetLineWidth(2)
		h_frac_xsec.SetLineStyle(1)
		h_frac_xsec.SetFillStyle(0)
		h_frac_xsec.SetMarkerSize(0)
		
		h_frac_reint.SetLineColor(rt.kOrange+7)
		h_frac_reint.SetLineWidth(2)
		h_frac_reint.SetLineStyle(1)
		h_frac_reint.SetFillStyle(0)
		h_frac_reint.SetMarkerSize(0)
		
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
					  h_frac_total.GetMaximum())
		h_frac_total.SetMaximum(max_val * 1.2)
		h_frac_total.SetMinimum(0.0)  # Start at 0
		
		# Draw total first to set up axes
		h_frac_total.Draw("hist")
		h_frac_stat.Draw("hist same")
		h_frac_flux.Draw("hist same")
		h_frac_xsec.Draw("hist same")
		h_frac_reint.Draw("hist same")
		
		# Set axis properties
		h_frac_total.GetXaxis().SetLabelSize(0.04)
		h_frac_total.GetXaxis().SetTitleSize(0.04)
		h_frac_total.GetYaxis().SetLabelSize(0.04)
		h_frac_total.GetYaxis().SetTitleSize(0.04)
		h_frac_total.GetYaxis().SetTitle("Fractional Uncertainty")
		
		# Add legend for fractional plot
		leg_frac = rt.TLegend(0.15, 0.65, 0.40, 0.88)
		leg_frac.SetTextSize(0.035)
		leg_frac.SetFillStyle(0)
		leg_frac.SetBorderSize(1)
		leg_frac.AddEntry(h_frac_total, "Total", "l")
		leg_frac.AddEntry(h_frac_stat, "Statistical", "l")
		leg_frac.AddEntry(h_frac_flux, "Flux", "l")
		leg_frac.AddEntry(h_frac_xsec, "Cross Section", "l")
		leg_frac.AddEntry(h_frac_reint, "Reinteraction", "l")
		# leg_frac.AddEntry(h_frac_total, "Total", "l")
		leg_frac.Draw()
		
		# canvas_frac.SetGridy(1)  # Removed horizontal grid lines
		canvas_frac.Update()
		canvas_frac.RedrawAxis()
		
		out.cd()
		canvas_frac.Write()
		
		print(f"  Fractional error plot saved for {var_name}")

	# Print summary
	print(f"\n=== {var_name.upper()} Analysis Summary ===")
	total_mc = sum(total_events[cat] for cat in total_events if cat != 'data')
	print(f"Total MC: {total_mc:.1f}")
	if 'data' in total_events:
		print(f"Data: {total_events['data']:.1f}")
		if total_mc > 0:
			print(f"Data/MC ratio: {total_events['data']/total_mc:.2f}")

	# CC Î½Î¼ purity
	cc_numu_events = total_events.get('cc_numu', 0)
	if total_mc > 0:
		print(f"CC Î½Î¼ purity: {cc_numu_events/total_mc*100:.1f}%")
	
	# Background breakdown
	cosmic_events = total_events.get('cosmic', 0)
	cc_nue_events = total_events.get('cc_nue', 0)
	nc_events = total_events.get('nc_nue', 0) + total_events.get('nc_numu', 0)
	
	if total_mc > 0:
		print(f"Cosmic background: {cosmic_events/total_mc*100:.1f}%")
		print(f"Î½e CC background: {cc_nue_events/total_mc*100:.1f}%") 
		print(f"NC background: {nc_events/total_mc*100:.1f}%")

	print(f"Plot saved for {var_name}")

print("\nSaved to", out_name)
out.Close()