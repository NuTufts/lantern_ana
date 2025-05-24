from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.cuts.fiducial_cuts import fiducial_cut
from lantern_ana.utils import get_true_primary_particle_counts 

@register_cut
def true_nue_CCinc(ntuple, params):
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

    ismc = params.get('ismc',False)
    if not ismc:
        # if not MC data, we automaticall pass it
        return True

    # Get threshold
    # make default
    true_part_cfg = {}
    true_part_cfg['eKE']  = params.get('eKE',30.0)
    true_part_cfg['muKE'] = params.get('muKE',30.0)
    true_part_cfg['piKE'] = params.get('piKE',30.0)
    true_part_cfg['pKE']  = params.get('pKE',60.0)
    true_part_cfg['gKE']  = params.get('gKE',10.0)
    true_part_cfg['xKE']  = params.get('xKE',60.0)
    part_count_params = params.get('part_count_params',true_part_cfg)
    fv_params  = params.get('fv_params',{'width':10.0,'apply_scc':False})
    fv_params['usetruevtx'] = True
    
    pass_fv = fiducial_cut(ntuple,fv_params)
    #print("pass_fv: ",pass_fv)
    if not pass_fv:
        return False

    counts = get_true_primary_particle_counts(ntuple,part_count_params)
    nprim_e = counts.get(11,0) + counts.get(-11,0)
    #print(nprim_mu)
    if nprim_e == 0:
        return False
    
    return True