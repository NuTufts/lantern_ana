# NeutrinoKinematicsProducer.py
"""
Custom Producer: NeutrinoKinematicsProducer

Created by: Analysis User
Date: 2025-09-05
Purpose: Extract neutrino energy, visible energy from largest primary shower, cos theta, and calculate efficacy/purity

This producer extracts key kinematic variables from neutrino events:
- Reconstructed neutrino energy (ntuple.recoNuE)
- Visible energy from largest primary shower (ntuple.showerRecoE[largest_primary_idx])
- Cos theta of largest primary shower (ntuple.showerCosTheta[largest_primary_idx])
- Efficacy and purity metrics from the largest primary shower

Example usage in YAML config:
    producers:
      nu_kinematics:
        type: NeutrinoKinematicsProducer
        config:
          min_shower_energy: 50.0   # Minimum energy threshold in MeV
          min_charge: 0.0           # Minimum charge for quality cuts
"""

# ==========================================
# REQUIRED IMPORTS
# ==========================================
import numpy as np
from typing import Dict, Any, List
from array import array
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register

@register  # This line makes your producer available to the framework!
class nuPropertiesProducer(ProducerBaseClass):
    """
    Producer to extract neutrino kinematic variables and reconstruction quality metrics.
    
    This producer calculates:
    - Reconstructed neutrino energy 
    - Visible energy from the largest primary shower
    - Cos theta of the largest primary shower
    - Efficacy (completeness) and purity of the largest primary shower
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize the producer with configuration parameters and output variables.
        
        Args:
            name: Producer instance name
            config: Configuration dictionary with parameters
        """
        super().__init__(name, config)
        
        # Configuration parameters with defaults
        self.min_shower_energy = config.get('min_shower_energy', 50.0)  # MeV
        self.min_charge = config.get('min_charge', 0.0)  # Minimum charge threshold
        
        # Output variables - use ROOT arrays for storage
        self.reco_nu_energy = array('f', [0.0])          # Reconstructed neutrino energy (GeV)
        self.visible_energy = array('f', [0.0])          # Visible energy from largest shower (GeV)
        self.cos_theta = array('f', [-999.0])            # Cos theta of largest shower
        self.efficacy = array('f', [-1.0])               # Completeness/efficacy
        self.purity = array('f', [-1.0])                 # Purity
        self.largest_shower_idx = array('i', [-1])       # Index of largest primary shower
        self.has_valid_shower = array('i', [0])          # Flag for valid shower found
        
    def prepareStorage(self, output_tree):
        """
        Create branches in the output ROOT tree for all calculated variables.
        
        Args:
            output_tree: ROOT TTree for output storage
        """
        # Create branches for each output variable
        output_tree.Branch(f"{self.name}_reco_nu_energy", self.reco_nu_energy, f"{self.name}_reco_nu_energy/F")
        output_tree.Branch(f"{self.name}_visible_energy", self.visible_energy, f"{self.name}_visible_energy/F")
        output_tree.Branch(f"{self.name}_cos_theta", self.cos_theta, f"{self.name}_cos_theta/F")
        output_tree.Branch(f"{self.name}_efficacy", self.efficacy, f"{self.name}_efficacy/F")
        output_tree.Branch(f"{self.name}_purity", self.purity, f"{self.name}_purity/F")
        output_tree.Branch(f"{self.name}_largest_shower_idx", self.largest_shower_idx, f"{self.name}_largest_shower_idx/I")
        output_tree.Branch(f"{self.name}_has_valid_shower", self.has_valid_shower, f"{self.name}_has_valid_shower/I")

    def setDefaultValues(self):
        """
        Reset all variables to their default values for each event.
        """
        self.reco_nu_energy[0] = 0.0
        self.visible_energy[0] = 0.0
        self.cos_theta[0] = -999.0       # Invalid value to indicate no measurement
        self.efficacy[0] = -1.0          # Invalid value 
        self.purity[0] = -1.0            # Invalid value
        self.largest_shower_idx[0] = -1  # No shower found
        self.has_valid_shower[0] = 0     # No valid shower by default
        
    def requiredInputs(self) -> List[str]:
        """
        Specify that this producer requires the gen2ntuple input.
        
        Returns:
            List of required input data sources
        """
        return ["gen2ntuple"]
    
    def find_largest_primary_shower(self, ntuple) -> int:
        """
        Find the index of the largest primary shower based on charge.
        
        Args:
            ntuple: Event data containing shower information
            
        Returns:
            Index of largest primary shower, or -1 if none found
        """
        largest_idx = -1
        max_charge = -1.0
        
        # Loop through all showers to find largest primary
        for i in range(ntuple.nShowers):
            # Must be primary shower (not secondary)
            if ntuple.showerIsSecondary[i] != 0:
                continue
                
            # Must be classified by LArPID
            if ntuple.showerClassified[i] != 1:
                continue
                
            # Apply energy threshold
            if ntuple.showerRecoE[i] < self.min_shower_energy:
                continue
                
            # Apply charge threshold if specified
            if ntuple.showerCharge[i] < self.min_charge:
                continue
                
            # Check if this is the largest so far
            if ntuple.showerCharge[i] > max_charge:
                max_charge = ntuple.showerCharge[i]
                largest_idx = i
                
        return largest_idx
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single event to extract neutrino kinematics and quality metrics.
        
        Args:
            data: Dictionary containing input data (including gen2ntuple)
            params: Additional processing parameters
            
        Returns:
            Dictionary with calculated variables for other producers to use
        """
        # Get the ntuple data
        ntuple = data["gen2ntuple"]
        
        # Reset to default values
        self.setDefaultValues()
        
        # Extract reconstructed neutrino energy (convert from MeV to GeV)
        if hasattr(ntuple, 'recoNuE'):
            self.reco_nu_energy[0] = ntuple.recoNuE / 1000.0  # Convert MeV to GeV
        
        # Find the largest primary shower
        largest_idx = self.find_largest_primary_shower(ntuple)
        
        if largest_idx >= 0:
            # Valid shower found
            self.largest_shower_idx[0] = largest_idx
            self.has_valid_shower[0] = 1
            
            # Extract visible energy from largest shower (convert MeV to GeV)
            self.visible_energy[0] = ntuple.showerRecoE[largest_idx] / 1000.0
            
            # Extract cos theta
            self.cos_theta[0] = ntuple.showerCosTheta[largest_idx]
            
            # Extract efficacy (completeness) and purity
            # These come from LArPID predictions
            if ntuple.showerComp[largest_idx] >= 0:  # Valid completeness
                self.efficacy[0] = ntuple.showerComp[largest_idx]
            
            if ntuple.showerPurity[largest_idx] >= 0:  # Valid purity
                self.purity[0] = ntuple.showerPurity[largest_idx]
        
        # Return summary for other producers to use
        return {
            'reco_nu_energy': self.reco_nu_energy[0],
            'visible_energy': self.visible_energy[0],
            'cos_theta': self.cos_theta[0],
            'efficacy': self.efficacy[0],
            'purity': self.purity[0],
            'largest_shower_idx': self.largest_shower_idx[0],
            'has_valid_shower': self.has_valid_shower[0]
        }