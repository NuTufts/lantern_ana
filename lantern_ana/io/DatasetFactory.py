import os
import importlib
import yaml
from .dataset import Dataset
from typing import Dict, Any, List, Optional, Type

# Dictionary to store all registered dataset classes
_REGISTERED_DATASETS = {}

def register_dataset(cls):
    """
    Decorator to register a dataset class with the DatasetFactory.
    The class name is used as the dataset type identifier.
    """
    if cls.__name__ in _REGISTERED_DATASETS:
        raise ValueError(f"Registering a dataset class with a name already registered: {cls.__name__}")

    _REGISTERED_DATASETS[cls.__name__] = cls
    return cls

class DatasetFactory:
    """
    Factory class for creating dataset instances.
    """
    
    @classmethod
    def discover_datasets(cls, package_path: str) -> None:
        """
        Discover and import all dataset modules in a package.
        
        This will auto-register any dataset classes that use the @register_dataset decorator.
        
        Args:
            package_path: Path to the package containing dataset modules
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
            import sys
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
    
    @classmethod
    def create_from_config(cls, name: str, config: Dict[str, Any]) -> Dataset:
        """
        Create a dataset instance from a configuration dictionary.
        
        Args:
            name: Name for the dataset instance
            config: Configuration dictionary for the dataset
            
        Returns:
            A new dataset instance
            
        Raises:
            ValueError: If the dataset type is not recognized
        """
        dataset_type = config.get('type')
        if not dataset_type:
            raise ValueError(f"Dataset configuration for '{name}' missing required 'type' field")
            
        if dataset_type not in _REGISTERED_DATASETS:
            raise ValueError(f"Dataset type '{dataset_type}' not registered. Available types: {', '.join(_REGISTERED_DATASETS.keys())}")
            
        # Create and initialize the dataset
        dataset = _REGISTERED_DATASETS[dataset_type](name, config)
        dataset.initialize()
        
        return dataset
        
    @classmethod
    def create_from_yaml(cls, yaml_file: str) -> Dict[str, Dataset]:
        """
        Create dataset instances from a YAML configuration file.
        
        Args:
            yaml_file: Path to the YAML configuration file
            
        Returns:
            Dictionary mapping dataset names to dataset instances
        """
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
            
        datasets = {}
        dataset_config = config.get('datasets', {})
        folders = dataset_config.get('folders',[])
        for dataset_name, dataset_config in dataset_config.items():
            if 'folders' not in dataset_config:
                dataset_config['folders'] = folders
            datasets[dataset_name] = cls.create_from_config(dataset_name, dataset_config)
            
        return datasets
        
    @classmethod
    def list_registered_datasets(cls) -> List[str]:
        """
        Get a list of all registered dataset types.
        
        Returns:
            List of registered dataset type names
        """
        return list(_REGISTERED_DATASETS.keys())
