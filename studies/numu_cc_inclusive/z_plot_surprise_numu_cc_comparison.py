import os, sys
import ROOT as rt

# Enable proper error bars
rt.TH1.SetDefaultSumw2(rt.kTRUE)

# Define target POT
targetpot = 1.32e21

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
        'truth_cut': ' && (numuIncCC_is_nc_interaction==1)',
        'color': rt.kGray,    # Light gray
        'fill_style': 1001,   # Solid fill
        'legend': 'NC #nu_{e}'
    },
    'cc_nue': {
        'samples': ['nue'], 
        'truth_cut': ' && (numuIncCC_is_cc_interaction==1)',
        'color': rt.kRed,     # Red
        'fill_style': 1001,   # Solid fill
        'legend': 'CC #nu_{e}'
    },
    'nc_numu': {
        'samples': ['numu'],
        'truth_cut': ' && (numuIncCC_is_nc_interaction==1)', 
        'color': rt.kGreen+1, # Green
        'fill_style': 1001,   # Solid fill
        'legend': 'NC #nu_{#mu}'
    },
    'cc_numu': {
        'samples': ['numu'],
        'truth_cut': ' && (numuIncCC_is_cc_interaction==1)',
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
        'cut_suffix': ' && (numuIncCC_reco_muon_momentum>0)'  # Valid momentum only
    },
    'muon_costheta': {
        'var': 'numuIncCC_reco_muon_costheta',
        'nbins': 20,
        'xmin': -1.0,
        'xmax': 1.0,
        'title': 'Inclusive CC #nu_{#mu} Selected Events; Reconstructed Muon cos(#theta); Events',
        'cut_suffix': ' && (numuIncCC_reco_muon_costheta>-900)'  # Valid cos(theta) only
    }
}

# Define scaling factors for each sample
scaling = {
    "numu": targetpot/7.881656209241413e+20,
    "nue": targetpot/1.0696499342682672e+22,
    "data": targetpot/5.843739138271457e+20,
    "extbnb": 0.47809891*0.80,
}

# Define file paths for each sample
files = {
    "numu": "./output_numu_run4b/run4b_bnb_nu_overlay_surprise.root",
    "nue": "./output_nue_run4b/run4b_bnb_nue_overlay.root",  # You'll need to add this
    "data": "./output_numu_run4b/run3b_bnb_nu_overlay_500k_CV.root",
    "extbnb": "./output_numu_run4b/run1_extbnb_mcc9_v29e_C1.root",
}

# Open files and get trees
tfiles = {}
trees = {}

rt.gStyle.SetOptStat(0)

# Get all unique samples from categories
all_samples = set()
for cat_info in categories.values():
    all_samples.update(cat_info['samples'])

print(f"Looking for samples: {all_samples}")
print(f"Available files: {list(files.keys())}")

for sample in all_samples:
    if sample in files:
        if os.path.exists(files[sample]):
            tfiles[sample] = rt.TFile(files[sample])
            if tfiles[sample].IsZombie():
                print(f"Error: File {files[sample]} is corrupted or cannot be opened")
                continue
            trees[sample] = tfiles[sample].Get("analysis_tree")
            if not trees[sample]:
                print(f"Error: Cannot find 'analysis_tree' in file {files[sample]}")
                continue
            nentries = trees[sample].GetEntries()
            print(f"sample={sample} has {nentries} entries")
        else:
            print(f"Warning: File {files[sample]} does not exist, skipping sample {sample}")
    else:
        print(f"Warning: No file path specified for sample {sample}")

# Create output file
out = rt.TFile("stacked_plots_output.root", "recreate")

# Base selection cuts
base_cut = "vertex_properties_found==1"
base_cut += " && muon_properties_pid_score>-1.0"
base_cut += " && vertex_properties_infiducial==1"

# Storage for histograms and canvases
hists = {}
canvs = {}

