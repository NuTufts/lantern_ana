# Cross Section and Flux Systematics

For the cross section and flux, we vary a set of parameters for these models and generate a weight for each event of the MC.  
Taking the entire set of MC events, by reweighting, 
we get a change in the predicted distribution of various observables as a function of model parameters.

We generate 1000 set of random draws based on prior distributions over the model parameters. 
The priors represent the amount of uncertainty on the model parameters and in principle have been constrained by external fits.

We store the weight for each event for each parameter draws in a TTree.

The trees are stored in ROOT files in this folder (made by Lauren Yates):

```
/pnfs/uboone/persistent/users/yatesla/arborist_mcc9/
```

The files available are:
```
[ tmw@uboonegpvm04 dlgen2_systematics ]$ ls -1 /pnfs/uboone/persistent/users/yatesla/arborist_mcc9/                                                        
arborist_v40_FakeDataSets2and3_bnb_nu_lowE_run3.root
arborist_v40_FakeDataSets2and3_bnb_nu_run1_partial.root
arborist_v40_FakeDataSets2and3_bnb_nu_run3.root
arborist_v40_FakeDataSets2and3_cc_pi0_run1_partial.root
arborist_v40_FakeDataSets2and3_cc_pi0_run3_partial.root
arborist_v40_FakeDataSets2and3_intrinsic_nue_run1.root
arborist_v40_FakeDataSets2and3_intrinsic_nue_run3.root
arborist_v40_FakeDataSets2and3_nc_pi0_run1_partial.root
arborist_v40_FakeDataSets2and3_nc_pi0_run3_partial.root
arborist_v40_bnb_nu_lowE_run1.root
arborist_v40_bnb_nu_lowE_run3.root
arborist_v40_bnb_nu_run1.root
arborist_v40_bnb_nu_run2.root
arborist_v40_bnb_nu_run3.root
arborist_v40_detsys_bnb_nu_run3b.root
arborist_v40_detsys_intrinsic_nue_run3b.root
arborist_v40_dirt_nu_run1.root
arborist_v40_dirt_nu_run3.root
arborist_v40_intrinsic_nue_lowE_run1.root
arborist_v40_intrinsic_nue_lowE_run3.root
arborist_v40_intrinsic_nue_run1.root
arborist_v40_intrinsic_nue_run2.root
arborist_v40_intrinsic_nue_run3.root
arborist_v48_Sep24_SingleKnobs_bnb_nu_lowE_run1.root
arborist_v48_Sep24_SingleKnobs_bnb_nu_lowE_run3.root
arborist_v48_Sep24_SingleKnobs_bnb_nu_run1.root
arborist_v48_Sep24_SingleKnobs_bnb_nu_run2.root
arborist_v48_Sep24_SingleKnobs_bnb_nu_run3.root
arborist_v48_Sep24_SingleKnobs_intrinsic_nue_lowE_run1.root
arborist_v48_Sep24_SingleKnobs_intrinsic_nue_lowE_run3.root
arborist_v48_Sep24_SingleKnobs_intrinsic_nue_run1.root
arborist_v48_Sep24_SingleKnobs_intrinsic_nue_run2.root
arborist_v48_Sep24_SingleKnobs_intrinsic_nue_run3.root
arborist_v48_Sep24_intrinsic_nue_run1_noNaNs.root
arborist_v48_Sep24_withExtraGENIE_bnb_nu_DetVar_run1.root
arborist_v48_Sep24_withExtraGENIE_bnb_nu_DetVar_run3.root
arborist_v48_Sep24_withExtraGENIE_bnb_nu_lowE_run1.root
arborist_v48_Sep24_withExtraGENIE_bnb_nu_lowE_run2.root
arborist_v48_Sep24_withExtraGENIE_bnb_nu_lowE_run3.root
arborist_v48_Sep24_withExtraGENIE_bnb_nu_run1.root
arborist_v48_Sep24_withExtraGENIE_bnb_nu_run1_noNaNs.root
arborist_v48_Sep24_withExtraGENIE_bnb_nu_run2.root
arborist_v48_Sep24_withExtraGENIE_bnb_nu_run3.root
arborist_v48_Sep24_withExtraGENIE_cc_pi0_run1.root
arborist_v48_Sep24_withExtraGENIE_cc_pi0_run3.root
arborist_v48_Sep24_withExtraGENIE_dirt_nu_run1.root
arborist_v48_Sep24_withExtraGENIE_dirt_nu_run3.root
arborist_v48_Sep24_withExtraGENIE_eLEE_high_DetVar_run1.root
arborist_v48_Sep24_withExtraGENIE_eLEE_high_DetVar_run3.root
arborist_v48_Sep24_withExtraGENIE_eLEE_low_DetVar_run1.root
arborist_v48_Sep24_withExtraGENIE_eLEE_low_DetVar_run3.root
arborist_v48_Sep24_withExtraGENIE_fullosc_nue_run1.root
arborist_v48_Sep24_withExtraGENIE_fullosc_nue_run2.root
arborist_v48_Sep24_withExtraGENIE_fullosc_nue_run3.root
arborist_v48_Sep24_withExtraGENIE_intrinsic_nue_DetVar_run1.root
arborist_v48_Sep24_withExtraGENIE_intrinsic_nue_DetVar_run3.root
arborist_v48_Sep24_withExtraGENIE_intrinsic_nue_lowE_run1.root
arborist_v48_Sep24_withExtraGENIE_intrinsic_nue_lowE_run2.root
arborist_v48_Sep24_withExtraGENIE_intrinsic_nue_lowE_run3.root
arborist_v48_Sep24_withExtraGENIE_intrinsic_nue_run1.root
arborist_v48_Sep24_withExtraGENIE_intrinsic_nue_run2.root
arborist_v48_Sep24_withExtraGENIE_intrinsic_nue_run3.root
arborist_v48_Sep24_withExtraGENIE_nc_pi0_run1.root
arborist_v48_Sep24_withExtraGENIE_nc_pi0_run2.root
arborist_v48_Sep24_withExtraGENIE_nc_pi0_run3.root
arborist_v55_Jun12_withExtraGENIE_bnb_nu_run1.root
arborist_v55_Jun12_withExtraGENIE_bnb_nu_run1_noNaNs.root
arborist_v55_Jun12_withExtraGENIE_bnb_nu_run2.root
arborist_v55_Jun12_withExtraGENIE_bnb_nu_run3.root
arborist_v55_Jun12_withExtraGENIE_intrinsic_nue_run1.root
arborist_v55_Jun12_withExtraGENIE_intrinsic_nue_run2.root
arborist_v55_Jun12_withExtraGENIE_intrinsic_nue_run3.root
arborist_v55_Jun20_withExtraGENIE_bnb_nu_run1.root
arborist_v55_Jun20_withExtraGENIE_bnb_nu_run1_noNaNs.root
arborist_v55_Jun20_withExtraGENIE_bnb_nu_run2.root
arborist_v55_Jun20_withExtraGENIE_bnb_nu_run3.root
arborist_v55_Jun20_withExtraGENIE_cc_pi0_run1.root
arborist_v55_Jun20_withExtraGENIE_cc_pi0_run3.root
arborist_v55_Jun20_withExtraGENIE_intrinsic_nue_run1.root
arborist_v55_Jun20_withExtraGENIE_intrinsic_nue_run2.root
arborist_v55_Jun20_withExtraGENIE_intrinsic_nue_run3.root
arborist_v55_Jun20_withExtraGENIE_nc_pi0_run1.root
arborist_v55_Jun20_withExtraGENIE_nc_pi0_run3.root
```

