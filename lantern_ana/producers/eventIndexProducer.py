# eventIndexProducer.py
"""
Custom Producer: eventIndexProducer

Created by: Taritree Wongjirad
Date: 2025-09-16
Purpose: Just copies over run, subrun, and event indices to the output tree

Run, subrun, and event are used in both the data and MC to uniquely label each event.

Example usage in YAML config:
    producers:
      my_variable:
        type: eventIndexProducer
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

@register  # This line makes your producer available to the framework!
class eventIndexProducer(ProducerBaseClass):
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
    [Write a detailed description here of what physics quantity you're measuring]
    
    EXAMPLE USE CASES:
    - Calculate track-to-shower energy ratio
    - Measure angular distributions of particles
    - Compute missing energy in events
    - Determine particle multiplicities
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
        2. Define your output variables using python arrays (from module 'array')
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
                       
        # STEP 2: DEFINE OUTPUT VARIABLES
        # ===============================
        # These are the quantities your producer will calculate for each event.
        # Use ROOT arrays so they can be saved to the output file.
        #
        # ARRAY TYPES:
        # - array('f', [0.0]) for floating point numbers (decimals)
        # - array('i', [0])   for integers (whole numbers)
        # - array('d', [0.0]) for double precision (very precise decimals)
    
        self.run    = array('i', [0])           # run number
        self.subrun = array('i', [0])           # run number
        self.event  = array('i', [0])           # run number
        self.fileid = array('i', [0])           # run number                
        
        # STEP 3: STORE VARIABLES IN A DICTIONARY (OPTIONAL BUT RECOMMENDED)
        # ==================================================================
        # This makes it easier to manage multiple variables
        self.output_vars = {
            'run':self.run,
            'subrun':self.subrun,
            'event':self.event,
            'fileid':self.fileid           
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
        for name,var in self.output_vars.items():
            var[0] = 0
    
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
        
        # ALTERNATIVE: Use the dictionary approach (cleaner for many variables)
        for var_name, var_array in self.output_vars.items():
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
        
        """
        
        # SPECIFY YOUR REQUIRED INPUTS
        # ============================
        # Most producers only need the raw detector data:
        required_inputs = ["gen2ntuple"]
        
        
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
        ismc = params.get('ismc', False)  # Is this Monte Carlo (simulated) data?
        
        # If you need other producer outputs:
        # vertex_data = data.get("vertex_properties", {})
        # electron_data = data.get("recoElectron", {})
        
        # STEP 2: RESET TO DEFAULTS
        # =========================
        # Start with clean values for this event
        self.setDefaultValues()
        
        # STEP 3: YOUR CALCULATIONS GO HERE!
        # ===================================
        # This is where you implement your physics analysis.
        # Use the detector data to calculate interesting quantities.

        
        
        # STEP 4: STORE YOUR RESULTS
        # ==========================
        # Put your calculated values into the output variables

        self.run[0]    = ntuple.run
        self.subrun[0] = ntuple.subrun
        self.event[0]  = ntuple.event
        self.fileid[0] = ntuple.fileid
        
        # STEP 5: RETURN SUMMARY (for other producers to use)
        # ===================================================
        # Return a dictionary so other producers can access your results
        return self.output_vars


# ==========================================
# EXAMPLE USAGE IN YAML CONFIG
# ==========================================
"""
# Add this to your analysis configuration:

producers:
  eventindex:                    # Your chosen name
    type: eventIndexProducer             # Must match your class name
    config: {}                           # Your configuration parameters
"""
