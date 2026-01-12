import os,sys
import ROOT as rt
import array
from math import sqrt



"""
POT:
BNB nu overlay  7.88166e+20
BNB dirt        3.05893e+20
BNB nue overlay 1.17858e+23
BNB ncpi0       5.01921e+21
BNB beam-on     9.75e+19

Triggers:
BNB beam-on 23090946 
BNB EXT     94414115
"""

run_num = 1

lantern_dir = "/nashome/z/zimani/lantern/lantern_ana/"

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
		"numu": f"{lantern_dir}/studies/xsecfluxsys/run1_outputs/xsecflux_run1_numu_intrinsic_nue.root"
	}
	show_data = True 
	plot_title = "Run 1"

	out_name = f"{lantern_dir}/zev_mmr/hists_xsecflux/nue_hists1.root"


## Run 4b (Suprise Files) 
if run_num == 4: 
	targetpot = 1.45e+20 ## was 1.3e+20 , need rerun yaml?
	scaling = {"numu":targetpot/7.881656209241413e+20,
			"nue":targetpot/1.1785765118473412e+23,
			"extbnb":34317881.0/96638186.0,
			"data":1.0}
	files = {"numu":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_BNB_nu_overlay_surprise.root",
			"nue":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_BNB_nue_overlay_surprise.root", 
			"extbnb":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_extbnb.root",
			"data":"./zev_mmr/mmr_outputs/run4b_beamon.root"}
	show_data = False 
	plot_title = "Run 4b"
	out_name = "./zev_mmr/hists/nue_hists4.root"
	

histmodes = ['cv','w','w2','N']
xsecflux_variables = ['visible_energy']
samples   = ['run1_bnb_nu_overlay_mcc9_v28_wctagger']
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


def make_hist_w_errors(rfile, varname, sample, parlist):
	"""
	Load uncertainty histograms from xsecflux file and compute total variance
	"""
	hists = {}
	hcv_name = f"h{varname}_{sample}_cv"
	hcv = rfile.Get(hcv_name)
	
	if not hcv:
		print(f"Warning: Could not find {hcv_name} in file")
		return None
	
	print("here")

	print(f"h{varname}__{sample}_totvariance")

	hvar_tot = hcv.Clone(f"h{varname}__{sample}_totvariance")
	hvar_tot.Reset()
	hmeans2 = hcv.Clone(f"h{varname}__{sample}_meanofmeans")
	hmeans2.Reset()
	
	for parname in parlist:
		hname_mean = f"h{varname}__{sample}__{parname}_mean"
		hname_var  = f"h{varname}__{sample}__{parname}_variance"
		hmean = rfile.Get(hname_mean)
		hvar  = rfile.Get(hname_var)
		
		if not hmean or not hvar:
			print(f"Warning: Could not find {hname_mean} or {hname_var}")
			continue
			
		hists[parname] = hvar
		for ibin in range(0, hvar_tot.GetXaxis().GetNbins()+1):
			xvar  = hvar.GetBinContent(ibin)
			xmean = hmean.GetBinContent(ibin)

			if xmean > 0:
				xfracvar = xvar / xmean
			else:
				xfracvar = 0.0

			cv_var = xfracvar * hcv.GetBinContent(ibin)

			xvar_tot  = hvar_tot.GetBinContent(ibin)
			hvar_tot.SetBinContent(ibin, xvar_tot + cv_var)  # add variances
			xmean2 = hmeans2.GetBinContent(ibin)
			hmeans2.SetBinContent(ibin, xmean2 + xmean / len(parlist))
	
	# set std for CV error
	for ibin in range(0, hvar_tot.GetXaxis().GetNbins()+1):
		stddev = sqrt(hvar_tot.GetBinContent(ibin))
		hcv.SetBinError(ibin, stddev)
	
	hists['cv'] = hcv
	hists['mean2'] = hmeans2
	hists['totvar'] = hvar_tot
	return hists


