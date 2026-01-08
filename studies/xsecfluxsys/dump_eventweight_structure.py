import os,sys
import ROOT as rt

rt.gSystem.Load("./libMapDict.so")

# test_inputpath = sys.argv[1]

## nu (good)
# test_inputpath = "/pnfs/uboone/persistent/users/yatesla/arborist_mcc9/arborist_v55_Jun20_withExtraGENIE_bnb_nu_run1_noNaNs.root"

# nue (issues)
test_inputpath = "/pnfs/uboone/persistent/users/yatesla/arborist_mcc9/arborist_v55_Jun20_withExtraGENIE_intrinsic_nue_run1.root"


inputfile = rt.TFile(test_inputpath,'read')

tree = inputfile.Get("eventweight_tree")
if not tree: 
    tree = inputfile.Get(f"arborist/eventweight_tree")

# tree.ls()

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
