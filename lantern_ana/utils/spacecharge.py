_uboone_reverse_scetool = None

def apply_sce_correction( pos ):
    """
    Remove the space-charge effect using MicroBooNE reverse SCE tool

    Parameters:
    - pos: reconstructed (x,y,z) position inside the TPC

    Returns:
    - tuple with (x,y,z) values
    """
    global _uboone_reverse_scetool
    if _uboone_reverse_scetool is None:
        from larlite import larlite
        from larlite import larutil
        _uboone_reverse_scetool = larutil.SpaceChargeMicroBooNE( larutil.SpaceChargeMicroBooNE.kMCC9_Backward )

    offset_v = _uboone_reverse_scetool.GetPosOffsets( pos[0], pos[1], pos[2] )

    return (pos[0]+offset_v[0], pos[1]+offset_v[1], pos[2]+offset_v[2])