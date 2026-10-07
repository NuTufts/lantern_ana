# 3). Making xsecflux systematics

Remember that all selections cuts must be made in these scripts, if they are not already made in the ntuple! (E.g. containment in my selection)  

Also, need to make “uncontained” version of systematics for uncontained plots/sample

Run 1 Uncontained Systematics

- This is the xsecflux file creation script for Run 1: `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/tki_run1_xsecflux_march2026_uncontained.yaml`
    - Takes as input the run1 bnb overlay ntuple in `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki/output_master_tki_run1`
    - Output is located in `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/systematics_output_run1_march2026_uncontained/output_xsecflux_tki_run1_march2026_uncontained.root`
    - To run it, in the xsecfluxsys folder, do `./run_xsecflux_ana.py tki_run1_xsecflux_march2026_uncontained.yaml`

Run 1 Contained Systematics

- This is the xsecflux file creation script for Run 1: `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/tki_run1_xsecflux_march2026_contained.yaml`
    - Takes as input the run1 bnb overlay ntuple in `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki/output_master_tki_run1`
    - Output is located in `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/systematics_output_run1_march2026_contained/output_xsecflux_tki_run1_march2026_contained.root`
    - To run it, in the xsecfluxsys folder, do `./run_xsecflux_ana.py tki_run1_xsecflux_march2026_contained.yaml`

Run 3 Uncontained

- Use this script for Run 3: `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/tki_run3b_1mil_xsecflux_uncontained.yaml`
    - This looks at what is in the `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki/output_tki_run3b_1mil` directory, in this case `mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_20260122_154228.root` (this is the 1mil CV file)
- To run it: `./run_xsecflux_ana.py tki_run3b_1mil_xsecflux_uncontained.yaml`
- Output goes into this directory: `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana//studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux_uncontained/output_xsecflux_tki_run3b_1mil_uncontained.root`

Run 3 Contained Systematics

- Use this script for Run 3: `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/tki_run3b_1mil_xsecflux_contained.yaml`
    - This looks at what is in the `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/numu_cc_tki/output_tki_run3b_1mil` directory, in this case `mcc9_v29e_dl_run3b_bnb_nu_overlay_1mil_20260122_154228.root` (this is the 1mil CV file)
- To run it: `./run_xsecflux_ana.py tki_run3b_1mil_xsecflux_contained.yaml`
- Output goes into this directory: `/cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana//studies/xsecfluxsys/output_tki_run3b_1mil_xsecflux_contained/output_xsecflux_tki_run3b_1mil_contained.root`