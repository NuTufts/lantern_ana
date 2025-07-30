import os,sys
import ROOT as rt

#What files are we drawing on?
samples = ['Montecarlo']

files = {
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250730_122502.root",
    #"Off-Beam": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/extbnb_20250702_162623.root",
    #"Beam Data": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/beamData_20250702_162930.root"
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


ntuple_file = tfiles["Montecarlo"]

eventTree = ntuple_file.Get("analysis_tree")

#Wipe the writefile
#with open("PhotonDataFile.txt", "w") as f:
#    f.write("")

trueVsVisibleEHistLarge = rt.TH2D("1g + X True Vs. Visible Histograms (Large)", "True Vs. Visible Photon Energy (All Photons)", 60, 0, 800, 60, 0, 800)
trueVsVisibleEHistSmall = rt.TH2D("1g + X True Vs. Visible Histograms (Small)", "True Vs. Visible Photon Energy (All Photons)", 60, 0, 40, 60, 0, 40)

totalPhotons = 0

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
        currentX = eventTree.matchedPhotonEnergiesTrue[x]
        currentY = eventTree.matchedPhotonEnergiesVisible[x]
        if currentX > -1 and currentY > -1:
            trueVsVisibleEHistLarge.Fill(currentX, currentY, eventTree.eventweight_weight)
            trueVsVisibleEHistSmall.Fill(currentX, currentY, eventTree.eventweight_weight)
            totalPhotons += 1

        #Document photon energy values for review
        #with open("PhotonDataFile.txt", "a") as f:
        #    f.write("Photon " + str(x) + " True energy: " + str(currentX) + " Visible Energy: " + str(currentY) + "\n")


trueVsVisibleECanvasLarge = rt.TCanvas("1g + X Inclusive Large","v3dev: 1g + X Inclusive Large",1000,800)

trueVsVisiblePadLarge = rt.TPad("trueVsVisiblePad", "trueVsVisiblePad", 0.0, 0.0, 1.0, 1.0) #Allows us to change axis labels

xAxis = trueVsVisibleEHistLarge.GetXaxis()
yAxis = trueVsVisibleEHistLarge.GetYaxis()
xAxis.SetTitle("True Energy (MeV)")
yAxis.SetTitle("Visible Energy (MeV)")
trueVsVisiblePadLarge.Draw()
trueVsVisibleEHistLarge.Draw()

trueVsVisibleECanvasSmall = rt.TCanvas("1g + X Inclusive Small","v3dev: 1g + X Inclusive Small",1000,800)
trueVsVisiblePadSmall = rt.TPad("trueVsVisiblePad", "trueVsVisiblePad", 0.0, 0.0, 1.0, 1.0) #Allows us to change axis labels


xAxis = trueVsVisibleEHistSmall.GetXaxis()
yAxis = trueVsVisibleEHistSmall.GetYaxis()
xAxis.SetTitle("True Energy (MeV)")
yAxis.SetTitle("Visible Energy (MeV)")
trueVsVisiblePadSmall.Draw()
trueVsVisibleEHistSmall.Draw()

outFile = rt.TFile("PhotonEnergyOutput.root", "RECREATE")

trueVsVisibleEHistLarge.Write()
trueVsVisibleECanvasSmall.Write()

print(totalPhotons)