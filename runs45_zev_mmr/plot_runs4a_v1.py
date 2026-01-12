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
    
    Args:
        covar_file: Path to xsecflux ROOT file
        var_name: Variable name (e.g., 'visible_energy', 'reco_neutrino_energy')
        dataset_name: Dataset name (e.g., 'run4a_nu')
        nbins: Number of bins
        systematics_to_include: List of systematic names to include (None = all)
    
    Returns:
        sys_errors: Array of combined systematic uncertainties per bin
        individual_errors: Dict of individual systematic errors for breakdown
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
                print(f"  Including systematic: {syst_name}")
    
    if not variance_hists:
        print(f"Available keys in file:")
        f.ls()
        f.Close()
        raise ValueError(f"No variance histograms found for {var_name}, {dataset_name}")
    
    # Initialize arrays
    total_variance = np.zeros(nbins)
    individual_errors = {}
    
    # Sum variances in quadrature
    for syst_name, hist in variance_hists.items():
        syst_variance = np.zeros(nbins)
        for i in range(nbins):
            var = hist.GetBinContent(i+1)
            syst_variance[i] = max(0, var)  # Ensure non-negative
        
        # Store individual systematic error
        individual_errors[syst_name] = np.sqrt(syst_variance)
        
        # Add to total variance
        total_variance += syst_variance
    
    # Total systematic error
    sys_errors = np.sqrt(total_variance)
    
    f.Close()
    return sys_errors, individual_errors

