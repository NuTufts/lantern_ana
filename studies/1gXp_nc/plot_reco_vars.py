import os,sys
import ROOT as rt


targetpot = 4.4e19
samples = ['1gXp']
#samples = ['nue','numu']
scaling = {"1gXp":targetpot/4.5221966264744385e+20}

#What files are we drawing on?
files = {"1gXp": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250612_142738.root"}
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
    ('vertex_properties_score',60,0.4,1.0,'keypoint score',0),
    ('leadingPhotonE',60,0, 700,'Leading Photon Energy (MeV)',0)
]

hists = {}
canvs = {}

#Cut based on basic vertex properties
cut = "(vertex_properties_found==1 && vertex_properties_infiducial)"
cut += " && (vertex_properties_cosmicfrac<0.15)"
cut += " && (vertex_properties_frac_intime_unreco_pixels<0.9)"

#Make sure we're dealing with events that meet our signal definition
cut += "&& (nphotons > 0)"
cut += "&& (nphotons < 3)"
cut += "&& (nProtons < 2)"
cut += "&& (nPions == 0)"
cut += "&& (nElectrons == 0)"
cut += "&& (nMuons == 0)"

#Cuts out most cosmics
cut += "&& (photonFromCharged > 5)"

#Now we actually go through and store the data
for var, nbins, xmin, xmax, htitle, setlogy in vars:

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {cname}",1000,800)
    canvs[var].Draw()

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )
        print("fill ",hname)

        #Sample-specific cuts...?
        samplecut = cut
        #if sample=="nue_sig":
        #    samplecut += " && (nueCCinc_is_target_nuecc_inclusive==1)"
        #elif sample=="nue_bg":
        #    samplecut += " && (nueCCinc_is_target_nuecc_inclusive!=1)"

        trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())

    #hists[(var,"nue_sig")].SetFillColor(rt.kRed)
    #hists[(var,"nue_sig")].SetFillStyle(3001)
    #hists[(var,"nue_bg")].SetFillColor(rt.kRed-4)
    #hists[(var,"nue_bg")].SetFillStyle(3001)

    #if (var,'data') in hists:
    #    hists[(var,"data")].SetLineColor(rt.kBlack)
    #    hists[(var,"data")].SetLineWidth(2)

    hstack_name = f"hs_{var}"
    hstack = rt.THStack(hstack_name,"")
    #if (var,'extbnb') in hists:
    #    hstack.Add( hists[(var,"extbnb")])
    #if (var,'numu') in hists:
    #    hstack.Add( hists[(var,"numu")])
    #if (var,'nue_bg') in hists:
    #    hstack.Add( hists[(var,"nue_bg")])
    #if (var,'nue_sig') in hists:
    #    hstack.Add( hists[(var,"nue_sig")])
    #hists[(hstack_name,sample)] = hstack

    hstack.Draw("hist")
    canvs[var].SetLogy(setlogy)

    predmax = hstack.GetMaximum()
    if (var,"data") in hists:
        datamax = hists[(var,"data")].GetMaximum()
    else:
        datamax = -1.0

    #if predmax>datamax:
    #    if setlogy==1:
    #        hstack.GetYaxis().SetRangeUser(0.1,predmax*5)
    #    hstack.SetTitle(htitle)
    #    hstack.Draw("hist")
    #else:
    #    if setlogy==1:
    #        hists[(var,"data")].GetYaxis().SetRangeUser(0.1,predmax*5)
    #    hists[(var,"data")].SetTitle(htitle)
    #    hists[(var,"data")].Draw("E1")
    #    hstack.Draw("histsame")

    #if (var,'data') in hists:
    #    hists[(var,"data")].Draw("E1same")

    canvs[var].Update()
    canvs[var].Write()

    #print("[enter] to continue")
    #input()


out.Write()

print("[enter] to close")
input()