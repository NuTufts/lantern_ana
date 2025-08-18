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

minOnePhotonHist = rt.TH1D("Events Containing at Least One Photon", "Events Containing at Least One Photon", 60, 0, 1)
trueVsVisibleEHistLarge = rt.TH2D("1g + X True Vs. EDep Histogram (Large)", "True Vs. Reconstructed Photon Energy (All Photons)", 60, 0, 800, 60, 0, 800)
trueVsVisibleEHistSmall = rt.TH2D("1g + X True Vs. EDep Histogram (Small)", "True Vs. Reconstructed Photon Energy (All Photons)", 60, 0, 100, 60, 0, 100)
trueVsEDepHistLarge = rt.TH2D("1g + X True Vs. Deposited Histogram (Large)", "True Vs. Deposited Photon Energy (All Photons)", 60, 0, 800, 60, 0, 800)
trueVsEDepHistSmall = rt.TH2D("1g + X True Vs. Deposited Histogram (Large)", "True Vs. Deposited Photon Energy (All Photons)", 60, 0, 100, 60, 0, 100)
normalPhotonCompleteness = rt.TH1D("Shower Completeness (correlated photons)", "Shower Completeness (correlated photons)", 60, 0, 1)
weirdShowerCompletenessHist = rt.TH1D("Shower Completeness (non-correlated photons)", "Shower Completeness (non-correlated photons)", 60, 0, 1)

totalPhotons = 0
oneGnoX = 0
oneGoneP = 0
oneGother = 0

twoGnoX = 0
twoGoneP = 0
twoGother = 0

somethingElse = 0

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
        visibleY = eventTree.matchedPhotonEnergiesVisible[x]
        eDepY = eventTree.EDepSumMax[x]
        if currentX > -1 and visibleY > -1:
            trueVsVisibleEHistLarge.Fill(currentX, visibleY, eventTree.eventweight_weight)
            trueVsVisibleEHistSmall.Fill(currentX, visibleY, eventTree.eventweight_weight)
            trueVsEDepHistLarge.Fill(currentX, eDepY, eventTree.eventweight_weight)
            trueVsEDepHistSmall.Fill(currentX, eDepY, eventTree.eventweight_weight)

            totalPhotons += 1

            if currentX > 70 and visibleY < 60:
                weirdShowerCompletenessHist.Fill(eventTree.photonCompleteness[x], eventTree.eventweight_weight)
                if eventTree.oneGnoXtrue == 1:
                    oneGnoX += 1
                elif eventTree.oneGonePtrue == 1:
                    oneGoneP += 1

                elif eventTree.trueOnePhotonInclusive == 1:
                    oneGother += 1

                elif eventTree.twoGnoXtrue == 1:
                    twoGnoX += 1

                elif eventTree.twoGonePtrue == 1:
                    twoGoneP += 1
                
                elif eventTree.trueTwoPhotonInclusive == 1:
                    twoGother += 1

                else: 
                    somethingElse += 1


            else: 
                normalPhotonCompleteness.Fill(eventTree.photonCompleteness[x], eventTree.eventweight_weight)


        #Document photon energy values for review
        #with open("PhotonDataFile.txt", "a") as f:
        #    f.write("Photon " + str(x) + " True energy: " + str(currentX) + " Visible Energy: " + str(currentY) + "\n")



#Handling histograms for TRUE VS VISIBLE
trueVsVisibleECanvasLarge = rt.TCanvas("1g + X Inclusive Large","v3dev: 1g + X Inclusive Large",1000,800)

trueVsVisiblePadLarge = rt.TPad("trueVsVisiblePad", "trueVsVisiblePad", 0.0, 0.0, 1.0, 1.0) #Allows us to change axis labels

xAxis = trueVsVisibleEHistLarge.GetXaxis()
yAxis = trueVsVisibleEHistLarge.GetYaxis()
xAxis.SetTitle("True Energy (MeV)")
yAxis.SetTitle("Reconstructed Energy (MeV)")
trueVsVisibleEHistLarge.Scale(scaleFactor)
trueVsVisiblePadLarge.Draw()
trueVsVisibleEHistLarge.Draw()

