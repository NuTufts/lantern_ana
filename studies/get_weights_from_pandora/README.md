This folder contains scripts used to extract weights from the pandora selection tree.

## Getting the GENIE tune weight

We needed to grab the GENIE tune weights for each event, which did not get passed into the lantern ntuple properly.

But no matter, as the pandora tree has this information.

To use the script, you have to first go into the script, `Strip_xsecweight.C`, to select which input and output path you want.

There are two hard-coded options currently for the BNB nu and BNB nue overlay files.

Then to run the script, enter:

```
root -x Strip_xsecweight.C
```

## Xsec and Flux systematic uncertainties

The pandora tree also has the xsec and flux weights from the N throws of the systematic uncertainty parameter priors.

Branches in the Pandora tree, 'nuselection/NuSelectionFilter':

The event index branches:
```
*............................................................................*
*Br    1 :run       : run/I                                                  *
*Entries :   170233 : Total  Size=     781727 bytes  File Size  =     109352 *
*Baskets :      922 : Basket Size=      32000 bytes  Compression=   6.98     *
*............................................................................*
*Br    2 :sub       : sub/I                                                  *
*Entries :   170233 : Total  Size=     781727 bytes  File Size  =     185234 *
*Baskets :      922 : Basket Size=      32000 bytes  Compression=   4.12     *
*............................................................................*
*Br    3 :evt       : evt/I                                                  *
*Entries :   170233 : Total  Size=     781727 bytes  File Size  =     453893 *
*Baskets :      922 : Basket Size=      32000 bytes  Compression=   1.68     *
*............................................................................*
```

Branches that have to do with weights:

