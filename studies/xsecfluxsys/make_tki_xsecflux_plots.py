import os, sys
import ROOT as rt
from math import sqrt

inputfiles = [
    "temp_covar.root"
]

plot_folder = "./plots_tki_systematics/"
os.system(f"mkdir -p {plot_folder}")

# Flux systematics
flux_parameters = [
    'expskin_FluxUnisim',
    'horncurrent_FluxUnisim',
    'nucleoninexsec_FluxUnisim',
    'nucleonqexsec_FluxUnisim',
    'nucleontotxsec_FluxUnisim',
    'pioninexsec_FluxUnisim',
    'pionqexsec_FluxUnisim',
    'piontotxsec_FluxUnisim',
    'kminus_PrimaryHadronNormalization',
    'kplus_PrimaryHadronFeynmanScaling',
    'kzero_PrimaryHadronSanfordWang',
    'piminus_PrimaryHadronSWCentralSplineVariation',
    'piplus_PrimaryHadronSWCentralSplineVariation'
]

# Cross-section systematics
xsec_parameters = [
    'All_UBGenie',
    'XSecShape_CCMEC_UBGenie',
    'RPA_CCQE_UBGenie',
    'AxFFCCQEshape_UBGenie',
    'VecFFCCQEshape_UBGenie',
    'DecayAngMEC_UBGenie',
    'xsr_scc_Fa3_SCC',
    'xsr_scc_Fv3_SCC',
    'NormCCCOH_UBGenie',
    'NormNCCOH_UBGenie',
    'ThetaDelta2NRad_UBGenie',
    'Theta_Delta2Npi_UBGenie'
]

# Geant4 reinteraction systematics
geant4_parameters = [
    'reinteractions_piminus_Geant4',
    'reinteractions_piplus_Geant4',
    'reinteractions_proton_Geant4'
]

# Combine all parameters
parameters = flux_parameters + xsec_parameters + geant4_parameters

# Variable short names as they appear in the file
variables = [
    'delPTT',
    'pN',
    'delAlphaT'
]

# Sample/run identifier
sample_id = "run3b_bnb_nu_overlay_mcc9_v29e_CV"

output_file = "systematics_tki_run3b.root"
rout = rt.TFile(output_file, 'recreate')

canvases = {}

for var in variables:
    print("=" * 80)
    print(f"[{var}] Calculating Fractional Variance")
    
    hvar_sum_frac = None
    
    for finput in inputfiles:
        rfile = rt.TFile(finput)
        
        for par in parameters:
            # New naming convention: h{var}__{sample_id}__{par}_mean and _variance
            hpar_mean_name = f"h{var}__{sample_id}__{par}_mean"
            hpar_var_name = f"h{var}__{sample_id}__{par}_variance"
            
            hpar_mean = rfile.Get(hpar_mean_name)  # mean (central value)
            hpar_var = rfile.Get(hpar_var_name)    # variance
            
            try:
                # Test if histogram exists
                hpar_mean.Integral()
                print(f"{par}: {hpar_mean_name}")
            except:
                continue
            
            rout.cd()
            
            if hvar_sum_frac is None:
                hvar_sum_frac = hpar_mean.Clone(f"h{var}__totfracvar")
                hvar_sum_frac.Reset()
            
            hpar_frac = hpar_mean.Clone(f"h{var}__{par}__fracvar")
            hpar_frac.Reset()
            
            for ibin in range(1, hpar_mean.GetXaxis().GetNbins() + 1):
                counts_mean = hpar_mean.GetBinContent(ibin)
                variance = hpar_var.GetBinContent(ibin)  # This is already variance
                
                if counts_mean > 0:
                    frac_variance = variance / float(counts_mean)
                    hpar_frac.SetBinContent(ibin, frac_variance)
                    var_tot = hvar_sum_frac.GetBinContent(ibin)
                    print(f"var[{var}]-bin[{ibin}] mean={counts_mean} var={variance} --> frac_var={frac_variance} running_tot={var_tot + frac_variance}")
                    hvar_sum_frac.SetBinContent(ibin, var_tot + frac_variance)
            
            # Save to file
            hpar_frac.Write()
    
    rout.cd()
    
    # Make the fractional stddev plot
    hstddev_frac = hvar_sum_frac.Clone(f"h{var}__totfracstddev")
    hstddev_frac.Reset()
    
    # Get CV histogram (central value)
    rfilecv = rt.TFile(inputfiles[0])
    hvar_cv_name = f"h{var}_{sample_id}_cv"
    hvar_cv = rfilecv.Get(hvar_cv_name)
    
    for ibin in range(1, hvar_sum_frac.GetXaxis().GetNbins() + 1):
        fracvar = hvar_sum_frac.GetBinContent(ibin)  # total fraction variance
        counts_cv = hvar_cv.GetBinContent(ibin)
        
        if counts_cv > 0:
            variance = fracvar * float(counts_cv)  # variance of bin due to all systematics
            frac_stddev = sqrt(variance) / counts_cv  # frac stddev of bin
            hstddev_frac.SetBinContent(ibin, frac_stddev)
            hvar_cv.SetBinError(ibin, sqrt(variance))
    
    cvar = rt.TCanvas(f"c{var}", var, 1600, 600)
    cvar.Divide(2, 1)
    cvar.cd(1).SetGridx(1)
    cvar.cd(1).SetGridy(1)
    hvar_cv.SetMinimum(0)
    hvar_cv.Draw("histE1")
    cvar.cd(2).SetGridx(1)
    cvar.cd(2).SetGridy(1)
    hstddev_frac.SetMinimum(0)
    hstddev_frac.Draw("hist")
    cvar.Update()
    cvar.SaveAs(f"{plot_folder}/c{var}_systematics.png")
    
    canvases[var] = cvar
    
    rout.cd()
    hvar_cv.Write()
    hstddev_frac.Write()
    hvar_sum_frac.Write()
    cvar.Write()

print("[enter] to close")
input()
rout.Close()