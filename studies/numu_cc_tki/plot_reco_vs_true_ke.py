import os,sys
import ROOT as rt
from math import sqrt

"""
"""
targetpot = 4.4e19

#samples = ['numu_sig',"numu_bg","extbnb","data"]
samples = ['numu_sig']
plot_output_dir="./output_plots_true_vs_reco_ke/"
os.makedirs(plot_output_dir, exist_ok=True)
scaling = {
    "numu_sig":targetpot/4.5221966264744385e+20,
    "numu_bg":targetpot/4.5221966264744385e+20,
    "extbnb":(176222.0/372480),
    "data":1.0
}

files = {
    "numu_sig":"./output_tki_dev/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250912_122816.root",
    "numu_bg":"./output_tki_dev/run1_bnb_nu_overlay_mcc9_v28_wctagger_20250912_122816.root",
    "extbnb":"./output_tki_dev/run1_extbnb_mcc9_v29e_C1_20250912_095602.root",
    "data":"./output_tki_dev/run1_bnb5e19_20250912_095707.root"
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
    ('pionke_reco_vs_true', 50, 0.0, 500.0, 50, 0.0, 500.0, f'Charged Pion Reco vs True KE ({targetpot:.2e} POT);true KE (MeV);reco KE (MeV)', 0),
    ('muonke_reco_vs_true', 50, 0.0, 1000.0, 50, 0.0, 1000.0, f'Muon Reco vs True KE ({targetpot:.2e} POT);true KE (MeV);reco KE (MeV)', 0),
    ('protonke_reco_vs_true', 50, 0.0, 500.0, 50, 0.0, 500.0, f'Proton Reco vs True KE ({targetpot:.2e} POT);true max proton KE (MeV);reco max proton KE (MeV)', 0),    
]

var_formula = {
    'pionke_reco_vs_true':'numuCC1piNpReco_pionKE:numuCC1piNp_pionKE',
    'muonke_reco_vs_true':'numuCC1piNpReco_muKE:numuCC1piNp_muonKE',
    'protonke_reco_vs_true':'numuCC1piNpReco_maxprotonKE:numuCC1piNp_protonKE'        
}

hists = {}
canvs = {}
lines = {}

signalcut = "(numuCC1piNp_is_infv==1 && numuCC1piNp_is_target_cc_numu_1pi_nproton==1)"
misidcut  = "(numuCC1piNp_is_infv==0 || numuCC1piNp_is_target_cc_numu_1pi_nproton==0)"
cut = "numuCC1piNpReco_is_target_1mu1piNproton==1"
#cut = "numuCC1piNp_is_infv==1 && numuCC1piNp_muonKE>=0.050" # should be proxy for CCnumu with vertex in TPC


for var, nxbins, xmin, xmax, nybins, ymin, ymax, htitle, setlogz in vars:

    print("="*100)

    cname = f"c{var}"
    canvs[var] = rt.TCanvas(cname,f"v3dev: {cname}",2000,2000)
    canvs[var].Draw()
    canvs[var].cd(1)
    canvs[var].cd(1).SetGridx(1)
    canvs[var].cd(1).SetGridy(1)        

    for sample in samples:

        hname = f'h{var}_{sample}'

        hists[(var,sample)] = rt.TH2D( hname, htitle, nxbins, xmin, xmax, nybins, ymin, ymax )

        samplecut = cut
        if sample == "numu_sig":
            samplecut += " && "+signalcut
        elif sample == "numu_bg":
            samplecut += " && "+misidcut

        fvar = var_formula[var]

        trees[sample].Draw(f"{fvar}>>{hname}",f"({samplecut})*eventweight_weight")
        hists[(var,sample)].Scale( scaling[sample] )

        print(f"{var}-{sample}: ",hists[(var,sample)].Integral()," scale-factor=",scaling[sample])
    hists[(var,'numu_sig')].Draw("colz")

    diag = rt.TLine(xmin,ymin,xmax,ymax)
    diag.SetLineColor(rt.kBlack)
    diag.SetLineWidth(2)
    diag.SetLineStyle(2)
    diag.Draw()

    lines[var] = diag

    # save plots as pdf (for quality) 
    canvs[var].SaveAs(f"{plot_output_dir}/reco_{var}_tki.png")
    
    #print("[enter] to continue")
    #input()

print("[enter] to close")
input()
