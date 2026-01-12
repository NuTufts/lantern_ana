import os,sys
import ROOT as rt
import array
from math import sqrt



run_num = 4  # Changed to 4 to use Run 4b settings

lantern_dir = "/exp/uboone/app/users/imani/lantern_ana/"

## Run 1 
if run_num == 1: 
	targetpot = 4.4e19
	scaling = {"numu":targetpot/4.675690535431973e+20,
			"nue":targetpot/9.662529168587103e+22,
			"extbnb":(176153.0)/(433446.0),
			"data":1.0}
	files = {"numu": f"{lantern_dir}/zev_mmr/mmr_outputs/run1_bnb_nu_overlay_mcc9_v28_wctagger.root",
			"nue":f"{lantern_dir}/zev_mmr/mmr_outputs/run1_bnb_nue_overlay_mcc9_v28_wctagger.root", 
			"extbnb":f"{lantern_dir}/zev_mmr/mmr_outputs/run1_extbnb_mcc9_v29e_C1.root",
			"data":f"{lantern_dir}/zev_mmr/mmr_outputs/run1_bnb5e19.root"}
	xsecflux_files = {
		"nue": f"{lantern_dir}/studies/xsecfluxsys/run1_outputs/xsecflux_run1_nue_intrinsic_nue.root",
		"numu": f"{lantern_dir}/studies/xsecfluxsys/run1_outputs/xsecflux_run1_nue_overlay_nu.root"
	}
	show_data = True 
	plot_title = "Run 1"

	# plot_title = "Run1: Inclusive CC #nu_{e} Selection"
	out_name = f"{lantern_dir}/zev_mmr/hists_xsecflux/nue_hists1.root"


## Run 4b (Updated to match plot_runs4b_v3.py) 
if run_num == 4: 
	# Base paths matching plot_runs4b_v3.py
	analysis_base = "/exp/uboone/app/users/imani/lantern_ana/runs45_zev_mmr/nue_raw_root/"
	covar_base = "/exp/uboone/app/users/imani/lantern_ana/studies/xsecfluxsys/"
	
	# POT information from plot_runs4b_v3.py
	pot_run4b = 4.498e+19
	mc_pot_nu = 2.3593114985024402e+20
	mc_pot_nue = 2.3593114985024402e+20
	mc_pot_dirt = 1.088128052604017e+20
	end1cnt_run4b = 10928307.0
	ext_beamoff = 29875806.0
	
	targetpot = 1.45e+20
	scaling = {
		"numu": pot_run4b / mc_pot_nu,
		"nue": pot_run4b / mc_pot_nue,
		"extbnb": end1cnt_run4b / ext_beamoff,
		"data": 1.0
	}
	
	# File paths matching plot_runs4b_v3.py
	files = {
		"numu": analysis_base + "run4b_v10_04_07_20_BNB_nu_overlay_retuple.root",
		"nue": analysis_base + "run4b_v10_04_07_09_BNB_nue_overlay_surprise.root", 
		"extbnb": analysis_base + "run4b_extbnb.root",
		"data": analysis_base + "run4b_beamon.root"
	}
	
	# Updated xsecflux file paths matching plot_runs4b_v3.py
	xsecflux_files = {
		"nue": covar_base + "xsecflux_run4b_nue.root",
		"numu": covar_base + "xsecflux_run4b_nu.root"
	}
	
	show_data = True 
	plot_title = "Run 4b"
	out_name = analysis_base + "nue_hists_run4b_xsecflux.root"
	
## Cross Section & Flux Uncertainties
xsecflux_variables = ['visible_energy', 'electron_momentum', 'electron_angle']

# Map neutrino type to the sample name in the xsecflux file
# Updated to match the dataset names in the covariance files
xsecflux_sample_map = {
	'numu': 'run4b_nu',  # Updated from run1 to run4b
	'nue': 'run4b_nue'   # Updated from run1 to run4b
}

# Map plotting variable names to xsecflux variable names
var_name_map = {
	'neutrino_energy': 'visible_energy',
	'electron_momentum': 'electron_momentum',
	'electron_costheta': 'electron_angle'
}
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


