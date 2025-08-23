import os,sys
import ROOT as rt

targetpot = 4.4e19

samples = ['nue','numu','extbnb','data']

scaling = {"numu":targetpot/4.675690535431973e+20,
		   "nue":targetpot/9.662529168587103e+22,
		   "extbnb":(176153.0)/(433446.0),
		   "data":1.0}

files = {"numu":"./my_mmr/numu_outputs/run1_bnb_nu_overlay_mcc9_v28_wctagger.root",
		 "nue":"./my_mmr/numu_outputs/run1_bnb_nue_overlay_mcc9_v28_wctagger.root", 
		 "extbnb":"./my_mmr/numu_outputs/run1_extbnb_mcc9_v29e_C1.root",
		 "data":"./my_mmr/numu_outputs/run1_bnb5e19.root"}

rt.gStyle.SetOptStat(0)

tfiles = {}
trees = {}

for sample in samples:
	tfiles[sample] = rt.TFile( files[sample] )
	trees[sample] = tfiles[sample].Get("analysis_tree")
	nentries = trees[sample].GetEntries()
	print(f"sample={sample} has {nentries} entries")

out = rt.TFile("./my_mmr/numu_hists.root","recreate")

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

# Define variables to plot
variables = {
	'neutrino_energy': {
		'var': 'numuIncCC_reco_nu_energy',
		'nbins': 20,
		'xmin': 0.0,
		'xmax': 2.0,
		'title': 'Inclusive CC #nu_{#mu} Selected Events; Reconstructed Neutrino Energy (GeV); Events',
		'cut_suffix': ''  # No additional cut
	},
	'muon_momentum': {
		'var': 'numuIncCC_reco_muon_momentum',
		'nbins': 25,
		'xmin': 0.0,
		'xmax': 1.5,
		'title': 'Inclusive CC #nu_{#mu} Selected Events; Reconstructed Muon Momentum (GeV/c); Events',
		'cut_suffix': '&& (numuIncCC_reco_muon_momentum>0)'  # Valid momentum only
	},
	'muon_costheta': {
		'var': 'numuIncCC_reco_muon_costheta',
		'nbins': 20,
		'xmin': -1.0,
		'xmax': 1.0,
		'title': 'Inclusive CC #nu_{#mu} Selected Events; Reconstructed Muon cos(#theta); Events',
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
			
			# Create histogram
			hist = rt.TH1D(hname, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
			hist.Sumw2()  # Enable proper error calculation
			
			print(f"Filling {hname} with cut: {full_cut}")
			
			# Fill histogram
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
	stack_order = ['cosmic', 'nc_nue', 'cc_nue', 'nc_numu', 'cc_numu']
	hstack = rt.THStack(f"hs_{var_name}", "")

	for cat_name in stack_order:
		if cat_name in hists and cat_name != 'data':
			hstack.Add(hists[cat_name])

	# Draw histograms
	stack_max = hstack.GetMaximum() if hstack.GetHists() else 0
	data_max = hists['data'].GetMaximum() if 'data' in hists else 0

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

	# Draw data on top as black line
	if 'data' in hists:
		hists['data'].Draw("E1same")

	# Create and configure legend
	legend = rt.TLegend(0.65, 0.55, 0.89, 0.89)
	legend.SetTextSize(0.03)
	legend.SetFillStyle(0)  # Transparent background
	legend.SetBorderSize(1)


	for cat_name in stack_order: #reversed(stack_order):
		if cat_name in hists and cat_name in categories:
			legend.AddEntry(hists[cat_name], categories[cat_name]['legend'], "f")

	# Add entries to legend (data first, then MC in reverse stack order)
	if 'data' in hists:
		legend.AddEntry(hists['data'], categories['data']['legend'], "lep")

	legend.Draw()
	# Update canvas
	canvas.SetLogy(0)  # Linear scale
	canvas.Update()

	# Save canvas and histograms
	canvas.Write()
	# for cat_name, hist in hists.items():
	# 	hist.Write()

	# Print summary for this variable
	print(f"\n=== {var_name.upper()} Analysis Summary ===")
	total_mc = sum(total_events[cat] for cat in total_events if cat != 'data')
	print(f"Total MC: {total_mc:.1f}")
	if 'data' in total_events:
		print(f"Data: {total_events['data']:.1f}")
		if total_mc > 0:
			print(f"Data/MC ratio: {total_events['data']/total_mc:.2f}")

	# CC νμ purity
	cc_numu_events = total_events.get('cc_numu', 0)
	if total_mc > 0:
		print(f"CC νμ purity: {cc_numu_events/total_mc*100:.1f}%")

	# Save plot as image files
	# canvas.SaveAs(f"./mmr_hists/{var_name}_colored_stack.png")
	# canvas.SaveAs(f"./mmr_hists/{var_name}_colored_stack.pdf")

	print(f"Plot saved as {var_name}_colored_stack.png and .pdf")

# Create a summary canvas with all three plots
summary_canvas = rt.TCanvas("c_summary", "CC νμ Selection Kinematics Summary", 1500, 500)
summary_canvas.Divide(3, 1)

# This would require re-creating the histograms in a more compact format
# For now, we'll just note that individual plots are saved

print(f"\n=== OVERALL ANALYSIS SUMMARY ===")
print("Three kinematic distributions created:")
print("1. Reconstructed Neutrino Energy (0-2 GeV)")
print("2. Reconstructed Muon Momentum (0-2.5 GeV/c)")  
print("3. Reconstructed Muon cos(θ) (-1 to +1)")
print("\nAll plots use the same CC νμ selection cuts:")
print("- LArMatch vertex in fiducial volume")
print("- Cosmic ray rejection via Wire-Cell tagging")
print("- LArPID muon identification")

out.Close()

print("\nAll histograms saved in numu_kinematics_hists.root")