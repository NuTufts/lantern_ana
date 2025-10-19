import os,sys
import ROOT as rt
rt.gStyle.SetOptStat(0)

rootfilepath = "./output_numu_run3b/mcc9_v29e_dl_run3b_bnb_nu_overlay_20251019_181154.root"
rootfile = rt.TFile(rootfilepath)

analysis_tree = rootfile.Get('analysis_tree')

numu_cut = "vertex_properties_found==1 && muon_properties_pid_score>-0.9 && vertex_properties_infiducial==1 && muon_properties_energy>0.0"

# FRACTIONAL ERROR PLOT
cfracerr = rt.TCanvas("cfracerr", "Fractional Total PE Error",800,600)
cfracerr.cd(1).SetGridy(1)
cfracerr.cd(1).SetGridx(1)

hnn_pefrac = rt.TH1D("hnn_pefrac",";total PE fractional error",50,-1.0,1.5)
hub_pefrac = rt.TH1D("hub_pefrac",";total PE fractional error",50,-1.0,1.5)
hnn_pefrac.SetLineColor(rt.kRed)

analysis_tree.Draw("flashpred_nnmodel_fracpe>>hnn_pefrac",f"flashpred_nnmodel_fracpe>=-1.0 && ({numu_cut})")
analysis_tree.Draw("flashpred_ublm_fracpe>>hub_pefrac",f"flashpred_nnmodel_fracpe>=-1.0 && ({numu_cut})")
hpefrac_max = 0.0
pefrac_max = 0.0
for h in [hnn_pefrac,hub_pefrac]:
    if h.GetMaximum()>pefrac_max:
        pefrac_max = h.GetMaximum()
        hpefrac_max = h
hpefrac_max.Draw()
hnn_pefrac.Draw("same")
hub_pefrac.Draw("same")
cfracerr.Update()


# BALANCED SINKHORN PLOT
cbalsinkdiv = rt.TCanvas("cbalsinkdiv", "Balanced Sinkhorn Divergence",800,600)
cbalsinkdiv.cd(1).SetGridy(1)
cbalsinkdiv.cd(1).SetGridx(1)

hnn_balsinkdiv = rt.TH1D("hnn_balsinkdiv",";balanced Sinkhorn Divergence",50,0.0,0.05)
hub_balsinkdiv = rt.TH1D("hub_balsinkdiv",";balanced Sinkhorn Divergence",50,0.0,0.05)
hnn_balsinkdiv.SetLineColor(rt.kRed)

analysis_tree.Draw("flashpred_nnmodel_balanced_sinkdiv>>hnn_balsinkdiv",f"flashpred_nnmodel_balanced_sinkdiv>=0.0 && ({numu_cut})")
analysis_tree.Draw("flashpred_ublm_balanced_sinkdiv>>hub_balsinkdiv",f"flashpred_ublm_balanced_sinkdiv>=0.0 && ({numu_cut})")
hbalsinkdiv_max = None
balsinkdiv_max = 0.0
for h in [hnn_balsinkdiv,hub_balsinkdiv]:
    if h.GetMaximum()>balsinkdiv_max:
        balsinkdiv_max = h.GetMaximum()
        hbalsinkdiv_max = h
hbalsinkdiv_max.Draw()
hnn_balsinkdiv.Draw("same")
hub_balsinkdiv.Draw("same")
cbalsinkdiv.Update()

# UNBALANCED SINKHORN PLOT
cunbsinkdiv = rt.TCanvas("cunbsinkdiv", "Unbalanced Sinkhorn Divergences",800,600)
cunbsinkdiv.cd(1).SetGridy(1)
cunbsinkdiv.cd(1).SetGridx(1)

hnn_unbsinkdiv = rt.TH1D("hnn_unbsinkdiv",";unbalanced Sinkhorn Divergence",50,0.0,0.5)
hub_unbsinkdiv = rt.TH1D("hub_unbsinkdiv",";unbalanced Sinkhorn Divergence",50,0.0,0.5)
hnn_unbsinkdiv.SetLineColor(rt.kRed)

analysis_tree.Draw("flashpred_nnmodel_unbalanced_sinkdiv>>hnn_unbsinkdiv",f"flashpred_nnmodel_unbalanced_sinkdiv>=0.0 && ({numu_cut})")
analysis_tree.Draw("flashpred_ublm_unbalanced_sinkdiv>>hub_unbsinkdiv",f"flashpred_ublm_unbalanced_sinkdiv>=0.0 && ({numu_cut})")
hunbsinkdiv_max = None
unbsinkdiv_max = 0.0
for h in [hnn_unbsinkdiv,hub_unbsinkdiv]:
    if h.GetMaximum()>unbsinkdiv_max:
        unbsinkdiv_max = h.GetMaximum()
        hunbsinkdiv_max = h
hunbsinkdiv_max.Draw()
hnn_unbsinkdiv.Draw("same")
hub_unbsinkdiv.Draw("same")
cunbsinkdiv.Update()


print("[enter] to exit")
input()