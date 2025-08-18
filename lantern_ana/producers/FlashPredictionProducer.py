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

        
        # REQUIRED: Call the parent class constructor
        super().__init__(name, config)
        
       
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
        
        for var_name, var_array in self._vars.items():
            if var_array.typecode == 'i':
                branch_type = f"{self.name}_{var_name}/I"
            else:
                branch_type = f"{self.name}_{var_name}/F"
            output_tree.Branch(f"{self.name}_{var_name}", var_array, branch_type)
            print(f"{self.name}_{var_name}")


    def requiredInputs(self) -> List[str]:

        required_inputs = ["gen2ntuple"]

        
        return required_inputs
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        
        ntuple = data["gen2ntuple"]  # Raw detector data - ALWAYS available
        ismc = params.get('ismc', False)  # Is this Monte Carlo (simulated) data?
        
        
       
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
