import os,sys
import ROOT as rt

"""
This script is used to plot the spatial distribution of nu interaction and photon edep positions.
"""

targetpot = 1.32e21
samples = ['bnbnu_intpc','bnbnu_outtpc']
#samples = ['nue','numu']
# 4.675690535431973e+20 is Run 1 BNB Nu Overlay MC POT
scaling = {
    "bnbnu_intpc":targetpot/4.675690535431973e+20,
    "bnbnu_outtpc":targetpot/4.675690535431973e+20
}


#What files are we drawing on?
files = {
    "bnbnu_intpc": "./output_1g1X_vertexstudies/bnbnumu_20250829_103951.root",
    "bnbnu_outtpc": "./output_1g1X_vertexstudies/bnbnumu_20250829_103951.root"
}

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
    ('true_vertex_properties_dwall',50,-100,150.0,'Only 1 detectable Photon;true vertex dwall (cm)',0),
    ('true_vertex_properties_x',50,-100,400.0,'Only 1 detectable Photon;true nu vertex X position (cm)',0),
    ('true_vertex_properties_y',44,-220,220.0,'Only 1 detectable Photon;true nu vertex Y position (cm)',0), 
    ('true_vertex_properties_z',130,-100,1200.0,'Only 1 detectable Photon;true nu vertex Z position (cm)',0), 
    ('leadingEDepDwall',40,-50,150.0,'Leading EDep dwall (cm)',0),
    ('eDepMaxPlane',50,0,1000.0,'leading Energy Deposited - max plane edep (MeV)',0),
    ('recovtx_to_photonedep',150,0,150,'Only 1 detectable Photon;distance between reco vertex and true photon edep (cm)',1),
    ('recovtx_to_nuvtx',150,0,150,'Only 1 detectable Photon;distance between reco vertex and true photon edep (cm)',1),
    ('dist2vtx',150,0,150,'Only 1 detectable Photon;smallest distance between reco vertex and either true edep or nu vertex (cm)',1)
]

var_formula = {
    'dist2vtx':"TMath::Min(recovtx_to_photonedep,recovtx_to_nuvtx)"
}

hists = {}
hstack_v = {}
canvs = {}
tlegend = {}

signaldef = "nTruePhotons==1"
#signaldef += " && nOverThreshold==0"

#Cut based on basic vertex properties
#selection_cut = "vertex_properties_found==1"
#selection_cut += " && nphotons==1"
#selection_cut += " && nProtons==0"
#selection_cut += " && nPions==0"
#selection_cut += " && nElectrons==0"
#selection_cut += " && nMuons==0"
#selection_cut += " && TMath::IsNaN(vertex_properties_score)==0"

SIGDEF_TOTAL = 0.0

