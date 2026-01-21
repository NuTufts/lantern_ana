#!/usr/bin/env python3
"""
MicroBooNE Run3b Analysis Plotting Script
Creates histograms from overlay files using selection cuts and CC/NC flags
Then loads systematic uncertainties from covariance files
"""

import numpy as np
import matplotlib.pyplot as plt
import uproot
import awkward as ak
from pathlib import Path
from typing import Dict, Tuple, Optional
import re

# ============================================================================
# MicroBooNE Standard Colors and Labels
# ============================================================================
SAMPLE_COLORS = {
    'cc_nue': '#4292c6',      # Blue for νe CC
    'cc_numu': '#ef6548',     # Red/orange for νμ CC  
    'nc_nue': '#41ab5d',      # Green for νe NC
    'nc_numu': '#807dba',     # Purple for νμ NC
    'bnb_ext': '#252525'      # Dark gray for EXT
}

SAMPLE_LABELS = {
    'cc_nue': r'$\nu_e$ CC',
    'cc_numu': r'$\nu_\mu$ CC',
    'nc_nue': r'$\nu_e$ NC',
    'nc_numu': r'$\nu_\mu$ NC',
    'bnb_ext': 'BNB EXT'
}

# Stack order (bottom to top)
STACK_ORDER = ['bnb_ext', 'nc_numu', 'nc_nue', 'cc_numu', 'cc_nue']


# ============================================================================
# Data Structures
# ============================================================================
class HistogramData:
    """Container for histogram data and uncertainties"""
    def __init__(self, bin_edges, bin_contents, stat_errors=None):
        self.bin_edges = np.array(bin_edges)
        self.bin_contents = np.array(bin_contents)
        self.bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        self.bin_widths = bin_edges[1:] - bin_edges[:-1]
        
        if stat_errors is None:
            self.stat_errors = np.sqrt(np.maximum(bin_contents, 0))
        else:
            self.stat_errors = np.array(stat_errors)
        
        # Systematic uncertainties by source
        self.flux_errors = np.zeros_like(bin_contents)
        self.xsec_errors = np.zeros_like(bin_contents)
        self.reint_errors = np.zeros_like(bin_contents)
        self.detector_errors = np.zeros_like(bin_contents)
    
    def total_uncertainty(self):
        """Combine all uncertainties in quadrature"""
        return np.sqrt(
            self.stat_errors**2 + 
            self.flux_errors**2 + 
            self.xsec_errors**2 + 
            self.reint_errors**2 +
            self.detector_errors**2
        )
    
    def systematic_uncertainty(self):
        """Combine only systematic uncertainties in quadrature"""
        return np.sqrt(
            self.flux_errors**2 + 
            self.xsec_errors**2 + 
            self.reint_errors**2 +
            self.detector_errors**2
        )


# ============================================================================
# Helper Functions
# ============================================================================
def identify_systematic_type(syst_name: str) -> str:
    """Identify if systematic is flux, xsec, or reinteraction based on name"""
    syst_lower = syst_name.lower()
    
    # Flux keywords
    flux_keywords = ['flux', 'horn', 'beam', 'kminus', 'kplus', 'kzero', 
                     'piminus', 'piplus', 'nucleon', 'expskin']
    
    # Reinteraction keywords
    reint_keywords = ['reint', 'fsi', 'absorption', 'charge_exchange', 
                     'elastic', 'inelastic', 'pion_prod']
    
    # Check flux first
    for keyword in flux_keywords:
        if keyword in syst_lower:
            return 'flux'
    
    # Check reinteraction
    for keyword in reint_keywords:
        if keyword in syst_lower:
            return 'reint'
    
    return 'xsec'


def apply_cuts(tree_dict: Dict, cut_string: str) -> np.ndarray:
    """Apply selection cuts to tree dictionary"""
    # Replace {ntuple.var} with tree_dict['var']
    eval_string = cut_string
    
    # Find all {ntuple.variable_name} patterns
    pattern = r'\{ntuple\.([^}]+)\}'
    matches = re.findall(pattern, cut_string)
    
    # Build evaluation dictionary
    eval_dict = {}
    for var in matches:
        if var in tree_dict:
            eval_dict[var] = tree_dict[var]
            eval_string = eval_string.replace(f'{{ntuple.{var}}}', f'eval_dict["{var}"]')
        else:
            print(f"Warning: Variable {var} not found in tree")
            return np.ones(len(tree_dict[list(tree_dict.keys())[0]]), dtype=bool)
    
    # Evaluate the cut string
    try:
        mask = eval(eval_string)
        return np.array(mask)
    except Exception as e:
        print(f"Error evaluating cuts: {e}")
        return np.ones(len(tree_dict[list(tree_dict.keys())[0]]), dtype=bool)


