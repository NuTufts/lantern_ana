# lantern_ana/cuts/muon_track_cuts.py
from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.cuts.fiducial_cuts import fiducial_cut
from lantern_ana.cuts.reco_muon_cuts import has_muon_track

@register_cut
def reco_numu_CCinc(ntuple, params):
    """
    Signal definition for candidated reconstructed numu CC inclusive events
    
    Parameters:
    - ntuple: The event ntuple
    - params: Dictionary with optional parameters:
        - 'fiducial_cut': Parameters for 'fiducial_cut' in lantern.ana.cuts.fiducial_cut
        - 'has_muon_track': Params for 'has_muon_track' in lantern.ana.reco_muon_cuts
        
    Returns:
    - True if all conditions satisfied
    """
    # Get parameters for subcuts
    fv_params  = params.get('fiducial_cut',{'width':10.0,'apply_scc':True,'usetruevtx':False,'useWCvolume':False})
    fv_params['usetruevtx'] = False
    reco_mu_params = params.get('has_muon_track',{})
    apply_goodvertex_truthcut = params.get('apply_goodvertex_truthcut', False)
    vtxDistToTrueCut = params.get('vtxDistToTrueCut',3.0)
    
    if fv_params['useWCvolume']:
        pass_fv = ntuple.vtxIsFiducial==1
    else:
        pass_fv = fiducial_cut(ntuple,fv_params)
    pass_recomu = has_muon_track(ntuple,reco_mu_params)

    pass_goodvertex = ntuple.foundVertex==1 and ntuple.vtxDistToTrue < vtxDistToTrueCut

    pass_event = pass_fv and pass_recomu
    if apply_goodvertex_truthcut and not pass_goodvertex:
        pass_event = False

    return pass_event