def get_uncertainty_histogram(var_name, h_total_mc, xsecflux_tfiles, scaling):
	"""
	Create uncertainty histogram by adding numu and nue uncertainties in quadrature
	"""
	if not xsecflux_tfiles:
		return None
		
	h_uncertainty = h_total_mc.Clone(f"h_uncertainty_{var_name}")
	h_uncertainty.Reset()
	
	# Map variable names to xsecflux naming convention
	var_map = {
		'neutrino_energy': 'visible_energy',
		'electron_momentum': 'visible_energy', 
		'electron_costheta': 'visible_energy'
	}
	
	xsecflux_var = var_map.get(var_name, 'visible_energy')
	
	# Process each sample (nue, numu)
	for sample_key in ['nue', 'numu']:
		if sample_key not in xsecflux_tfiles:
			continue
			
		xfile = xsecflux_tfiles[sample_key]
		
		# Get the sample name from the xsecflux file
		# Assuming the sample name in xsecflux follows pattern: run1_bnb_nXe_overlay_...
		if sample_key == 'nue':
			xsec_sample = 'run1_bnb_nue_overlay_mcc9_v28_wctagger'
		else:
			xsec_sample = 'run1_bnb_nu_overlay_mcc9_v28_wctagger'
		
		# Get uncertainty histograms
		hists_dict = make_hist_w_errors(xfile, xsecflux_var, xsec_sample, all_pars)
		
		if hists_dict is None:
			print(f"Warning: Could not load uncertainties for {sample_key}")
			continue
		
		hvar = hists_dict['totvar']
		
		# Scale the variance by the POT scaling factor (squared for variance)
		scale_factor = scaling[sample_key if sample_key == 'numu' else 'nue']
		
		# Add variance in quadrature (scaled)
		for ibin in range(0, h_uncertainty.GetXaxis().GetNbins()+1):
			current_var = h_uncertainty.GetBinContent(ibin)
			new_var = hvar.GetBinContent(ibin) * (scale_factor * scale_factor)
			h_uncertainty.SetBinContent(ibin, current_var + new_var)
	
	# Convert variance to standard deviation
	for ibin in range(0, h_uncertainty.GetXaxis().GetNbins()+1):
		variance = h_uncertainty.GetBinContent(ibin)
		h_uncertainty.SetBinContent(ibin, sqrt(variance))
		h_uncertainty.SetBinError(ibin, 0)  # Uncertainty on uncertainty is not shown
	
	# Now copy bin contents to bin errors of total MC for proper display
	for ibin in range(0, h_total_mc.GetXaxis().GetNbins()+1):
		mc_content = h_total_mc.GetBinContent(ibin)
		uncertainty = h_uncertainty.GetBinContent(ibin)
		h_uncertainty.SetBinContent(ibin, mc_content)
		h_uncertainty.SetBinError(ibin, uncertainty)
	
	return h_uncertainty


rt.gStyle.SetOptStat(0)

tfiles = {}
trees = {}

samples = ['nue','numu','extbnb','data']

for sample in samples:
	tfiles[sample] = rt.TFile(files[sample])
	trees[sample] = tfiles[sample].Get("analysis_tree")
	nentries = trees[sample].GetEntries()
	print(f"sample={sample} has {nentries} entries")

# Load xsecflux files for uncertainties
xsecflux_tfiles = {}
for key, filepath in xsecflux_files.items():
	if os.path.exists(filepath):
		xsecflux_tfiles[key] = rt.TFile(filepath)
		print(f"Loaded xsecflux file for {key}: {filepath}")
	else:
		print(f"Warning: xsecflux file not found: {filepath}")

## Output file (must be set after loading samples)
out = rt.TFile(out_name, "recreate")

# Base cuts using NeutrinoSelectionProducer variables
base_cut = f"(nueIncCC_cut1_vertex_fiducial==1)"
base_cut += f" && (nueIncCC_cut2_cosmic_rejection==1)"
base_cut += f" && (nueIncCC_cut3_no_muon_tracks==1)"
base_cut += f" && (nueIncCC_cut4_has_electron==1)"
base_cut += f" && (nueIncCC_cut5_low_muon_score==1)"
base_cut += f" && (nueIncCC_cut6_electron_confidence==1)"

print(f"Base cuts using NeutrinoSelectionProducer (νe CC Selection): {base_cut}")

