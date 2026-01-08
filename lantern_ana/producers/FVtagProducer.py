# FVtagProducer.py
"""
Custom Producer: FVtagProducer

Created by: [Your Name Here]
Date: 2025-06-09
Purpose: [Describe what this producer calculates - be specific!]

This producer calculates [YOUR DESCRIPTION HERE] from neutrino event data.
It takes raw detector information and produces derived quantities that
can be used by cuts to select interesting events.

Example usage in YAML config:
    producers:
      my_variable:
        type: FVtagProducer
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
class FVtagProducer(ProducerBaseClass):
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
        
        self.min_energy = config.get('fiducial_distance', 17.0)  # Fiducial Distance (in cm)

        
        # ADD YOUR CONFIGURATION PARAMETERS HERE:
        # self.my_parameter = config.get('my_parameter', default_value)
        
        # STEP 2: DEFINE OUTPUT VARIABLES
        # ===============================
        # These are the quantities your producer will calculate for each event.
        # Use ROOT arrays so they can be saved to the output file.
        #
        # ARRAY TYPES:
        # - array('f', [0.0]) for floating point numbers (decimals)
        # - array('i', [0])   for integers (whole numbers)
        # - array('d', [0.0]) for double precision (very precise decimals)
        
        self.is_in_fv = array('i', [0])         

        
        # ADD YOUR VARIABLES HERE:
        # self.my_variable = array('f', [0.0])  # Description of what this measures
        
        # STEP 3: STORE VARIABLES IN A DICTIONARY (OPTIONAL BUT RECOMMENDED)
        # ==================================================================
        # This makes it easier to manage multiple variables
        self.output_vars = {
            'total_energy': self.total_energy,
            'particle_count': self.particle_count,
            'energy_ratio': self.energy_ratio,
            'max_angle': self.max_angle,
            'is_interesting': self.is_interesting,
            # ADD YOUR VARIABLES HERE:
            # 'my_variable': self.my_variable,
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
        # Example resets - MODIFY THESE for your variables!
        self.total_energy[0] = 0.0      # No energy initially
        self.particle_count[0] = 0       # No particles found
        self.energy_ratio[0] = -1.0      # Invalid ratio (use -1 to indicate "not calculated")
        self.max_angle[0] = 0.0          # No angle measured
        self.is_interesting[0] = 0       # Not interesting by default
        
        # RESET YOUR VARIABLES HERE:
        # self.my_variable[0] = default_value
    
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
        
        # Example branches - MODIFY THESE for your variables!
        output_tree.Branch(f"{self.name}_isinfv", self.is_in_fv, f"{self.name}_isinfv/F")
      
        # ADD YOUR BRANCHES HERE:
        # output_tree.Branch(f"{self.name}_my_variable", self.my_variable, f"{self.name}_my_variable/F")
        
        # ALTERNATIVE: Use the dictionary approach (cleaner for many variables)
        # for var_name, var_array in self.output_vars.items():
        #     if var_array.typecode == 'i':
        #         branch_type = f"{self.name}_{var_name}/I"
        #     else:
        #         branch_type = f"{self.name}_{var_name}/F"
        #     output_tree.Branch(f"{self.name}_{var_name}", var_array, branch_type)
    
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
        
        # EXAMPLE CALCULATION 1: Count and sum particle energies
        # =====================================================
        total_energy = 0.0
        particle_count = 0
        
        # Count and sum track energies
        for i in range(ntuple.nTracks):
            if ntuple.trackIsSecondary[i] == 0:  # Only primary tracks
                if ntuple.trackRecoE[i] > self.min_energy:  # Above threshold
                    total_energy += ntuple.trackRecoE[i]
                    particle_count += 1
        
        # Count and sum shower energies  
        for i in range(ntuple.nShowers):
            if ntuple.showerIsSecondary[i] == 0:  # Only primary showers
                if ntuple.showerRecoE[i] > self.min_energy:  # Above threshold
                    total_energy += ntuple.showerRecoE[i]
                    particle_count += 1
        
        # EXAMPLE CALCULATION 2: Calculate energy ratio
        # ============================================
        track_energy = sum(ntuple.trackRecoE[i] for i in range(ntuple.nTracks) 
                          if ntuple.trackIsSecondary[i] == 0)
        shower_energy = sum(ntuple.showerRecoE[i] for i in range(ntuple.nShowers) 
                           if ntuple.showerIsSecondary[i] == 0)
        
        if shower_energy > 0:
            energy_ratio = track_energy / shower_energy
        else:
            energy_ratio = -1.0  # Invalid - no showers found
        
        # EXAMPLE CALCULATION 3: Find maximum opening angle
        # ================================================
        max_angle = 0.0
        # [Add your angle calculation here if needed]
        
        # EXAMPLE CALCULATION 4: Interesting event flag
        # ============================================
        # Define your own criteria for what makes an event "interesting"
        is_interesting = 1 if (total_energy > 200.0 and particle_count >= 2) else 0
        
        # STEP 4: STORE YOUR RESULTS
        # ==========================
        # Put your calculated values into the output variables
        self.total_energy[0] = total_energy
        self.particle_count[0] = particle_count
        self.energy_ratio[0] = energy_ratio
        self.max_angle[0] = max_angle
        self.is_interesting[0] = is_interesting
        
        # ADD YOUR CALCULATIONS HERE:
        # ===========================
        # 1. Access detector data from 'ntuple'
        # 2. Do your physics calculations
        # 3. Store results in your variables
        # 
        # USEFUL DETECTOR DATA:
        # ntuple.nTracks, ntuple.nShowers - number of reconstructed objects
        # ntuple.trackRecoE[i] - energy of track i
        # ntuple.showerRecoE[i] - energy of shower i  
        # ntuple.trackIsSecondary[i] - 0 for primary, 1 for secondary
        # ntuple.vtxX, ntuple.vtxY, ntuple.vtxZ - vertex position
        # ntuple.foundVertex - 1 if vertex found, 0 otherwise
        #
        # EXAMPLE PHYSICS CALCULATIONS:
        # - Total visible energy: sum all track + shower energies
        # - Particle multiplicities: count tracks/showers above threshold
        # - Angular distributions: calculate angles between particles
        # - Missing energy: compare visible vs. neutrino energy (MC only)
        # - Quality metrics: completeness, purity of reconstruction
        
        # STEP 5: RETURN SUMMARY (for other producers to use)
        # ===================================================
        # Return a dictionary so other producers can access your results
        return {
            'total_energy': total_energy,
            'particle_count': particle_count,
            'energy_ratio': energy_ratio,
            'max_angle': max_angle,
            'is_interesting': is_interesting,
            # ADD YOUR VARIABLES HERE:
            # 'my_variable': self.my_variable[0],
        }

    def finalize(self):
        """
        nothing to do after the event loop
        """
        super().finalize()
        return

# ==========================================
# HELPFUL PHYSICS FORMULAS AND EXAMPLES
# ==========================================
"""
COMMON PHYSICS CALCULATIONS FOR NEUTRINO EVENTS:

