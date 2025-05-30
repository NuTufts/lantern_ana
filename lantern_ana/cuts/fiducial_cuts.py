# lantern_ana/cuts/fiducial_cuts_new.py
from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.cuts.cutBaseClass import CutBaseClass
from lantern_ana.utils import is_inside_tpc, apply_sce_correction, get_uboone_tpc_bounds
from typing import Dict, Any, List, Union, Tuple

@register_cut
class FiducialCut(CutBaseClass):
    """
    Cut events where the vertex is outside the fiducial volume.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.width = config.get('width', 10.0)
        self.apply_scc = config.get('apply_scc', True)
        self.use_true_vtx = config.get('use_true_vtx', False)
        self.use_wc_volume = config.get('use_wc_volume', False)
    
    def evaluate(self, ntuple: Any, params: Dict[str, Any]) -> bool:
        """
        Evaluate fiducial volume cut.
        
        Parameters from config:
        - width: Margin from detector edges (default: 10 cm)
        - apply_scc: Apply Space Charge Correction (default: True)
        - use_true_vtx: Use true vertex variable (default: False)
        - use_wc_volume: Use Wire Cell fiducial volume definition (default: False)
        
        Returns:
        - True if the vertex is inside the fiducial volume, False otherwise
        """

        # Use the inside WireCell Volume check run when the lantern ntuple is made
        if self.use_wc_volume:
            return ntuple.vtxIsFiducial == 1

        # do we use the true or the reco vertex
        if not self.use_true_vtx:
            # Check if we have a reconstructed vertex
            if not hasattr(ntuple, 'foundVertex') or ntuple.foundVertex != 1:
                return False
                
            pos = (ntuple.vtxX, ntuple.vtxY, ntuple.vtxZ)
        else:
            # Check FV requirement using true vtx

            # But first, is this a MC file?
            ismc = params.get('ismc',False)
            if not ismc:
                # this is not a MC file, but we want to evaluate a truth vertex. Then just pass the event.
                return True
            pos = (ntuple.trueVtxX, ntuple.trueVtxY, ntuple.trueVtxZ)


        # Detector boundaries
        if not is_inside_tpc(pos):
            return False

        if self.apply_scc:
            corrected_pos = apply_sce_correction(pos)
        else:
            corrected_pos = pos

        # Detector boundaries
        ((xMin, xMax), (yMin, yMax), (zMin, zMax)) = get_uboone_tpc_bounds()
        
        # Check if vertex is within fiducial volume
        if (corrected_pos[0] <= (xMin + self.width) or 
            corrected_pos[0] >= (xMax - self.width) or 
            corrected_pos[1] <= (yMin + self.width) or 
            corrected_pos[1] >= (yMax - self.width) or 
            corrected_pos[2] <= (zMin + self.width) or 
            corrected_pos[2] >= (zMax - self.width)):
            return False
        else:
            return True
    
    def get_description(self) -> str:
        return f"Fiducial volume cut with {self.width} cm margin from detector edges"
    
    def get_required_branches(self) -> List[str]:
        branches = []
        if self.use_true_vtx:
            branches.extend(['trueVtxX', 'trueVtxY', 'trueVtxZ'])
        else:
            branches.extend(['foundVertex', 'vtxX', 'vtxY', 'vtxZ'])
        
        if self.use_wc_volume:
            branches.append('vtxIsFiducial')
            
        return branches
    
    def validate_config(self) -> bool:
        """Validate configuration parameters."""
        if not isinstance(self.width, (int, float)) or self.width < 0:
            return False
        if not isinstance(self.apply_scc, bool):
            return False
        if not isinstance(self.use_true_vtx, bool):
            return False
        if not isinstance(self.use_wc_volume, bool):
            return False
        return True
