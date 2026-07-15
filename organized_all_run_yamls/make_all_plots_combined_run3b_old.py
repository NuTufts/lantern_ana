import os, sys
import ROOT as rt
import array
from math import sqrt

# =============================================================================
# RUN 3 CONFIGURATION
# =============================================================================

run_num = 3  # Run 3b configuration

# Directory paths
lantern_dir = "/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana"

# Target POT for scaling
targetpot = 4.4e19

# Scaling factors (for xsecflux systematics which are at different POT)
xsecflux_pot = 8.98323351831587e+20
scaling_xsecflux = targetpot / xsecflux_pot

# XsecFlux systematics file
xsecflux_file = f"{lantern_dir}/studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux/output_xsecflux_tki_run3b_1mil.root"
xsecflux_sample = "mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil"

# Detector systematics files
detsys_files = [
    f"{lantern_dir}/studies/xsecfluxsys/detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil.root",  # Has 7 params
    f"{lantern_dir}/studies/xsecfluxsys/detsys_cv500k_run3b_bnb_nu_overlay_500k_CV.root"  # Has SCE and recomb2
]

# Output settings
plot_title = "Run 3b: CC Inclusive Numu"
out_name = f"{lantern_dir}/organized_all_run_yamls/plots/numu_run3b_combined_systematics.root"

# Variable names (as they appear in detsys/xsecflux files)
variables = ['delPTT', 'delAlphaT', 'pN', 'muKE', 'maxprotonKE', 'pionKE']

# Variable display properties
var_properties = {
    'delPTT': {'title': '#delta p_{TT} (GeV)', 'xmin': 0.0, 'xmax': 1.0},
    'delAlphaT': {'title': '#delta #alpha_{T} (deg)', 'xmin': 0.0, 'xmax': 180.0},
    'pN': {'title': 'p_{N} (GeV)', 'xmin': 0.0, 'xmax': 1.0},
    'muKE': {'title': 'Muon Kinetic Energy (GeV)', 'xmin': 0.0, 'xmax': 1.0},
    'maxprotonKE': {'title': 'Max Proton Kinetic Energy (GeV)', 'xmin': 0.0, 'xmax': 1.0},
    'pionKE': {'title': 'Pion Kinetic Energy (GeV)', 'xmin': 0.0, 'xmax': 1.0}
}

# =============================================================================
# SYSTEMATICS PARAMETERS
# =============================================================================

# Flux systematics
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

# GENIE cross section systematics
genie_params = [
    "All_UBGenie"
]

# Other cross section systematics
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

# Detector variation parameters (500k file has all 9)
detsys_params = [
    "wiremodX", "wiremodYZ", "wiremodThetaXZ", "wiremodThetaYZ", 
    "LYAtt", "LYDown", "LYRayleigh",
    "recomb2", "SCE"
]

# Combined list of all xsecflux parameters
all_xsecflux_pars = flux_params + genie_params + other_xsec

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def identify_systematic_type(syst_name):
    """Identify if systematic is flux, xsec, or reinteraction based on name"""
    syst_lower = syst_name.lower()
    
    # Flux keywords
    flux_keywords = ['flux', 'horn', 'beam', 'kminus', 'kplus', 'kzero', 
                     'nucleon', 'expskin', 'pion']
    
    # Reinteraction keywords
    reint_keywords = ['reint', 'fsi', 'absorption', 'charge_exchange', 
                     'elastic', 'inelastic', 'pion_prod', 'geant4']
    
    # Check flux first
    for keyword in flux_keywords:
        if keyword in syst_lower:
            return 'flux'
    
    # Check reinteraction
    for keyword in reint_keywords:
        if keyword in syst_lower:
            return 'reint'
    
    # Default to cross section
    return 'xsec'


