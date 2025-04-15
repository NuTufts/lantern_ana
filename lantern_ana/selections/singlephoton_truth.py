import os,sys
from lantern_photon.cuts import *
from lantern_photon.cuts.truth_photon_def import truePhotonList

truthdef_1gamma_category_names = ["vertexFV",
                                  "atLeastOneDetPhoton",
                                  "muonBelowThreshold",
                                  "electronBelowThreshold",
                                  "pionsBelowThreshold",
                                  "protonsBelowThreshold",
                                  "only1Photon"]

photon_analysis_truthtags = ["outFV:0g",
                             "outFV:1g",
                             "outFV:2g",
                             "outFV:Mg",
                             "inFV:0g",
                             "inFV:Mg",
                             "inFV:1g1mu", # 1 det gamma + primary muon above threshold + X
                             "inFV:1g1e",  # 1 det gamma + primary electron above threshold + X
                             "inFV:1gNpi", # 1 det gamma + below threshold e/mu + primary pions above threshold + X
                             "inFV:1g0p",  # 1 det gamma + below threshold e/mu/pi + 0 proton (1g0X)   [photon inclusive signal]
                             "inFV:1g1p",  # 1 det gamma + below threshold e/mu/pi + 1 proton (1g1p)    [photon inclusive signal]
                             "inFV:1gMp",  # 1 det gamma + below threshold e/mu/pi + >=2 protons (1gMp) [photon inclusive signal]
                             "inFV:2g1mu", # 2 det gamma + primary muon above threshold + X
                             "inFV:2g1e",  # 2 det gamma + primary electron above threshold + X
                             "inFV:2gNpi", # 2 det gamma + below threshold e/mu + primary pions above threshold + X
                             "inFV:2g0p",  # 2 det gamma + below threshold e/mu/pi + 0 protons (2g0X)
                             "inFV:2g1p",  # 2 det gamma + below threshold e/mu/pi + 1 protons (2g1p)
                             "inFV:2gMp",  # 2 det gamma + below threshold e/mu/pi + >=2 protons (2gMp)
                             "other"] # catch all, should not fill here

truthdef_MBphotonsinglering_tags = ["outFV:1g",
                                    "inFV:1g0p",
                                    "inFV:1g1p",
                                    "inFV:1gMp"]

def truthdef_1gamma_cuts( eventTree, photonEDepThreshold, fiducialData, return_on_fail=True ):

    passes = True
    truthcuts = {}
    for catname in truthdef_1gamma_category_names:
        truthcuts[catname] = False # default to not-passing
        
    # make placeholder for variables to return from evaluating the cuts
    truthcuts["NEdepPhotons"] = 0
    truthcuts["truePhotonIDs"] = []
    truthcuts["trueOpeningAngle"] = 0.0
    truthcuts["pionCount"] = 0
    truthcuts["protonCount"] = 0

    # count the number of true photons with energy deposits in the TPC
    truePhotonIDs,photonTrackIDs = truePhotonList(eventTree, fiducialData, threshold=photonEDepThreshold)
    nEdepPhotons = len(truePhotonIDs)
    trueOpeningAngle = 0.0
    if nEdepPhotons==2:
        # WC inclusive opening angle acceptance
        trueOpeningAngle = trueTwoPhotonOpeningAngle( eventTree, truePhotonIDs[0], truePhotonIDs[1] )
        if trueOpeningAngle<20.0:
            nEdepPhotons=1
    truthcuts["truePhotonIDs"]=truePhotonIDs
    truthcuts["NEdepPhotons"]=nEdepPhotons
    truthcuts["trueOpeningAngle"]=trueOpeningAngle
    truthcuts['photonIDs']=photonTrackIDs
    

    #Selecting events using truth
    if trueCutFiducials(eventTree, fiducialData) == False:
        passes = False
        if return_on_fail:
            return passes, truthcuts
    else:
        truthcuts["vertexFV"] = True

    if len(truePhotonIDs)==0:
        passes = False
        if return_on_fail:
            return passes, truthcuts
    else:
        truthcuts["atLeastOneDetPhoton"] = True

    if trueCutMuons(eventTree) == False:
        passes = False        
        if return_on_fail:
            return passes, truthcuts
    else:
        truthcuts["muonBelowThreshold"] = True

    if trueCutElectrons(eventTree) == False:
        passes = False        
        if return_on_fail:
            return passes, truthcuts
    else:
        truthcuts["electronBelowThreshold"] = True

    pionCount, protonCount = trueCutPionProton(eventTree)
    truthcuts["pionCount"] = pionCount
    truthcuts["protonCount"] = protonCount
    if pionCount > 0:
        passes = False        
        if return_on_fail:
            return passes,truthcuts
    else:
        truthcuts["pionsBelowThreshold"]=True
        
    if protonCount>1:
        passes = False        
        if return_on_fail:
            return passes,truthcuts
    else:
        truthcuts["protonsBelowThreshold"]=True

    if nEdepPhotons != 1:
        passes = False        
        if return_on_fail:
            return passes, truthcuts
    else:
        truthcuts["only1Photon"]=True
    
    return passes, truthcuts, None

def make_truthtag( eventTree, photoEDepThreshold, fiducialData ):
    
    passall, truthcuts = truthdef_1gamma_cuts( eventTree, photonEDepThreshold, fiducialData, return_on_fail=False )

    Ng = truthcuts["nEdepPhotons"]
    Np = truthcuts["protonCount"]
    Npi = truthcuts["pionCount"]
    
    # outside FV tags
    if not truthcuts["vertexFV"]:
        tag = "outFV:"
        if Ng<2:
            tag += "%dg"%(Ng)
        else:
            tag += "Mg"
        return tag

    # rest are inside FV    
    tag = "inFV:"
    
    # zero photon events
    if Ng==0:
        tag += "0g"
        return tag
    elif Ng>=3:
        tag += "Mg"
        return tag

    # rest are 1 or 2 gamma events
    tag += "%dg"%(Ng)

    if truthcuts["muonBelowThreshold"]==False:
        tag += "1mu"
        return tag
    if truthcuts["electronBelowThreshold"]==False:
        tag += "1e"
        return tag
    if Npi>0:
        tag += "Npi"
        return tag
    
    # now everything has now above threshold muon, electron, or pion
    # just the proton designation is left
    if Np<2:
        tag += "%dp"%(Np)
        return tag
    else:
        tag += "Mp"
        return tag

    # should never return this tag
    return "other"
    
    
