import os,sys
import ROOT as rt
import math



targetpot = 4.4e19
samples = ['Montecarlo']
scaling = {
    "Montecarlo":targetpot/4.5221966264744385e+20,
    }

recoSidebands = ['reco 1g0X', 
                'reco 1g1p', 
                'reco 1g2p', 
                'reco 1g1u', 
                'reco 1gXpi', 
                'reco 2g0X', 
                'reco 2g1p', 
                'reco 2g2p', 
                'reco 2g1u', 
                'reco 2gXpi'
                ]

noRecoSidebands = len(recoSidebands)

recoBackgroundTypes = ['Vertex Not Reconstructed',
    'Vertex Reconstructed Out of Fiducial',
    'Cosmic Fraction Cut',
    'Unreconstructed Pixel Cut',
    'Charged Score Cut',
    'Significantly Over-Threshold Muon',
    '2+ Slightly Over-Threshold Muons',
    'Over-Threshold Electron',
    'Over-Threshold Pion',
    '3+ Protons',
    'No Photons',
    'Excess Photons'
    ]

noBackgrounds = len(recoBackgroundTypes)

recoBackgroundCuts = {'Vertex Not Reconstructed': "&& (vertex_properties_found != 1)",
    'Vertex Reconstructed Out of Fiducial': "&& (inFiducial != 1)",
    'Cosmic Fraction Cut': "&& (vertex_properties_cosmicfrac > 0.15)",
    'Unreconstructed Pixel Cut': "&& (vertex_properties_frac_intime_unreco_pixels > 0.9)",
    'Charged Score Cut': "&& (photonFromCharged < 5)",
    'Significantly Over-Threshold Muon': "&& (nMuons > nJustOverMuons)",
    '2+ Slightly Over-Threshold Muons': "&& (nMuons > 1)",
    'Over-Threshold Electron': "&& (nElectrons > 0)",
    'Over-Threshold Pion': "&& (nPions > nJustOverPions)",
    '3+ Protons': "&& (nProtons > 2)",
    'No Photons': "&& (nphotons == 0)",
    'Excess Photons': "&& (nphotons > 2)",
    'Sinkhorn Div': "&& (sinkhornDiv > 40)",
    'observedPE': "&& (observedPE < 250)"
    }

recoBackgroundCutsUsed = {'Vertex Not Reconstructed': "&& (vertex_properties_found == 1)",
    'Vertex Reconstructed Out of Fiducial': "&& (inFiducial == 1)",
    'Cosmic Fraction Cut': "&& (vertex_properties_cosmicfrac <= 0.15)",
    'Unreconstructed Pixel Cut': "&& (vertex_properties_frac_intime_unreco_pixels <= 0.9)",
    'Charged Score Cut': "&& (photonFromCharged >= 5)",
    'Significantly Over-Threshold Muon': "&& (nMuons <= nJustOverMuons)",
    '2+ Slightly Over-Threshold Muons': "&& (nJustOverMuons <= 1)",
    'Over-Threshold Electron': "&& (nElectrons == 0)",
    'Over-Threshold Pion': "&& (nPions <= nJustOverPions)",
    '3+ Protons': "&& (nProtons <= 2)",
    'No Photons': "&& (nphotons != 0)",
    'Excess Photons': "&& (nphotons <= 2)",
    'Sinkhorn Div': "&& (sinkhornDiv <= 40)",
    'observedPE': "&& (observedPE >= 250)"
    }


recoSidebandCuts = {'reco 1g0X': "&& (oneGnoX == 1)",
    'reco 1g1p': "&& (oneGoneP == 1)",
    'reco 1g2p': "&& (oneGtwoP == 1)",
    'reco 1g1u': "&& (oneGoneMu == 1)",
    'reco 1gXpi': "&& (oneGxPi == 1)",
    'reco 2g0X': "&& (twoGnoX == 1)",
    'reco 2g1p': "&& (twoGoneP == 1)",
    'reco 2g2p': "&& (twoGtwoP == 1)",
    'reco 2g1u': "&& (twoGoneMu == 1)",
    'reco 2gXpi': "&& (twoGxPi == 1)"
    }

graphingVar = "trueLeadingPhotonE"