def make_hist_w_errors( rfile, varname, sample, parlist ):
	hists = {}
	hcv_name = f"h{varname}_{sample}_cv"
	hcv = rfile.Get(hcv_name)
	hvar_tot = hcv.Clone(f"h{varname}__{sample}_totvariance")
	hvar_tot.Reset()
	hmeans2 = hcv.Clone(f"h{varname}__{sample}_meanofmeans")
	hmeans2.Reset()
	for parname in parlist:
		hname_mean = f"h{varname}__{sample}__{parname}_mean"
		hname_var  = f"h{varname}__{sample}__{parname}_variance"
		hmean = rfile.Get(hname_mean)
		hvar  = rfile.Get(hname_var)
		hists[parname] = hvar
		for ibin in range(0,hvar_tot.GetXaxis().GetNbins()+1):
			xvar  = hvar.GetBinContent(ibin)
			xmean = hmean.GetBinContent(ibin)

			if xmean>0:
				xfracvar = xvar/xmean
			else:
				xfracvar = 0.0

			cv_var = xfracvar*hcv.GetBinContent(ibin)

			xvar_tot  = hvar_tot.GetBinContent(ibin)
			hvar_tot.SetBinContent(ibin, xvar_tot+cv_var ) # add variances
			xmean2 = hmeans2.GetBinContent(ibin)
			hmeans2.SetBinContent(ibin, xmean2 + xmean/len(parlist) )
	# set std for CV error
	for ibin in range(0,hvar_tot.GetXaxis().GetNbins()+1):
		stddev = sqrt(hvar_tot.GetBinContent(ibin))
		hcv.SetBinError(ibin,stddev)
	hists['cv'] = hcv
	hists['mean2'] = hmeans2
	hists['totvar'] = hvar_tot
	return hists


rt.gStyle.SetOptStat(0)

tfiles = {}
trees = {}

samples = ['nue','numu','extbnb','data']

for sample in samples:
	tfiles[sample] = rt.TFile( files[sample] )
	trees[sample] = tfiles[sample].Get("analysis_tree")
	nentries = trees[sample].GetEntries()
	print(f"sample={sample} has {nentries} entries")

## Output file (must be set after loading samples)
out = rt.TFile(out_name,"recreate")

# Alternative: use the combined cut from the producer
base_cut = f"(nueIncCC_passes_all_cuts==1)"

# Define sample categories with requested colors - updated for electron neutrino analysis
categories = {
	'cosmic': {
		'samples': ['extbnb'],
		'truth_cut': f' ',  # No truth cut for cosmic background
		'color': rt.kGray+2,  # Dark gray
		'fill_style': 1001,   # Solid fill
		'legend': 'Cosmic bkgd'
	},
	'nc_nue': {
		'samples': ['nue'],
		'truth_cut': f' && (nueIncCC_is_neutral_current==1)',
		'color': rt.kGreen+1,    
		'fill_style': 1001,   # Solid fill
		'legend': 'NC #nu_{e}'
	},
	'cc_nue': {
		'samples': ['nue'], 
		'truth_cut': f' && (nueIncCC_is_charge_current==1)',
		'color': rt.kRed,     # Red
		'fill_style': 1001,   # Solid fill
		'legend': 'CC #nu_{e}'
	},
	'nc_numu': {
		'samples': ['numu'],
		'truth_cut': f' && (nueIncCC_is_neutral_current==1)', 
		'color': rt.kGray, # Green
		'fill_style': 1001,   # Solid fill
		'legend': 'NC #nu_{#mu}'
	},
	'cc_numu': {
		'samples': ['numu'],
		'truth_cut': f' && (nueIncCC_is_charge_current==1)',
		'color': rt.kBlue,    # Blue
		'fill_style': 1001,   # Solid fill
		'legend': 'CC #nu_{#mu}'
	},
		'data': {
		'samples': ['data'],
		'truth_cut': '',  # No truth cut for data
		'color': rt.kBlack,   # Black line
		'legend': 'Data'
	}
}

if not show_data: 
	del categories['data']

legend_POT_string = " Events Per "+str(targetpot)+" POT"

