import os,sys
import ROOT as rt
from math import sqrt
from datetime import datetime

rt.gROOT.SetBatch(True) # so plots don't pop up

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

targetpot = 4.4e19

samples = ['numu_sig',"numu_bg","extbnb","data"]

scaling = {
    "numu_sig":targetpot/4.5221966264744385e+20,
    "numu_bg":targetpot/4.5221966264744385e+20,
    "extbnb":(176222.0/372480),
    "data":1.0
}

files = {
    "numu_sig":"./output_tki_dev/run1_bnb_nu_overlay_mcc9_v28_wctagger_20251113_151939.root",
     "numu_bg":"./output_tki_dev/run1_bnb_nu_overlay_mcc9_v28_wctagger_20251113_151939.root",
      "extbnb":"./output_tki_dev/run1_extbnb_mcc9_v29e_C1_20251113_152412.root",
        "data":"./output_tki_dev/run1_bnb5e19_20251113_152521.root"
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
    ('numuCC1piNpReco_muKE',        25, 0.0, 1500.0, f'Reco Muon KE ({targetpot:.2e} POT);muon KE (MeV)',         0),
    ('numuCC1piNpReco_maxprotonKE', 25, 0.0, 500.0, f'Reco Max Proton KE ({targetpot:.2e} POT);proton KE (MeV)',   0),
    ('numuCC1piNpReco_pionKE',      25, 0.0, 500.0, f'Reco Charged Pion KE ({targetpot:.2e} POT);pion KE (MeV)', 0),
    ('numuCC1piNpReco_hadronicM',  25, 1000.0, 1600.0, f'Hadronic Invariant Mass ({targetpot:.2e} POT);invariant mass (MeV/c^{2})', 0),
<<<<<<< HEAD
    ('numuCC1piNpReco_delPTT', 25, -1, 1, f'Reco delPTT (GeV/c) ({targetpot:.2e} POT);#Delta p_{{TT}}', 0),
    ('numuCC1piNpReco_pN', 25, 0, 1.6, f'Reco pN (GeV/c) ({targetpot:.2e} POT);p_{{N}}', 0),
    ('numuCC1piNpReco_delAlphaT', 10, 0, 180, f'Reco delAlphaT (deg) ({targetpot:.2e} POT);#Delta #alpha_{{T}}', 0)
=======
    ('numuCC1piNp_delPTT', 50, -1, 1, f'True delPTT (GeV/c) ({targetpot:.2e} POT)', 0),
    ('numuCC1piNp_pN', 50, 0, 1.6, f'True pN (GeV/c) ({targetpot:.2e} POT)', 0),
    ('numuCC1piNp_delAlphaT', 50, 0, 180, f'True delAlphaT )deg) ({targetpot:.2e} POT)', 0)
>>>>>>> add rest of tki vars to plotting scripts
]

truth_var = {
    'numuCC1piNpReco_muKE':'numuCC1piNp_muonKE',
    'numuCC1piNpReco_maxprotonKE':'numuCC1piNp_protonKE',
    'numuCC1piNpReco_pionKE':'numuCC1piNp_pionKE',
    'numuCC1piNpReco_hadronicM':'numuCC1piNp_hadronicM', # needs to be fixed
    'numuCC1piNpReco_delPTT':'numuCC1piNp_delPTT',
    'numuCC1piNpReco_pN':'numuCC1piNp_pN',
    'numuCC1piNpReco_delAlphaT':'numuCC1piNp_delAlphaT'
}

hists = {}
canvs = {}


signalcut = "(numuCC1piNp_is_infv==1 && numuCC1piNp_is_target_cc_numu_1pi_nproton==1)"
misidcut  = "(numuCC1piNp_is_infv==0 || numuCC1piNp_is_target_cc_numu_1pi_nproton==0)"
cut = "numuCC1piNpReco_is_target_1mu1piNproton==1"
#cut = "numuCC1piNp_is_infv==1 && numuCC1piNp_muonKE>=0.050" # should be proxy for CCnumu with vertex in TPC