trueVsVisibleECanvasSmall = rt.TCanvas("1g + X Inclusive Small","v3dev: 1g + X Inclusive Small",1000,800)
trueVsVisiblePadSmall = rt.TPad("trueVsVisiblePad", "trueVsVisiblePad", 0.0, 0.0, 1.0, 1.0) #Allows us to change axis labels

xAxis = trueVsVisibleEHistSmall.GetXaxis()
yAxis = trueVsVisibleEHistSmall.GetYaxis()
xAxis.SetTitle("True Energy (MeV)")
yAxis.SetTitle("Reconstucted Energy (MeV)")
trueVsVisibleEHistSmall.Scale(scaleFactor)

trueVsVisiblePadSmall.Draw()
trueVsVisibleEHistSmall.Draw()


outFile = rt.TFile("PhotonEnergyOutput.root", "RECREATE")

trueVsVisibleEHistLarge.Write()
trueVsVisibleECanvasSmall.Write()


#Handling Histograms for TRUE VS EDEP
trueVsEDepCanvasLarge = rt.TCanvas("1g + X Inclusive Large","v3dev: 1g + X Inclusive Large",1000,800)

trueVsEDepPadLarge = rt.TPad("trueVsEDepPad", "trueVsEDepPad", 0.0, 0.0, 1.0, 1.0) #Allows us to change axis labels

xAxis = trueVsEDepHistLarge.GetXaxis()
yAxis = trueVsEDepHistLarge.GetYaxis()
xAxis.SetTitle("True Energy (MeV)")
yAxis.SetTitle("EDep Energy (MeV)")
trueVsEDepHistLarge.Scale(scaleFactor)
trueVsEDepPadLarge.Draw()
trueVsEDepHistLarge.Draw()

trueVsEDepCanvasSmall = rt.TCanvas("1g + X Inclusive Small","v3dev: 1g + X Inclusive Small",1000,800)
trueVsEDepPadSmall = rt.TPad("trueVsEDepPad", "trueVsEDepPad", 0.0, 0.0, 1.0, 1.0) #Allows us to change axis labels

xAxis = trueVsEDepHistSmall.GetXaxis()
yAxis = trueVsEDepHistSmall.GetYaxis()
xAxis.SetTitle("True Energy (MeV)")
yAxis.SetTitle("EDep Energy (MeV)")
trueVsEDepHistSmall.Scale(scaleFactor)

trueVsEDepPadSmall.Draw()
trueVsEDepHistSmall.Draw()

trueVsEDepHistLarge.Write()
trueVsEDepCanvasSmall.Write()

#HANDLING HISTOGRAMS FOR COMPLETENESS
completenessCanvasAll = rt.TCanvas("1g + X Inclusive Small","v3dev: 1g + X Inclusive Small",1000,800)

xAxis = normalPhotonCompleteness.GetXaxis()
yAxis = normalPhotonCompleteness.GetYaxis()
xAxis.SetTitle("Shower Completeness")
yAxis.SetTitle(f"Photons per {targetpot} POT")
normalPhotonCompleteness.Scale(scaleFactor)

normalPhotonCompleteness.Draw()

completenessCanvasAll.Write()


completenessCanvasWeird = rt.TCanvas("1g + X Inclusive Small","v3dev: 1g + X Inclusive Small",1000,800)

xAxis = weirdShowerCompletenessHist.GetXaxis()
yAxis = weirdShowerCompletenessHist.GetYaxis()
xAxis.SetTitle("Shower Completeness")
yAxis.SetTitle(f"Photons per {targetpot} POT")
weirdShowerCompletenessHist.Scale(scaleFactor)

weirdShowerCompletenessHist.Draw()

completenessCanvasWeird.Write()



print("totalPhotons:", totalPhotons)
print("oneGnoX:", oneGnoX)
print("oneGoneP:", oneGoneP)
print("oneGother:", oneGother)
print("twoGnoX:", twoGnoX)
print("twoGoneP:", twoGoneP)
print("twoGother:", twoGother)
print("somethingElse:", somethingElse)