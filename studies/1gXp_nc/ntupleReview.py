import os,sys
import ROOT as rt

#What files are we drawing on?
samples = ['Montecarlo']

files = {
    "Montecarlo": "/cluster/tufts/wongjiradlabnu/ndahle01/lantern_ana/output/bnbnumu_20250703_131407.root",
    #"LucasMontecarlo": "/cluster/tufts/wongjiradlabnu/lforbe02/tutorial/lantern_ana/ntuple_mcc9_v28_wctagger_bnboverlay_v3dev_reco_retune.root"
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

#with open("1g0X_event_numbers.txt", "w") as f:
#    f.write("")


for i in range(eventTree.GetEntries()):
    eventTree.GetEntry(i)
    for x in range(eventTree.nTracks):
        #infoString = f"{eventTree.event},{eventTree.run},{eventTree.subrun}\n"
        #print(infoString)


        #with open("1g0X_event_numbers.txt", "a") as f:
        #    f.write(infoString)

        