def create_histogram_from_tree(filename: str, tree_name: str, variable: str,
                               bins: np.ndarray, cut_string: str,
                               cc_flag: str, nc_flag: str,
                               sample_type: str,
                               pot_scale: float = 1.0,
                               weight_branch: str = None) -> HistogramData:
    """
    Create histogram from TTree with cuts and CC/NC categorization
    
    Parameters:
    -----------
    filename : str
        ROOT file path
    tree_name : str
        TTree name
    variable : str
        Variable to histogram
    bins : np.ndarray
        Bin edges
    cut_string : str
        Selection cuts
    cc_flag : str
        Name of CC flag branch
    nc_flag : str
        Name of NC flag branch  
    sample_type : str
        'cc_nue', 'cc_numu', 'nc_nue', 'nc_numu'
    pot_scale : float
        POT scaling factor
    weight_branch : str
        Name of event weight branch (optional)
    """
    try:
        with uproot.open(filename) as f:
            tree = f[tree_name]
            
            # Get list of all branches we need
            needed_branches = [variable, cc_flag, nc_flag]
            
            # Extract variable names from cut string
            pattern = r'\{ntuple\.([^}]+)\}'
            cut_vars = re.findall(pattern, cut_string)
            needed_branches.extend(cut_vars)
            
            # Add weight branch if specified
            if weight_branch:
                needed_branches.append(weight_branch)
            
            # Remove duplicates
            needed_branches = list(set(needed_branches))
            
            # Load branches
            arrays = tree.arrays(needed_branches, library='ak')
            
            # Convert to dict for easier access
            tree_dict = {branch: ak.to_numpy(ak.flatten(arrays[branch], axis=None)) 
                        for branch in needed_branches}
            
            # Apply selection cuts
            cut_mask = apply_cuts(tree_dict, cut_string)
            
            # Get CC and NC flags
            is_cc = tree_dict[cc_flag].astype(bool)
            is_nc = tree_dict[nc_flag].astype(bool)
            
            # Apply sample-specific masks
            if sample_type == 'cc_nue':
                sample_mask = cut_mask & is_cc
            elif sample_type == 'cc_numu':
                sample_mask = cut_mask & is_cc
            elif sample_type == 'nc_nue':
                sample_mask = cut_mask & is_nc
            elif sample_type == 'nc_numu':
                sample_mask = cut_mask & is_nc
            else:
                sample_mask = cut_mask
            
            # Get variable values for selected events
            var_values = tree_dict[variable][sample_mask]
            
            # Get event weights
            if weight_branch and weight_branch in tree_dict:
                weights = tree_dict[weight_branch][sample_mask] * pot_scale
            else:
                weights = np.ones(len(var_values)) * pot_scale
            
            # Create histogram
            hist, _ = np.histogram(var_values, bins=bins, weights=weights)
            
            # Calculate statistical errors
            hist_var, _ = np.histogram(var_values, bins=bins, weights=weights**2)
            stat_errors = np.sqrt(hist_var)
            
            return HistogramData(bins, hist, stat_errors)
    
    except Exception as e:
        print(f"  Error creating histogram: {e}")
        import traceback
        traceback.print_exc()
        raise


def load_histogram_from_file(filename: str, histname: str, pot_scale: float = 1.0) -> HistogramData:
    """Load pre-made histogram from ROOT file (for EXT, data, or systematics)"""
    try:
        with uproot.open(filename) as f:
            hist = f[histname]
            bin_edges = hist.axis().edges()
            bin_contents = hist.values() * pot_scale
            stat_errors = np.sqrt(hist.variances()) * pot_scale
            
            return HistogramData(bin_edges, bin_contents, stat_errors)
    except Exception as e:
        print(f"  Error loading {histname}: {e}")
        raise


