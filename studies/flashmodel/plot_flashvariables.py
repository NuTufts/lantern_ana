import os,sys
import ROOT as rt
rt.gStyle.SetOptStat(0)

output_plot_folder="./plots_flashvariables/"
os.system(f"mkdir {output_plot_folder}")

#rootfilepath = "./output_numu_run3b/mcc9_v29e_dl_run3b_bnb_nu_overlay_20251019_181154_nopescale.root"
rootfilepath = "./output_numu_run3b/mcc9_v29e_dl_run3b_bnb_nu_overlay_20251019_200712.root"
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
cfracerr.SaveAs(f"{output_plot_folder}/pe_fracerr.png")

# PE Total Plot
ctotpe = rt.TCanvas("ctotpe", "Total PE",800,600)
ctotpe.cd(1).SetGridy(1)
ctotpe.cd(1).SetGridx(1)

hnn_totpe = rt.TH1D("hnn_totpe",";total PE",100,0.0,15000.0)
hub_totpe = rt.TH1D("hub_totpe",";total PE",100,0.0,15000.0)
hnn_totpe.SetLineColor(rt.kRed)

analysis_tree.Draw("flashpred_nnmodel_totpe>>hnn_totpe",f"flashpred_nnmodel_totpe>=0.0 && ({numu_cut})")
analysis_tree.Draw("flashpred_ublm_totpe>>hub_totpe",f"flashpred_ublm_totpe>=0.0 && ({numu_cut})")
htotpe_max = 0.0
totpe_max = 0.0
for h in [hnn_totpe,hub_totpe]:
    if h.GetMaximum()>totpe_max:
        totpe_max = h.GetMaximum()
        htotpe_max = h
htotpe_max.Draw()
hnn_totpe.Draw("same")
hub_totpe.Draw("same")
ctotpe.Update()
ctotpe.SaveAs(f"{output_plot_folder}/totpe.png")

# PE per PMT
cpeperpmt = rt.TCanvas("cpeperpmt", "PE per PMT",800,600)
cpeperpmt.cd(1).SetGridy(1)
cpeperpmt.cd(1).SetGridx(1)

hnn_peperpmt = rt.TH1D("hnn_peperpmt",";PMT PE",50,0.0,1000.0)
hub_peperpmt = rt.TH1D("hub_peperpmt",";PMT PE",50,0.0,1000.0)
hnn_peperpmt.SetLineColor(rt.kRed)

analysis_tree.Draw("flashpred_nnmodel_pe_per_pmt>>hnn_peperpmt",f"flashpred_nnmodel_pe_per_pmt>=0.0 && ({numu_cut})")
analysis_tree.Draw("flashpred_ublm_pe_per_pmt>>hub_peperpmt",f"flashpred_ublm_pe_per_pmt>=0.0 && ({numu_cut})")
hpeperpmt_max = 0.0
peperpmt_max = 0.0
for h in [hnn_peperpmt,hub_peperpmt]:
    if h.GetMaximum()>peperpmt_max:
        peperpmt_max = h.GetMaximum()
        hpeperpmt_max = h
hpeperpmt_max.Draw()
hnn_peperpmt.Draw("same")
hub_peperpmt.Draw("same")
cpeperpmt.Update()
cpeperpmt.SaveAs(f"{output_plot_folder}/pe_per_pmt.png")

# PE per PMT: Low PE
clowpeperpmt = rt.TCanvas("clowpeperpmt", "Low PE per PMT",800,600)
clowpeperpmt.cd(1).SetGridy(1)
clowpeperpmt.cd(1).SetGridx(1)

hnn_lowpeperpmt = rt.TH1D("hnn_lowpeperpmt",";PMT PE (<10.0)",100,0.0,1.0)
hub_lowpeperpmt = rt.TH1D("hub_lowpeperpmt",";PMT PE (<10.0)",100,0.0,1.0)
hnn_lowpeperpmt.SetLineColor(rt.kRed)

analysis_tree.Draw("flashpred_nnmodel_pe_per_pmt>>hnn_lowpeperpmt",f"flashpred_nnmodel_pe_per_pmt>=0.0 && ({numu_cut})")
analysis_tree.Draw("flashpred_ublm_pe_per_pmt>>hub_lowpeperpmt",f"flashpred_ublm_pe_per_pmt>=0.0 && ({numu_cut})")
hlowpeperpmt_max = 0.0
lowpeperpmt_max = 0.0
for h in [hnn_lowpeperpmt,hub_lowpeperpmt]:
    if h.GetMaximum()>lowpeperpmt_max:
        lowpeperpmt_max = h.GetMaximum()
        hlowpeperpmt_max = h
