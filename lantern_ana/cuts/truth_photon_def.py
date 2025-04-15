

def truePhotonList(ntuple, fiducial, threshold=5.0, vtx_radius=1.0):
  #Uses truth to create a list of photons that pass the vertex and deposit tests
  list1 = []
  secondaryList = []
  primList = []
  genie_primaries = []
  photonTrackIDs = []
  for i in range(ntuple.nTruePrimParts):
      genie_primaries.append( ntuple.truePrimPartPDG[i] )
      
  for x in range(ntuple.nTrueSimParts):
    if ntuple.trueSimPartTID[x] == ntuple.trueSimPartMID[x]:
      primList.append(ntuple.trueSimPartTID[x])
  #print("genie pdgs: ",genie_primaries)
  #print("primList: ",primList)
  
  for x in range(ntuple.nTrueSimParts):
    if ntuple.trueSimPartPDG[x] == 22:
      if ntuple.trueSimPartMID[x] in primList:
        secondaryList.append(x)
      elif (abs(ntuple.trueSimPartX[x] - ntuple.trueVtxX) <= vtx_radius
            and abs(ntuple.trueSimPartY[x] - ntuple.trueVtxY) <= vtx_radius
            and abs(ntuple.trueSimPartZ[x] - ntuple.trueVtxZ) <= vtx_radius):
        secondaryList.append(x)
        photonTrackIDs.append( (ntuple.trueSimPartTID[x],x) )
  #print('photon (trackid,index): ',photonTrackIDs)
  
  for x in secondaryList:
    if ( ntuple.trueSimPartEDepX[x] > (fiducial["xMin"] + fiducial["photonWidth"])
         and ntuple.trueSimPartEDepX[x] < (fiducial["xMax"] - fiducial["photonWidth"])
         and ntuple.trueSimPartEDepY[x] > (fiducial["yMin"] + fiducial["photonWidth"])
         and ntuple.trueSimPartEDepY[x] < (fiducial["yMax"] - fiducial["photonWidth"])
         and ntuple.trueSimPartEDepZ[x] > (fiducial["zMin"] + fiducial["photonWidth"])
         and ntuple.trueSimPartEDepZ[x] < (fiducial["zMax"] - fiducial["photonWidth"]) ):
        #print('edep pos: ',ntuple.trueSimPartEDepX[x],',',ntuple.trueSimPartEDepY[x],',',ntuple.trueSimPartEDepZ[x],')')        
        pixelList = [ntuple.trueSimPartPixelSumUplane[x],
                     ntuple.trueSimPartPixelSumVplane[x],
                     ntuple.trueSimPartPixelSumYplane[x]]
        #print('edep: ',pixelList)
        nplanes = 0
        for pixsum in pixelList:
          if pixsum*0.0126>=threshold:
              nplanes += 1
        #print('nplanes: ',nplanes)
        if nplanes>=2:
            list1.append(x)

  return list1,photonTrackIDs