def load_systematics_from_covar(covar_file: str, variable: str, sample: str) -> Tuple:
    """
    Load systematic uncertainties from covariance file
    
    Returns: (flux_errors, xsec_errors, reint_errors)
    """
    if not Path(covar_file).exists():
        print(f"  Warning: Covariance file not found: {covar_file}")
        return None, None, None
    
    try:
        with uproot.open(covar_file) as f:
            # Look for histogram matching pattern: {variable}_{sample}
            hist_pattern = f"{variable}_{sample}"
            
            # Initialize variance arrays
            flux_var = None
            xsec_var = None
            reint_var = None
            
            # Find all variance histograms
            for key in f.keys():
                key_str = key.split(';')[0]
                
                # Check if this is a variance histogram for our variable and sample
                if hist_pattern in key_str and 'variance' in key_str.lower():
                    # Extract systematic name
                    # Expected format: variable_sample_variance_systname
                    parts = key_str.split('_')
                    
                    # Find the variance index
                    try:
                        var_idx = [i for i, p in enumerate(parts) if 'variance' in p.lower()][0]
                        syst_name = '_'.join(parts[var_idx+1:])
                        
                        # Load variance
                        var_hist = f[key_str]
                        variance = var_hist.values()
                        
                        # Categorize
                        syst_type = identify_systematic_type(syst_name)
                        
                        if syst_type == 'flux':
                            if flux_var is None:
                                flux_var = np.zeros_like(variance)
                            flux_var += variance
                            
                        elif syst_type == 'xsec':
                            if xsec_var is None:
                                xsec_var = np.zeros_like(variance)
                            xsec_var += variance
                            
                        elif syst_type == 'reint':
                            if reint_var is None:
                                reint_var = np.zeros_like(variance)
                            reint_var += variance
                    
                    except Exception as e:
                        continue
            
            # Convert variances to errors
            flux_err = np.sqrt(flux_var) if flux_var is not None else None
            xsec_err = np.sqrt(xsec_var) if xsec_var is not None else None
            reint_err = np.sqrt(reint_var) if reint_var is not None else None
            
            return flux_err, xsec_err, reint_err
    
    except Exception as e:
        print(f"  Error loading systematics: {e}")
        return None, None, None


