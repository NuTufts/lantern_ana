import os,sys
import ROOT as rt


"""
"""
targetpot = 4.4e19
signal_factor = 1.0
samples = ['nue_sig','nue_bg','numu','extbnb','data']
#samples = ['nue','numu']
scaling = {"numu":targetpot/4.5221966264744385e+20,
           "nue_sig":targetpot/1.059100558499451e+22*signal_factor,
           "nue_bg":targetpot/1.0696499342682672e+22,
           "extbnb":(176222.0/368589)*0.8,
           "data":1.0}
files = {"numu":   "./output_with_flashdev/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250617_142741.root",
         "nue_sig":"./output_with_flashdev/run1_bnb_nue_overlay_mcc9_v28_wctagger_20250617_142445.root",
         "nue_bg": "./output_with_flashdev/run1_bnb_nue_overlay_mcc9_v28_wctagger_20250617_142445.root",
         "extbnb": "./output_with_flashdev/run1_extbnb_mcc9_v29e_C1_20250617_143455.root",
         "data":   "./output_with_flashdev/run1_bnb5e19_20250617_143733.root"}
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
    ('vertex_properties_score',60,0.4,1.0,'keypoint score',0),
    ('vertex_properties_cosmicfrac',50,0,1.01,'fraction of pixels near vertex',0),
    ('vertex_properties_frac_outoftime_pixels',50,0,1.01,'fraction of reco pixels labed out of time',1),
    ('vertex_properties_frac_intime_unreco_pixels',50,0,1.01,'fraction of unreco\'d pixels in event are in-time',1),
    ('recoElectron_emax_econfidence', 40, 0, 20, 'electron confidence', 1),
    ('recoElectron_emax_primary_score',40,0,1.0,'primary score', 1),
    ('recoElectron_emax_fromneutral_score',40,0,1.0,'from neutral parent score', 1),
    ('recoElectron_emax_fromcharged_score',40,0,1.0,'from charged parent score', 1),
    ('recoElectron_emax_el_normedscore',40,0,1.0,'electron score (normalized)', 1),
    ('recoElectron_emax_charge',100,0,1000e3,'electron charge',1),
    ('visible_energy',15,0,3000,'visible energy; MeV', 0),
    ('recoMuonTrack_nMuTracks',20,0,20,'number of mu-like track-prongs',0),
    ('recoMuonTrack_max_muscore',42,-20,1,'max mu-like score',1),
    ('recoMuonTrack_max_mucharge',100,0,100e3,'max mu-like charge',1),
    ('flashpred_sinkhorn_div',200,0,100,'sinkhorn divcergence',1),
    ('flashpred_fracerr',240,-2,10,'fractional error',1),
    ('vertex_properties_dwall',100,-5,200,'dwall',0),
]

hists = {}
canvs = {}

# Loose cuts
# cut = "(vertex_properties_found==1 && vertex_properties_infiducial)"
# cut += " && (flashpred_fracerr>-0.95 && flashpred_fracerr<3.0)"
# cut += " && (flashpred_sinkhorn_div<40.0)"
# cut += " && (vertex_properties_frac_outoftime_pixels>0.5)"
# cut += " && (recoMuonTrack_max_muscore<-1.0)"
# cut += " && (recoElectron_emax_primary_score>0.1)"
# cut += " && (vertex_properties_frac_intime_unreco_pixels<0.95)"

cut = "(vertex_properties_found==1 && vertex_properties_infiducial)"
cut += " && (flashpred_fracerr>-0.95 && flashpred_fracerr<3.0)"
cut += " && (flashpred_sinkhorn_div<40.0)"
cut += " && (vertex_properties_frac_outoftime_pixels>0.50)"
cut += " && (recoMuonTrack_max_muscore<-3.0)"
cut += " && (recoElectron_emax_primary_score>0.7)"
cut += " && (vertex_properties_frac_intime_unreco_pixels<0.95)"
cut += " && (recoElectron_emax_charge>1.0e3)"
cut += " && (recoElectron_emax_econfidence>5.0)"
cut += " && (recoElectron_emax_fromcharged_score<0.10)"
cut += " && (recoElectron_emax_el_normedscore>0.9)"
#cut += " && (vertex_properties_cosmicfrac<0.40)"
cut += " && (vertex_properties_score>0.80)"
cut += " && (recoElectron_emax_fromcharged_score<0.05)"
cut += " && (vertex_properties_frac_outoftime_pixels>0.90)"
cut += " && (recoElectron_emax_fromneutral_score<0.15)"
#cut += " && (vertex_properties_frac_intime_unreco_pixels<0.5)"


# 

# 



for var, nbins, xmin, xmax, htitle, setlogy in vars:

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {cname}",1000,800)
    canvs[var].Draw()

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )
        print("fill ",hname)

        samplecut = cut
        if sample=="nue_sig":
            samplecut += " && (nueCCinc_is_target_nuecc_inclusive_nofvcut==1 && nueCCinc_dwalltrue>=5.0)"
        elif sample=="nue_bg":
            samplecut += " && (nueCCinc_is_target_nuecc_inclusive_nofvcut!=1 || nueCCinc_dwalltrue<5.0)"

        trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
    
    hists[(var,"nue_sig")].SetFillColor(rt.kRed)
    hists[(var,"nue_sig")].SetFillStyle(3001)
    hists[(var,"nue_bg")].SetFillColor(rt.kRed-4)
    hists[(var,"nue_bg")].SetFillStyle(3001)
    if (var,'numu') in hists:
        hists[(var,"numu")].SetFillColor(rt.kBlue-3)
        hists[(var,"numu")].SetFillStyle(3003)
    if (var,'extbnb') in hists:
        hists[(var,"extbnb")].SetFillColor(rt.kGray)
        hists[(var,"extbnb")].SetFillStyle(3144)
    if (var,'data') in hists:
        hists[(var,"data")].SetLineColor(rt.kBlack)
        hists[(var,"data")].SetLineWidth(2)

    hstack_name = f"hs_{var}"
    hstack = rt.THStack(hstack_name,"")
    if (var,'extbnb') in hists:
        hstack.Add( hists[(var,"extbnb")])
    if (var,'numu') in hists:
        hstack.Add( hists[(var,"numu")])
    if (var,'nue_bg') in hists:
        hstack.Add( hists[(var,"nue_bg")])
    if (var,'nue_sig') in hists:
        hstack.Add( hists[(var,"nue_sig")])
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
    canvs[var].Write()

    print("[enter] to continue")
    #input()

print("[enter] to close")
input()
