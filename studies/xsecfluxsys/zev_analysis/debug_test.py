import os
import ROOT as rt

"""
Debug script to inspect the contents of xsecflux covariance files
and print out histogram names
"""

# Files to check
files_to_check = [
    "../run1_outputs/xsecflux_run1_nue_intrinsic_nue.root",
    "../run1_outputs/xsecflux_run1_numu_intrinsic_nue.root",
    "temp_covar.root"
]

for filename in files_to_check:
    print("\n" + "="*80)
    print(f"Checking file: {filename}")
    print("="*80)
    
    if not os.path.exists(filename):
        print(f"  FILE NOT FOUND!")
        continue
    
    tfile = rt.TFile(filename)
    if not tfile or tfile.IsZombie():
        print(f"  ERROR: Could not open file!")
        continue
    
    # Get list of all keys
    keys = tfile.GetListOfKeys()
    print(f"\nTotal number of objects: {keys.GetEntries()}")
    
    # Categorize histograms
    cv_hists = []
    mean_hists = []
    var_hists = []
    other_hists = []
    
    for key in keys:
        name = key.GetName()
        if "_cv" in name:
            cv_hists.append(name)
        elif "_mean" in name:
            mean_hists.append(name)
        elif "_variance" in name:
            var_hists.append(name)
        else:
            other_hists.append(name)
    
    print(f"\nCV histograms ({len(cv_hists)}):")
    for name in cv_hists[:10]:  # Show first 10
        hist = tfile.Get(name)
        if hist:
            print(f"  {name} - Entries: {hist.GetEntries()}, Integral: {hist.Integral()}")
    if len(cv_hists) > 10:
        print(f"  ... and {len(cv_hists)-10} more")
    
    print(f"\nMean histograms ({len(mean_hists)}):")
    for name in mean_hists[:5]:  # Show first 5
        print(f"  {name}")
    if len(mean_hists) > 5:
        print(f"  ... and {len(mean_hists)-5} more")
    
    print(f"\nVariance histograms ({len(var_hists)}):")
    for name in var_hists[:5]:  # Show first 5
        print(f"  {name}")
    if len(var_hists) > 5:
        print(f"  ... and {len(var_hists)-5} more")
    
    if len(other_hists) > 0:
        print(f"\nOther objects ({len(other_hists)}):")
        for name in other_hists[:10]:
            print(f"  {name}")
        if len(other_hists) > 10:
            print(f"  ... and {len(other_hists)-10} more")
    
    # Try to infer the sample names and variables
    print("\n" + "-"*80)
    print("Attempting to parse sample names and variables from CV histograms:")
    print("-"*80)
    
    for cv_name in cv_hists[:5]:
        # Expected format: h{varname}_{sample}_cv
        # or possibly h{varname}__{sample}_cv
        parts = cv_name.split("_cv")[0]  # Remove _cv suffix
        print(f"\nCV histogram: {cv_name}")
        print(f"  Without _cv: {parts}")
        
        # Try to split and identify
        if parts.startswith("h"):
            parts = parts[1:]  # Remove leading 'h'
            # Look for pattern: could be varname_sample or varname__sample
            if "__" in parts:
                split_parts = parts.split("__")
                print(f"  Splitting on '__': {split_parts}")
                if len(split_parts) >= 2:
                    print(f"    -> Variable: {split_parts[0]}")
                    print(f"    -> Sample: {split_parts[1]}")
            else:
                # Try to split on single underscore
                # This is tricky since varname might have underscores
                print(f"  Contains single underscores, need to determine split point")
                print(f"  Full string after 'h': {parts}")
    
    tfile.Close()

print("\n" + "="*80)
print("Done!")
print("="*80)