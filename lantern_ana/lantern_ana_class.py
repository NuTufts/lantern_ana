"""
Main LanternAna class for the Lantern Analysis Framework

This module provides the LanternAna class which combines the dataset, cut, and producer
systems into a unified analysis framework that can be configured via YAML files.
"""

"""
Enhanced LanternAna class with producer-first architecture support
"""

import os
import sys
import yaml
import time
import logging
import ROOT
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from array import array

# Import core components
from lantern_ana.io.dataset_factory import DatasetFactory
from lantern_ana.cuts.cut_factory import CutFactory
from lantern_ana.producers.producer_factory import ProducerFactory
from lantern_ana.producers.producerManager import ProducerManager
from lantern_ana.tags.tag_factory import TagFactory

class LanternAna:
    """
    LanternAna with producer-first architecture.
    
    Key changes:
    - Producers run first and generate all features
    - Cuts receive producer outputs via params
    - Clean separation of feature calculation and selection logic
    """
    
    def __init__(self, config_file: str, log_level: str = "INFO"):
        """Initialize the framework."""
        
        # Load configuration
        self.config_file = config_file
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

        # Create output directory
        self.output_dir = self.config.get('output_dir', '.')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up logging
        self._setup_logging(log_level)
        self.logger = logging.getLogger("LanternAna")

        self.logger.info(f"Loading configuration from {config_file}")

        # Configuration options
        self._filter_events = self.config.get('filter_events', False)
        self._producer_first = self.config.get('producer_first_mode', True)  # New option
        
        # Initialize components
        self._discover_components()
        
        # Initialize factories
        self.cut_factory = CutFactory()
        self.producer_manager = ProducerManager()
        self.tag_factory = TagFactory()
        
        # Configure components from YAML
        self._configure_components()
        
        # Initialize dataset
        self.datasets = {}
        
        # Statistics
        self.stats = {}
        
    def _setup_logging(self, level_str: str):
        """Set up logging configuration."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        level = level_map.get(level_str.upper(), logging.INFO)
        
        # Only configure root logger if not already configured
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(sys.stdout),
                    logging.FileHandler(os.path.join(self.output_dir, 'lantern_ana.log'))
                ]
            )
    
    def _discover_components(self):
        """Discover and load all available components."""
        import lantern_ana
        import os

        self.logger.info("Discovering components...")
        
        # Auto-discover cuts, producers, and dataset types
        CutFactory.auto_discover_cuts()
        homedir = os.path.dirname(lantern_ana.__file__)
        ProducerFactory.discover_producers(f"{homedir}/producers")
        DatasetFactory.discover_datasets(f"{homedir}/io")
        TagFactory.auto_discover_tags()
        
        self.logger.info(f"Found {len(CutFactory.list_available_cuts())} cuts")
        self.logger.info(f"Found {len(ProducerFactory.list_producers())} producers")
        self.logger.info(f"Found {len(DatasetFactory.list_registered_datasets())} dataset types")
        self.logger.info(f"Found {len(TagFactory.list_available_tags())} tags")
    
    def _configure_components(self):
        """Configure components from YAML configuration."""
        self.logger.info("Configuring components...")
        
        # Configure producer manager first (producer-first architecture)
        self.producer_manager.load_configuration(self.config_file)
        
        # Configure cuts - they'll get producer data at runtime
        for cut_name, cut_params in self.config.get('cuts', {}).items():
            self.logger.debug(f"Adding cut: {cut_name}")
            self.cut_factory.add_cut(cut_name, cut_params)
        
        # Set cut logic if provided
        if 'cut_logic' in self.config:
            self.logger.debug(f"Setting cut logic: {self.config['cut_logic']}")
            self.cut_factory.set_cut_logic(self.config['cut_logic'])
        
        # Configure tags
        for tag_name, tag_params in self.config.get('tags', {}).items():
            self.logger.debug(f"Adding tag: {tag_name}")
            self.tag_factory.add_tag(tag_name, tag_params)
    
    def load_datasets(self):
        """Load datasets from configuration."""
        self.logger.info("Loading datasets...")
        
        # Create datasets from configuration
        self.datasets = DatasetFactory.create_from_yaml(self.config_file)
        
        for name, dataset in self.datasets.items():
            dataset.initialize()
            self.logger.info(f"Loaded dataset '{name}' with {dataset.get_num_entries()} entries")
            if dataset.ismc:
                self.logger.info(f"  MC dataset with {dataset.pot} POT")
    
    def run(self, dataset_names: Optional[List[str]] = None):
        """Run the analysis on specified datasets."""
        self.logger.info("Starting enhanced analysis run...")
        
        # Load datasets if not already loaded
        if not self.datasets:
            self.load_datasets()
        
        # Determine which datasets to process
        if dataset_names is None:
            datasets_to_process = self.datasets
        else:
            datasets_to_process = {name: self.datasets[name] for name in dataset_names if name in self.datasets}
            if len(datasets_to_process) != len(dataset_names):
                missing = set(dataset_names) - set(datasets_to_process.keys())
                self.logger.warning(f"Some requested datasets were not found: {missing}")
        
        # Process each dataset
        for dataset_name, dataset in datasets_to_process.items():
            if dataset.do_we_process():
                self._process_dataset_enhanced(dataset_name, dataset)
        
        # Print statistics
        self._print_statistics()
        
        self.logger.info("analysis complete!")
    
    def save_statistics(self, filename: str):
        """Save analysis statistics to file."""
        import yaml
        
        # Combine analysis and producer statistics
        stats_data = {
            'analysis_statistics': self.stats,
            'producer_statistics': self.producer_manager.get_performance_summary() if hasattr(self.producer_manager, 'get_performance_summary') else {}
        }
        
        # Save as YAML
        with open(filename, 'w') as f:
            yaml.dump(stats_data, f, indent=2)
        
        self.logger.info(f"Statistics saved to: {filename}")
    
    def _process_dataset_enhanced(self, dataset_name: str, dataset):
        """
        Process a single dataset with producer-first architecture.
        """
        self.logger.info(f"Processing dataset with enhanced architecture: {dataset_name}")
        
        # Create output file and tree
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_path = os.path.join(self.output_dir, f"{dataset_name}_{timestamp}.root")
        output_file = ROOT.TFile(output_file_path, "RECREATE")
        output_tree = ROOT.TTree("analysis_tree", "Processed Events")
        
        # Create POT tree for MC datasets
        pot_tree = ROOT.TTree("livetime_tree", "POT and nspills Information")
        pot = array('f', [0.0])
        nspills = array('f', [0.0])
        ismc = array('i', [0])
        pot_tree.Branch("pot", pot, "pot/F")
        pot_tree.Branch("nspills", nspills, "nspills/F")
        pot_tree.Branch("ismc", ismc, "ismc/I")
        
        # Set POT information
        ismc[0] = 1 if dataset.ismc else 0
        pot[0] = dataset.pot
        nspills[0] = dataset.nspills
        pot_tree.Fill()
        
        # Prepare storage for producers
        self.producer_manager.prepare_storage(output_tree)
        
        # Get number of entries to process
        nentries = dataset.get_num_entries()
        max_events = self.config.get('max_events', nentries)
        if max_events <= 0:
            max_events = nentries
        else:
            max_events = min(max_events, nentries)
        
        # Initialize statistics
        self.stats[dataset_name] = {
            'total': max_events,
            'passed': 0,
            'failed': 0,
            'cut_stats': {},
            'processing_time': 0
        }
        
        # Start timer
        start_time = time.time()
        
        # Show progress every N events
        progress_step = max(1, max_events // 20)
        
        # Event loop with enhanced processing
        self.logger.info(f"Processing {max_events} events with producer-first architecture...")
        for i in range(max_events):
            if i > 0 and i % progress_step == 0:
                progress = (i / max_events) * 100
                elapsed = time.time() - start_time
                estimated_total = elapsed / (i / max_events)
                remaining = estimated_total - elapsed
                self.logger.info(f"Progress: {progress:.1f}% ({i}/{max_events}), Est. time remaining: {remaining:.1f}s")
            
            # Get current entry from dataset
            dataset.set_entry(i)
            data = dataset.get_data()
            ntuple = data['tree']
            
            # ENHANCED PROCESSING: Producer-first architecture
            if self._producer_first:
                passes, producer_results, cut_results = self._process_event_producer_first(
                    ntuple, dataset, i
                )
            else:
                # Fallback to original architecture
                passes, cut_results, cut_data = self.cut_factory.apply_cuts(
                    ntuple, dataset.name, return_on_fail=False, ismc=dataset.ismc
                )
                producer_results = {}
            
            # Update cut statistics
            for cut_name, result in cut_results.items():
                if cut_name not in self.stats[dataset_name]['cut_stats']:
                    self.stats[dataset_name]['cut_stats'][cut_name] = {'pass': 0, 'fail': 0}
                
                if result:
                    self.stats[dataset_name]['cut_stats'][cut_name]['pass'] += 1
                else:
                    self.stats[dataset_name]['cut_stats'][cut_name]['fail'] += 1
            
            # Process event if it passes cuts (or if not filtering)
            if passes or not self._filter_events:
                if passes:
                    self.stats[dataset_name]['passed'] += 1
                else:
                    self.stats[dataset_name]['failed'] += 1
                
                # Fill output tree (producer data already filled by producer manager)
                output_tree.Fill()
            else:
                self.stats[dataset_name]['failed'] += 1
        
        # End timer
        end_time = time.time()
        self.stats[dataset_name]['processing_time'] = end_time - start_time
        
        # Write output trees
        output_file.cd()
        pot_tree.Write()
        output_tree.Write()
        
        # Finalize histogram producers
        for producer_name, producer in self.producer_manager.producers.items():
            if hasattr(producer, 'finalize'):
                producer.finalize()
        
        # Close output file
        output_file.Close()
        
        self.logger.info(f"Dataset {dataset_name} processed in {self.stats[dataset_name]['processing_time']:.1f}s")
        self.logger.info(f"Results written to {output_file_path}")
    
    def _process_event_producer_first(self, ntuple, dataset, event_index):
        """
        Process a single event using producer-first architecture.
        
        Returns:
            passes: Boolean indicating if event passes cuts
            producer_results: Dictionary of producer outputs
            cut_results: Dictionary of cut results
        """
        # Step 1: Run all producers first
        event_data = {"gen2ntuple": ntuple}
        
        # Apply tags if configured
        if hasattr(self, 'tag_factory') and self.tag_factory.tags:
            tags = self.tag_factory.apply_tags(ntuple)
            event_data['event_tags'] = tags
        
        # Process with producers
        producer_results = self.producer_manager.process_event(
            event_data, 
            {"event_index": event_index, 'ismc': dataset.ismc, 'dataset_name':dataset.name}
        )
        
        # Step 2: Run cuts with access to producer results
        cut_params = {
            'ismc': dataset.ismc,
            'producer_data': producer_results,  # KEY ENHANCEMENT: Pass producer data to cuts
            'event_index': event_index
        }
        
        passes, cut_results, cut_data = self.cut_factory.apply_cuts(
            ntuple, dataset.name, return_on_fail=False, 
            ismc=dataset.ismc, producer_outputs=producer_results
        )
        
        return passes, producer_results, cut_results
    
    def _print_statistics(self):
        """Print analysis statistics."""
        self.logger.info("=" * 50)
        self.logger.info("Enhanced Analysis Statistics")
        self.logger.info("=" * 50)
        
        for dataset_name, stats in self.stats.items():
            self.logger.info(f"Dataset: {dataset_name}")
            self.logger.info(f"  Total events: {stats['total']}")
            self.logger.info(f"  Passed events: {stats['passed']} ({stats['passed']/stats['total']*100:.1f}%)")
            self.logger.info(f"  Failed events: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
            self.logger.info(f"  Processing time: {stats['processing_time']:.1f}s")
            
            self.logger.info("  Cut statistics:")
            for cut_name, cut_stats in stats['cut_stats'].items():
                total = cut_stats['pass'] + cut_stats['fail']
                pass_pct = cut_stats['pass'] / total * 100 if total > 0 else 0
                self.logger.info(f"    {cut_name}: {cut_stats['pass']}/{total} ({pass_pct:.1f}%)")
        
        self.logger.info("=" * 50)

def run_lantern_ana():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Lantern Analysis")
    parser.add_argument('config', help='Path to YAML configuration file')
    parser.add_argument('--dataset', action='append', dest='datasets', 
                      help='Process only specified datasets (can be used multiple times)')
    parser.add_argument('--log-level', default='INFO', 
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Set logging level')
    
    args = parser.parse_args()
    
    # Create and run analysis
    analysis = LanternAna(args.config, log_level=args.log_level)
    analysis.run(args.datasets)
    
    # Save statistics
    stats_file = os.path.join(analysis.output_dir, 'statistics.yaml')
    analysis.save_statistics(stats_file)

if __name__=="__main__":
    run_lantern_ana()