# Define variables to plot - updated for electron neutrino analysis
variables = {
	'neutrino_energy': {
		'var': 'nueIncCC_reco_nu_energy',
		'nbins': 30,
		'xmin': 0.0,
		'xmax': 3.0,
		'title': plot_title+'; Reconstructed Neutrino Energy (GeV); '+legend_POT_string,
		'cut_suffix': '',  # No additional cut
		'y_max': 30,  # Set fixed y-axis maximum
		'rebin_config': {
			'type': 'variable',
			'bins': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0],  # 0-2 GeV in 0.2 GeV bins
			'overflow': True  # Last bin is overflow
		}
	},
	'electron_momentum': {
		'var': 'nueIncCC_reco_electron_momentum',
		'nbins': 25,
		'xmin': 0.0,
		'xmax': 1.5,
		'title': plot_title+'; Reconstructed Electron Momentum (GeV); '+legend_POT_string,
		'cut_suffix': '&& (nueIncCC_reco_electron_momentum>0)',  # Valid momentum only
		'rebin_config': {
			'type': 'constant',
			'factor': 2,
			'overflow': True  # Last bin is overflow
		}
	},
	'electron_costheta': {
		'var': 'nueIncCC_reco_electron_costheta',
		'nbins': 20,
		'xmin': -1.0,
		'xmax': 1.0,
		'title': plot_title+'; Reconstructed Electron cos#theta; '+legend_POT_string,
		'cut_suffix': '&& (nueIncCC_reco_electron_costheta>-999)',  # Valid angle
		'rebin_config': {
			'type': 'range',
			'xmin': 0.0,
			'xmax': 1.0,
			'underflow': True,  # Add underflow to first bin
			'overflow': False   # Don't add overflow
		}
	}
}

print("\n=== LOADING XSECFLUX UNCERTAINTIES ===")
xsecflux_hists = {}

for xsample_name in ['nue', 'numu']:
	xsecflux_hists[xsample_name] = {}
	xfile_path = xsecflux_files[xsample_name]
	
	if not os.path.exists(xfile_path):
		print(f"WARNING: Cannot find xsecflux file: {xfile_path}")
		continue
	
	print(f"\nLoading uncertainties for {xsample_name} from {xfile_path}")
	xfile = rt.TFile.Open(xfile_path, "READ")
	
	if not xfile or xfile.IsZombie():
		print(f"ERROR: Cannot open {xfile_path}")
		continue
	
	# Get the dataset name for this sample
	dataset_name = xsecflux_sample_map[xsample_name]
	
	for xvar in xsecflux_variables:
		print(f"  Loading histograms for variable: {xvar}, dataset: {dataset_name}")
		try:
			xsecflux_hists[xsample_name][xvar] = make_hist_w_errors(
				xfile, xvar, dataset_name, all_pars
			)
			print(f"    Successfully loaded {len(xsecflux_hists[xsample_name][xvar])} histograms")
		except Exception as e:
			print(f"    ERROR loading {xvar}: {e}")
			xsecflux_hists[xsample_name][xvar] = None

print("\n=== XSECFLUX LOADING COMPLETE ===\n")

# Store order of categories for stacking
stack_order = ['cosmic', 'nc_numu', 'cc_numu', 'nc_nue', 'cc_nue']

# Create canvas with appropriate size
canvas = rt.TCanvas("c1", "c1", 800, 600)
canvas.SetLeftMargin(0.12)
canvas.SetRightMargin(0.05)

