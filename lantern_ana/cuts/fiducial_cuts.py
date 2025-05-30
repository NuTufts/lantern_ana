# lantern_ana/cuts/fiducial_cuts_new.py
from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.utils import is_inside_tpc, apply_sce_correction, get_uboone_tpc_bounds
from typing import Dict, Any, List, Union, Tuple


def fiducial_cut(ntuple, params):
    """
    Function-based fiducial volume cut based on the FiducialCut class.
    
    Parameters:
    - ntuple: The event ntuple
    - params: Dictionary with parameters:
        - 'width': Margin from detector edges (default: 10 cm)
        - 'apply_scc': Apply Space Charge Correction (default: True)
        - 'usetruevtx': Use true vertex variable (default: False)
        - 'useWCvolume': Use Wire Cell fiducial volume definition (default: False)
        
    Returns:
    - True if the vertex is inside the fiducial volume, False otherwise
    """
    # Extract parameters with defaults
    width = params.get('width', 10.0)
    apply_scc = params.get('apply_scc', True)
    use_true_vtx = params.get('usetruevtx', False)
    use_wc_volume = params.get('useWCvolume', False)
    
    # Use the inside WireCell Volume check run when the lantern ntuple is made
    if use_wc_volume:
        return ntuple.vtxIsFiducial == 1

    # Determine which vertex to use
    if not use_true_vtx:
        # Check if we have a reconstructed vertex
        if not hasattr(ntuple, 'foundVertex') or ntuple.foundVertex != 1:
            return False
        pos = (ntuple.vtxX, ntuple.vtxY, ntuple.vtxZ)
    else:
        # Check FV requirement using true vtx
        ismc = params.get('ismc', False)
        if not ismc:
            # Not a MC file, but we want to evaluate a truth vertex. Just pass the event.
            return True
        pos = (ntuple.trueVtxX, ntuple.trueVtxY, ntuple.trueVtxZ)

    # Check if inside TPC
    if not is_inside_tpc(pos):
        return False

    # Apply space charge correction if requested
    if apply_scc:
        corrected_pos = apply_sce_correction(pos)
    else:
        corrected_pos = pos

    # Get detector boundaries
    ((xMin, xMax), (yMin, yMax), (zMin, zMax)) = get_uboone_tpc_bounds()
    
    # Check if vertex is within fiducial volume
    if (corrected_pos[0] <= (xMin + width) or 
        corrected_pos[0] >= (xMax - width) or 
        corrected_pos[1] <= (yMin + width) or 
        corrected_pos[1] >= (yMax - width) or 
        corrected_pos[2] <= (zMin + width) or 
        corrected_pos[2] >= (zMax - width)):
        return False
    else:
        return True
