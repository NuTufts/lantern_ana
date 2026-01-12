import os,sys
import ROOT as rt
import array
from math import sqrt

"""
Updated plot_numu.py to include xsecflux uncertainty bars
Combines uncertainties from separate nue and numu files in quadrature
"""

# CRITICAL: Enable automatic sum of weights squared for proper error calculation
rt.TH1.SetDefaultSumw2(rt.kTRUE)

run_num = 1

lantern_dir = "/nashome/z/zimani/lantern/lantern_ana/"

## Run 1 Configuration
if run_num == 1: 
	targetpot = 4.4e19
	scaling = {"numu":targetpot/4.675690535431973e+20,
			"nue":targetpot/9.662529168587103e+22,
			"extbnb":(176153.0)/(433446.0),
			"data":1.0}
	files = {"numu": f"{lantern_dir}/zev_mmr/mmr_outputs/run1_bnb_nu_overlay_mcc9_v28_wctagger.root",
			"nue":f"{lantern_dir}/zev_mmr/mmr_outputs/run1_bnb_nue_overlay_mcc9_v28_wctagger.root", 
			"extbnb":f"{lantern_dir}/zev_mmr/mmr_outputs/run1_extbnb_mcc9_v29e_C1.root",
			"data":f"{lantern_dir}/zev_mmr/mmr_outputs/run1_bnb5e19.root"}
	out_name = "./numu_hists1.root"
	plot_title = "Run 1"
	
	# Separate xsecflux covariance files for nue and numu
	xsecflux_files = {
		"nue": f"{lantern_dir}/studies/xsecflux/run1_outputs/xsecflux_run1_nue_intrinsic_nue.root",
		"numu": f"{lantern_dir}/studies/xsecflux/run1_outputs/xsecflux_run1_numu_intrinsic_nue.root"
	}

## Run 4b Configuration
# if run_num == 4: 
# 	targetpot = 1.45e+20
# 	scaling = {"numu":targetpot/7.881656209241413e+20,
# 	           "nue":targetpot/1.1785765118473412e+23,
# 	           "extbnb":34317881.0/96638186.0,
# 	           "data":1.0}
# 	files = {"numu":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_BNB_nu_overlay_surprise.root",
# 			 "nue":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_BNB_nue_overlay_surprise.root", 
# 			 "extbnb":"./zev_mmr/mmr_outputs/run4b_v10_04_07_09_extbnb.root",
# 			 "data":"./zev_mmr/mmr_outputs/run4b_beamon.root"}
# 	out_name = "./zev_mmr/hists/numu_hists4.root"
# 	plot_title = "Run 4b"
	
# 	# Separate xsecflux covariance files for nue and numu
# 	xsecflux_files = {
# 		"nue": "xsecflux_run4_nue_intrinsic_nue.root",
# 		"numu": "xsecflux_run4_numu_intrinsic_nue.root"
# 	}

# Define systematic parameters (from make_temp_test_plot.py)
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
genie_params = [
    "All_UBGenie"
]
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
all_pars = flux_params + genie_params + other_xsec

def make_hist_w_errors(rfile, varname, sample, parlist):
    """
    Create histogram with xsecflux uncertainty errors added
    Based on make_temp_test_plot.py
    
    Note: CV histograms use single underscore, mean/variance use double underscores
    """
    hists = {}
    hcv_name = f"h{varname}_{sample}_cv"  # Single underscore for CV
    hcv = rfile.Get(hcv_name)
    
    if not hcv:
        print(f"Warning: Could not find CV histogram {hcv_name}")
        return None
    
    hvar_tot = hcv.Clone(f"h{varname}__{sample}_totvariance")
    hvar_tot.Reset()
    hmeans2 = hcv.Clone(f"h{varname}__{sample}_meanofmeans")
    hmeans2.Reset()
    
    for parname in parlist:
        hname_mean = f"h{varname}__{sample}__{parname}_mean"
        hname_var  = f"h{varname}__{sample}__{parname}_variance"
        hmean = rfile.Get(hname_mean)
        hvar  = rfile.Get(hname_var)
        
        if not hmean or not hvar:
            continue
            
        hists[parname] = hvar
        for ibin in range(0, hvar_tot.GetXaxis().GetNbins()+1):
            xvar  = hvar.GetBinContent(ibin)
            xmean = hmean.GetBinContent(ibin)

            if xmean > 0:
                xfracvar = xvar/xmean
            else:
                xfracvar = 0.0

            cv_var = xfracvar * hcv.GetBinContent(ibin)

            xvar_tot  = hvar_tot.GetBinContent(ibin)
            hvar_tot.SetBinContent(ibin, xvar_tot + cv_var)  # add variances
            xmean2 = hmeans2.GetBinContent(ibin)
            hmeans2.SetBinContent(ibin, xmean2 + xmean/len(parlist))
    
    # Set std dev for CV error bars
    for ibin in range(0, hvar_tot.GetXaxis().GetNbins()+1):
        stddev = sqrt(hvar_tot.GetBinContent(ibin))
        hcv.SetBinError(ibin, stddev)
    
    hists['cv'] = hcv
    hists['mean2'] = hmeans2
    hists['variance'] = hvar_tot
    return hists

