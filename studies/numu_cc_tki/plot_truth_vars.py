import os,sys
import ROOT as rt


"""
"""
targetpot = 1.32e21

samples = ['numu']

scaling = {
    "numu":targetpot/4.5221966264744385e+20,
    #"extbnb":(176222.0/368589)*0.8,
    #"data":1.0
}

files = {
#    "numu":"./output_tki_dev/run1_bnb_nu_overlay_mcc9_v28_wctagger_17cm_truefv.root",
    "numu":"./output_tki_dev/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250606_131119.root",
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
    ('numuCC1piNp_muonKE',  200, 0.0, 4000.0, f'True Muon KE ({targetpot:.2e} POT)',         0),
    ('numuCC1piNp_protonKE',150, 0.0, 3000.0, f'True Max Proton KE ({targetpot:.2e} POT)',   0),
    ('numuCC1piNp_pionKE',  150, 0.0, 3000.0, f'True Charged Pion KE ({targetpot:.2e} POT)', 0),
    ('eventweight_weight',  150, 0.0, 10.0,   f'event weight ({targetpot:.2e} POT)',         0),
]

hists = {}
canvs = {}


cut = "(numuCC1piNp_is_infv==1 && numuCC1piNp_is_target_cc_numu_1pi_nproton==1)"
#cut = "numuCC1piNp_is_infv==1 && numuCC1piNp_muonKE>=0.050" # should be proxy for CCnumu with vertex in TPC


for var, nbins, xmin, xmax, htitle, setlogy in vars:

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {cname}",1000,800)
    canvs[var].Draw()

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )
        samplecut = cut
        if var!="eventweight_weight":
            trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})*eventweight_weight")
            hists[(var,sample)].Scale( scaling[sample] )
        else:
            trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})")
        
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral()," scale-factor=",scaling[sample])

    if (var,'numu') in hists:
        hists[(var,"numu")].SetFillColor(rt.kRed-3)
        hists[(var,"numu")].SetFillStyle(3003)
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

    canvs[var].Update()

    print("[enter] to continue")
    #input()

print("[enter] to close")
input()
