import os,sys
import ROOT as rt

ntuple="kpreco_study_mcc9_v40a_dl_run1_bnb_intrinsic_nue_overlay_CV.root"
rfile = rt.TFile(ntuple,'read')
truekp = rfile.Get("truekp")
recokp = rfile.Get("recokp")

kptypes=['nu','shower','photon','tracks']
kptype_cuts = {"nu":"kptype==0",
               "shower":"kptype==3",
               "photon":"pid==22",
               "tracks":"kptype==1 || kptype==2"}

for kptype in kptypes:
    cut = kptype_cuts[kptype]

    # efficiency
    nkptype_all = truekp.GetEntries(cut)
    if cut in ['photon']:
        nkptype_selected = truekp.GetEntries(f"({cut}) && dist2ave<10.0")
    else:
        nkptype_selected = truekp.GetEntries(f"({cut}) && dist2ave<3.0")        
    print(kptype)
    print(" all: ",nkptype_all)
    print(" selected: ",nkptype_selected)
    eff = float(nkptype_selected)/float(nkptype_all)
    print(" efficiency: ",eff)
        


