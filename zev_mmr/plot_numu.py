import os,sys
import ROOT as rt
import array

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

# CRITICAL: Enable automatic sum of weights squared for proper error calculation
rt.TH1.SetDefaultSumw2(rt.kTRUE)

# targetpot = 9.75e+19

samples = ['nue','numu','extbnb','data']

# scaling = {"numu":targetpot/7.88166e+20,
# 		   "nue":targetpot/1.17858e+23,
# 		   "extbnb":(23090946)/(94414115),
# 		   "data":1.0}

# files = {"numu":"./run4_mmr/run4_outputs/run4_bnb_nu_overlay.root",
# 		 "nue":"./run4_mmr/run4_outputs/run4_bnb_nue_overlay.root", 
# 		 "extbnb":"./run4_mmr/run4_outputs/run4_ext_bnb.root",
# 		 "data":"./run4_mmr/run4_outputs/run4_data.root"}

run_num = 4

## Run 1 
if run_num == 1: 
	targetpot = 4.4e19
	scaling = {"numu":targetpot/4.675690535431973e+20,
			"nue":targetpot/9.662529168587103e+22,
			"extbnb":(176153.0)/(433446.0),
			"data":1.0}
	files = {"numu":"./zev_mmr/mmr_outputs/run1_bnb_nu_overlay_mcc9_v28_wctagger.root",
			"nue":"./zev_mmr/mmr_outputs/run1_bnb_nue_overlay_mcc9_v28_wctagger.root", 
			"extbnb":"./zev_mmr/mmr_outputs/run1_extbnb_mcc9_v29e_C1.root",
			"data":"./zev_mmr/mmr_outputs/run1_bnb5e19.root"}
	out_name = "./zev_mmr/hists/numu_hists1.root"
	# plot_title = Run1: Inclusive CC #nu_{#mu} Selection
	plot_title = "Run 1"

## Run 4b
if run_num == 4: 
	##  Old? 
	# targetpot = 1.3e+20
	# scaling = {"numu":targetpot/7.881656209241413e+20,
	#            "nue":targetpot/1.1785765118473412e+23,
	#            "extbnb":23090946.0/94414115.0,
	#            "data":1.0}
	targetpot = 1.45e+20
	scaling = {"numu":targetpot/7.881656209241413e+20,
	           "nue":targetpot/1.1785765118473412e+23,
	           "extbnb":34317881.0/96638186.0,
				# "extbnb": 23090946.0/94414115.0,
	           "data":1.0}
	files = {"numu":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_BNB_nu_overlay_surprise.root",
			 "nue":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_BNB_nue_overlay_surprise.root", 
			 "extbnb":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_extbnb.root",
			 "data":"./zev_mmr/mmr_outputs/run4b_beamon.root"}
	out_name = "./zev_mmr/hists/numu_hists4.root"
	plot_title = "Run 4b"



rt.gStyle.SetOptStat(0)
rt.gStyle.SetEndErrorSize(0) ## doesn't do anything 

tfiles = {}
trees = {}

for sample in samples:
	tfiles[sample] = rt.TFile( files[sample] )
	trees[sample] = tfiles[sample].Get("analysis_tree")
	nentries = trees[sample].GetEntries()
	print(f"sample={sample} has {nentries} entries")

out = rt.TFile(out_name,"recreate")

# Base cuts using NeutrinoSelectionProducer variables
base_cut = f"(numuIncCC_has_vertex_in_fv==1)"  # Cut 1: Vertex in fiducial volume
base_cut += f" && (numuIncCC_passes_cosmic_rejection==1)"  # Cut 2: Cosmic rejection
base_cut += f" && (numuIncCC_has_muon_track==1)"  # Cut 3: Muon identification

print(f"Base cuts using NeutrinoSelectionProducer: {base_cut}")

