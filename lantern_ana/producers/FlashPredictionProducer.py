# FlashPredictionProducer.py
"""
Custom Producer: FlashPredictionProducer

Created by: Taritree Wongjirad
Date: 2025-06-14
Purpose: Transfers info related to comparison of predicted and observed optical signal.

This producer transfers information made from calculating the predicted optical signal
for each neutrino candidate. This includes the predicted PE, the observed PE, 
the fractional error of the total PE predicted, and the sinkhorn divergence between the
normalized spatial pattern.

Example usage in YAML config:
    producers:
      flashprediction:
        type: FlashPredictionProducer
        config: {}

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
class FlashPredictionProducer(ProducerBaseClass):
    
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
        # No config parameters
        
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
        
        # Defining variables in a dictionary for easier use

        self._vars = {
            'predictedpe':  array('f',[0.0]),
            'observedpe':   array('f',[0.0]),
            'fracerr':      array('f',[0.0]),
            'sinkhorn_div': array('f',[0.0])
        }
    
    def setDefaultValues(self):
        """
        """
        
        # REQUIRED: Call parent class method
        super().setDefaultValues()
        
        # RESET YOUR VARIABLES TO DEFAULTS
        # ================================
        for varname, var in self._vars.items():
            if var.typecode=='f':
              var[0] = 0.0
            else:
              var[0] = 0

        # good value we want is a low sinkhorn_div, so we store a high sentinal value
        self._vars['sinkhorn_div'][0] = 9999.0

    def prepareStorage(self, output_tree):
        """
        BRANCH NAMING CONVENTION:
        ========================
        - Branches are named: "{producer_name}_{variable_name}"
        - Types: /F for float, /I for integer, /D for double
        """
        
        # CREATE BRANCHES FOR YOUR VARIABLES
        # ==================================
        # Format: output_tree.Branch(branch_name, variable_array, "branch_name/TYPE")
        
        # Example branches - MODIFY THESE for your variables!       
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
        
        # if no vertex is found, just return default values
        if ntuple.foundVertex==0:
          out = {}
          for varname,val in self._vars.items():
            out[varname] = val[0]
          return out

        # We are trying to match the flashprediction info to the vertex saved by the ntuple maker
        # We can only do this by matching position (vertex ID was not saved)

        # which vertex did we save into the ntuple
        matchedvertices = []
        vtx = np.array( (ntuple.vtxX,ntuple.vtxY,ntuple.vtxZ) )
        obs_total_pe = ntuple.obs_total_pe
        nvertices    = ntuple.pred_total_pe_all.size()
        mindist = 1.0e9

        m = (70.0/3.0)
        b = 70.0

        #print("VTX: ",vtx)
        for ivtx in range(nvertices):

          vtxflash = np.array( (ntuple.reco_vertex_x[ivtx],ntuple.reco_vertex_y[ivtx],ntuple.reco_vertex_z[ivtx]) )

          #print("FlASH VTX: ",vtxflash)
          dist = vtx-vtxflash
          dist = (dist*dist).sum()

          if dist < mindist:
            mindist = dist

          if dist>1.0e-2:
            # not the right vertex
            continue

          sinkdiv_all  = ntuple.sinkhorn_div_all[ivtx][1]
          pred_total_pe_all = ntuple.pred_total_pe_all.at(ivtx)*2.0
          fracerr = (pred_total_pe_all-obs_total_pe)/(0.1+obs_total_pe)
          x_fracerr = fracerr+1.0

          # print(sinkdiv_all)
          # print(x_fracerr)


          z_test = sinkdiv_all - m*x_fracerr - b

          matchedvertices.append( {'ivtx':ivtx,'sinkdiv_all':sinkdiv_all,'fracerr':fracerr,'pred':pred_total_pe_all,'z_test':z_test} )

        matched = None
        if len(matchedvertices)>1:
          # we have to pick the best match. first, do we have any that passes out pre-selection cut (using z_test)
          npass = 0
          min_sink = 1.0e9
          min_index = -1
          min_sink_pass = 1.0e9
          min_index_pass = -1
          for idx,vertexdata in enumerate(matchedvertices):
            # get best, from only those passing cut
            if vertexdata['z_test']<=0:
              npass += 1
              if min_sink_pass > vertexdata['sinkdiv_all']:
                min_sink_pass  = vertexdata['sinkdiv_all']
                min_index_pass = idx
            # get best, regardless of passing
            if min_sink > vertexdata['sinkdiv_all']:
              min_sink  = vertexdata['sinkdiv_all']
              min_index = idx

          if npass==0:
            # just simply pick lowest sinkdiv
            matched = matchedvertices[min_index]
          else:
            # pick from the passing
            matched = matchedvertices[min_index_pass]

        elif len(matchedvertices)==1:
          matched = matchedvertices[0]
        else:
          raise ValueError(f"DID NOT FIND MATCHED VERTEX: mindist={mindist} nvertices(flash)={nvertices}")

        
        # STEP 4: STORE YOUR RESULTS
        # ==========================
        # Put your calculated values into the output variables
        self._vars['sinkhorn_div'][0] = matched['sinkdiv_all']
        self._vars['fracerr'][0]      = matched['fracerr']
        self._vars['predictedpe'][0]  = matched['pred']
        self._vars['observedpe'][0]   = obs_total_pe
        
        
        # STEP 5: RETURN SUMMARY (for other producers to use)
        # ===================================================
        # Return a dictionary so other producers can access your results
        out = {}
        for varname,val in self._vars.items():
          out[varname] = val[0]

        return out

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
    type: FlashPredictionProducer             # Must match your class name
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
