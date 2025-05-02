from abc import ABC, abstractmethod
import yaml
from typing import Dict, Any, List, Optional, Type
import os
import importlib
import inspect
import glob

class Dataset(ABC):
    """
    Abstract base class for dataset access.
    All concrete dataset implementations should inherit from this class.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize the dataset with a name and configuration.
        
        Args:
            name: A unique identifier for this dataset
            config: Dictionary containing configuration parameters
        """
        self.name = name
        self.config = config
        self._current_entry = -1
        self._initialized = False
        
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the dataset, loading necessary files and resources.
        This method should be called before any data access.
        """
        pass
        
    @abstractmethod
    def get_num_entries(self) -> int:
        """
        Get the number of entries in the dataset.
        
        Returns:
            Number of entries in the dataset
        """
        pass
        
    @abstractmethod
    def set_entry(self, entry: int) -> bool:
        """
        Set the current entry in the dataset.
        
        Args:
            entry: Entry index to set
            
        Returns:
            True if successful, False otherwise
        """
        pass
        
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """
        Get the data for the current entry.
        
        Returns:
            Dictionary containing data for the current entry
        """
        pass
        
    @property
    def current_entry(self) -> int:
        """
        Get the current entry index.
        
        Returns:
            Current entry index
        """
        return self._current_entry
        
    def __len__(self) -> int:
        """
        Get the number of entries in the dataset.
        
        Returns:
            Number of entries in the dataset
        """
        return self.get_num_entries()