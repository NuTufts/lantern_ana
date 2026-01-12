import ROOT
import numpy as np
import matplotlib.pyplot as plt

def create_histogram_from_tree(tree, branch_name, nbins, xmin, xmax, 
                                cut_string="", weight_branch="eventweight_weight"):
    """
    Create histogram from tree branch with optional cuts and weights
    """
    hist = ROOT.TH1D(f"h_{branch_name}", "", nbins, xmin, xmax)
    hist.Sumw2()
    
    if cut_string:
        draw_string = f"{branch_name}>>h_{branch_name}"
        tree.Draw(draw_string, f"({cut_string})*{weight_branch}", "goff")
    else:
        draw_string = f"{branch_name}>>h_{branch_name}"
        tree.Draw(draw_string, weight_branch, "goff")
    
    return hist

def get_combined_xsecflux_uncertainties(covar_file, var_name, dataset_name, nbins,
                                        systematics_to_include=None):
    """
    Extract and combine systematic uncertainties from individual variance histograms
    """
    f = ROOT.TFile.Open(covar_file, "READ")
    
    # Pattern for variance histograms: h<var>__<dataset>__<syst>_variance
    variance_pattern = f"h{var_name}__{dataset_name}__"
    
    # Find all variance histograms
    variance_hists = {}
    keys = f.GetListOfKeys()
    
    for key in keys:
        name = key.GetName()
        if variance_pattern in name and "_variance" in name:
            # Extract systematic name
            syst_name = name.replace(variance_pattern, "").replace("_variance", "")
            
            # Check if we should include this systematic
            if systematics_to_include is None or syst_name in systematics_to_include:
                variance_hists[syst_name] = f.Get(name)
    
    if not variance_hists:
        print(f"Available keys in file:")
        f.ls()
        f.Close()
        raise ValueError(f"No variance histograms found for {var_name}, {dataset_name}")
    
    # Initialize arrays
    total_variance = np.zeros(nbins)
    
    # Sum variances in quadrature
    for syst_name, hist in variance_hists.items():
        for i in range(nbins):
            var = hist.GetBinContent(i+1)
            total_variance[i] += max(0, var)
    
    # Total systematic error
    sys_errors = np.sqrt(total_variance)
    
    f.Close()
    return sys_errors

