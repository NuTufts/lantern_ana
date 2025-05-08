from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Type

class ProducerBaseClass(ABC):
    """
    Abstract base class for data producers.
    
    A producer processes input data (typically from a ROOT TTree) and 
    produces output that can be consumed by other producers.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize the producer with a name and configuration.
        
        Args:
            name: A unique identifier for this producer instance
            config: Dictionary containing configuration parameters
        """
        self.name = name
        self.config = config
        self._output = None  # Will be set by prepareStorage
    
    @abstractmethod
    def prepareStorage(self, output: Any) -> None:
        """
        Prepare output storage for this producer.
        
        This method is called by the manager to set up storage for
        the producer's output (e.g., a branch in a ROOT TTree).
        
        Args:
            output: The output storage interface (e.g., a ROOT TTree)
        """
        pass

    @abstractmethod
    def setDefaultValues(self):
        """
        Set the default values for the variables we are making.
        """
        pass
    
    def productType(self) -> Type:
        """
        Get the type of the product produced by this producer.
        
        Returns:
            The Python type of the output product (default: float)
        """
        return float
    
    def requiredInputs(self) -> List[str]:
        """
        Get a list of required input producer names and/or source dataset.
        
        Returns:
            List of names of producers whose outputs are required by this producer
        """
        return ["gen2ntuple"]
    
    @abstractmethod
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Any:
        """
        Process a single event using the provided data.
        
        Args:
            data: Dictionary mapping producer names to their outputs
            params: Additional parameters for this processing step
            
        Returns:
            The output of the producer for this event
        """
        pass