import os,sys
import ROOT as rt

#What files are we drawing on?
samples = ['Montecarlo',"Off-Beam","Beam Data"]

files = {
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250620_131849.root",
    "Off-Beam": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/extbnb_20250620_132727.root",
    "Beam Data": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/beamData_20250620_132928.root"
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


ntuple_file = files["Montecarlo"]

eventTree = ntuple_file.Get("EventTree")

for i in range(eventTree.GetEntries()):
    eventTree.GetEntry(i)