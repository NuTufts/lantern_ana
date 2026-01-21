import os,sys
import ROOT as rt
from math import sqrt

rt.gStyle.SetOptStat(0)
rt.gStyle.SetPadLeftMargin(0.1)
rt.gStyle.SetPadRightMargin(0.05)

rfile = rt.TFile("./output_numu_run4a_surprise/xsecflux_numu_cc_inclusive_run4a_surprise.root")

"""
"""

TARGET_POT=8.806e18
MCSAMPLE_POT=2.3593114985024402e+20
POT_SCALE=TARGET_POT/MCSAMPLE_POT


histmodes = ['cv','w','w2','N']
variables = ['visible_energy']
samples   = ['run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise']
flux_params = [
    "flux_all"
]
genie_params = [
    "All_UBGenie"
]
other_xsec = [
    "XSecShape_CCMEC_UBGenie",
    "DecayAngMEC_UBGenie",    
    "RPA_CCQE_UBGenie",
    "AxFFCCQEshape_UBGenie",
    "VecFFCCQEshape_UBGenie",
    "xsr_scc_Fa3_SCC",
    "xsr_scc_Fv3_SCC",
    "NormCCCOH_UBGenie",
    "NormNCCOH_UBGenie",
    "ThetaDelta2NRad_UBGenie",
    "Theta_Delta2Npi_UBGenie"
    ]
reinteractions=[
    "reint_all"
]
all_pars = flux_params+genie_params+other_xsec+reinteractions
#all_pars = flux_params
#all_pars = genie_params
#all_pars = other_xsec
#all_pars = reinteractions
#all_pars = genie_params+other_xsec

def make_hist_w_errors( rfile, varname, sample, parlist, pot_scale=1.0 ):
    hists = {}
    hcv_name = f"h{varname}_{sample}_cv"
    hcv = rfile.Get(hcv_name)
    hcv.Scale(pot_scale)
    hvar_tot = hcv.Clone(f"h{varname}__{sample}_totvariance")
    hvar_tot.Reset()
    hmeans2 = hcv.Clone(f"h{varname}__{sample}_meanofmeans")
    hmeans2.Reset()
    hfracerr = hcv.Clone(f"h{varname}__{sample}_fracerror")
    hfracerr.Reset()
    for parname in parlist:
        h2d_name = f"h{varname}__{sample}__{parname}"        
        hname_mean = f"h{varname}__{sample}__{parname}_mean"
        hname_var  = f"h{varname}__{sample}__{parname}_variance"
        hmean = rfile.Get(hname_mean)
        hvar  = rfile.Get(hname_var)
        h2d   = rfile.Get(h2d_name)
        print(f"{parname} # of variations: ",h2d.GetYaxis().GetNbins())
        hists[parname] = hcv.Clone(f"h{varname}__{sample}__{parname}__cv_with_var")
        for ibin in range(1,hvar_tot.GetXaxis().GetNbins()+1):
            #xvar  = hvar.GetBinContent(ibin)*pot_scale*pot_scale
            xstd  = hmean.GetBinError(ibin)*pot_scale
            xmean = hmean.GetBinContent(ibin)*pot_scale

            if xmean>0:
                xfracvar = xstd/xmean
            else:
                xfracvar = 0.0

            cv_std = xfracvar*hcv.GetBinContent(ibin)

            xvar_tot  = hvar_tot.GetBinContent(ibin)
            hvar_tot.SetBinContent(ibin, xvar_tot+cv_std*cv_std ) # add in quadtrature
            xmean2 = hmeans2.GetBinContent(ibin)
            hmeans2.SetBinContent(ibin, xmean2 + xmean/len(parlist) )
            hists[parname].SetBinError(ibin,cv_std)
    # set std for CV error
    for ibin in range(1,hvar_tot.GetXaxis().GetNbins()+1):
        stddev = sqrt(hvar_tot.GetBinContent(ibin))
        hcv.SetBinError(ibin,stddev)
        # same frac error hist
        binval = hcv.GetBinContent(ibin)
        if binval>0.0:
            fracerr = stddev/binval
            hfracerr.SetBinContent(ibin,fracerr)
        
    hists['cv'] = hcv
    hists['mean2'] = hmeans2
    hists['fracerr'] = hfracerr
    hists['var_tot'] = hvar_tot
    return hists
    
        
temp = rt.TFile("temp.root",'recreate')
canvs = {}

for var in variables:
    for sample in samples:
        hists = make_hist_w_errors(rfile, var,sample,all_pars,pot_scale=POT_SCALE)
        c = rt.TCanvas(f"c{var}_{sample}",f"{var} {sample}",3000,2000)
        c.Divide(2,2)
        c.Draw()
        c.cd(1)
        c.cd(1).SetGridx(1)
        c.cd(1).SetGridy(1)
        
        hcv = hists['cv']
        hcvline = hists['cv'].Clone(f"h{var}_{sample}_cvline")
        hcvline.SetLineWidth(2)
        hcv.SetFillColor(rt.kBlue+2)
        hcv.SetFillStyle(3003)
        hcv.GetXaxis().SetTitle("reco. neutrino energy (MeV)")
        hcv.GetYaxis().SetTitle(f"counts per {TARGET_POT:.2e} POT")        

        hmeans2 = hists['mean2']
        hmeans2.SetLineWidth(2)
        hmeans2.SetLineColor(rt.kRed-2)


        hcv.Draw("E2")
        hcvline.Draw("histsame")
        #hmeans2.Draw("histsame")

        c.cd(2)
        c.cd(2).SetRightMargin(0.5)
        c.cd(2).SetLeftMargin(0.05)        
        #hists['fracerr'].Draw("hist")

        # make stack
        hstack = rt.THStack(f"hstack_{var}_{sample}_fracvar_frompars",";reco. neutrino energy (MeV);fraction of total variance")
        len_stack = rt.TLegend(0.52,0.9,0.98,0.1)        
        hcomps = []
        icolor = 2
        icolor_ii = 0
        hcomp_with_name = []
        for ipar,par in enumerate(all_pars):
            hpar = hcv.Clone(f"hcomps_{var}_{sample}_{par}")
            hpar.Reset()
            for ibin in range(1,hpar.GetXaxis().GetNbins()+1):
                stddev = hists[par].GetBinError(ibin)
                if hists['var_tot'].GetBinContent(ibin)>0.0:
                    frac_var = (stddev*stddev)/hists['var_tot'].GetBinContent(ibin)
                    print(stddev,"/",hists['var_tot'].GetBinContent(ibin))
                    hpar.SetBinContent(ibin,frac_var)
                else:
                    hpar.SetBinContent(ibin,0.0)
            hpar.SetFillColor( icolor )
            hpar.GetXaxis().SetTitle("reco. neutrino energy (MeV)")                                
            icolor += 1
            if icolor>=10:
                icolor_ii += 1
                icolor = 2
            hpar.SetFillStyle(3003+icolor_ii)
            print(hpar.GetName(),": ",hpar.Integral()," color=",icolor)
            hstack.Add( hpar )
            #len_stack.AddEntry(hpar,par,"f")
            hcomp_with_name.append( (par,hpar) )
            hcomps.append(hpar)
        for (name,h) in reversed(hcomp_with_name):
            len_stack.AddEntry(h,name,'f')

        #hstack.GetXaxis().SetTitle("reco. neutrino energy (MeV)")                    
        hstack.Draw()
        len_stack.Draw()

        c.cd(3)
        hists['fracerr'].Draw("hist")
        hists['fracerr'].SetMinimum(0)

        c.cd(4)
        
        c.Update()
        canvs[(var,sample)] = c
print("[enter] to exit")
input()



