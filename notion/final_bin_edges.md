# Final Bin Edges

- This is for all plots! Both Run 1 and Run 3, as well as Contained and Uncontained for each
- These were made by using an adaptive binning script to find a binning scheme that results in at least 100 raw MC events in each bin
    - The bottleneck is Run 3 Contained, it seems to have the fewest events. These bins were made from rebinning the Run 3 Contained, and happened to work for the others as well
- Script was: /cluster/tufts/wongjiradlabnu/pabrat01/lantern_ana/studies/xsecfluxsys/find_adaptive_bins_all_runs.py
    - Running with `python3 find_adaptive_bins_all_runs_100count.py —run 3 —contained` recomputes to bins. All other options just check if this run3 contained binning works for everything else
        - Old version is without the _100count part

NEW BIN EDGES WITH AT LEAST 100 RAW MC COUNTS PER BIN (use these): 

NEW_EDGES = {
"numuCC1piNpReco_delAlphaT":   [0.0, 18.0, 36.0, 54.0, 72.0, 90.0, 108.0, 126.0, 144.0, 162.0, 180.0],
"numuCC1piNpReco_pN":          [0.0, 0.128, 0.192, 0.256, 0.32, 0.384, 0.448, 0.512, 0.576, 0.64, 0.768, 1.6],
"numuCC1piNpReco_delPTT":      [-1.0, -0.36, -0.28, -0.2, -0.12, -0.04, 0.04, 0.12, 0.2, 0.28, 0.36, 1.0],
"numuCC1piNpReco_muKE":        [0.0, 60.0, 120.0, 180.0, 240.0, 300.0, 360.0, 420.0, 480.0, 540.0, 660.0, 1500.0],
"numuCC1piNpReco_pionKE":      [0.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 220.0, 260.0, 500.0],
"numuCC1piNpReco_maxprotonKE": [0.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 320.0, 360.0, 500.0],
}

---

---

---

---

---

---

OLD BIN EDGES WITH AT LEAST 10 RAW MC COUNTS PER BIN

delAlphaT:    [0.0, 18.0, 36.0, 54.0, 72.0, 90.0, 108.0, 126.0, 144.0, 162.0, 180.0]
pN:           [0.0, 0.064, 0.128, 0.192, 0.256, 0.32, 0.384, 0.448, 0.512, 0.576, 0.64, 0.704, 0.768, 0.832, 0.896, 0.96, 1.024, 1.088, 1.6]
delPTT:       [-1.0, -0.52, -0.44, -0.36, -0.28, -0.2, -0.12, -0.04, 0.04, 0.12, 0.2, 0.28, 0.36, 0.44, 0.52, 1.0]
muKE:         [0.0, 60.0, 120.0, 180.0, 240.0, 300.0, 360.0, 420.0, 480.0, 540.0, 600.0, 660.0, 720.0, 780.0, 840.0, 900.0, 1020.0, 1140.0, 1500.0]
pionKE:       [0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 300.0, 320.0, 340.0, 360.0, 500.0]
maxprotonKE:  [0.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 260.0, 280.0, 300.0, 320.0, 340.0, 360.0, 380.0, 400.0, 500.0]