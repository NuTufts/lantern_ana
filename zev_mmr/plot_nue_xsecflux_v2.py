import os,sys
import ROOT as rt
import array
from math import sqrt



run_num = 1

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


## Run 4b (Suprise Files) 
if run_num == 4: 
	targetpot = 1.45e+20 ## was 1.3e+20 , need rerun yaml?
	scaling = {"numu":targetpot/7.881656209241413e+20,
			"nue":targetpot/1.1785765118473412e+23,
			# "extbnb":23090946.0/94414115.0,
			"extbnb":34317881.0/96638186.0,
			"data":1.0}
	files = {"numu":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_BNB_nu_overlay_surprise.root",
			"nue":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_BNB_nue_overlay_surprise.root", 
			"extbnb":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_extbnb.root",
			"data":"./zev_mmr/mmr_outputs/run4b_beamon.root"}
	show_data = False 
	plot_title = "Run 4b"
	# plot_title = "Run4b: Inclusive CC #nu_{e} Selection"
	out_name = "./zev_mmr/hists/nue_hists4.root"
	
## Cross Section & Flux Uncertianties
xsecflux_variables = ['visible_energy', 'electron_momentum', 'electron_angle']
# Map neutrino type to the sample name in the xsecflux file
xsecflux_sample_map = {
	'numu': 'run1_bnb_nu_overlay_mcc9_v28_wctagger',
	'nue': 'run1_bnb_nue_overlay_mcc9_v28_wctagger'
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
		'title': plot_title+'; Reconstructed Electron cos(#theta); '+legend_POT_string,
		'cut_suffix': '&& (nueIncCC_reco_electron_costheta>-900)',  # Valid cos(theta) only
		'rebin_config': {
			'type': 'range',
			'xmin': 0.0,
			'xmax': 1.0,
			'underflow': True  # First bin is underflow
		}
	}
}

# Load xsecflux uncertainties for each sample
xsecflux_hists = {}
for xsample_name, xfile_path in xsecflux_files.items():
	print(f"\nLoading xsecflux uncertainties from {xfile_path}")
	xfile = rt.TFile(xfile_path)
	xsecflux_hists[xsample_name] = {}
	
	# Get the correct sample name for this neutrino type
	xsample = xsecflux_sample_map[xsample_name]
	
	for var in xsecflux_variables:
		hists_with_errors = make_hist_w_errors(xfile, var, xsample, all_pars)
		xsecflux_hists[xsample_name][var] = hists_with_errors
		print(f"  Loaded uncertainties for {xsample_name}, variable {var}")