# Define sample categories with requested colors
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
		'truth_cut': f'&& (numuIncCC_is_nc_interaction==1)',
		'color': rt.kGray,    # Light gray
		'fill_style': 1001,   # Solid fill
		'legend': 'NC #nu_{e}'
	},
	'cc_nue': {
		'samples': ['nue'], 
		'truth_cut': f'&& (numuIncCC_is_cc_interaction==1)',
		'color': rt.kRed,     # Red
		'fill_style': 1001,   # Solid fill
		'legend': 'CC #nu_{e}'
	},
	'nc_numu': {
		'samples': ['numu'],
		'truth_cut': f'&& (numuIncCC_is_nc_interaction==1)', 
		'color': rt.kGreen+1, # Green
		'fill_style': 1001,   # Solid fill
		'legend': 'NC #nu_{#mu}'
	},
	'cc_numu': {
		'samples': ['numu'],
		'truth_cut': f'&& (numuIncCC_is_cc_interaction==1)',
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
	hist.Sumw2()  # Ensure error calculation is enabled
	return hist

# Function to properly scale histogram while maintaining sqrt(N) errors
def scale_histogram_with_correct_errors(hist, scale_factor):
	"""
	Scale histogram while maintaining proper sqrt(N) statistical errors.
	For a histogram with N raw events in a bin, after scaling by factor S:
	- Scaled content = N * S
	- Scaled error = sqrt(N) * S
	"""
	# Create a copy to work with
	scaled_hist = hist.Clone(hist.GetName() + "_scaled_temp")
	
	# Scale the histogram normally (this scales both content and errors)
	scaled_hist.Scale(scale_factor)
	
	# For data histograms, we want Poisson errors, so we need to correct
	# the error calculation after scaling
	for ibin in range(1, scaled_hist.GetNbinsX() + 1):
		content = scaled_hist.GetBinContent(ibin)
		# For Poisson statistics: error = sqrt(scaled_content)
		# But only for data - for MC we keep the propagated errors
		if scale_factor == 1.0:  # This is data (scale factor = 1.0)
			error = rt.TMath.Sqrt(content) if content > 0 else 0
			scaled_hist.SetBinError(ibin, error)
	
	return scaled_hist

legend_POT_string = " Events Per "+str(targetpot)+" POT"

# Define variables to plot
variables = {
	'neutrino_energy': {
		'var': 'numuIncCC_reco_nu_energy',
		'nbins': 20,
		'xmin': 0.0,
		'xmax': 2.0,
		'title': plot_title+'; Reconstructed Neutrino Energy (GeV); '+legend_POT_string,
		'has_overflow': True,
		'cut_suffix': ''  # No additional cut
	},
	'muon_momentum': {
		'var': 'numuIncCC_reco_muon_momentum',
		'nbins': 25,
		'xmin': 0.0,
		'xmax': 1.5,
		'title': plot_title+'; Reconstructed Muon Momentum (GeV); '+legend_POT_string,
		'cut_suffix': '&& (numuIncCC_reco_muon_momentum>0)'  # Valid momentum only
	},
	'muon_costheta': {
		'var': 'numuIncCC_reco_muon_costheta',
		'nbins': 20,
		'xmin': -1.0,
		'xmax': 1.0,
		'title': plot_title+'; Reconstructed Muon cos(#theta); '+legend_POT_string,
		'cut_suffix': '&& (numuIncCC_reco_muon_costheta>-900)'  # Valid cos(theta) only
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
				hist.Sumw2()  # Enable error calculation
			
			# print(f"Filling {hname} with cut: {full_cut}")
			
			# For neutrino energy: manually handle overflow by adjusting values > 2.0 to be exactly 2.0
			if var_name == 'neutrino_energy':
				# Create a temporary histogram to capture all events including overflow
				temp_hist = rt.TH1D(hname+"_temp", "", 1000, 0, 10)  # Large range to capture all events
				temp_hist.Sumw2()  # Enable error calculation for temp histogram
				trees[sample].Draw(f"{var_info['var']}>>{hname}_temp", f"({full_cut})*eventweight_weight", "goff")
				
				# Now fill the actual histogram, forcing overflow values into the last bin
				for ibin in range(1, temp_hist.GetNbinsX() + 1):
					bin_content = temp_hist.GetBinContent(ibin)
					bin_error = temp_hist.GetBinError(ibin)
					if bin_content > 0:
						energy_val = temp_hist.GetBinCenter(ibin)
						
						# If energy > 2.0, put it in the overflow (last bin)
						if energy_val >= 2.0:
							hist.Fill(1.99, bin_content)  # Fill just below 2.0 to ensure it goes in last bin
						else:
							hist.Fill(energy_val, bin_content)
			
			# For electron momentum: manually handle overflow by adjusting values > 1.5 to be exactly 1.5
			elif var_name == 'electron_momentum':
				# Create a temporary histogram to capture all events including overflow
				temp_hist = rt.TH1D(hname+"_temp", "", 1000, 0, 10)  # Large range to capture all events
				temp_hist.Sumw2()
				trees[sample].Draw(f"{var_info['var']}>>{hname}_temp", f"({full_cut})*eventweight_weight", "goff")
				
				# Now fill the actual histogram, forcing overflow values into the last bin
				for ibin in range(1, temp_hist.GetNbinsX() + 1):
					bin_content = temp_hist.GetBinContent(ibin)
					if bin_content > 0:
						momentum_val = temp_hist.GetBinCenter(ibin)
						
						# If momentum >= 1.5, put it in the overflow (last bin)
						if momentum_val >= 1.5:
							hist.Fill(1.49, bin_content)  # Fill just below 1.5 to ensure it goes in last bin
						else:
							hist.Fill(momentum_val, bin_content)
			
			# For cos theta: manually handle underflow by adjusting values < -1.0 to be exactly -1.0
			elif var_name == 'electron_costheta':
				# Create a temporary histogram to capture all events including underflow
				temp_hist = rt.TH1D(hname+"_temp", "", 1000, -2, 2)  # Wide range to capture all events
				temp_hist.Sumw2()
				trees[sample].Draw(f"{var_info['var']}>>{hname}_temp", f"({full_cut})*eventweight_weight", "goff")
				
				# Now fill the actual histogram, forcing underflow values into the first bin
				for ibin in range(1, temp_hist.GetNbinsX() + 1):
					bin_content = temp_hist.GetBinContent(ibin)
					if bin_content > 0:
						costheta_val = temp_hist.GetBinCenter(ibin)
						
						# If costheta < 0.375 (first bin upper edge), put it in the underflow (first bin)
						if costheta_val < 0.375:
							hist.Fill(0.0, bin_content)  # Fill at 0.0 to ensure it goes in first bin
						else:
							hist.Fill(costheta_val, bin_content)
			
			else:
				# Standard filling for other variables
				trees[sample].Draw(f"{var_info['var']}>>{hname}", f"({full_cut})*eventweight_weight", "goff")

			# Scale by POT/exposure using the improved scaling function
			scaled_hist = scale_histogram_with_correct_errors(hist, scaling[sample])
			hist = scaled_hist  # Replace original with properly scaled version
			
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

	# Create total MC histogram for uncertainty calculation with proper error handling
	h_total_mc = None
	for cat_name in stack_order:
		if cat_name in hists and cat_name != 'data':
			hstack.Add(hists[cat_name])
			if h_total_mc is None:
				h_total_mc = hists[cat_name].Clone(f"h_total_mc_{var_name}")
				h_total_mc.Sumw2()  # Ensure error calculation is enabled
			else:
				h_total_mc.Add(hists[cat_name])

	# Create uncertainty histogram with blue hatching and proper error calculation
	h_uncertainty = None
	if h_total_mc is not None:
		h_uncertainty = h_total_mc.Clone(f"h_uncertainty_{var_name}")
		
		# The uncertainty histogram will show the statistical uncertainty of the total MC prediction
		# When histograms with Sumw2() are added together, ROOT automatically calculates
		# the error as sqrt(sum of squares of individual bin errors), which is correct
		# for independent statistical uncertainties
		
		# Verify that errors are properly calculated
		for ibin in range(1, h_uncertainty.GetNbinsX() + 1):
			content = h_uncertainty.GetBinContent(ibin)
			error = h_uncertainty.GetBinError(ibin)
			
			# For debugging: print bin info for neutrino energy plot
			if var_name == 'neutrino_energy' and ibin <= 5:  # Only print first few bins
				print(f"Uncertainty hist bin {ibin}: content={content:.3f}, error={error:.3f}")
			
			# The error should be the quadrature sum of errors from all MC components
			# ROOT handles this automatically when adding histograms with Sumw2() enabled
			# No manual calculation needed unless there are issues
		
		h_uncertainty.SetFillColor(rt.kGray+1)
		h_uncertainty.SetFillStyle(3002)  # Hatched pattern
		h_uncertainty.SetLineColor(rt.kGray+1)
		h_uncertainty.SetLineWidth(1)
		h_uncertainty.SetMarkerSize(0)

	# Draw histograms
	stack_max = hstack.GetMaximum() if hstack.GetHists() else 0
	data_max = hists['data'].GetMaximum() if 'data' in hists else 0

	# Set y-axis maximum - use fixed value for neutrino energy, calculated for others
	# if var_name == 'neutrino_energy' and 'y_max' in var_info:
	# 	y_max = var_info['y_max']
	# else:
	y_max = max(stack_max, data_max) * 1.4

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
		y_pos = -500.0  # Position below x-axis ## TODO: fix this 
		
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

print("\nSaved to", out_name)

out.Close()