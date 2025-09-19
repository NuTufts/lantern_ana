import os,sys
import ROOT as rt
import numpy as nphotons


def crossesPlane(planeCoordStart, planeCoordEnd, firstStart, secondStart, plane, firstSlope, secondSlope, firstMin, firstMax, secondMin, secondMax):
    #See if a particle crosses a given plane. Meant primarily as a helper function for detectorGeometry
    detectorDimensions = {"xMin":0, "xMax":256, "yMin":-116.5, "yMax":116.5, "zMin":0, "zMax":1036}
    #First see if the particle crosses the plane's dimension
    if (planeCoordStart < detectorDimensions[str(plane)] and planeCoordEnd > detectorDimensions[str(plane)]) or (planeCoordStart > detectorDimensions[str(plane)] and planeCoordEnd < detectorDimensions[str(plane)]):
        #Now that we know it does, find the point at which it crosses
        firstCoord = firstSlope*(detectorDimensions[str(plane)] - planeCoordStart) + firstStart
        secondCoord = secondSlope*(detectorDimensions[str(plane)] - planeCoordStart) + secondStart

        #See if that point is on the detector plane, or if it passes by it
        if (firstCoord >= detectorDimensions[str(firstMin)] 
            and firstCoord <= detectorDimensions[str(firstMax)]
            and secondCoord >= detectorDimensions[str(secondMin)]
            and secondCoord <= detectorDimensions[str(secondMax)]
        ):
            return True #True means we know the point crosses
    
        #If it either didn't fall on the plane or didn't cross the dimension, we return false
        else:
            return False

    else:
        return False

def detectorGeometry(startX,
    startY, 
    startZ,
    endX,
    endY,
    endZ,
    ):
    #Given the specs for a particle, find the planes detector that particle moves through. Needs crossesPlane to function
    
    #We'll store our results here
    resultDict = {"CrossesX0":False, "CrossesXF":False, "CrossesY0":False, "CrossesYF":False, "CrossesZ0":False, "CrossesZF":False}

    #Start by finding the slopes of the track along x-y, x-z, y-z (and their inverses):
    slopeXY = (startY - endY)/(startX - endX)
    slopeYX = (startX - endX)/(startY - endY)
    slopeXZ = (startZ - endZ)/(startX - endX)
    slopeZX = (startX - endX)/(startZ - endZ)
    slopeYZ = (startZ - endZ)/(startY - endY)
    slopeZY = (startY - endY)/(startZ - endZ)
    #These slops will allow us to find the precise point of intersection, should it exist

    #Now we run crossesPlane on all six wire planes and record the results
    resultDict["CrossesX0"] = crossesPlane(startX, endX, startY, startZ, "xMin", slopeXY, slopeXZ, "yMin", "yMax", "zMin", "zMax")
    resultDict["CrossesXF"] = crossesPlane(startX, endX, startY, startZ, "xMax", slopeXY, slopeXZ, "yMin", "yMax", "zMin", "zMax")
    resultDict["CrossesY0"] = crossesPlane(startY, endY, startX, startZ, "yMin", slopeYX, slopeYZ, "xMin", "xMax", "zMin", "zMax")
    resultDict["CrossesYF"] = crossesPlane(startY, endY, startX, startZ, "yMax", slopeYX, slopeYZ, "xMin", "xMax", "zMin", "zMax")
    resultDict["CrossesZ0"] = crossesPlane(startZ, endZ, startX, startY, "zMin", slopeZX, slopeZY, "xMin", "xMax", "yMin", "yMax")
    resultDict["CrossesZF"] = crossesPlane(startZ, endZ, startX, startY, "zMax", slopeZX, slopeZY, "xMin", "xMax", "yMin", "yMax")

    return resultDict