import os,sys
import ROOT as rt
from math import sqrt

rfile = rt.TFile("temp_covar.root")

histmodes = ['cv','w','w2','N']
variables = ['visible_energy']
samples   = ['run1_bnb_nu_overlay_mcc9_v28_wctagger']
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
all_pars = flux_params+genie_params+other_xsec

def make_hist_w_errors( rfile, varname, sample, parlist ):
    hists = {}
    hcv_name = f"h{varname}_{sample}_cv"
    hcv = rfile.Get(hcv_name)
    hvar_tot = hcv.Clone(f"h{varname}__{sample}_totvariance")
    hvar_tot.Reset()
    hmeans2 = hcv.Clone(f"h{varname}__{sample}_meanofmeans")
    hmeans2.Reset()
    for parname in parlist:
        hname_mean = f"h{varname}__{sample}__{parname}_mean"
        hname_var  = f"h{varname}__{sample}__{parname}_variance"
        hmean = rfile.Get(hname_mean)
        hvar  = rfile.Get(hname_var)
        hists[parname] = hvar
        for ibin in range(0,hvar_tot.GetXaxis().GetNbins()+1):
            xvar  = hvar.GetBinContent(ibin)
            xmean = hmean.GetBinContent(ibin)

            if xmean>0:
                xfracvar = xvar/xmean
            else:
                xfracvar = 0.0

            cv_var = xfracvar*hcv.GetBinContent(ibin)

            xvar_tot  = hvar_tot.GetBinContent(ibin)
            hvar_tot.SetBinContent(ibin, xvar_tot+cv_var ) # add variances
            xmean2 = hmeans2.GetBinContent(ibin)
            hmeans2.SetBinContent(ibin, xmean2 + xmean/len(parlist) )
    # set std for CV error
    for ibin in range(0,hvar_tot.GetXaxis().GetNbins()+1):
        stddev = sqrt(hvar_tot.GetBinContent(ibin))
        hcv.SetBinError(ibin,stddev)
    hists['cv'] = hcv
    hists['mean2'] = hmeans2
    return hists
    
        
temp = rt.TFile("temp.root",'recreate')
canvs = {}

for var in variables:
    for sample in samples:
        hists = make_hist_w_errors(rfile, var,sample,all_pars)
        c = rt.TCanvas(f"c{var}_{sample}",f"{var} {sample}",2000,1000)
        c.Draw()
        c.cd(1)
        c.cd(1).SetGridx(1)
        c.cd(1).SetGridy(1)

        hcv = hists['cv']
        hcvline = hists['cv'].Clone(f"h{var}_{sample}_cvline")
        hcvline.SetLineWidth(2)
        hcv.SetFillColor(rt.kBlue-3)
        hcv.SetFillStyle(3003)

        hmeans2 = hists['mean2']
        hmeans2.SetLineWidth(2)
        hmeans2.SetLineColor(rt.kRed-2)


        hcv.Draw("E2")
        hcvline.Draw("histsame")
        hmeans2.Draw("histsame")
        c.Update()
        canvs[(var,sample)] = c
print("[enter] to exit")
input()



