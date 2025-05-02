#!/usr/bin/env python3
"""
Example script for analyzing neutrino events using the lantern_ana framework.
This script:
1. Loads datasets from a YAML configuration
2. Sets up cuts for neutrino event selection
3. Configures producers to calculate derived variables
4. Processes events and creates output histograms
"""

import os
import sys
import argparse
import yaml
import ROOT
from array import array

# Import from lantern_ana package
from lantern_ana.io.DatasetFactory import DatasetFactory

test_config = 'datasets/lantern_dataset_test.yaml'

print("Load dataset(s) from test config: ",test_config)

testdata = DatasetFactory.create_from_yaml(test_config)
for k in testdata:
    print(f"Number of entries[{k}]: {testdata[k].get_num_entries()}")