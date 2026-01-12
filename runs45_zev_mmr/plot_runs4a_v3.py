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
            - 'covar_file': Path to covariance ROOT file (optional for data)
            - 'dataset_name': Dataset name in covariance file (optional for data)
            - 'label': Legend label
            - 'color': Histogram color
            - 'pot_scale': POT scaling factor
            - 'cut_string': Optional additional cuts for this sample
            - 'include_uncertainties': If False, don't include systematic uncertainties (keeps stat errors)
            - 'is_data': If True, treat as data (plot as points, don't stack)
        branch_name: Branch to plot
        var_name_in_covar: Variable name in covariance files
        nbins, xmin, xmax: Histogram binning
        output_name: Output filename
        xlabel: X-axis label
        title: Plot title
        systematics_to_include: List of systematics to include
    """
    
    # Storage for MC samples
    mc_nominal = []
    mc_stat_errors = []
    mc_sys_errors = []
    mc_labels = []
    mc_colors = []
    
    # Storage for data
    data_nominal = None
    data_stat_errors = None
    data_label = None
    
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
        
        # For data, don't use event weights
        is_data = sample.get('is_data', False)
        if is_data:
            h_nominal = create_histogram_from_tree(tree, branch_name, nbins, xmin, xmax, 
                                                   cut_string=cut_string, weight_branch="1")
        else:
            h_nominal = create_histogram_from_tree(tree, branch_name, nbins, xmin, xmax, 
                                                   cut_string=cut_string)
        
        # Get bin edges (should be same for all samples)
        if bin_edges is None:
            bin_edges = np.array([h_nominal.GetBinLowEdge(i+1) for i in range(nbins+1)])
        
        # Get bin contents and statistical errors
        pot_scale = sample.get('pot_scale', 1.0)
        nominal_values = np.array([h_nominal.GetBinContent(i+1) * pot_scale for i in range(nbins)])
        stat_errors = np.array([h_nominal.GetBinError(i+1) * pot_scale for i in range(nbins)])
        
        # Check if we should include systematic uncertainties for this sample
        include_uncert = sample.get('include_uncertainties', True)
        
        if not is_data and include_uncert and 'covar_file' in sample:
            # Get systematic uncertainties for MC
            print(f"Reading systematic uncertainties from: {sample['covar_file']}")
            sys_errors = get_combined_xsecflux_uncertainties(
                sample['covar_file'], var_name_in_covar, sample['dataset_name'], 
                nbins, systematics_to_include
            )
        else:
            sys_errors = np.zeros(nbins)
            if not include_uncert and not is_data:
                print(f"Skipping systematic uncertainties for this sample (stat errors still included)")
        
        # Calculate total error for this sample
        total_errors = np.sqrt(stat_errors**2 + sys_errors**2)
        
        # Calculate fractional errors for this sample
        mask = nominal_values > 0
        frac_total = np.zeros(nbins)
        if np.any(mask):
            frac_total[mask] = total_errors[mask] / nominal_values[mask]
        
        # Print individual sample statistics
        print(f"\nSample {sample['label']} statistics:")
        print(f"  Total events: {np.sum(nominal_values):.2f}")
        print(f"  Is data: {is_data}")
        if not is_data and np.any(mask):
            print(f"  Average fractional stat error: {np.mean(stat_errors[mask]/nominal_values[mask]):.4f}")
            if include_uncert:
                print(f"  Average fractional sys error: {np.mean(sys_errors[mask]/nominal_values[mask]):.4f}")
            print(f"  Average fractional total error: {np.mean(frac_total[mask]):.4f}")
        
        # Store based on type
        if is_data:
            data_nominal = nominal_values
            data_stat_errors = stat_errors
            data_label = sample['label']
        else:
            mc_nominal.append(nominal_values)
            mc_stat_errors.append(stat_errors)
            mc_sys_errors.append(sys_errors)
            mc_labels.append(sample['label'])
            mc_colors.append(sample['color'])
        
        f_analysis.Close()
    
    # Calculate stacked MC totals
    stacked_mc = np.sum(mc_nominal, axis=0)
    
    # Combine MC errors in quadrature
    stacked_stat_errors = np.sqrt(np.sum([e**2 for e in mc_stat_errors], axis=0))
    stacked_sys_errors = np.sqrt(np.sum([e**2 for e in mc_sys_errors], axis=0))
    stacked_total_errors = np.sqrt(stacked_stat_errors**2 + stacked_sys_errors**2)
    
    # Calculate fractional errors for each sample (relative to stacked total)
    mask = stacked_mc > 0
    frac_errors_by_sample = []
    for i in range(len(mc_nominal)):
        sample_total_err = np.sqrt(mc_stat_errors[i]**2 + mc_sys_errors[i]**2)
        frac_err = np.zeros(nbins)
        frac_err[mask] = sample_total_err[mask] / stacked_mc[mask]
        frac_errors_by_sample.append(frac_err)
    
    # Total fractional error
    frac_total = np.zeros(nbins)
    frac_total[mask] = stacked_total_errors[mask] / stacked_mc[mask]
    
    # Print stacking details
    print(f"\n{'='*60}")
    print("STACKING DIAGNOSTICS:")
    print(f"{'='*60}")
    for i, label in enumerate(mc_labels):
        print(f"{label}: {np.sum(mc_nominal[i]):.2f} events")
        if np.any(mask):
            avg_frac = np.mean(frac_errors_by_sample[i][mask])
            print(f"  Avg. fractional contribution to total error: {avg_frac:.4f}")
    print(f"Stacked MC total: {np.sum(stacked_mc):.2f} events")
    if data_nominal is not None:
        print(f"{data_label}: {np.sum(data_nominal):.2f} events")
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), 
                                     gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.05})
    
    # Top panel: Stacked histogram with error band and data
    # Plot stacked MC histogram
    ax1.hist([bin_edges[:-1] for _ in mc_nominal], 
             bins=bin_edges, 
             weights=mc_nominal,
             histtype='stepfilled',
             stacked=True,
             color=mc_colors,
             alpha=0.7,
             label=mc_labels,
             edgecolor='black',
             linewidth=1)
    
    # Add MC uncertainty band
    ax1.fill_between(bin_edges[:-1], 
                     stacked_mc - stacked_total_errors, 
                     stacked_mc + stacked_total_errors,
                     step='post', alpha=0.3, color='gray', 
                     label='MC uncertainty', zorder=10)
    
    # Plot data if available
    if data_nominal is not None:
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        ax1.errorbar(bin_centers, data_nominal, yerr=data_stat_errors,
                    fmt='ko', markersize=5, linewidth=2,
                    label=data_label, zorder=20)
    
    ax1.set_ylabel('Events', fontsize=14)
    ax1.legend(fontsize=12, loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Add title if provided
    if title:
        ax1.set_title(title, fontsize=16, pad=10)
    
    # Bottom panel: Stacked fractional error contributions
    # Create stacked histogram of fractional errors
    ax2.hist([bin_edges[:-1] for _ in frac_errors_by_sample], 
             bins=bin_edges, 
             weights=frac_errors_by_sample,
             histtype='stepfilled',
             stacked=True,
             color=mc_colors,
             alpha=0.7,
             label=[f"{label} error" for label in mc_labels],
             edgecolor='black',
             linewidth=1)
    
    # Add total error line
    ax2.step(bin_edges[:-1], frac_total, where='post', 
             color='black', linewidth=2, linestyle='--', 
             label='Total error', zorder=10)
    
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
    print(f"Total stacked MC: {np.sum(stacked_mc):.2f}")
    if data_nominal is not None:
        print(f"Total data: {np.sum(data_nominal):.2f}")
        print(f"Data/MC ratio: {np.sum(data_nominal)/np.sum(stacked_mc):.3f}")
    if np.any(mask):
        print(f"Average total fractional error: {np.mean(frac_total[mask]):.4f}")
    
    plt.close()

# Example usage
if __name__ == "__main__":
    
    # Base paths
    analysis_base = "/exp/uboone/app/users/imani/lantern_ana/runs45_zev_mmr/nue_raw_root/"
    covar_base = "/exp/uboone/app/users/imani/lantern_ana/studies/xsecfluxsys/"
    
    # POT and trigger information for Run 4a (from getDataInfo.py)
    # You'll need to update these with your actual values
    end1cnt_run4a = 10928307.0  # E1DCNT_wcut for beam on
    pot_run4a = 4.498e+19       # tor875_wcut for beam on
    ext_beamoff = 29875806.0    # EXT for beam off
    
    # MC POT - you'll need to get this from your MC files
    # This should be the total POT in your nu and nue overlay samples
    # mc_pot_nu = 2.3593114985024402e+20   # Example - update with actual value
    # mc_pot_nue = 3.6831120503927822e+22  # Example - update with actual value
    # mc_pot_dirt = 1.088128052604017e+20  # Example - update with actual value
    
    # fake
    mc_pot_nu = 2.3593114985024402e+22   # Example - update with actual value
    mc_pot_nue = 3.6831120503927822e+19  # Example - update with actual value
    mc_pot_dirt = 1.088128052604017e+22  # Example - update with actual value


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
    # nu_cuts = f"({mmr_cuts}) && ({remove_true_nue_cc})"
    nu_cuts = mmr_cuts
    nue_cuts = mmr_cuts
    
    # Define samples (order matters for stacking - bottom to top)
    samples = [
        {
            'analysis_file': analysis_base + "run4a_v10_04_07_13_BNB_nu_overlay_surprise.root",
            'covar_file': covar_base + "xsecflux_run4a_nu.root",
            'dataset_name': "run4a_nu",
            'label': r'$\nu_\mu$ CC (background)',
            'color': 'blue',
            'pot_scale': pot_run4a / mc_pot_nu,
            'cut_string': nu_cuts,
            'include_uncertainties': True,  # Only stat errors (sys errors zeroed)
            'is_data': False
        },
        {
            'analysis_file': analysis_base + "run4a_v10_04_07_13_BNB_nue_overlay_surprise.root",
            'covar_file': covar_base + "xsecflux_run4a_nue.root",
            'dataset_name': "run4a_nue",
            'label': r'$\nu_e$ CC (signal)',
            'color': 'red',
            'pot_scale': pot_run4a / mc_pot_nue,
            'cut_string': nue_cuts,
            'include_uncertainties': True,  # Stat + sys errors
            'is_data': False
        },
        {
            'analysis_file': analysis_base + "run4a_dirt.root",
            'label': 'Dirt',
            'color': 'orange',
            'pot_scale': pot_run4a / mc_pot_dirt,
            'cut_string': mmr_cuts,
            'include_uncertainties': True,  # Only stat errors
            'is_data': False
        },
        {
            'analysis_file': analysis_base + "run4a_extbnb.root",  # Update with actual filename
            'label': 'EXT (beam off)',
            'color': 'gray',
            'pot_scale': end1cnt_run4a / ext_beamoff,
            'cut_string': mmr_cuts,
            'include_uncertainties': True,  # Only stat errors
            'is_data': False  # Treat as MC for stacking
        },
        # {
        #     'analysis_file': analysis_base + "run4a_beamon.root",  # Update with actual filename
        #     'label': 'Data (beam on)',
        #     'color': 'black',
        #     'pot_scale': 1.0,
        #     'cut_string': mmr_cuts,
        #     'is_data': True  # Plot as data points
        # }
    ]
    
    # Plot visible energy
    plot_stacked_with_systematics(
        samples=samples,
        branch_name="visible_energy",
        var_name_in_covar="visible_energy",
        nbins=30,
        xmin=0.0,
        xmax=3000.0,
        output_name="visible_energy_stacked_with_data.png",
        xlabel="Visible Energy [MeV]",
        title="Run 4a Visible Energy"
    )
    
    # Plot reco neutrino energy
    plot_stacked_with_systematics(
        samples=samples,
        branch_name="vertex_properties_recoEnuMeV",
        var_name_in_covar="reco_neutrino_energy",
        nbins=30,
        xmin=0.0,
        xmax=3000.0,
        output_name="reco_neutrino_energy_stacked_with_data.png",
        xlabel="Reconstructed Neutrino Energy [MeV]",
        title="Run 4a Reconstructed Neutrino Energy"
    )