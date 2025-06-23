import os,sys
import ROOT as rt


targetpot = 4.4e19
samples = ['Montecarlo']
scaling = {
    "Montecarlo":targetpot/4.5221966264744385e+20
    }

sidebands = ['onePhotonInclusive', 
    'twoPhotonInclusive'
    '1g0X', 
    '1g1p', 
    '1g2p', 
    '1g1u', 
    '1gXpi', 
    '2g0X', 
    '2g1p', 
    '2g2p', 
    '2g1u', 
    '2gXpi', 
    ]

sidebandCuts = {"onePhotonInclusive": "&& (onePhotonInclusive == 1)", 
    "twoPhotonInclusive": "&& (twoPhotonInclusive == 1)",
    '1g0X': "&& (trueOneGnoX == 1)",
    'oneGnoX': "&& (trueOneGnoX == 1)",
    'oneGoneP': "&& (trueOneGoneP == 1)",
    'oneGtwoP': "&& (trueOneGtwoP == 1)",
    'oneGoneMu': "&& (trueOneGoneMu == 1)",
    'oneGxPi': "&& (trueOneGxPi == 1)",
    'twoGnoX': "&& (trueTwoGnoX == 1)",
    'twoGoneP': "&& (trueTwoGoneP == 1)",
    'twoGtwoP': "&& (trueTwoGtwoP == 1)",
    'twoGoneMu': "&& (trueTwoGoneMu == 1)",
    'twoGxPi': "&& (trueTwoGxPi == 1)"
    }

categories = ['Found', 'Misclassified', 'Missed Photon', 'Excess Photons', 'Wrongly Identified Muon', 'Wrong Other Particles']

categoryCuts = {'Found': "&& (isFound == 1)",
    'Misclassified': "&& (isMisclassified == 1)",
    'Missed Photon': "&& (isMissed == 1) && (noPhotonsFound == 1)",
    'Excess Photons': "&& (isMissed == 1) && (tooManyPhotonsFound == 1)",
    'Wrongly Identified Muon': "& (isMissed == 1) && (wrongMuon == 1)",
    'Wrong Other Particles': "&& (isMissed == 1) && (wrongOtherParticle == 1)"
    }



#What files are we drawing on?
files = {
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250620_131849.root",
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
out = rt.TFile("SignalOutput.root","recreate")

#Whip up our histograms
vars = [
    ("trueLeadingPhotonE",60,0, 700,'1gX0 Sample',"Reco", 0)
]

graphingVar = "trueLeadingPhotonE"

nBins = 60
xMin = 0
xMax = 400

sidebandList = [
    ("oneGnoX",nBins, xMin, xMax,'1g0X Sample'),
    ("oneGoneP",nBins, xMin, xMax,'1g1p Sample'),
    ("oneGtwoP",nBins, xMin, xMax,'1g2p Sample'),
    ("oneGoneMu",nBins, xMin, xMax,'1g1u Sample'),
    ("oneGxPi",nBins, xMin, xMax,'1gXpi Sample'),
    ("twoGnoX",nBins, xMin, xMax,'2g0X Sample'),
    ("twoGoneP",nBins, xMin, xMax,'2g1p Sample'),
    ("twoGtwoP",nBins, xMin, xMax,'2g2p Sample'),
    ("twoGoneMu",nBins, xMin, xMax,'2g1u Sample'),
    ("twoGxPi",nBins, xMin, xMax,'2gXpi Sample'),
    ("onePhotonInclusive",nBins, xMin, xMax,'Single Photon Inclusive Sample'),
    ("twoPhotonInclusive",nBins, xMin, 900,'Two Photon Inclusive Sample')
]

hists = {}
canvs = {}

#CUT LIST
#Cut based on basic vertex properties
cut = "nTruePhotons > 0"

#Now we actually go through and store the data
for sideband, nbins, xmin, xmax, htitle in sidebandList:
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

    for category in categories:
        hname = f'{sample}_{sideband}_{category}'

        legendName = f'{category}'
        hists[(sideband,category)] = rt.TH1D(hname, "", nbins, xmin, xmax )
        print("NOW FILLING:",hname)

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
        print("Hist integral:", histInt)
        legend.AddEntry(hists[(sideband,category)], str(legendName)+": "+str(round(histInt, 1)), "f")

        stack.Add(hists[(sideband,category)])


    #Now we draw and save the whole canvas
    stack.Draw("HIST")
    stack.GetXaxis().SetTitle(str("Leading Photon Energy (MeV)"))
    stack.GetYaxis().SetTitle("Events per 4.4e+19 POT")

    legend.Draw()


    canvs[sideband].Update()
    canvs[sideband].Write()