def load_detector_variations(rfiles, varname, detsys_params):
    """Load detector variation histograms from multiple files and calculate fractional uncertainties"""
    
    detector_hists = {}
    
    # Try to find a CV histogram to get binning (from first file)
    h_reference = None
    for rfile in rfiles:
        if rfile is None or rfile.IsZombie():
            continue
        for param in detsys_params:
            cv_name = f"hnumuCC1piNpReco_{varname}__{param}__cv"
            h_temp = rfile.Get(cv_name)
            if h_temp and not h_temp.IsZombie():
                h_reference = h_temp
                break
        if h_reference:
            break
    
    if h_reference is None:
        print(f"  Warning: Could not find reference histogram for {varname}")
        return None
    
    # Create combined fractional variance histogram
    h_frac_var = h_reference.Clone(f"hnumuCC1piNpReco_{varname}__detector_frac_variance")
    h_frac_var.Reset()
    
    # Process each detector parameter, checking all files
    n_loaded = 0
    for param in detsys_params:
        found = False
        for rfile in rfiles:
            if rfile is None or rfile.IsZombie():
                continue
                
            cv_name = f"hnumuCC1piNpReco_{varname}__{param}__cv"
            var_name = f"hnumuCC1piNpReco_{varname}__{param}__var"
            
            h_cv = rfile.Get(cv_name)
            h_var = rfile.Get(var_name)
            
            if not h_cv or h_cv.IsZombie():
                continue
            
            if not h_var or h_var.IsZombie():
                continue
            
            # Found this parameter in this file
            found = True
            n_loaded += 1
            
            # Calculate fractional variance for this parameter
            for ibin in range(0, h_frac_var.GetNbinsX() + 2):
                cv_val = h_cv.GetBinContent(ibin)
                var_val = h_var.GetBinContent(ibin)
                
                if cv_val > 0:
                    # Fractional difference: (var - cv) / cv
                    frac_diff = (var_val - cv_val) / cv_val
                    # Add squared fractional difference to variance
                    current_var = h_frac_var.GetBinContent(ibin)
                    h_frac_var.SetBinContent(ibin, current_var + frac_diff**2)
            
            break  # Found it in this file, don't check other files
    
    print(f"  Loaded {n_loaded}/{len(detsys_params)} detector variations")
    
    detector_hists['frac_variance'] = h_frac_var
    detector_hists['n_params'] = n_loaded
    
    return detector_hists


