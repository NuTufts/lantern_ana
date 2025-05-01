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

cut_configs = ["reco","truesig","both"]
modes = ["numuCC0p0pi0x","numuCC1p0pi0x","numuCCMp0pi0x","NC","nueCC","uncategorized"]

files = {}
hists = {}

# get all the hists
for cutname in cut_configs:
    finput = rt.TFile(f"analysis_evisStacked_{cutname}_stacked_histograms.root")
    files[cutname] = finput
    for n,mode in enumerate(modes):
        hname = f'h_prod_evisStacked_{cutname}_{mode}'
        h = finput.Get(hname)
        hists[(cutname,mode)] = h
        if n==0:
            # make a "tot" histogram
            htotname = f"h_prod_evisStacked_{cutname}_total"
            htot = h.Clone(htotname)
            htot.Reset()
            hists[(cutname,"total")] = htot
        hists[(cutname,"total")].Add(h)

for label,h in hists.items():
    print(label,": ",h.Integral())


# Make stack: reco
hstack = rt.THStack()
for mode in modes:
    hstack.Add( hists[('reco',mode)] )
c = rt.TCanvas("c","c",800,600)
c.Draw()
hstack.Draw()
c.Update()

# Make Efficiency and purity
heff = hists[("both","total")].Clone("heff")
hpur = hists[("both","total")].Clone("hpurity")

heff.Divide( hists[("truesig","total")])
hpur.Divide( hists[("reco","total")])

for hh in [heff,hpur]:
    for ibin in range(hh.GetXaxis().GetNbins()):
        x = hh.GetBinContent(ibin+1)
        err = x*(1-x) # simple binomial error
        hh.SetBinError(ibin+1,err)

ceff = rt.TCanvas("ceff","",800,600)
ceff.Draw()
heff.Draw("histE1")
ceff.Update()

cpur = rt.TCanvas("pur","",800,600)
cpur.Draw()
hpur.Draw("histE1")
cpur.Update()

print("[enter] to exit")
input()
        