# Define sample categories
categories = {
	'cosmic': {
		'samples': ['extbnb'],
		'truth_cut': f' ',
		'color': rt.kGray+2,
		'fill_style': 1001,
		'legend': 'Cosmic bkgd'
	},
	'nc_nue': {
		'samples': ['nue'],
		'truth_cut': f' && (nueIncCC_is_neutral_current==1)',
		'color': rt.kGreen+1,
		'fill_style': 1001,
		'legend': 'NC #nu_{e}'
	},
	'cc_nue': {
		'samples': ['nue'],
		'truth_cut': f' && (nueIncCC_is_charge_current==1)',
		'color': rt.kRed,
		'fill_style': 1001,
		'legend': 'CC #nu_{e}'
	},
	'nc_numu': {
		'samples': ['numu'],
		'truth_cut': f' && (nueIncCC_is_neutral_current==1)',
		'color': rt.kGray,
		'fill_style': 1001,
		'legend': 'NC #nu_{#mu}'
	},
	'cc_numu': {
		'samples': ['numu'],
		'truth_cut': f' && (nueIncCC_is_charge_current==1)',
		'color': rt.kBlue,
		'fill_style': 1001,
		'legend': 'CC #nu_{#mu}'
	},
	'data': {
		'samples': ['data'],
		'truth_cut': '',
		'color': rt.kBlack,
		'fill_style': 0,
		'legend': 'Data'
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
		'has_overflow': True,
		'y_max': 30
	},
	'electron_momentum': {
		'var': 'nueIncCC_reco_electron_momentum',
		'nbins': 25,
		'xmin': 0.0,
		'xmax': 1.5,
		'title': plot_title+'; Reconstructed Electron Momentum (GeV); '+legend_POT_string,
		'cut_suffix': '&& (nueIncCC_reco_electron_momentum>0)',
		'has_overflow': True
	},
	'electron_costheta': {
		'var': 'nueIncCC_reco_electron_costheta',
		'nbins': 20,
		'xmin': -1.0,
		'xmax': 1.0,
		'title': plot_title+'; Reconstructed Electron cos(#theta); '+legend_POT_string,
		'cut_suffix': '&& (nueIncCC_reco_electron_costheta>-900)',
		'has_underflow': True
	}
}

