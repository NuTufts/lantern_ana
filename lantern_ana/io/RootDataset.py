import os
from .dataset import Dataset
from .DatasetFactory import register_dataset
from typing import Dict, Any, List, Optional, Type


# Example implementation of a ROOT-based dataset
@register_dataset
class RootDataset(Dataset):
    """
    Implementation of Dataset for ROOT files.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize a ROOT dataset.
        
        Args:
            name: A unique identifier for this dataset
            config: Dictionary containing configuration parameters:
                - tree: Name of the TTree to read
                - filepaths: List of ROOT file paths
                - ismc: Whether this is a Monte Carlo dataset, {default: False}
                - nspills: Number of spills this data set represents (optional) {default: None}
                - pot: POT for this data set (optional) {default: None}
        """
        super().__init__(name, config)
        self._tree_name = config.get('tree')
        self._folders   = config.get('folders',["./"])
        self._filepaths = config.get('filepaths', [])
        self._ismc = config.get('ismc', False)
        self._tree = None
        self._num_entries = 0
        self._pot = None
        self._nspills = None
        self._added_filepaths = []
        
    def initialize(self) -> None:
        """
        Initialize the dataset by opening the ROOT file and getting the tree.
        """
        import ROOT
        
        if not self._filepaths:
            raise ValueError(f"No file paths provided for dataset '{self.name}'")
            
        self._tree = ROOT.TChain( self._tree_name )

        for fpath in self._filepaths:
            if len(fpath)>0 and fpath[0]!="/":
                xfpath = self.find_file_in_folders( fpath, self._folders )
                if xfpath is None:
                    raise ValueError(f"Could not find file={fpath} in folders: {self._folders}")
            else:
                xfpath = fpath

            if not os.path.exists(xfpath):
                raise ValueError(f"could not load filepath for '{self._tree_name}': {xfpath}" )
            print(f'Adding to dataset[{self._tree_name}] to Tree[{self._tree_name}]: {xfpath}')
            self._tree.Add(xfpath)
            self._added_filepaths.append(xfpath)
           
        self._num_entries = self._tree.GetEntries()
        
        # Get POT information for MC datasets
        if self._ismc:
            pot_tree = self._rfile.Get("potTree")
            if pot_tree:
                for i in range(pot_tree.GetEntries()):
                    pot_tree.GetEntry(i)
                    self._pot += pot_tree.totGoodPOT
                    
        self._initialized = True

    def find_file_in_folders(self, filename, folder_list):
        """
        Looks for a file in a list of folders.

        Args:
            filename: The name of the file to search for.
            folder_list: A list of folder paths to search in.

        Returns:
            The full path to the file if found, otherwise None.
        """
        for folder in folder_list:
            for root, _, files in os.walk(folder):
                if filename in files:
                    return os.path.join(root, filename)
        return None
        
    def get_num_entries(self) -> int:
        """
        Get the number of entries in the dataset.
        
        Returns:
            Number of entries in the dataset
        """
        if not self._initialized:
            self.initialize()
            
        return self._num_entries
        
    def set_entry(self, entry: int) -> bool:
        """
        Set the current entry in the dataset.
        
        Args:
            entry: Entry index to set
            
        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            self.initialize()
            
        if entry < 0 or entry >= self._num_entries:
            return False
            
        bytes_read = self._tree.GetEntry(entry)
        if bytes_read <= 0:
            return False
            
        self._current_entry = entry
        return True
        
    def get_data(self) -> Dict[str, Any]:
        """
        Get the data for the current entry.
        
        Returns:
            Dictionary containing data for the current entry
        """
        if not self._initialized:
            self.initialize()
            
        if self._current_entry < 0:
            raise ValueError("No entry selected. Call set_entry() first.")
            
        # For ROOT datasets, we simply return the tree itself
        # Consumers can access the tree's branches directly
        return {
            "tree": self._tree,
            "entry": self._current_entry,
            "ismc": self._ismc,
            "pot": self._pot
        }
        
    @property
    def pot(self) -> float:
        """
        Get the POT (Protons On Target) for this dataset.
        Only relevant for MC datasets.
        
        Returns:
            POT value
        """
        if not self._initialized:
            self.initialize()
            
        return self._pot