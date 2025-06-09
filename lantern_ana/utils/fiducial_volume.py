import os,sys
from lantern_ana.utils.boundarytests import get_uboone_tpc_bounds, is_inside_tpc

def dwall_inside( x, y, z, return_dim_dists=False ):
    """
    Calculate the perpendicular distance from a TPC boundary, assuming
    the point is inside the TPC. If the tpc is outside, return
    a sentinal value of -1.0.
    """
    vtx = (x,y,z)
    if not is_inside_tpc(vtx):
        return -1.0

    tpcwall = get_uboone_tpc_bounds()
    mindist = 1e8
    dimdists = [1e9,1e9,1e9]
    for idim in range(3):
        distlo = vtx[idim]-tpcwall[idim][0]
        disthi = tpcwall[idim][1]-vtx[idim]

        # tests for dim
        if distlo>=0 and distlo<dimdists[idim]:
            dimdists[idim] = distlo
        if disthi>=0 and disthi<dimdists[idim]:
            dimdists[idim] = disthi

        if dimdists[idim]<mindist:
            mindist = dimdists[idim]

    if return_dim_dists:
        return mindist,dimdists
    else:
        return mindist


def dwall_outside( x, y, z, return_dim_dists=False ):
    """
    Calculate the perpendicular distance from a TPC boundary, assuming
    the point is inside the TPC. If the tpc is outside, return
    a sentinal value of -1.0.
    """
    vtx = (x,y,z)
    if is_inside_tpc(vtx):
        return -1.0

    tpcwall = get_uboone_tpc_bounds()
    mindist = 1e8
    dimdists = [1e9,1e9,1e9]
    for idim in range(3):
        distlo = tpcwall[idim][0]-vtx[idim]
        disthi = vtx[idim]-tpcwall[idim][1]

        # tests for dim: only positive values are valid
        if distlo>=0 and distlo<dimdists[idim]:
            dimdists[idim] = distlo
        if disthi>=0 and disthi<dimdists[idim]:
            dimdists[idim] = disthi

        if dimdists[idim]<mindist:
            mindist = dimdists[idim]

    if return_dim_dists:
        return mindist,dimdists
    else:
        return mindist
    

def dwall( x, y, z, return_dim_dists=False):

    vtx = (x,y,z)

    if return_dim_dists:
        if is_inside_tpc( vtx ):
            mindist, dimdists = dwall_inside( x, y, z, return_dim_dists=True )
        else:
            mindist, dimdists = dwall_outside( x, y, z, return_dim_dists=True )
            # by convention, the distances outside are negnative
            mindist *= -1.0
            for i in len(dimdists):
                dimdists[i] *= -1.0
    else:
        if is_inside_tpc( vtx ):
            mindist = dwall_inside( x, y, z )
        else:
            mindist = dwall_outside( x, y, z )
            # by convention, the distances outside are negnative
            mindist *= -1.0

    return mindist
    