# Create histograms for each variable
for var_name, var_info in variables.items():
	print(f"\n=== Creating {var_name} histogram ===")
	
	# Create canvas
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
			
			# Handle overflow/underflow for specific variables
			if var_name == 'neutrino_energy':
				temp_hist = rt.TH1D(hname+"_temp", "", 1000, 0, 10)
				trees[sample].Draw(f"{var_info['var']}>>{hname}_temp", f"({full_cut})*eventweight_weight", "goff")
				
				for ibin in range(1, temp_hist.GetNbinsX() + 1):
					bin_content = temp_hist.GetBinContent(ibin)
					if bin_content > 0:
						energy_val = temp_hist.GetBinCenter(ibin)
						weight = bin_content
						
						if energy_val >= 2.0:
							hist.Fill(1.99, weight)
						else:
							hist.Fill(energy_val, weight)
			
			elif var_name == 'electron_momentum':
				temp_hist = rt.TH1D(hname+"_temp", "", 1000, 0, 10)
				trees[sample].Draw(f"{var_info['var']}>>{hname}_temp", f"({full_cut})*eventweight_weight", "goff")
				
				for ibin in range(1, temp_hist.GetNbinsX() + 1):
					bin_content = temp_hist.GetBinContent(ibin)
					if bin_content > 0:
						momentum_val = temp_hist.GetBinCenter(ibin)
						weight = bin_content
						
						if momentum_val >= 1.5:
							hist.Fill(1.49, weight)
						else:
							hist.Fill(momentum_val, weight)
			
			elif var_name == 'electron_costheta':
				temp_hist = rt.TH1D(hname+"_temp", "", 1000, -2, 2)
				trees[sample].Draw(f"{var_info['var']}>>{hname}_temp", f"({full_cut})*eventweight_weight", "goff")
				
				for ibin in range(1, temp_hist.GetNbinsX() + 1):
					bin_content = temp_hist.GetBinContent(ibin)
					if bin_content > 0:
						costheta_val = temp_hist.GetBinCenter(ibin)
						weight = bin_content
						
						if costheta_val < 0.375:
							hist.Fill(0.0, weight)
						else:
							hist.Fill(costheta_val, weight)
			
			else:
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

	# Set histogram styles
	for cat_name, cat_info in categories.items():
		if cat_name in hists:
			hist = hists[cat_name]
			
			if cat_name == 'data':
				hist.SetLineColor(rt.kBlack)
				hist.SetLineWidth(2)
				hist.SetMarkerStyle(2)
				hist.SetMarkerColor(rt.kBlack)
				hist.SetMarkerSize(0.8)
			else:
				hist.SetFillColor(cat_info['color'])
				hist.SetFillStyle(cat_info['fill_style'])
				hist.SetLineColor(cat_info['color'])
				hist.SetLineWidth(1)

	# Create stack for MC components
	stack_order = ['cosmic', 'nc_nue', 'nc_numu', 'cc_numu', 'cc_nue']
	hstack = rt.THStack(f"hs_{var_name}", "")

	# Create total MC histogram
	h_total_mc = None
	for cat_name in stack_order:
		if cat_name in hists and cat_name != 'data':
			hstack.Add(hists[cat_name])
			if h_total_mc is None:
				h_total_mc = hists[cat_name].Clone(f"h_total_mc_{var_name}")
			else:
				h_total_mc.Add(hists[cat_name])

	# Create uncertainty histogram with proper error propagation
	h_uncertainty = None
	if h_total_mc is not None and xsecflux_tfiles:
		h_uncertainty = get_uncertainty_histogram(var_name, h_total_mc, xsecflux_tfiles, scaling)
		
		if h_uncertainty is not None:
			h_uncertainty.SetFillColor(rt.kGray+1)
			h_uncertainty.SetFillStyle(3002)
			h_uncertainty.SetLineColor(rt.kGray+1)
			h_uncertainty.SetLineWidth(1)
			h_uncertainty.SetMarkerSize(0)

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

	# Draw uncertainty histogram
	if h_uncertainty is not None:
		h_uncertainty.Draw("E2same")

	# Draw data
	if 'data' in hists:
		hists['data'].Draw("E1same")
	
	# Set x-axis range for cos theta
	if var_name == 'electron_costheta':
		if hstack.GetHists():
			hstack.GetXaxis().SetRangeUser(0.0, 1.0)
		else:
			hists['data'].GetXaxis().SetRangeUser(0.0, 1.0)

	# Add overflow text
	if var_name == 'neutrino_energy' and var_info.get('has_overflow', False):
		overflow_text = rt.TText()
		overflow_text.SetTextSize(0.03)
		overflow_text.SetTextAlign(22)
		overflow_text.SetTextColor(rt.kBlack)
		
		hist_for_axis = hstack if hstack.GetHists() else hists['data']
		last_bin = hist_for_axis.GetXaxis().GetNbins()
		x_pos = hist_for_axis.GetXaxis().GetBinCenter(last_bin)
		y_pos = -0.8
		
		overflow_text.DrawText(x_pos, y_pos, "overflow")
		
		if hstack.GetHists():
			hist.GetXaxis().CenterTitle()
		else:
			hists['data'].GetXaxis().CenterTitle()

	# Create legend
	legend = rt.TLegend(0.65, 0.50, 0.89, 0.89)
	legend.SetTextSize(0.03)
	legend.SetFillStyle(0)
	legend.SetBorderSize(1)

	for cat_name in stack_order:
		if cat_name in hists and cat_name in categories:
			legend.AddEntry(hists[cat_name], categories[cat_name]['legend'], "f")

	if 'data' in hists:
		legend.AddEntry(hists['data'], categories['data']['legend'], "lep")

	if h_uncertainty is not None:
		legend.AddEntry(h_uncertainty, "Syst. Uncertainty", "f")

	legend.Draw()

	# Update canvas
	canvas.SetLogy(0)
	canvas.Update()

	# Save
	canvas.Write()
	if h_total_mc:
		h_total_mc.Write()
	if h_uncertainty:
		h_uncertainty.Write()

	# Print summary
	print(f"\n=== {var_name.upper()} Analysis Summary ===")
	total_mc = sum(total_events[cat] for cat in total_events if cat != 'data')
	print(f"Total MC: {total_mc:.1f}")
	if 'data' in total_events:
		print(f"Data: {total_events['data']:.1f}")
		if total_mc > 0:
			print(f"Data/MC ratio: {total_events['data']/total_mc:.2f}")

	cc_nue_events = total_events.get('cc_nue', 0)
	if total_mc > 0:
		print(f"CC νe purity: {cc_nue_events/total_mc*100:.1f}%")
	
	cosmic_events = total_events.get('cosmic', 0)
	cc_numu_events = total_events.get('cc_numu', 0)
	nc_events = total_events.get('nc_nue', 0) + total_events.get('nc_numu', 0)
	
	if total_mc > 0:
		print(f"Cosmic background: {cosmic_events/total_mc*100:.1f}%")
		print(f"νμ CC background: {cc_numu_events/total_mc*100:.1f}%") 
		print(f"NC background: {nc_events/total_mc*100:.1f}%")

	print(f"Plot saved for {var_name}")

print("\nSaved to", out_name)

# Close files
out.Close()
for tfile in xsecflux_tfiles.values():
	tfile.Close()