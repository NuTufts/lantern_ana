from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.cuts.fiducial_cuts import fiducial_cut

@register_cut
def reco_nue_CCinc(ntuple, params):
    """
    Signal definition for reconstructed nue CC inclusive events.
    
    This version uses producer outputs.
    Cuts only make selection decisions based on pre-calculated values.
    
    Parameters:
    - ntuple: The event ntuple
    - params: Dictionary with parameters:
        - 'producer_data': Dictionary containing producer outputs
        - 'fiducial_cut': Parameters for fiducial volume cut
        - Various threshold parameters for selection
        
    Returns:
    - Boolean: True if event passes all cuts
    """
    
    # Extract producer data
    producer_data = params.get('producer_data', {})
    vertex_data = producer_data.get('vertex_properties', {})
    electron_data = producer_data.get('recoElectron', {})
    muon_data = producer_data.get('recoMuonTrack', {})
    
    # Get cut parameters
    fv_params = params.get('fv_params', {'width': 10.0, 'apply_scc': True, 'usetruevtx': False})
    fv_params['usetruevtx'] = False
    
    elconfidence_cut = params.get('min_electron_confidence', 0.0)
    maxmuscore_cut = params.get('max_muscore', -3.7)
    vtxcosmicfrac_cut = params.get('min_vtx_cosmic_fraction', 1.0)
    debug = params.get('debug', False)
    apply_goodvertex_truthcut = params.get('apply_goodvertex_truthcut', False)
    vtxDistToTrueCut = params.get('vtxDistToTrueCut', 3.0)
    ismc = params.get('ismc', False)

    if debug:
        print(f'[fileid, run, subrun, event]: {ntuple.fileid} {ntuple.run} {ntuple.subrun} {ntuple.event}')

    # Check if vertex found (from producer data)
    has_vertex = vertex_data.get('found', 0) == 1
    if not has_vertex:
        if debug: print('nue: no vertex')
        return False

    if debug and ismc: 
        dist2true = vertex_data.get('mc_dist2true', 10000.0)
        print(f"nue: has vertex. dist2true={dist2true}")

    # Fiducial volume cut (still uses ntuple directly)
    pass_fv = fiducial_cut(ntuple, fv_params)
    if debug: print('nue: pass_fv', pass_fv)
    if not pass_fv:
        return False

    # Check for primary electron (from producer data)
    has_prim_electron = electron_data.get('has_primary_electron', 0) == 1
    if debug: print(f'nue: pass_has_electron={has_prim_electron}')
    if not has_prim_electron:
        return False

    # Electron confidence cut (from producer data)
    elconfidence = electron_data.get('emax_econfidence', 0.0)
    pass_electron_confidence = elconfidence > elconfidence_cut
    if debug: print(f'nue: pass_electron_confidence={pass_electron_confidence} confidence={elconfidence}')

    # Muon-related cuts (from producer data)
    nMuTracks = muon_data.get('nMuTracks', 0)
    maxMuScore = muon_data.get('max_muscore', -200.0)
    
    pass_hasmuon = nMuTracks > 0
    pass_maxmuscore = nMuTracks > 1 and maxMuScore < maxmuscore_cut
    if debug:
        print(f'nue: pass_hasmuon={pass_hasmuon} nMuTracks={nMuTracks}')
        print(f'nue: pass_maxmuscore={pass_maxmuscore} score={maxMuScore}')

    # Vertex cosmic fraction cut (from producer data)
    vtxcosmicfrac = vertex_data.get('cosmicfrac', 0.0)
    pass_vtxcosmicfrac = vtxcosmicfrac < vtxcosmicfrac_cut
    if debug: print(f'nue: pass_vtxcosmicfrac={pass_vtxcosmicfrac} frac={vtxcosmicfrac}')

    # Good vertex truth cut for MC
    pass_goodvertex = True
    if ismc and apply_goodvertex_truthcut:
        dist2true = vertex_data.get('mc_dist2true', 10000.0)
        pass_goodvertex = dist2true < vtxDistToTrueCut

    # Combine all cuts
    pass_event = (pass_fv and 
                  has_prim_electron and 
                  pass_electron_confidence and
                  pass_vtxcosmicfrac and
                  pass_goodvertex)
    
    if debug: print(f'nue: passes all={pass_event}')
    
    return pass_event


@register_cut
def reco_nue_ccinclusive_gen2val_cuts(ntuple, params):
    """
    Matthew Rosenberg's nue inclusive cc selection.
    Uses producer outputs instead of calculating quantities directly.
    """
    
    # Extract producer data
    producer_data = params.get('producer_data', {})
    vertex_data = producer_data.get('vertex_properties', {})
    electron_data = producer_data.get('recoElectron', {})
    muon_data = producer_data.get('recoMuonTrack', {})
    
    # Check vertex requirements (from producer data)
    foundVertex = vertex_data.get('found', 0)
    vtxIsFiducial = vertex_data.get('infiducial', 0)
    pass_vertex = foundVertex == 1 and vtxIsFiducial == 1
    
    if not pass_vertex:
        return False

    # Check cosmic fraction (from producer data)
    vtxFracHitsOnCosmic = vertex_data.get('cosmicfrac', 1.0)
    pass_frac_on_cosmics = vtxFracHitsOnCosmic < (1.0 - 1e-6)

    # Check muon requirements (from producer data)
    nMuons = muon_data.get('nMuTracks', 0)
    maxMuScore = muon_data.get('max_muscore', -99.0)
    pass_no_muon = nMuons == 0

    # Check electron requirements (from producer data)
    has_primary_electron = electron_data.get('has_primary_electron', 0) == 1
    elMaxQConf = electron_data.get('emax_econfidence', -9.0)
    
    # Combined electron requirements
    pass_has_primary_electron = pass_no_muon and has_primary_electron
    pass_not_mulike = pass_has_primary_electron and maxMuScore < -3.7
    pass_confPrimEl = pass_not_mulike and elMaxQConf > 7.1
    pass_CCnue = pass_confPrimEl

    return pass_CCnue
