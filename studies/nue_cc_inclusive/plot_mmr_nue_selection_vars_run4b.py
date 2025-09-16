import os,sys
import ROOT as rt

"""
2025-05-25 04:35:20,426 - LanternAna - INFO - Loaded dataset 'run1_bnb_nue_overlay_mcc9_v28_wctagger' with 14804 entries
2025-05-25 04:35:20,427 - LanternAna - INFO -   MC dataset with 1.7586890825003933e+22 POT
Adding to dataset[EventTree] to Tree[EventTree]: /home/twongjirad/working/larbys/gen2/container_u20_env/work/lantern_ana/ntuple_mcc9_v28_wctagger_bnboverlay_v3dev_reco_retune.root
2025-05-25 04:35:20,454 - LanternAna - INFO - Loaded dataset 'run1_bnb_nu_overlay_mcc9_v28_wctagger' with 69741 entries
2025-05-25 04:35:20,454 - LanternAna - INFO -   MC dataset with 1.7458035848006284e+20 POT
Adding to dataset[EventTree] to Tree[EventTree]: /home/twongjirad/working/larbys/gen2/container_u20_env/work/lantern_ana/ntuple_mcc9_v29e_dl_run1_C1_extbnb_v3dev_reco_retune.root
2025-05-25 04:35:20,471 - LanternAna - INFO - Loaded dataset 'run1_extbnb_mcc9_v29e_C1' with 42147 entries
Adding to dataset[EventTree] to Tree[EventTree]: /home/twongjirad/working/larbys/gen2/container_u20_env/work/lantern_ana/ntuple_mcc9_v28_wctagger_bnb5e19_v3dev_reco_retune.root
2025-05-25 04:35:20,542 - LanternAna - INFO - Loaded dataset 'run1_bnb5e19' with 176222 entries
2025-05-25 04:35:20,542 - LanternAna - INFO - Processing dataset: run1_extbnb_mcc9_v29e_C1
2025-05-25 04:35:20,572 - LanternAna - INFO - Processing 42147 events...
"""

"""
"""
targetpot = 1.3e+20
samples = ['nue','numu','extbnb','data']
#samples = ['nue','data']
scaling = {"numu":targetpot/7.881656209241413e+20,
           "nue":targetpot/1.1785765118473412e+23,
           "extbnb":23090946.0/94414115.0,
           "data":1.0}
files = {
    "numu":"./output_nue_run4b_surprise/run4b_v10_04_07_09_BNB_nu_overlay_surprise.root",
    "nue":"./output_nue_run4b_surprise/run4b_v10_04_07_09_BNB_nue_overlay_surprise.root",
    "extbnb":"./output_nue_run4b_surprise/run4b_v10_04_07_09_extbnb.root",
    "data":"./output_nue_run4b_surprise/run4b_beamon.root"
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

vars = [('eventweight_weight',200,0,10,'event weight',0),
    ('recoElectron_emax_econfidence', 40, 0, 20,'electron confidence score',0),
    ('recoElectron_emax_primary_score',40,0,1.0,'primary score',0),
    ('recoElectron_emax_fromneutral_score',40,0,1.0,'from neutral parent score',0),
    ('recoElectron_emax_fromcharged_score',40,0,1.0,'from charged parent score',0),
    ('recoElectron_emax_el_normedscore',40,0,1.0,'electron-like score (normalized)',0),
    ('recoMuonTrack_nMuTracks',20,0,20,'num of muon-like tracks',0),
    ('recoMuonTrack_max_muscore',50,-20,0.5,'max mu-like score',0),
    ('vertex_properties_score',60,0.4,1.0,'keypoint score',0),
    ('vertex_properties_cosmicfrac',50,0,1.01,'fraction of cosmic pixel near vertex',0),
    ('visible_energy',15,0,3000,'visible energy; MeV',0)
]

hists = {}
canvs = {}

cut = "vertex_properties_infiducial==1"
cut += " && vertex_properties_cosmicfrac<1.0"
cut += " && recoMuonTrack_nMuTracks==0"
cut += " && (recoElectron_has_primary_electron==1 && recoElectron_emax_primary_score>recoElectron_emax_fromcharged_score && recoElectron_emax_primary_score>recoElectron_emax_fromneutral_score)"
cut += " && (recoMuonTrack_max_muscore<-3.7)"
cut += " && (recoElectron_emax_econfidence>7.0)"


for var, nbins, xmin, xmax, htitle, setlogy in vars:

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v2me06: {cname}",1000,800)
    canvs[var].Draw()

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )
        print("fill ",hname)
        #trees[sample].Draw(f"{var}>>{hname}",f"({cut})*eventweight_weight")
        trees[sample].Draw(f"{var}>>{hname}",f"({cut})") # for debug: do not use GENIE tune
        hists[(var,sample)].Scale( scaling[sample] )
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
    
    hists[(var,"nue")].SetFillColor(rt.kRed)
    hists[(var,"nue")].SetFillStyle(3001)
    hists[(var,"numu")].SetFillColor(rt.kBlue-3)
    hists[(var,"numu")].SetFillStyle(3003)
    hists[(var,"extbnb")].SetFillColor(rt.kGray)
    hists[(var,"extbnb")].SetFillStyle(3144)
    hists[(var,"data")].SetLineColor(rt.kBlack)
    hists[(var,"data")].SetLineWidth(2)

    hstack_name = f"hs_{var}"
    hstack = rt.THStack(hstack_name,"")
    hstack.Add( hists[(var,"extbnb")])
    hstack.Add( hists[(var,"numu")])
    hstack.Add( hists[(var,"nue")])
    hists[(hstack_name,sample)] = hstack

    hstack.Draw("hist")

    predmax = hstack.GetMaximum()
    datamax = hists[(var,"data")].GetMaximum()

    if predmax>datamax:
        hstack.SetTitle(htitle)
        hstack.Draw("hist")
    else:
        hists[(var,"data")].SetTitle(htitle)
        hists[(var,"data")].Draw("E1")
        hstack.Draw("histsame")

    hists[(var,"data")].Draw("E1same")

    canvs[var].SetLogy(setlogy)
    canvs[var].Update()
    canvs[var].SaveAs(f'output_mmr/plot_v2me06_mmr_{cname}.png')

    print("[enter] to continue")
    #input()

print("[enter] to close")
# input()
