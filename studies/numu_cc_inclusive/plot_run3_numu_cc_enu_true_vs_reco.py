import os,sys
import ROOT as rt

"""
"""

"""
"""
targetpot = 6.67e20
plot_folder="./output_plots_numu_run3/"
os.system(f"mkdir -p {plot_folder}")

samples = ['numu_cc']
scaling = {"numu_cc":targetpot/8.98323351831587e+20}

files = {
    "numu_cc":"./output_numu_run3b/mcc9_v29e_dl_run3b_bnb_nu_overlay_20251224_132737.root"
}

tfiles = {}
trees = {}

rt.gStyle.SetOptStat(0)
rt.gStyle.SetPadLeftMargin(0.15)
rt.gStyle.SetPadRightMargin(0.20)
rt.gStyle.SetPadBottomMargin(0.15)
rt.gStyle.SetPadTopMargin(0.05)

for sample in samples:
    tfiles[sample] = rt.TFile( files[sample] )
    trees[sample] = tfiles[sample].Get("analysis_tree")
    nentries = trees[sample].GetEntries()
    print(f"sample={sample} has {nentries} entries")

out = rt.TFile("temp.root","recreate")

vars = [
    ('henumu_reco_v_true',2,'vertex_properties_recoEnuMeV:(trueNu_Enu*1000.0)',30,0,3000,30,0,3000, ';true neutrino energy (MeV);reco. neutrino energy (MeV)', 0, False),
    ('henumu_Enufracerr_v_true',2,'(vertex_properties_recoEnuMeV-(trueNu_Enu*1000.0))/(trueNu_Enu*1000.0):(trueNu_Enu*1000.0)',30,0,3000,50,-1.0,1.0, ';true neutrino energy (MeV);fractional error (E_{reco}-E_{true})/E_{true}', 0, False),
]
hists = {}
canvs = {}

# Reco Cuts
cut = "vertex_properties_found==1"
cut += " && muon_properties_pid_score>-0.9"
cut += " && vertex_properties_infiducial==1"
cut += " && muon_properties_energy>0.0"
# Numu CC signal cut
cut += " && (sigdef_numuccinc_is_target_numucc_inclusive_nofvcut==1 && sigdef_numuccinc_dwalltrue>=5.0)"
# require 60% completeness on properly reco primary muon
#cut += " && muon_properties_primary_true_completeness>0.60"
#cut += " && muon_properties_endpt_dwall>5.0"

annotations = {}

for plot_config in vars:

    var = plot_config[0]

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {cname}",1400,1000)
    canvs[var].Draw()
    canvs[var].cd(1)
    canvs[var].cd(1).SetGridx(1)
    canvs[var].cd(1).SetGridy(1)

    for sample in samples:
        hname = f'h{var}_{sample}'
        print("fill ",hname)

        ndims = plot_config[1]
        if ndims==2:
            # TH2D plots
            varformula,nbinx,xmin,xmax,nbiny,ymin,ymax,title,setlog,xx = plot_config[2:]
            hist = rt.TH2D( hname, title, nbinx, xmin, xmax, nbiny, ymin, ymax )
        else:
            varformula,nbins,xmin,xmax,title,setlog,xx = plot_config[2:]
            hist = rt.TH1D( hname, "", nbins, xmin, xmax )

        hists[(var,sample)] = hist
        samplecut = cut

        trees[sample].Draw(f"{varformula}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )
        print(f"{var}-{sample}: ",hists[(var,sample)].Integral())
    

    canvs[var].cd(1).SetLogz(setlog)
    hists[(var,"numu_cc")].GetXaxis().SetTitleSize(0.05)
    hists[(var,"numu_cc")].GetYaxis().SetTitleSize(0.05)
    hists[(var,"numu_cc")].GetZaxis().SetTitleSize(0.05)
    hists[(var,"numu_cc")].GetZaxis().SetTitleOffset(1.3)
    hists[(var,"numu_cc")].Draw("colz")
    hists[(var,"numu_cc")].GetZaxis().SetTitle("events per 6.67#times 10^{20} POT")

    tline = rt.TLine(0.0,0.0,3000.0,3000.0)
    tline.SetLineWidth(2)
    tline.SetLineStyle(2)
    tline.Draw()
    annotations[f'line_{var}'] = tline

    canvs[var].Update()
    canvs[var].SaveAs(f"{plot_folder}/c{var}.png")

    print("[enter] to continue")
    #input()

print("[enter] to close")
input()
