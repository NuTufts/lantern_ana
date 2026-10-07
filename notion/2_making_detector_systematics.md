# 2). Making Detector Systematics

- Note that this is only done for Run 3 (only have detsys files for Run 3 on the Tufts Cluster)
    - For Run 1 systematics, use the resulting Run 3 files
- The code below makes makes detvar samples with 1mil and 500k (SCE and recomb2) overlay samples, EXT, and data for Run 3
    - Does not make 100k sample (lower stats, was just a prelim sample), this was replaced with the 1mil
1. [MAKING NTUPLE] First, need to run my selection to make the detvar ntuples (making dlgen2 → ntuple file step)
    1. In this path: `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki`
    2. Have two yamls encompassing everything. This is because when I tried to run everything together (1mil, 500k, ext, data) in 1 yaml, for some reason the logs showed it would randomly stoped running on the cluster. So the two yamls needed for this are called: 
        - `split_run3_dlgen2_to_ntuple_1mil.yaml`
        - `split_run3_dlgen2_to_ntuple_500k_ext_data.yaml`
    - Output for both goes into `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki/output_split_tki_run3`
        - Output includes 1mil overlay CV file, 1mil of all variations, a 500k CV file, 500k variation files (SCE and recomb2), EXT file, and data file
2. [MAKING DETVAR FILES] Now run detvar yaml over the above ntuples to get variation files/histograms that I will use in my plotting code
    1. This yaml (remember it is run3 only) is located in `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/`
    2. The uncontained version of the files are (two separate ones for 1mil and 500k samples): 
        1. `tki_run3_detsys_1mil_uncontained.yaml`
        2. `tki_run3_detsys_cv500k_uncontained.yaml`
    3. Versions with containment cut (1mil and 500k): 
        1. `tki_run3_detsys_1mil_contained.yaml`
        2. `tki_run3_detsys_cv500k_contained.yaml`
    4. Inside these, make sure I have the cuts and bin configurations I want (these DO NOT include the containment cut) 
    5. To run them, in this folder, do `./run_xsecflux_ana.py <yaml>`
    6. The output files will go into the same `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/` folder! NOT in the directories specified in the files (but logs would be in there). The output filenames are (for both contained and uncontained, will output these): 
        1. `detsys_run3b_1mil_mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil.root`
        2. `detsys_cv500k_run3b_bnb_nu_overlay_500k_CV.root`
    7. Make sure to rename the above files to be either “_uncontained.root” or “_contained.root” at the end. Running the script again will overwrite the above filenames if the names are kept the same
3. Use these resulting files in my plotting code that takes detector systematics files as input