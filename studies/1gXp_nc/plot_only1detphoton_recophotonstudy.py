import os,sys
import ROOT as rt


targetpot = 1.32e21
boost = 1.0
plot_folder = "./output_plots_only1detphoton_backgrounds/"
os.system(f"mkdir -p {plot_folder}")
samples = ['bnbnu_1gXp_sig_goodvtx','bnbnu_1gXp_sig_badvtx','bnbnu_0g_bg','bnbnu_Mg_bg']
scaling = {
    "bnbnu_1gXp_sig_goodvtx":boost*targetpot/4.675690535431973e+20,
    "bnbnu_1gXp_sig_badvtx":targetpot/4.675690535431973e+20,
    "bnbnu_0g_bg":targetpot/4.675690535431973e+20,
    "bnbnu_Mg_bg":targetpot/4.675690535431973e+20,
}

good_vtx_threshold = 3.0

# What files are we drawing on?
#  Deriving from ntuple_mcc9_v28_wctagger_bnboverlay_v3dev_reco_retune_nuvtxphotonsel_vtest.root
#  using 1gXp_vertex_ana.yaml
lantern_ana_file="bnbnumu_20250905_105804.root"
files = {
    "bnbnu_1gXp_sig_goodvtx": "./output_1g1X_vertexstudies/"+lantern_ana_file,
    "bnbnu_1gXp_sig_badvtx": "./output_1g1X_vertexstudies/"+lantern_ana_file,
    "bnbnu_0g_bg": "./output_1g1X_vertexstudies/"+lantern_ana_file,
    "bnbnu_Mg_bg": "./output_1g1X_vertexstudies/"+lantern_ana_file
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
    ('notrackphoton_truepid',10,0,10.0,';category of highest true par',0),
    ('notrackphoton_recoPhScore',1000,0,1.0,';category of highest true par',0),
]

var_formula = {
    'dist2vtx':"TMath::Min(recovtx_to_photonedep,recovtx_to_nuvtx)",
    'recophoton_photon_purity':"recophoton_recoPur[0]",
    'recophoton_photon_completeness':"recophoton_recoComp[0]",
    'notrackphoton_photon_purity':"notrackphoton_recoPur[0]",
    'notrackphoton_photon_completeness':"notrackphoton_recoComp[0]",
    'notrackphoton_recoPhScore':'TMath::Exp(notrackphoton_recoPhScore)'
}

hists = {}
hstack_v = {}
canvs = {}
tlegend = {}

segment_def = {
    "bnbnu_1gXp_sig_goodvtx":"nTruePhotons==1 && TMath::Min(recovtx_to_photonedep,recovtx_to_nuvtx)<%.2f"%(good_vtx_threshold),
    "bnbnu_1gXp_sig_badvtx":"nTruePhotons==1 && TMath::Min(recovtx_to_photonedep,recovtx_to_nuvtx)>%.2f"%(good_vtx_threshold),
    "bnbnu_0g_bg":"nTruePhotons==0",
    "bnbnu_Mg_bg":"nTruePhotons>1",
}

segment_color = {
    "bnbnu_1gXp_sig_goodvtx":rt.kRed,
    "bnbnu_1gXp_sig_badvtx":rt.kOrange,
    "bnbnu_0g_bg":rt.kGray,
    "bnbnu_Mg_bg":rt.kBlue-2
}

sample_legend = {
    "bnbnu_1gXp_sig_goodvtx":"1gX (signal), good vtx reco.",
    "bnbnu_1gXp_sig_badvtx":"1gX (signal), bad vtx reco.",
    "bnbnu_0g_bg":"0 gamma (background)",
    "bnbnu_Mg_bg":">1 gamma (background)"
}

# signaldef = "nTruePhotons==1"
#signaldef += " && nOverThreshold==0"

#Cut based on basic vertex properties
selection_cut = "vertex_properties_found==1 && vertex_properties_dwall>0.0"
selection_cut += " && notrackphoton_leadingPhotonE>30.0"
selection_cut += " && vertex_properties_sinkhorn_div<30.0"
selection_cut += " && vertex_properties_fracerrPE<0.0"
selection_cut += " && notrackphoton_entryused==1"
selection_cut += " && TMath::Exp(notrackphoton_recoPhScore)>0.8"

