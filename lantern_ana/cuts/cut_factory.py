import os
import sys
import importlib
import inspect
import glob
from functools import wraps

# Dictionary to store all registered cut functions
_REGISTERED_CUTS = {}

def register_cut(func):
    """
    Decorator to register a cut function with the CutFactory.
    The function name is used as the cut identifier.
    """
    if func.__name__ in _REGISTERED_CUTS:
        raise ValueError("Registering a cut function with a name already registered: ",func.__name__)

    _REGISTERED_CUTS[func.__name__] = func
    return func

class CutFactory:
    """
    Factory class to manage and apply cut functions to events.
    """
    def __init__(self):
        self.cuts = []
        self.auto_discover_cuts()
        
    def auto_discover_cuts(self):
        """
        Automatically discover and import all cut modules in the cuts directory.
        This allows for automatic registration of decorated cut functions.
        """
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Find all Python files in the directory (excluding __init__.py and this file)
        module_files = glob.glob(os.path.join(current_dir, "*.py"))
        for module_path in module_files:
            module_name = os.path.basename(module_path).replace('.py', '')
            if module_name in ['__init__', 'cut_factory']:
                continue
                
            # Import the module to trigger the decorators
            try:
                # Convert file path to module path
                module_path = f"lantern_ana.cuts.{module_name}"
                importlib.import_module(module_path)
            except ImportError as e:
                print(f"Warning: Could not import cut module {module_name}: {e}")
    
    def list_available_cuts(self):
        """
        Return a list of all registered cut names.
        """
        return list(_REGISTERED_CUTS.keys())
        
    def add_cut(self, name, params=None):
        """
        Add a cut to the list to be applied per event.
        Store params to be passed to the cut function when run.
        
        Parameters:
        - name: Name of the registered cut function to use
        - params: Dictionary with parameters to control the cut behavior
        """
        if name not in _REGISTERED_CUTS:
            available_cuts = ", ".join(self.list_available_cuts())
            raise ValueError(f"Cut '{name}' is not registered. Available cuts: {available_cuts}")
            
        if params is None:
            params = {}
            
        self.cuts.append({
            'name': name,
            'function': _REGISTERED_CUTS[name],
            'params': params
        })
        
    def apply_cuts(self, ntuple, return_on_fail=True):
        """
        Apply all registered cuts in order.
        
        Parameters:
        - ntuple: The ntuple tree to run the cuts on
        - return_on_fail: If True, return immediately when a cut fails
        
        Returns:
        - passes: Boolean indicating if all cuts passed
        - results: Dictionary with cut names as keys and results as values
        """
        results = {}
        passes = True
        
        for cut in self.cuts:
            name = cut['name']
            func = cut['function']
            params = cut['params']
            
            # Apply the cut
            cut_result = func(ntuple, params)
            results[name] = cut_result
            
            # Check if we should continue
            if not cut_result and return_on_fail:
                passes = False
                break
                
            if not cut_result:
                passes = False
        
        return passes, results