# Process each variable
for var_name, var_info in variables.items():
	print(f"\nProcessing variable: {var_name}")
	
	# Storage for histograms and totals
	hists = {}
	total_events = {}
	h_total_mc = None  # Will be the sum of all MC categories
	
	# Process each category
	for cat_name, cat_info in categories.items():
		if cat_name not in stack_order and cat_name != 'data':
			continue
			
		print(f"  Processing category: {cat_name}")
		
		# Create histogram for this category
		h_cat = rt.TH1D(f"h_{var_name}_{cat_name}", var_info['title'],
						var_info['nbins'], var_info['xmin'], var_info['xmax'])
		h_cat.Sumw2()
		
		# Get the tree-level cuts for this variable and category
		var_cut = base_cut
		if var_info.get('cut_suffix'):
			var_cut += var_info['cut_suffix']
		
		truth_cut = cat_info.get('truth_cut', '')
		full_cut = var_cut + truth_cut
		
		# Loop through samples for this category and fill histogram
		cat_total = 0.0
		for sample_name in cat_info['samples']:
			tree = trees[sample_name]
			
			# Create temporary histogram for this sample
			h_temp = rt.TH1D(f"h_temp_{var_name}_{cat_name}_{sample_name}", "",
							var_info['nbins'], var_info['xmin'], var_info['xmax'])
			h_temp.Sumw2()
			
			# Fill histogram - for data use no weight, for MC use eventweight
			if sample_name == 'data':
				draw_string = f"{var_info['var']}>>h_temp_{var_name}_{cat_name}_{sample_name}"
				tree.Draw(draw_string, full_cut, "goff")
			else:
				draw_string = f"{var_info['var']}>>h_temp_{var_name}_{cat_name}_{sample_name}"
				weight_string = f"({full_cut})*eventweight_weight"
				tree.Draw(draw_string, weight_string, "goff")
			
			# Scale by POT if not data
			if sample_name != 'data':
				h_temp.Scale(scaling[sample_name])
			
			# Add to category histogram
			h_cat.Add(h_temp)
			
			sample_integral = h_temp.Integral()
			cat_total += sample_integral
			
			h_temp.Delete()
		
		# Store category histogram
		hists[cat_name] = h_cat
		total_events[cat_name] = cat_total
		
		# Set histogram style
		h_cat.SetFillColor(cat_info['color'])
		h_cat.SetLineColor(rt.kBlack)
		h_cat.SetLineWidth(1)
		
		if cat_name == 'data':
			h_cat.SetMarkerStyle(20)
			h_cat.SetMarkerSize(0.8)
			h_cat.SetLineWidth(2)
		else:
			h_cat.SetFillStyle(cat_info['fill_style'])
		
		# Add to total MC if not data
		if cat_name != 'data':
			if h_total_mc is None:
				h_total_mc = h_cat.Clone(f"h_total_mc_{var_name}")
			else:
				h_total_mc.Add(h_cat)
		
		print(f"    {cat_name}: {cat_total:.2f} events")
	
	# Create stack in the correct order (bottom to top)
	hstack = rt.THStack(f"hs_{var_name}", "")
	for cat_name in stack_order:
		if cat_name in hists:
			hstack.Add(hists[cat_name])
	
	# Apply rebinning if configured
	if 'rebin_config' in var_info:
		rebin_config = var_info['rebin_config']
		rebin_type = rebin_config.get('type', 'constant')
		
		print(f"  Applying rebinning: {rebin_type}")
		
		if rebin_type == 'constant':
			# Simple constant rebinning
			factor = rebin_config.get('factor', 1)
			for cat_name in hists:
				hists[cat_name].Rebin(factor)
			if h_total_mc is not None:
				h_total_mc.Rebin(factor)
		
		elif rebin_type == 'variable':
			# Variable width binning
			bins_array = array.array('d', rebin_config['bins'])
			for cat_name in hists:
				h = hists[cat_name]
				h_rebinned = h.Rebin(len(bins_array)-1, f"{h.GetName()}_rebinned", bins_array)
				hists[cat_name] = h_rebinned
			
			if h_total_mc is not None:
				h_total_mc = h_total_mc.Rebin(len(bins_array)-1, f"h_total_mc_{var_name}_rebinned", bins_array)
			
			# Handle overflow if specified
			if rebin_config.get('overflow', False):
				# For each histogram, add all overflow bins to the last bin
				for cat_name in hists:
					h = hists[cat_name]
					nbins = h.GetNbinsX()
					last_bin_content = h.GetBinContent(nbins)
					last_bin_error_sq = h.GetBinError(nbins)**2
					
					# Sum all overflow bins
					overflow_content = 0.0
					overflow_error_sq = 0.0
					for ibin in range(nbins+1, h.GetNbinsX() + 1): #100
						overflow_content += h.GetBinContent(ibin)
						overflow_error_sq += h.GetBinError(ibin)**2
					
					h.SetBinContent(nbins, last_bin_content + overflow_content)
					h.SetBinError(nbins, sqrt(last_bin_error_sq + overflow_error_sq))
					# Clear overflow bins
					for ibin in range(nbins+1, h.GetNbinsX() + 100):
						h.SetBinContent(ibin, 0)
						h.SetBinError(ibin, 0)
				
				if h_total_mc is not None:
					nbins = h_total_mc.GetNbinsX()
					last_bin_content = h_total_mc.GetBinContent(nbins)
					last_bin_error_sq = h_total_mc.GetBinError(nbins)**2
					
					overflow_content = 0.0
					overflow_error_sq = 0.0
					for ibin in range(nbins+1, h_total_mc.GetNbinsX() + 100):
						overflow_content += h_total_mc.GetBinContent(ibin)
						overflow_error_sq += h_total_mc.GetBinError(ibin)**2
					
					h_total_mc.SetBinContent(nbins, last_bin_content + overflow_content)
					h_total_mc.SetBinError(nbins, sqrt(last_bin_error_sq + overflow_error_sq))
					for ibin in range(nbins+1, h_total_mc.GetNbinsX() + 100):
						h_total_mc.SetBinContent(ibin, 0)
						h_total_mc.SetBinError(ibin, 0)
		
		elif rebin_type == 'range':
			# Range restriction (for electron_costheta: 0-1)
			xmin = rebin_config.get('xmin', 0.0)
			xmax = rebin_config.get('xmax', 1.0)
			
			# Find bin numbers for the range
			for cat_name in hists:
				h = hists[cat_name]
				bin_min = h.GetXaxis().FindBin(xmin)
				bin_max = h.GetXaxis().FindBin(xmax - 0.0001)  # Slightly less to ensure we're in the right bin
				
				# Add underflow to first bin if specified - sum all bins below the range
				if rebin_config.get('underflow', False):
					first_bin_content = h.GetBinContent(bin_min)
					first_bin_error_sq = h.GetBinError(bin_min)**2
					
					# Sum all underflow bins (everything before bin_min)
					underflow_content = 0.0
					underflow_error_sq = 0.0
					print("MINDBIN", bin_min)
					for ibin in range(0, bin_min):
						underflow_content += h.GetBinContent(ibin)
						underflow_error_sq += h.GetBinError(ibin)**2
					
					h.SetBinContent(bin_min, first_bin_content + underflow_content)
					h.SetBinError(bin_min, sqrt(first_bin_error_sq + underflow_error_sq))
					# Clear underflow bins
					for ibin in range(0, bin_min):
						h.SetBinContent(ibin, 0)
						h.SetBinError(ibin, 0)
			
			if h_total_mc is not None and rebin_config.get('underflow', False):
				bin_min = h_total_mc.GetXaxis().FindBin(xmin)
				first_bin_content = h_total_mc.GetBinContent(bin_min)
				first_bin_error_sq = h_total_mc.GetBinError(bin_min)**2
				
				underflow_content = 0.0
				underflow_error_sq = 0.0
				for ibin in range(0, bin_min):
					underflow_content += h_total_mc.GetBinContent(ibin)
					underflow_error_sq += h_total_mc.GetBinError(ibin)**2
				
				h_total_mc.SetBinContent(bin_min, first_bin_content + underflow_content)
				h_total_mc.SetBinError(bin_min, sqrt(first_bin_error_sq + underflow_error_sq))
				for ibin in range(0, bin_min):
					h_total_mc.SetBinContent(ibin, 0)
					h_total_mc.SetBinError(ibin, 0)
		
		# Rebuild the stack with rebinned histograms
		hstack = rt.THStack(f"hs_{var_name}", "")
		for cat_name in stack_order:
			if cat_name in hists and cat_name != 'data':
				hstack.Add(hists[cat_name])

	# Create uncertainty histogram using xsecflux uncertainties
	h_uncertainty = None
	if h_total_mc is not None:
		h_uncertainty = h_total_mc.Clone(f"h_uncertainty_{var_name}")
		
		# Map the plotting variable name to the xsecflux variable name
		xsecflux_var = var_name_map.get(var_name, var_name)
		
		# Apply xsecflux uncertainties to the total MC histogram
		# Combine uncertainties from nue and numu samples in quadrature
		for ibin in range(0, h_uncertainty.GetNbinsX() + 2):  # Include overflow (nbins+1)
			total_variance = 0.0
			
			# Get variance contributions from each neutrino sample
			for xsample_name in ['nue', 'numu']:
				try:
					if xsample_name in xsecflux_hists and xsecflux_var in xsecflux_hists[xsample_name]:
						xsec_hists = xsecflux_hists[xsample_name][xsecflux_var]
						
						# Get the total variance histogram
						if 'totvar' in xsec_hists:
							hvar = xsec_hists['totvar']
							hcv = xsec_hists['cv']
							
							# Get variance and scale it to match our POT scaling
							variance_from_xsec = hvar.GetBinContent(ibin)
							cv_from_xsec = hcv.GetBinContent(ibin)
							
							# Scale the variance by our POT scaling factor
							scaled_variance = variance_from_xsec #* (scaling[xsample_name]**2)
							total_variance += scaled_variance
				except (AttributeError, ReferenceError):
					# Skip this sample if histogram is null or doesn't exist
					continue
			
			# Set the bin error as sqrt of total variance
			h_uncertainty.SetBinError(ibin, sqrt(total_variance))
		
		# Set style for uncertainty band
		h_uncertainty.SetFillColor(rt.kGray+1)
		h_uncertainty.SetFillStyle(3002)  # Hatched pattern
		h_uncertainty.SetLineColor(rt.kGray+1)
		h_uncertainty.SetLineWidth(1)
		h_uncertainty.SetMarkerSize(0)

	# Draw histograms
	stack_max = hstack.GetMaximum() if hstack.GetHists() else 0
	data_max = hists['data'].GetMaximum() if 'data' in hists else 0

	# Set y-axis maximum - use fixed value for neutrino energy, calculated for others
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

	# Draw uncertainty histogram on top of stack (but below data)
	if h_uncertainty is not None:
		h_uncertainty.Draw("E2same")

	# Draw data on top as black line
	if 'data' in hists:
		hists['data'].Draw("E1same")
	
	# Set x-axis range for cos theta plot to show only 0 to 1
	if var_name == 'electron_costheta':
		if hstack.GetHists():
			hstack.GetXaxis().SetRangeUser(0.0, 1.0)
		else:
			hists['data'].GetXaxis().SetRangeUser(0.0, 1.0)

	# Add overflow text for neutrino energy plot
	if var_name == 'neutrino_energy' and var_info.get('has_overflow', False):
		# Create text object for overflow label
		overflow_text = rt.TText()
		overflow_text.SetTextSize(0.03)
		overflow_text.SetTextAlign(22)  # Center alignment
		overflow_text.SetTextColor(rt.kBlack)
		
		# Position the text below the last bin - center it in the bin
		hist_for_axis = hstack if hstack.GetHists() else hists['data']
		last_bin = hist_for_axis.GetXaxis().GetNbins()
		x_pos = hist_for_axis.GetXaxis().GetBinCenter(last_bin)
		y_pos = -0.8  # Position below x-axis
		
		overflow_text.DrawText(x_pos, y_pos, "overflow")
		
		# Center the x-axis title
		if hstack.GetHists():
			hist.GetXaxis().CenterTitle()
		else:
			hists['data'].GetXaxis().CenterTitle()

	# Create and configure legend
	legend = rt.TLegend(0.65, 0.50, 0.89, 0.89)
	legend.SetTextSize(0.03)
	legend.SetFillStyle(0)  # Transparent background
	legend.SetBorderSize(1)

	# Add entries to legend in the specified order
	for cat_name in stack_order:
		if cat_name in hists and cat_name in categories:
			legend.AddEntry(hists[cat_name], categories[cat_name]['legend'], "f")

	# Add data to legend
	if 'data' in hists:
		legend.AddEntry(hists['data'], categories['data']['legend'], "lep")

	# Add uncertainty to legend
	if h_uncertainty is not None:
		legend.AddEntry(h_uncertainty, "xsec flux sys.", "f")

	legend.Draw()

	# Update canvas
	canvas.SetLogy(0)  # Linear scale
	canvas.Update()

	# Save canvas to ROOT file (only canvas, not individual histograms)
	out.cd()
	canvas.Write()

	# Print summary for this variable
	print(f"\n=== {var_name.upper()} Analysis Summary ===")
	total_mc = sum(total_events[cat] for cat in total_events if cat != 'data')
	print(f"Total MC: {total_mc:.1f}")
	if 'data' in total_events:
		print(f"Data: {total_events['data']:.1f}")
		if total_mc > 0:
			print(f"Data/MC ratio: {total_events['data']/total_mc:.2f}")

	# CC νe purity and efficiency
	cc_nue_events = total_events.get('cc_nue', 0)
	if total_mc > 0:
		print(f"CC νe purity: {cc_nue_events/total_mc*100:.1f}%")
	
	# Background breakdown
	cosmic_events = total_events.get('cosmic', 0)
	cc_numu_events = total_events.get('cc_numu', 0)
	nc_events = total_events.get('nc_nue', 0) + total_events.get('nc_numu', 0)
	
	if total_mc > 0:
		print(f"Cosmic background: {cosmic_events/total_mc*100:.1f}%")
		print(f"νμ CC background: {cc_numu_events/total_mc*100:.1f}%") 
		print(f"NC background: {nc_events/total_mc*100:.1f}%")

	print(f"Plot saved for {var_name}")

print("\nSaved to", out_name)

out.Close()