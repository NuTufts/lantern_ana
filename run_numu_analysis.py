# run_numu_cc_analysis.py
import os
import sys
import argparse
import yaml
import ROOT
from lantern_ana.io.SampleDataset import SampleDataset
from lantern_ana.cuts.cut_factory import CutFactory
from lantern_ana.producers.producer_factory import ProducerFactory
from lantern_ana.producers.producerManager import ProducerManager

def main(config_file):
    # Load configuration
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create output directory if it doesn't exist
    output_dir = config.get('output_dir', '.')
    os.makedirs(output_dir, exist_ok=True)
    
    # Discover and register cuts and producers
    cut_factory = CutFactory()
    ProducerFactory.discover_producers("lantern_ana/producers")
    
    # Apply cuts from configuration
    for cut_name, cut_params in config.get('cuts', {}).items():
        cut_factory.add_cut(cut_name, cut_params)
    
    # Create producer manager
    producer_manager = ProducerManager()
    producer_manager.load_configuration(config_file)
    
    # Optionally print dependency graph
    if config.get('print_dependency_graph', False):
        producer_manager.print_dependency_graph()
    
    # Set up datasets
    datasets = {}
    for dataset_name, dataset_config in config.get('datasets', {}).items():
        file_path = dataset_config.get('filename')
        is_mc = dataset_config.get('ismc', False)
        
        print(f"Loading dataset {dataset_name} from {file_path}")
        dataset = SampleDataset(dataset_name, file_path, ismc=is_mc)
        datasets[dataset_name] = dataset
    
    # Process each dataset
    for dataset_name, dataset in datasets.items():
        print(f"Processing dataset: {dataset_name}")
        
        # Set up output file and tree
        output_file_path = os.path.join(output_dir, f"{dataset_name}_processed.root")
        output_file = ROOT.TFile(output_file_path, "RECREATE")
        output_tree = ROOT.TTree("numu_cc_tree", "Inclusive NuMu CC Events")
        
        # Prepare storage in output tree
        producer_manager.prepare_storage(output_tree)
        
        # Get ntuple
        ntuple = dataset.ntuple
        nentries = config.get('max_events', ntuple.GetEntries())
        if nentries<=0:
            nentries = ntuple.GetEntries()
        
        print(f"Processing {nentries} events")
        
        # Event loop
        n_passed = 0
        for i in range(nentries):
            if i > 0 and i % 1000 == 0:
                print(f"Processing event {i}/{nentries}")
            
            ntuple.GetEntry(i)
            
            # Apply cuts
            passes, cut_results = cut_factory.apply_cuts(ntuple)
            
            if passes:
                n_passed += 1
                
                # Process with producers
                event_data = {"gen2ntuple": ntuple}
                producer_manager.process_event(event_data, {"event_index": i})
                
                # Fill tree
                output_tree.Fill()
        
        print(f"Processed {nentries} events, {n_passed} passed cuts ({n_passed/nentries*100:.2f}%)")
        
        # Write and close output
        output_file.cd()
        output_tree.Write()
        output_file.Close()
        print(f"Results written to {output_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process ntuple files for inclusive numu CC analysis")
    parser.add_argument('config', help='Path to YAML configuration file')
    args = parser.parse_args()
    
    main(args.config)