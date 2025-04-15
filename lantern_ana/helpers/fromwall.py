import os,sys
import numpy as np
from ROOT as rt

def fromwall( start, pdir, fiducial_data, eps=1.0e-6 ):

    sVmin = (fiducial_data["vMin"]-start)/(pdir-eps) # unit step lengths to the axis-aligned minimum TPC boundaries
    sVmax = (fiducial_data["vMax"]-start)/(pdir-eps) # unit step lengths to the axis-aligned maximum TPC boundaries
    s = np.concatenate((sVmin,sVmax)) # put into the same array

    # find the minimum parameter to get to one of the walls
    sabs = np.abs(s) # take absolute value
    sindex = np.argmin(sabs)
    s_min = s[sindex] # get the shortest step distance

    # use to determine the TPC intersection point
    xpos = start+s_min*pdir

    # return distance to wall intersection point, along with intersection point, and index telling us which boundary we hit
    # index : boundary
    #  0    : xMin
    #  1    : yMin
    #  2    : zMin
    #  3    : xMax
    #  4    : yMax
    #  5    : zMax
    return np.abs(s_min), xpos, sindex
    
    
