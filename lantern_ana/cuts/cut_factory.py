# lantern_ana/cuts/cut_factory.py
import os
import sys
import importlib
import inspect
import glob
from functools import wraps
from typing import Dict, Type, List, Any, Optional

from .cutBaseClass import CutBaseClass

# Dictionary to store all registered cut classes
_REGISTERED_CUTS: Dict[str, Type[CutBaseClass]] = {}

def register_cut(cls: Type[CutBaseClass]) -> Type[CutBaseClass]:
    """
    Decorator to register a cut class with the CutFactory.
    The class name is used as the cut identifier.
    """
    if not issubclass(cls, CutBaseClass):
        raise ValueError(f"Cut class {cls.__name__} must inherit from CutBaseClass")
    
    if cls.__name__ in _REGISTERED_CUTS:
        raise ValueError(f"Registering a cut class with a name already registered: {cls.__name__}")

    _REGISTERED_CUTS[cls.__name__] = cls
    return cls

class CutFactory:
    """
    Factory class to manage and apply cut classes to events.
    """
    def __init__(self):
        self.cuts: List[Dict[str, Any]] = []
        self.auto_discover_cuts()
        self.cut_logic: Optional[str] = None
        
    @classmethod
    def auto_discover_cuts(cls):
        """
        Automatically discover and import all cut modules in the cuts directory.
        This allows for automatic registration of decorated cut classes.
        """
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Find all Python files in the directory (excluding __init__.py and this file)
        module_files = glob.glob(os.path.join(current_dir, "*.py"))
        for module_path in module_files:
            module_name = os.path.basename(module_path).replace('.py', '')
            if module_name in ['__init__', 'cut_factory', 'cut_factory_new', 'cutBaseClass']:
                continue
                
            # Import the module to trigger the decorators
            try:
                # Convert file path to module path
                module_path = f"lantern_ana.cuts.{module_name}"
                importlib.import_module(module_path)
            except ImportError as e:
                print(f"Warning: Could not import cut module {module_name}: {e}")
    
    @classmethod
    def list_available_cuts(cls) -> List[str]:
        """
        Return a list of all registered cut names.
        """
        return list(_REGISTERED_CUTS.keys())
        
    def add_cut(self, name: str, cut_name: str, params: Optional[Dict[str, Any]] = None):
        """
        Add a cut to the list to be applied per event.
        
        Parameters:
        - name: Instance name for this cut (for reference in cut logic)
        - cut_name: Name of the registered cut class to use
        - params: Dictionary with parameters to control the cut behavior
        """
        if cut_name not in _REGISTERED_CUTS:
            available_cuts = ", ".join(self.list_available_cuts())
            raise ValueError(f"Cut '{cut_name}' is not registered. Available cuts: {available_cuts}")
            
        if params is None:
            params = {}
        
        # Create cut instance
        cut_class = _REGISTERED_CUTS[cut_name]
        cut_instance = cut_class(name, params)
        
        # Validate configuration
        if not cut_instance.validate_config():
            raise ValueError(f"Invalid configuration for cut '{cut_name}' with name '{name}'")
            
        self.cuts.append({
            'name': name,
            'cut_name': cut_name,
            'instance': cut_instance,
            'params': params
        })

    def set_cut_logic(self, logic_expression: str) -> None:
        """
        Set the logical expression for combining cuts.
        
        Args:
            logic_expression: Boolean expression using cut names
        """
        assert isinstance(logic_expression, str)
        self.cut_logic = logic_expression
        
    def apply_cuts(self, ntuple: Any, data_name: str, return_on_fail: bool = True, ismc: bool = False) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
        """
        Apply all registered cuts in order.
        
        Parameters:
        - ntuple: The ntuple tree to run the cuts on
        - data_name: name for the ntuple data given, can be used to modify cut behavior
        - return_on_fail: If True, return immediately when a cut fails
        - ismc: Whether this is Monte Carlo data
        
        Returns:
        - passes: Boolean indicating if all cuts passed
        - results: Dictionary with cut names as keys and results as values
        - cutdata: Dictionary with cut data from evaluations
        """
        results = {}
        cutdata = {}
        passes = True

        self.check_logic_expression()

        cut_expression = ""
        if self.cut_logic is not None:
            cut_expression += self.cut_logic

        for cut in self.cuts:
            name = cut['name']
            instance = cut['instance']
            params = cut['params'].copy()  # Copy to avoid modifying original
            params['ismc'] = ismc
            params['data_name'] = data_name
            
            # Apply the cut
            cut_result = instance.evaluate(ntuple, params)
            
            if isinstance(cut_result, bool):
                results[name] = cut_result
                cutdata[f'cutdata_{name}'] = {}
            elif isinstance(cut_result, tuple) and len(cut_result) == 2:
                if not isinstance(cut_result[0], bool):
                    raise ValueError('If cut returns tuple, first entry must be bool.')
                if not isinstance(cut_result[1], dict):
                    raise ValueError('If cut returns data (as second return item), must be in form of dictionary.')
                
                results[name] = cut_result[0]
                cutdata[f'cutdata_{name}'] = cut_result[1]
            else:
                raise ValueError('Cut must return either bool or tuple of (bool, dict).')
            
            # Check if we should continue
            if self.cut_logic is None:
                # no logic expression provided, so we assume ALL cuts are combined by AND
                if not cut_result[0] if isinstance(cut_result, tuple) else not cut_result:
                    passes = False
                if not passes and return_on_fail:
                    break
            else:
                try:
                    result_bool = cut_result[0] if isinstance(cut_result, tuple) else cut_result
                    cut_expression = cut_expression.replace("{%s}" % name, str(result_bool))
                except Exception as e:
                    raise RuntimeError(f'Could not replace result of cutname={name} in the cut expression:\n{str(e)}')
        
        if self.cut_logic is None:
            return passes, results, cutdata

        # eval expression
        passes = eval(cut_expression)

        return passes, results, cutdata

    def check_logic_expression(self):
        """
        If a cut logic expression has been provided, we check that we can find the names of 
        all the cuts in it.
        """
        if self.cut_logic is None:
            return True
        missing = []
        for cut in self.cuts:
            if cut['name'] not in self.cut_logic:
                missing.append(cut['name'])
        if len(missing) > 0:
            print("Cut logic expression does not use certain cuts: ")
            for cutname in missing:
                print("  ", cutname)
            raise ValueError("Missing Cut Error")

    def get_cut_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all registered cuts.
        
        Returns:
            Dictionary mapping cut names to descriptions
        """
        descriptions = {}
        for cut in self.cuts:
            descriptions[cut['name']] = cut['instance'].get_description()
        return descriptions

    def get_required_branches(self) -> List[str]:
        """
        Get all required branches for the current cuts.
        
        Returns:
            List of all required branch names
        """
        all_branches = []
        for cut in self.cuts:
            branches = cut['instance'].get_required_branches()
            all_branches.extend(branches)
        return list(set(all_branches))  # Remove duplicates