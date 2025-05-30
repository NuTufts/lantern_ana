import os,sys

def get_primary_muon_candidates( ntuple, params ):
    """
    Get a list of possible primary muon candidates.
    Parameters provide options for setting certain quality cuts.
    We also return some summary information for the set of possible candidates.
    """

    # has primary muon shower
    prim_muon_idx_list = []
    prim_muon_data = {}

    # we will return info about the largest primary shower classified as an muon
    muMaxQ = -1.0
    muMaxIdx = -1

    # quality cuts
    min_charge = params.get('min_charge',0.0)
    min_completeness = params.get('min_completeness',0.0)
    min_purity = params.get('min_purity',0.0)

    # # check the showers
    # for idx in range(ntuple.nShowers):
    #     # needs to be a primary shower
    #     if ntuple.showerIsSecondary[idx]!=0:
    #         continue
    #     # needs to have been run through LArPID classifier
    #     if ntuple.showerClassified[idx]!=1:
    #         continue
    #     # highest LArPID score is muon type
    #     larpid = abs(ntuple.showerPID[idx])
    #     if larpid not in [11,22]:
    #         # accept as shower
    #         continue

    #     shower_is_muon = False
    #     if ntuple.showerElScore[idx]>ntuple.showerPhScore[idx]:
    #         shower_is_muon = True

    #     # muon confidence
    #     elConf = ntuple.showerElScore[idx] - (ntuple.showerPhScore[idx] + ntuple.showerPiScore[idx])/2.0
    #     # shower charge
    #     elQ = ntuple.showerCharge[idx]
    #     # purity and completeness
    #     elPurity = ntuple.showerPurity[idx]
    #     elComp   = ntuple.showerComp[idx]

    #     # apply quality cuts
    #     if elQ<min_charge:
    #         continue
    #     if elPurity<min_purity:
    #         continue
    #     if elComp<min_completeness:
    #         continue

    #     # process index
    #     elprocess = ntuple.showerProcess[idx]
    #     elcostheta = ntuple.showerCosTheta[idx]
    #     elvtxdist  = ntuple.showerDistToVtx[idx]
    #     prim_muon_data[idx] = {
    #         'showerQ':elQ,
    #         'process':elprocess,
    #         'costheta':elcostheta,
    #         'vtxdist':elvtxdist,
    #         'elconfidence':elConf,
    #         'larpid':larpid,
    #         'larpid[muon]':ntuple.showerElScore[idx],
    #         'larpid[photon]':ntuple.showerPhScore[idx],
    #         'larpid[pion]':ntuple.showerPiScore[idx],
    #         'larpid[muon]':ntuple.showerMuScore[idx],
    #         'larpid[proton]':ntuple.showerPrScore[idx],
    #         'purity':ntuple.showerPurity[idx],
    #         'completeness':ntuple.showerComp[idx],
    #         'primary':ntuple.showerPrimaryScore[idx],
    #         'fromNeutralPrimary':ntuple.showerFromNeutralScore[idx],
    #         'fromChargedPrimary':ntuple.showerFromChargedScore[idx]
    #     }
    #     prim_muon_idx_list.append(idx)

    #     # check if this is the largest shower
    #     if elQ > shMaxQ:
    #         shMaxQ = elQ
    #         shMaxIdx = idx

    #     # record the max shower
    #     if shower_is_muon and elQ>elMaxQ:
    #         elMaxIdx = idx
    #         elMaxQ = elQ
    
     # check the tracks
    for idx in range(ntuple.nTracks):
        # needs to be a primary track
        if ntuple.trackIsSecondary[idx]!=0:
            continue
        # needs to have been run through LArPID classifier
        if ntuple.trackClassified[idx]!=1:
            continue
        # highest LArPID score is muon type
        larpid = abs(ntuple.trackPID[idx])
        if larpid not in [13]:
            # accept as mu-like track
            continue
        # track charge
        muQ = ntuple.trackCharge[idx]
        # purity and completeness
        muPurity = ntuple.trackPurity[idx]
        muComp   = ntuple.trackComp[idx]

        # apply quality cuts
        if muQ<min_charge:
            continue
        if muPurity<min_purity:
            continue
        if muComp<min_completeness:
            continue

        # process index
        muprocess = ntuple.trackProcess[idx]
        mucostheta = ntuple.trackCosTheta[idx]
        muvtxdist  = ntuple.trackDistToVtx[idx]
        prim_muon_data[idx] = {
            'showerQ': muQ,
            'process': muprocess,
            'costheta':mucostheta,
            'vtxdist': muvtxdist,
            'larpid':larpid,
            'larpid[electron]':ntuple.trackElScore[idx],
            'larpid[photon]':ntuple.trackPhScore[idx],
            'larpid[pion]':ntuple.trackPiScore[idx],
            'larpid[muon]':ntuple.trackMuScore[idx],
            'larpid[proton]':ntuple.trackPrScore[idx],
            'purity':ntuple.trackPurity[idx],
            'completeness':ntuple.trackComp[idx],
            'primary':ntuple.trackPrimaryScore[idx],
            'fromNeutralPrimary':ntuple.trackFromNeutralScore[idx],
            'fromChargedPrimary':ntuple.trackFromChargedScore[idx]
        }
        prim_muon_idx_list.append(idx)

        # check if this is the largest track
        if muQ>muMaxQ:
            muMaxIdx = idx
            muMaxQ = muQ


    # output
    output = {
        'idxlist':prim_muon_idx_list,
        'prongDict':prim_muon_data,
        'muMaxIdx':muMaxIdx,
        'muMaxQ':muMaxQ
    }
    return output