for var, nbins, xmin, xmax, htitle, setlogy in vars:

    print("="*100)

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {cname}",2100,700)
    canvs[var].Divide(3,1)
    canvs[var].Draw()

    canvs[var].cd(1)

    # signal denominator, for efficiency
    hname_effdenom = f'h{var}_effdenom'
    truthvar = truth_var[var]
    hists[(var,'effdenom')] = rt.TH1D( hname_effdenom, htitle, nbins, xmin, xmax )
    trees['numu_sig'].Draw(f"{truthvar}>>{hname_effdenom}",f"({signalcut})*eventweight_weight")
    hists[(var,'effdenom')].Scale(scaling['numu_sig'])

    for sample in samples:

        hname = f'h{var}_{sample}'

        hists[(var,sample)] = rt.TH1D( hname, htitle, nbins, xmin, xmax )

        samplecut = cut
        if sample == "numu_sig":
            samplecut += " && "+signalcut
        elif sample == "numu_bg":
            samplecut += " && "+misidcut

        trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )

        if sample=='numu_sig':
            hname_effnum = f'h{var}_effnum'
            hists[(var,'effnum')] = rt.TH1D(hname_effnum,htitle,nbins,xmin,xmax)
            trees[sample].Draw(f"{truthvar}>>{hname_effnum}",f"({samplecut})*eventweight_weight")
            hists[(var,'effnum')].Scale( scaling[sample] )
        
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral()," scale-factor=",scaling[sample])

    if (var,'numu_sig') in hists:
        hists[(var,"numu_sig")].SetFillColor(rt.kRed-3)
        hists[(var,"numu_sig")].SetFillStyle(3003)
    if (var,'numu_bg') in hists:
        hists[(var,"numu_bg")].SetFillColor(rt.kBlue-3)
        hists[(var,"numu_bg")].SetFillStyle(3003)
    if (var,'extbnb') in hists:
        hists[(var,"extbnb")].SetFillColor(rt.kGray)
        hists[(var,"extbnb")].SetFillStyle(3144)
    if (var,'data') in hists:
        hists[(var,"data")].SetLineColor(rt.kBlack)
        hists[(var,"data")].SetLineWidth(2)

    hstack_name = f"hs_{var}"
    #hstack = rt.THStack(hstack_name,htitle)
    hstack = rt.THStack(hstack_name,"")
    if (var,'extbnb') in hists:
        hstack.Add( hists[(var,"extbnb")])
    if (var,'numu_sig') in hists:
        hstack.Add( hists[(var,"numu_sig")])
    if (var,'numu_bg') in hists:
        hstack.Add( hists[(var,"numu_bg")])

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
        #hstack.SetTitle(htitle)
        hstack.Draw("hist")
    else:
        if setlogy==1:
            hists[(var,"data")].GetYaxis().SetRangeUser(0.1,predmax*5)
        #hists[(var,"data")].SetTitle(htitle)
        hists[(var,"data")].Draw("E1")
        hstack.Draw("histsame")


    if (var,'data') in hists:
        hists[(var,"data")].Draw("E1same")

    # redraw delAlphaT to fix y-axis issue
    if var == 'numuCC1piNpReco_delAlphaT':
        # create pad1
        canvs[var].cd(1)
        pad1 = canvs[var].cd(1)
        pad1.Clear()

        # create new hist 
        frame_name = f"frame_{var}"
        frame = rt.TH1D(frame_name, htitle, nbins, xmin, xmax)

        # set y-axs
        frame.SetMinimum(0.0)
        frame.SetMaximum(50.0)

        frame.Draw("AXIS")
        hstack.Draw("HIST SAME")

        if (var, "data") in hists:
            hists[(var, "data")].Draw("E1 SAME")

        pad1.Modified()
        pad1.Update()

    canvs[var].cd(2)
    canvs[var].cd(2).SetGridx(1)
    canvs[var].cd(2).SetGridy(1)
    canvs[var].cd(2)

    # make purity plot
    hpur_name = f"h{var}_purity"
    hsum    = hists[(var,"numu_sig")].Clone( hpur_name+"_sum" )
    hpurity = hists[(var,"numu_sig")].Clone( hpur_name )
    htitle_split = htitle.split(";")
    print("htitle_split: ",htitle_split)
    if len(htitle_split)<=1:
        hpurity.SetTitle("Purity")
    if len(htitle_split)>=2:
        xaxis_title = htitle_split[1]                
        hpurity.SetTitle( f"Purity;{xaxis_title}" )
    if len(htitle_split)>=3:
        xaxis_title = htitle_split[1]        
        yaxis_title = htitle_split[2]
        hpurity.SetTitle( f"Purity;{xaxis_title};{yaxis_title}" )        
    hsum.Add( hists[(var,"numu_bg")] )
    hsum.Add( hists[(var,"extbnb")] )
    sigtot = hpurity.Integral()
    sumtot = hsum.Integral()
    overall_purity = sigtot/sumtot
    hpurity.Divide( hsum )
    for ibin in range(hpurity.GetXaxis().GetNbins()):
        x = hpurity.GetBinContent(ibin+1) # efficiency
        xm = hists[(var,'numu_sig')].GetBinContent(ibin+1)  # number of events in numerator
        xn = hsum.GetBinContent(ibin+1)  # number of events in denomenator
        if xn>0:
            err = sqrt( xm*(1-x) )/xn
        else:
            err = 0
        hpurity.SetBinError(ibin+1,err)
    
    hpurity.Draw("histE1")
    hpurity.GetYaxis().SetRangeUser(0.0,1.0)
    hists[(var,'purity')] = hpurity
    print(f"Overall Purity: {overall_purity:.2f}")

    canvs[var].cd(3)
    canvs[var].cd(3).SetGridx(1)
    canvs[var].cd(3).SetGridy(1)
    canvs[var].cd(3)
    heff = hists[(var,'effnum')]
    if len(htitle_split)<=1:
        heff.SetTitle("Efficiency")
    if len(htitle_split)>=2:
        xaxis_title = htitle_split[1]                
        heff.SetTitle( f"Efficiency;{xaxis_title}" )
    if len(htitle_split)>=3:
        xaxis_title = htitle_split[1]        
        yaxis_title = htitle_split[2]
        heff.SetTitle( f"Efficiency;{xaxis_title};{yaxis_title}" )        
    effnumer_tot = hists[(var,'effnum')].Integral()
    effdenom_tot = hists[((var,'effdenom'))].Integral()
    overall_eff = effnumer_tot/effdenom_tot
    hists[(var,'effnum')].Divide( hists[(var,'effdenom')])
    hists[(var,'effnum')].Draw("hist")
    hists[(var,'effnum')].GetYaxis().SetRangeUser(0,1.0)
    #hists[(var,'effdenom')].Draw("hist") #  for debug
    
    print(f"overall eff: {overall_eff:.2f}")
    canvs[var].Update()

    # save plots as pdf (for quality) 
    outdir = "plots"
    os.makedirs(outdir, exist_ok=True)
    canvs[var].SaveAs(f"{outdir}/reco_{var}_fixingDelAlphaT.png")
    

    

    #print("[enter] to continue")
    #input()

#print("[enter] to close")
#input()