rt.gStyle.SetOptStat(0)
rt.gStyle.SetEndErrorSize(0)

samples = ['nue','numu','extbnb','data']

tfiles = {}
trees = {}

for sample in samples:
	tfiles[sample] = rt.TFile(files[sample])
	trees[sample] = tfiles[sample].Get("analysis_tree")
	nentries = trees[sample].GetEntries()
	print(f"sample={sample} has {nentries} entries")

# Load xsecflux covariance files
xsec_files = {}
for sample_type, filepath in xsecflux_files.items():
	if os.path.exists(filepath):
		xsec_files[sample_type] = rt.TFile(filepath)
		print(f"Loaded xsecflux covariance file for {sample_type}: {filepath}")
	else:
		print(f"Warning: Xsecflux file {filepath} not found for {sample_type}.")

out = rt.TFile(out_name, "recreate")

# Base cuts using NeutrinoSelectionProducer variables
base_cut = f"(numuIncCC_has_vertex_in_fv==1)"
base_cut += f" && (numuIncCC_cosmic_frac<0.30)"
base_cut += f" && (numuIncCC_has_muon==1)"
base_cut += f" && (numuIncCC_muon_pid_score>-0.9)"

# Cut for signal vs background in numu sample
numu_cc_cut = f"({base_cut}) && (true_nu_pdg==14 && true_ccnc==0)"
numu_bg_cut = f"({base_cut}) && !(true_nu_pdg==14 && true_ccnc==0)"

# Data cuts
data_cut = base_cut
extbnb_cut = base_cut

# nue always background for numu selection
nue_cut = base_cut

# Define plot variables (name, nbins, xmin, xmax, xtitle, is_log, use_xsec_errors)
vars = [
	('visible_energy', 30, 0, 3000, 'Visible Energy (MeV)', False, True),
	('muon_properties_angle', 16, -1.01, 1.01, 'Muon Angle cos#theta_{beam}', False, False),
	('muon_properties_energy', 50, 0, 2500.0, 'Muon Kinetic Energy (MeV)', False, False),
	('muon_properties_pid_score', 101, -1.01, 0.01, 'Muon PID Score', False, False),
	('vertex_properties_score', 30, 0.7, 1.0, 'Keypoint Score', False, False),
]

hists = {}
canvs = {}

