from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.cuts.fiducial_cuts import fiducial_cut
from lantern_ana.cuts.reco_muon_cuts import has_muon_track
from lantern_ana.utils.get_primary_electron_candidates import get_primary_electron_candidates

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
    el_candidate_cuts = params.get('electron_candidate_quality_cuts',{})

    # dict of info to return downstream
    cutdata = {}

    if debug:
        print(f'[fileid, run, subrun, event]: {ntuple.fileid} {ntuple.run} {ntuple.subrun} {ntuple.event}')

    # has to have a vertex. 
    cutdata['foundvertex'] = ntuple.foundVertex
    if ntuple.foundVertex!=1:
        if debug: print('nue: no vertex')
        return False, cutdata # Cannot calculate quantities below without it. So return False.
    else:
        if debug and ismc: print(f"nue: has vertex. dist2true={ntuple.vtxDistToTrue}")    

    # FV volume cut
    pass_fv = fiducial_cut(ntuple,fv_params)
    if debug: print('nue: pass_fv',pass_fv)

    # get primary electron candidates
    el_candidate_info = get_primary_electron_candidates( ntuple, el_candidate_cuts)

    # has primary electron shower
    has_prim_electron = False
    prim_idx_list = el_candidate_info['idxlist']
    prim_electron_data = el_candidate_info['prongDict']
    elMaxQ = el_candidate_info['elMaxQ']
    elMaxIdx = el_candidate_info['elMaxIdx']
    if elMaxIdx>=0:
        has_prim_electron = True

    # loop over the tracks
    # getting max muon score
    # getting number of tracks above certain KE energy
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
    
    # apply requirements on electron
    pass_has_electron = has_prim_electron
    if debug: 
        print(f'nue: pass_has_electron={pass_has_electron}',flush=True)
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

    # Fill Cut data

    # full cuts
    pass_event = pass_fv and pass_has_electron and pass_electron_confidence and pass_hasmuon and pass_maxmuscore and pass_vtxcosmicfrac
    if debug: print(f'nue: passes all={pass_event}')
    if pass_event:
        return True, cutdata
    
    return False, cutdata
