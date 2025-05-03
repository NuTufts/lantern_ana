import os
import sys
import importlib
import inspect
import glob
from functools import wraps

# Dictionary to store all registered tag functions
_REGISTERED_TAGS = {}

def register_tag(func):
    """
    Decorator to register a tag function with the tagFactory.
    The function name is used as the tag identifier.
    """
    if func.__name__ in _REGISTERED_TAGS:
        raise ValueError("Registering a tag function with a name already registered: ",func.__name__)

    _REGISTERED_TAGS[func.__name__] = func
    return func

class TagFactory:
    """
    Factory class to manage and apply tag functions to events.
    """
    def __init__(self):
        self.tags = []
        TagFactory.auto_discover_tags()
        
    @classmethod
    def auto_discover_tags(cls):
        """
        Automatically discover and import all tag modules in the tags directory.
        This allows for automatic registration of decorated tag functions.
        """
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Find all Python files in the directory (excluding __init__.py and this file)
        module_files = glob.glob(os.path.join(current_dir, "*.py"))
        for module_path in module_files:
            module_name = os.path.basename(module_path).replace('.py', '')
            if module_name in ['__init__', 'tag_factory']:
                continue
                
            # Import the module to trigger the decorators
            try:
                # Convert file path to module path
                module_path = f"lantern_ana.tags.{module_name}"
                importlib.import_module(module_path)
            except ImportError as e:
                print(f"Warning: Could not import tag module {module_name}: {e}")
    
    @classmethod
    def list_available_tags(cls):
        """
        Return a list of all registered tag names.
        """
        return list(_REGISTERED_TAGS.keys())
        
    def add_tag(self, name, params=None):
        """
        Add a tag to the list to be applied per event.
        Store params to be passed to the tag function when run.
        
        Parameters:
        - name: Name of the registered tag function to use
        - params: Dictionary with parameters to control the tag behavior
        """
        if name not in _REGISTERED_TAGS:
            available_tags = ", ".join(TagFactory.list_available_tags())
            raise ValueError(f"Tag '{name}' is not registered. Available tags: {available_tags}")
            
        if params is None:
            params = {}
            
        self.tags.append({
            'name': name,
            'function': _REGISTERED_TAGS[name],
            'params': params
        })
        
    def apply_tags(self, ntuple):
        """
        Apply all registered tags in order.
        
        Parameters:
        - ntuple: The ntuple tree to run the tags on
        
        Returns:
        - passes: Boolean indicating if all tags passed
        - results: Dictionary with tag names as keys and results as values
        """
        tags = []
        
        for tag in self.tags:
            name = tag['name']
            func = tag['function']
            params = tag['params']
            
            # Apply the tag
            tag_result = func(ntuple, params)
            if tag_result is not None:
                tags.append(tag_result)
                
        return tags