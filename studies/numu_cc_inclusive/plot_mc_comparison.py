import os,sys
import ROOT as rt

"""
Comparing MC Predictions between runs
"""

"""
"""
targetpot = 6.6e20
samples = ['run4b','run3b','run1']
scaling = {"run4b":targetpot/7.881656209241413e+20,
           "run3b":targetpot/5.843739138271457e+20,
           #"run3b":targetpot/9.65858292116677e+19,
           "run1":targetpot/4.675690535431973e+20
}

files = {
    "run4b":"./output_numu_run4b_weights/run4b_v10_04_07_09_BNB_nu_overlay_surprise_20250906_040103.root",
    "run3b":"./output_numu_run4b/run3b_bnb_nu_overlay_500k_CV_20250821_080225.root",
#    "run3b":"./output_numu_run3b/mcc9_v29e_dl_run3b_bnb_nu_overlay_20250906_051252.root",
     "run1":"./output_numu_run1/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250906_043957.root"
}
color = {
    'run4b':rt.kBlack,
    'run3b':rt.kBlue-3,
    'run1':rt.kRed-3
}

tfiles = {}
trees = {}
legends = {}

rt.gStyle.SetOptStat(0)

for sample in samples:
    tfiles[sample] = rt.TFile( files[sample] )
    trees[sample] = tfiles[sample].Get("analysis_tree")
    nentries = trees[sample].GetEntries()
    print(f"sample={sample} has {nentries} entries")

out = rt.TFile("temp.root","recreate")

vars = [
    ('visible_energy', 30, 0, 3000, 'visible energy; MeV', 0),
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
cut += " && muon_properties_pid_score>-0.9"
cut += " && vertex_properties_infiducial==1"
cut += " && muon_properties_energy>0.0"

for var, nbins, xmin, xmax, htitle, setlogy in vars:

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {cname}",1000,800)
    canvs[var].Draw()

    tlen = rt.TLegend(0.6,0.6,0.8,0.8)

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )
        hists[(var,sample)].SetLineWidth(2)
        print("fill ",hname)

        samplecut = cut
        if sample in ['run3b','run4b','run1']:
            samplecut += " && (sigdef_numuccinc_is_target_numucc_inclusive_nofvcut==1 && sigdef_numuccinc_dwalltrue>=5.0)"
        
        trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )
        hists[(var,sample)].SetLineColor(color[sample])
        
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
        tlen.AddEntry(hists[(var,sample)],sample,"L")
    
    legends[var] = tlen
    canvs[var].cd(1).SetLogy(setlogy)
    canvs[var].cd(1).SetGridx(1)
    canvs[var].cd(1).SetGridy(1)

    hists[(var,'run4b')].Draw("hist")
    hists[(var,'run3b')].Draw("histsame")
    hists[(var,'run1')].Draw("histsame")    
    tlen.Draw()

    canvs[var].Update()

    print("[enter] to continue")
    #input()

print("[enter] to close")
input()