def load_all_samples(nu_overlay: str, nue_overlay: str, ext_file: str,
                    tree_name: str, variable: str, bins: np.ndarray,
                    cuts_nu: str, cuts_nue: str, pot_scales: Dict,
                    nu_covar: str, nue_covar: str,
                    cc_flag: str = 'nueIncCC_is_charge_current',
                    nc_flag: str = 'nueIncCC_is_neutral_current',
                    weight_branch: str = None) -> Dict[str, HistogramData]:
    """Load all samples from Run3b files"""
    
    samples = {}
    
    print(f"\nCreating histograms for: {variable}")
    print("=" * 70)
    print(f"Bins: {len(bins)-1} bins from {bins[0]:.1f} to {bins[-1]:.1f}")
    
    # CC numu from nu overlay (with nue removal cut)
    if 'cc_numu' in STACK_ORDER:
        print(f"\ncc_numu:")
        print(f"  File: {Path(nu_overlay).name}")
        print(f"  Applying nu selection cuts (removes true nue CC)")
        print(f"  POT scale: {pot_scales['cc_numu']:.6f}")
        
        try:
            samples['cc_numu'] = create_histogram_from_tree(
                nu_overlay, tree_name, variable, bins,
                cuts_nu, cc_flag, nc_flag, 'cc_numu',
                pot_scales['cc_numu'], weight_branch
            )
            print(f"  Events: {samples['cc_numu'].bin_contents.sum():.2f}")
            
            # Load systematics
            flux_err, xsec_err, reint_err = load_systematics_from_covar(
                nu_covar, variable, 'cc_numu'
            )
            if flux_err is not None:
                n_bins = len(samples['cc_numu'].bin_contents)
                samples['cc_numu'].flux_errors = flux_err[:n_bins] * pot_scales['cc_numu']
                samples['cc_numu'].xsec_errors = xsec_err[:n_bins] * pot_scales['cc_numu']
                samples['cc_numu'].reint_errors = reint_err[:n_bins] * pot_scales['cc_numu']
                print(f"  Systematics loaded")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # NC numu from nu overlay
    if 'nc_numu' in STACK_ORDER:
        print(f"\nnc_numu:")
        print(f"  File: {Path(nu_overlay).name}")
        print(f"  Applying nu selection cuts")
        print(f"  POT scale: {pot_scales['nc_numu']:.6f}")
        
        try:
            samples['nc_numu'] = create_histogram_from_tree(
                nu_overlay, tree_name, variable, bins,
                cuts_nu, cc_flag, nc_flag, 'nc_numu',
                pot_scales['nc_numu'], weight_branch
            )
            print(f"  Events: {samples['nc_numu'].bin_contents.sum():.2f}")
            
            # Load systematics
            flux_err, xsec_err, reint_err = load_systematics_from_covar(
                nu_covar, variable, 'nc_numu'
            )
            if flux_err is not None:
                n_bins = len(samples['nc_numu'].bin_contents)
                samples['nc_numu'].flux_errors = flux_err[:n_bins] * pot_scales['nc_numu']
                samples['nc_numu'].xsec_errors = xsec_err[:n_bins] * pot_scales['nc_numu']
                samples['nc_numu'].reint_errors = reint_err[:n_bins] * pot_scales['nc_numu']
                print(f"  Systematics loaded")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # CC nue from nue overlay
    if 'cc_nue' in STACK_ORDER:
        print(f"\ncc_nue:")
        print(f"  File: {Path(nue_overlay).name}")
        print(f"  Applying nue selection cuts (keep all)")
        print(f"  POT scale: {pot_scales['cc_nue']:.6f}")
        
        try:
            samples['cc_nue'] = create_histogram_from_tree(
                nue_overlay, tree_name, variable, bins,
                cuts_nue, cc_flag, nc_flag, 'cc_nue',
                pot_scales['cc_nue'], weight_branch
            )
            print(f"  Events: {samples['cc_nue'].bin_contents.sum():.2f}")
            
            # Load systematics
            flux_err, xsec_err, reint_err = load_systematics_from_covar(
                nue_covar, variable, 'cc_nue'
            )
            if flux_err is not None:
                n_bins = len(samples['cc_nue'].bin_contents)
                samples['cc_nue'].flux_errors = flux_err[:n_bins] * pot_scales['cc_nue']
                samples['cc_nue'].xsec_errors = xsec_err[:n_bins] * pot_scales['cc_nue']
                samples['cc_nue'].reint_errors = reint_err[:n_bins] * pot_scales['cc_nue']
                print(f"  Systematics loaded")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # NC nue from nue overlay
    if 'nc_nue' in STACK_ORDER:
        print(f"\nnc_nue:")
        print(f"  File: {Path(nue_overlay).name}")
        print(f"  Applying nue selection cuts")
        print(f"  POT scale: {pot_scales['nc_nue']:.6f}")
        
        try:
            samples['nc_nue'] = create_histogram_from_tree(
                nue_overlay, tree_name, variable, bins,
                cuts_nue, cc_flag, nc_flag, 'nc_nue',
                pot_scales['nc_nue'], weight_branch
            )
            print(f"  Events: {samples['nc_nue'].bin_contents.sum():.2f}")
            
            # Load systematics
            flux_err, xsec_err, reint_err = load_systematics_from_covar(
                nue_covar, variable, 'nc_nue'
            )
            if flux_err is not None:
                n_bins = len(samples['nc_nue'].bin_contents)
                samples['nc_nue'].flux_errors = flux_err[:n_bins] * pot_scales['nc_nue']
                samples['nc_nue'].xsec_errors = xsec_err[:n_bins] * pot_scales['nc_nue']
                samples['nc_nue'].reint_errors = reint_err[:n_bins] * pot_scales['nc_nue']
                print(f"  Systematics loaded")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # EXT from ext file
    if 'bnb_ext' in STACK_ORDER:
        print(f"\nbnb_ext:")
        print(f"  File: {Path(ext_file).name}")
        print(f"  Trigger scale: {pot_scales['bnb_ext']:.6f}")
        
        try:
            # EXT might be a pre-made histogram or needs to be created from tree
            # Try histogram first (most likely for EXT)
            try:
                hist_name = f"{variable}_bnb_ext"
                samples['bnb_ext'] = load_histogram_from_file(
                    ext_file, hist_name, pot_scales['bnb_ext']
                )
                print(f"  Loaded from histogram: {hist_name}")
            except:
                # Try without suffix
                try:
                    samples['bnb_ext'] = load_histogram_from_file(
                        ext_file, variable, pot_scales['bnb_ext']
                    )
                    print(f"  Loaded from histogram: {variable}")
                except:
                    # If neither work, try to create from tree
                    print(f"  Creating from tree...")
                    samples['bnb_ext'] = create_histogram_from_tree(
                        ext_file, tree_name, variable, bins,
                        cuts_nue,  # Use same cuts as nue
                        cc_flag, nc_flag, 'bnb_ext',
                        pot_scales['bnb_ext'], weight_branch
                    )
            
            print(f"  Events: {samples['bnb_ext'].bin_contents.sum():.2f}")
            
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    return samples


