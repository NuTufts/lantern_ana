# lantern_ana/cuts/cutBaseClass.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple

class CutBaseClass(ABC):
    """
    Abstract base class for cut implementations.
    
    A cut processes input data (typically from a ROOT TTree) and 
    returns a boolean indicating whether the event passes the cut,
    optionally with additional data.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize the cut with a name and configuration.
        
        Args:
            name: A unique identifier for this cut instance
            config: Dictionary containing configuration parameters
        """
        self.name = name
        self.config = config
    
    @abstractmethod
    def evaluate(self, ntuple: Any, params: Dict[str, Any]) -> Union[bool, Tuple[bool, Dict[str, Any]]]:
        """
        Evaluate the cut for a single event.
        
        Args:
            ntuple: The event ntuple/tree to evaluate
            params: Additional parameters for this cut evaluation
            
        Returns:
            Either:
            - bool: True if event passes cut, False otherwise
            - Tuple[bool, Dict]: (passes, cut_data) where cut_data contains
              additional information from the cut evaluation
        """
        pass
    
    def get_description(self) -> str:
        """
        Get a human-readable description of what this cut does.
        
        Returns:
            Description string
        """
        return f"Cut: {self.__class__.__name__}"
    
    def get_required_branches(self) -> List[str]:
        """
        Get a list of required ntuple branches for this cut.
        
        Returns:
            List of branch names that must be present in the ntuple
        """
        return []
    
    def validate_config(self) -> bool:
        """
        Validate the configuration parameters for this cut.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        return True