hlowpeperpmt_max.Draw()
hnn_lowpeperpmt.Draw("same")
hub_lowpeperpmt.Draw("same")
clowpeperpmt.Update()
clowpeperpmt.SaveAs(f"{output_plot_folder}/lowpe_per_pmt.png")

# Diff PE per PMT
cdiffpmtpe = rt.TCanvas("cdiffpmtpe", "Difference PE per PMT",800,600)
cdiffpmtpe.cd(1).SetGridy(1)
cdiffpmtpe.cd(1).SetGridx(1)

hnn_diffpmtpe = rt.TH1D("hnn_diffpmtpe",";PMT PE difference (NN-UBLM)",1000,-50.0,50.0)
hnn_diffpmtpe.SetLineColor(rt.kRed)

analysis_tree.Draw("flashpred_nnmodel_pe_per_pmt-flashpred_ublm_pe_per_pmt>>hnn_diffpmtpe",f"flashpred_nnmodel_pe_per_pmt>=0.0 && ({numu_cut})")
hnn_diffpmtpe.Draw()
cdiffpmtpe.Update()
cdiffpmtpe.SaveAs(f"{output_plot_folder}/diff_pmtpe.png")


# BALANCED SINKHORN PLOT
cbalsinkdiv = rt.TCanvas("cbalsinkdiv", "Balanced Sinkhorn Divergence",800,600)
cbalsinkdiv.cd(1).SetGridy(1)
cbalsinkdiv.cd(1).SetGridx(1)

hnn_balsinkdiv = rt.TH1D("hnn_balsinkdiv",";balanced Sinkhorn Divergence",50,0.0,0.025)
hub_balsinkdiv = rt.TH1D("hub_balsinkdiv",";balanced Sinkhorn Divergence",50,0.0,0.025)
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
cbalsinkdiv.SaveAs(f"{output_plot_folder}/balanced_sinkhorn_divergence.png")

# UNBALANCED SINKHORN PLOT
cunbsinkdiv = rt.TCanvas("cunbsinkdiv", "Unbalanced Sinkhorn Divergences",800,600)
cunbsinkdiv.cd(1).SetGridy(1)
cunbsinkdiv.cd(1).SetGridx(1)

hnn_unbsinkdiv = rt.TH1D("hnn_unbsinkdiv",";unbalanced Sinkhorn Divergence",50,0.0,0.15)
hub_unbsinkdiv = rt.TH1D("hub_unbsinkdiv",";unbalanced Sinkhorn Divergence",50,0.0,0.15)
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
cunbsinkdiv.SaveAs(f"{output_plot_folder}/unbalanced_sinkhorn_divergence.png")


# UNBALANCED SINKHORN DIFF PLOT
cdiff_unbsinkdiv = rt.TCanvas("cdiff_unbsinkdiv", "Unbalanced Sinkhorn Divergence Difference",800,600)
cdiff_unbsinkdiv.cd(1).SetGridy(1)
cdiff_unbsinkdiv.cd(1).SetGridx(1)

hdiff_unbsinkdiv = rt.TH1D("hdiff_unbsinkdiv",";unbalanced Sinkhorn Divergence differnce",50,-0.2,0.2)
hdiff_unbsinkdiv.SetLineColor(rt.kRed)

analysis_tree.Draw("flashpred_nnmodel_unbalanced_sinkdiv-flashpred_ublm_unbalanced_sinkdiv>>hdiff_unbsinkdiv",f"flashpred_nnmodel_unbalanced_sinkdiv>=0.0 && ({numu_cut})")
hdiff_unbsinkdiv.Draw()
cdiff_unbsinkdiv.Update()
cdiff_unbsinkdiv.SaveAs(f"{output_plot_folder}/diff_unbalanced_sinkhorn.png")

# BALANCED SINKHORN DIFF PLOT
cdiff_balsinkdiv = rt.TCanvas("cdiff_sinkdiv", "Balanced Sinkhorn Divergence Difference",800,600)
cdiff_balsinkdiv.cd(1).SetGridy(1)
cdiff_balsinkdiv.cd(1).SetGridx(1)

hdiff_balsinkdiv = rt.TH1D("hdiff_balsinkdiv",";balanced Sinkhorn Divergence differnce",50,-0.03,0.03)
hdiff_balsinkdiv.SetLineColor(rt.kRed)

analysis_tree.Draw("flashpred_nnmodel_balanced_sinkdiv-flashpred_ublm_balanced_sinkdiv>>hdiff_balsinkdiv",f"flashpred_nnmodel_balanced_sinkdiv>=0.0 && ({numu_cut})")
hdiff_balsinkdiv.Draw()
cdiff_balsinkdiv.Update()
cdiff_balsinkdiv.SaveAs(f"{output_plot_folder}/diff_balanced_sinkhorn.png")


print("[enter] to exit")
input()