# ============================================================================
# Plotting Functions
# ============================================================================
def plot_stacked_histogram(samples: Dict[str, HistogramData],
                          data_hist: HistogramData = None,
                          xlabel: str = "Variable",
                          ylabel: str = "Events",
                          title: str = "",
                          output_file: str = "stacked_plot.pdf",
                          show_ratio: bool = False,
                          xlim: Tuple[float, float] = None):
    """Create stacked histogram with uncertainty band"""
    
    fig_height = 8 if show_ratio else 6
    fig, axes = plt.subplots(
        2 if show_ratio else 1, 
        1, 
        figsize=(10, fig_height),
        gridspec_kw={'height_ratios': [3, 1]} if show_ratio else None,
        sharex=True if show_ratio else False
    )
    
    if show_ratio:
        ax_main, ax_ratio = axes
    else:
        ax_main = axes
    
    # Get bin information
    bin_edges = list(samples.values())[0].bin_edges
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    
    # Prepare stacked histogram data
    stack_contents = []
    stack_colors = []
    stack_labels = []
    
    total_mc = np.zeros(len(bin_centers))
    total_mc_var = np.zeros(len(bin_centers))
    
    for sample in STACK_ORDER:
        if sample not in samples:
            continue
        
        hist_data = samples[sample]
        stack_contents.append(hist_data.bin_contents)
        stack_colors.append(SAMPLE_COLORS[sample])
        stack_labels.append(SAMPLE_LABELS[sample])
        
        total_mc += hist_data.bin_contents
        total_mc_var += hist_data.total_uncertainty()**2
    
    total_mc_error = np.sqrt(total_mc_var)
    
    # Plot stacked histogram
    ax_main.hist(
        [bin_centers for _ in stack_contents],
        bins=bin_edges,
        weights=stack_contents,
        stacked=True,
        color=stack_colors,
        label=stack_labels,
        histtype='stepfilled',
        edgecolor='black',
        linewidth=0.5
    )
    
    # Add uncertainty band
    ax_main.fill_between(
        bin_edges,
        np.concatenate([[total_mc[0] - total_mc_error[0]], 
                        total_mc - total_mc_error]),
        np.concatenate([[total_mc[0] + total_mc_error[0]], 
                        total_mc + total_mc_error]),
        step='pre',
        alpha=0.3,
        color='gray',
        label='Total Uncertainty',
        linewidth=0
    )
    
    # Plot data if provided
    if data_hist is not None:
        ax_main.errorbar(
            bin_centers,
            data_hist.bin_contents,
            yerr=data_hist.stat_errors,
            fmt='ko',
            markersize=6,
            label='BNB Data',
            capsize=3,
            linewidth=1.5
        )
    
    # Formatting
    ax_main.set_ylabel(ylabel, fontsize=14)
    if title:
        ax_main.set_title(title, fontsize=16, pad=10)
    
    if not show_ratio:
        ax_main.set_xlabel(xlabel, fontsize=14)
    
    ax_main.legend(loc='best', fontsize=11, frameon=True)
    ax_main.grid(True, alpha=0.3, linestyle='--')
    
    if xlim:
        ax_main.set_xlim(xlim)
    
    # MicroBooNE label
    ax_main.text(
        0.05, 0.95, 
        'MicroBooNE Preliminary',
        transform=ax_main.transAxes,
        fontsize=12,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )
    
    # Ratio plot
    if show_ratio and data_hist is not None:
        ratio = np.divide(
            data_hist.bin_contents, 
            total_mc,
            out=np.ones_like(data_hist.bin_contents),
            where=total_mc > 0
        )
        ratio_error = np.divide(
            data_hist.stat_errors,
            total_mc,
            out=np.zeros_like(data_hist.stat_errors),
            where=total_mc > 0
        )
        
        ax_ratio.errorbar(
            bin_centers,
            ratio,
            yerr=ratio_error,
            fmt='ko',
            markersize=6,
            capsize=3,
            linewidth=1.5
        )
        
        # Uncertainty band on ratio
        mc_frac_error = np.divide(
            total_mc_error,
            total_mc,
            out=np.zeros_like(total_mc_error),
            where=total_mc > 0
        )
        
        ax_ratio.fill_between(
            bin_edges,
            np.concatenate([[1 - mc_frac_error[0]], 1 - mc_frac_error]),
            np.concatenate([[1 + mc_frac_error[0]], 1 + mc_frac_error]),
            step='pre',
            alpha=0.3,
            color='gray',
            linewidth=0
        )
        
        ax_ratio.axhline(y=1, color='black', linestyle='--', linewidth=1)
        ax_ratio.set_xlabel(xlabel, fontsize=14)
        ax_ratio.set_ylabel('Data / MC', fontsize=12)
        ax_ratio.set_ylim([0.5, 1.5])
        ax_ratio.grid(True, alpha=0.3, linestyle='--')
        
        if xlim:
            ax_ratio.set_xlim(xlim)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nSaved: {output_file}")
    plt.close()


