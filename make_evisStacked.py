import ROOT as rt

"""
TFile**		analysis_evisStacked_stacked_histograms.root	
 TFile*		analysis_evisStacked_stacked_histograms.root	
  KEY: TH1F	h_prod_evisStacked_numuCC0p0pi0x;1	Reco Visible Energy
  KEY: TH1F	h_prod_evisStacked_numuCC1p0pi0x;1	Reco Visible Energy
  KEY: TH1F	h_prod_evisStacked_numuCCMp0pi0x;1	Reco Visible Energy
  KEY: TH1F	h_prod_evisStacked_NC;1	Reco Visible Energy
  KEY: TH1F	h_prod_evisStacked_nueCC;1	Reco Visible Energy
  KEY: TH1F	h_prod_evisStacked_uncategorized;1	Reco Visible Energy
"""

var_v=["evisStacked","trueEnuStacked"]
cut_configs = ["reco","truesig","both"]
modes = ["numuCC0p0pi0x","numuCC1p0pi0x","numuCCMp0pi0x","NC","nueCC","uncategorized"]

files = {}
hists = {}

#folder="./v3dev/"
folder="./v2me06/"

# get all the hists
for var in var_v:
    for cutname in cut_configs:
        finput = rt.TFile(f"{folder}/analysis_{var}_{cutname}_stacked_histograms.root")
        files[(var,cutname)] = finput
        for n,mode in enumerate(modes):
            hname = f'h_prod_{var}_{cutname}_{mode}'
            h = finput.Get(hname)
            hists[(var,cutname,mode)] = h
            if n==0:
                # make a "tot" histogram
                htotname = f"h_prod_{var}_{cutname}_total"
                htot = h.Clone(htotname)
                htot.Reset()
                hists[(var,cutname,"total")] = htot
            hists[(var,cutname,"total")].Add(h)

for label,h in hists.items():
    print(label,": ",h.Integral())


# Plot stack: reco
hstack_evis = rt.THStack()
for mode in modes:
    hstack_evis.Add( hists[('evisStacked','reco',mode)] )
cevis = rt.TCanvas("cRecoEvis","cRecoEvis",800,600)
cevis.Draw()
hstack_evis.Draw("hist")
cevis.Update()

# Plot stack: trueEnu
hstack_enu = rt.THStack()
for mode in modes:
    hstack_enu.Add( hists[('trueEnuStacked','truesig',mode)] )
cenu = rt.TCanvas("cTrueEnu","cTrueEnu",800,600)
cenu.Draw()
hstack_enu.Draw("hist")
cenu.Update()

out = rt.TFile("out.root","recreate")

# Make Efficiency and purity
# start with numerator histogram
heff = hists[("trueEnuStacked","both","total")].Clone("heff") 
hpur = hists[("evisStacked","both","total")].Clone("hpurity")

# divide by denominator histogram
heff.Divide( hists[("trueEnuStacked","truesig","total")])
hpur.Divide( hists[("evisStacked","reco","total")])

for hh in [heff,hpur]:
    for ibin in range(hh.GetXaxis().GetNbins()):
        x = hh.GetBinContent(ibin+1)
        err = x*(1-x) # simple binomial error
        hh.SetBinError(ibin+1,err)

ceff = rt.TCanvas("ceff","",800,600)
ceff.Draw()
heff.SetTitle("#nu_#muCC-inclusive efficiency;true E_{#nu} (GeV);efficiency")
heff.Draw("histE1")
ceff.Update()

cpur = rt.TCanvas("pur","",800,600)
hpur.SetTitle("#nu_#muCC-inclusive purity;reco E_{vis} (MeV);purity")
cpur.Draw()
hpur.Draw("histE1")
cpur.Update()

out.cd()
heff.Write()
hpur.Write()

print("[enter] to exit")
input()
        
