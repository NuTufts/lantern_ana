import os,sys
import ROOT as rt

#What files are we drawing on?
samples = ['Montecarlo']

files = {
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250806_121812.root",
    #"Off-Beam": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/extbnb_20250702_162623.root",
    #"Beam Data": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/beamData_20250702_162930.root"
}

#targetpot = 4.4e19
targetpot = 6.6e20
#samplePOT = 8.037960000001028e23 
samplePOT = 4.5221966264744385e+20
scaleFactor = targetpot/samplePOT #For Montecarlo

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

#print(eventTree.pot)


minOnePhotonHist = rt.TH1D("Vertex X Position of Events With at Least One Photon", "Vertex X Position of Events With at Least One Photon", 60, -200, 500)
onlyOnePhotonHist = rt.TH1D("Vertex X Position of Events With Exactly One Photon", "Vertex X Position of Events With Exactly One Photon", 60, -200, 500)
onlyOnePhotonInFiducialHist = rt.TH1D("Vertex X Position of Events With Exactly One Photon in Fiducial", "Vertex X Position of Events With Exactly One Photon in Fiducial", 60, -200, 500)
nothingButOnePhotonInFiducialHist = rt.TH1D("Vertex X Position of Events where the Only Photon is in Fiducal", "Vertex X Position of Events where the Only Photon is in Fiducal", 60, -200, 500)
#onePhotonInCryostat = rt.TH1D("Vertex X Position of Events With at Least One Photon in Cryostat", "Vertex X Position of Events With at Least One Photon", 60, -200, 500)


photonEvents = 0
singlePhotonEvents = 0
inFiducialPhotonEvents = 0

#Plot the true vs. visible energy of each photon we were able to measure both for
for i in range(eventTree.GetEntries()):
    #print("Running event", i)
    eventTree.GetEntry(i)

    if eventTree.nTruePhotons > 0:
        #Grab vertex position
        vertexXPos = eventTree.true_vertex_properties_x
        #Graph!
        minOnePhotonHist.Fill(vertexXPos, eventTree.eventweight_weight)

        #Now see if it satisfies any of our additional checks
        if eventTree.nTruePhotons == 1:
            onlyOnePhotonHist.Fill(vertexXPos, eventTree.eventweight_weight)

            if eventTree.nTrueFiducialPhotons == 1:
                nothingButOnePhotonInFiducialHist.Fill(vertexXPos, eventTree.eventweight_weight)

        if eventTree.nTrueFiducialPhotons == 1:
            onlyOnePhotonInFiducialHist.Fill(vertexXPos, eventTree.eventweight_weight)



def prepHist(histogram, scale, targetPOT, upperValue = 2600):
    #Set up the canvas
    histCanvas = rt.TCanvas(f"{histogram}_Canvas",f"{histogram}_Canvas",1000,800)
    #Scale histogram
    histogram.Scale(scale)
    #Get the information for a legend
    bins = histogram.GetNbinsX()
    histInt = histogram.Integral(1, int(bins))
    legend = rt.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(histogram, "Events: "+str(round(histInt, 1)), "l")

    #Set up to the axes
    xAxis = histogram.GetXaxis()
    yAxis = histogram.GetYaxis()
    xAxis.SetTitle("Vertex X Position")
    yAxis.SetTitle(f"Predicted Events for {targetpot} POT")

    #Draw everything
    histogram.Draw()
    legend.Draw()

    lowerBound = rt.TLine(0, 0, 0, upperValue)
    upperBound = rt.TLine(256, 0, 256, upperValue)
    lowerBound.Draw()
    upperBound.Draw()


    #Return it all, so the variables get saved
    return histCanvas, legend, histInt


minOnePhotonCanvas, minOnePhotonLegend, minOnePhotonInt = prepHist(minOnePhotonHist, scaleFactor, targetpot)
onlyOnePhotonCanvas, onlyOnePhotonLegend, onlyOnePhotonInt = prepHist(onlyOnePhotonHist, scaleFactor, targetpot)
onlyOnePhotonInFiducialCanvas, onlyOnePhotonInFiducialLegend, onlyOnePhotonInFiducialInt = prepHist(onlyOnePhotonInFiducialHist, scaleFactor, targetpot)
nothingButOnePhotonInFiducialCanvas, nothingButOnePhotonInFiducialLegend, nothingButOnePhotonInFiducialInt = prepHist(nothingButOnePhotonInFiducialHist, scaleFactor, targetpot)
#onePhotonInCryostatCanvas, onePhotonInCryostatLegend, onePhotonInCryostatInt = prepHist(minOnePhotonHist, scaleFactor, targetpot)

writeList = [minOnePhotonCanvas, onlyOnePhotonCanvas, onlyOnePhotonInFiducialCanvas, nothingButOnePhotonInFiducialCanvas] #, onePhotonInCryostatCanvas]

outFile = rt.TFile("VertexStatsOutput.root", "RECREATE")

for canvas in writeList:
    canvas.Write()