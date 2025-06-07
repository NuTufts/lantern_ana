import os,sys
import ROOT as rt
from math import sqrt


targetpot = 1.32e21

samples = ['numu','numu_reco']

scaling = {
    "numu":targetpot/4.5221966264744385e+20,
    "numu_reco":targetpot/4.5221966264744385e+20,
    #"extbnb":(176222.0/368589)*0.8,
    #"data":1.0
}

files = {
    "numu":"./output_tki_dev/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250607_113130.root",
    "numu_reco":"./output_tki_dev/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250607_113130.root",
    "extbnb":"./output_tki_dev/run1_extbnb_mcc9_v29e_C1_20250607_113723.root",
    "data":"./output_tki_dev/run1_bnb5e19_20250607_113630.root"
}

tfiles = {}
trees = {}

rt.gStyle.SetOptStat(0)

for sample in samples:
    tfiles[sample] = rt.TFile( files[sample] )
    trees[sample] = tfiles[sample].Get("analysis_tree")
    nentries = trees[sample].GetEntries()
    print(f"sample={sample} has {nentries} entries")

out = rt.TFile("temp.root","recreate")

vars = [
    ('numuCC1piNp_muonKE',  50, 0.0, 4000.0, f'True Muon KE ({targetpot:.2e} POT)',         0),
    ('numuCC1piNp_protonKE',50, 0.0, 3000.0, f'True Max Proton KE ({targetpot:.2e} POT)',   0),
    ('numuCC1piNp_pionKE',  50, 0.0, 3000.0, f'True Charged Pion KE ({targetpot:.2e} POT)', 0),
#    ('eventweight_weight',  50, 0.0, 10.0,   f'event weight ({targetpot:.2e} POT)',         0),
]

hists = {}
canvs = {}


cut = "(numuCC1piNp_is_infv==1 && numuCC1piNp_is_target_cc_numu_1pi_nproton==1)"
#cut = "numuCC1piNp_is_infv==1 && numuCC1piNp_muonKE>=0.050" # should be proxy for CCnumu with vertex in TPC


for var, nbins, xmin, xmax, htitle, setlogy in vars:

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {cname}",1800,800)
    canvs[var].Divide(2,1)
    canvs[var].Draw()
    canvs[var].cd(1)

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )
        samplecut = cut
        if sample in ['numu_reco']:
            samplecut += " && (numuCC1piNpReco_is_target_1mu1piNproton==1)"
        if var!="eventweight_weight":
            trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})*eventweight_weight")
            hists[(var,sample)].Scale( scaling[sample] )
        else:
            trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})")
        
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral()," scale-factor=",scaling[sample])

    if (var,'numu') in hists:
        hists[(var,"numu")].SetFillColor(rt.kBlue-3)
        hists[(var,"numu")].SetFillStyle(0)
    if (var,'numu_reco') in hists:
        hists[(var,"numu_reco")].SetFillColor(rt.kRed-3)
        hists[(var,"numu_reco")].SetFillStyle(3003)
    # if (var,'extbnb') in hists:
    #     hists[(var,"extbnb")].SetFillColor(rt.kGray)
    #     hists[(var,"extbnb")].SetFillStyle(3144)
    # if (var,'data') in hists:
    #     hists[(var,"data")].SetLineColor(rt.kBlack)
    #     hists[(var,"data")].SetLineWidth(2)

    hstack_name = f"hs_{var}"
    hstack = rt.THStack(hstack_name,"")
    if (var,'extbnb') in hists:
        hstack.Add( hists[(var,"extbnb")])
    if (var,'numu') in hists:
        hstack.Add( hists[(var,"numu")])
    hists[(hstack_name,sample)] = hstack

    hstack.Draw("hist")
    canvs[var].SetLogy(setlogy)

    predmax = hstack.GetMaximum()
    if (var,"data") in hists:
        datamax = hists[(var,"data")].GetMaximum()
    else:
        datamax = -1.0

    if predmax>datamax:
        if setlogy==1:
            hstack.GetYaxis().SetRangeUser(0.1,predmax*5)
        hstack.SetTitle(htitle)
        hstack.Draw("hist")
    else:
        if setlogy==1:
            hists[(var,"data")].GetYaxis().SetRangeUser(0.1,predmax*5)
        hists[(var,"data")].SetTitle(htitle)
        hists[(var,"data")].Draw("E1")
        hstack.Draw("histsame")

    if (var,'data') in hists:
        hists[(var,"data")].Draw("E1same")

    if (var,'numu_reco') in hists:
        hists[(var,'numu_reco')].Draw('histsame')

    canvs[var].cd(2)
    canvs[var].cd(2).SetGridx(1)
    canvs[var].cd(2).SetGridy(1)

    heffname = f'h{var}_eff'
    heff = hists[(var,'numu_reco')].Clone(heffname)
    heff.SetFillColor(0)
    heff.Divide( hists[(var,'numu')] )

    for ibin in range(heff.GetXaxis().GetNbins()):
        x = heff.GetBinContent(ibin+1) # efficiency
        xm = hists[(var,'numu_reco')].GetBinContent(ibin+1)  # number of events in numerator
        xn = hists[(var,'numu')].GetBinContent(ibin+1)  # number of events in denomenator
        if xn>0:
            err = sqrt( xm*(1-x) )/xn
        else:
            err = 0
        heff.SetBinError(ibin+1,err)

    heff.Draw("histE1")
    hists[(var,"efficiency")] = heff
    canvs[var].Update()

    print("[enter] to continue")
    #input()

print("[enter] to close")
input()
