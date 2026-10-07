# 1). Making dlgen2 → ntuple files

- dlgen2 are the original “full” files
- Need to run them through my selection to make ntuple files that are used for analysis plots
- Note that my selection does not include containment cut, but the ntuple does. Will use this cut later on in the systematics yaml and in plotting code

### Current Run 3 Instruction files/paths/commands:

How to make/remake:

1. Go to `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki`
2. Open `split_run3_dlgen2_to_ntuple_1mil.yaml` and `split_run3_dlgen2_to_ntuple_500k_ext_data.yaml` if need to edit anything
3. To run (each): 
    1. `nohup run_lantern_ana.py split_run3_dlgen2_to_ntuple_1mil.yaml > output_split_run3_1mil_<date>.out &`
    2. `nohup run_lantern_ana.py split_run3_dlgen2_to_ntuple_500k_ext_data.yaml > output_split_run3_500k_ext_data_<date>.out &`
    3. Will take a while to run, so better to leave it in the background (check the logs to see if they completed) 
4. Output ntuple root files will be put into this dir: `output_split_tki_run3`

*****NOTE: The full Run3 master file does not finish sometimes :((( So I made two split parts, one with just the 1 mil and one with the rest (500k, ext, data). *****

### **Run 3 Instructions:**

This procedure makes the following (for run3 only):

- 1Mil sample for detector systematics
    - Includes CV file, LYAtt, LYDown, etc…
    - 1Mil CV file is overlay, can be used for xsecflux systematics plots downstream
- 500k sample for detector systematics (for SCE and recomb2)
- EXT file for run3 (hadded 4 files for this: F, G1, G2, and G2a)
- Data file for run3 (1e19)

How to make/remake:

1. Go to `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki`
2. Open `master_run3_dlgen2_to_ntuple_1mil.yaml` if need to edit anything
3. To run: `nohup run_lantern_ana.py master_run3_dlgen2_to_ntuple_1mil.yaml > output_master_run3_<date>.out &`
    1. Will take a while to run, so better to leave it in the background
4. Output ntuple root files will be put into this dir: `output_master_tki_run3`

### **Run 1 Instructions:**

- Taritree says we do not have detector systematics for Run 1 on the cluster (I think SURPRISE has them for Zev tho?).
    - He says to use the run3 detector systematics for run1…
- In any case, in this master script example above, we do NOT make detsys files for run1!
- Go to `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki`
- Open `master_run1_dlgen2_to_ntuple.yaml` if need to edit anything
    - ~~The overlay uses a v7 “nocrtremerge” file. Taritree says this is fine (up to date and all that)~~ Apparently this was run3??!
    - Should use `dlgen2_reco_v2me06_ntuple_v5_mcc9_v28_wctagger_bnboverlay.root`, this is run1
- To run: `nohup run_lantern_ana.py master_run1_dlgen2_to_ntuple.yaml > output_master_run1_<date>.out &`
- Output files are in `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki/output_master_tki_run1`
    - Quick check: the correct run1 output file here will have a POT of 4.67569e+20 in the livetime tree