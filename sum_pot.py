#!/bin/env python3
import os,sys

def sum_pot_tree( pottree ):
    n = pottree.GetEntries()
    pot = 0.0
    for i in range(n):
        pottree.GetEntry(i)
        pot += pottree.totGoodPOT
    return pot

if __name__ == "__main__":

    import ROOT as rt
    fname = sys.argv[1]
    
    rfile = rt.TFile(fname,"open")
    pottree = rfile.Get("potTree")

    pot = sum_pot_tree(pottree)
    print("pot: ",pot)