#Now we actually go through and store the data
for var, nbins, xmin, xmax, htitle, setlogy in vars:

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {var}",1000,500)
    canvs[var].Draw()

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )

        if "intpc" in sample:
            samplecut = f"({signaldef}) && true_vertex_properties_dwall>=0"
        elif "outtpc" in sample:
            samplecut = f"({signaldef}) && true_vertex_properties_dwall<0"

        if var in var_formula:
            fvar = var_formula[var]
        else:
            fvar = var
        
        trees[sample].Draw(f"{fvar}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].SetTitle( htitle )
        hists[(var,sample)].GetXaxis().SetTitleSize(0.06)
        hists[(var,sample)].GetXaxis().SetLabelSize(0.05)
        hists[(var,sample)].GetXaxis().SetTitleOffset(1.2)
        hists[(var,sample)].Scale( scaling[sample] )
        print("-"*80)
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
        print(samplecut)

    hists[(var,"bnbnu_intpc")].SetFillColor(rt.kRed-4)
    hists[(var,"bnbnu_intpc")].SetFillStyle(3001)

    hists[(var,"bnbnu_outtpc")].SetFillColor(rt.kBlue-4)
    hists[(var,"bnbnu_outtpc")].SetFillStyle(3001)

    #if (var,'data') in hists:
    #    hists[(var,"data")].SetLineColor(rt.kBlack)
    #    hists[(var,"data")].SetLineWidth(2)

    hstack_name = f"hs_{var}"
    hstack = rt.THStack(hstack_name,"")
    #if (var,'extbnb') in hists:
    #    hstack.Add( hists[(var,"extbnb")])
    #if (var,'numu') in hists:
    #    hstack.Add( hists[(var,"numu")])
    if (var,'bnbnu_intpc') in hists:
        hstack.Add( hists[(var,"bnbnu_intpc")])
    if (var,'bnbnu_outtpc') in hists:
        hstack.Add( hists[(var,"bnbnu_outtpc")])
    hstack.Draw("hist")

    hstack.GetHistogram().GetXaxis().SetLabelSize(0.05)
    hstack.GetHistogram().GetXaxis().SetTitleSize(0.06)
    hstack.GetHistogram().GetYaxis().SetTitleSize(0.06)
    hstack.GetHistogram().GetYaxis().SetLabelSize(0.05)
    hstack.GetHistogram().GetXaxis().SetTitleOffset(1.20)

    # custom title size for long title
    if var in ['dist2vtx']:
        hstack.GetHistogram().GetXaxis().SetTitleSize(0.05)
        hstack.GetHistogram().GetXaxis().SetTitleOffset(1.4)

    hists[(hstack_name,sample)] = hstack

    ntotal = 0
    for sample in samples:
        ntotal += hists[(var,sample)].Integral()

    if var=="true_vertex_properties_dwall":
        SIGDEF_TOTAL = ntotal

    tlen = rt.TLegend(0.6,0.6,0.9,0.9)
    tlen.AddEntry(hists[(var,"bnbnu_intpc")], "Nu Vertex in TPC","F")
    tlen.AddEntry(hists[(var,"bnbnu_outtpc")],"Nu Vertex out of TPC","F")
    tlen.AddEntry(0,"POT: %.2e"%(targetpot),"")
    tlen.AddEntry(0,"Entries: %.2f"%(ntotal),"")

    if var=="dist2vtx":
        # we customize the legend
        ibin_3cm = hists[(var,'bnbnu_intpc')].GetXaxis().FindBin(3.0)
        print("Bin at 3 cm: ",ibin_3cm)
        nevents_3cm_intpc = hists[(var,'bnbnu_intpc')].Integral(1,ibin_3cm)
        nevents_3cm_outtpc = hists[(var,'bnbnu_outtpc')].Integral(1,ibin_3cm)
        nevents_3cm = nevents_3cm_intpc+nevents_3cm_outtpc
        frac_in_3cm = float(nevents_3cm)/float(ntotal)
        vtx_eff = float(nevents_3cm)/float(SIGDEF_TOTAL)
        tlen.AddEntry(0,"Frac. within 3 cm: %.2f"%(frac_in_3cm),"")
        tlen.AddEntry(0,"Good Vertex Eff.: %.2f"%(vtx_eff),"")

    canvs[var].SetBottomMargin(0.2)


    hstack.SetTitle(htitle)
    hstack_v[var] = hstack

    tlen.Draw()
    tlegend[var] = tlen

    canvs[var].SetLogy(setlogy)
    
    #hists[(var,"bnbnu")].Draw("hist")

    canvs[var].Update()
    canvs[var].Write()
    canvs[var].SaveAs(f"onlyonedetphoton_{var}.png")


out.Write()

# Total
ntotal = 0
for sample in samples:
    ntotal += hists[('leadingEDepDwall',sample)].Integral()
print("Number of events: ",ntotal)

# quick estimate of vertex performance
ibin_3cm = hists[('dist2vtx','bnbnu_intpc')].GetXaxis().FindBin(5.0)
nevents_3cm_intpc = hists[('dist2vtx','bnbnu_intpc')].Integral(0,ibin_3cm)
nevents_3cm_outtpc = hists[('dist2vtx','bnbnu_outtpc')].Integral(0,ibin_3cm)
nevents_3cm = nevents_3cm_intpc+nevents_3cm_outtpc
print("Number of events with vertex within 3 cm of nu or edep vtx: ",nevents_3cm)
print("  out of tpc: ",nevents_3cm_outtpc)
print("  in tpc: ",nevents_3cm_intpc)

print("Target POT: ",targetpot)
print("[enter] to close")
input()
