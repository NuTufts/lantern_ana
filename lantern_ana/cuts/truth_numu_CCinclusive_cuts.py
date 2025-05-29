# lantern_ana/cuts/muon_track_cuts.py
from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.cuts.fiducial_cuts import fiducial_cut
from lantern_ana.utils import get_true_primary_particle_counts 

@register_cut
def true_numu_CCinc(ntuple, params):
    """
    Signal definition for true numu CC inclusive event
    
    Parameters:
    - ntuple: The event ntuple
    - params: Dictionary with optional parameters:
        - 'part_count_params': Parameters for primary particle counter
        - 'fv_params': Params for fiducial volume cut
        
    Returns:
    - True if all conditions satisfied
    """
    if params['ismc']==False:
        # if not MC, just pass the event
        return True

    # Get threshold
    part_count_params = params.get('part_count_params',{})
    fv_params  = params.get('fv_params',{'width':10.0,'apply_scc':False})
    fv_params['usetruevtx'] = True
    
    pass_fv = fiducial_cut(ntuple,fv_params)
    #print("pass_fv: ",pass_fv)
    if not pass_fv:
        return False

    counts = get_true_primary_particle_counts(ntuple,part_count_params)
    nprim_mu = counts.get(13,0) + counts.get(-13,0)
    #print(nprim_mu)
    if nprim_mu == 0:
        return False
    
    return True