import os,sys
import ROOT as rt


targetpot = 4.4e19
samples = ['Montecarlo',"Off-Beam","Beam Data"]
scaling = {
    "Montecarlo":targetpot/4.5221966264744385e+20,
    "Off-Beam":176222.0/368589,
    "Beam Data":targetpot/4.4e19
    }

trueSidebands = ['true 1g0X', 
                'true 1g1p', 
                'true 1g2p', 
                'true 1g1u', 
                'true 1gXpi', 
                'true 2g0X', 
                'true 2g1p', 
                'true 2g2p', 
                'true 2g1u', 
                'true 2gXpi'
                ]
noTrueSidebands = len(trueSidebands)

trueBackgroundTypes = ['Significantly Over Threshold Muon',
    'Multiple, Slightly Over-Threshold Muons',
    'Over Threshold Electron',
    '> 2 Detectable Protons',
    'Over Threshold Pion',
    'No Photons',
    'Too Many Photons'
    ]
noBackgrounds = len(trueBackgroundTypes)

trueBackgroundCuts = {
    'Significantly Over Threshold Muon': "&& (nTrueMuons > nTrueMuonsBarelyOver)",
    'Multiple, Slightly Over-Threshold Muons': "&& (nTrueMuonsBarelyOver > 1)",
    'Over Threshold Electron': "&& (nTrueElectrons > 0)",
    '> 2 Detectable Protons': "&& (nTrueProtons > 2)",
    'Over Threshold Pion': "&& (nTruePions > nTruePionsBarelyOver)",
    'No Photons': "&& (nTruePhotons == 0)",
    'Too Many Photons': "&& (nTruePhotons > 2)"
}

trueBackgroundCutsUsed = {
    'Significantly Over Threshold Muon': "&& (nTrueMuons <= nTrueMuonsBarelyOver)",
    'Multiple, Slightly Over-Threshold Muons': "&& (nTrueMuonsBarelyOver <= 1)",
    'Over Threshold Electron': "&& (nTrueElectrons == 0)",
    '> 2 Detectable Protons': "&& (nTrueProtons <= 2)",
    'Over Threshold Pion': "&& (nTruePions <= nTruePionsBarelyOver)",
    'No Photons': "&& (nTruePhotons != 0)",
    'Too Many Photons': "&& (nTruePhotons < 2)"
}


sidebandCuts = {'oneGinclusive': "&& (recoOnePhotonInclusive == 1)",
    'twoGinclusive': "&& (recoTwoPhotonInclusive == 1)",
    'oneGnoX': "&& (oneGnoX == 1)",
    'oneGoneP': "&& (oneGoneP == 1)",
    'oneGtwoP': "&& (oneGtwoP == 1)",
    'oneGoneMu': "&& (oneGoneMu == 1)",
    'oneGxPi': "&& (oneGxPi == 1)",
    'twoGnoX': "&& (twoGnoX == 1)",
    'twoGoneP': "&& (twoGoneP == 1)",
    'twoGtwoP': "&& (twoGtwoP == 1)",
    'twoGoneMu': "&& (twoGoneMu == 1)",
    'twoGxPi': "&& (twoGxPi == 1)",
    }

trueSidebandCuts = {'true 1g0X': "&& (oneGnoXtrue == 1)",
    'true 1g1p': "&& (oneGonePtrue == 1)",
    'true 1g2p': "&& (oneGtwoPtrue == 1)",
    'true 1g1u': "&& (oneGoneMutrue == 1)",
    'true 1gXpi': "&& (oneGxPitrue == 1)",
    'true 2g0X': "&& (twoGnoXtrue == 1)",
    'true 2g1p': "&& (twoGonePtrue == 1)",
    'true 2g2p': "&& (twoGtwoPtrue == 1)",
    'true 2g1u': "&& (twoGoneMutrue == 1)",
    'true 2gXpi': "&& (twoGxPitrue == 1)"
    }


#What files are we drawing on?
files = {
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250630_145735.root",
    "Off-Beam": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/extbnb_20250630_151126.root",
    "Beam Data": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/beamData_20250630_151526.root"
}


tfiles = {}
trees = {}

rt.gStyle.SetOptStat(0)

#Iterate over files, get trees and events and whatnot
for sample in samples:
    tfiles[sample] = rt.TFile( files[sample] ) #Assign a file using the dictionary
    trees[sample] = tfiles[sample].Get("analysis_tree") #Extract the ttree from that file
    nentries = trees[sample].GetEntries() #Extract the number of entries from the tree
    #print(f"sample={sample} has {nentries} entries")

#Assign our output file
out = rt.TFile("PurityOutput.root","recreate")

graphingVar = "leadingPhotonE"
#graphingVar = "flashpred_sinkhorn_div"
#graphingVar = "flashpred_observedpe"

graphingVarName = "Reconstructed Leading Photon Energy"
#graphingVarName = "Sinkhorn Divergence"
#graphingVarName = "Observed PE"

nBins = 100
xMin = 0
xMax = 2500

