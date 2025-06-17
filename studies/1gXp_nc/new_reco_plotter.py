import os,sys
import ROOT as rt


targetpot = 4.4e19
samples = ['Montecarlo',"Off-Beam","Beam Data"]
scaling = {
    "Montecarlo":targetpot/4.5221966264744385e+20,
    "Off-Beam":176222.0/368589,
    "Beam Data":targetpot/4.4e19
    }

sidebands = ['1g0X', '1g1p', '1g2p', '1g1u', '1gXpi', '2g0X', '2g1p', '2g2p', '2g1u', '2gXpi']

sidebandCuts = {'1g0X': "&& (oneGnoX == 1)",
    'oneGnoX': "&& (oneGnoX == 1)",
    'oneGoneP': "&& (oneGoneP == 1)",
    'oneGtwoP': "&& (oneGtwoP == 1)",
    'oneGoneMu': "&& (oneGoneMu == 1)",
    'oneGxPi': "&& (oneGxPi == 1)",
    'twoGnoX': "&& (twoGnoX == 1)",
    'twoGoneP': "&& (twoGoneP == 1)",
    'twoGtwoP': "&& (twoGtwoP == 1)",
    'twoGoneMu': "&& (twoGoneMu == 1)",
    'twoGxPi': "&& (twoGxPi == 1)"
    }

categories = ['Signal', 'WrongSideband', 'Background']
categoryCuts = {'Signal': "&& (isSignal == 1)",
    'Background': "&& (isBackground == 1)",
    'WrongSideband': "&& (isWrongSideband == 1)"
    }


#What files are we drawing on?
files = {
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250617_153237.root",
    "Off-Beam": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/extbnb_20250617_154125.root",
    "Beam Data": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/beamData_20250617_154325.root"
}


tfiles = {}
trees = {}

rt.gStyle.SetOptStat(0)

#Iterate over files, get trees and events and whatnot
for sample in samples:
    tfiles[sample] = rt.TFile( files[sample] ) #Assign a file using the dictionary
    trees[sample] = tfiles[sample].Get("analysis_tree") #Extract the ttree from that file
    nentries = trees[sample].GetEntries() #Extract the number of entries from the tree
    print(f"sample={sample} has {nentries} entries")

#Assign our output file
out = rt.TFile("temp.root","recreate")

#Whip up our histograms
vars = [
    ("leadingPhotonE",60,0, 700,'2g2p Sample',"Reco", 0)
]

graphingVar = "leadingPhotonE"

nBins = 60
xMin = 0
xMax = 700

sidebands = [
    ("oneGnoX",nBins, xMin, xMax,'1g0X Sample',"Reco", 0),
    ("oneGoneP",nBins, xMin, xMax,'1g1p Sample',"Reco", 0),
    ("oneGtwoP",nBins, xMin, xMax,'1g2p Sample',"Reco", 0),
    ("oneGoneMu",nBins, xMin, xMax,'1g1u Sample',"Reco", 0),
    ("oneGxPi",nBins, xMin, xMax,'1gXpi Sample',"Reco", 0),
    ("twoGnoX",nBins, xMin, xMax,'2g0X Sample',"Reco", 0),
    ("twoGoneP",nBins, xMin, xMax,'2g1p Sample',"Reco", 0),
    ("twoGtwoP",nBins, xMin, xMax,'2g2p Sample',"Reco", 0),
    ("twoGoneMu",nBins, xMin, xMax,'2g1u Sample',"Reco", 0),
    ("twoGxPi",nBins, xMin, xMax,'2gXpi Sample',"Reco", 0)
]

hists = {}
canvs = {}

#CUT LIST
#Cut based on basic vertex properties
cut = "(vertex_properties_found==1 && vertex_properties_infiducial)"
cut += " && (vertex_properties_cosmicfrac<0.15)"
cut += " && (vertex_properties_frac_intime_unreco_pixels<0.9)"

#Make sure we're dealing with events that meet our signal definition
#cut += "&& (nphotons > 0)"
#cut += "&& (nphotons < 3)"
#cut += "&& (nProtons == 0)"
#cut += "&& (nPions == 0)"
#cut += "&& (nElectrons == 0)"
#cut += "&& (nMuons == 0)"

#Cuts out most cosmics
cut += "&& (photonFromCharged > 5)"