def plot_stacked_with_systematics(samples, branch_name, var_name_in_covar,
                                   nbins=30, xmin=0.0, xmax=3000.0,
                                   output_name="plot_stacked.png",
                                   xlabel=None,
                                   title=None,
                                   systematics_to_include=None):
    """
    Plot stacked histogram with combined systematic uncertainties
    
    Args:
        samples: List of dicts with keys:
            - 'analysis_file': Path to analysis ROOT file
            - 'covar_file': Path to covariance ROOT file
            - 'dataset_name': Dataset name in covariance file
            - 'label': Legend label
            - 'color': Histogram color
            - 'pot_scale': POT scaling factor
            - 'cut_string': Optional additional cuts for this sample
            - 'include_uncertainties': If False, don't include this sample's uncertainties (default True)
        branch_name: Branch to plot
        var_name_in_covar: Variable name in covariance files
        nbins, xmin, xmax: Histogram binning
        output_name: Output filename
        xlabel: X-axis label
        title: Plot title
        systematics_to_include: List of systematics to include
    """
    
    # Storage for all samples
    all_nominal = []
    all_stat_errors = []
    all_sys_errors = []
    all_labels = []
    all_colors = []
    all_include_uncert = []
    
    bin_edges = None
    
    # Process each sample
    for sample in samples:
        print(f"\n{'='*60}")
        print(f"Processing sample: {sample['label']}")
        print(f"{'='*60}")
        
        # Open analysis file
        f_analysis = ROOT.TFile.Open(sample['analysis_file'], "READ")
        tree = f_analysis.Get("analysis_tree")
        
        if not tree:
            raise ValueError(f"Could not find analysis_tree in {sample['analysis_file']}")
        
        # Get cut string for this sample
        cut_string = sample.get('cut_string', "")
        if cut_string:
            print(f"Applying cuts: {cut_string[:100]}...")
        
        # Create histogram
        print(f"Creating histogram from branch: {branch_name}")
        h_nominal = create_histogram_from_tree(tree, branch_name, nbins, xmin, xmax, 
                                               cut_string=cut_string)
        
        # Get bin edges (should be same for all samples)
        if bin_edges is None:
            bin_edges = np.array([h_nominal.GetBinLowEdge(i+1) for i in range(nbins+1)])
        
        # Get bin contents and statistical errors
        pot_scale = sample.get('pot_scale', 1.0)
        nominal_values = np.array([h_nominal.GetBinContent(i+1) * pot_scale for i in range(nbins)])
        stat_errors = np.array([h_nominal.GetBinError(i+1) * pot_scale for i in range(nbins)])
        
        # Check if we should include uncertainties for this sample
        include_uncert = sample.get('include_uncertainties', True)
        
        if include_uncert:
            # Get systematic uncertainties
            print(f"Reading systematic uncertainties from: {sample['covar_file']}")
            sys_errors = get_combined_xsecflux_uncertainties(
                sample['covar_file'], var_name_in_covar, sample['dataset_name'], 
                nbins, systematics_to_include
            )
        else:
            print(f"Skipping uncertainties for this sample (include_uncertainties=False)")
            sys_errors = np.zeros(nbins)
            stat_errors = np.zeros(nbins)  # Also zero out stat errors if ignoring uncertainties
        
        # Calculate total error for this sample
        total_errors = np.sqrt(stat_errors**2 + sys_errors**2)
        
        # Calculate fractional errors for this sample
        mask = nominal_values > 0
        frac_stat = np.zeros(nbins)
        frac_sys = np.zeros(nbins)
        frac_total = np.zeros(nbins)
        if include_uncert and np.any(mask):
            frac_stat[mask] = stat_errors[mask] / nominal_values[mask]
            frac_sys[mask] = sys_errors[mask] / nominal_values[mask]
            frac_total[mask] = total_errors[mask] / nominal_values[mask]
        
        # Print individual sample statistics
        print(f"\nSample {sample['label']} statistics:")
        print(f"  Total events: {np.sum(nominal_values):.2f}")
        print(f"  Include uncertainties: {include_uncert}")
        if include_uncert and np.any(mask):
            print(f"  Average stat. fractional error: {np.mean(frac_stat[mask]):.4f}")
            print(f"  Average sys. fractional error: {np.mean(frac_sys[mask]):.4f}")
            print(f"  Average total fractional error: {np.mean(frac_total[mask]):.4f}")
        
        # Store
        all_nominal.append(nominal_values)
        all_stat_errors.append(stat_errors)
        all_sys_errors.append(sys_errors)
        all_labels.append(sample['label'])
        all_colors.append(sample['color'])
        all_include_uncert.append(include_uncert)
        
        f_analysis.Close()
    
    # Calculate stacked totals
    stacked_nominal = np.sum(all_nominal, axis=0)
    
    # Combine errors in quadrature (samples are independent)
    # Only include errors from samples with include_uncertainties=True
    stacked_stat_errors = np.sqrt(np.sum([e**2 for e in all_stat_errors], axis=0))
    stacked_sys_errors = np.sqrt(np.sum([e**2 for e in all_sys_errors], axis=0))
    stacked_total_errors = np.sqrt(stacked_stat_errors**2 + stacked_sys_errors**2)
    
    # Calculate fractional errors
    mask = stacked_nominal > 0
    frac_total = np.zeros(nbins)
    frac_total[mask] = stacked_total_errors[mask] / stacked_nominal[mask]
    
    # Print stacking details
    print(f"\n{'='*60}")
    print("STACKING DIAGNOSTICS:")
    print(f"{'='*60}")
    for i, label in enumerate(all_labels):
        uncert_str = "with uncertainties" if all_include_uncert[i] else "WITHOUT uncertainties"
        print(f"{label}: {np.sum(all_nominal[i]):.2f} events ({uncert_str})")
    print(f"Stacked total: {np.sum(stacked_nominal):.2f} events")
    print(f"\nError breakdown:")
    for i, label in enumerate(all_labels):
        if all_include_uncert[i]:
            avg_frac = np.mean(np.sqrt(all_stat_errors[i]**2 + all_sys_errors[i]**2)[mask] / stacked_nominal[mask]) if np.any(mask) else 0
            print(f"{label} contribution to stacked fractional error: {avg_frac:.4f}")
        else:
            print(f"{label} contribution to stacked fractional error: 0.0000 (ignored)")
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), 
                                     gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.05})
    
    # Top panel: Stacked histogram with error band
    # Plot stacked histogram
    ax1.hist([bin_edges[:-1] for _ in all_nominal], 
             bins=bin_edges, 
             weights=all_nominal,
             histtype='stepfilled',
             stacked=True,
             color=all_colors,
             alpha=0.7,
             label=all_labels,
             edgecolor='black',
             linewidth=1)
    
    # Add total uncertainty band
    ax1.fill_between(bin_edges[:-1], 
                     stacked_nominal - stacked_total_errors, 
                     stacked_nominal + stacked_total_errors,
                     step='post', alpha=0.3, color='gray', 
                     label='Total uncertainty', zorder=10)
    
    ax1.set_ylabel('Events', fontsize=14)
    ax1.legend(fontsize=12, loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Add title if provided
    if title:
        ax1.set_title(title, fontsize=16, pad=10)
    
    # Bottom panel: Total fractional error as line histogram
    ax2.step(bin_edges[:-1], frac_total, where='post', 
             color='black', linewidth=2, label='Total frac. error')
    
    # Set x-axis label
    if xlabel is None:
        xlabel = branch_name.replace('_', ' ').title() + ' [MeV]'
    
    ax2.set_xlabel(xlabel, fontsize=14)
    ax2.set_ylabel('Fractional Error', fontsize=14)
    ax2.legend(fontsize=10, loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    if np.any(mask):
        ax2.set_ylim(0, min(1.0, np.max(frac_total[mask]) * 1.2))
    
    # Match x-axis limits
    ax1.set_xlim(bin_edges[0], bin_edges[-1])
    ax2.set_xlim(bin_edges[0], bin_edges[-1])
    ax1.set_xticklabels([])
    
    plt.tight_layout()
    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    print(f"\n{'='*60}")
    print(f"Saved plot to {output_name}")
    print(f"{'='*60}")
    
    # Print summary statistics
    print(f"\nCombined Summary:")
    print(f"Total stacked events: {np.sum(stacked_nominal):.2f}")
    if np.any(mask):
        print(f"Average stacked fractional error: {np.mean(frac_total[mask]):.4f}")
    
    plt.close()

# Example usage
if __name__ == "__main__":
    
    # Base paths
    analysis_base = "/exp/uboone/app/users/imani/lantern_ana/runs45_zev_mmr/nue_raw_root/"
    covar_base = "/exp/uboone/app/users/imani/lantern_ana/studies/xsecfluxsys/"
    
    # Define MMR cuts (from your YAML config)
    mmr_cuts = ("vertex_properties_infiducial==1 && "
                "vertex_properties_cosmicfrac<1.0 && "
                "recoMuonTrack_nMuTracks==0 && "
                "recoElectron_has_primary_electron==1 && "
                "recoElectron_emax_primary_score>recoElectron_emax_fromcharged_score && "
                "recoElectron_emax_primary_score>recoElectron_emax_fromneutral_score && "
                "recoMuonTrack_max_muscore<-3.7 && "
                "recoElectron_emax_econfidence>7.0")
    
    # Remove true nue CC events from nu sample
    remove_true_nue_cc = "nueCCinc_is_target_nuecc_inclusive_nofvcut!=1"
    
    # Combine cuts for nu sample
    nu_cuts = f"({mmr_cuts}) && ({remove_true_nue_cc})"
    nue_cuts = mmr_cuts
    
    # Define samples
    samples = [
        {
            'analysis_file': analysis_base + "run4a_v10_04_07_13_BNB_nu_overlay_surprise.root",
            'covar_file': covar_base + "xsecflux_run4a_nu.root",
            'dataset_name': "run4a_nu",
            'label': r'$\nu_\mu$ CC',
            'color': 'blue',
            'pot_scale': 1.0,
            'cut_string': nu_cuts,
            'include_uncertainties': False  # Set to False to ignore nu uncertainties
        },
        {
            'analysis_file': analysis_base + "run4a_v10_04_07_13_BNB_nue_overlay_surprise.root",
            'covar_file': covar_base + "xsecflux_run4a_nue.root",
            'dataset_name': "run4a_nue",
            'label': r'$\nu_e$ CC',
            'color': 'red',
            'pot_scale': 1.0,
            'cut_string': nue_cuts,
            'include_uncertainties': True  # Keep nue uncertainties
        }
    ]
    
    # Plot visible energy
    plot_stacked_with_systematics(
        samples=samples,
        branch_name="visible_energy",
        var_name_in_covar="visible_energy",
        nbins=30,
        xmin=0.0,
        xmax=3000.0,
        output_name="visible_energy_stacked.png",
        xlabel="Visible Energy [MeV]",
        title="Run 4a Visible Energy with Systematic Uncertainties"
    )
    
    # Plot reco neutrino energy
    plot_stacked_with_systematics(
        samples=samples,
        branch_name="vertex_properties_recoEnuMeV",
        var_name_in_covar="reco_neutrino_energy",
        nbins=30,
        xmin=0.0,
        xmax=3000.0,
        output_name="reco_neutrino_energy_stacked.png",
        xlabel="Reconstructed Neutrino Energy [MeV]",
        title="Run 4a Reconstructed Neutrino Energy with Systematic Uncertainties"
    )