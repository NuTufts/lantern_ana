import os,sys
import ROOT as rt

#What files are we drawing on?
samples = ['Montecarlo']

files = {
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250806_121812.root",
    #"Off-Beam": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/extbnb_20250702_162623.root",
    #"Beam Data": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/beamData_20250702_162930.root"
}

targetpot = 4.4e19
scaleFactor = targetpot/4.5221966264744385e+20 #For Montecarlo

tfiles = {}
trees = {}

rt.gStyle.SetOptStat(0)

#Iterate over files, get trees and events and whatnot
for sample in samples:
    tfiles[sample] = rt.TFile( files[sample] ) #Assign a file using the dictionary
    trees[sample] = tfiles[sample].Get("analysis_tree") #Extract the ttree from that file
    nentries = trees[sample].GetEntries() #Extract the number of entries from the tree
    print(f"sample={sample} has {nentries} entries")


ntuple_file = tfiles["Montecarlo"]

eventTree = ntuple_file.Get("analysis_tree")

#Wipe the writefile
#with open("PhotonDataFile.txt", "w") as f:
#    f.write("")

weirdPhotonsPurityCompletenessReco = rt.TH2D("Reco Purity vs. Completeness (weird photons)", "Reco Purity vs. Completeness (weird photons)", 60, 0, 1, 60, 0, 1)
weirdPhotonsPurityCompletenessTrue = rt.TH2D("True Purity vs. Completeness (weird photons)", "True Purity vs. Completeness (weird photons)", 60, 0, 1, 60, 0, 1)
weirdPhotonsPurityRecoPurityTrue = rt.TH2D("Reco Purity vs. True Purity (weird photons)", "Reco Purity vs. True Purity (weird photons)", 60, 0, 1, 60, 0, 1)
weirdPhotonsCompRecoCompTrue = rt.TH2D("Reco Completeness vs. True Completeness (weird photons)", "Reco Completeness vs. True Completeness (weird photons)", 60, 0, 1, 60, 0, 1)

normalPhotonsPurityCompletenessReco = rt.TH2D("Reco Purity vs. Completeness (normal photons)", "Reco Purity vs. Completeness (normal photons)", 60, 0, 1, 60, 0, 1)
normalPhotonsPurityCompletenessTrue = rt.TH2D("True Purity vs. Completeness (normal photons)", "True Purity vs. Completeness (normal photons)", 60, 0, 1, 60, 0, 1)
normalPhotonsPurityRecoPurityTrue = rt.TH2D("Reco Purity vs. True Purity (normal photons)", "Reco Purity vs. True Purity (normal photons)", 60, 0, 1, 60, 0, 1)
normalPhotonsCompRecoCompTrue = rt.TH2D("Reco Completeness vs. True Completeness (normal photons)", "Reco Completeness vs. True Completeness (normal photons)", 60, 0, 1, 60, 0, 1)


writeList = []
#Plot the true vs. visible energy of each photon we were able to measure both for
for i in range(eventTree.GetEntries()):
    #print("Running event", i)
    eventTree.GetEntry(i)

    #if eventTree.trueOnePhotonInclusive != 1:
    #    continue

    #Track the event number
    #with open("PhotonDataFile.txt", "a") as f:
    #    f.write("Event no. " + str(i) + "\n")

    for x in range(len(eventTree.matchedPhotonEnergiesVisible)):
        #Get photon energy
        trueE = eventTree.matchedPhotonEnergiesTrue[x]
        visE = eventTree.matchedPhotonEnergiesVisible[x]

        #Verify that we have a matched photon
        if trueE > -1 and visE > -1:
            
            #See if the photon falls in the uncorrelated sideband
            if trueE > 70 and visE < 60:
                weirdPhotonsPurityCompletenessReco.Fill(eventTree.photonPurity[x], eventTree.photonCompleteness[x], eventTree.eventweight_weight)
                weirdPhotonsPurityCompletenessTrue.Fill(eventTree.truePhotonPurity[x], eventTree.truePhotonCompleteness[x], eventTree.eventweight_weight)
                weirdPhotonsPurityRecoPurityTrue.Fill(eventTree.truePhotonPurity[x], eventTree.photonPurity[x], eventTree.eventweight_weight)
                weirdPhotonsCompRecoCompTrue.Fill(eventTree.truePhotonCompleteness[x], eventTree.photonCompleteness[x], eventTree.eventweight_weight)

        
            else: 
                normalPhotonsPurityCompletenessReco.Fill(eventTree.photonPurity[x], eventTree.photonCompleteness[x], eventTree.eventweight_weight)
                normalPhotonsPurityCompletenessTrue.Fill(eventTree.truePhotonPurity[x], eventTree.truePhotonCompleteness[x], eventTree.eventweight_weight)
                normalPhotonsPurityRecoPurityTrue.Fill(eventTree.truePhotonPurity[x], eventTree.photonPurity[x], eventTree.eventweight_weight)
                normalPhotonsCompRecoCompTrue.Fill(eventTree.truePhotonCompleteness[x], eventTree.photonCompleteness[x], eventTree.eventweight_weight)

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

normalRecoPCCanvas = prepHist(normalPhotonsPurityCompletenessReco, scaleFactor, "Reconstructed Purity", "Reconstructed Completeness")
normalTruePCCanvas = prepHist(normalPhotonsPurityCompletenessTrue, scaleFactor, "True Purity", "True Completeness")
normalPPCanvas = prepHist(normalPhotonsPurityRecoPurityTrue, scaleFactor, "True Purity", "Reconstructed Purity")
normalCCCanvas = prepHist(normalPhotonsCompRecoCompTrue, scaleFactor, "True Completeness", "Reconstructed Completeness")

weirdRecoPCCanvas = prepHist(weirdPhotonsPurityCompletenessReco, scaleFactor, "Reconstructed Purity", "Reconstructed Completeness")
weirdTruePCCanvas = prepHist(weirdPhotonsPurityCompletenessTrue, scaleFactor, "True Purity", "True Completeness")
weirdPPCanvas = prepHist(weirdPhotonsPurityRecoPurityTrue, scaleFactor, "True Purity", "Reconstructed Purity")
weirdCCCanvas = prepHist(weirdPhotonsCompRecoCompTrue, scaleFactor, "True Completeness", "Reconstructed Completeness")

outFile = rt.TFile("compPurityOutput.root", "RECREATE")
for canvas in writeList:
    canvas.Write()