def plot_with_systematics(analysis_file, covar_file, branch_name, 
                          var_name_in_covar, dataset_name,
                          nbins=30, xmin=0.0, xmax=3000.0,
                          cut_string="",
                          output_name="plot_with_errors.png",
                          pot_scale=1.0,
                          xlabel=None,
                          title=None,
                          systematics_to_include=None):
    """
    Plot histogram from tree branch with statistical and systematic error bands
    
    Args:
        analysis_file: Path to analysis ROOT file with TTree
        covar_file: Path to xsecflux covariance ROOT file
        branch_name: Name of branch in analysis tree (e.g., 'visible_energy')
        var_name_in_covar: Name used in covariance file (e.g., 'visible_energy')
        dataset_name: Dataset name in covariance file (e.g., 'run4a_nu')
        nbins, xmin, xmax: Histogram binning
        cut_string: Optional cut to apply
        output_name: Output plot filename
        pot_scale: POT scaling factor
        xlabel: X-axis label
        title: Plot title
        systematics_to_include: List of systematics to include (None = all)
    """
    
    # Open analysis file and get tree
    f_analysis = ROOT.TFile.Open(analysis_file, "READ")
    tree = f_analysis.Get("analysis_tree")
    
    if not tree:
        raise ValueError("Could not find analysis_tree")
    
    # Create histogram from tree
    print(f"Creating histogram from branch: {branch_name}")
    h_nominal = create_histogram_from_tree(tree, branch_name, nbins, xmin, xmax, 
                                           cut_string=cut_string)
    
    # Get histogram properties
    bin_edges = np.array([h_nominal.GetBinLowEdge(i+1) for i in range(nbins+1)])
    bin_centers = np.array([h_nominal.GetBinCenter(i+1) for i in range(nbins)])
    
    # Get bin contents and statistical errors
    nominal_values = np.array([h_nominal.GetBinContent(i+1) * pot_scale for i in range(nbins)])
    stat_errors = np.array([h_nominal.GetBinError(i+1) * pot_scale for i in range(nbins)])
    
    # Get systematic uncertainties
    print(f"\nReading systematic uncertainties from: {covar_file}")
    sys_errors, individual_errors = get_combined_xsecflux_uncertainties(
        covar_file, var_name_in_covar, dataset_name, nbins, systematics_to_include
    )
    
    # Combine errors in quadrature
    total_errors = np.sqrt(stat_errors**2 + sys_errors**2)
    
    # Calculate fractional errors (avoid division by zero)
    mask = nominal_values > 0
    frac_stat = np.zeros(nbins)
    frac_sys = np.zeros(nbins)
    frac_total = np.zeros(nbins)
    frac_stat[mask] = stat_errors[mask] / nominal_values[mask]
    frac_sys[mask] = sys_errors[mask] / nominal_values[mask]
    frac_total[mask] = total_errors[mask] / nominal_values[mask]
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), 
                                     gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.05})
    
    # Top panel: Histogram with error bands
    ax1.hist(bin_centers, bins=bin_edges, weights=nominal_values, 
             histtype='step', color='black', linewidth=2, label='Nominal')
    
    # Add systematic error band
    ax1.fill_between(bin_edges[:-1], 
                     nominal_values - sys_errors, 
                     nominal_values + sys_errors,
                     step='post', alpha=0.3, color='blue', 
                     label='Systematic uncertainty')
    
    # Add total error band
    ax1.fill_between(bin_edges[:-1], 
                     nominal_values - total_errors, 
                     nominal_values + total_errors,
                     step='post', alpha=0.2, color='red', 
                     label='Total uncertainty')
    
    ax1.set_ylabel('Events', fontsize=14)
    ax1.legend(fontsize=12, loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Add title if provided
    if title:
        ax1.set_title(title, fontsize=16, pad=10)
    
    # Bottom panel: Fractional errors as stacked line histogram
    # Create step histogram for each component
    ax2.step(bin_edges[:-1], frac_stat, where='post', 
             color='green', linewidth=2, label='Stat. frac. error')
    ax2.step(bin_edges[:-1], frac_sys, where='post', 
             color='blue', linewidth=2, label='Sys. frac. error')
    ax2.step(bin_edges[:-1], frac_total, where='post', 
             color='red', linewidth=2, label='Total frac. error')
    
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
    print(f"\nSaved plot to {output_name}")
    
    # Print summary statistics
    print(f"\nSummary for {branch_name}:")
    print(f"Total events: {np.sum(nominal_values):.2f}")
    if np.any(mask):
        print(f"Average stat. fractional error: {np.mean(frac_stat[mask]):.3f}")
        print(f"Average sys. fractional error: {np.mean(frac_sys[mask]):.3f}")
        print(f"Average total fractional error: {np.mean(frac_total[mask]):.3f}")
    
    # Print individual systematic contributions
    print(f"\nIndividual systematic contributions (averaged over bins with events):")
    for syst_name in sorted(individual_errors.keys()):
        avg_frac_err = np.mean(individual_errors[syst_name][mask] / nominal_values[mask]) if np.any(mask) else 0
        print(f"  {syst_name:40s}: {avg_frac_err:.4f}")
    
    f_analysis.Close()
    plt.close()

# Example usage
if __name__ == "__main__":
    
    # Paths to your files
    analysis_file = "/exp/uboone/app/users/imani/lantern_ana/runs45_zev_mmr/nue_raw_root/run4a_v10_04_07_13_BNB_nue_overlay_surprise.root"
    covar_file = "/exp/uboone/app/users/imani/lantern_ana/studies/xsecfluxsys/xsecflux_run4a_nu.root"
    
    # Plot visible energy
    plot_with_systematics(
        analysis_file=analysis_file,
        covar_file=covar_file,
        branch_name="visible_energy",
        var_name_in_covar="visible_energy",
        dataset_name="run4a_nu",
        nbins=30,
        xmin=0.0,
        xmax=3000.0,
        output_name="visible_energy_with_systematics.png",
        xlabel="Visible Energy [MeV]",
        title="Visible Energy with Systematic Uncertainties"
    )
    
    # Plot reco neutrino energy
    plot_with_systematics(
        analysis_file=analysis_file,
        covar_file=covar_file,
        branch_name="vertex_properties_recoEnuMeV",
        var_name_in_covar="reco_neutrino_energy",
        dataset_name="run4a_nu",
        nbins=30,
        xmin=0.0,
        xmax=3000.0,
        output_name="reco_neutrino_energy_with_systematics.png",
        xlabel="Reconstructed Neutrino Energy [MeV]",
        title="Reconstructed Neutrino Energy with Systematic Uncertainties"
    )