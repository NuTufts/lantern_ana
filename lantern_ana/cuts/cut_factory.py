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
        self.cut_logic = None
        
    @classmethod
    def auto_discover_cuts(cls):
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
    
    @classmethod
    def list_available_cuts(cls):
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

    def set_cut_logic(self,logic_expression : str) -> None:
        assert(type(logic_expression) is str)
        self.cut_logic = logic_expression
        
    def apply_cuts(self, ntuple, return_on_fail=True, ismc=False):
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
        cutdata = {}
        passes = True

        self.check_logic_expression()

        cut_expression = ""
        if self.cut_logic is not None:
            cut_expression += self.cut_logic

        for cut in self.cuts:
            name = cut['name']
            func = cut['function']
            params = cut['params']
            params['ismc'] = ismc
            
            # Apply the cut
            cut_result = func(ntuple, params)
            if type(cut_result) is bool:
                results[name] = cut_result
                cutdata[f'cutdata_{name}'] = {}
            elif type(cut_result) is tuple:
                if len(cut_result)==2:
                    if type(cut_result[0]) is bool:
                        results[name] = cut_result[0]
                    else:
                        raise ValueError('if cut function returns tuple, first entry must be bool.')
                    if type(cut_result[1]) is not dict:
                        raise ValueError('if cut function returns data (as second return item), must be in form of dictionary.')
                    else:
                        cutdata[f'cutdata_{name}'] = cut_result[1]
                else:
                    raise ValueError('cut function must return at most 2 outputs.')
            
            # Check if we should continue
            if self.cut_logic is None:
                # no logic expression provided, so we assume ALL cuts are combined by AND
                if not cut_result:
                    passes = False
                if not passes and return_on_fail:
                    break
            else:
                try:
                    cut_expression = cut_expression.replace("{%s}"%(name),str(cut_result))
                except e:
                    raise RuntimeError(f'Could not replace result of cutname={name} in the cut expression:\n{e.what()}')
        
        if self.cut_logic is None:
            return passes, results, cutdata

        # eval expression
        passes = eval(cut_expression)
        #print(cut_expression," --> ",passes)

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
        if len(missing)>0:
            print("Cut logic expression does not use certain cuts: ")
            for cutname in missing:
                print("  ",cutname)
            raise ValueError("Missing Cut Error")