sidebandList = [
    ("oneGinclusive",nBins, xMin, xMax,'1g + X Inclusive Sample',"Reco", -1), #No signal category
    ("twoGinclusive",nBins, xMin, xMax,'2g + X Inclusive Sample',"Reco", -1), #No signal category
    ("oneGnoX",nBins, xMin, xMax,'1g0X Sample',"Reco", 0),
    ("oneGoneP",nBins, xMin, xMax,'1g1p Sample',"Reco", 1),
    ("oneGtwoP",nBins, xMin, xMax,'1g2p Sample',"Reco", 2),
    ("oneGoneMu",nBins, xMin, xMax,'1g1u Sample',"Reco", 3),
    ("oneGxPi",nBins, xMin, xMax,'1gXpi Sample',"Reco", 4),
    ("twoGnoX",nBins, xMin, xMax,'2g0X Sample',"Reco", 5),
    ("twoGoneP",nBins, xMin, xMax,'2g1p Sample',"Reco", 6),
    ("twoGtwoP",nBins, xMin, xMax,'2g2p Sample',"Reco", 7),
    ("twoGoneMu",nBins, xMin, xMax,'2g1u Sample',"Reco", 8),
    ("twoGxPi",nBins, xMin, xMax,'2gXpi Sample',"Reco", 9)
]

hists = {}
canvs = {}

#CUT LIST
#Cut based on basic vertex properties
cut = "1==1"


