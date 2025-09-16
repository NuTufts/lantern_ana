import os,sys
import ROOT as rt
from math import sqrt

rfile = rt.TFile("temp_covar.root")

histmodes = ['cv','w','w2','N']

stem = "visible_energy_run1_bnb_nu_overlay_mcc9_v28_wctagger"
hists = {}
for x in histmodes:
    hname = f"h{stem}_{x}"
    print(hname)
    hists[x] = rfile.Get(hname)
    
print(hists)
    
c = rt.TCanvas("c","c",1000,500)
c.Draw()
c.cd(1)
c.cd(1).SetGridx(1)
c.cd(1).SetGridy(1)

#hists['mean'] = hists['w'].Clone("mean")
#hists['mean'].Divide( hists['N'] )

#hists['Ew2'] = hists['w2'].Clone("Ew2")
#hists['Ew2'].Divide( hists['N'] )

#for ibin in range(1,hists['mean'].GetXaxis().GetNbins()+1):
#    xmean = hists['mean'].GetBinContent(ibin)
#    xxmean = hists['Ew2'].GetBinContent(ibin)
#    n = hists['N'].GetBinContent(ibin)
#    print(ibin,": ",xmean," ",xxmean," = ",xxmean-xmean*xmean)
#    #stddev = sqrt(xxmean - xmean*xmean)
#    #hists['mean'].SetBinError(ibin,stddev)

for k,h in hists.items():
    try:
        h.SetLineWidth(2)
    except:
        continue

# transfer the fractional error from the variations histogram, 'w', to the cv histogram
for ibin in range(1,hists['cv'].GetXaxis().GetNbins()+1):
    w = hists['w'].GetBinContent(ibin)
    werr = hists['w'].GetBinError(ibin)
    if w>0.0:
        ferr = werr/w
    else:
        ferr = 0.0
    cv = hists['cv'].GetBinContent(ibin)
    cv_err = cv*ferr
    print(f"[ibin] CV: {cv} +/- {cv_err} | W: {w} +/- {werr} | fracerr={ferr}")
    hists['cv'].SetBinError(ibin,cv_err)

hists['cv'].SetLineColor(rt.kBlue-4)
hists['cv'].SetFillColor(rt.kBlue-3)
hists['cv'].SetFillStyle(3002)
hists['N'].SetLineColor(rt.kGreen-4)
hists['w'].SetLineColor(rt.kRed-2)
hists['w'].SetLineColor(rt.kRed-2)


hists['cv'].Draw('E2')
hists['w'].Draw("histE1same")
#hists['N'].Draw("histsame")

c.Update()
print("[enter] to exit")
input()



