from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.cuts.fiducial_cuts import fiducial_cut
from lantern_ana.cuts.reco_muon_cuts import has_muon_track
from lantern_ana.utils.get_primary_electron_candidates import get_primary_electron_candidates
from math import exp, sqrt

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
    elconfidence_cut = params.get('min_electron_confidence',0.0) # lower until we tune
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
    maxMuQ     = 0.0
    maxmu_idx = -1
    num_tracks_above_threshold = 0
    nMuTracks = 0
    for iT in range(ntuple.nTracks):

        # count number of primaries above some length
        if ntuple.trackIsSecondary[iT]==0:
            # primary cut
            if ntuple.trackRecoE[iT]>25.0:
                num_tracks_above_threshold += 1

        # look for muons
        if ntuple.trackIsSecondary[iT] !=0 or ntuple.trackClassified[iT] != 1:
            continue

        if abs(ntuple.trackPID[iT]) == 13:
            nMuTracks += 1
        if ntuple.trackMuScore[iT] > maxMuScore:
            maxMuScore = ntuple.trackMuScore[iT]
            maxmu_idx = iT
            maxMuQ = ntuple.trackCharge[iT]

    
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

    pass_hasmuon = nMuTracks>0
    pass_maxmuscore = nMuTracks>1 and maxMuScore<maxmuscore_cut
    if debug: 
        print(f'nue: pass_hasmuon={pass_hasmuon} nMuTracks={nMuTracks}')
        print(f'nue: pass_maxmuscore={pass_maxmuscore} score={maxMuScore} num_tracks={num_tracks_above_threshold}')

    # vertex cosmic fraction
    vtxcosmicfrac = ntuple.vtxFracHitsOnCosmic
    pass_vtxcosmicfrac = vtxcosmicfrac<vtxcosmicfrac_cut
    if debug: print(f'nue: pass_vtxcosmicfrac={pass_vtxcosmicfrac} frac={vtxcosmicfrac}')

    # For debug
    pass_goodvertex = ismc and ntuple.foundVertex==1 and ntuple.vtxDistToTrue < vtxDistToTrueCut

    # must pass everything
    pass_event = pass_fv and pass_has_electron

    if ismc and apply_goodvertex_truthcut and not pass_goodvertex:
        pass_event = False

    # Fill Cut data
    if ntuple.foundVertex==1:
        cutdata['vtx_kpscore/F']    = ntuple.vtxScore
        cutdata['vtx_dwall/F']      = 0.0
        cutdata['vtx_cosmicfrac/F'] = ntuple.vtxFracHitsOnCosmic
        if ismc:
            cutdata['mc_dist2true/F'] = ntuple.vtxDistToTrue
        else:
            cutdata['mc_dist2true/F'] = 10000.0
    else:
        cutdata['vtx_kpscore/F'] = 0.0
        cutdata['vtx_dwall/F'] = 0.0
        cutdata['vtx_cosmicfrac/F'] = 0.0
        cutdata['mc_dist2true/F'] = 10000.0


    if elMaxIdx>=0:
        emaxdata = prim_electron_data[elMaxIdx]
        spid = [ emaxdata['larpid[electron]'],
            emaxdata['larpid[photon]'],
            emaxdata['larpid[pion]'],
            emaxdata['larpid[muon]'],
            emaxdata['larpid[proton]']
        ]
        elnormscore = exp(spid[0])/(exp(spid[0])+exp(spid[1])+exp(spid[2])+exp(spid[3])+exp(spid[4]))
        
        ptype = [exp(emaxdata['primary']),exp(emaxdata['fromNeutralPrimary']),exp(emaxdata['fromChargedPrimary'])]
        pnorm = ptype[0]+ptype[1]+ptype[2]

        cutdata['emax_primary_score/F']     = ptype[0]/pnorm
        cutdata['emax_purity/F']            = emaxdata['purity']
        cutdata['emax_completeness/F']      = emaxdata['completeness']
        cutdata['emax_fromneutral_score/F'] = ptype[1]/pnorm
        cutdata['emax_fromcharged_score/F'] = ptype[2]/pnorm
        cutdata['emax_charge/F']            = emaxdata['showerQ']
        cutdata['emax_econfidence/F']       = emaxdata['elconfidence']       
        cutdata['emax_fromdwall/F']         = 0.0
        cutdata['emax_nplaneabove/I']       = 0
        cutdata['emax_el_normedscore/F']    = elnormscore
        if elMaxIdx>=100:
            cutdata['emax_fromshower/I'] = 0
        else:
            cutdata['emax_fromshower/I'] = 1
    else:
        cutdata['emax_primary_score/F'] = 0.0
        cutdata['emax_purity/F'] = 0.0
        cutdata['emax_completeness/F'] = 0.0
        cutdata['emax_fromneutral_score/F'] = 0.0
        cutdata['emax_fromcharged_score/F'] = 0.0
        cutdata['emax_charge/F'] = 0.0
        cutdata['emax_econfidence/F'] = 0.0
        cutdata['emax_fromdwall/F'] = 0.0
        cutdata['emax_el_normedscore/F'] = 0.0
        cutdata['emax_nplaneabove/I'] = 0
        cutdata['emax_el_normedscore/F'] = 0.0
        cutdata['emax_fromshower/I'] = 0


    cutdata['max_muscore/F']    = maxMuScore
    cutdata['max_mucharge/F']   = maxMuQ
    cutdata['ntracks_above/I']  = num_tracks_above_threshold
    cutdata['nMuTracks/I']      = nMuTracks

    # full cuts
    pass_event = pass_fv and pass_has_electron
    if debug: print(f'nue: passes all={pass_event}')
    if pass_event:
        return True, cutdata
    
    return False, cutdata


