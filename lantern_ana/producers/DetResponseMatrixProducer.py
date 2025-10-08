# DetResponseMatrixProducer.py
"""
Custom Producer: DetResponseMatrixProducer

Created by: Taritree Wongjirad
Date: 2025-10-08
Purpose: Create response matrix between reco and true observables

This producer fills a response matrix between two variables, typically 
where one is a 'true' value while another is anobservable. For example:
   - true neutrino energy versus reco neutrino energy
   - true muon momentum versus reco muon momentum

Example usage in YAML config:
    # datasets block specifies data files we loop through
    datasets:
      mcc9_v29e_run1_bnb_nu_overlay:
        ...
    producers:
      detresponse_nuenergy:
        type: DetResponseMatrixProducer
        config:
          xbinconfig: 
            variable_formula: "ntuple.true_nu_energy"
            # use a list of binedges for non-uniform binning
            binedges: [0.0, 100.0, 200.0, 300.0, 500.0, 700.0, 1000.0] 
            # OR specify nbins and range for uniform bins
            numbins: 10
            minvalue: 0.0
            maxvalue: 1000.0
          ybinconfig:
            variable_formula: "ntuple.reco_nu_energy"
            numbins: 10
            minvalue: 0.0
            maxvalue: 1000.0
          event_weight_formula: "ntuple.eventweight_weight"
          apply_to_datasets:
            - mcc9_v29e_run1_bnb_nu_overlay
          cut_formulas:
            pass_selection: "{ntuple.numuCC1piNpReco_is_target_1mu1piNproton}==1"
          event_selection_critera: ['pass_selection']

          
Output:
  The producer will create a rootfile with the following products.
    - a TH2D with name h{producer_name}_{dataset_name}


"""

# ==========================================
# REQUIRED IMPORTS - Don't change these!
# ==========================================
import numpy as np
from typing import Dict, Any, List
from array import array
import ROOT as rt
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
import re

# ==========================================
# OPTIONAL IMPORTS - Add what you need
# ==========================================
# from math import sqrt, log, exp, sin, cos, pi
# from lantern_ana.utils.kinematics import calculate_angle
# from lantern_ana.cuts.fiducial_cuts import fiducial_cut

@register  # This line makes your producer available to the framework!
class DetResponseMatrixProducer(ProducerBaseClass):

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

        We configure the producer based on the config.
        """

        self.x_config = config.get('xbinconfig',None)
        self.y_config = config.get('ybinconfig',None)
        if self.x_config is None:
          raise ValueError("DetResponseMatrixProducer requires parmeter xbinconfig, a dictionary defining the x-bins.")
        if self.y_config is None:
          raise ValueError("DetResponseMatrixProducer requires parmeter ybinconfig, a dictionary defining the y-bins.")

        self.applicable_datasets = config.get('apply_to_datasets',[])
        if len(self.applicable_datasets)==0:
          raise ValueError("Missing list of datasets to apply this producer to. Parameter name is 'apply_to_datasets'")

        self.event_weight_formula = config.get('event_weight_formula',None)
        # if not specified, just using event weight of 1.0

        # event selection criterion
        self.cut_formulas = config.get('cut_formulas',{})
        self.event_selection_critera = config.get('event_selection_critera',[])
        
        # REQUIRED: Call the parent class constructor
        super().__init__(name, config)
        
        # STEP 3: STORE VARIABLES IN A DICTIONARY (OPTIONAL BUT RECOMMENDED)
        # ==================================================================
        # This makes it easier to manage multiple variables
        self.output_vars = {}
    
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

        We do not have values to reset each event.
        
        """
    
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
        
        We create histograms.
        """
        
        self.detresponse_hists = {}
        for dataset in self.applicable_datasets:
          hname = f"hdetresponse__{self.name}__{dataset}"
          if 'binedges' in self.x_config and 'binedges' in self.y_config:
            xbins = array('f',self.x_config.get('binedges'))
            ybins = array('f',self.y_config.get('binedges'))
            hdetresposne = rt.TH2D(hname,"",xbins,ybins)
          elif 'binedges' in self.x_config and 'binedges' not in self.y_config:
            xbins = array('f',self.x_config.get('binedges'))
            hdetresposne = rt.TH2D(hname,"",xbins,self.y_config['numbins'],self.y_config['minvalue'],self.y_config['maxvalue'])
          elif 'binedges' in self.y_config and 'binedges' not in self.x_config:
            ybins = array('f',self.y_config.get('binedges'))
            hdetresposne = rt.TH2D(hname,"",self.x_config['numbins'],self.x_config['minvalue'],self.x_config['maxvalue'],ybins)
          else:
            hdetresposne = rt.TH2D(hname,"",self.x_config['numbins'],self.x_config['minvalue'],self.x_config['maxvalue'],
                                    self.y_config['numbins'],self.y_config['minvalue'],self.y_config['maxvalue'] )
          print("creating histogram for dataset[",dataset,"]: ",hname," ",hdetresposne)
          self.detresponse_hists[dataset] = hdetresposne
          
    
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
        
        PARAMETERS:
        ===========
        - data: Dictionary containing input data
          - data["gen2ntuple"]: Raw detector data
          - data["other_producer"]: Outputs from other producers
        - params: Dictionary with event information
          - params["ismc"]: True if this is simulated data
          - params["event_index"]: Event number being processed
          - params["dataset_name"]: Name of dataset we are currently looping through
        
        RETURNS:
        ========
        Since all we do is fill a histogram, we do not return any variables
        """
        
        # Get dataset info and check if this produce applies to it
        ntuple = data["gen2ntuple"]  # Raw detector data - ALWAYS available
        ismc = params.get('ismc', False)  # Is this Monte Carlo (simulated) data?
        dataset_name = params.get('dataset_name')

        if dataset_name not in self.detresponse_hists:
          return {}
        
        # evaluate the cuts and see if we apply them
        passes = self._process_selection_cut( ntuple )

        if not passes:
          return {}


        # Fill histogram
        xvariable = eval(self.x_config['variable_formula'])
        yvariable = eval(self.y_config['variable_formula'])
        if self.event_weight_formula is None:
          eventweight = 1.0
        else:
          eventweight = eval(self.event_weight_formula)

        #print(xvariable," ",yvariable," ",eventweight)

        self.detresponse_hists[dataset_name].Fill(xvariable,yvariable,eventweight)

        # Return an empty dictionary since we didnt create any new informatino
        return {}

    def _process_selection_cut( self, ntuple ):

        # in order to decide if this event is something we are going to fill
        select_results = {}
        for cutname,cutformula in self.cut_formulas.items():
            # Extract placeholders from the formula (strings inside {})
            placeholders = re.findall(r'\{([^}]+)\}', cutformula)

            # Create clean expression and namespace
            clean_expression = cutformula
            namespace = {}
            for placeholder in placeholders:
                # Create a simple variable name from the placeholder
                var_name = placeholder.replace('.', '_').replace('[', '_').replace(']', '')
                clean_expression = clean_expression.replace(f"{{{placeholder}}}", var_name)
                # Evaluate the placeholder to get the actual value
                namespace[var_name] = eval(placeholder)

            # Evaluate the clean expression with the namespace
            select_results[cutname] = eval(clean_expression, namespace)

        #print(select_results)
        passes = True
        for cutname,result in select_results.items():
            if result==False:
                passes = False
                break

        return passes

    def finalize(self) -> None:
      for dataset_name,hist in self.detresponse_hists.items():
        hist.Write()
      return 