1. VISIBLE ENERGY:
   E_visible = sum(track_energies) + sum(shower_energies)

2. PARTICLE MULTIPLICITIES:
   n_tracks = count(tracks with E > threshold)
   n_showers = count(showers with E > threshold)

3. OPENING ANGLES (between two particles):
   cos(θ) = (p1⃗ · p2⃗) / (|p1⃗| |p2⃗|)
   where p⃗ is the momentum vector

4. MISSING TRANSVERSE MOMENTUM:
   p_T_miss = |∑p⃗_T_visible - p⃗_T_neutrino|

5. INVARIANT MASS (for particle pairs):
   M_inv = sqrt((E1 + E2)² - (p⃗1 + p⃗2)²)

6. EVENT TOPOLOGY VARIABLES:
   - Sphericity: measure of how "spherical" vs "jet-like" 
   - Aplanarity: measure of how planar the event is
   - Thrust: measure of how collimated the event is

USEFUL NTUPLE VARIABLES:
========================
Tracks:
- ntuple.nTracks: number of reconstructed tracks
- ntuple.trackRecoE[i]: reconstructed energy of track i
- ntuple.trackStartX[i], trackStartY[i], trackStartZ[i]: track start point
- ntuple.trackEndX[i], trackEndY[i], trackEndZ[i]: track end point
- ntuple.trackIsSecondary[i]: 0=primary, 1=secondary
- ntuple.trackPID[i]: particle ID (13=muon, 211=pion, 2212=proton)

Showers:
- ntuple.nShowers: number of reconstructed showers
- ntuple.showerRecoE[i]: reconstructed energy of shower i
- ntuple.showerStartX[i], showerStartY[i], showerStartZ[i]: shower start
- ntuple.showerIsSecondary[i]: 0=primary, 1=secondary
- ntuple.showerPID[i]: particle ID (11=electron, 22=photon)

Vertex:
- ntuple.foundVertex: 1 if vertex found, 0 otherwise
- ntuple.vtxX, vtxY, vtxZ: reconstructed vertex position
- ntuple.vtxIsFiducial: 1 if in fiducial volume

Monte Carlo Truth (MC only):
- ntuple.trueNuE: true neutrino energy
- ntuple.trueNuPDG: neutrino type (12=nue, 14=numu, -12=antinue, -14=antinumu)
- ntuple.trueNuCCNC: 0=CC, 1=NC interaction
- ntuple.trueVtxX, trueVtxY, trueVtxZ: true vertex position

DEBUGGING TIPS:
===============
1. Start simple - calculate one variable first
2. Print values during development:
   print(f"Debug: total_energy = {total_energy}")
3. Test with small event samples (max_events: 100)
4. Check for edge cases (division by zero, empty lists)
5. Use default values for invalid calculations
6. Look at existing producers for examples
"""

# ==========================================
# EXAMPLE USAGE IN YAML CONFIG
# ==========================================
"""
# Add this to your analysis configuration:

producers:
  my_physics_vars:                    # Your chosen name
    type: FVtagProducer             # Must match your class name
    config:                           # Your configuration parameters
      min_energy: 50.0                # Minimum energy threshold (MeV)
      use_tracks: true                # Include tracks in calculations
      use_showers: true               # Include showers in calculations
      # Add your custom parameters here

# Then your cuts can use the calculated variables:
cuts:
  high_energy_cut:
    min_total_energy: 500.0           # Uses my_physics_vars_total_energy
  interesting_events:
    require_interesting: true         # Uses my_physics_vars_is_interesting
"""
