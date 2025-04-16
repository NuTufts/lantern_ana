
def get_uboone_tpc_bounds():
    return ((0, 256), (-116.5, 116.5), (0, 1036))

def is_inside_tpc(pos):
    """
    Test if inside the canonical uboone TPC boundary
    """
    # Detector boundaries
    ((xMin, xMax), (yMin, yMax), (zMin,zMax)) = get_uboone_tpc_bounds()
    
    # Check if vertex is within fiducial volume
    if (pos[0] <= xMin or 
        pos[0] >= xMax or 
        pos[1] <= yMin or 
        pos[1] >= yMax or 
        pos[2] <= zMin or 
        pos[2] >= zMax):
        return False
    else:
        return True