# Loop over variables to plot
for var_name, var_info in variables.items():
    print(f"Processing variable: {var_name}")
    
    # Create canvas
    cname = f"c_{var_name}"
    canvs[var_name] = rt.TCanvas(cname, var_info['title'], 1200, 800)
    canvs[var_name].Draw()
    
    # Create histograms for each category
    hstack = rt.THStack(f"hs_{var_name}", "")
    legend = rt.TLegend(0.65, 0.65, 0.88, 0.88)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    
    # Process categories in order (background first, data last)
    category_order = ['cosmic', 'nc_nue', 'cc_nue', 'nc_numu', 'cc_numu', 'data']
    
    data_hist = None
    
    for cat_name in category_order:
        if cat_name not in categories:
            continue
            
        cat_info = categories[cat_name]
        
        # Create combined histogram for this category
        hname = f"h_{var_name}_{cat_name}"
        hist = rt.TH1D(hname, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
        
        # Fill histogram from all samples in this category
        total_entries = 0
        for sample in cat_info['samples']:
            if sample not in trees:
                print(f"Warning: Sample {sample} not found, skipping")
                continue
                
            # Build the full cut string
            full_cut = base_cut + var_info['cut_suffix'] + cat_info['truth_cut']
            
            # Create temporary histogram for this sample
            temp_hname = f"temp_{var_name}_{sample}_{cat_name}"
            temp_hist = rt.TH1D(temp_hname, "", var_info['nbins'], var_info['xmin'], var_info['xmax'])
            
            # Fill the temporary histogram
            draw_string = f"{var_info['var']}>>{temp_hname}"
            weight_string = f"({full_cut})*eventweight_weight"
            
            print(f"  Filling {cat_name} from {sample}")
            print(f"    Draw: {draw_string}")
            print(f"    Cut: {weight_string}")
            
            n_drawn = trees[sample].Draw(draw_string, weight_string, "goff")
            entries_before_scale = temp_hist.Integral()
            
            # Scale by POT
            if sample in scaling:
                temp_hist.Scale(scaling[sample])
                entries_after_scale = temp_hist.Integral()
                print(f"    Entries drawn: {n_drawn}, Before scale: {entries_before_scale:.2f}, After scale: {entries_after_scale:.2f}")
            else:
                print(f"    Warning: No scaling factor for sample {sample}")
                entries_after_scale = entries_before_scale
                print(f"    Entries drawn: {n_drawn}, Integral: {entries_after_scale:.2f}")
            
            # Add to category histogram
            hist.Add(temp_hist)
            total_entries += entries_after_scale
            
            # Clean up temporary histogram
            temp_hist.Delete()
        
        print(f"  Total entries for {cat_name}: {total_entries:.2f}")
        
        # Configure histogram appearance
        hist.SetFillColor(cat_info['color'])
        hist.SetLineColor(cat_info['color'])
        hist.SetFillStyle(cat_info['fill_style'])
        
        # Handle data separately (points, not stacked)
        if cat_name == 'data':
            hist.SetLineColor(rt.kBlack)
            hist.SetMarkerColor(rt.kBlack)
            hist.SetMarkerStyle(20)
            hist.SetFillStyle(0)
            data_hist = hist
            legend.AddEntry(hist, cat_info['legend'], "lep")
        else:
            # Add to stack for MC
            if hist.Integral() > 0:
                hstack.Add(hist)
                legend.AddEntry(hist, cat_info['legend'], "f")
        
        # Store histogram
        hists[(var_name, cat_name)] = hist
    
    # Check if stack has any histograms before drawing
    if hstack.GetNhists() > 0:
        # Draw the stack
        hstack.Draw("hist")
        hstack.SetTitle(var_info['title'])
        
        # Set y-axis range
        max_val = hstack.GetMaximum()
        if data_hist and data_hist.GetMaximum() > max_val:
            max_val = data_hist.GetMaximum()
        
        hstack.GetYaxis().SetRangeUser(0, max_val * 1.2)
    else:
        # If no histograms in stack, just draw data if available
        if data_hist and data_hist.Integral() > 0:
            data_hist.Draw("E1")
            data_hist.SetTitle(var_info['title'])
            max_val = data_hist.GetMaximum()
            data_hist.GetYaxis().SetRangeUser(0, max_val * 1.2)
        else:
            # Create empty histogram for axis
            empty_hist = rt.TH1D(f"empty_{var_name}", var_info['title'], 
                               var_info['nbins'], var_info['xmin'], var_info['xmax'])
            empty_hist.Draw()
            print(f"Warning: No data found for variable {var_name}")
    
    # Draw data on top if it exists
    if data_hist and data_hist.Integral() > 0:
        data_hist.Draw("E1 same")
    
    # Draw legend
    legend.Draw()
    
    # Update canvas
    canvs[var_name].Update()
    
    # Store the stack
    hists[(var_name, 'stack')] = hstack

# Write everything to output file
out.Write()
print(f"Plots saved to: stacked_plots_output.root")

# Clean up
out.Close()

print("Plotting complete!")