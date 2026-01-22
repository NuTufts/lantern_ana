import os,sys
import ROOT as rt

rt.gSystem.Load("./libMapDict.so")

test_inputpath = sys.argv[1]

inputfile = rt.TFile(test_inputpath,'read')

tree = inputfile.Get("nuselection/NeutrinoSelectionFilter")

"""
*............................................................................*
*Br  402 :weights   : Int_t weights_                                         *
*Entries :   170233 : Total  Size=    4943992 bytes  File Size  =     380401 *
*Baskets :      922 : Basket Size=      32000 bytes  Compression=   3.82     *
*............................................................................*
*Br  403 :weights.first : string first[weights_]                             *
*Entries :   170233 : Total  Size=   58171233 bytes  File Size  =    1859874 *
*Baskets :     2296 : Basket Size=      32000 bytes  Compression=  31.25     *
*............................................................................*
*Br  404 :weights.second : vector<double> second[weights_]                   *
*Entries :170233 : Total  Size= 3496245779 bytes  File Size  = 3100741652 *
*Baskets :   170233 : Basket Size=      32000 bytes  Compression=   1.13     *
*............................................................................*
*Br  405 :weightsFlux : vector<unsigned short>                               *
*Entries :   170233 : Total  Size=  344320345 bytes  File Size  =  256444427 *
*Baskets :    11766 : Basket Size=      32000 bytes  Compression=   1.34     *
*............................................................................*
*Br  406 :weightsGenie : vector<unsigned short>                              *
*Entries :   170233 : Total  Size=  173356849 bytes  File Size  =  137196373 *
*Baskets :     5875 : Basket Size=      32000 bytes  Compression=   1.26     *
*............................................................................*
*Br  407 :weightsReint : vector<unsigned short>                              *
*Entries :   170233 : Total  Size=  344332115 bytes  File Size  =  211005685 *
*Baskets :    11766 : Basket Size=      32000 bytes  Compression=   1.63     *
*............................................................................*
"""

nentries = tree.GetEntries()
print(f"Num Entries: {nentries}")

tree.GetEntry(824)

nmap_elems = tree.weights.size()
print("Number of elements in dictionary: ",nmap_elems)

# Iterate over the map elements
for key, values in tree.weights:
    print(f"Key: {key}")
    print(f"  Number of values: {len(values)}")
    if len(values) > 0:
        print(f"  First few values: {list(values[:min(3, len(values))])}")

print("done")
