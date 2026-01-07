import os,sys
import ROOT as rt

"""
/exp/uboone/app/users/zarko/getDataInfo.py -v3 -d MCC9.10_Test_Samples_v10_04_07_03_Run4b_super_unified_reco2_BNB_beam_on_reco2_hist
Definition MCC9.10_Test_Samples_v10_04_07_03_Run4b_super_unified_reco2_BNB_beam_on_reco2_hist contains 348 files
           EXT         Gate2        E1DCNT        tor860        tor875   E1DCNT_wcut   tor860_wcut   tor875_wcut
    38291055.0    11700180.0    11592705.0     4.614e+19     4.614e+19    10928307.0     4.498e+19     4.498e+19
"""

"""
/exp/uboone/app/users/zarko/getDataInfo.py -v3 -d MCC9.10_Test_Samples_v10_04_07_03_Run4b_super_unified_reco2_BNB_beam_off_reco2_hist
Definition MCC9.10_Test_Samples_v10_04_07_03_Run4b_super_unified_reco2_BNB_beam_off_reco2_hist contains 833 files
           EXT         Gate2        E1DCNT        tor860        tor875   E1DCNT_wcut   tor860_wcut   tor875_wcut
    29875806.0    10431318.0    10345859.0     4.192e+19     4.192e+19     9740417.0      4.08e+19      4.08e+19
"""

end1cnt_run4a = 10928307.0
pot_run4a   = 4.498e+19
ext_beamoff = 29875806.0

targetpot = pot_run4a
plot_folder="./plots_numu_run4a_surprise/"
os.system(f"mkdir -p {plot_folder}")

samples = ['numu_cc','numu_bg','numu_dirt','data','extbnb']
scaling = {"numu_cc":targetpot/2.3593114985024402e+20,
           "numu_bg":targetpot/2.3593114985024402e+20,
           "numu_dirt":targetpot/1.088128052604017e+20,           
           "extbnb":end1cnt_run4a/ext_beamoff,
           "data":1.0
}


anafile_folder="./output_numu_run4a_surprise/"
files = {
    "numu_cc":"./output_numu_run4a_surprise/run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_20260107_103745.root",
    "numu_bg":"./output_numu_run4a_surprise/run4a4c4d5_v10_04_07_13_BNB_nu_overlay_surprise_20260107_103745.root",
    "numu_dirt":"./output_numu_run4a_surprise/run4a4c4d5_v10_04_07_13_BNB_dirt_overlay_surprise_20260107_105003.root",
     "extbnb":"./output_numu_run4a_surprise/run4a4c4d5_v10_04_07_13_BNB_beam_off_data_surprise_20260107_105432.root",
       "data":"./output_numu_run4a_surprise/run4a4c4d5_v10_04_07_13_BNB_beam_on_data_surprise_20260107_105513.root",
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
    ('muon_properties_pid_score',41,-1.01,0.01,'muon pid score', 0, False),
    ('vertex_properties_score',30,0.7,1.0,'keypoint score', 0, False),
    ('eventweight_weight',150,0,15.0,';event weight;',1, True),
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
        elif sample in ['numu_dirt']:
            samplecut += ""

        trees[sample].Draw(f"{var}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
    
    hists[(var,"numu_cc")].SetFillColor(rt.kRed-3)
    hists[(var,"numu_cc")].SetFillStyle(3003)
    if (var,'numu_bg') in hists:
        hists[(var,"numu_bg")].SetFillColor(rt.kBlue-3)
        hists[(var,"numu_bg")].SetFillStyle(3003)
    if (var,'numu_dirt') in hists:
        hists[(var,"numu_dirt")].SetFillColor(rt.kOrange-7)
        hists[(var,"numu_dirt")].SetFillStyle(3003)
    if (var,'extbnb') in hists:
        hists[(var,"extbnb")].SetFillColor(rt.kGray)
        hists[(var,"extbnb")].SetFillStyle(3144)
    if (var,'data') in hists:
        hists[(var,"data")].SetLineColor(rt.kBlack)
        hists[(var,"data")].SetLineWidth(2)

    hstack_name = f"hs_{var}"
    hstack = rt.THStack(hstack_name,"")
    hstack.Add( hists[(var,"numu_cc")])
    
    if (var,'numu_bg') in hists:
        hstack.Add( hists[(var,"numu_bg")])
    if (var,'numu_dirt') in hists:
        hstack.Add( hists[(var,"numu_dirt")])        
    if (var,'extbnb') in hists:
        hstack.Add( hists[(var,"extbnb")])
        
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
            for sample in ['numu_cc','numu_bg','extbnb','numu_dirt']:
                if (var,sample) in hists:
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
