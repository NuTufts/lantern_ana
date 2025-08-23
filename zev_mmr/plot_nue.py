import os,sys
import ROOT as rt
import array

targetpot = 4.4e19

samples = ['nue','numu','extbnb','data']

scaling = {"numu":targetpot/4.675690535431973e+20,
		   "nue":targetpot/9.662529168587103e+22,
		   "extbnb":(176153.0)/(433446.0),
		   "data":1.0}

files = {"numu":"./my_mmr/nue_outputs/run1_bnb_nu_overlay_mcc9_v28_wctagger.root",
		 "nue":"./my_mmr/nue_outputs/run1_bnb_nue_overlay_mcc9_v28_wctagger.root", 
		 "extbnb":"./my_mmr/nue_outputs/run1_extbnb_mcc9_v29e_C1.root",
		 "data":"./my_mmr/nue_outputs/run1_bnb5e19.root"}

rt.gStyle.SetOptStat(0)

tfiles = {}
trees = {}

for sample in samples:
	tfiles[sample] = rt.TFile( files[sample] )
	trees[sample] = tfiles[sample].Get("analysis_tree")
	nentries = trees[sample].GetEntries()
	print(f"sample={sample} has {nentries} entries")

out = rt.TFile("./my_mmr/nue_hists.root","recreate")

# NEW: Base cuts using NeutrinoSelectionProducer variables
# These implement the 6 cuts for electron neutrino selection
base_cut = f"(nueIncCC_cut1_vertex_fiducial==1)"        # Cut 1: Vertex in fiducial volume
base_cut += f" && (nueIncCC_cut2_cosmic_rejection==1)"   # Cut 2: Cosmic rejection  
base_cut += f" && (nueIncCC_cut3_no_muon_tracks==1)"     # Cut 3: No muon tracks
base_cut += f" && (nueIncCC_cut4_has_electron==1)"       # Cut 4: Has primary electron
base_cut += f" && (nueIncCC_cut5_low_muon_score==1)"     # Cut 5: Low muon scores
base_cut += f" && (nueIncCC_cut6_electron_confidence==1)" # Cut 6: High electron confidence

# Alternative: use the combined cut from the producer
# base_cut = f"(nueIncCC_passes_all_cuts==1)"

print(f"Base cuts using NeutrinoSelectionProducer (νe CC Selection): {base_cut}")

# Define sample categories with requested colors - updated for electron neutrino analysis
categories = {
	'cosmic': {
		'samples': ['extbnb'],
		'truth_cut': '',  # No truth cut for cosmic background
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
		'fill_style': 0,      # No fill for data points
		'legend': 'Data'
	}
}

