import os,sys
import ROOT as rt
from math import sqrt

rt.gStyle.SetOptStat(0)

os.system('mkdir -p plots')

ntuple="kpreco_study_mcc9_v40a_dl_run1_bnb_intrinsic_nue_overlay_CV.root"
sampletag='mcc9_v40a_dl_run1_bnb_intrinsic_nue_overlay_CV_v3dev_easywave97k'

#ntuple="kpreco_study_mcc9_v28_wctagger_bnboverlay.root"
#sampletag='mcc9v28_wctagger_bnboverlay_v3dev_easywave97k'

rfile = rt.TFile(ntuple,'read')
truekp = rfile.Get("truekp")
recokp = rfile.Get("recokp")

#kptypes=['nu','shower','photon','tracks']
#kptypes=['photon']
kptypes=['nu','shower']

kptype_cuts = {"nu":"kptype==0",
               "shower":"kptype==3",
               "photon":"pid==22",
               "tracks":"kptype==1 || kptype==2"}

var_thrumu="(thrumu_pixsum[0]+thrumu_pixsum[1]+thrumu_pixsum[2])"
select_cut = "maxscore>0.5 && (thrumu_pixsum[0]+thrumu_pixsum[1]+thrumu_pixsum[2])<50.0"
canv = {}
hists = {}

def in_tpc( pos ):
    if pos[0]<0 and pos[0]>256.0:
        return False
    if pos[1]<-116.0 and pos[1]>116.0:
        return False
    if pos[2]<0.0 and pos[2]>1036.0:
        return False
    return True

def in_fv( pos, fv_dist ):
    if pos[0]<fv_dist and pos[0]>(256.0-fv_dist):
        return False
    if pos[1]<(-116.0+fv_dist) and pos[1]>(116.0-fv_dist):
        return False
    if pos[2]<fv_dist and pos[2]>(1036.0-fv_dist):
        return False
    return True

def get_in_fv_cutstr( fv_dist ):
    cut="("
    cut+=f" pos[0]>{fv_dist} && pos[0]<(256.0-{fv_dist})"
    cut+=f" && pos[1]>(-116.0+{fv_dist}) && pos[1]<(116.0-{fv_dist})"
    cut+=f" && pos[2]>{fv_dist} && pos[2]<(1036.0-{fv_dist})"
    cut+=" )"
    return cut

fv_cut = get_in_fv_cutstr(10.0)

