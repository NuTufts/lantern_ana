# lantern_ana/cuts/cut_factory.py
"""
Cut Factory with Comprehensive Logging

This module provides a system for applying selection criteria (cuts) to physics events.
Think of cuts like filters - they decide which events to keep for analysis.

What this does:
- Manages a collection of cuts that can be applied to events
- Logs detailed information about what each cut is doing
- Keeps track of how many events pass or fail each cut
- Can combine multiple cuts using logical expressions (AND, OR, etc.)

Key Concepts:
- Cut: A function that looks at an event and returns True (keep) or False (reject)
- Event: A single neutrino interaction recorded by the detector
- Selection: The process of choosing which events to analyze
"""

import os
import sys
import importlib
import glob
import logging
import time
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Dictionary to store all registered cut functions
# This is like a phone book - it maps cut names to the actual cut functions
_REGISTERED_CUTS = {}

def register_cut(func):
    """
    A decorator that registers a cut function so it can be used by the factory.
    
    What this does:
    - Takes a function that implements a cut
    - Adds it to our registry so we can find it later by name
    - Returns the function unchanged
    
    Example:
        @register_cut
        def my_cut(ntuple, params):
            return ntuple.energy > 100  # Keep events with energy > 100 MeV
    """
    if func.__name__ in _REGISTERED_CUTS:
        raise ValueError(f"Cut function '{func.__name__}' is already registered!")

    _REGISTERED_CUTS[func.__name__] = func
    return func

