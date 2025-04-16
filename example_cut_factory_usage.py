import os
import sys
import argparse

from lantern_ana.SampleDataset import SampleDataset
from lantern_ana.cuts import CutFactory

def main( ntuple_name, ntuple_path, event_limit=None ):
    # Create a sample dataset
    dataset = SampleDataset(ntuple_name, ntuple_path, ismc=True)
    eventTree = dataset.ntuple
    
    # Create a cut factory
    factory = CutFactory()
    
    # List available cuts
    print("Available cuts:", factory.list_available_cuts())
    
    # Add cuts with parameters
    factory.add_cut('fiducial_cut', {
        'width': 10.0,  # Use a wider fiducial volume
        'applyscc':True, # Apply Space Charge Correction
        'xKE':100.0,    # Apply KE threshold for X (other) particles
    })

    
    # Process events
    n_passed = 0
    n_total = 0

    print("Number of entries: ",eventTree.GetEntries())

    if event_limit is None:
        nentries = eventTree.GetEntries()
    if event_limit is not None and event_limit>0:
        event_limit = min( event_limit, eventTree.GetEntries())
    else:
        event_limit = eventTree.GetEntries()
    
    for i in range(event_limit):
        if i > 0 and i % 1000 == 0:
            print(f"Processing entry {i}/{eventTree.GetEntries()}")
            
        eventTree.GetEntry(i)
        n_total += 1
        
        # Apply all cuts
        passes, results = factory.apply_cuts(eventTree)
        
        if passes:
            n_passed += 1
            # Process passing event...
            
    # Print results
    print(f"Events processed: {n_total}")
    print(f"Events passed: {n_passed} ({n_passed/n_total*100:.2f}%)")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser("example_cut_factory_usage.py","Provides an example of how to define cut and use CutFactory")
    parser.add_argument('ntuple_path',help='ntuple file')
    parser.add_argument('--nentries',default=None,type=int,help='Number of entries to run.')
    args = parser.parse_args()
    main("ntuple",args.ntuple_path, event_limit=args.nentries)