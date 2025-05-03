#!/usr/bin/env python3
from lantern_ana import LanternAna

print(LanternAna)

config = "numu_analysis.yaml"
ana = LanternAna(config)
ana.run()
