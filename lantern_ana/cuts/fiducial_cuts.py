from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.utils import is_inside_tpc, apply_sce_correction, get_uboone_tpc_bounds

@register_cut
def fiducial_cut(ntuple, params):
    """
    Cut events where the vertex is outside the fiducial volume.
    
    Parameters:
    - ntuple: The event ntuple
    - params: Dictionary with optional parameters:
        - 'width': Margin from detector edges (default: 10 cm)
        - 'applyscc': Apply Space Charge Correction (default: True)
        
    Returns:
    - True if the vertex is inside the fiducial volume, False otherwise
    """
    # Default width
    width = params.get('width', 10.0)
    applyscc = params.get('applyscc',True)
    
    # Check if we have a reconstructed vertex
    if not hasattr(ntuple, 'foundVertex') or ntuple.foundVertex != 1:
        return False
        
    pos = (ntuple.vtxX, ntuple.vtxY, ntuple.vtxZ)
    # Detector boundaries
    if not is_inside_tpc(pos):
        return False

    if applyscc:
        corrected_pos = apply_sce_correction(pos)
    else:
        corrected_pos = pos

    # Detector boundaries
    ((xMin, xMax), (yMin, yMax), (zMin,zMax)) = get_uboone_tpc_bounds()
    
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