import os,sys
import ROOT as rt

#What files are we drawing on?
samples = ['Montecarlo']

files = {
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250806_121812.root",
    #"Off-Beam": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/extbnb_20250702_162623.root",
    #"Beam Data": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/beamData_20250702_162930.root"
}

targetpot = 4.4e+19
#targetpot = 6.6e20
#samplePOT = 8.037960000001028e23 
samplePOT = 4.5221966264744385e+20
scaleFactor = targetpot/samplePOT #For Montecarlo

print(scaleFactor)

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


vertexXHist = rt.TH1D("Vertex X Position of Events With at Least One Photon", "Vertex X Position of Events With at Least One Photon", 60, -200, 500)
vertexYHist = rt.TH1D("Vertex Y Position of Events With at Least One Photon", "Vertex Y Position of Events With at Least One Photon", 60, -250, 250)
vertexZHist = rt.TH1D("Vertex Z Position of Events With at Least One Photon", "Vertex Z Position of Events With at Least One Photon", 60, -200, 1200)



photonEvents = 0
singlePhotonEvents = 0
inFiducialPhotonEvents = 0

#Plot the true vs. visible energy of each photon we were able to measure both for
for i in range(eventTree.GetEntries()):
    #print("Running event", i)
    eventTree.GetEntry(i)

    if eventTree.nTruePhotons > 0:
        #Grab variables
        vertexXPos = eventTree.true_vertex_properties_x
        vertexYPos = eventTree.true_vertex_properties_y
        vertexZPos = eventTree.true_vertex_properties_z
        
        #Fill histograms
        vertexXHist.Fill(vertexXPos, eventTree.eventweight_weight)
        vertexYHist.Fill(vertexYPos, eventTree.eventweight_weight)
        vertexZHist.Fill(vertexZPos, eventTree.eventweight_weight)

        #Add up our event tallies
        photonEvents += 1
        if eventTree.nTruePhotons == 1:
            singlePhotonEvents += 1


#Handling histograms for X AXIS
vertexXPosCanvas = rt.TCanvas("vertexXPosCanvas","vertexXPosCanvas",1000,800)
vertexXHist.Scale(scaleFactor)

bins = vertexXHist.GetNbinsX()
histInt = vertexXHist.Integral(1, int(bins))

legendX = rt.TLegend(0.7, 0.7, 0.9, 0.9)
legendX.AddEntry(vertexXHist, "Events: "+str(round(histInt, 1)), "l")


xAxisX = vertexXHist.GetXaxis()
yAxisX = vertexXHist.GetYaxis()
xAxisX.SetTitle("Vertex X Position")
yAxisX.SetTitle(f"Predicted Events for {targetpot} POT")
vertexXHist.Draw()
legendX.Draw()

#Add lines to the graph to denote detector boundaries
lowerBoundX = rt.TLine(0, 0, 0, 2600)
upperBoundX = rt.TLine(256, 0, 256, 2600)

lowerBoundX.Draw()
upperBoundX.Draw()


#Handling histograms for Y AXIS
vertexYPosCanvas = rt.TCanvas("vertexYPosCanvas","vertexYPosCanvas",1000,800)

bins = vertexYHist.GetNbinsX()
histInt = vertexYHist.Integral(1, int(bins))

legendY = rt.TLegend(0.7, 0.7, 0.9, 0.9)
legendY.AddEntry(vertexYHist, "Events: "+str(round(histInt, 1)), "l")

xAxisY = vertexYHist.GetXaxis()
yAxisY = vertexYHist.GetYaxis()
xAxisY .SetTitle("Vertex Y Position")
yAxisY.SetTitle(f"Predicted Events for {targetpot} POT")
vertexYHist.Scale(scaleFactor)
vertexYHist.Draw()
legendY.Draw()

#Add lines to the graph to denote detector boundaries
lowerBoundY = rt.TLine(-116.5, 0, -116.5, 2100)
upperBoundY = rt.TLine(116.5, 0, 116.5, 2100)

lowerBoundY.Draw()
upperBoundY.Draw()

#Handling histograms for Z AXIS
vertexZPosCanvas = rt.TCanvas("vertexZPosCanvas","vertexZPosCanvas",1000,800)

bins = vertexZHist.GetNbinsX()
histInt = vertexZHist.Integral(1, int(bins))

legendZ = rt.TLegend(0.7, 0.7, 0.9, 0.9)
legendZ.AddEntry(vertexZHist, "Events: "+str(round(histInt, 1)), "l")


xAxisZ = vertexZHist.GetXaxis()
yAxisZ = vertexZHist.GetYaxis()
xAxisZ.SetTitle("Vertex Z Position")
yAxisZ.SetTitle(f"Predicted Events for {targetpot} POT")
vertexZHist.Scale(scaleFactor)
vertexZHist.Draw()
legendZ.Draw()

#Add lines to the graph to denote detector boundaries
lowerBoundZ = rt.TLine(0, 0, 0, 1450)
upperBoundZ = rt.TLine(1036, 0, 1036, 1450)

lowerBoundZ.Draw()
upperBoundZ.Draw()


outFile = rt.TFile("VertexPhotonStatsOutput.root", "RECREATE")

vertexXPosCanvas.Write()
vertexYPosCanvas.Write()
vertexZPosCanvas.Write()