import os,sys
import ROOT as rt

#What files are we drawing on?
samples = ['Off-Beam']

files = {
    #"Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250805_124820.root",
    "Off-Beam": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/extbnb_20250806_122727.root",
    #"Beam Data": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/beamData_20250702_162930.root"
}

targetpot = 4.4e19
#scaleFactor = targetpot/4.5221966264744385e+20 #For Montecarlo
scaleFactor = 176222.0/368589 #For Cosmics

tfiles = {}
trees = {}

rt.gStyle.SetOptStat(0)

#Iterate over files, get trees and events and whatnot
for sample in samples:
    tfiles[sample] = rt.TFile( files[sample] ) #Assign a file using the dictionary
    trees[sample] = tfiles[sample].Get("analysis_tree") #Extract the ttree from that file
    nentries = trees[sample].GetEntries() #Extract the number of entries from the tree
    print(f"sample={sample} has {nentries} entries")


ntuple_file = tfiles["Off-Beam"]

eventTree = ntuple_file.Get("analysis_tree")

cosmicPhotonsPurityCompletenessReco = rt.TH2D("Reco Purity vs. Completeness (cosmic photons)", "Reco Purity vs. Completeness (cosmic photons)", 60, 0, 1, 60, 0, 1)


#Plot the true vs. visible energy of each photon we were able to measure both for
for i in range(eventTree.GetEntries()):
    eventTree.GetEntry(i)

    for x in range(len(eventTree.matchedPhotonEnergiesVisible)):
        #Get 'photon' completeness
        if eventTree.recoComp[x] > -1:

            #Store the 'photon' if we have data for it
            cosmicPhotonsPurityCompletenessReco.Fill(eventTree.recoPur[x], eventTree.recoComp[x], eventTree.eventweight_weight)

writeList = []

def prepHist(histogram, scale, xLabel, yLabel, writelist = writeList):
    #Set up the canvas
    histCanvas = rt.TCanvas(f"{histogram}_Canvas",f"{histogram}_Canvas",1000,800)
    #Scale histogram
    histogram.Scale(scale)
    #Set up to the axes
    xAxis = histogram.GetXaxis()
    yAxis = histogram.GetYaxis()
    xAxis.SetTitle(str(xLabel))
    yAxis.SetTitle(str(yLabel))

    #Draw everything
    histogram.Draw()

    writelist.append(histCanvas)

    #Return it all, so the variables get saved
    return histCanvas

cosmicCanvas = prepHist(cosmicPhotonsPurityCompletenessReco, scaleFactor, "Reconstructed Purity", "Reconstructed Completeness")


outFile = rt.TFile("CosmicPurityOutput.root", "RECREATE")
for canvas in writeList:
    canvas.Write()