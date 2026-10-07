# 4). Chi-Square Calculations

This includes making covariance matrix plots as well as the table with chi-square, p-values, etc. 

The examples below are for Run 1 contained events. The instructions/paths/files for the rest (Run 1 uncontained, Run 3 Contained and Run 3 uncontained) are below

**General gist:** 

- To make covariance matrix plots, take as input the systematics file but rebinned
- Note that we had to rebin so all bins had at least 100 raw MC counts, so the chi-square wasn’t a weird at those bins
    - Claude script to rebin the original binning of xsecflux file to new one:
    `python3 rebin_xsecflux_100count.py --run 1 --contained`
    - New output files:
        - Run 1 Contained: /cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/systematics_output_run1_march2026_contained/output_xsecflux_tki_run1_march2026_contained_rebinned_100count.root
        - Run 1 Uncontained: /cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/systematics_output_run1_march2026_uncontained/output_xsecflux_tki_run1_march2026_uncontained_rebinned_100count.root
        - Run 3 Contained: /cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux_contained/output_xsecflux_tki_run3b_1mil_contained_rebinned_100count.root
        - Run 3 Uncontained: /cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux_uncontained/output_xsecflux_tki_run3b_1mil_uncontained_rebinned_100count.root

**Instructions (for Run 1 Contained):** 

1). Run T’s covariance matrix creation script on the new rebinned xsecflux file (have to use the 6var one I customized for my analysis):

- `python3 make_covar_matrices_6var_all_runs_100count.py --run 1 --contained`
    - It will recognize it from the filenames above (no need to input it as an arg)
- Output is: `output_covariance_run1_contained.root`

2). (Optional) Make those fractional uncertainty and covar matrix diagonal comparison plots with event counts. Use the script “plot_xsecflux_fracunc3.py” to do this

- go in and change the XSECFLUX file part to be the rebinned one
run with: python3 plot_xsecflux_fracunc3.py
this checks if any bins have ratios off from 1 (just a sanity check)

3). Calculate chi-2 and make p-value table. In this script, check to make sure it has the right inputs:

- `python3 compute_chi2_tki_100count.py --run 1 --contained`