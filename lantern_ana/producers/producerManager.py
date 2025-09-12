# lantern_ana/producers/producer_manager.py
"""
Producer Manager with Comprehensive Logging

This module manages the calculation of derived quantities from physics event data.
Think of producers like specialized calculators that each compute specific measurements.

What this does:
- Manages a collection of producers that calculate different quantities
- Runs them in the correct order (some calculations depend on others)
- Logs detailed information about performance and timing
- Handles dependencies between producers automatically
- Stores all calculated values to output files

Key Concepts:
- Producer: A class that calculates some quantity (e.g., visible energy, particle angles)
- Event: A single neutrino interaction with measured data
- Dependencies: Some calculations need results from other calculations first
- Execution Order: The sequence in which producers must run to satisfy dependencies
"""

import yaml
import networkx as nx
import logging
import time
import json
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from datetime import datetime
import sys
import traceback

from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import ProducerFactory

class ProducerManager:
    """
    A manager class that coordinates multiple producers with detailed logging and monitoring.
    
    What this class does:
    - Keeps track of all the producers (calculators) we want to use
    - Figures out what order to run them in (dependency resolution)
    - Runs each producer and times how long it takes
    - Logs detailed information about what's happening
    - Tracks performance statistics over many events
    - Handles errors gracefully and reports them
    
    Think of this like a project manager coordinating a team:
    - Each producer is like a team member with a specific job
    - Some jobs depend on others being finished first
    - The manager schedules the work in the right order
    - They keep detailed records of progress and performance
    """
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        Initialize the producer manager with logging capabilities.
        
        Args:
            log_level: How detailed should logging be?
                      "DEBUG" = very detailed, "INFO" = normal, "WARNING" = problems only
            log_file: Optional file to save logs to (in addition to console)
        """
        # Core storage
        self.producers: Dict[str, ProducerBaseClass] = {}  # name -> producer object
        self.execution_order: List[str] = []  # order to run producers in
        self.last_outputs: Dict[str, Any] = {}  # cached results from last event
        
        # Performance tracking
        self.producer_statistics = defaultdict(lambda: {
            "total_time": 0.0,
            "num_calls": 0,
            "num_errors": 0,
            "average_time": 0.0
        })
        self.total_events_processed = 0
        self.dependency_graph: Optional[nx.DiGraph] = None
        
        # Set up logging
        self.logger = self._setup_logging(log_level, log_file)
        
        self.logger.info("LoggedProducerManager initialized successfully")
    
    def _setup_logging(self, level_str: str, log_file: Optional[str]) -> logging.Logger:
        """
        Set up the logging system to track what the producer manager is doing.
        
        This creates a logger that will write messages about:
        - Which producers are being run and in what order
        - How long each producer takes to calculate its results
        - Any errors or problems that occur
        - Performance statistics over time
        
        Args:
            level_str: How detailed the logs should be
            log_file: Optional file to save logs to
            
        Returns:
            A logger object for writing log messages
        """
        # Convert string to logging level
        level_map = {
            "DEBUG": logging.DEBUG,    # Very detailed - shows every calculation
            "INFO": logging.INFO,      # Normal detail - shows important events
            "WARNING": logging.WARNING, # Only problems
            "ERROR": logging.ERROR,    # Only serious problems
            "CRITICAL": logging.CRITICAL # Only catastrophic problems
        }
        level = level_map.get(level_str.upper(), logging.INFO)
        
        # Create a logger with a unique name
        logger = logging.getLogger(f"ProducerManager_{id(self)}")
        logger.setLevel(level)
        
        # Prevent inheritance from root logger to avoid duplicate messages
        logger.propagate = False
        
        # Don't add handlers if they already exist (prevents duplicates)
        if logger.handlers:
            return logger
        
        # Create formatter - this determines how log messages look
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add console handler - prints to terminal
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Add file handler if requested - saves to file
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info(f"Logging to file: {log_file}")
        
        return logger
    
    def load_configuration(self, config_file: str) -> None:
        """
        Load producer configuration from a YAML file.
        
        What this does:
        - Reads a configuration file that describes which producers to use
        - Creates each producer with its specific settings
        - Figures out the correct order to run them in
        
        Args:
            config_file: Path to the YAML configuration file
            
        Example YAML structure:
            producers:
              visible_energy:
                type: VisibleEnergyProducer
                config:
                  include_tracks: true
              muon_angle:
                type: MuonPropertiesProducer
                config:
                  min_energy: 50.0
        """
        self.logger.info(f"Loading configuration from: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {config_file}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML file: {e}")
            raise
        
        # Create producers from configuration
        producers_config = config.get('producers', {})
        self.logger.info(f"Found {len(producers_config)} producers in configuration")
        
        for producer_name, producer_config in producers_config.items():
            try:
                self._create_producer_from_config(producer_name, producer_config)
            except Exception as e:
                self.logger.error(f"Failed to create producer '{producer_name}': {e}")
                raise
        
        # Determine execution order based on dependencies
        self._determine_execution_order()
        
        self.logger.info(f"Configuration loaded successfully. "
                        f"Execution order: {' -> '.join(self.execution_order)}")
    
    def _create_producer_from_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Create a single producer from configuration data.
        
        Args:
            name: Name to give this producer instance
            config: Configuration dictionary with 'type' and 'config' keys
        """
        producer_type = config.get('type')
        if not producer_type:
            raise ValueError(f"Producer '{name}' missing required 'type' field")
        
        # Create producer instance
        producer_config = config.get('config', {})
        producer = ProducerFactory.create(producer_type, name, producer_config)
        
        self.producers[name] = producer
        self.logger.debug(f"Created producer '{name}' of type '{producer_type}'")
    
    def add_producer(self, name: str, producer_type: str, config: Dict[str, Any]) -> None:
        """
        Add a producer programmatically (without a config file).
        
        What this does:
        - Creates a new producer with the given type and configuration
        - Adds it to our collection of producers
        - Recalculates the execution order to account for dependencies
        
        Args:
            name: Name for this producer instance
            producer_type: Type of producer to create (must be registered)
            config: Configuration parameters for the producer
            
        Example:
            manager.add_producer('energy_calc', 'VisibleEnergyProducer', {})
        """
        self.logger.info(f"Adding producer '{name}' of type '{producer_type}'")
        
        try:
            producer = ProducerFactory.create(producer_type, name, config)
            self.producers[name] = producer
            
            # Recalculate execution order
            self._determine_execution_order()
            
            self.logger.info(f"Producer '{name}' added successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to add producer '{name}': {e}")
            raise
    
    def _determine_execution_order(self) -> None:
        """
        Figure out what order to run producers in based on their dependencies.
        
        What this does:
        - Looks at what inputs each producer needs
        - Creates a dependency graph showing which producers depend on others
        - Uses graph algorithms to find a valid execution order
        - Detects circular dependencies (impossible situations)
        
        Think of this like planning a cooking recipe:
        - Some steps must happen before others (you can't bake before mixing)
        - This figures out the correct sequence automatically
        """
        self.logger.debug("Determining producer execution order...")
        
        # Create directed graph for dependency resolution
        graph = nx.DiGraph()
        
        # Add all producers as nodes
        for name in self.producers:
            graph.add_node(name)
        
        # Add edges based on required inputs
        for name, producer in self.producers.items():
            required_inputs = producer.requiredInputs()
            self.logger.debug(f"Producer '{name}' requires: {required_inputs}")
            
            for required in required_inputs:
                if required in self.producers:
                    # This creates an edge: required -> name
                    # Meaning 'required' must run before 'name'
                    graph.add_edge(required, name)
                    self.logger.debug(f"Dependency: '{required}' must run before '{name}'")
        
        # Store the graph for later use
        self.dependency_graph = graph
        
        # Check for cycles (circular dependencies)
        if not nx.is_directed_acyclic_graph(graph):
            self.logger.error("Circular dependency detected in producer configuration!")
            self._log_dependency_graph()
            raise ValueError("Circular dependency detected - cannot determine execution order")
        
        # Get topological sort (execution order)
        # This gives us an order where all dependencies are satisfied
        self.execution_order = list(nx.topological_sort(graph))
        
        self.logger.info(f"Execution order determined: {' -> '.join(self.execution_order)}")
        self._log_dependency_summary()
    
    def _log_dependency_summary(self) -> None:
        """
        Log a summary of the dependency relationships between producers.
        """
        self.logger.debug("Producer dependency summary:")
        
        for name in self.execution_order:
            producer = self.producers[name]
            dependencies = [dep for dep in producer.requiredInputs() if dep in self.producers]
            
            if dependencies:
                self.logger.debug(f"  {name} depends on: {', '.join(dependencies)}")
            else:
                self.logger.debug(f"  {name} has no dependencies (can run first)")
    
    def prepare_storage(self, output_interface: Any) -> None:
        """
        Set up storage for all producer outputs in the output file.
        
        What this does:
        - Tells each producer to create branches in the output ROOT tree
        - This is where calculated values will be saved for each event
        - Must be called before processing any events
        
        Args:
            output_interface: The output ROOT TTree where results will be stored
        """
        self.logger.info("Preparing storage for producer outputs...")
        
        for name in self.execution_order:
            try:
                producer = self.producers[name]
                producer.prepareStorage(output_interface)
                self.logger.debug(f"Storage prepared for producer '{name}'")
                
            except Exception as e:
                self.logger.error(f"Failed to prepare storage for producer '{name}': {e}")
                raise
        
        self.logger.info(f"Storage prepared for {len(self.execution_order)} producers")
    
    def process_event(self, event_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single event through all producers in the correct order.
        
        What this does:
        - Takes event data and runs each producer on it
        - Times how long each producer takes
        - Passes outputs from early producers to later ones
        - Logs detailed information about the process
        - Handles errors gracefully
        
        Args:
            event_data: Initial data for the event (usually includes the ROOT tree)
            params: Additional parameters (like event index, MC flag, etc.)
            
        Returns:
            Dictionary with all producer outputs for this event
        """
        event_start_time = time.time()
        self.total_events_processed += 1
        
        self.logger.debug(f"Processing event {self.total_events_processed}")
        
        # Start with the input data
        results = {}
        results.update(event_data)
        
        # Process each producer in dependency order
        for name in self.execution_order:
            producer = self.producers[name]
            
            try:
                # Time this producer
                producer_start_time = time.time()
                
                self.logger.debug(f"Running producer '{name}'")
                
                # Actually run the producer
                result = producer.processEvent(results, params)
                
                # Record the result
                results[name] = result
                
                # Update timing statistics
                producer_time = time.time() - producer_start_time
                stats = self.producer_statistics[name]
                stats["total_time"] += producer_time
                stats["num_calls"] += 1
                stats["average_time"] = stats["total_time"] / stats["num_calls"]
                
                self.logger.debug(f"Producer '{name}' completed in {producer_time:.4f}s")
                
            except Exception as e:
                # Handle producer errors
                self.logger.error(f"Error in producer '{name}': {e}\n"+str(traceback.format_exc()))
                
                # Record the error in statistics
                self.producer_statistics[name]["num_errors"] += 1
                
                # Set default values for this producer
                try:
                    producer.setDefaultValues()
                    results[name] = {}
                except Exception as e2:
                    self.logger.error(f"Failed to set default values for '{name}': {e2}")
                    results[name] = {}

                # stop on Error
                sys.exit(1)
        
        # Cache the producer outputs
        self.last_outputs = {name: results[name] for name in self.execution_order}
        
        # Log event summary
        total_event_time = time.time() - event_start_time
        self.logger.debug(f"Event {self.total_events_processed} completed in {total_event_time:.4f}s")
        
        return results
    
    def get_producer_outputs(self) -> Dict[str, Any]:
        """
        Get the outputs from the last processed event.
        
        What this does:
        - Returns a copy of all producer outputs from the most recent event
        - Useful for cuts that need to use calculated quantities
        
        Returns:
            Dictionary mapping producer names to their outputs
        """
        return self.last_outputs.copy()
    
    def set_default_values(self):
        """
        Set all producer variables to their default values.
        
        What this does:
        - Calls each producer's setDefaultValues() method
        - This is typically done before processing an event
        - Ensures clean state if an event fails or has missing data
        """
        self.logger.debug("Setting default values for all producers")
        
        for name in self.execution_order:
            try:
                producer = self.producers[name]
                producer.setDefaultValues()
            except Exception as e:
                self.logger.warning(f"Failed to set default values for '{name}': {e}")
        
        # Clear cached outputs
        self.last_outputs = {}
    
    def get_available_producers(self) -> List[str]:
        """
        Get a list of all configured producer names.
        
        Returns:
            List of producer names that are available
        """
        return list(self.producers.keys())
    
    def has_producer(self, name: str) -> bool:
        """
        Check if a producer with the given name is configured.
        
        Args:
            name: Producer name to check
            
        Returns:
            True if the producer exists
        """
        return name in self.producers
    
    def validate_cut_dependencies(self, required_producers: List[str]) -> bool:
        """
        Check that all producers required by cuts are actually configured.
        
        What this does:
        - Takes a list of producer names that cuts need
        - Checks that we actually have all of them configured
        - Raises an error if any are missing
        
        Args:
            required_producers: List of producer names needed by cuts
            
        Returns:
            True if all dependencies are satisfied
            
        Raises:
            ValueError: If required producers are missing
        """
        available = set(self.producers.keys())
        required = set(required_producers)
        
        missing = required - available
        if missing:
            error_msg = (f"Cuts require producers that are not configured: {missing}. "
                        f"Available producers: {available}")
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info("All cut dependencies satisfied")
        return True
    
    def print_statistics(self):
        """
        Print a detailed performance report for all producers.
        
        What this shows:
        - How many events were processed
        - For each producer: number of calls, total time, average time, error count
        - Overall performance summary
        """
        print("\n" + "="*70)
        print("PRODUCER MANAGER STATISTICS")
        print("="*70)
        
        print(f"Total events processed: {self.total_events_processed}")
        print(f"Number of producers: {len(self.producers)}")
        print(f"Execution order: {' -> '.join(self.execution_order)}")
        
        print(f"\nProducer performance:")
        print(f"{'Producer':<20} {'Calls':<8} {'Errors':<8} {'Total Time':<12} {'Avg Time':<12}")
        print("-" * 70)
        
        total_time = 0.0
        for name in self.execution_order:
            stats = self.producer_statistics[name]
            total_time += stats["total_time"]
            
            print(f"{name:<20} {stats['num_calls']:<8} {stats['num_errors']:<8} "
                  f"{stats['total_time']:<11.4f}s {stats['average_time']:<11.4f}s")
        
        if self.total_events_processed > 0:
            avg_time_per_event = total_time / self.total_events_processed
            print(f"\nTotal processing time: {total_time:.4f}s")
            print(f"Average time per event: {avg_time_per_event:.4f}s")
        
        print("="*70)
    
    def save_statistics(self, filename: str):
        """
        Save detailed performance statistics to a file.
        
        What this does:
        - Creates a file with all producer performance data
        - Includes timing, error counts, dependency information
        - Can be used to analyze performance over time
        
        Args:
            filename: Path where to save the statistics file
        """
        # Prepare data to save
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'total_events_processed': self.total_events_processed,
            'execution_order': self.execution_order,
            'producer_statistics': dict(self.producer_statistics),
            'producers_configured': [
                {
                    'name': name,
                    'type': type(producer).__name__,
                    'dependencies': producer.requiredInputs()
                }
                for name, producer in self.producers.items()
            ]
        }
        
        # Add dependency graph information if available
        if self.dependency_graph:
            stats_data['dependency_edges'] = list(self.dependency_graph.edges())
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(stats_data, f, indent=2)
        
        self.logger.info(f"Statistics saved to: {filename}")
    
    def reset_statistics(self):
        """
        Clear all performance statistics and start counting from zero.
        
        Useful for measuring performance of specific analysis phases.
        """
        self.producer_statistics.clear()
        self.total_events_processed = 0
        self.logger.info("Producer statistics reset to zero")
    
    def _log_dependency_graph(self):
        """
        Log the complete dependency graph for debugging purposes.
        """
        if not self.dependency_graph:
            return
            
        self.logger.debug("Producer dependency graph:")
        
        # Log all edges (dependencies)
        for source, target in self.dependency_graph.edges():
            self.logger.debug(f"  {source} -> {target}")
        
        # Log any cycles if they exist
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            if cycles:
                self.logger.error("Circular dependencies found:")
                for cycle in cycles:
                    self.logger.error(f"  Cycle: {' -> '.join(cycle)} -> {cycle[0]}")
        except Exception:
            pass  # Graph algorithms might fail on complex graphs
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of producer performance metrics.
        
        Returns:
            Dictionary with performance data for programmatic analysis
        """
        summary = {
            'total_events': self.total_events_processed,
            'total_producers': len(self.producers),
            'execution_order': self.execution_order.copy(),
            'producer_metrics': {}
        }
        
        total_time = 0.0
        for name in self.execution_order:
            stats = self.producer_statistics[name]
            total_time += stats["total_time"]
            
            summary['producer_metrics'][name] = {
                'calls': stats['num_calls'],
                'errors': stats['num_errors'],
                'total_time': stats['total_time'],
                'average_time': stats['average_time'],
                'error_rate': stats['num_errors'] / max(1, stats['num_calls'])
            }
        
        summary['total_processing_time'] = total_time
        if self.total_events_processed > 0:
            summary['average_time_per_event'] = total_time / self.total_events_processed
        
        return summary