@register_cut
def reco_nue_ccinclusive_gen2val_cuts( ntuple, params ):
    """
    Direct reproduction of Matthew Rosenberg's nue inclusive cc nue selection.
    https://github.com/NuTufts/gen2val/blob/main/plot_CCinclusive_selections_efficiency_and_purity_makeHists.cpp#L26C1-L64C4
    """

    pass_vertex = False
    pass_frac_on_cosmics = False
    pass_no_muon = False
    pass_has_primary_electron = False
    pass_not_mulike = False
    pass_confPrimEl = False
    pass_CCnue = False

    cut_data = {
        'foundVertex':ntuple.foundVertex,
        'vtxIsFiducial':ntuple.vtxIsFiducial,
        'vtxFracHitsOnCosmics':ntuple.vtxFracHitsOnCosmic,
        'pass_vertex':pass_vertex,
        'pass_frac_on_cosmics':pass_frac_on_cosmics,
        'pass_no_muon':pass_no_muon,
        'pass_has_primary_electron':pass_has_primary_electron,
        'pass_not_mulike':pass_not_mulike,
        'pass_confPrimEl':pass_confPrimEl,
        'pass_CCnue':pass_CCnue
    }

    if ntuple.foundVertex==1 and ntuple.vtxIsFiducial==1:
        pass_vertex = True

    # if not vertex, cannot evaluate downstream cuts
    if pass_vertex==False:
        return False, cut_data

    if ntuple.vtxFracHitsOnCosmic < (1. - 1e-6):
        pass_frac_on_cosmics = True

    nMuons = 0
    maxMuScore = -99.
    for iT in range(ntuple.nTracks):
        if ntuple.trackIsSecondary[iT]== 1 or ntuple.trackClassified[iT] != 1:
            continue
        if ntuple.trackPID[iT]== 13:
            nMuons += 1
        if ntuple.trackMuScore[iT] > maxMuScore:
            maxMuScore = ntuple.trackMuScore[iT]

    if nMuons==0:
        pass_no_muon = True

    #if nMuons == 0 and maxMuScore < -3.7:
    #    pass_no_muon = True

    nElectrons = 0
    elMaxQ = -99.
    elMaxQConf = -9.
    elMaxQProc = -1
    for iS in range( ntuple.nShowers ):
        if ntuple.showerIsSecondary[iS] == 1 or ntuple.showerClassified[iS] != 1:
            continue

        if ntuple.showerPID[iS] == 11:
            nElectrons += 1
            if ntuple.showerCharge[iS] > elMaxQ:
                elMaxQ = ntuple.showerCharge[iS]
                elMaxQProc = ntuple.showerProcess[iS]
                elMaxQConf = ntuple.showerElScore[iS] - (ntuple.showerPhScore[iS] + ntuple.showerPiScore[iS])/2.0

    if nMuons==0 and nElectrons>=1 and elMaxQProc == 0:
        pass_has_primary_electron = True

    if pass_has_primary_electron and maxMuScore < -3.7:
        pass_not_mulike = True

    if pass_not_mulike and elMaxQConf > 7.1:
        pass_confPrimEl = True 
        pass_CCnue = True

    #if not pass_not_mulike:
    #    pass_CCnumu = True

    cut_data['pass_vertex'] = pass_vertex
    cut_data['pass_frac_on_cosmics'] = pass_frac_on_cosmics
    cut_data['pass_no_muon'] = pass_no_muon
    cut_data['pass_has_primary_electron'] = pass_has_primary_electron
    cut_data['pass_not_mulike'] = pass_not_mulike
    cut_data['pass_confPrimEl'] = pass_confPrimEl
    cut_data['pass_CCnue'] = pass_CCnue
    cut_data['nMuons'] = nMuons
    cut_data['nElectrons'] = nElectrons
    cut_data['elMaxQ'] = elMaxQ
    cut_data['maxMuScore'] = maxMuScore
    cut_data['elMaxQConf'] = elMaxQConf
    cut_data['elMaxQProc'] = elMaxQProc

    return pass_CCnue, cut_data