class CutFactory:
    """
    A factory class that manages and applies cuts to physics events with detailed logging.
    
    What this class does:
    - Keeps a list of cuts to apply to each event
    - Runs all the cuts and combines their results
    - Logs detailed information about what's happening
    - Tracks statistics about how often cuts pass/fail
    - Can save performance and efficiency information
    
    Think of this like a quality control system in a factory:
    - Each "cut" is like a quality check
    - Events are like products moving through the factory
    - We keep detailed logs of what passes/fails each check
    - At the end, we have statistics about our quality control process
    """
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        Initialize the cut factory with logging capabilities.
        
        Args:
            log_level: How detailed should the logging be? 
                      "DEBUG" = very detailed, "INFO" = normal, "WARNING" = problems only
            log_file: Optional file to save logs to (in addition to console output)
        """
        # Storage for our cuts and configuration
        self.cuts = []  # List of cuts to apply
        self.cut_logic: Optional[str] = None  # How to combine cut results (e.g., "cut1 and cut2")
        
        # Statistics tracking - these count how often things happen
        self.cut_statistics = defaultdict(lambda: {"pass": 0, "fail": 0, "total_time": 0.0})
        self.total_events_processed = 0
        self.total_events_passed = 0
        
        # Set up logging - this is like keeping a detailed diary of what happens
        self.logger = self._setup_logging(log_level, log_file)
        
        # Automatically find and register all available cuts
        self._discover_cuts()
        
        self.logger.info("LoggedCutFactory initialized successfully")
        self.logger.info(f"Found {len(_REGISTERED_CUTS)} available cuts")
    
    def _setup_logging(self, level_str: str, log_file: Optional[str]) -> logging.Logger:
        """
        Set up the logging system to track what the cut factory is doing.
        
        This creates a logger that will write messages about:
        - Which cuts are being applied
        - How long each cut takes to run
        - How many events pass/fail each cut
        - Any problems that occur
        
        Args:
            level_str: How detailed the logs should be
            log_file: Optional file to save logs to
            
        Returns:
            A logger object that we can use to write log messages
        """
        # Convert string to logging level
        level_map = {
            "DEBUG": logging.DEBUG,    # Very detailed - shows everything
            "INFO": logging.INFO,      # Normal detail - shows important events
            "WARNING": logging.WARNING, # Only problems
            "ERROR": logging.ERROR,    # Only serious problems
            "CRITICAL": logging.CRITICAL # Only catastrophic problems
        }
        level = level_map.get(level_str.upper(), logging.INFO)
        
        # Create a logger with a specific name
        logger = logging.getLogger(f"CutFactory_{id(self)}")
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
    
    def _discover_cuts(self):
        """
        Automatically find and load all available cut functions.
        
        What this does:
        - Looks in the cuts directory for Python files
        - Imports each file, which triggers the @register_cut decorators
        - This populates our registry with all available cuts
        
        Think of this like scanning a library catalog to see what books are available.
        """
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Find all Python files in the directory
        module_files = glob.glob(os.path.join(current_dir, "*.py"))
        
        cuts_found = 0
        for module_path in module_files:
            module_name = os.path.basename(module_path).replace('.py', '')
            
            # Skip special files
            if module_name.startswith('__') or 'factory' in module_name:
                continue
                
            try:
                # Import the module - this triggers @register_cut decorators
                module_path = f"lantern_ana.cuts.{module_name}"
                importlib.import_module(module_path)
                cuts_found += 1
                self.logger.debug(f"Successfully imported cut module: {module_name}")
                
            except ImportError as e:
                self.logger.warning(f"Could not import cut module {module_name}: {e}")
        
        self.logger.info(f"Discovered cuts from {cuts_found} modules")
    
    def list_available_cuts(self) -> List[str]:
        """
        Get a list of all cuts that can be used.
        
        Returns:
            List of cut names (strings) that you can add to the factory
            
        Example:
            cuts = factory.list_available_cuts()
            print(f"Available cuts: {cuts}")
        """
        return list(_REGISTERED_CUTS.keys())
    
    def add_cut(self, name: str, params: Optional[Dict[str, Any]] = None):
        """
        Add a cut to the list of cuts that will be applied to each event.
        
        What this does:
        - Takes the name of a cut and its configuration parameters
        - Adds it to our internal list of cuts to apply
        - Validates that the cut exists and the parameters make sense
        
        Args:
            name: The name of the cut function to use (must be registered)
            params: Dictionary of parameters to control how the cut behaves
        
        Example:
            factory.add_cut('fiducial_cut', {'width': 10.0})
            factory.add_cut('energy_cut', {'min_energy': 50.0})
        """
        # Check if the cut exists
        if name not in _REGISTERED_CUTS:
            available = ", ".join(self.list_available_cuts())
            raise ValueError(f"Cut '{name}' is not registered. Available cuts: {available}")
        
        # Use empty dictionary if no parameters provided
        if params is None:
            params = {}
        
        # Add to our list
        self.cuts.append({
            'name': name,
            'function': _REGISTERED_CUTS[name],
            'params': params
        })
        
        self.logger.info(f"Added cut '{name}' with parameters: {params}")
    
    def set_cut_logic(self, logic_expression: str):
        """
        Set how multiple cuts should be combined using boolean logic.
        
        What this does:
        - Takes a logical expression that describes how to combine cuts
        - Stores it for use when applying cuts to events
        
        Args:
            logic_expression: Boolean expression using cut names
        
        Examples:
            factory.set_cut_logic("cut1 and cut2")  # Both must pass
            factory.set_cut_logic("cut1 or cut2")   # Either can pass
            factory.set_cut_logic("cut1 and (cut2 or cut3)")  # Complex logic
        """
        self.cut_logic = logic_expression
        self.logger.info(f"Set cut logic: {logic_expression}")
        
        # Validate that all cuts in the expression are actually added
        self._validate_cut_logic()
    
    def _validate_cut_logic(self):
        """
        Check that the cut logic expression makes sense.
        
        What this does:
        - Looks at the logical expression
        - Makes sure all cut names mentioned are actually added to the factory
        - Warns if there are cuts added but not used in the logic
        """
        if self.cut_logic is None:
            return
        
        # Find which cuts are mentioned in the logic
        cut_names = [cut['name'] for cut in self.cuts]
        unused_cuts = []
        
        for cut_name in cut_names:
            if cut_name not in self.cut_logic:
                unused_cuts.append(cut_name)
        
        if unused_cuts:
            self.logger.warning(f"Cuts added but not used in logic: {unused_cuts}")
    
    def apply_cuts(self, ntuple: Any, data_name: str, return_on_fail: bool = True, 
                  ismc: bool = False, producer_outputs: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
        """
        Apply all configured cuts to a single event.
        
        What this does:
        - Takes an event (ntuple) and runs all cuts on it
        - Times how long each cut takes
        - Logs detailed information about what happens
        - Returns whether the event passes and detailed results
        
        Args:
            ntuple: The event data to analyze
            data_name: Name of the dataset (for logging)
            return_on_fail: If True, stop at first failed cut (faster)
            ismc: Whether this is Monte Carlo (simulated) data
            producer_outputs: Additional calculated quantities to use
        
        Returns:
            Tuple of:
            - passes: True if event passes all cuts
            - results: Dictionary with each cut's result (True/False)
            - cutdata: Dictionary with additional data from cuts
        """
        start_time = time.time()
        
        # Increment our event counter
        self.total_events_processed += 1
        
        # Storage for results
        results = {}      # True/False for each cut
        cutdata = {}      # Additional data from cuts
        overall_passes = True
        
        self.logger.debug(f"Processing event {self.total_events_processed} from {data_name}")
        
        # Prepare cut logic expression if we have one
        cut_expression = self.cut_logic
        
        # Apply each cut one by one
        for cut_info in self.cuts:
            cut_name = cut_info['name']
            cut_function = cut_info['function']
            cut_params = cut_info['params'].copy()  # Copy to avoid modifying original
            
            # Add standard parameters that all cuts might need
            cut_params['ismc'] = ismc
            cut_params['data_name'] = data_name
            
            # Add producer outputs if available
            if producer_outputs is not None:
                cut_params['producer_outputs'] = producer_outputs
            
            # Time how long this cut takes
            cut_start_time = time.time()
            
            try:
                # Actually run the cut
                self.logger.debug(f"Applying cut '{cut_name}'")
                cut_result = cut_function(ntuple, cut_params)
                
                # Handle different types of results
                if isinstance(cut_result, bool):
                    # Simple True/False result
                    results[cut_name] = cut_result
                    cutdata[f'cutdata_{cut_name}'] = {}
                    
                elif isinstance(cut_result, tuple) and len(cut_result) == 2:
                    # Cut returned (True/False, additional_data)
                    if not isinstance(cut_result[0], bool):
                        raise ValueError(f"Cut '{cut_name}': First return value must be boolean")
                    if not isinstance(cut_result[1], dict):
                        raise ValueError(f"Cut '{cut_name}': Second return value must be dictionary")
                    
                    results[cut_name] = cut_result[0]
                    cutdata[f'cutdata_{cut_name}'] = cut_result[1]
                    
                else:
                    raise ValueError(f"Cut '{cut_name}': Must return bool or (bool, dict)")
                
                # Record timing and statistics
                cut_time = time.time() - cut_start_time
                self.cut_statistics[cut_name]["total_time"] += cut_time
                
                if results[cut_name]:
                    self.cut_statistics[cut_name]["pass"] += 1
                    self.logger.debug(f"Cut '{cut_name}' PASSED (took {cut_time:.4f}s)")
                else:
                    self.cut_statistics[cut_name]["fail"] += 1
                    self.logger.debug(f"Cut '{cut_name}' FAILED (took {cut_time:.4f}s)")
                
                # Handle cut logic
                if cut_expression is None:
                    # No logic expression - use simple AND of all cuts
                    if not results[cut_name]:
                        overall_passes = False
                        if return_on_fail:
                            self.logger.debug(f"Stopping early after cut '{cut_name}' failed")
                            break
                else:
                    # Replace cut name in expression with result
                    placeholder = f"{{{cut_name}}}"
                    cut_expression = cut_expression.replace(placeholder, str(results[cut_name]))
                
            except Exception as e:
                # Something went wrong with this cut
                self.logger.error(f"Error in cut '{cut_name}': {e}")
                results[cut_name] = False
                cutdata[f'cutdata_{cut_name}'] = {}
                overall_passes = False
                
                if return_on_fail:
                    break
        
        # Evaluate final cut expression if we have complex logic
        if cut_expression is not None and self.cut_logic is not None:
            try:
                overall_passes = eval(cut_expression)
                self.logger.debug(f"Cut logic '{self.cut_logic}' evaluated to: {overall_passes}")
            except Exception as e:
                self.logger.error(f"Error evaluating cut logic '{self.cut_logic}': {e}")
                overall_passes = False
        
        # Update overall statistics
        if overall_passes:
            self.total_events_passed += 1
        
        # Log summary for this event
        total_time = time.time() - start_time
        self.logger.debug(f"Event {self.total_events_processed}: {'PASSED' if overall_passes else 'FAILED'} "
                         f"(total time: {total_time:.4f}s)")
        
        return overall_passes, results, cutdata
    
    def print_statistics(self):
        """
        Print a detailed summary of cut performance and efficiency.
        
        What this shows:
        - How many events were processed total
        - For each cut: pass rate, fail rate, average time per event
        - Overall efficiency of the selection
        """
        print("\n" + "="*60)
        print("CUT FACTORY STATISTICS")
        print("="*60)
        
        print(f"Total events processed: {self.total_events_processed}")
        print(f"Total events passed: {self.total_events_passed}")
        
        if self.total_events_processed > 0:
            overall_efficiency = (self.total_events_passed / self.total_events_processed) * 100
            print(f"Overall efficiency: {overall_efficiency:.2f}%")
        
        print(f"\nCut logic: {self.cut_logic or 'Simple AND of all cuts'}")
        
        print(f"\nIndividual cut statistics:")
        print(f"{'Cut Name':<25} {'Pass':<8} {'Fail':<8} {'Efficiency':<12} {'Avg Time':<10}")
        print("-" * 65)
        
        for cut_name in [cut['name'] for cut in self.cuts]:
            stats = self.cut_statistics[cut_name]
            total = stats["pass"] + stats["fail"]
            
            if total > 0:
                efficiency = (stats["pass"] / total) * 100
                avg_time = stats["total_time"] / total
                print(f"{cut_name:<25} {stats['pass']:<8} {stats['fail']:<8} "
                      f"{efficiency:<11.2f}% {avg_time:<9.4f}s")
            else:
                print(f"{cut_name:<25} {'N/A':<8} {'N/A':<8} {'N/A':<12} {'N/A':<10}")
        
        print("="*60)
    
    def save_statistics(self, filename: str):
        """
        Save detailed statistics to a file for later analysis.
        
        What this does:
        - Creates a file with all the cut performance data
        - Includes timestamps, efficiency numbers, timing data
        - Can be used to track performance over time or compare different configurations
        
        Args:
            filename: Path where to save the statistics file
        """
        import json
        
        # Prepare data to save
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'total_events_processed': self.total_events_processed,
            'total_events_passed': self.total_events_passed,
            'overall_efficiency': (self.total_events_passed / max(1, self.total_events_processed)) * 100,
            'cut_logic': self.cut_logic,
            'cut_statistics': dict(self.cut_statistics),
            'cuts_configured': [
                {
                    'name': cut['name'],
                    'parameters': cut['params']
                }
                for cut in self.cuts
            ]
        }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(stats_data, f, indent=2)
        
        self.logger.info(f"Statistics saved to: {filename}")
    
    def reset_statistics(self):
        """
        Clear all statistics and start counting from zero.
        
        Useful when you want to measure performance of a specific part of your analysis.
        """
        self.cut_statistics.clear()
        self.total_events_processed = 0
        self.total_events_passed = 0
        self.logger.info("Statistics reset to zero")
    
    def get_efficiency_report(self) -> Dict[str, float]:
        """
        Get a simple efficiency report for all cuts.
        
        Returns:
            Dictionary mapping cut names to their efficiency percentages
            
        Example:
            efficiencies = factory.get_efficiency_report()
            print(f"Fiducial cut efficiency: {efficiencies['fiducial_cut']:.1f}%")
        """
        report = {}
        
        for cut_name in [cut['name'] for cut in self.cuts]:
            stats = self.cut_statistics[cut_name]
            total = stats["pass"] + stats["fail"]
            
            if total > 0:
                efficiency = (stats["pass"] / total) * 100
                report[cut_name] = efficiency
            else:
                report[cut_name] = 0.0
        
        return report
    
    @staticmethod
    def auto_discover_cuts():
        """
        Static method to discover cuts (for compatibility with main analysis class).
        
        This method imports all cut modules which triggers the @register_cut decorators
        to populate the global _REGISTERED_CUTS registry.
        """
        import lantern_ana
        import os
        import glob
        import importlib
        
        # Get the cuts directory
        cuts_dir = os.path.join(os.path.dirname(lantern_ana.__file__), 'cuts')
        
        # Find all Python files in the cuts directory
        module_files = glob.glob(os.path.join(cuts_dir, "*.py"))
        
        cuts_found = 0
        for module_path in module_files:
            module_name = os.path.basename(module_path).replace('.py', '')
            
            # Skip special files
            if module_name.startswith('__') or 'factory' in module_name:
                continue
                
            try:
                # Import the module - this triggers @register_cut decorators
                module_path = f"lantern_ana.cuts.{module_name}"
                importlib.import_module(module_path)
                cuts_found += 1
                
            except ImportError as e:
                # Silently continue if module can't be imported
                pass
    
    @staticmethod
    def list_available_cuts():
        """
        Static method to list available cuts.
        
        Returns:
            List of available cut names
        """
        return list(_REGISTERED_CUTS.keys())