```
*............................................................................*
*Br  402 :weights   : Int_t weights_                                         *
*Entries :   201771 : Total  Size=    1783426 bytes  File Size  =     282409 *
*Baskets :      192 : Basket Size=      32000 bytes  Compression=   5.78     *
*............................................................................*
*Br  403 :weights.first : string first[weights_]                             *
*Entries :   201771 : Total  Size=   68626945 bytes  File Size  =    1202579 *
*Baskets :      192 : Basket Size=     621056 bytes  Compression=  57.06     *
*............................................................................*
*Br  404 :weights.second : vector<double> second[weights_]                   *
*Entries :201771 : Total  Size= 4119022055 bytes  File Size  = 3741431215 *
*Baskets :     6840 : Basket Size=     621056 bytes  Compression=   1.10     *
*............................................................................*
*Br  405 :weightsFlux : vector<unsigned short>                               *
*Entries :   201771 : Total  Size=  406462377 bytes  File Size  =  274398653 *
*Baskets :      762 : Basket Size=     621056 bytes  Compression=   1.48     *
*............................................................................*
*Br  406 :weightsGenie : vector<unsigned short>                              *
*Entries :   201771 : Total  Size=  204644263 bytes  File Size  =  160884613 *
*Baskets :      382 : Basket Size=     621056 bytes  Compression=   1.27     *
*............................................................................*
*Br  407 :weightsReint : vector<unsigned short>                              *
*Entries :   201771 : Total  Size=  406463143 bytes  File Size  =  281742058 *
*Baskets :      762 : Basket Size=     621056 bytes  Compression=   1.44     *
*............................................................................*
*Br  408 :weightSpline : weightSpline/F                                      *
*Entries :   201771 : Total  Size=     874677 bytes  File Size  =      76768 *
*Baskets :      570 : Basket Size=       2048 bytes  Compression=  11.24     *
*............................................................................*
*Br  409 :weightTune : weightTune/F                                          *
*Entries :   201771 : Total  Size=     873529 bytes  File Size  =     533146 *
*Baskets :      570 : Basket Size=       2048 bytes  Compression=   1.62     *
*............................................................................*
*Br  410 :weightSplineTimesTune : weightSplineTimesTune/F                    *
*Entries :   201771 : Total  Size=     879843 bytes  File Size  =     539629 *
*Baskets :      570 : Basket Size=       2048 bytes  Compression=   1.61     *
*............................................................................*
*Br  411 :knobRPAup : knobRPAup/D                                            *
*Entries :   201771 : Total  Size=    1658312 bytes  File Size  =     928282 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.78     *
*............................................................................*
*Br  412 :knobRPAdn : knobRPAdn/D                                            *
*Entries :   201771 : Total  Size=    1658312 bytes  File Size  =     928729 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.78     *
*............................................................................*
*Br  413 :knobCCMECup : knobCCMECup/D                                        *
*Entries :   201771 : Total  Size=    1659082 bytes  File Size  =     921634 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  414 :knobCCMECdn : knobCCMECdn/D                                        *
*Entries :   201771 : Total  Size=    1659082 bytes  File Size  =     784191 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   2.11     *
*............................................................................*
*Br  415 :knobAxFFCCQEup : knobAxFFCCQEup/D                                  *
*Entries :   201771 : Total  Size=    1660237 bytes  File Size  =     922063 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  416 :knobAxFFCCQEdn : knobAxFFCCQEdn/D                                  *
*Entries :   201771 : Total  Size=    1660237 bytes  File Size  =     922777 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  417 :knobVecFFCCQEup : knobVecFFCCQEup/D                                *
*Entries :   201771 : Total  Size=    1660622 bytes  File Size  =     921639 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  418 :knobVecFFCCQEdn : knobVecFFCCQEdn/D                                *
*Entries :   201771 : Total  Size=    1660622 bytes  File Size  =     923158 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  419 :knobDecayAngMECup : knobDecayAngMECup/D                            *
*Entries :   201771 : Total  Size=    1661392 bytes  File Size  =     923414 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  420 :knobDecayAngMECdn : knobDecayAngMECdn/D                            *
*Entries :   201771 : Total  Size=    1661392 bytes  File Size  =     923920 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  421 :knobThetaDelta2Npiup : knobThetaDelta2Npiup/D                      *
*Entries :   201771 : Total  Size=    1662547 bytes  File Size  =    1303421 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.27     *
*............................................................................*
*Br  422 :knobThetaDelta2Npidn : knobThetaDelta2Npidn/D                      *
*Entries :   201771 : Total  Size=    1662547 bytes  File Size  =     925179 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  423 :knobThetaDelta2NRadup : knobThetaDelta2NRadup/D                    *
*Entries :   201771 : Total  Size=    1662932 bytes  File Size  =     925560 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  424 :knobThetaDelta2NRaddn : knobThetaDelta2NRaddn/D                    *
*Entries :   201771 : Total  Size=    1662932 bytes  File Size  =     925560 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  425 :knobNormCCCOHup : knobNormCCCOHup/D                                *
*Entries :   201771 : Total  Size=    1660622 bytes  File Size  =     925188 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  426 :knobNormCCCOHdn : knobNormCCCOHdn/D                                *
*Entries :   201771 : Total  Size=    1660622 bytes  File Size  =     923158 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  427 :knobNormNCCOHup : knobNormNCCOHup/D                                *
*Entries :   201771 : Total  Size=    1660622 bytes  File Size  =     923158 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  428 :knobNormNCCOHdn : knobNormNCCOHdn/D                                *
*Entries :   201771 : Total  Size=    1660622 bytes  File Size  =     923158 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   1.79     *
*............................................................................*
*Br  429 :knobxsr_scc_Fv3up : knobxsr_scc_Fv3up/D                            *
*Entries :   201771 : Total  Size=    1661392 bytes  File Size  =     372716 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   4.44     *
*............................................................................*
*Br  430 :knobxsr_scc_Fv3dn : knobxsr_scc_Fv3dn/D                            *
*Entries :   201771 : Total  Size=    1661392 bytes  File Size  =     381572 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   4.33     *
*............................................................................*
*Br  431 :knobxsr_scc_Fa3up : knobxsr_scc_Fa3up/D                            *
*Entries :   201771 : Total  Size=    1661392 bytes  File Size  =     649677 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   2.54     *
*............................................................................*
*Br  432 :knobxsr_scc_Fa3dn : knobxsr_scc_Fa3dn/D                            *
*Entries :   201771 : Total  Size=    1661392 bytes  File Size  =     674177 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=   2.45     *
*............................................................................*
*Br  433 :RootinoFix : RootinoFix/D                                          *
*Entries :   201771 : Total  Size=    1658697 bytes  File Size  =      59612 *
*Baskets :      381 : Basket Size=       7680 bytes  Compression=  27.69     *
*............................................................................*
```

The data in the `weights` branch, which is a map<string,vector<double>>, looks like the following:

```
[ tmw@uboonegpvm04 get_weights_from_pandora ]$ ./inspect_weights 
Inspect weights in Pandora tree.
Number of entries: 170233
Data in map for Entry[0]
  All_UBGenie: nweights=500
  AxFFCCQEshape_UBGenie: nweights=2
  DecayAngMEC_UBGenie: nweights=2
  NormCCCOH_UBGenie: nweights=2
  NormNCCOH_UBGenie: nweights=2
  RPA_CCQE_UBGenie: nweights=2
  RootinoFix_UBGenie: nweights=1
  ThetaDelta2NRad_UBGenie: nweights=2
  Theta_Delta2Npi_UBGenie: nweights=2
  TunedCentralValue_UBGenie: nweights=1
  VecFFCCQEshape_UBGenie: nweights=2
  XSecShape_CCMEC_UBGenie: nweights=2
  flux_all: nweights=1000
  ppfx_all: nweights=0
  reint_all: nweights=1000
  splines_general_Spline: nweights=1
  xsr_scc_Fa3_SCC: nweights=10
  xsr_scc_Fv3_SCC: nweights=10
```

TODO: extract these for use by the lantern ana framework.
