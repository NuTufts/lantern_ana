import os,sys
import ROOT as rt


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

recoBackgroundCuts = {'Vertex Not Reconstructed': "&& (noVertex == 1)",
    'Vertex Reconstructed Out of Fiducial': "&& (outOfFiducial == 1)",
    'Cosmic Fraction Cut': "&& (cosmicFracCut == 1)",
    'Unreconstructed Pixel Cut': "&& (unReconstructedPixelCut == 1)",
    'Charged Score Cut': "&& (photonFromChargedCut == 1)",
    'Significantly Over-Threshold Muon': "&& (overThresholdMuon == 1)",
    '2+ Slightly Over-Threshold Muons': "&& (manyJustOverMuons == 1)",
    'Over-Threshold Electron': "&& (overThresholdElectron == 1)",
    'Over-Threshold Pion': "&& (overThresholdPion == 1)",
    '3+ Protons': "&& (tooManyProtons == 1)",
    'No Photons': "&& (noPhotons == 1)",
    'Excess Photons': "&& (manyPhotons == 1)"
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
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250627_112700.root",
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

graphingVar = "trueLeadingPhotonE"

nBins = 60
xMin = 0
xMax = 700

trueSidebandList = [
    ("oneGinclusiveTrue",nBins, xMin, xMax,'1g + X Inclusive Outcomes',"True", -1), #No signal category
    ("twoGinclusiveTrue",nBins, xMin, xMax,'2g + X Inclusive Sample',"True", -1), #No signal category
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
cut = "1==1"


#Now we actually go through and store the data
for sideband, nbins, xmin, xmax, htitle, dataType, correctSidebandIndex in trueSidebandList:
    #Define our canvas (what we draw everything on) and our legend
    cname = f"c{sideband}"
    canvs[sideband] = rt.TCanvas(cname,f"v3dev: {cname}",1000,800)
    canvs[sideband].Draw()
    legend = rt.TLegend(0.5, 0.5, 0.9, 0.9)
    histIntTotal = 0

    #We use these to color our histograms
    colors = [rt.kBlue, rt.kOrange+1, rt.kViolet+3, rt.kBlue+3, rt.kCyan, rt.kGreen +2, rt.kMagenta, rt.kYellow+1, rt.kViolet]
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
        if sideband == 'oneGinclusiveTrue' and recoSideband == 'reco 1g0X':
            print("filling ",hname)

        recoSidebandCut = trueSidebandCut + recoSidebandCuts[str(recoSideband)]

        trees[sample].Draw(f"{graphingVar}>>{hname}",f"({recoSidebandCut})*eventweight_weight") #Execute all cuts
        if sideband == 'oneGinclusiveTrue' and recoSideband == 'reco 1g0X':
            print("Drawing based on:", recoSidebandCut)
        hists[(sideband,recoSideband)].Scale(scaling[sample])

        bins = hists[(sideband,recoSideband)].GetNbinsX()

        histInt = hists[(sideband,recoSideband)].Integral(1, int(bins))
        if sideband == 'oneGinclusiveTrue' and recoSideband == 'reco 1g0X':
            print("Histint:", histInt)
        
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