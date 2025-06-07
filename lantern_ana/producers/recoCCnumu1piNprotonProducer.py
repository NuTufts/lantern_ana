# recoCCnumu1piNprotonProducer.py
"""
Custom Producer: recoCCnumu1piNprotonProducer

Created by: Taritree Wongjirad
Date: 2025-06-06
Purpose: Find events with a 1 mu + 1 charged pion + >=1 proton final state

This producer calculates final state info from neutrino event data.
It takes raw detector information and produces derived quantities that
can be used by cuts to select interesting events.

Example usage in YAML config:
    producers:
      my_variable:
        type: recoCCnumu1piNprotonProducer
        config:
          parameter1: value1
          parameter2: value2
"""

# ==========================================
# REQUIRED IMPORTS - Don't change these!
# ==========================================
import numpy as np
from typing import Dict, Any, List
from array import array
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register

# ==========================================
# OPTIONAL IMPORTS - Add what you need
# ==========================================
# from math import sqrt, log, exp, sin, cos, pi
# from lantern_ana.utils.kinematics import calculate_angle
# from lantern_ana.cuts.fiducial_cuts import fiducial_cut

@register  # This line makes your producer available to the framework!
class recoCCnumu1piNprotonProducer(ProducerBaseClass):
    """
    STUDENT INSTRUCTIONS:
    =====================
    
    This is your custom producer class. A producer is like a calculator that
    takes raw detector data and computes new quantities for analysis.
    
    Think of it like a cooking recipe:
    - Input: Raw ingredients (detector data)
    - Process: Follow steps (your calculations)
    - Output: Finished dish (analysis variables)
    
    YOUR MISSION:
    1. Fill in the __init__ method with your variables
    2. Implement the processEvent method with your calculations
    3. Update the other methods as needed
    4. Test with a small dataset first!
    
    WHAT THIS PRODUCER CALCULATES:
    It looks through the prongs and counts the number of muons, pions, and protons.
    These particles have to pass a quality and energy threshold.
    
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        WHAT THIS DOES:
        ===============
        This is the "constructor" - it sets up your producer when the analysis starts.
        It's called once at the beginning, before processing any events.
        
        Think of this like setting up your calculator:
        - Define what variables you'll calculate
        - Set up any configuration parameters
        - Create storage for your results
        
        STUDENT TASKS:
        ==============
        1. Read configuration parameters from the 'config' dictionary
        2. Define your output variables using ROOT arrays
        3. Set any default values
        
        PARAMETERS:
        ===========
        - name: The name you give this producer in your YAML config
        - config: Dictionary of settings from your YAML config
        
        EXAMPLE VARIABLES TO CALCULATE:
        ===============================
        - Energy ratios, angles, distances
        - Particle counts, multiplicities
        - Timing information, quality metrics
        """
        
        # REQUIRED: Call the parent class constructor
        super().__init__(name, config)
        
        # STEP 1: READ CONFIGURATION PARAMETERS
        # ====================================
        # These come from your YAML config file under 'config:'
        # Use .get() with default values for safety
        
        self.min_muon_energy = config.get('min_muon_energy', 30.0)  # Minimum energy threshold (MeV)
        self.min_pion_energy = config.get('min_pion_energy', 30.0)  # Minimum energy threshold (MeV)
        self.min_proton_energy = config.get('min_proton_energy', 60.0)  # Minimum energy threshold (MeV)
        self.min_muon_completeness = config.get('min_muon_completeness',0.5)
        self.min_muon_purity = config.get('min_muon_purity',0.5)
        self.use_tracks = config.get('use_tracks', True)   # Whether to include tracks
        self.use_showers = config.get('use_showers', True) # Whether to include showers

        self.thresholds = {
          13:self.min_muon_energy,
          211:self.min_pion_energy,
          2212:self.min_proton_energy
        }
        
        # STEP 2: DEFINE OUTPUT VARIABLES
        # ===============================
        # These are the quantities your producer will calculate for each event.
        # Use arrays so they can be saved to the output file.
        #
        # ARRAY TYPES:
        # - array('f', [0.0]) for floating point numbers (decimals)
        # - array('i', [0])   for integers (whole numbers)
        # - array('d', [0.0]) for double precision (very precise decimals)
        self._vars = {
          'nmuons':array('i',[0]),
          'npions':array('i',[0]),
          'nprotons':array('i',[0]),
          'muKE':array('f',[0.0]),
          'maxprotonKE':array('f',[0.0]),
          'pionKE':array('f',[0.0]),
          'is_target_1mu1piNproton':array('i',[0])
        }
        self._counts = {
          13:self._vars['nmuons'],
          211:self._vars['npions'],
          2212:self._vars['nprotons']
        }
        
    
    def setDefaultValues(self):
        """
        WHAT THIS DOES:
        ===============
        Reset all your variables to safe default values before processing each event.
        This ensures clean data if something goes wrong or if the event is missing data.
        
        Think of this like clearing your calculator before doing a new problem.
        
        WHEN IT'S CALLED:
        ==================
        - Automatically before each event
        - Manually if an error occurs during processing
        
        STUDENT TASKS:
        ==============
        Set all your output variables to appropriate default values:
        - Use 0.0 for energies, angles, ratios
        - Use 0 for counts, flags
        - Use -1 or -999 for "invalid" or "not found" conditions
        """
        
        # REQUIRED: Call parent class method
        super().setDefaultValues()
        
        # RESET YOUR VARIABLES TO DEFAULTS
        # ================================
        for varname, var in self._vars.items():
          if var.typecode=='f':
            self._vars[varname][0] = 0.0
          elif var.typecode=='i':
            self._vars[varname][0] = 0


    
    def prepareStorage(self, output_tree):
        """
        WHAT THIS DOES:
        ===============
        Tell the output ROOT file what variables you want to save and how to store them.
        This creates "branches" in the output tree - think of them as columns in a spreadsheet.
        
        Think of this like labeling the columns in your data table before you start filling it.
        
        WHEN IT'S CALLED:
        ==================
        Once at the beginning, before processing any events.
        
        STUDENT TASKS:
        ==============
        Create a branch for each variable you want to save. The framework will
        automatically fill these branches with your calculated values.
        
        BRANCH NAMING CONVENTION:
        ========================
        - Branches are named: "{producer_name}_{variable_name}"
        - Types: /F for float, /I for integer, /D for double
        """
        
        # CREATE BRANCHES FOR YOUR VARIABLES
        # ==================================
        # Format: output_tree.Branch(branch_name, variable_array, "branch_name/TYPE")
        
        # ADD YOUR BRANCHES HERE:
        # output_tree.Branch(f"{self.name}_my_variable", self.my_variable, f"{self.name}_my_variable/F")
        
        # ALTERNATIVE: Use the dictionary approach (cleaner for many variables)
        for var_name, var_array in self._vars.items():
            if var_array.typecode == 'i':
                branch_type = f"{self.name}_{var_name}/I"
            else:
                branch_type = f"{self.name}_{var_name}/F"
            output_tree.Branch(f"{self.name}_{var_name}", var_array, branch_type)
    
    def requiredInputs(self) -> List[str]:
        """
        WHAT THIS DOES:
        ===============
        Tell the framework what data your producer needs to do its calculations.
        This ensures that other producers run first if you depend on their results.
        
        Think of this like listing the ingredients you need before you can cook.
        
        WHEN IT'S CALLED:
        ==================
        During setup, to determine the order that producers should run.
        
        STUDENT TASKS:
        ==============
        Return a list of the data sources you need:
        - "gen2ntuple" for raw detector data (most common)
        - Names of other producers if you need their calculated values
        
        COMMON INPUTS:
        ==============
        - "gen2ntuple": Raw detector data (tracks, showers, vertices, etc.)
        - "vertex_properties": Vertex information from VertexPropertiesProducer
        - "recoElectron": Electron properties from RecoElectronPropertiesProducer
        - "visible_energy": Energy calculation from VisibleEnergyProducer
        """
        
        # SPECIFY YOUR REQUIRED INPUTS
        # ============================
        # Most producers only need the raw detector data:
        required_inputs = ["gen2ntuple"]
        
        # If you need other producer outputs, add them here:
        # required_inputs.append("vertex_properties")
        # required_inputs.append("recoElectron")
        # required_inputs.append("visible_energy")
        
        return required_inputs
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        WHAT THIS DOES:
        ===============
        This is the MAIN FUNCTION where you do your calculations!
        It's called once for each neutrino event in your dataset.
        
        Think of this like the actual cooking process - you take your ingredients
        (input data) and follow your recipe (calculations) to create the final dish
        (analysis variables).
        
        WHEN IT'S CALLED:
        ==================
        Once for every event in your dataset. If you're processing 10,000 events,
        this function will be called 10,000 times.
        
        STUDENT TASKS:
        ==============
        1. Get the input data (ntuple, other producer outputs)
        2. Reset your variables to defaults
        3. Do your calculations using the detector data
        4. Store results in your output variables
        5. Return a summary dictionary
        
        PARAMETERS:
        ===========
        - data: Dictionary containing input data
          - data["gen2ntuple"]: Raw detector data
          - data["other_producer"]: Outputs from other producers
        - params: Dictionary with event information
          - params["ismc"]: True if this is simulated data
          - params["event_index"]: Event number being processed
        
        RETURNS:
        ========
        Dictionary with your calculated values (for other producers to use)
        """
        
        # STEP 1: GET INPUT DATA
        # ======================
        # Extract the data you need for your calculations
        ntuple = data["gen2ntuple"]  # Raw detector data - ALWAYS available
             
        # STEP 2: RESET TO DEFAULTS
        # =========================
        # Start with clean values for this event
        self.setDefaultValues()
        
        # STEP 3: YOUR CALCULATIONS GO HERE!
        # ===================================
        
        # Count and sum track energies
        max_idx = {
          13:-1,
          211:-1,
          2212:-1
        }
        max_energy = {
          13:0.0,
          211:0.0,
          2212:0.0
        }

        if ntuple.foundVertex==1:
          for i in range(ntuple.nTracks):
            if ntuple.trackIsSecondary[i] == 0:  # Only primary tracks
              pid = abs(ntuple.trackPID[i])
              if pid not in self.thresholds:
                continue
              if ntuple.trackRecoE[i]>self.thresholds[pid]:
                self._counts[pid][0] += 1
                if ntuple.trackRecoE[i]>max_energy[pid]:
                  max_idx[pid] = i
                  max_energy[pid] = ntuple.trackRecoE[i]

          # Count and sum shower energies  
          for i in range(ntuple.nShowers):
            if ntuple.showerIsSecondary[i] == 0:  # Only primary tracks
              pid = abs(ntuple.showerPID[i])
              if pid not in self.thresholds:
                continue
              if ntuple.showerRecoE[i]>self.thresholds[pid]:
                self._counts[pid][0] += 1
                if ntuple.showerRecoE[i]>max_energy[pid]:
                  max_idx[pid] = i
                  max_energy[pid] = ntuple.showerRecoE[i]

          if ( self._counts[13][0]==1 and
               self._counts[211][0]==1 and
               self._counts[2212][0]>=1 ):
            self._vars['is_target_1mu1piNproton'][0] = 1
          else:
            self._vars['is_target_1mu1piNproton'][0] = 0

          if self._counts[13][0]>0:
            self._vars['muKE'][0] = max_energy[13]
          if self._counts[211][0]>0:
            self._vars['pionKE'][0] = max_energy[211]
          if self._counts[2212][0]>0:
            self._vars['maxprotonKE'][0] = max_energy[2212] 
        # end of if vertex found       

        # STEP 5: RETURN SUMMARY (for other producers to use)
        # ===================================================
        # Return a dictionary so other producers can access your results
        # Copy over the values of all the variables we're going to store in the tree
        out = {}

        for varname, var in self._vars.items():
          out[varname] = var[0]

        return out