print("\n=== Creating histograms ===")
for var_name, nbins, xmin, xmax, xtitle, is_log, use_xsec_errors in vars:
	print(f"\nProcessing variable: {var_name}")
	
	# Create histograms for each sample
	h_numu_sig = rt.TH1D(f"h_{var_name}_numu_sig", f"#nu_#mu CC Signal;{xtitle};Events", nbins, xmin, xmax)
	h_numu_bg  = rt.TH1D(f"h_{var_name}_numu_bg",  f"#nu_#mu Background;{xtitle};Events", nbins, xmin, xmax)
	h_nue      = rt.TH1D(f"h_{var_name}_nue",      f"#nu_e Background;{xtitle};Events", nbins, xmin, xmax)
	h_extbnb   = rt.TH1D(f"h_{var_name}_extbnb",   f"Beam-off;{xtitle};Events", nbins, xmin, xmax)
	h_data     = rt.TH1D(f"h_{var_name}_data",     f"Data;{xtitle};Events", nbins, xmin, xmax)

	# Fill histograms
	trees['numu'].Draw(f"{var_name}>>h_{var_name}_numu_sig", f"eventweight_weight*{scaling['numu']}*({numu_cc_cut})", "goff")
	trees['numu'].Draw(f"{var_name}>>h_{var_name}_numu_bg",  f"eventweight_weight*{scaling['numu']}*({numu_bg_cut})", "goff")
	trees['nue'].Draw(f"{var_name}>>h_{var_name}_nue",       f"eventweight_weight*{scaling['nue']}*({nue_cut})", "goff")
	trees['extbnb'].Draw(f"{var_name}>>h_{var_name}_extbnb", f"{scaling['extbnb']}*({extbnb_cut})", "goff")
	trees['data'].Draw(f"{var_name}>>h_{var_name}_data", f"{scaling['data']}*({data_cut})", "goff")

	# Get xsecflux uncertainties for both nue and numu samples
	hist_with_sys = {}
	
	if use_xsec_errors:
		# Process numu uncertainties (signal + background)
		if 'numu' in xsec_files:
			xsec_hists_numu = make_hist_w_errors(xsec_files['numu'], var_name, xsec_sample_name, all_pars)
			if xsec_hists_numu:
				h_numu_total_sys = xsec_hists_numu['cv'].Clone(f"h_{var_name}_numu_total_sys")
				h_numu_total_sys.Scale(scaling['numu'])
				
				# Split into signal and background based on histogram content ratio
				h_numu_sig_sys = h_numu_total_sys.Clone(f"h_{var_name}_numu_sig_sys")
				h_numu_bg_sys = h_numu_total_sys.Clone(f"h_{var_name}_numu_bg_sys")
				for ibin in range(1, h_numu_sig_sys.GetNbinsX()+1):
					total_numu = h_numu_sig.GetBinContent(ibin) + h_numu_bg.GetBinContent(ibin)
					if total_numu > 0:
						sig_frac = h_numu_sig.GetBinContent(ibin) / total_numu
						bg_frac = h_numu_bg.GetBinContent(ibin) / total_numu
					else:
						sig_frac = 0.5
						bg_frac = 0.5
					
					total_err = h_numu_total_sys.GetBinError(ibin)
					h_numu_sig_sys.SetBinError(ibin, total_err * sig_frac)
					h_numu_bg_sys.SetBinError(ibin, total_err * bg_frac)
				
				hist_with_sys['numu_sig'] = h_numu_sig_sys
				hist_with_sys['numu_bg'] = h_numu_bg_sys
				print(f"  Added xsecflux uncertainties to numu sample")
		
		# Process nue intrinsic uncertainties
		if 'nue' in xsec_files:
			xsec_hists_nue = make_hist_w_errors(xsec_files['nue'], var_name, xsec_sample_name, all_pars)
			if xsec_hists_nue:
				h_nue_sys = xsec_hists_nue['cv'].Clone(f"h_{var_name}_nue_sys")
				h_nue_sys.Scale(scaling['nue'])
				hist_with_sys['nue'] = h_nue_sys
				print(f"  Added xsecflux uncertainties to nue intrinsic sample_numu_sig_sys")
			hist_with_sys['numu_bg'] = h_numu_bg_sys
			print(f"  Added xsecflux uncertainties to numu sample")
	
	# Process nue intrinsic uncertainties
	if 'nue' in xsec_files and xsec_varname and sample_names and 'nue' in sample_names:
		xsec_hists_nue = make_hist_w_errors(xsec_files['nue'], xsec_varname, sample_names['nue'], all_pars)
		if xsec_hists_nue:
			h_nue_sys = xsec_hists_nue['cv'].Clone(f"h_{var_name}_nue_sys")
			h_nue_sys.Scale(scaling['nue'])
			hist_with_sys['nue'] = h_nue_sys
			print(f"  Added xsecflux uncertainties to nue intrinsic sample")

	# Save histograms
	h_numu_sig.Write()
	h_numu_bg.Write()
	h_nue.Write()
	h_extbnb.Write()
	h_data.Write()
	for key, h in hist_with_sys.items():
		h.Write()

	# Create stacked plot
	c = rt.TCanvas(f"c_{var_name}", var_name, 1200, 800)
	c.Draw()
	
	if is_log:
		c.SetLogy()

	# Set histogram styles
	h_numu_sig.SetFillColor(rt.kBlue-4)
	h_numu_sig.SetLineColor(rt.kBlack)
	h_numu_bg.SetFillColor(rt.kGreen-3)
	h_numu_bg.SetLineColor(rt.kBlack)
	h_nue.SetFillColor(rt.kRed-4)
	h_nue.SetLineColor(rt.kBlack)
	h_extbnb.SetFillColor(rt.kGray)
	h_extbnb.SetLineColor(rt.kBlack)

	h_data.SetMarkerStyle(20)
	h_data.SetMarkerSize(1.0)
	h_data.SetLineColor(rt.kBlack)

	# Create stack
	hs = rt.THStack(f"hs_{var_name}", f";{xtitle};Events")
	hs.Add(h_extbnb)
	hs.Add(h_nue)
	hs.Add(h_numu_bg)
	hs.Add(h_numu_sig)

	# Draw
	hs.Draw("hist")
	
	# Add systematic uncertainty band combining all sources in quadrature
	if len(hist_with_sys) > 0:
		# Start with extbnb (no systematics)
		h_sys_band = h_extbnb.Clone(f"h_{var_name}_sys_band")
		
		# List to collect histograms with their systematic errors
		hists_to_combine = []
		
		# Add nue with systematics if available, otherwise without
		if 'nue' in hist_with_sys:
			hists_to_combine.append((hist_with_sys['nue'], 1.0))
		else:
			# No systematics, use nominal with stat errors only
			hists_to_combine.append((h_nue, 1.0))
		
		# Add numu background with systematics if available
		if 'numu_bg' in hist_with_sys:
			hists_to_combine.append((hist_with_sys['numu_bg'], 1.0))
		else:
			hists_to_combine.append((h_numu_bg, 1.0))
		
		# Add numu signal with systematics if available
		if 'numu_sig' in hist_with_sys:
			hists_to_combine.append((hist_with_sys['numu_sig'], 1.0))
		else:
			hists_to_combine.append((h_numu_sig, 1.0))
		
		# Combine all uncertainties in quadrature
		for ibin in range(1, h_sys_band.GetNbinsX()+1):
			total_content = h_extbnb.GetBinContent(ibin)
			total_err_sq = 0.0  # extbnb has no flux/xsec systematics
			
			for hist, scale in hists_to_combine:
				total_content += hist.GetBinContent(ibin) * scale
				error = hist.GetBinError(ibin) * scale
				total_err_sq += error * error
			
			h_sys_band.SetBinContent(ibin, total_content)
			h_sys_band.SetBinError(ibin, sqrt(total_err_sq))
		
		h_sys_band.SetFillColor(rt.kBlue-3)
		h_sys_band.SetFillStyle(3003)
		h_sys_band.SetLineWidth(2)
		h_sys_band.Draw("E2 same")

	h_data.Draw("E1 same")

	# Legend
	leg = rt.TLegend(0.65, 0.65, 0.88, 0.88)
	leg.SetBorderSize(0)
	leg.SetFillStyle(0)
	leg.AddEntry(h_data, "Data", "lep")
	leg.AddEntry(h_numu_sig, "#nu_{#mu} CC Signal", "f")
	leg.AddEntry(h_numu_bg, "#nu_{#mu} Background", "f")
	leg.AddEntry(h_nue, "#nu_{e} Background", "f")
	leg.AddEntry(h_extbnb, "Beam-off", "f")
	if len(hist_with_sys) > 0:
		leg.AddEntry(h_sys_band, "Flux+XSec Syst.", "f")
	leg.Draw()

	# Title
	title = rt.TLatex()
	title.SetNDC()
	title.SetTextSize(0.04)
	title.DrawLatex(0.12, 0.92, plot_title)

	c.Update()
	canvs[var_name] = c

	# Save as PNG
	c.SaveAs(f"{var_name}_numu_selection.png")

out.Close()
for xsec_file in xsec_files.values():
	xsec_file.Close()

print("\n=== Histograms saved to:", out_name, "===")
print("Enter to exit")