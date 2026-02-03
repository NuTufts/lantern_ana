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


'''
py dump_surprise_weight_structure.py /pnfs/uboone/persistent/users/uboonepro/surprise/retuple/BNB/MCC9.10_Run4b_v10_04_07_20_BNB_nu_overlay_retuple_retuple_hist.root
Num Entries: 635989
Number of elements in dictionary:  18
Key: All_UBGenie
  Number of values: 500
  First few values: [1.3008141374478273, 1.3766012527192042, 1.0382438207498141]
Key: AxFFCCQEshape_UBGenie
  Number of values: 2
  First few values: [1.2556887255733338, 1.249732904553856]
Key: DecayAngMEC_UBGenie
  Number of values: 2
  First few values: [1.249732904553856, 1.249732904553856]
Key: NormCCCOH_UBGenie
  Number of values: 2
  First few values: [1.249732904553856, 1.249732904553856]
Key: NormNCCOH_UBGenie
  Number of values: 2
  First few values: [1.249732904553856, 1.249732904553856]
Key: RPA_CCQE_UBGenie
  Number of values: 2
  First few values: [1.6454448743717793, 0.8540209347359337]
Key: RootinoFix_UBGenie
  Number of values: 1
  First few values: [1.0]
Key: ThetaDelta2NRad_UBGenie
  Number of values: 2
  First few values: [1.249732904553856, 1.249732904553856]
Key: Theta_Delta2Npi_UBGenie
  Number of values: 2
  First few values: [1.249732904553856, 1.249732904553856]
Key: TunedCentralValue_UBGenie
  Number of values: 1
  First few values: [1.249732904553856]
Key: VecFFCCQEshape_UBGenie
  Number of values: 2
  First few values: [1.2959355497926863, 1.249732904553856]
Key: XSecShape_CCMEC_UBGenie
  Number of values: 2
  First few values: [1.249732904553856, 1.249732904553856]
Key: flux_all
  Number of values: 1000
  First few values: [1.0134712361028264, 1.0636540591536108, 1.0311838481323323]
Key: ppfx_all
  Number of values: 0
Key: reint_all
  Number of values: 1000
  First few values: [0.9862253475222929, 0.9580234919623365, 1.0275182332679123]
Key: splines_general_Spline
  Number of values: 1
  First few values: [1.0]
Key: xsr_scc_Fa3_SCC
  Number of values: 10
  First few values: [1.0002097352313706, 1.0007518674004936, 0.9991613802913236]
Key: xsr_scc_Fv3_SCC
  Number of values: 10
  First few values: [0.98668210670973, 0.975076258172307, 1.0011685476513525]
'''