# Function to create custom binning for neutrino energy (combines first two bins)
def create_neutrino_energy_binning():
	# Original: 10 bins from 0.0 to 2.0 GeV (bin width = 0.2 GeV)
	# Modified: 9 bins total - first bin is 0.0-0.4, then 0.4-0.6, 0.6-0.8, ..., 1.8-2.0+
	bin_edges = [0.0, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
	return array.array('d', bin_edges)

# Function to create custom binning for cos theta with underflow bin
def create_costheta_binning():
	# Create binning: first bin from -1 to 0.375, then 5 equal bins from 0.375 to 1.0
	# 5 bins from 0.375 to 1.0: bin width = (1.0 - 0.375) / 5 = 0.125
	bin_edges = [-1.0, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]
	return array.array('d', bin_edges)

# Function to create histograms with proper overflow handling
def create_variable_binning_hist(name, title, bin_edges):
	hist = rt.TH1D(name, title, len(bin_edges)-1, bin_edges)
	hist.Sumw2()
	return hist

# Define variables to plot - updated for electron neutrino analysis
variables = {
	'neutrino_energy': {
		'var': 'nueIncCC_reco_nu_energy',
		'custom_binning': True,
		'bin_edges': create_neutrino_energy_binning(),
		'title': 'Inclusive CC #nu_{e} Selected Events; Reconstructed Neutrino Energy (GeV); Events per 4.4e+19 POT',
		'cut_suffix': '',  # No additional cut
		'has_overflow': True,
		'y_max': 13  # Set fixed y-axis maximum
	},
	'electron_momentum': {
		'var': 'nueIncCC_reco_electron_momentum',
		'nbins': 8,
		'xmin': 0.0,
		'xmax': 1.5,
		'title': 'Inclusive CC #nu_{e} Selected Events; Reconstructed Electron Momentum (GeV/c); Events per 4.4e+19 POT',
		'cut_suffix': '&& (nueIncCC_reco_electron_momentum>0)',  # Valid momentum only
		'custom_binning': False,
		'has_overflow': True
	},
	'electron_costheta': {
		'var': 'nueIncCC_reco_electron_costheta',
		'custom_binning': True,
		'bin_edges': create_costheta_binning(),
		'title': 'Inclusive CC #nu_{e} Selected Events; Reconstructed Electron cos(#theta); Events per 4.4e+19 POT',
		'cut_suffix': '&& (nueIncCC_reco_electron_costheta>-900)',  # Valid cos(theta) only
		'has_underflow': True  # Special flag to indicate this variable has underflow bin
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
			
			# Create histogram with appropriate binning
			if var_info.get('custom_binning', False):
				hist = create_variable_binning_hist(hname, "", var_info['bin_edges'])
			else:
				hist = rt.TH1D(hname, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
				hist.Sumw2()
			
			# print(f"Filling {hname} with cut: {full_cut}")
			
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
				hist.SetLineColor(rt.kBlack)
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

	# Create uncertainty histogram with blue hatching
	h_uncertainty = None
	if h_total_mc is not None:
		h_uncertainty = h_total_mc.Clone(f"h_uncertainty_{var_name}")
		h_uncertainty.SetFillColor(rt.kBlue)
		h_uncertainty.SetFillStyle(3002)  # Hatched pattern
		h_uncertainty.SetLineColor(rt.kBlue)
		h_uncertainty.SetLineWidth(1)
		h_uncertainty.SetMarkerSize(0)

	# Draw histograms
	stack_max = hstack.GetMaximum() if hstack.GetHists() else 0
	data_max = hists['data'].GetMaximum() if 'data' in hists else 0

	# Set y-axis maximum - use fixed value for neutrino energy, calculated for others
	if var_name == 'neutrino_energy' and 'y_max' in var_info:
		y_max = var_info['y_max']
	else:
		y_max = max(stack_max, data_max) * 1.3

	if stack_max > data_max:
		hstack.SetTitle(var_info['title'])
		hstack.Draw("hist")
		hstack.SetMaximum(y_max)
	else:
		hists['data'].SetTitle(var_info['title'])
		hists['data'].Draw("E1")
		hists['data'].SetMaximum(y_max)
		hstack.Draw("histsame")

	# Draw uncertainty histogram on top of stack
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

	# Add underflow text for cos theta plot
	if var_name == 'electron_costheta' and var_info.get('has_underflow', False):
		# Create text object for underflow label
		underflow_text = rt.TText()
		underflow_text.SetTextSize(0.03)
		underflow_text.SetTextAlign(22)  # Center alignment
		underflow_text.SetTextColor(rt.kBlack)
		
		# Position the text below the first bin
		hist_for_axis = hstack if hstack.GetHists() else hists['data']
		x_pos = hist_for_axis.GetXaxis().GetBinCenter(1)
		y_pos = -0.08 * y_max  # Position below x-axis
		
		underflow_text.DrawText(x_pos, y_pos, "underflow")

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
		legend.AddEntry(h_uncertainty, "Error (WiP)", "f")

	legend.Draw()

	# Update canvas
	canvas.SetLogy(0)  # Linear scale
	canvas.Update()

	# Save canvas and histograms
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

out.Close()