# Create histograms for each variable
for var_name, var_info in variables.items():
	print(f"\n=== Creating {var_name} histogram ===")
	
	# Create canvas for main histogram
	canvas = rt.TCanvas(f"c_{var_name}", f"{var_name} Distribution", 1000, 800)
	canvas.Draw()

	hists = {}
	total_events = {}

	# Create histograms for each category
	for cat_name, cat_info in categories.items():
		total_events[cat_name] = 0
		
		for sample in cat_info['samples']:
			# Construct full cut string
			full_cut = f"({base_cut}){cat_info['truth_cut']}{var_info['cut_suffix']}"
			
			# Create histogram name
			hname = f'h_{var_name}_{cat_name}_{sample}'
			
			# Create histogram 
			hist = rt.TH1D(hname, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
			hist.Sumw2()
						
			# For neutrino energy: manually handle overflow by adjusting values > 2.0 to be exactly 2.0
			if var_name == 'neutrino_energy':
				# Create a temporary histogram to capture all events including overflow
				temp_hist = rt.TH1D(hname+"_temp", "", 1000, 0, 10)  # Large range to capture all events
				trees[sample].Draw(f"{var_info['var']}>>{hname}_temp", f"({full_cut})*eventweight_weight", "goff")
				
				# Now fill the actual histogram, forcing overflow values into the last bin
				for ibin in range(1, temp_hist.GetNbinsX() + 1):
					bin_content = temp_hist.GetBinContent(ibin)
					if bin_content > 0:
						energy_val = temp_hist.GetBinCenter(ibin)
						weight = bin_content
						
						# If energy > 2.0, put it in the overflow (last bin)
						if energy_val >= 2.0:
							hist.Fill(1.99, weight)  # Fill just below 2.0 to ensure it goes in last bin
						else:
							hist.Fill(energy_val, weight)
			
			# For electron momentum: manually handle overflow by adjusting values > 1.5 to be exactly 1.5
			elif var_name == 'electron_momentum':
				# Create a temporary histogram to capture all events including overflow
				temp_hist = rt.TH1D(hname+"_temp", "", 1000, 0, 10)  # Large range to capture all events
				trees[sample].Draw(f"{var_info['var']}>>{hname}_temp", f"({full_cut})*eventweight_weight", "goff")
				
				# Now fill the actual histogram, forcing overflow values into the last bin
				for ibin in range(1, temp_hist.GetNbinsX() + 1):
					bin_content = temp_hist.GetBinContent(ibin)
					if bin_content > 0:
						momentum_val = temp_hist.GetBinCenter(ibin)
						weight = bin_content
						
						# If momentum >= 1.5, put it in the overflow (last bin)
						if momentum_val >= 1.5:
							hist.Fill(1.49, weight)  # Fill just below 1.5 to ensure it goes in last bin
						else:
							hist.Fill(momentum_val, weight)
			
			# For cos theta: manually handle underflow by adjusting values < -1.0 to be exactly -1.0
			elif var_name == 'electron_costheta':
				# Create a temporary histogram to capture all events including underflow
				temp_hist = rt.TH1D(hname+"_temp", "", 1000, -2, 2)  # Wide range to capture all events
				trees[sample].Draw(f"{var_info['var']}>>{hname}_temp", f"({full_cut})*eventweight_weight", "goff")
				
				# Now fill the actual histogram, forcing underflow values into the first bin
				for ibin in range(1, temp_hist.GetNbinsX() + 1):
					bin_content = temp_hist.GetBinContent(ibin)
					if bin_content > 0:
						costheta_val = temp_hist.GetBinCenter(ibin)
						weight = bin_content
						
						# If costheta < 0.375 (first bin upper edge), put it in the underflow (first bin)
						if costheta_val < 0.375:
							hist.Fill(0.0, weight)  # Fill at 0.0 to ensure it goes in first bin
						else:
							hist.Fill(costheta_val, weight)
			
			else:
				# Standard filling for other variables
				trees[sample].Draw(f"{var_info['var']}>>{hname}", f"({full_cut})*eventweight_weight", "goff")

			# Scale by POT/exposure
			hist.Scale(scaling[sample])
			
			# Store in dictionary
			if cat_name not in hists:
				hists[cat_name] = hist.Clone(f"h_{var_name}_{cat_name}")
				hists[cat_name].Reset()
			
			# Add to category total
			hists[cat_name].Add(hist)
			total_events[cat_name] += hist.Integral()
			
			print(f"{cat_name}-{sample}: {hist.Integral():.2f} events")

			# hack to avoid duplicating integral in legend 
			if "(" not in categories[cat_name]['legend']: 
				categories[cat_name]['legend'] += f" ({hist.Integral():.1f})"

	# Set histogram styles with requested colors
	for cat_name, cat_info in categories.items():
		if cat_name in hists:
			hist = hists[cat_name]
			
			if cat_name == 'data':
				# Data: black line with error bars
				hist.SetLineColor(cat_info['color'])
				hist.SetLineWidth(2)
				hist.SetMarkerStyle(2)
				hist.SetMarkerColor(rt.kBlack)
				hist.SetMarkerSize(0.8)
			else:
				# MC: filled histograms with solid colors
				hist.SetFillColor(cat_info['color'])
				hist.SetFillStyle(cat_info['fill_style'])
				hist.SetLineColor(cat_info['color'])
				hist.SetLineWidth(1)

	# Create stack for MC components (exclude data)
	stack_order = ['cosmic', 'nc_nue', 'nc_numu', 'cc_numu', 'cc_nue']
	hstack = rt.THStack(f"hs_{var_name}", "")

	# Create total MC histogram for uncertainty calculation
	h_total_mc = None
	for cat_name in stack_order:
		if cat_name in hists and cat_name != 'data':
			hstack.Add(hists[cat_name])
			if h_total_mc is None:
				h_total_mc = hists[cat_name].Clone(f"h_total_mc_{var_name}")
			else:
				h_total_mc.Add(hists[cat_name])

	# Apply rebinning based on variable configuration
	rebin_config = var_info.get('rebin_config', {})
	
	if rebin_config:
		rebin_type = rebin_config.get('type', 'constant')
		
		if rebin_type == 'variable':
			# Variable bin width rebinning (for neutrino_energy: 0-2 GeV)
			new_bins = array.array('d', rebin_config['bins'])
			
			for cat_name in hists:
				hists[cat_name] = hists[cat_name].Rebin(len(new_bins)-1, hists[cat_name].GetName()+"_rebin", new_bins)
			
			if h_total_mc is not None:
				h_total_mc = h_total_mc.Rebin(len(new_bins)-1, h_total_mc.GetName()+"_rebin", new_bins)
			
			# Add overflow if specified - sum all bins beyond the range
			if rebin_config.get('overflow', False):
				# First, get the original histogram before rebinning to sum all overflow bins
				for cat_name in hists:
					h = hists[cat_name]
					nbins = h.GetNbinsX()
					last_bin_content = h.GetBinContent(nbins)
					last_bin_error_sq = h.GetBinError(nbins)**2
					
					# Sum all overflow bins (everything beyond the last bin)
					overflow_content = 0.0
					overflow_error_sq = 0.0
					for ibin in range(nbins+1, h.GetNbinsX() + 100):  # Sum far beyond to catch all overflow
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
		
		elif rebin_type == 'constant':
			# Constant rebinning factor (for electron_momentum)
			rebin_factor = rebin_config.get('factor', 2)
			
			for cat_name in hists:
				hists[cat_name].Rebin(rebin_factor)
			
			if h_total_mc is not None:
				h_total_mc.Rebin(rebin_factor)
			
			# Add overflow if specified - sum all bins beyond the range
			if rebin_config.get('overflow', False):
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

	# Force tick marks on all sides
	canvas.SetTickx(1)
	canvas.SetTicky(1)
	
	# Update canvas
	canvas.SetLogy(0)  # Linear scale
	canvas.Update()

	# Save main canvas to ROOT file
	out.cd()
	canvas.Write()

	# === Create SEPARATE canvas for fractional error plot ===
	canvas_frac = rt.TCanvas(f"c_{var_name}_frac_error", f"{var_name} Fractional Error", 1000, 600)
	canvas_frac.Draw()
	canvas_frac.SetTickx(1)
	canvas_frac.SetTicky(1)
	
	# Create fractional error histogram
	h_frac_error = None
	if h_uncertainty is not None and h_total_mc is not None:
		h_frac_error = h_uncertainty.Clone(f"h_frac_error_{var_name}")
		
		# Calculate fractional error for each bin
		for ibin in range(0, h_frac_error.GetNbinsX() + 2):  # Include underflow/overflow
			central_value = h_total_mc.GetBinContent(ibin)
			error = h_uncertainty.GetBinError(ibin)
			
			if central_value > 0:
				frac_error = error / central_value
				h_frac_error.SetBinContent(ibin, frac_error)
				h_frac_error.SetBinError(ibin, 0)  # No error bars on fractional error
			else:
				h_frac_error.SetBinContent(ibin, 0)
				h_frac_error.SetBinError(ibin, 0)
		
		# Get x-axis title from original variable info
		title_parts = var_info['title'].split(';')
		x_axis_title = title_parts[1].strip() if len(title_parts) > 1 else ""
		
		# Set style for fractional error plot with proper full-canvas formatting
		frac_title = f"{plot_title}; {x_axis_title}; Fractional Systematic Uncertainty"
		h_frac_error.SetTitle(frac_title)
		h_frac_error.SetFillColor(rt.kBlue-9)
		h_frac_error.SetFillStyle(1001)
		h_frac_error.SetLineColor(rt.kBlue)
		h_frac_error.SetLineWidth(2)
		h_frac_error.SetMarkerSize(0)
		
		# Set axis label sizes for full canvas (not small pad)
		h_frac_error.GetXaxis().SetLabelSize(0.04)
		h_frac_error.GetXaxis().SetTitleSize(0.05)
		h_frac_error.GetXaxis().SetTitleOffset(1.0)
		h_frac_error.GetXaxis().SetTickLength(0.02)
		h_frac_error.GetXaxis().SetNdivisions(510)  # 5 major divisions, 10 minor
		
		h_frac_error.GetYaxis().SetLabelSize(0.04)
		h_frac_error.GetYaxis().SetTitleSize(0.05)
		h_frac_error.GetYaxis().SetTitleOffset(1.2)
		h_frac_error.GetYaxis().SetTickLength(0.015)
		h_frac_error.GetYaxis().SetNdivisions(505)  # 5 major divisions, 5 minor
		
		# Set y-axis range for fractional error (typically 0 to ~0.3 or 30%)
		max_frac_error = 0
		for ibin in range(1, h_frac_error.GetNbinsX() + 1):
			frac = h_frac_error.GetBinContent(ibin)
			if frac > max_frac_error:
				max_frac_error = frac
		
		y_range_max = max(0.5, max_frac_error * 1.3)  # At least 50% range, with some headroom
		h_frac_error.SetMinimum(0)
		h_frac_error.SetMaximum(y_range_max)
		
		# Draw fractional error
		h_frac_error.Draw("hist")
		
		# Set x-axis range for cos theta plot to show only 0 to 1
		if var_name == 'electron_costheta':
			h_frac_error.GetXaxis().SetRangeUser(0.0, 1.0)
		
		# Add horizontal grid lines for easier reading
		canvas_frac.SetGridy(1)
		
		# Add horizontal line at y=0 for reference
		if hstack.GetHists():
			x_min = hstack.GetXaxis().GetXmin()
			x_max = hstack.GetXaxis().GetXmax()
		else:
			x_min = hists['data'].GetXaxis().GetXmin()
			x_max = hists['data'].GetXaxis().GetXmax()
		
		# Adjust x_min and x_max for electron_costheta to match the displayed range
		if var_name == 'electron_costheta':
			x_min = 0.0
			x_max = 1.0
		
		line_zero = rt.TLine(x_min, 0, x_max, 0)
		line_zero.SetLineColor(rt.kBlack)
		line_zero.SetLineStyle(2)
		line_zero.SetLineWidth(2)
		line_zero.Draw()
		
		# Add text label describing uncertainty sources
		label = rt.TLatex()
		label.SetNDC()
		label.SetTextSize(0.035)
		label.SetTextFont(42)
		label.DrawLatex(0.15, 0.85, "Systematic uncertainties: GENIE, flux, FSI")
		
		canvas_frac.Update()
		canvas_frac.RedrawAxis()
		
		# Save fractional error canvas
		out.cd()
		canvas_frac.Write()
		
		print(f"  Fractional error plot saved for {var_name}")
		print(f"  Max fractional error: {max_frac_error:.1%}")


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