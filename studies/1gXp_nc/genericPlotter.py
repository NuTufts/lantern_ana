import os,sys
import ROOT as rt


targetpot = 4.4e19
samples = ['Montecarlo']
scaling = {
    "Montecarlo":targetpot/4.5221966264744385e+20,
    }

#What files are we drawing on?
files = {
    "Montecarlo": "[YOUR FILEPATH HERE]",
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

graphingVar = "[GRAPHING VARIABLE HERE]" #You'll want to put in your invariant mass variable

#Graph size - tweak as needed
nBins = 60
xMin = 0
xMax = 700

histogramSpecsList = [ #Format: ("[SAMPLE VARIABLE]",nBins, xMin, xMax,'[TITLE]')
    ("oneGnoX",nBins, xMin, xMax,'1g0X Sample')
] #Add more entries in the same format as needed

canvs = {}

#CUT LIST
#Generic cut to build on
cut = "1==1"

#Cuts are added to the string with the format "&& ([CONDITION HERE])"
#For example:
#cut += "&& (nphotons > 0)"
#Would add a cut removing any events with 0 photons


#Now we actually go through and store the data
for sampleVar, nbins, xmin, xmax, htitle in histogramSpecsList:
    #Define our canvas (what we draw everything on) and our legend
    cname = f"c{sampleVar}"
    canvs[sampleVar] = rt.TCanvas(cname,f"v3dev: {cname}",1000,800)
    canvs[sampleVar].Draw()
    legend = rt.TLegend(0.5, 0.5, 0.9, 0.9)

    #We use these to color our histograms
    colors = [rt.kGreen, rt. kBlue,  rt. kOrange+1, rt.kViolet+3, rt.kRed, rt.kCyan, rt.kMagenta, rt.kYellow+1, rt.kBlack, rt.kViolet]
    colorIndex = 0 

    stack = rt.THStack(f"hs_{sampleVar}", f"{htitle}")

    #BEGIN WITH THE MONTECARLO DATA
    sample = "Montecarlo"

    #Apply cuts, fill histogram
    sampleCut = cut
    sampleCut += sampleCuts[sampleVar]
        
    legendName = f'{category}'

    hists[graphingVar] = rt.TH1D(hname, "", nbins, xmin, xmax )

    trees[sample].Draw(f"{graphingVar}>>{hname}",f"({categoryCut})*eventweight_weight") #Execute all cuts
    hist[graphingVar].Scale(scaling[sample])
        
        #Make it look pretty
    hist[graphingVar].SetLineColor(rt.kBlack)
    hist[graphingVar].SetFillColor(colors[colorIndex%9])
    colorIndex += 1

    #Add histogram to the legend
    bins = hist[graphingVar].GetNbinsX()
    histInt = hist[graphingVar].Integral(1, int(bins))
    legend.AddEntry(hist[graphingVar], str(legendName)+": "+str(round(histInt, 1)), "f")

    stack.Add(hist[graphingVar])

    #Draw the data hist to the canvas, on top of the stack
    stack.Draw("HIST")
    stack.GetXaxis().SetTitle(str("Leading Photon Energy (MeV)"))
    stack.GetYaxis().SetTitle("Events per 4.4e+19 POT")
    hist[graphingVar].Draw("E1 SAME")

    #Add data to the legend
    bins = hist[graphingVar].GetNbinsX()
    histInt = hist[graphingVar].Integral(1, int(bins))
    legend.AddEntry(hist[graphingVar], str(hname)+": "+str(round(histInt, 1)), "l")

    #Now we draw the legend and save the whole canvas
    legend.Draw()

    canvs[sideband].Update()
    canvs[sideband].Write()