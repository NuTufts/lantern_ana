import os,sys,time
import re
from typing import Dict, Any, List, Optional, Type
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
import numpy as np

# Example implementation of a ROOT-based dataset
@register
class FlashmodelVariablesProducer(ProducerBaseClass):
    """
    Implementation of Dataset for ROOT files.
    """
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        """
        
        We use this to copy flash predictions and metrics
        for the specific neutrino interaction vertex chosen by the ntuple maker.

        Requires that we setup an ntuple dataset to have the FlashMatchData as a friend TTree. 

        Example dataset configuration block:

        # Dataset configuration
        datasets:
          folders:
            - /mnt/ddrive/data/lantern_ana_ntuples/
          mcc9_v29e_dl_run3b_bnb_nu_overlay:
            type: RootDataset
            tree: EventTree
            ismc: false
            process: true
            filepaths:
             - ntuple_mcc9_v28_wctagger_run3_bnb1e19_v2_me_06_03_prod.root
            friendtrees:
              FlashPredictionTree: /mnt/ddrive/data/lantern_ana_ntuples/flashprediction_mcc9_v28_wctagger_run3_bnb1e19_v2_me_06_03_prod.root
        
        # Example producer configuration
        producers:
          flashmodel:
            type: FlashmodelVariablesProducer
            config:
              npmts: 32

        """
        super().__init__(name, config)

        self.NPMTS = config.get('npmts',32)


    def prepareStorage(self, output: Any) -> None:
        """
        Set up what to save in the output ROOT TTree.
        """
        self.flashvariables = {}
        self.flashvariables['observed_pe_per_pmt']        = array('f',[0.0]*self.NPMTS)
        self.flashvariables['observed_totpe']             = array('f',[0.0])
        self.flashvariables['cosmic_totpe']               = array('f',[0.0])        

        self.flashvariables['nnmodel_pe_per_pmt']         = array('f',[0.0]*self.NPMTS)
        self.flashvariables['nnmodel_totpe']              = array('f',[0.0])
        self.flashvariables['nnmodel_fracpe']             = array('f',[0.0])
        self.flashvariables['nnmodel_balanced_sinkdiv']   = array('f',[0.0])
        self.flashvariables['nnmodel_unbalanced_sinkdiv'] = array('f',[0.0])

        self.flashvariables['ublm_pe_per_pmt']            = array('f',[0.0]*self.NPMTS)
        self.flashvariables['ublm_totpe']                 = array('f',[0.0])
        self.flashvariables['ublm_fracpe']                = array('f',[0.0])
        self.flashvariables['ublm_balanced_sinkdiv']      = array('f',[0.0])
        self.flashvariables['ublm_unbalanced_sinkdiv']    = array('f',[0.0])
        
        """Set up branches in the output ROOT TTree."""
        for var_name, var_array in self.flashvariables.items():
            if var_array.typecode == 'i':
                branch_type = f"{self.name}_{var_name}/I"
            else:
                branch_type = f"{self.name}_{var_name}/F"
            output.Branch(f"{self.name}_{var_name}", var_array, branch_type)

        return

    def setDefaultValues(self):
        super().setDefaultValues()
        for varname in self.flashvariables:
            var_array = self.flashvariables[varname]
            if len(var_array)>1:
                # Reset all elements to zero using slice assignment
                for i in range(len(var_array)):
                    var_array[i] = 0.0
            else:
                var_array[0] = -1.0

        return

    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]

    def return_variables(self) -> Dict[str,Any]:
        """
        return values of variables in self.flashvariables.
        return length 1 arrays as floats and length>1 arrays as tuples
        """
        out = {}
        for varname,vararray in self.flashvariables.items():
            # Check length and return appropriate type
            if len(vararray) == 1:
                out[varname] = float(vararray[0])
            else:
                out[varname] = tuple(vararray)

        return out



    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Copy data from the FlashPredictionTree TTree

        Available branches in FlashPredictionTree:
        *Br    0 :entry     : entry/I
        *Br    1 :run       : run/I
        *Br    2 :subrun    : subrun/I
        *Br    3 :event     : event/I
        *Br    4 :n_vertices : n_vertices/I
        *Br    5 :has_vertices : has_vertices/O
        *Br    6 :has_flash : has_flash/O
        *Br    7 :obs_total_pe : obs_total_pe/F
        *Br    8 :obs_time  : obs_time/F
        *Br    9 :obs_pe_per_pmt : vector<float>
        *Br   10 :reco_vertex_x : vector<float>
        *Br   11 :reco_vertex_y : vector<float>
        *Br   12 :reco_vertex_z : vector<float>
        *Br   13 :n_tracks_all : vector<int>
        *Br   14 :n_showers_all : vector<int>
        *Br   15 :n_primary_tracks : vector<int>
        *Br   16 :n_primary_showers : vector<int>
        *Br   17 :total_charge_all : vector<float>
        *Br   18 :total_photons_all : vector<float>
        *Br   19 :ubpred_total_pe_all : vector<float>
        *Br   20 :ubpred_pe_per_pmt_all : vector<vector<float> >
        *Br   21 :ub_sinkhorn_div_all : vector<vector<float> >
        *Br   22 :ub_unbalanced_sinkhorn_div_all : vector<vector<float> >
        *Br   23 :ub_pe_diff_all : vector<float>
        *Br   24 :ub_pe_fracerr_all : vector<float>
        *Br   25 :siren_total_pe_all : vector<float>
        *Br   26 :siren_pe_per_pmt_all : vector<vector<float> >
        *Br   27 :siren_outtpc_pts : vector<int>
        *Br   28 :siren_voxelcharge : vector<float>
        *Br   29 :siren_sinkhorn_div_all : vector<vector<float> >
        *Br   30 :siren_unbalanced_sinkhorn_div_all : vector<vector<float> >
        *Br   31 :siren_pe_diff_all : vector<float>
        *Br   32 :siren_pe_fracerr_all : vector<float>
        *Br   33 :vtx_dist_to_true : vector<float>
        *Br   34 :true_vtx_x : true_vtx_x/F
        *Br   35 :true_vtx_y : true_vtx_y/F
        *Br   36 :true_vtx_z : true_vtx_z/F
        *Br   37 :has_mc_truth : has_mc_truth/O
        """
        ntuple = data["gen2ntuple"]
        ismc = params.get('ismc', False)
        datasetname = params.get('dataset_name')

        if ntuple.foundVertex==0:
            return self.return_variables()

        # Get FlashPredictionTree from friend trees
        flashtree = None
        if hasattr(ntuple, 'GetFriend'):
            flashtree = ntuple.GetFriend("FlashPredictionTree")

        if flashtree is None:
            # No flash prediction data available
            return self.return_variables()

        # Test if the TTree has the vtxIndex branch
        nucand_ubmodel_vertex_index = -1
        nucand_siren_vertex_index = -1
        has_vtxIndex_branch = hasattr(flashtree, 'vtxIndex')

        if has_vtxIndex_branch:
            nucand_ubmodel_vertex_index = flashtree.vtxIndex
            nucand_siren_vertex_index   = flashtree.vtxIndex
        else:
            # In the case of many of the current ntuples, we did not save the vtxIndex branch. 
            # We must find another way to match the flash prediction for the various nu candidates in an event
            # To the one saved in the primary EventTree TTree.
            # We have saved info about the nu candidate vertices in the FlashPredictionTree to do this match.
            # We use the reco position and the number of track and showers (primary and all).
            # For those that match, we choose the flash prediction with the lowest unbalanced sinkhorn divergence.
            # We independently check which prediction to return for the ub light model prediction and the siren model prediction.

            # valid matches must match the reco vertex position and nshowers and number of tracks
            # get this information from the primary EventTree tree
            reco_vtx_pos = np.array( (ntuple.vtxX, ntuple.vtxY, ntuple.vtxZ) )
            nshowers     = ntuple.nShowers
            ntracks      = ntuple.nTracks
            nprim_tracks = 0
            nprim_showers = 0
            for i in range(ntracks):
                if ntuple.trackIsSecondary[i]==0:
                    nprim_tracks += 1
            for i in range(nshowers):
                if ntuple.showerIsSecondary[i]==0:
                    nprim_showers += 1

            # Find best matching vertex for UB and SIREN model based on lowest unbalanced sinkhorn divergence
            min_ub_div    = float('inf')
            for i in range(flashtree.ub_unbalanced_sinkhorn_div_all.size()):
                # get the copy of the reco vertex positions in the friend FlashPredictionTree TTree
                vtxpos = np.array( (ntuple.reco_vertex_x[i], ntuple.reco_vertex_y[i], ntuple.reco_vertex_z[i]))
                dist = np.power(vtxpos-reco_vtx_pos,2).sum()
                if (dist<1.0e-3 
                      and nshowers==ntuple.n_showers_all[i] 
                      and ntracks==ntuple.n_tracks_all[i]
                      and nprim_tracks==ntuple.n_primary_tracks[i]
                      and nprim_showers==ntuple.n_primary_showers[i]
                      and flashtree.ub_unbalanced_sinkhorn_div_all[i].size() > 0):
                    div_val = flashtree.ub_unbalanced_sinkhorn_div_all[i][0]
                    if div_val < min_ub_div:
                        min_ub_div = div_val
                        nucand_ubmodel_vertex_index = i

            # Find best matching vertex for SIREN model based on lowest unbalanced sinkhorn divergence
            min_siren_div = float('inf')
            for i in range(flashtree.siren_unbalanced_sinkhorn_div_all.size()):
                # get the copy of the reco vertex positions in the friend FlashPredictionTree TTree
                vtxpos = np.array( (ntuple.reco_vertex_x[i], ntuple.reco_vertex_y[i], ntuple.reco_vertex_z[i]))
                dist = np.power(vtxpos-reco_vtx_pos,2).sum()
                if (dist<1.0e-3 
                      and nshowers==ntuple.n_showers_all[i] 
                      and ntracks==ntuple.n_tracks_all[i]
                      and nprim_tracks==ntuple.n_primary_tracks[i]
                      and nprim_showers==ntuple.n_primary_showers[i]
                      and flashtree.siren_unbalanced_sinkhorn_div_all[i].size() > 0):
                    div_val = flashtree.siren_unbalanced_sinkhorn_div_all[i][0]
                    if div_val < min_siren_div:
                        min_siren_div = div_val
                        nucand_siren_vertex_index = i

        # Now we can copy over nu candidate flash predictions
        if nucand_siren_vertex_index>=0 and nucand_siren_vertex_index<flashtree.siren_pe_per_pmt_all.size():
            # Transfer SIREN model information from the ntuple to self.flashvariables
            siren_pmt_vec = flashtree.siren_pe_per_pmt_all[nucand_siren_vertex_index]
            for i in range(min(self.NPMTS, siren_pmt_vec.size())):
                self.flashvariables['nnmodel_pe_per_pmt'][i] = siren_pmt_vec[i]

            self.flashvariables['nnmodel_totpe'][0] = flashtree.siren_total_pe_all[nucand_siren_vertex_index]
            self.flashvariables['nnmodel_fracpe'][0] = flashtree.siren_pe_fracerr_all[nucand_siren_vertex_index]

            if flashtree.siren_sinkhorn_div_all[nucand_siren_vertex_index].size() > 0:
                self.flashvariables['nnmodel_balanced_sinkdiv'][0] = flashtree.siren_sinkhorn_div_all[nucand_siren_vertex_index][0]
            if flashtree.siren_unbalanced_sinkhorn_div_all[nucand_siren_vertex_index].size() > 0:
                self.flashvariables['nnmodel_unbalanced_sinkdiv'][0] = flashtree.siren_unbalanced_sinkhorn_div_all[nucand_siren_vertex_index][0]

        if nucand_ubmodel_vertex_index>=0 and nucand_ubmodel_vertex_index<flashtree.ubpred_pe_per_pmt_all.size():
            # Transfer UB light model information from the ntuple to self.flashvariables
            ub_pmt_vec = flashtree.ubpred_pe_per_pmt_all[nucand_ubmodel_vertex_index]
            for i in range(min(self.NPMTS, ub_pmt_vec.size())):
                self.flashvariables['ublm_pe_per_pmt'][i] = ub_pmt_vec[i]

            self.flashvariables['ublm_totpe'][0] = flashtree.ubpred_total_pe_all[nucand_ubmodel_vertex_index]
            self.flashvariables['ublm_fracpe'][0] = flashtree.ub_pe_fracerr_all[nucand_ubmodel_vertex_index]

            if flashtree.ub_sinkhorn_div_all[nucand_ubmodel_vertex_index].size() > 0:
                self.flashvariables['ublm_balanced_sinkdiv'][0] = flashtree.ub_sinkhorn_div_all[nucand_ubmodel_vertex_index][0]
            if flashtree.ub_unbalanced_sinkhorn_div_all[nucand_ubmodel_vertex_index].size() > 0:
                self.flashvariables['ublm_unbalanced_sinkdiv'][0] = flashtree.ub_unbalanced_sinkhorn_div_all[nucand_ubmodel_vertex_index][0]

        # Copy over observed pe per pmt
        if hasattr(flashtree, 'obs_pe_per_pmt'):
            for i in range(min(self.NPMTS, flashtree.obs_pe_per_pmt.size())):
                self.flashvariables['observed_pe_per_pmt'][i] = flashtree.obs_pe_per_pmt[i]
            self.flashvariables['observed_totpe'][0] = flashtree.obs_total_pe
        if hasattr(flashtree, 'cosmic_pe_per_pmt'):
            #for i in range(min(self.NPMTS, flashtree.obs_pe_per_pmt.size())):
            #    self.flashvariables['observed_pe_per_pmt'][i] = flashtree.obs_pe_per_pmt[i]
            self.flashvariables['cosmic_totpe'][0] = flashtree.cosmic_total_pe

        return self.return_variables()

    def finalize(self):
        """
        nothing to do
        """
        return
        