def make_hist_w_errors(rfile, varname, sample, parlist):
    """Load histograms and separate into flux, xsec, and reinteraction"""
    hists = {}
    
    # Try to find the CV histogram
    # Format: hnumuCC1piNpReco_delPTT_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_cv (single underscore)
    cv_name = f"hnumuCC1piNpReco_{varname}_{sample}_cv"
    hcv = rfile.Get(cv_name)
    
    if not hcv or hcv.IsZombie():
        print(f"  Warning: Could not find CV histogram {cv_name}")
        return None
    
    print(f"  Found CV histogram: {cv_name}")
    
    # Create variance histograms for each category
    hvar_flux = hcv.Clone(f"h{varname}__{sample}_flux_variance")
    hvar_flux.Reset()
    hvar_xsec = hcv.Clone(f"h{varname}__{sample}_xsec_variance")
    hvar_xsec.Reset()
    hvar_reint = hcv.Clone(f"h{varname}__{sample}_reint_variance")
    hvar_reint.Reset()
    hvar_tot = hcv.Clone(f"h{varname}__{sample}_totvariance")
    hvar_tot.Reset()
    
    hmeans2 = hcv.Clone(f"h{varname}__{sample}_meanofmeans")
    hmeans2.Reset()
    
    n_loaded = 0
    # Process each parameter
    for parname in parlist:
        # Format: hnumuCC1piNpReco_delPTT__mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil__All_UBGenie_variance (DOUBLE underscores)
        var_name = f"hnumuCC1piNpReco_{varname}__{sample}__{parname}_variance"
        mean_name = f"hnumuCC1piNpReco_{varname}__{sample}__{parname}_mean"
        
        hvar = rfile.Get(var_name)
        hmean = rfile.Get(mean_name)
        
        if not hvar or hvar.IsZombie():
            continue
        
        if not hmean or hmean.IsZombie():
            continue
        
        n_loaded += 1
        hists[parname] = hvar
        
        # Identify the type of systematic
        syst_type = identify_systematic_type(parname)
        
        # Add variance to appropriate category
        for ibin in range(0, hvar_tot.GetXaxis().GetNbins()+1):
            xvar = hvar.GetBinContent(ibin)
            xmean = hmean.GetBinContent(ibin)
            
            if xmean > 0:
                scale_factor = hcv.GetBinContent(ibin) / xmean
                cv_var = xvar * scale_factor * scale_factor
            else:
                cv_var = 0.0
            
            # Add to total variance
            xvar_tot = hvar_tot.GetBinContent(ibin)
            hvar_tot.SetBinContent(ibin, xvar_tot + cv_var)
            
            # Add to category-specific variance
            if syst_type == 'flux':
                xvar_flux_bin = hvar_flux.GetBinContent(ibin)
                hvar_flux.SetBinContent(ibin, xvar_flux_bin + cv_var)
            elif syst_type == 'xsec':
                xvar_xsec_bin = hvar_xsec.GetBinContent(ibin)
                hvar_xsec.SetBinContent(ibin, xvar_xsec_bin + cv_var)
            elif syst_type == 'reint':
                xvar_reint_bin = hvar_reint.GetBinContent(ibin)
                hvar_reint.SetBinContent(ibin, xvar_reint_bin + cv_var)
            
            # Add to mean
            xmean2 = hmeans2.GetBinContent(ibin)
            hmeans2.SetBinContent(ibin, xmean2 + xmean/len(parlist))
    
    # Set std for CV error (total only)
    for ibin in range(0, hvar_tot.GetXaxis().GetNbins()+1):
        stddev = sqrt(hvar_tot.GetBinContent(ibin))
        hcv.SetBinError(ibin, stddev)
    
    # Debug: Print summary of systematic counts
    n_flux = sum(1 for p in parlist if identify_systematic_type(p) == 'flux')
    n_xsec = sum(1 for p in parlist if identify_systematic_type(p) == 'xsec')
    n_reint = sum(1 for p in parlist if identify_systematic_type(p) == 'reint')
    print(f"  Loaded {n_loaded}/{len(parlist)} systematics: {n_flux} flux, {n_xsec} xsec, {n_reint} reint")
    
    hists['cv'] = hcv
    hists['mean2'] = hmeans2
    hists['totvar'] = hvar_tot
    hists['fluxvar'] = hvar_flux
    hists['xsecvar'] = hvar_xsec
    hists['reintvar'] = hvar_reint
    
    return hists

# =============================================================================
# MAIN SCRIPT
# =============================================================================

rt.gStyle.SetOptStat(0)

# Create output directory if it doesn't exist
out_dir = os.path.dirname(out_name)
if out_dir and not os.path.exists(out_dir):
    os.makedirs(out_dir)
    print(f"Created output directory: {out_dir}")

print(f"\nOutput file: {out_name}")

# Output file
out = rt.TFile(out_name, "recreate")

# =============================================================================
# LOAD SYSTEMATICS
# =============================================================================

# Load xsecflux uncertainties
print(f"\nLoading xsecflux uncertainties from {xsecflux_file}")
xsecflux_hists = {}
if os.path.exists(xsecflux_file):
    xfile = rt.TFile(xsecflux_file)
    if not xfile.IsZombie():
        for var in variables:
            hists_with_errors = make_hist_w_errors(xfile, var, xsecflux_sample, all_xsecflux_pars)
            if hists_with_errors:
                xsecflux_hists[var] = hists_with_errors
    else:
        print(f"  Warning: Could not open xsecflux file")
else:
    print(f"  Warning: xsecflux file not found")

# Load detector variations
print(f"\nLoading detector variations from multiple files:")
for f in detsys_files:
    print(f"  - {f}")
detsys_hists = {}
dfiles = []
for detsys_file in detsys_files:
    if os.path.exists(detsys_file):
        dfile = rt.TFile(detsys_file)
        if not dfile.IsZombie():
            dfiles.append(dfile)
        else:
            print(f"  Warning: Could not open {detsys_file}")
    else:
        print(f"  Warning: File not found: {detsys_file}")

