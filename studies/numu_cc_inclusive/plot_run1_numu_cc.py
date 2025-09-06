import os,sys
import ROOT as rt

"""
"""

"""
"""
targetpot = 4.4e19
plot_folder="./output_plots_numu_run1/"
os.system(f"mkdir -p {plot_folder}")

samples = ['numu_cc','data','numu_bg','extbnb']
scaling = {"numu_cc":targetpot/4.675690535431973e+20,
           "numu_bg":targetpot/4.675690535431973e+20,
           "extbnb":0.47809891*0.80,
           "data":1.0
}

files = {
    "numu_cc":"./output_numu_run1/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250906_043957.root",
    "numu_bg":"./output_numu_run1/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250906_043957.root",
     "extbnb":"./output_numu_run1/run1_extbnb_mcc9_v29e_C1_20250906_043533.root",
       "data":"./output_numu_run1/run1_bnb5e19_20250906_043555.root",
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
    ('visible_energy', 30, 0, 3000, 'visible energy; MeV', 0, False),
    ('muon_properties_angle',16,-1.01,1.01,'muon angle; cos#theta_{beam}', 0, False),
    ('muon_properties_energy',50,0,2500.0,'muon kinetic energy (MeV)', 0, False),
    ('muon_properties_pid_score',101,-1.01,0.01,'muon pid score', 0, False),
    ('vertex_properties_score',30,0.7,1.0,'keypoint score', 0, False),
    ('eventweight_weight',200,0,10,';event weight;',0, True),
    #('nuselvar_mumax_primary_score',40,0,1.0,'primary score', 1),
    #('nuselvar_mumax_fromneutral_score',40,0,1.0,'from neutral parent score', 1),
    #('nuselvar_mumax_fromcharged_score',40,0,1.0,'from charged parent score', 1),
    #('nuselvar_mumax_mu_normedscore',40,0,1.0,'muon score (normalized)', 1),
    #('nuselvar_nMuTracks',20,0,20,'number of mu-like track-prongs',1),
    #('nuselvar_max_muscore',300,-2,1,'max mu-like score',1),
    #('nuselvar_vtx_cosmicfrac',50,0,1.01,'fraction of pixels near vertex',1),
    ('trueNu_Enu',50,0,5,'true neutrino energy; GeV',0, True),
    #('nuselvar_frac_outoftime_pixels',50,0,1.01,'fraction of recod pixels that are out of time',1),
    #('nuselvar_frac_intime_unreco_pixels',50,0,1.01,'fraction of intime pixels covered by recod interaction',1),
]
hists = {}
canvs = {}


cut = "vertex_properties_found==1"
cut += " && muon_properties_pid_score>-0.9"
cut += " && vertex_properties_infiducial==1"
cut += " && muon_properties_energy>0.0"

for var, nbins, xmin, xmax, htitle, setlogy, ismc in vars:

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {cname}",2000,800)
    canvs[var].Divide(2,1)
    canvs[var].Draw()
    canvs[var].cd(1)
    canvs[var].cd(1)
    canvs[var].cd(1).SetGridx(1)
    canvs[var].cd(1).SetGridy(1)

    for sample in samples:
        hname = f'h{var}_{sample}'
        hists[(var,sample)] = rt.TH1D( hname, "", nbins, xmin, xmax )
        print("fill ",hname)

        samplecut = cut
        if sample in ['numu_cc']:
            samplecut += " && (sigdef_numuccinc_is_target_numucc_inclusive_nofvcut==1 && sigdef_numuccinc_dwalltrue>=5.0)"
        elif sample in ['numu_bg']:
            samplecut += " && (sigdef_numuccinc_is_target_numucc_inclusive_nofvcut==0 || sigdef_numuccinc_dwalltrue<5.0)"

        trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
    
    hists[(var,"numu_cc")].SetFillColor(rt.kRed-3)
    hists[(var,"numu_cc")].SetFillStyle(3003)
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
    hstack = rt.THStack(hstack_name,"")
    hstack.Add( hists[(var,"numu_cc")])
    
    if (var,'extbnb') in hists:
        hstack.Add( hists[(var,"extbnb")])
    if (var,'numu_bg') in hists:
        hstack.Add( hists[(var,"numu_bg")])
        
    hists[(hstack_name,sample)] = hstack

    hstack.Draw("hist")
    canvs[var].SetLogy(setlogy)

    predmax = hstack.GetMaximum()
    if (var,'data') in hists:
        datamax = hists[(var,"data")].GetMaximum()
    else:
        datamax = 0

    if predmax>datamax or ismc:
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

    if not ismc and (var,'data') in hists:
        hists[(var,"data")].Draw("E1same")
    
    if not ismc:
        canvs[var].cd(2)
        canvs[var].cd(2).SetGridx(1)
        canvs[var].cd(2).SetGridy(1)
        hdataratio_name = hstack_name = f"hs_{var}_datamcratio"
        # copying histogram in order to inherit bin definitions, histogram axis labels
        hdataratio = hists[(var,"numu_cc")].Clone(hdataratio_name)
        hdataratio.Reset()
        hdataratio.SetFillStyle(0)
        hdataratio.SetFillColor(0)
        hdataratio.SetLineWidth(2)
        for ibin in range(1,hdataratio.GetXaxis().GetNbins()+1):
            bintotal = 0.0
            for sample in ['numu_cc','numu_bg','extbnb']:
                bintotal += hists[(var,sample)].GetBinContent(ibin)
            datatotal = hists[(var,'data')].GetBinContent(ibin)
            if bintotal>0.0:
                hdataratio.SetBinContent(ibin,datatotal/bintotal)
        hdataratio.Draw("hist")
        hdataratio.GetYaxis().SetTitle("data/MC ratio")

    canvs[var].Update()
    canvs[var].SaveAs(f"{plot_folder}/c{var}.png")

    print("[enter] to continue")
    #input()

print("[enter] to close")
input()
