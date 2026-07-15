import ROOT as rt
f = rt.TFile("/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/systematics_output_run1_march2026_contained/output_xsecflux_tki_run1_march2026_contained_rebinned.root")
h = f.Get("hnumuCC1piNpReco_muKE_run1_bnb_nu_overlay_mcc9_v28_wctagger_cv")
for i in range(1, h.GetNbinsX()+2):
    print(f"bin {i}: lo={h.GetXaxis().GetBinLowEdge(i):.1f}")