#Now we actually go through and store the data
for sideband, nbins, xmin, xmax, htitle, dataType, correctSidebandIndex in sidebandList:
    #Define our canvas (what we draw everything on) and our legend
    cname = f"c{sideband}"
    canvs[sideband] = rt.TCanvas(cname,f"v3dev: {cname}",1000,800)
    canvs[sideband].Draw()
    legend = rt.TLegend(0.5, 0.5, 0.9, 0.9)
    histIntTotal = 0

    #We use these to color our histograms
    #colors = [rt.kOrange+1, rt.kViolet+3, rt.kSpring, rt.kBlue+3, rt.kCyan, rt.kGreen +2, rt.kMagenta, rt.kAzure, rt.kYellow+1, rt.kViolet, rt.kPearl, rt.kPink]
    colors = [rt.kCyan, rt.kGray + 2, rt.kGreen, rt.kOrange, rt.kOrange + 2, rt.kViolet, rt.kGray, rt.kRed, rt.kYellow]
    colorIndex = 0 
    noColors = len(colors)

    stack = rt.THStack(f"hs_{sideband}", f"{htitle}")

    #BEGIN WITH THE MONTECARLO DATA
    sample = "Montecarlo"

    #Apply cuts, fill histogram
    sidebandCut = cut
    sidebandCut += sidebandCuts[sideband]
    #We have to fill in a separate histogram for each true sideband. Did we get it right?
    for x in range(len(trueSidebands)):
        trueSideband = trueSidebands[x]
        hname = f'{sample}_{sideband}_{trueSideband}'
        if correctSidebandIndex == x:
            legendName = f'{trueSideband} (CORRECTLY IDENTIFIED)'
        hists[(sideband,trueSideband)] = rt.TH1D(hname, "", nbins, xmin, xmax )

        #print("fill ",hname)

        trueSidebandCut = sidebandCut + trueSidebandCuts[str(trueSideband)]

        trees[sample].Draw(f"{graphingVar}>>{hname}",f"({trueSidebandCut})*eventweight_weight") #Execute all cuts
        #print("Drawn based on", trueSidebandCut)

        hists[(sideband,trueSideband)].Scale(scaling[sample])
        bins = hists[(sideband,trueSideband)].GetNbinsX()

        histInt = hists[(sideband,trueSideband)].Integral(1, int(bins))
        #print("Histint:", histInt)

        #Make it look pretty
        hists[(sideband,trueSideband)].SetLineColor(rt.kBlack)
        if sideband == 'oneGnoX' and trueSideband == 'true 1g0X':
            bins = hists[(sideband,trueSideband)].GetNbinsX()
            histInt = hists[(sideband,trueSideband)].Integral(1, int(bins))
            print("Filling oneGnoX. Cuts:", trueSidebandCut, "histInt:", histInt)
        #If we got it right, we fill it in with green
        if correctSidebandIndex == x: 
            hists[(sideband,trueSideband)].SetFillColor(rt.kGreen)
            
        if correctSidebandIndex == x: #If it's the signal, graph it immediately. Otherwise do it after
            bins = hists[(sideband,trueSideband)].GetNbinsX()
            histInt = hists[(sideband,trueSideband)].Integral(1, int(bins))
            histIntTotal += histInt
            legend.AddEntry(hists[(sideband,trueSideband)], str(legendName)+": "+str(round(histInt, 1)), "f")
            stack.Add(hists[(sideband,trueSideband)])

    #Add histogram to the stack
    for x in range(len(trueSidebands)):
        if x == correctSidebandIndex:
            continue #Don't graph signal twice
        trueSideband = trueSidebands[x]
        stack.Add(hists[(sideband,trueSideband)])
    
    #Now we do the same for true background:
    for background in trueBackgroundTypes:
        hname = f'{sample}_{sideband}_{background}'
        hists[(sideband,background)] = rt.TH1D(hname, "", nbins, xmin, xmax )
        #print("fill ",hname)

        baseBackgroundCut = sidebandCut
        backgroundCut = baseBackgroundCut + trueBackgroundCuts[str(background)]

        trees[sample].Draw(f"{graphingVar}>>{hname}",f"({backgroundCut})*eventweight_weight") #Execute all cuts
        hists[(sideband,background)].Scale(scaling[sample])
        
        baseBackgroundCut += trueBackgroundCutsUsed[str(background)] #This allows us to avoid double-counting events

        #Make it look pretty
        hists[(sideband,background)].SetLineColor(rt.kBlack)
        hists[(sideband,background)].SetFillColor(colors[colorIndex%noColors])
        colorIndex += 1

        stack.Add(hists[(sideband,background)])

    #HANDLE THE OFF-BEAM DATA
    sample = "Off-Beam"
    #Define our histogram
    hname = f'{sample}_{sideband}'
    hists[(sideband,sample)] = rt.TH1D(hname, "", nbins, xmin, xmax )
    #print("fill ",hname)

    #Apply cuts, fill histogram
    trees[sample].Draw(f"{graphingVar}>>{hname}",f"({sidebandCut})*eventweight_weight") #Execute all cuts
    hists[(sideband,sample)].Scale(scaling[sample])
        
    #Make it look pretty
    hists[(sideband,sample)].SetLineColor(rt.kBlack)
    hists[(sideband,sample)].SetFillColor(rt.kBlue)
    colorIndex += 1


    stack.Add(hists[(sideband,sample)])

    #Now we overlay the data
    #Set up the histogram
    sample = "Beam Data"
    hname = f"Beam_Data_{sideband}"
    hists[(sideband,sample)] = rt.TH1D(hname, "", 60,0, 700 )
    #print("fill ",hname)

    #Apply cuts, weights
    trees[sample].Draw(f"{graphingVar}>>{hname}",f"({sidebandCut})*eventweight_weight") #Execute all cuts
    hists[(sideband,sample)].Scale(scaling["Beam Data"])

    #Make it look pretty
    hists[(sideband,sample)].SetLineColor(rt.kBlack)
    colorIndex += 1
 
    #Draw the data hist to the canvas, on top of the stack
    stack.Draw("HIST")
    stack.GetXaxis().SetTitle(str(graphingVarName))
    stack.GetYaxis().SetTitle("Events per 4.4e+19 POT")
    hists[(sideband,sample)].Draw("E1 SAME")

    #Add data to the legend
    bins = hists[(sideband,sample)].GetNbinsX()
    histInt = hists[(sideband,sample)].Integral(1, int(bins))
    legend.AddEntry(hists[(sideband,sample)], "Beam Data"+": "+str(round(histInt, 1)), "l")

    #Add off-beam to the legend
    sample = "Off-Beam"
    bins = hists[(sideband,sample)].GetNbinsX()
    histInt = hists[(sideband,sample)].Integral(1, int(bins))
    histIntTotal += histInt
    legendName = "Off-Beam (Cosmic)"
    legend.AddEntry(hists[(sideband,sample)], str(legendName)+": "+str(round(histInt, 1)), "f")

    #Add background categories to the legend
    for x in range(len(trueBackgroundTypes)):
        background = trueBackgroundTypes[noBackgrounds - 1 - x]
        legendName = f'{background}'
        bins = hists[(sideband,background)].GetNbinsX()
        histInt = hists[(sideband,background)].Integral(1, int(bins))
        histIntTotal += histInt
        if histInt != 0: #Don't add entries that aren't actually on the graph
            hists[(sideband,background)].SetFillColor(colors[colorIndex%noColors])
            colorIndex += 1
            legend.AddEntry(hists[(sideband,background)], str(legendName)+": "+str(round(histInt, 1)), "f")


    #Add sidebands to the legend
    for x in range(len(trueSidebands)):
        if noTrueSidebands - 1 - x == correctSidebandIndex:
            continue #Don't double-count signal
        trueSideband = trueSidebands[noTrueSidebands - 1 - x]
        legendName = f'{trueSideband}'
        bins = hists[(sideband,trueSideband)].GetNbinsX()
        histInt = hists[(sideband,trueSideband)].Integral(1, int(bins))
        histIntTotal += histInt
        if histInt != 0: #Don't add entries that aren't actually on the graph
            hists[(sideband,trueSideband)].SetFillColor(colors[colorIndex%noColors])
            colorIndex += 1
            legend.AddEntry(hists[(sideband,trueSideband)], str(legendName)+": "+str(round(histInt, 1)), "f")


    #Now we draw the legend and save the whole canvas
    legendHeaderString = "Total (Not Including Beam Data): " + str(round((histIntTotal),1)) 
    legend.SetHeader(str(legendHeaderString), "C")
    legend.Draw()

    canvs[sideband].Update()
    canvs[sideband].Write()