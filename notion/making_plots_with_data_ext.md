# Making Plots with data, EXT, etc.

The final plotting code is: 

`/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/organized_all_run_yamls/run1_run3_plotting_code_FINAL_REBINNED_100count_fixBinomEff.py`

### RUN 3 Weights Info

- **For overlay/simulation**, need to consider POT for the run. This is `targetpot / bnbnu_pot`
    - For Run3, `targetpot = 8.806e+18`
    - `bnbnu_pot` depends on the file itself. For this, we use the "1mil" CV file. The POT is in the livetime_tree in the root file. It is `1.34669e+21`
    - So scaling for simulation/overlay is `8.806e+18` / `1.34669e+21` = **0.00653899811 (confirm this)**
- **For EXT**, have spills. Need to take “E1DCNT” and divide by the sum of spills for each piece of EXT data.
    - Run3 reference is in Taritree’s analysis area. Go to lantern_ana/studies/numu_cc_inclusive/plot_run3b_1mil_numu_cc.py
        - Has a table for Run3
        - `E1DCNT = 2263559.0` (this is beam_numspills)
        - For Run3, I hadded 4 files (F, G1 (dlreco only), G2, G2a). Their spills are each listed in the “EXT_triggers” column of Taritree’s file
            - Total added up = 14817082.0 + 58677653.0 + 19214565.0 + 18619185.0 = 111328485.0 (this is extbnb_numspills)
        - Divide E1DCNT by this sum = 2263559.0 / **111328485.0 = 0.02033225369**
            - Weigh the EXT events in each bin by this number!
- **For data**, have no POT scaling/weighting. It is just “1.0”

### RUN 1 Weights Info

- Done similarly as above
- **For run1 overlay/simulation**,  `scaling = targetpot / bnbnu_pot`
    - For run 1, the target POT (numerator) will always be 4.446e+19
    - For the denominator `bnbnu_pot`, this depends on the ntuple used! So always check this! In the overlay ntuple, is the number in the `livetime_tree`
    - For my latest version, scaling = 4.446e+19 / 8.98323351831587e+20 = **0.04949220112**
    - This is the scaling to apply to the simulation for this run
    - Note that this targetpot number does NOT apply the “bad subrun list” (a todo list item for later?)
- **For run1 EXT,** for this analysis, use only run1_C1 (run1_C2 exists, but is not processed on the cluster?)
    - E1DCNT = 10375708.0, EXT_triggers for C1 = 34202767.0
    - EXT weighting to use: 10375708.0 / 34202767.0 = **0.30335873118**
- **For data**, have no POT scaling/weighting. It is just “1.0”