if dfiles:
    for var in variables:
        det_hists = load_detector_variations(dfiles, var, detsys_params)
        if det_hists:
            detsys_hists[var] = det_hists
else:
    print(f"  Warning: No detector files available")

# =============================================================================
# CREATE PLOTS
# =============================================================================

for var in variables:
    print(f"\n{'='*80}")
    print(f"Creating plots for {var}")
    print(f"{'='*80}")
    
    # Get CV histogram from detsys file (already has correct selection applied)
    # Use first detsys file (1mil) which has the CVCV histogram
    if dfiles and len(dfiles) > 0:
        h_cv = dfiles[0].Get(f"hnumuCC1piNpReco_{var}__CVCV")
        
        if not h_cv or h_cv.IsZombie():
            print(f"  Warning: Could not find CV histogram hnumuCC1piNpReco_{var}__CVCV")
            continue
        
        # Clone for our use
        h_total_mc = h_cv.Clone(f"h_{var}_total_mc")
        print(f"  Loaded CV: {h_total_mc.Integral():.2f} events")
    else:
        print(f"  Error: No detsys files available")
        continue
    
    # Create uncertainty histograms
    h_uncertainty_total = h_total_mc.Clone(f"h_uncertainty_total_{var}")
    h_uncertainty_flux = h_total_mc.Clone(f"h_uncertainty_flux_{var}")
    h_uncertainty_xsec = h_total_mc.Clone(f"h_uncertainty_xsec_{var}")
    h_uncertainty_reint = h_total_mc.Clone(f"h_uncertainty_reint_{var}")
    h_uncertainty_detector = h_total_mc.Clone(f"h_uncertainty_detector_{var}")
    
    # Apply uncertainties bin-by-bin
    for ibin in range(0, h_uncertainty_total.GetNbinsX() + 2):
        central = h_total_mc.GetBinContent(ibin)
        
        if central <= 0:
            h_uncertainty_total.SetBinError(ibin, 0.0)
            h_uncertainty_flux.SetBinError(ibin, 0.0)
            h_uncertainty_xsec.SetBinError(ibin, 0.0)
            h_uncertainty_reint.SetBinError(ibin, 0.0)
            h_uncertainty_detector.SetBinError(ibin, 0.0)
            continue
        
        # Initialize fractional variances
        frac_var_flux = 0.0
        frac_var_xsec = 0.0
        frac_var_reint = 0.0
        frac_var_detector = 0.0
        
        # Get fractional variances from xsecflux
        if var in xsecflux_hists:
            xsec_hists = xsecflux_hists[var]
            
            cv_from_xsecflux = xsec_hists['cv'].GetBinContent(ibin) if 'cv' in xsec_hists else 0.0
            
            if cv_from_xsecflux > 0:
                if 'fluxvar' in xsec_hists:
                    abs_var_flux = xsec_hists['fluxvar'].GetBinContent(ibin)
                    frac_var_flux = abs_var_flux / (cv_from_xsecflux ** 2)
                if 'xsecvar' in xsec_hists:
                    abs_var_xsec = xsec_hists['xsecvar'].GetBinContent(ibin)
                    frac_var_xsec = abs_var_xsec / (cv_from_xsecflux ** 2)
                if 'reintvar' in xsec_hists:
                    abs_var_reint = xsec_hists['reintvar'].GetBinContent(ibin)
                    frac_var_reint = abs_var_reint / (cv_from_xsecflux ** 2)
        
        # Add detector fractional variance
        if var in detsys_hists and 'frac_variance' in detsys_hists[var]:
            frac_var_detector = detsys_hists[var]['frac_variance'].GetBinContent(ibin)
        
        # Statistical fractional uncertainty (use CV bin content as "unscaled")
        frac_var_stat = (1.0 / central) if central > 0 else 0.0
        
        # Total fractional variance (add in quadrature)
        frac_var_total = frac_var_stat + frac_var_flux + frac_var_xsec + frac_var_reint + frac_var_detector
        
        # Convert to absolute errors
        abs_error_total = central * sqrt(frac_var_total)
        abs_error_flux = central * sqrt(frac_var_flux)
        abs_error_xsec = central * sqrt(frac_var_xsec)
        abs_error_reint = central * sqrt(frac_var_reint)
        abs_error_detector = central * sqrt(frac_var_detector)
        
        # Set bin errors
        h_uncertainty_total.SetBinError(ibin, abs_error_total)
        h_uncertainty_flux.SetBinError(ibin, abs_error_flux)
        h_uncertainty_xsec.SetBinError(ibin, abs_error_xsec)
        h_uncertainty_reint.SetBinError(ibin, abs_error_reint)
        h_uncertainty_detector.SetBinError(ibin, abs_error_detector)
    
    # === Create main data/MC comparison canvas ===
    canvas = rt.TCanvas(f"c_{var}", f"{var} Distribution", 1000, 800)
    canvas.Draw()
    canvas.SetTickx(1)
    canvas.SetTicky(1)
    
    # Set histogram style
    h_total_mc.SetFillColor(rt.kAzure+1)
    h_total_mc.SetFillStyle(1001)
    h_total_mc.SetLineColor(rt.kAzure+1)
    h_total_mc.SetLineWidth(1)
    
    var_props = var_properties.get(var, {'title': var, 'xmin': 0, 'xmax': 1})
    h_total_mc.SetTitle(f"{plot_title}; {var_props['title']}; Events Per {targetpot:.1e} POT")
    h_total_mc.SetMaximum(h_total_mc.GetMaximum() * 1.5)
    h_total_mc.Draw("hist")
    
    # Draw uncertainty band
    h_uncertainty_total.SetFillColor(rt.kGray+1)
    h_uncertainty_total.SetFillStyle(3002)
    h_uncertainty_total.SetLineColor(rt.kGray+1)
    h_uncertainty_total.SetLineWidth(1)
    h_uncertainty_total.SetMarkerSize(0)
    h_uncertainty_total.Draw("E2same")
    
    # Create legend
    legend = rt.TLegend(0.65, 0.65, 0.89, 0.89)
    legend.SetTextSize(0.03)
    legend.SetFillStyle(0)
    legend.SetBorderSize(1)
    legend.AddEntry(h_total_mc, f"CC #nu_{{#mu}} overlay ({h_total_mc.Integral():.1f})", "f")
    legend.AddEntry(h_uncertainty_total, "Sys. unc.", "f")
    legend.Draw()
    
    canvas.Update()
    out.cd()
    canvas.Write()
    
    # === Create fractional error plot ===
    canvas_frac = rt.TCanvas(f"c_{var}_frac_error", f"{var} Fractional Error", 1000, 600)
    canvas_frac.Draw()
    canvas_frac.SetTickx(1)
    canvas_frac.SetTicky(1)
    
    # Create fractional error histograms
    h_frac_stat = h_total_mc.Clone(f"h_frac_stat_{var}")
    h_frac_flux = h_total_mc.Clone(f"h_frac_flux_{var}")
    h_frac_xsec = h_total_mc.Clone(f"h_frac_xsec_{var}")
    h_frac_reint = h_total_mc.Clone(f"h_frac_reint_{var}")
    h_frac_detector = h_total_mc.Clone(f"h_frac_detector_{var}")
    h_frac_total = h_total_mc.Clone(f"h_frac_total_{var}")
    
    h_frac_stat.Reset()
    h_frac_flux.Reset()
    h_frac_xsec.Reset()
    h_frac_reint.Reset()
    h_frac_detector.Reset()
    h_frac_total.Reset()
    
    # Calculate fractional errors
    for ibin in range(0, h_total_mc.GetNbinsX() + 2):
        central = h_total_mc.GetBinContent(ibin)
        
        if central > 0:
            # Get fractional uncertainties
            stat_frac = (1.0 / sqrt(central)) if central > 0 else 0.0
            flux_frac = h_uncertainty_flux.GetBinError(ibin) / central
            xsec_frac = h_uncertainty_xsec.GetBinError(ibin) / central
            reint_frac = h_uncertainty_reint.GetBinError(ibin) / central
            detector_frac = h_uncertainty_detector.GetBinError(ibin) / central
            total_frac = sqrt(stat_frac**2 + flux_frac**2 + xsec_frac**2 + reint_frac**2 + detector_frac**2)
            
            # Fill fractional error histograms
            h_frac_stat.SetBinContent(ibin, stat_frac)
            h_frac_flux.SetBinContent(ibin, flux_frac)
            h_frac_xsec.SetBinContent(ibin, xsec_frac)
            h_frac_reint.SetBinContent(ibin, reint_frac)
            h_frac_detector.SetBinContent(ibin, detector_frac)
            h_frac_total.SetBinContent(ibin, total_frac)
    
    # Set histogram styles - MicroBooNE publication style
    h_frac_stat.SetLineColor(rt.kGray+1)
    h_frac_stat.SetLineWidth(2)
    h_frac_stat.SetFillStyle(0)
    
    h_frac_flux.SetLineColor(rt.kGreen+1)
    h_frac_flux.SetLineWidth(2)
    h_frac_flux.SetFillStyle(0)
    
    h_frac_xsec.SetLineColor(rt.kRed)
    h_frac_xsec.SetLineWidth(2)
    h_frac_xsec.SetFillStyle(0)
    
    h_frac_reint.SetLineColor(rt.kBlack)
    h_frac_reint.SetLineWidth(2)
    h_frac_reint.SetFillStyle(0)
    
    h_frac_detector.SetLineColor(rt.kBlue)
    h_frac_detector.SetLineWidth(2)
    h_frac_detector.SetFillStyle(0)
    
    h_frac_total.SetLineColor(rt.kBlack)
    h_frac_total.SetLineWidth(3)
    h_frac_total.SetFillStyle(0)
    
    # Set title and axis
    h_frac_total.SetTitle(f"Uncertainties in CC#nu_{{#mu}} Selection; {var_props['title']}; Fractional Uncertainty")
    
    # Set y-axis range - cap at 2.0 (200% uncertainty) to avoid empty plots
    max_val = max(h_frac_stat.GetMaximum(), h_frac_flux.GetMaximum(), 
                  h_frac_xsec.GetMaximum(), h_frac_reint.GetMaximum(),
                  h_frac_detector.GetMaximum(), h_frac_total.GetMaximum())
    
    # Cap the maximum at 2.0 to avoid empty plots from outliers
    max_val = min(max_val, 2.0)
    
    h_frac_total.SetMaximum(max_val * 1.1)  # Add 10% headroom
    h_frac_total.SetMinimum(0.0)
    
    # Draw
    h_frac_total.Draw("hist")
    h_frac_stat.Draw("hist same")
    h_frac_flux.Draw("hist same")
    h_frac_xsec.Draw("hist same")
    h_frac_reint.Draw("hist same")
    h_frac_detector.Draw("hist same")
    
    # Add legend - MicroBooNE style (upper left)
    leg_frac = rt.TLegend(0.15, 0.60, 0.40, 0.88)
    leg_frac.SetTextSize(0.035)
    leg_frac.SetFillStyle(0)
    leg_frac.SetBorderSize(1)
    leg_frac.AddEntry(h_frac_stat, "Statistical", "l")
    leg_frac.AddEntry(h_frac_detector, "Detector", "l")
    leg_frac.AddEntry(h_frac_reint, "Hadron re-int.", "l")
    leg_frac.AddEntry(h_frac_flux, "Flux", "l")
    leg_frac.AddEntry(h_frac_xsec, "Cross Section", "l")
    leg_frac.AddEntry(h_frac_total, "Total", "l")
    leg_frac.Draw()
    
    # Add text label - MicroBooNE style
    latex = rt.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.SetTextColor(rt.kRed)
    latex.DrawLatex(0.55, 0.82, "MicroBooNE Simulation,")
    latex.DrawLatex(0.55, 0.77, "Preliminary")
    
    canvas_frac.Update()
    out.cd()
    canvas_frac.Write()
    
    print(f"  Created plots for {var}: {h_total_mc.Integral():.2f} events")

print(f"\nSaved to {out_name}")
out.Close()