for kptype in kptypes:
    cut = kptype_cuts[kptype]

    # TRUE KP PLOTS 
    

    # overall efficiency 
    nkptype_all = truekp.GetEntries(f"({cut})") # denominator    
    nkptype_fv = truekp.GetEntries(f"({cut}) && ({fv_cut})") # denominator
    nkptype_selected = truekp.GetEntries(f"({cut}) && ({fv_cut}) && ({select_cut})")
    print(kptype)
    print(" all of ",kptype,": ",nkptype_all)
    print(" ",kptype," in fv: ",nkptype_fv)    
    print(" selected: ",nkptype_selected)
    if nkptype_fv>0:
        eff = float(nkptype_selected)/float(nkptype_fv)
    else:
        eff = 0.0
    print(" efficiency: ",eff)

    # dist2true
    canv[(kptype,"dist2true")] = rt.TCanvas(f"cdist2true_{kptype}",f"Distance to nearest reco'd point: {kptype}",1200,800)
    canv[(kptype,"dist2true")].cd(1).SetLeftMargin(0.1)
    canv[(kptype,"dist2true")].cd(1).SetTopMargin(0.05)    
    canv[(kptype,"dist2true")].cd(1).SetBottomMargin(0.15) 
    kptrue_hname_dist2true = f"hdist2true_{kptype}_kptrue"
    hdist2true_kptrue = rt.TH1D(f"{kptrue_hname_dist2true}","",100,0,10)
    truekp.Draw(f"dist2max>>{kptrue_hname_dist2true}",f"({cut}) && ({fv_cut}) && ({select_cut})") # numerator of eff
    hdist2true_kptrue.SetLineWidth(4)
    hdist2true_kptrue.Draw("histE1")
    canv[(kptype,"dist2true")].Update()

    # efficiency vs. enu
    canv[(kptype,"eff")] = rt.TCanvas(f"ceff_{kptype}",f"Effiency: {kptype}",1200,800)
    canv[(kptype,"eff")].cd(1).SetLeftMargin(0.1)
    canv[(kptype,"eff")].cd(1).SetTopMargin(0.05)    
    canv[(kptype,"eff")].cd(1).SetBottomMargin(0.15)    
    
    hname_eff = f"heff_enu_{kptype}"
    heff_num = rt.TH1D(f"{hname_eff}","",50,0,3000)
    heff_den = rt.TH1D(f"{hname_eff}_nosel","",50,0,3000)
    truekp.Draw(f"enu>>{hname_eff}",f"({cut}) && ({fv_cut}) && ({select_cut})") # numerator of eff
    truekp.Draw(f"enu>>{hname_eff}_nosel",f"({cut}) && ({fv_cut})") # denominator of eff
    heff_num_N = heff_num.Clone(f'{hname_eff}_N') # make a copy to keep number of passing events in each bin
    heff_num.Divide(heff_den) # divide by denonminator
    for ibin in range(1,heff_num.GetXaxis().GetNbins()+1):
        m = heff_num_N.GetBinContent(ibin)
        n = heff_den.GetBinContent(ibin)
        if n>0:
            bineff = float(m)/float(n)
            err = sqrt(m*(1-bineff))/n
            heff_num.SetBinError( ibin, err )
    heff_num.Draw("histE1")
    heff_num.SetLineWidth(4)
    heff_num.SetTitle(";true E_{#nu} (MeV); efficiency (for %s keypoints)"%(kptype))
    heff_num.GetYaxis().SetRangeUser(0.0,1.0)
    heff_num.GetYaxis().SetNdivisions(1010)
    heff_num.GetXaxis().SetNdivisions(1010)
    heff_num.GetYaxis().SetTitleSize(0.05)
    heff_num.GetYaxis().SetTitleOffset(0.8)    
    heff_num.GetXaxis().SetTitleSize(0.05)
    heff_num.GetXaxis().SetTitleOffset(1.1)  
    hists[(kptype,'eff_enu')] = heff_num  
    canv[(kptype,"eff")].cd(1).SetGridx(1)
    canv[(kptype,"eff")].cd(1).SetGridy(1)    
    canv[(kptype,"eff")].Update()
    canv[(kptype,"eff")].SaveAs(f'plots/kpreco_{sampletag}_{kptype}_eff_vs_enu.png')

    # True KP: thrumu sum of matched keypoints
    cname_thrumu = f"ctruekp_thrumu_{kptype}"
    canv[(kptype,"truekp_thrumu")] = rt.TCanvas(cname_thrumu,cname_thrumu,1200,800)
    hname_true_thrumu = f"htruekp_thrumu_{kptype}"
    htrue_thrumu = rt.TH1D(hname_true_thrumu,"",100,0,1000)
    truekp.Draw(var_thrumu+">>"+hname_true_thrumu,f"({cut}) && ({fv_cut}) && maxscore>0.2") # low threshold
    hists[(kptype,'truekp_thrumu')] = htrue_thrumu
    canv[(kptype,"truekp_thrumu")].Update()

    # True KP: efficiency vs true particle KE
    canv[(kptype,"eff_partke")] = rt.TCanvas(f"ceff_{kptype}_partke",f"Effiency vs. particle KE: {kptype}",1200,800)
    canv[(kptype,"eff_partke")].cd(1).SetLeftMargin(0.1)
    canv[(kptype,"eff_partke")].cd(1).SetTopMargin(0.05)    
    canv[(kptype,"eff_partke")].cd(1).SetBottomMargin(0.15) 
    hname_eff_partke = f"heff_partke_{kptype}"
    heff_num_partke = rt.TH1D(f"{hname_eff_partke}","",50,0,1000)
    heff_den_partke = rt.TH1D(f"{hname_eff_partke}_nosel","",50,0,1000)
    truekp.Draw(f"partKE>>{hname_eff_partke}",f"({cut}) && ({fv_cut}) && ({select_cut})") # numerator of eff
    truekp.Draw(f"partKE>>{hname_eff_partke}_nosel",f"({cut}) && ({fv_cut})") # denominator of eff
    heff_num_N_partke = heff_num_partke.Clone(f'{hname_eff_partke}_N') # make a copy to keep number of passing events in each bin
    heff_num_partke.Divide(heff_den_partke) # divide by denonminator
    for ibin in range(1,heff_num_partke.GetXaxis().GetNbins()+1):
        m = heff_num_N_partke.GetBinContent(ibin)
        n = heff_den_partke.GetBinContent(ibin)
        if n>0:
            bineff = float(m)/float(n)
            err = sqrt(m*(1-bineff))/n
            heff_num_partke.SetBinError( ibin, err )
    heff_num_partke.Draw("histE1")
    heff_num_partke.SetLineWidth(4)
    heff_num_partke.SetTitle(";particle true KE (MeV); efficiency (for %s keypoints)"%(kptype))
    heff_num_partke.GetYaxis().SetRangeUser(0.0,1.0)
    heff_num_partke.GetYaxis().SetNdivisions(1010)
    heff_num_partke.GetXaxis().SetNdivisions(1010)
    heff_num_partke.GetYaxis().SetTitleSize(0.05)
    heff_num_partke.GetYaxis().SetTitleOffset(0.8)    
    heff_num_partke.GetXaxis().SetTitleSize(0.05)
    heff_num_partke.GetXaxis().SetTitleOffset(1.1)
    hists[(kptype,'eff_partke')] = heff_num_partke
    canv[(kptype,"eff_partke")].cd(1).SetGridx(1)
    canv[(kptype,"eff_partke")].cd(1).SetGridy(1)    
    canv[(kptype,"eff_partke")].Update()
    canv[(kptype,"eff_partke")].SaveAs(f'plots/kpreco_{sampletag}_{kptype}_eff_vs_partke.png')
    # True KP: ncluster of matched keypoints - need to add to tree
    #hname_true_ncluster = f"htruekp_ncluster_{kptype}"
    #htrue_ncluster = rt.TH1D(hname_true_ncluster,"",1000,0,1000)
    #cname_ncluster = f"ctruekp_ncluster_{kptype}"
    #canv[(kptype,"truekp_ncluster")] = rt.TCanvas(cname_ncluster, cname_ncluster, 1200, 800)
    #truekp.Draw("ncluster>>"+hname_true_ncluster,f"({cut}) && ({fv_cut}) && maxscore>0.2")
    #canv[(kptype,"truekp_ncluster")].Update()

    # reco tree stuff
    if kptype in ["photon","tracks"]:
        input()
        continue
    
    # max score vs. thrumu_sum split into good and bad
    hname_good = f"h{kptype}_thrumu_vs_max_good"
    h2_good = rt.TH2D(hname_good,f"{kptype} good",50,0.5,1.0,50,0,15e3)
    
    hname_bad = f"h{kptype}_thrumu_vs_max_bad"
    h2_bad = rt.TH2D(hname_bad,f"{kptype} bad",50,0.5,1.0,50,0,15e3)

    # thrumu cut 1D hist: only true selection with good/bad tag based on reco-closeness
    hname_thrumu = f'h{kptype}_thrumu'
    hthrumu_good = rt.TH1D(hname_thrumu+"_good",hname_thrumu+" good",250,0,5000)
    hthrumu_bad  = rt.TH1D(hname_thrumu+"_bad",hname_thrumu+"bad",250,0,5000)
    canv[(kptype,"thrumu")] = rt.TCanvas(f"c{kptype}_thrumu","Thrumu cut",1200,800)
    recokp.Draw(f"(thrumu_pixsum[0]+thrumu_pixsum[1]+thrumu_pixsum[2])>>{hname_thrumu}_good",f"({cut}) && dist2true<3.0")
    recokp.Draw(f"(thrumu_pixsum[0]+thrumu_pixsum[1]+thrumu_pixsum[2])>>{hname_thrumu}_bad", f"({cut}) && dist2true>3.0")
    hthrumu_good.SetLineColor(rt.kRed)
    hthrumu_bad.Draw("hist")
    hthrumu_good.Draw("histsame")
    canv[(kptype,"thrumu")].SetLogx(1)
    canv[(kptype,"thrumu")].SetLogy(1)    
    canv[(kptype,"thrumu")].Update()    
    canv[(kptype,"thrumu")].Draw()

    # maxscore: after thrumu cut with good/bad tag
    hname_maxscore = f'h{kptype}_maxscore'
    hmaxscore_good = rt.TH1D(hname_maxscore+"_good",hname_maxscore+" good",100,0,1.0)
    hmaxscore_bad  = rt.TH1D(hname_maxscore+"_bad",hname_maxscore+"bad",100,0,1.0)
    canv[(kptype,"maxscore")] = rt.TCanvas(f"c{kptype}_maxscore","Maxscore cut",1200,800)
    recokp.Draw(f"maxscore>>{hname_maxscore}_good",f"({cut}) && {var_thrumu}<50.0 && dist2true<3.0")
    recokp.Draw(f"maxscore>>{hname_maxscore}_bad", f"({cut}) && {var_thrumu}<50.0 && dist2true>3.0")
    hmaxscore_good.SetLineColor(rt.kRed)
    hmaxscore_good.Draw("hist")
    hmaxscore_bad.Draw("histsame")
    canv[(kptype,"maxscore")].SetLogy(1)
    canv[(kptype,"maxscore")].Update()    
    canv[(kptype,"maxscore")].Draw()

    # Reco KP: nspacepoints for reco keypoints
    hname_reco_ncluster = f"hrecokp_ncluster_{kptype}"
    hreco_ncluster_good = rt.TH1D(hname_reco_ncluster+"_good","",1000,0,1000)
    hreco_ncluster_bad  = rt.TH1D(hname_reco_ncluster+"_bad","",1000,0,1000)    
    cname_reco_ncluster = f"crecokp_ncluster_{kptype}"
    canv[(kptype,"recokp_ncluster")] = rt.TCanvas(cname_reco_ncluster, cname_reco_ncluster, 1200, 800)
    recokp.Draw("nclusterpts>>"+hname_reco_ncluster+"_good",f"({cut}) && {var_thrumu}<50.0 && dist2true<3.0")
    recokp.Draw("nclusterpts>>"+hname_reco_ncluster+"_bad",f"({cut}) && {var_thrumu}<50.0 && dist2true>3.0")
    hreco_ncluster_bad.SetLineWidth(2)
    hreco_ncluster_good.SetLineWidth(2)
    hreco_ncluster_good.SetLineColor(rt.kRed)
    hreco_ncluster_bad.Draw("hist")
    hreco_ncluster_good.Draw("histsame")
    canv[(kptype,"recokp_ncluster")].Update()
    

    # reduction by  thrumu cut
    n_with_thrumu_cut = recokp.GetEntries(f"({cut}) && {var_thrumu}<50.0")
    

    # TH2D
    canv[(kptype,"2d")] = rt.TCanvas(f"c{kptype}",f"{kptype}: cosmic pixel sum vs. max kp score",1200,800)    
    recokp.Draw(f"(thrumu_pixsum[0]+thrumu_pixsum[1]+thrumu_pixsum[2]):maxscore>>{hname_good}",f"({cut}) && dist2true<3.0")
    recokp.Draw(f"(thrumu_pixsum[0]+thrumu_pixsum[1]+thrumu_pixsum[2]):maxscore>>{hname_bad}",f"({cut}) && dist2true>3.0")
    h2_good.SetLineColor(rt.kRed)
    h2_good.Draw("box")
    h2_bad.Draw("boxsame")
    canv[(kptype,"2d")].Update()

    input()


    