def plot_fractional_uncertainties(samples: Dict[str, HistogramData],
                                  xlabel: str = "Variable",
                                  title: str = "",
                                  output_file: str = "fractional_uncertainties.png",
                                  xlim: Tuple[float, float] = None):
    """Plot fractional uncertainties as stacked areas"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get bin information
    bin_edges = list(samples.values())[0].bin_edges
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    
    # Calculate total MC and uncertainties
    total_mc = np.zeros(len(bin_centers))
    total_stat_var = np.zeros(len(bin_centers))
    total_flux_var = np.zeros(len(bin_centers))
    total_xsec_var = np.zeros(len(bin_centers))
    total_reint_var = np.zeros(len(bin_centers))
    total_detector_var = np.zeros(len(bin_centers))
    
    for sample in STACK_ORDER:
        if sample not in samples:
            continue
        
        hist_data = samples[sample]
        total_mc += hist_data.bin_contents
        total_stat_var += hist_data.stat_errors**2
        total_flux_var += hist_data.flux_errors**2
        total_xsec_var += hist_data.xsec_errors**2
        total_reint_var += hist_data.reint_errors**2
        total_detector_var += hist_data.detector_errors**2
    
    # Calculate fractional uncertainties
    def safe_divide(num, denom):
        return np.divide(num, denom, out=np.zeros_like(num), where=denom > 0)
    
    frac_stat = safe_divide(np.sqrt(total_stat_var), total_mc) * 100
    frac_flux = safe_divide(np.sqrt(total_flux_var), total_mc) * 100
    frac_xsec = safe_divide(np.sqrt(total_xsec_var), total_mc) * 100
    frac_reint = safe_divide(np.sqrt(total_reint_var), total_mc) * 100
    frac_detector = safe_divide(np.sqrt(total_detector_var), total_mc) * 100
    
    # Total uncertainty (in quadrature, not linear sum!)
    total_var = total_stat_var + total_flux_var + total_xsec_var + total_reint_var + total_detector_var
    frac_total = safe_divide(np.sqrt(total_var), total_mc) * 100
    
    # Create stacked area plot
    # Start with statistical (bottom)
    stack_bottom = np.zeros_like(frac_stat)
    
    # Plot statistical
    ax.fill_between(bin_centers, stack_bottom, frac_stat,
                    label='Statistical', color='#969696', alpha=0.8, step='mid')
    stack_bottom = frac_stat.copy()
    
    # Add flux
    if frac_flux.sum() > 0:
        ax.fill_between(bin_centers, stack_bottom, stack_bottom + frac_flux,
                        label='Flux', color='#e41a1c', alpha=0.8, step='mid')
        stack_bottom += frac_flux
    
    # Add cross section
    if frac_xsec.sum() > 0:
        ax.fill_between(bin_centers, stack_bottom, stack_bottom + frac_xsec,
                        label='Cross Section', color='#377eb8', alpha=0.8, step='mid')
        stack_bottom += frac_xsec
    
    # Add reinteraction
    if frac_reint.sum() > 0:
        ax.fill_between(bin_centers, stack_bottom, stack_bottom + frac_reint,
                        label='Reinteraction', color='#ff7f00', alpha=0.8, step='mid')
        stack_bottom += frac_reint
    
    # Add detector if present
    if frac_detector.sum() > 0:
        ax.fill_between(bin_centers, stack_bottom, stack_bottom + frac_detector,
                        label='Detector', color='#4daf4a', alpha=0.8, step='mid')
        stack_bottom += frac_detector
    
    # Plot total uncertainty as a line (shows it's added in quadrature, not linearly)
    ax.plot(bin_centers, frac_total, 'k-', linewidth=2.5, 
            label='Total (quadrature)', zorder=10)
    
    # Add text box explaining quadrature sum
    textstr = r'Total = $\sqrt{\mathrm{stat}^2 + \mathrm{flux}^2 + \mathrm{xsec}^2 + \mathrm{reint}^2}$'
    ax.text(0.98, 0.98, textstr, transform=ax.transAxes,
            fontsize=10, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel('Fractional Uncertainty (%)', fontsize=14)
    if title:
        ax.set_title(title, fontsize=16, pad=10)
    
    ax.legend(loc='upper left', fontsize=11, frameon=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    if xlim:
        ax.set_xlim(xlim)
    
    # Set y limit to show everything clearly
    y_max = max(frac_total.max(), stack_bottom.max()) * 1.2
    ax.set_ylim([0, y_max])
    
    # MicroBooNE label
    ax.text(
        0.05, 0.98,
        'MicroBooNE Preliminary',
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def print_event_summary(samples: Dict[str, HistogramData], 
                       data_hist: Optional[HistogramData] = None):
    """Print summary of events by sample"""
    print("\n" + "="*70)
    print("EVENT SUMMARY")
    print("="*70)
    
    total_mc = 0.0
    total_mc_stat = 0.0
    total_mc_sys = 0.0
    
    for sample in STACK_ORDER:
        if sample not in samples:
            continue
        
        hist_data = samples[sample]
        n_events = hist_data.bin_contents.sum()
        stat_unc = np.sqrt((hist_data.stat_errors**2).sum())
        sys_unc = np.sqrt((hist_data.systematic_uncertainty()**2).sum())
        
        total_mc += n_events
        total_mc_stat += stat_unc**2
        total_mc_sys += sys_unc**2
        
        print(f"{SAMPLE_LABELS[sample]:15s}: {n_events:8.2f} ± {stat_unc:6.2f} (stat) ± {sys_unc:6.2f} (sys)")
    
    total_mc_stat = np.sqrt(total_mc_stat)
    total_mc_sys = np.sqrt(total_mc_sys)
    
    print("-" * 70)
    print(f"{'Total MC':15s}: {total_mc:8.2f} ± {total_mc_stat:6.2f} (stat) ± {total_mc_sys:6.2f} (sys)")
    
    if data_hist is not None:
        n_data = data_hist.bin_contents.sum()
        stat_data = np.sqrt(n_data)
        print(f"{'Data':15s}: {n_data:8.0f} ± {stat_data:6.2f} (stat)")
        print(f"{'Data/MC':15s}: {n_data/total_mc:8.4f}")
    
    print("="*70 + "\n")


# ============================================================================
# Main Analysis
# ============================================================================
if __name__ == "__main__":
    
    # ========================================================================
    # CONFIGURATION
    # ========================================================================
    
    # Target POT for normalization
    TARGET_POT = 5e19
    
    # ==================== RUN3B FILES ====================
    NU_OVERLAY_FILE = "/exp/uboone/app/users/imani/lantern_ana/run3_mmr/root_files/selection/run3b_bnb_nu_overlay_20260112_154048.root"
    NUE_OVERLAY_FILE = "/exp/uboone/app/users/imani/lantern_ana/run3_mmr/root_files/selection/run3b_bnb_nue_overlay_20260112_155555.root"
    EXT_FILE = "/exp/uboone/app/users/imani/lantern_ana/run3_mmr/root_files/selection/run3b_extbnb_20260112_160141.root"
    DATA_FILE = "/exp/uboone/app/users/imani/lantern_ana/run3_mmr/root_files/selection/run3b_data_20260112_175802.root"
    
    # ==================== POT VALUES ====================
    NU_OVERLAY_POT = 8.98323351831587e+20
    NUE_OVERLAY_POT = 4.702159572049976e+22
    EXT_TRIGGERS = 1.23  # Trigger ratio
    DATA_POT = 5e19
    
    # ==================== COVARIANCE FILES ====================
    NU_COVAR_FILE = "/exp/uboone/app/users/imani/lantern_ana/run3_mmr/root_files/xsecflux/run3b_nue_covar_nu.root"
    NUE_COVAR_FILE = "/exp/uboone/app/users/imani/lantern_ana/run3_mmr/root_files/xsecflux/run3b_nue_covar_nue.root"
    
    # ==================== DETECTOR SYSTEMATICS ====================
    USE_DETECTOR_SYSTEMATICS = False
    
    # ==================== TREE AND BRANCH NAMES ====================
    TREE_NAME = "analysis_tree"  # TTree name in overlay files
    CC_FLAG = "nueIncCC_is_charge_current"
    NC_FLAG = "nueIncCC_is_neutral_current"
    WEIGHT_BRANCH = None  # Set to weight branch name if available
    
    # ==================== OUTPUT DIRECTORY ====================
    OUTPUT_DIR = "./plots"
    
    # ==================== SELECTION CUTS ====================
    CUTS_NUE = """{ntuple.nueIncCC_passes_all_cuts}==1"""
    
    CUTS_NU = """{ntuple.nueIncCC_passes_all_cuts}==1 and
                    {ntuple.remove_true_nue_cc_flag}!=1"""
    
    # ==================== VARIABLES TO PLOT ====================
    VARIABLES = {
        'visible_energy': {
            'bins': np.linspace(0, 3000, 31),  # 30 bins, 0-3000 MeV
            'xlabel': 'Visible Energy (MeV)',
            'ylabel': 'Events / 100 MeV',
            'title': '',
            'xlim': (0, 3000),
            'output_prefix': 'visible_energy'
        },
        'vertex_properties_recoEnuMeV': {
            'bins': np.linspace(0, 3000, 31),  # 30 bins
            'xlabel': r'Reconstructed $E_\nu$ (MeV)',
            'ylabel': 'Events / 100 MeV',
            'title': '',
            'xlim': (0, 3000),
            'output_prefix': 'reco_neutrino_energy'
        },
        'nueIncCC_reco_electron_momentum': {
            'bins': np.linspace(0, 1.5, 16),  # 15 bins, 0-1.5 GeV
            'xlabel': r'Reconstructed Electron Momentum (GeV/c)',
            'ylabel': 'Events / 0.1 GeV/c',
            'title': '',
            'xlim': (0, 1.5),
            'output_prefix': 'reco_electron_energy'
        },
        'nueIncCC_reco_electron_costheta': {
            'bins': np.linspace(-1, 1, 21),  # 20 bins
            'xlabel': r'Reconstructed $\cos\theta$',
            'ylabel': 'Events / 0.1',
            'title': '',
            'xlim': (-1, 1),
            'output_prefix': 'reco_cos_theta'
        },
    }
    
    # ==================== PLOT OPTIONS ====================
    SHOW_RATIO = True
    MAKE_FRACTIONAL_PLOTS = True
    
    # ========================================================================
    # END CONFIGURATION
    # ========================================================================
    
    # Create output directory if it doesn't exist
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    
    # Calculate POT scaling factors
    pot_scales = {
        'cc_nue': TARGET_POT / NUE_OVERLAY_POT,
        'nc_nue': TARGET_POT / NUE_OVERLAY_POT,
        'cc_numu': TARGET_POT / NU_OVERLAY_POT,
        'nc_numu': TARGET_POT / NU_OVERLAY_POT,
        'bnb_ext': EXT_TRIGGERS,
    }
    
    print("="*70)
    print("MicroBooNE Run3b Analysis Plotting")
    print("="*70)
    print(f"Target POT: {TARGET_POT:.2e}")
    print(f"Nu overlay POT: {NU_OVERLAY_POT:.2e}")
    print(f"Nue overlay POT: {NUE_OVERLAY_POT:.2e}")
    print(f"EXT trigger ratio: {EXT_TRIGGERS:.4f}")
    print("\nPOT Scaling Factors:")
    for sample, scale in pot_scales.items():
        print(f"  {sample:12s}: {scale:.6e}")
    
    # Load data if provided
    data_hist_dict = {}
    if DATA_FILE and Path(DATA_FILE).exists():
        print(f"\nData file available: {Path(DATA_FILE).name}")
        # Will load data for each variable
    
    # Loop over variables and create plots
    for var_name, var_config in VARIABLES.items():
        print("\n" + "="*70)
        print(f"Processing: {var_name}")
        print("="*70)
        
        # Load all samples for this variable
        try:
            samples = load_all_samples(
                NU_OVERLAY_FILE,
                NUE_OVERLAY_FILE,
                EXT_FILE,
                TREE_NAME,
                var_name,
                var_config['bins'],
                CUTS_NU,
                CUTS_NUE,
                pot_scales,
                NU_COVAR_FILE,
                NUE_COVAR_FILE,
                CC_FLAG,
                NC_FLAG,
                WEIGHT_BRANCH
            )
        except Exception as e:
            print(f"❌ Error loading samples for {var_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        if not samples:
            print(f"❌ No samples loaded for {var_name}, skipping")
            continue
        
        # Try to load data
        data_hist = None
        if DATA_FILE and Path(DATA_FILE).exists():
            try:
                # Try pre-made histogram first
                try:
                    hist_name = f"{var_name}_data"
                    data_hist = load_histogram_from_file(DATA_FILE, hist_name, 1.0)
                    print(f"\nLoaded data from histogram: {hist_name}")
                except:
                    # Try without suffix
                    try:
                        data_hist = load_histogram_from_file(DATA_FILE, var_name, 1.0)
                        print(f"\nLoaded data from histogram: {var_name}")
                    except:
                        # Create from tree
                        print(f"\nCreating data from tree...")
                        data_hist = create_histogram_from_tree(
                            DATA_FILE, TREE_NAME, var_name, var_config['bins'],
                            CUTS_NUE, CC_FLAG, NC_FLAG, 'data', 1.0, WEIGHT_BRANCH
                        )
                
                print(f"Data: {data_hist.bin_contents.sum():.0f} events")
            except Exception as e:
                print(f"\n⚠️  Could not load data: {e}")
                import traceback
                traceback.print_exc()
        
        # Print event summary
        print_event_summary(samples, data_hist)
        
        # Create stacked histogram
        output_stacked = Path(OUTPUT_DIR) / f"{var_config['output_prefix']}_stacked.png"
        plot_stacked_histogram(
            samples,
            data_hist=data_hist,
            xlabel=var_config['xlabel'],
            ylabel=var_config['ylabel'],
            title=var_config['title'],
            output_file=str(output_stacked),
            show_ratio=SHOW_RATIO and data_hist is not None,
            xlim=var_config['xlim']
        )
        
        # Create fractional uncertainty plot
        if MAKE_FRACTIONAL_PLOTS:
            output_frac = Path(OUTPUT_DIR) / f"{var_config['output_prefix']}_fractional_uncertainties.png"
            plot_fractional_uncertainties(
                samples,
                xlabel=var_config['xlabel'],
                title=var_config['title'],
                output_file=str(output_frac),
                xlim=var_config['xlim']
            )
    
    print("\n" + "="*70)
    print("✓ All plots completed successfully!")
    print("="*70)
    print(f"\nPlots saved to: {OUTPUT_DIR}/")
    print("\nOutput files:")
    for var_config in VARIABLES.values():
        print(f"  - {var_config['output_prefix']}_stacked.png")
        if MAKE_FRACTIONAL_PLOTS:
            print(f"  - {var_config['output_prefix']}_fractional_uncertainties.png")