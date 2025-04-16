import importlib
import inspect
import sys
import os
from typing import Dict, Type, List, Any

class ProducerFactory:
    """
    Factory class for managing producer registration and instantiation.
    """
    
    _producers: Dict[str, Type[ProducerBaseClass]] = {}
    
    @classmethod
    def register(cls, producer_class: Type[ProducerBaseClass]) -> Type[ProducerBaseClass]:
        """
        Register a producer class with the factory.
        
        This method is intended to be used as a decorator.
        
        Args:
            producer_class: The producer class to register
            
        Returns:
            The registered producer class (unchanged)
        """
        cls._producers[producer_class.__name__] = producer_class
        return producer_class
    
    @classmethod
    def create(cls, producer_type: str, name: str, config: Dict[str, Any]) -> ProducerBaseClass:
        """
        Create a new producer instance.
        
        Args:
            producer_type: The type of producer to create (must be registered)
            name: Name for the new producer instance
            config: Configuration dictionary for the new producer
            
        Returns:
            A new instance of the requested producer
            
        Raises:
            ValueError: If the requested producer type is not registered
        """
        if producer_type not in cls._producers:
            raise ValueError(f"Producer type '{producer_type}' not registered")
        
        return cls._producers[producer_type](name, config)
    
    @classmethod
    def list_producers(cls) -> List[str]:
        """
        Get a list of registered producer types.
        
        Returns:
            List of registered producer type names
        """
        return list(cls._producers.keys())
    
    @classmethod
    def discover_producers(cls, package_path: str) -> None:
        """
        Discover and import all producer modules in a package.
        
        This will auto-register any producer classes that use the @register decorator.
        
        Args:
            package_path: Path to the package containing producer modules
        """
        # Get absolute path to the package
        abs_path = os.path.abspath(package_path)
        if not os.path.isdir(abs_path):
            raise ValueError(f"Package path '{package_path}' is not a directory")
        
        # Get package name from path
        package_name = os.path.basename(abs_path)
        
        # Add package parent directory to path if not already there
        parent_dir = os.path.dirname(abs_path)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Import all Python modules in the package
        for root, dirs, files in os.walk(abs_path):
            rel_path = os.path.relpath(root, parent_dir)
            module_prefix = rel_path.replace(os.sep, '.')
            
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    module_name = file[:-3]  # Remove .py extension
                    full_module_name = f"{module_prefix}.{module_name}"
                    
                    try:
                        importlib.import_module(full_module_name)
                    except ImportError as e:
                        print(f"Error importing module {full_module_name}: {e}")


# Define register decorator as alias for ProducerFactory.register
register = ProducerFactory.register