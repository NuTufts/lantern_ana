import os,sys
import ROOT as rt

"""
"""

"""
"""
targetpot = 1.32e21
samples = ['numu_cc','data']
scaling = {"numu_cc":targetpot/7.881656209241413e+20,
           "data":targetpot/5.843739138271457e+20,
           #"data":targetpot/4.5221966264744385e+20,
           "numu_bg":targetpot/4.5221966264744385e+20,
           "nue":targetpot/1.0696499342682672e+22,
           "extbnb":0.47809891*0.80,
           #"data":1.0
}
files = {"numu_cc":"./output_numu_run4b/run4b_bnb_nu_overlay_surprise_20250821_065946.root",
         #"numu_cc":"./output_numu_run4b/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250821_075426.root",
         "data":"./output_numu_run4b/run3b_bnb_nu_overlay_500k_CV_20250821_080225.root",
         #"data":"./output_numu_run4b/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250821_075426.root",
         "numu_bg":"./output_numu_v3dev/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250529_141918.root",
         "extbnb":"./output_numu_run4b/run1_extbnb_mcc9_v29e_C1_20250821_074215.root",
         #"data":"./output_numu_run4b/run1_bnb5e19_20250821_072411.root"
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

vars = [('visible_energy', 30, 0, 3000, 'visible energy; MeV', 0),
        ('muon_properties_angle',50,-1.01,1.01,'muon angle; cos#theta_{beam}', 0),
        ('muon_properties_energy',50,0,2500.0,'muon kinetic energy (MeV)', 0),
        ('muon_properties_pid_score',101,-2,0.01,'muon pid score', 0),
        ('vertex_properties_score',40,0,1.0,'keypoint score', 0),
        #('nuselvar_mumax_primary_score',40,0,1.0,'primary score', 1),
        #('nuselvar_mumax_fromneutral_score',40,0,1.0,'from neutral parent score', 1),
        #('nuselvar_mumax_fromcharged_score',40,0,1.0,'from charged parent score', 1),
        #('nuselvar_mumax_mu_normedscore',40,0,1.0,'muon score (normalized)', 1),
        #('nuselvar_nMuTracks',20,0,20,'number of mu-like track-prongs',1),
        #('nuselvar_max_muscore',300,-2,1,'max mu-like score',1),
        #('nuselvar_vtx_cosmicfrac',50,0,1.01,'fraction of pixels near vertex',1),
        ('trueNu_Enu',50,0,5,'true neutrino energy; GeV',0),
        #('nuselvar_frac_outoftime_pixels',50,0,1.01,'fraction of recod pixels that are out of time',1),
        #('nuselvar_frac_intime_unreco_pixels',50,0,1.01,'fraction of intime pixels covered by recod interaction',1),
]
hists = {}
canvs = {}


cut = "vertex_properties_found==1"
cut += " && muon_properties_pid_score>-1.0"
cut += " && vertex_properties_infiducial==1"

for var, nbins, xmin, xmax, htitle, setlogy in vars:

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {cname}",1000,800)
    canvs[var].Draw()

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )
        print("fill ",hname)

        samplecut = cut
        if sample in ['numu_cc']:
            samplecut += " && (1==1)"
        elif sample in ['numu_bg']:
            samplecut += " && (1==1)"

        trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
    
    hists[(var,"numu_cc")].SetFillColor(rt.kRed-3)
    hists[(var,"numu_cc")].SetFillStyle(3003)
    #hists[(var,"numu_bg")].SetFillColor(rt.kBlue-3)
    #hists[(var,"numu_bg")].SetFillStyle(3003)
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
    #hstack.Add( hists[(var,"numu_bg")])
    hstack.Add( hists[(var,"numu_cc")])
    hists[(hstack_name,sample)] = hstack

    hstack.Draw("hist")
    canvs[var].SetLogy(setlogy)

    predmax = hstack.GetMaximum()
    if (var,'data') in hists:
        datamax = hists[(var,"data")].GetMaximum()
    else:
        datamax = 0

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
