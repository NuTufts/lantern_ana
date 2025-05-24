from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.cuts.fiducial_cuts import fiducial_cut
from lantern_ana.cuts.reco_muon_cuts import has_muon_track

@register_cut
def reco_nue_CCinc(ntuple, params):
    """
    Signal definition for candidated reconstructed numu CC inclusive events.

    Building off of Matt R's selection
    https://github.com/mmrosenberg/gen2val/blob/main/plot_selection_test_results_cut_efficiency.py
    1. foundVertex
    2. is in fiducial
    3. vtxFracHitsonCosmic >=1 (strong) 
    4. !foundMuon
    5. foundElectron (does not have to be only 1)
    6. Process==0 (primary)
    7. maxMuScore >= -3.7
    8. electronConfidence <= 7.1 (for max shower)

    
    Parameters:
    - ntuple: The event ntuple
    - params: Dictionary with optional parameters:
        - 'fiducial_cut': Parameters for 'fiducial_cut' in lantern.ana.cuts.fiducial_cut
        - 'has_muon_track': Params for 'has_muon_track' in lantern.ana.reco_muon_cuts
        
    Returns:
    - True if all conditions satisfied

    """
    # Get parameters for subcuts
    fv_params  = params.get('fiducial_cut',{'width':10.0,'apply_scc':True,'usetruevtx':False})
    fv_params['usetruevtx'] = False

    # default for selecting electron
    has_primary_electron_cfg = {
        'has_primary_electron':30.0,
        'min_nhits':20,
    }
    reco_e_params = params.get('has_primary_electron',has_primary_electron_cfg)
    elconfidence_cut = params.get('min_electron_confidence',3.0) # lower until we tune
    maxmuscore_cut = params.get('max_muscore',-3.7) # this is kind of a numuCCpi+ check, maybe we can more judicious about this one
    vtxcosmicfrac_cut = params.get('min_vtx_cosmic_fraction',1.0)
    debug = params.get('debug',False)
    apply_goodvertex_truthcut = params.get('apply_goodvertex_truthcut', False)
    vtxDistToTrueCut = params.get('vtxDistToTrueCut',3.0)
    ismc = params.get('ismc',False)

    if debug:
        print(f'[fileid, run, subrun, event]: {ntuple.fileid} {ntuple.run} {ntuple.subrun} {ntuple.event}')

    # has to have a vertex. 
    if ntuple.foundVertex!=1:
        if debug: print('nue: no vertex')
        return False # Cannot calculate quantities below without it. So return False.
    else:
        if debug and ismc: print(f"nue: has vertex. dist2true={ntuple.vtxDistToTrue}")    

    # FV volume cut
    pass_fv = fiducial_cut(ntuple,fv_params)
    if debug: print('nue: pass_fv',pass_fv)

    # has primary electron shower
    has_prim_electron = False
    prim_idx_list = []
    prim_electron_data = {}
    elMaxQ = -1.0
    elMaxIdx = -1

    # check the showers
    for idx in range(ntuple.nShowers):
        # needs to be a primary shower
        if ntuple.showerIsSecondary[idx]!=0:
            continue
        # needs to have been run through LArPID classifier
        if ntuple.showerClassified[idx]!=1:
            continue
        # highest LArPID score is electron type
        larpid = abs(ntuple.showerPID[idx])
        if larpid not in [11]:
            # accept as shower
            continue
        shower_is_electron = False
        if ntuple.showerElScore[idx]>ntuple.showerPhScore[idx]:
            has_prim_electron = True
            shower_is_electron = True

        # electron confidence
        elConf = ntuple.showerElScore[idx] - (ntuple.showerPhScore[idx] + ntuple.showerPiScore[idx])/2.0
        # shower charge
        elQ = ntuple.showerCharge[idx]
        elprocess = ntuple.showerProcess[idx]
        elcostheta = ntuple.showerCosTheta[idx]
        elvtxdist  = ntuple.showerDistToVtx[idx]
        prim_electron_data[idx] = {
            'showerQ':elQ,
            'process':elprocess,
            'costheta':elcostheta,
            'vtxdist':elvtxdist,
            'elconfidence':elConf,
            'larpid':larpid,
            'larpid[electron]':ntuple.showerElScore[idx],
            'larpid[photon]':ntuple.showerPhScore[idx],
            'parpid[pion]':ntuple.showerPiScore[idx]
        }
        prim_idx_list.append(idx)

        # record the max shower
        if shower_is_electron and elQ>elMaxQ:
            elMaxIdx = idx
            elMaxQ = elQ

    # loop over the tracks
    # remove events with a primary muon
    maxMuScore = -200.0
    maxmu_idx = -1
    foundMuon = False
    num_tracks_above_threshold = 0
    for iT in range(ntuple.nTracks):

        # count number of primaries above some length
        if ntuple.trackIsSecondary[iT]==0:
            # primary cut
            if ntuple.trackRecoE[iT]>25.0:
                num_tracks_above_threshold += 1

        # look for muons
        if ntuple.trackIsSecondary[iT] == 1 or ntuple.trackClassified[iT] != 1:
          continue
        if ntuple.trackMuScore[iT] > maxMuScore:
          maxMuScore = ntuple.trackMuScore[iT]
          maxmu_idx = iT
        if ntuple.trackPID[iT] == 13:
          foundMuon = True

        # look for electron-like stubs
        if ntuple.trackIsSecondary[iT]==0 and ntuple.trackClassified[iT]==1 and abs(ntuple.trackPID[iT])==11:
            # highest LArPID track is electron type
            # electron-like
            elConf = ntuple.trackElScore[iT] - (ntuple.trackPhScore[iT] + ntuple.trackPiScore[iT])/2.0
            # track charge
            elQ = ntuple.trackCharge[iT]
            elprocess = ntuple.trackProcess[iT]
            elcostheta = ntuple.trackCosTheta[iT]
            elvtxdist  = ntuple.trackDistToVtx[iT]
            larpid = abs(ntuple.trackPID[iT])
            prim_electron_data[iT+100] = {
                'showerQ':elQ,
                'process':elprocess,
                'costheta':elcostheta,
                'vtxdist':elvtxdist,
                'elconfidence':elConf,
                'larpid':larpid,
                'larpid[electron]':ntuple.trackElScore[iT],
                'larpid[photon]':ntuple.trackPhScore[iT],
                'parpid[pion]':ntuple.trackPiScore[iT]
            }
            # record the largest primary electron
            if elQ>elMaxQ:
                elMaxIdx = iT+100
                elMaxQ = elQ



    
    # apply requirements on electron
    pass_has_electron = has_prim_electron
    if debug: 
        print(f'nue: pass_has_electron={pass_has_electron}')
        for showeridx in prim_electron_data:
            print(f'  shower[{showeridx}]',flush=True)
            if elMaxIdx==showeridx:
                print('  MAX Q ELECTRON')
            for k in prim_electron_data[showeridx]:
                print('  ',k,": ",prim_electron_data[showeridx][k],flush=True)

    pass_prime_process = True
    pass_electron_confidence = False
    if elMaxIdx>=0:
        maxQ_process = prim_electron_data[elMaxIdx]['process']
        pass_prime_process = prim_electron_data[elMaxIdx]['process']!=2
        if debug: print(f'nue: pass_prime_process={pass_prime_process} process={maxQ_process}')

        pass_electron_confidence = prim_electron_data[elMaxIdx]['elconfidence']>elconfidence_cut
        maxQ_elconf = prim_electron_data[elMaxIdx]['elconfidence']
        if debug: print(f'nue: pass_electron_confidence={pass_electron_confidence} confidence={maxQ_elconf}')

    pass_hasmuon = foundMuon==False
    pass_maxmuscore = (num_tracks_above_threshold>1) or (maxMuScore<maxmuscore_cut)
    if debug: 
        print(f'nue: pass_hasmuon={pass_hasmuon}')
        print(f'nue: pass_maxmuscore={pass_maxmuscore} score={maxMuScore} num_tracks={num_tracks_above_threshold}')

    # vertex cosmic fraction
    vtxcosmicfrac = ntuple.vtxFracHitsOnCosmic
    pass_vtxcosmicfrac = vtxcosmicfrac<vtxcosmicfrac_cut
    if debug: print(f'nue: pass_vtxcosmicfrac={pass_vtxcosmicfrac} frac={vtxcosmicfrac}')

    # For debug
    pass_goodvertex = ismc and ntuple.foundVertex==1 and ntuple.vtxDistToTrue < vtxDistToTrueCut

    # must pass everything
    pass_event = pass_fv and pass_has_electron and pass_electron_confidence and pass_hasmuon and pass_maxmuscore

    if ismc and apply_goodvertex_truthcut and not pass_goodvertex:
        pass_event = False

    
    # full cuts
    #pass_event = pass_fv and pass_has_electron and pass_electron_confidence and pass_hasmuon and pass_maxmuscore and pass_vtxcosmicfrac
    if debug: print(f'nue: passes all={pass_event}')
    if pass_event:
        return True
    
    return False