Within each ROOT file is a single TTree named `eventweight_tree`.
It has the following structure:

```
******************************************************************************
*Tree    :eventweight_tree: eventweight_tree                                       *
*Entries :  1084394 : Total =    162510239855 bytes  File  Size = 92267832243 *
*        :          : Tree compression factor =   1.76                       *
******************************************************************************
*Br    0 :run       : run/I                                                  *
*Entries :  1084394 : Total  Size=    4651217 bytes  File Size  =     459146 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=  10.00     *
*............................................................................*
*Br    1 :subrun    : subrun/I                                               *
*Entries :  1084394 : Total  Size=    4660445 bytes  File Size  =     661969 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   6.95     *
*............................................................................*
*Br    2 :event     : event/I                                                *
*Entries :  1084394 : Total  Size=    4657369 bytes  File Size  =    2304406 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   1.99     *
*............................................................................*
*Br    3 :nu_pdg    : nu_pdg/I                                               *
*Entries :  1084394 : Total  Size=    4660445 bytes  File Size  =     444242 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=  10.35     *
*............................................................................*
*Br    4 :nu_energy_true : nu_energy_true/D                                  *
*Entries :  1084394 : Total  Size=    9022637 bytes  File Size  =    6237276 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   1.44     *
*............................................................................*
*Br    5 :nu_interaction_ccnc : nu_interaction_ccnc/I                        *
*Entries :  1084394 : Total  Size=    4700433 bytes  File Size  =     845201 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   5.49     *
*............................................................................*
*Br    6 :nu_interaction_mode : nu_interaction_mode/I                        *
*Entries :  1084394 : Total  Size=    4700433 bytes  File Size  =    1077041 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   4.31     *
*............................................................................*
*Br    7 :nu_interaction_type : nu_interaction_type/I                        *
*Entries :  1084394 : Total  Size=    4700433 bytes  File Size  =    1437503 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   3.23     *
*............................................................................*
*Br    8 :nu_target_pdg : nu_target_pdg/I                                    *
*Entries :  1084394 : Total  Size=    4681977 bytes  File Size  =     799435 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   5.78     *
*............................................................................*
*Br    9 :nu_L_true : nu_L_true/D                                            *
*Entries :  1084394 : Total  Size=    9007257 bytes  File Size  =    8385140 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   1.07     *
*............................................................................*
*Br   10 :spline_weight : spline_weight/D                                    *
*Entries :  1084394 : Total  Size=    9019561 bytes  File Size  =    3911532 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   2.29     *
*............................................................................*
*Br   11 :rootino_weight : rootino_weight/D                                  *
*Entries :  1084394 : Total  Size=    9022637 bytes  File Size  =     457728 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=  19.58     *
*............................................................................*
*Br   12 :ub_tune_weight : ub_tune_weight/D                                  *
*Entries :  1084394 : Total  Size=    9022637 bytes  File Size  =    4629339 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   1.94     *
*............................................................................*
*Br   13 :xsec_corr_weight : xsec_corr_weight/D                              *
*Entries :  1084394 : Total  Size=    9028789 bytes  File Size  =    4659105 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=   1.92     *
*............................................................................*
*Br   14 :lee_weight : lee_weight/D                                          *
*Entries :  1084394 : Total  Size=    9010333 bytes  File Size  =     422868 *
*Baskets :     3072 : Basket Size=      51200 bytes  Compression=  21.16     *
*............................................................................*
*Br   15 :sys_weights : map<string,vector<double> >                          *
*Entries :1084394 : Total  Size=162409692689 bytes  File Size  = 92230582732 *
*Baskets :     9215 : Basket Size=   25600000 bytes  Compression=   1.76     *
*............................................................................*
```

Code matt used to parse the tree using sbnfit (deprecated):
```
/exp/uboone/app/users/mmr/dlgen2_systematics
```