trueSidebandCuts = {
    'oneGnoXtrue': "&& (oneGnoXtrue == 1)",
    'oneGonePtrue': "&& (oneGonePtrue == 1)",
    'oneGtwoPtrue': "&& (oneGtwoPtrue == 1)",
    'oneGoneMutrue': "&& (oneGoneMutrue == 1)",
    'oneGxPitrue': "&& (oneGxPitrue == 1)",
    'twoGnoXtrue': "&& (twoGnoXtrue == 1)",
    'twoGonePtrue': "&& (twoGonePtrue == 1)",
    'twoGtwoPtrue': "&& (twoGtwoPtrue == 1)",
    'twoGoneMutrue': "&& (twoGoneMutrue == 1)",
    'twoGxPitrue': "&& (twoGxPitrue == 1)",
    'oneGinclusiveTrue': "&& (trueOnePhotonInclusive == 1)",
    'twoGinclusiveTrue': "&& (trueTwoPhotonInclusive == 1)"
    }


#What files are we drawing on?
files = {
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250730_164857.root",
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
out = rt.TFile("EfficiencyOutput.root","recreate")

#Whip up our histograms
vars = [
    ("leadingPhotonE",60,0, 1000,'2g2p Sample',"Reco", 0)
]

nBins = 60
xMin = 0
xMax = 700

trueSidebandList = [
    ("oneGinclusiveTrue",nBins, xMin, xMax,'1g + X Inclusive Outcomes',"True", -1), #No signal category
    ("twoGinclusiveTrue",nBins, xMin, xMax,'2g + X Inclusive Outcomes',"True", -1), #No signal category
    ("oneGnoXtrue",nBins, xMin, xMax,'True 1g0X Outcomes',"True", 0),
    ("oneGonePtrue",nBins, xMin, xMax,'True 1g1p Outcomes',"True", 1),
    ("oneGtwoPtrue",nBins, xMin, xMax,'True 1g2p Outcomes',"True", 2),
    ("oneGoneMutrue",nBins, xMin, xMax,'True 1g1u Outcomes',"True", 3),
    ("oneGxPitrue",nBins, xMin, xMax,'True 1gXpi Outcomes',"True", 4),
    ("twoGnoXtrue",nBins, xMin, xMax,'True 2g0X Outcomes',"True", 5),
    ("twoGonePtrue",nBins, xMin, xMax,'True 2g1p Outcomes',"True", 6),
    ("twoGtwoPtrue",nBins, xMin, xMax,'True 2g2p Outcomes',"True", 7),
    ("twoGoneMutrue",nBins, xMin, xMax,'True 2g1u Outcomes',"True", 8),
    ("twoGxPitrue",nBins, xMin, xMax,'True 2gXpi Outcomes',"True", 9)
]

hists = {}
canvs = {}

#CUT LIST
#Cut based on basic vertex properties
cut = "(eventweight_weight > -1e9 && eventweight_weight < 1e9)"
#cut = f"(TMath::IsFinite({graphingVar}) && TMath::IsFinite(eventweight_weight))"


#Now we actually go through and store the data
for sideband, nbins, xmin, xmax, htitle, dataType, correctSidebandIndex in trueSidebandList:
    #Define our canvas (what we draw everything on) and our legend
    cname = f"c{sideband}"
    canvs[sideband] = rt.TCanvas(cname,f"v3dev: {cname}",1000,800)
    canvs[sideband].Draw()
    legend = rt.TLegend(0.5, 0.5, 0.9, 0.9)
    histIntTotal = 0

    #We use these to color our histograms
    colors = [rt.kCyan, rt.kGray + 2, rt.kGreen, rt.kOrange, rt.kOrange + 2, rt.kViolet, rt.kGray, rt.kRed, rt.kYellow]
    noColors = len(colors)
    colorIndex = 0

    stack = rt.THStack(f"hs_{sideband}", f"{htitle}")

    #BEGIN WITH THE MONTECARLO DATA
    sample = "Montecarlo"

    #Apply cuts, fill histogram
    trueSidebandCut = cut
    trueSidebandCut += trueSidebandCuts[sideband]
    #We have to fill in a special histogram for each true sideband. Did we get it right?
    for x in range(len(recoSidebands)):
        recoSideband = recoSidebands[x]
        hname = f'{sample}_{sideband}_{recoSideband}'
        if correctSidebandIndex == x:
            legendName = f'{recoSideband} (CORRECTLY IDENTIFIED)'
        hists[(sideband,recoSideband)] = rt.TH1D(hname, "", nbins, xmin, xmax )
        if sideband == 'oneGnoXtrue' and recoSideband == 'reco 1g0X':
            print("filling ",hname)

        recoSidebandCut = trueSidebandCut + recoSidebandCuts[str(recoSideband)]

        trees[sample].Draw(f"{graphingVar}>>{hname}",f"({recoSidebandCut})*eventweight_weight") #Execute all cuts
        #print("Drawing based on:", recoSidebandCut)
        hists[(sideband,recoSideband)].Scale(scaling[sample])

        bins = hists[(sideband,recoSideband)].GetNbinsX()

        histInt = hists[(sideband,recoSideband)].Integral(1, int(bins))
        #print("Histint:", histInt)
        
        hist = hists[(sideband, recoSideband)]
        bins = hist.GetNbinsX()
        #for i in range(1, nbins + 1):  # ROOT bins start at 1
        #    val = hist.GetBinContent(i)
        #    print(val)
            #if math.isnan(val) or math.isinf(val):
            #    print(f"Bad bin content at bin {i}: {val}")



        #Make it look pretty
        hists[(sideband,recoSideband)].SetLineColor(rt.kBlack)
        if correctSidebandIndex == x:
            hists[(sideband,recoSideband)].SetFillColor(rt.kGreen)

        if correctSidebandIndex == x: #If it's the signal, graph it immediately. Otherwise do it after
            bins = hists[(sideband,recoSideband)].GetNbinsX()
            histInt = hists[(sideband,recoSideband)].Integral(1, int(bins))
            histIntTotal += histInt
            legend.AddEntry(hists[(sideband,recoSideband)], str(legendName)+": "+str(round(histInt, 1)), "f")
        
        
        stack.Add(hists[(sideband,recoSideband)])
        
    #Now we do the same for true background:
    for background in recoBackgroundTypes:
        hname = f'{sample}_{sideband}_{background}'
        legendName = f'{background}'
        hists[(sideband,background)] = rt.TH1D(hname, "", nbins, xmin, xmax )
        #print("fill ",hname)

        backgroundCut = trueSidebandCut + recoBackgroundCuts[str(background)]

        trees[sample].Draw(f"{graphingVar}>>{hname}",f"({backgroundCut})*eventweight_weight") #Execute all cuts
        #print("Drawing based on:", backgroundCut)
        hists[(sideband,background)].Scale(scaling[sample])
        h = rt.gDirectory.Get(hname)
        #trees[sample].Scan(f"{graphingVar}:eventweight_weight", 
        #           "!(eventweight_weight < 1e9 && eventweight_weight > -1e9)")


        trueSidebandCut += recoBackgroundCutsUsed[str(background)]

        stack.Add(hists[(sideband,background)])

        

    #Add background hists to the legend:
    for x in range(len(recoBackgroundTypes)):
        background = recoBackgroundTypes[noBackgrounds - 1 - x]
        #Add histogram to the legend
        bins = hists[(sideband,background)].GetNbinsX()
        legendName = f'{background}'
        histInt = hists[(sideband,background)].Integral(1, int(bins))
        histIntTotal += histInt
        if histInt != 0:
            #Make it look pretty
            hists[(sideband,background)].SetLineColor(rt.kBlack)
            hists[(sideband,background)].SetFillColor(colors[colorIndex%9])
            colorIndex += 1
            legend.AddEntry(hists[(sideband,background)], str(legendName)+": "+str(round(histInt, 1)), "f")

    

    #Add the non-signal sidebands to the legend
    for x in range(len(recoSidebands)):
        if noRecoSidebands - 1 - x == correctSidebandIndex:
            continue #Don't double-count signal
        recoSideband = recoSidebands[noRecoSidebands - 1 - x]
        legendName = f'{recoSideband}'
        bins = hists[(sideband,recoSideband)].GetNbinsX()
        histInt = hists[(sideband,recoSideband)].Integral(1, int(bins))
        histIntTotal += histInt
        if histInt != 0:
            #Make it look pretty
            hists[(sideband,recoSideband)].SetLineColor(rt.kBlack)
            hists[(sideband,recoSideband)].SetFillColor(colors[colorIndex%9])
            colorIndex += 1
            legend.AddEntry(hists[(sideband,recoSideband)], str(legendName)+": "+str(round(histInt, 1)), "f")

    #Draw the stack
    stack.Draw("HIST")
    stack.GetXaxis().SetTitle("True Leading Photon Energy")
    stack.GetYaxis().SetTitle("Events per 4.4e+19 POT")

    #Now we draw the legend and save the whole canvas
    legendHeaderString = "Total: " + str(round((histIntTotal),1)) 
    legend.SetHeader(str(legendHeaderString), "C")
    legend.Draw()

    


    canvs[sideband].Update()
    canvs[sideband].Write()

#Now we draw a histogram for the visible vs. true photon energy:
energyVisibleCut = "(eventweight_weight > -1e9 && eventweight_weight < 1e9 && visibleEnergy > -1 && trueLeadingPhotonE < 300 && visibleEnergy < 300)"

trueVsVisibleECanvas = rt.TCanvas("1g + X Inclusive","v3dev: 1g + X Inclusive",1000,800)
trueVsVisiblePad = rt.TPad("trueVsVisiblePad", "trueVsVisiblePad", 0.0, 0.0, 1.0, 1.0) #Allows us to change axis labels
trueVsVisibleEHist = rt.TH2D("1g + X True Vs. Visible Histograms", "1g + X Inclusive True Vs. Visible Histograms", 600, 0, 600, 600, 0, 600)
sample = "Montecarlo"

graphingVary = "visibleEnergy"
graphingVarx = "trueLeadingPhotonE"

trueVsVisiblePad.SetTitle("1g + X Inclusive True Vs. Visible Energy")
xAxis = trueVsVisibleEHist.GetXaxis()
yAxis = trueVsVisibleEHist.GetYaxis()
trueVsVisiblePad.Draw()
trueVsVisibleEHist.Draw()

trees[sample].Draw(f"{graphingVary}:{graphingVarx}>>{trueVsVisibleEHist}", f"({energyVisibleCut})*eventweight_weight", "COLZ")

xAxis.SetTitle("Visible Leading Photon Energy (MeV)")
yAxis.SetTitle("True Leading Photon Energy (MeV)")

#GRAPH OF EDEP VS. TRUESIMPARTE, ALL EVENTS
eDepTrueCut = "(eventweight_weight > -1e9 && eventweight_weight < 1e9 && visibleEnergy > -1 && trueLeadingPhotonE < 600 && EDepSumMax < 600)"

trueVsEDepCanvas = rt.TCanvas("1g + X Inclusive EDep","v3dev: 1g + X Inclusive EDep",1000,800)
trueVsEDepPad = rt.TPad("trueVsEDepPad", "trueVsEDepPad", 0.0, 0.0, 1.0, 1.0) #Allows us to change axis labels
trueVsEDepHist = rt.TH2D("1g + X True Vs. EDep Histograms", "1g + X Inclusive True Vs. EDep Histograms", 600, 0, 600, 600, 0, 600)
sample = "Montecarlo"

graphingVary = "EDepSumMax"
graphingVarx = "trueLeadingPhotonE"

trueVsEDepPad.SetTitle("1g + X Inclusive True Vs. Desposited Energy")
trees[sample].Draw(f"{graphingVary}:{graphingVarx}>>{trueVsEDepHist}", f"({eDepTrueCut})*eventweight_weight", "COLZ") #Draw the graph!
xAxis = trueVsEDepHist.GetXaxis()
yAxis = trueVsEDepHist.GetYaxis()
trueVsEDepPad.Draw()
trueVsEDepHist.Draw()

xAxis.SetTitle("Deposited Leading Photon Energy (MeV)")
yAxis.SetTitle("True Leading Photon Energy (MeV)")


trees[sample].Draw(f"{graphingVary}:{graphingVarx}>>{trueVsVisibleEHist}", f"({energyVisibleCut})*eventweight_weight", "COLZ")


trueVsVisibleECanvas.Write()
trueVsEDepCanvas.Write()