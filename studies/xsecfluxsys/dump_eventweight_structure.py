import os,sys
import ROOT as rt

rt.gSystem.Load("./libMapDict.so")

test_inputpath = sys.argv[1]

inputfile = rt.TFile(test_inputpath,'read')

tree = inputfile.Get("eventweight_tree")

nentries = tree.GetEntries()
print(f"Num Entries: {nentries}")

tree.GetEntry(0)

nmap_elems = tree.sys_weights.size()
print("Number of elements in dictionary: ",nmap_elems)

# Iterate over the map elements
for key, values in tree.sys_weights:
    print(f"Key: {key}")
    print(f"  Number of values: {len(values)}")
    #if len(values) > 0:
    #    print(f"  First few values: {list(values[:min(3, len(values))])}")

print("done")
