#!/usr/bin/env python3
# run.py

from lantern_ana import LanternAna

# Create analysis object
ana = LanternAna("numu_cc_tki_analysis.yaml")

# Run the analysis
ana.run()

print("✅ Analysis complete! Check ./my_first_results/ for output files")
