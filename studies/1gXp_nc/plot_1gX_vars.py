import os,sys
import ROOT as rt


targetpot = 4.4e19
samples = ['bnbnu_sig','bnbnu_bg']
#samples = ['nue','numu']
scaling = {"bnbnu_sig":targetpot/4.5221966264744385e+20,
           "bnbnu_bg":targetpot/4.5221966264744385e+20}

#What files are we drawing on?
files = {"bnbnu_sig": "output/bnbnumu_20250703_184910.root",
         "bnbnu_bg":  "output/bnbnumu_20250703_184910.root"}
tfiles = {}
trees = {}

rt.gStyle.SetOptStat(0)

#Iterate over files, get trees and events and whatnot
for sample in samples:
    tfiles[sample] = rt.TFile( files[sample] ) #Assign a file using the dictionary
    trees[sample] = tfiles[sample].Get("analysis_tree") #Extract the ttree from that file
    nentries = trees[sample].GetEntries() #Extract the number of entries from the tree
    print(f"sample={sample} has {nentries} entries")

#Assign our output file
out = rt.TFile("temp.root","recreate")

#Whip up our histograms
vars = [
    ('trueLeadingPhotonDwall',40,-50,150.0,'true photon start pos dwall (cm)',0),
    ('vertex_properties_score',50,0,1.0,'keypoint score',0)
]

hists = {}
canvs = {}

signaldef = "nTruePhotons==1"
signaldef += " && nOverThreshold==0"

#Cut based on basic vertex properties
selection_cut = "vertex_properties_found==1"
selection_cut += " && nphotons==1"
selection_cut += " && nProtons==0"
selection_cut += " && nPions==0"
selection_cut += " && nElectrons==0"
selection_cut += " && nMuons==0"
selection_cut += " && TMath::IsNaN(vertex_properties_score)==0"

#Now we actually go through and store the data
for var, nbins, xmin, xmax, htitle, setlogy in vars:

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {var}",1000,800)
    canvs[var].Draw()

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )
        samplecut = selection_cut
        if sample=="bnbnu_sig":
            samplecut = f"({samplecut}) && ({signaldef})"
        elif sample=="bnbnu_bg":
            samplecut = f"({samplecut}) && !({signaldef})"
        else:
            raise ValueError(f"Unrecognized sample: {sample}")

        trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )
        print("------------------------------------------------")
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
        print(samplecut)

    hists[(var,"bnbnu_sig")].SetFillColor(rt.kRed-4)
    hists[(var,"bnbnu_sig")].SetFillStyle(3001)
    hists[(var,"bnbnu_bg")].SetFillColor(rt.kBlue-6)
    hists[(var,"bnbnu_bg")].SetFillStyle(3001)

    #if (var,'data') in hists:
    #    hists[(var,"data")].SetLineColor(rt.kBlack)
    #    hists[(var,"data")].SetLineWidth(2)

    hstack_name = f"hs_{var}"
    hstack = rt.THStack(hstack_name,"")
    #if (var,'extbnb') in hists:
    #    hstack.Add( hists[(var,"extbnb")])
    #if (var,'numu') in hists:
    #    hstack.Add( hists[(var,"numu")])
    if (var,'bnbnu_bg') in hists:
        hstack.Add( hists[(var,"bnbnu_bg")])
    if (var,'bnbnu_sig') in hists:
       hstack.Add( hists[(var,"bnbnu_sig")])
    hists[(hstack_name,sample)] = hstack

    hstack.Draw("hist")
    canvs[var].SetLogy(setlogy)
    #hists[(var,"bnbnu")].Draw("hist")

    canvs[var].Update()
    canvs[var].Write()


out.Write()

print("[enter] to close")
input()
