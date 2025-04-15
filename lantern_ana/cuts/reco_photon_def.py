import os,sys

def getRecoPhotonList(ntuple, fiducial, showerE_threshold = 0, tracksize_threshold=0, completeness_threshold=0.3):
  #Creates a list of photons based on the showers in the event
  recoPhotonInfo = []

  # from showers
  for x in range(ntuple.nShowers):
    accept = False
    if showerE_threshold == 0:
      if ntuple.showerClassified[x] == 1:
        if ntuple.showerPID[x] == 22:
          if ntuple.showerComp[x]<completeness_threshold:
            continue
          if ( ntuple.showerStartPosX[x] > (fiducial["xMin"] + fiducial["photonWidth"])
               and ntuple.showerStartPosX[x] < (fiducial["xMax"] - fiducial["photonWidth"])
               and ntuple.showerStartPosY[x] > (fiducial["yMin"] + fiducial["photonWidth"])
               and ntuple.showerStartPosY[x] < (fiducial["yMax"] - fiducial["photonWidth"])
               and ntuple.showerStartPosZ[x] > (fiducial["zMin"] + fiducial["photonWidth"])
               and ntuple.showerStartPosZ[x] < (fiducial["zMax"] - fiducial["photonWidth"])):
            accept = True
    elif ntuple.showerRecoE[x] > showerE_threshold:
      if ntuple.showerPID[x] == 22:
        if ntuple.showerComp[x]<completeness_threshold:
          continue        
        #Extra check to ensure photons deposit in fiducial volume
        if ( ntuple.showerStartPosX[x] > (fiducial["xMin"] + fiducial["photonWidth"])
             and ntuple.showerStartPosX[x] < (fiducial["xMax"] - fiducial["photonWidth"])
             and ntuple.showerStartPosY[x] > (fiducial["yMin"] + fiducial["photonWidth"])
             and ntuple.showerStartPosY[x] < (fiducial["yMax"] - fiducial["photonWidth"])
             and ntuple.showerStartPosZ[x] > (fiducial["zMin"] + fiducial["photonWidth"])
             and ntuple.showerStartPosZ[x] < (fiducial["zMax"] - fiducial["photonWidth"]) ):
          accept = True

    if accept:
      recoinfo = {'energy':ntuple.showerRecoE[x],
                  'completeness':ntuple.showerComp[x],
                  'purity':ntuple.showerPurity[x],
                  'process':ntuple.showerProcess[x],
                  'primary':ntuple.showerPrimaryScore[x],
                  'fromneutral':ntuple.showerFromNeutralScore[x],
                  'fromcharged':ntuple.showerFromChargedScore[x],
                  'showerPhScore':ntuple.showerPhScore[x],
                  'showerElScore':ntuple.showerElScore[x],
                  'source':'recoshower',
                  'index':x}
      recoPhotonInfo.append(recoinfo)

  # from tracks
  for x in range(ntuple.nTracks):
    accept = False
    if tracksize_threshold == 0 or ntuple.trackSize[x]>tracksize_threshold:
      if ntuple.trackClassified[x] == 1:
        if ntuple.trackPID[x] == 22:
          if ntuple.trackComp[x]<completeness_threshold:
            continue        
          
            #Extra check to ensure photons deposit in fiducial volume (with a 5 cm margin of error)
          if (ntuple.trackStartPosX[x] > (fiducial["xMin"] + fiducial["photonWidth"])
              and ntuple.trackStartPosX[x] < (fiducial["xMax"] - fiducial["photonWidth"])
              and ntuple.trackStartPosY[x] > (fiducial["yMin"] + fiducial["photonWidth"])
              and ntuple.trackStartPosY[x] < (fiducial["yMax"] - fiducial["photonWidth"])
              and ntuple.trackStartPosZ[x] > (fiducial["zMin"] + fiducial["photonWidth"])
              and ntuple.trackStartPosZ[x] < (fiducial["zMax"] - fiducial["photonWidth"])):
            accept = True
    if accept:
      recoinfo = {'energy':ntuple.trackRecoE[x], # this is not good
                  'completeness':ntuple.trackComp[x],
                  'purity':ntuple.trackPurity[x],
                  'process':ntuple.trackProcess[x],
                  'primary':ntuple.trackPrimaryScore[x],
                  'fromneutral':ntuple.trackFromNeutralScore[x],
                  'fromcharged':ntuple.trackFromChargedScore[x],
                  'showerPhScore':ntuple.trackPhScore[x],
                  'showerElScore':ntuple.trackElScore[x],
                  'source':'recotrack',
                  'index':x}      

  return recoPhotonInfo