#Now we actually go through and store the data
for sideband, nbins, xmin, xmax, htitle, dataType, protonNo in sidebands:
    #Define our canvas (what we draw everything on) and our legend
    cname = f"c{sideband}"
    canvs[sideband] = rt.TCanvas(cname,f"v3dev: {cname}",1000,800)
    canvs[sideband].Draw()
    legend = rt.TLegend(0.5, 0.5, 0.9, 0.9)

    #We use these to color our histograms
    colors = [rt.kGreen, rt. kBlue,  rt. kOrange+1, rt.kViolet+3, rt.kRed, rt.kCyan, rt.kMagenta, rt.kYellow+1, rt.kBlack, rt.kViolet]
    colorIndex = 0 

    stack = rt.THStack(f"hs_{sideband}", f"{htitle}")

    #BEGIN WITH THE MONTECARLO DATA
    sample = "Montecarlo"

    #Apply cuts, fill histogram
    sidebandCut = cut
    sidebandCut += sidebandCuts[sideband]
    #We have to fill in a special histogram for each category
    for category in categories:
        hname = f'{sample}_{sideband}_{category}'
        legendName = f'{category}'
        hists[(sideband,category)] = rt.TH1D(hname, "", nbins, xmin, xmax )
        print("fill ",hname)

        categoryCut = sidebandCut + categoryCuts[str(category)]

        trees[sample].Draw(f"{graphingVar}>>{hname}",f"({categoryCut})*eventweight_weight") #Execute all cuts
        hists[(sideband,category)].Scale(scaling[sample])
        
        #Make it look pretty
        hists[(sideband,category)].SetLineColor(rt.kBlack)
        hists[(sideband,category)].SetFillColor(colors[colorIndex%9])
        colorIndex += 1

        #Add histogram to the legend
        bins = hists[(sideband,category)].GetNbinsX()
        histInt = hists[(sideband,category)].Integral(1, int(bins))
        legend.AddEntry(hists[(sideband,category)], str(legendName)+": "+str(round(histInt, 1)), "f")

        stack.Add(hists[(sideband,category)])


    #HANDLE THE OFF-BEAM DATA
    sample = "Off-Beam"
    #Define our histogram
    hname = f'{sample}_{sideband}'
    hists[(sideband,sample)] = rt.TH1D(hname, "", nbins, xmin, xmax )
    print("fill ",hname)

    #Apply cuts, fill histogram
    trees[sample].Draw(f"{graphingVar}>>{hname}",f"({sidebandCut})*eventweight_weight") #Execute all cuts
    hists[(sideband,sample)].Scale(scaling[sample])
        
    #Make it look pretty
    hists[(sideband,sample)].SetLineColor(rt.kBlack)
    hists[(sideband,sample)].SetFillColor(colors[colorIndex%9])
    colorIndex += 1

    #Add histogram to the legend
    bins = hists[(sideband,sample)].GetNbinsX()
    histInt = hists[(sideband,sample)].Integral(1, int(bins))
    legendName = "Off-Beam (Cosmic)"
    legend.AddEntry(hists[(sideband,sample)], str(legendName)+": "+str(round(histInt, 1)), "f")

    stack.Add(hists[(sideband,sample)])

    #Now we overlay the data
    #Set up the histogram
    sample = "Beam Data"
    hname = f"Beam_Data_{sideband}"
    hists[(sideband,sample)] = rt.TH1D(hname, "", 60,0, 700 )
    print("fill ",hname)

    #Apply cuts, weights
    trees[sample].Draw(f"{graphingVar}>>{hname}",f"({sidebandCut})*eventweight_weight") #Execute all cuts
    hists[(sideband,sample)].Scale(scaling["Beam Data"])

    #Make it look pretty
    hists[(sideband,sample)].SetLineColor(rt.kRed)
    colorIndex += 1
 
    #Draw the data hist to the canvas, on top of the stack
    stack.Draw("HIST")
    stack.GetXaxis().SetTitle(str("Leading Photon Energy (MeV)"))
    stack.GetYaxis().SetTitle("Events per 4.4e+19 POT")
    hists[(sideband,sample)].Draw("E1 SAME")

    #Add data to the legend
    bins = hists[(sideband,sample)].GetNbinsX()
    histInt = hists[(sideband,sample)].Integral(1, int(bins))
    legend.AddEntry(hists[(sideband,sample)], str(hname)+": "+str(round(histInt, 1)), "l")

    #Now we draw the legend and save the whole canvas
    legend.Draw()

    canvs[sideband].Update()
    canvs[sideband].Write()