#selection_cut += " && vertex_properties_frac_intime_unreco_pixels>0.02"
#selection_cut += " && notrackphoton_recoComp[0]>0.5"
#selection_cut += " && notrackphoton_nphotons==1"

# selection_cut += " && vertex_properties_frac_outoftime_pixels>0.8"
# 

# selection_cut += " && TMath::IsNaN(vertex_properties_score)==0"

#Now we actually go through and store the data
for var, nbins, xmin, xmax, htitle, setlogy in vars:

    print("="*80)
    print("VARIABLE: ",var)

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {var}",1000,500)
    canvs[var].Draw()

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )

        segment_cut = segment_def[sample]

        samplecut = f"({segment_cut}) && ({selection_cut})"

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
        hists[(var,sample)].SetFillColor( segment_color[sample] )
        hists[(var,sample)].SetFillStyle( 3003 )
        print("-"*80)
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
        print(samplecut)

    #if (var,'data') in hists:
    #    hists[(var,"data")].SetLineColor(rt.kBlack)
    #    hists[(var,"data")].SetLineWidth(2)

    hstack_name = f"hs_{var}"
    hstack = rt.THStack(hstack_name,"")
    tlen = rt.TLegend(0.6,0.6,0.85,0.85)

    #if (var,'extbnb') in hists:
    #    hstack.Add( hists[(var,"extbnb")])
    #if (var,'numu') in hists:
    #    hstack.Add( hists[(var,"numu")])
    for sample in samples:
        if (var,sample) in hists:
            hstack.Add( hists[(var,sample)])
            tlen.AddEntry(hists[(var,sample)], "%s: %.2f"%(sample_legend[sample],hists[(var,sample)].Integral()),"F")

    hstack.Draw("hist")
    hstack.GetHistogram().GetXaxis().SetLabelSize(0.05)
    hstack.GetHistogram().GetXaxis().SetTitleSize(0.06)
    hstack.GetHistogram().GetYaxis().SetTitleSize(0.06)
    hstack.GetHistogram().GetYaxis().SetLabelSize(0.05)
    hstack.GetHistogram().GetXaxis().SetTitleOffset(1.20)

    hists[(hstack_name,sample)] = hstack

    ntotal = 0
    for sample in samples:
        ntotal += hists[(var,sample)].Integral()
    print("TOTAL: ",ntotal)



    # tlen.AddEntry(hists[(var,"bnbnu_intpc")], "Nu Vertex in TPC","F")
    # tlen.AddEntry(hists[(var,"bnbnu_outtpc")],"Nu Vertex out of TPC","F")
    # tlen.AddEntry(0,"POT: %.2e"%(targetpot),"")
    # tlen.AddEntry(0,"Entries: %.2f"%(ntotal),"")

    canvs[var].SetBottomMargin(0.2)


    hstack.SetTitle(htitle)
    hstack_v[var] = hstack

    tlen.Draw()
    tlegend[var] = tlen

    canvs[var].SetLogy(setlogy)
    
    #hists[(var,"bnbnu")].Draw("hist")

    canvs[var].Update()
    canvs[var].Write()
    canvs[var].SaveAs(f"{plot_folder}/{var}.png")


out.Write()

# quick estimate of vertex performance
#ibin_3cm = hists[('dist2vtx','bnbnu_intpc')].GetXaxis().FindBin(5.0)
#nevents_3cm_intpc = hists[('dist2vtx','bnbnu_intpc')].Integral(0,ibin_3cm)
#nevents_3cm_outtpc = hists[('dist2vtx','bnbnu_outtpc')].Integral(0,ibin_3cm)
#nevents_3cm = nevents_3cm_intpc+nevents_3cm_outtpc
#print("Number of events with vertex within 3 cm of nu or edep vtx: ",nevents_3cm)
#print("  out of tpc: ",nevents_3cm_outtpc)
#print("  in tpc: ",nevents_3cm_intpc)

print("Target POT: ",targetpot)
print("[enter] to close")
input()
