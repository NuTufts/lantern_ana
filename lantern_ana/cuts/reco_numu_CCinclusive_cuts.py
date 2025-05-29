# lantern_ana/cuts/muon_track_cuts.py
from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.cuts.fiducial_cuts import fiducial_cut
from lantern_ana.cuts.reco_muon_cuts import has_muon_track
from lantern_ana.utils.get_primary_electron_candidates import get_primary_electron_candidates
from math import exp,sqrt

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
    ismc = params.get('ismc',False)
            
    # info to return for study
    cutdata = {
        'vtx_found/I'              : ntuple.foundVertex,
        'vtx_infiducial/I'         : ntuple.vtxIsFiducial,
        'vtx_cosmicfrac/F'         : ntuple.vtxFracHitsOnCosmic,
        'has_primary_electron/I'   : 0,
        'emax_primary_score/F'     : 0.0, 
        'emax_purity/F'            : 0.0,
        'emax_completeness/F'      : 0.0,
        'emax_fromneutral_score/F' : 0.0,
        'emax_fromcharged_score/F' : 0.0,
        'emax_charge/F'            : 0.0,
        'emax_econfidence/F'       : 0.0,     
        'emax_fromdwall/F'         : 0.0,
        'emax_nplaneabove/I'       : 0,
        'emax_el_normedscore/F'    : 0.0,
        'emax_fromshower/I'        : -1,
        'max_muscore/F'            : -20.0,
        'max_mucharge/F'           : 0.0,
        'nMuTracks/I'              : 0
    }
    # need cosmic vertex variable

    if ntuple.foundVertex==0:
        return False,cutdata

    # Fiducial volume: can define boundary or use WC volume
    if fv_params['useWCvolume']:
        pass_fv = ntuple.vtxIsFiducial==1
    else:
        pass_fv = fiducial_cut(ntuple,fv_params)
    

    # get primary electron candidates
    el_candidate_cuts = params.get('electron_candidate_quality_cuts',{})
    el_candidate_info = get_primary_electron_candidates( ntuple, el_candidate_cuts)

    # has primary electron shower
    prim_electron_data = el_candidate_info['prongDict']
    elMaxIdx = el_candidate_info['elMaxIdx']
    pass_no_prim_electron = elMaxIdx<0

    # look for muon primary
    maxMuScore = -20.0
    maxMuQ     = 0.0
    maxmu_idx = -1
    nMuTracks = 0
    for iT in range(ntuple.nTracks):

        # look for muons
        if ntuple.trackIsSecondary[iT] !=0 or ntuple.trackClassified[iT] != 1:
            continue

        if abs(ntuple.trackPID[iT]) == 13:
            nMuTracks += 1
        if ntuple.trackMuScore[iT] > maxMuScore:
            maxMuScore = ntuple.trackMuScore[iT]
            maxmu_idx = iT
            maxMuQ = ntuple.trackCharge[iT]

    pass_has_muon = maxMuScore>-3.7
    
    if ismc:
        if apply_goodvertex_truthcut:
            # if goodvertex cut is to be applied, we evaluate it
            pass_goodvertex = ntuple.foundVertex==1 and ntuple.vtxDistToTrue < vtxDistToTrueCut
        else:
            # if not to be applied, we just auto-pass this cut
            pass_goodvertex = True
    else:
        # if not MC, but data, just pass this cut
        pass_goodvertex = True

    pass_event = pass_fv and pass_no_prim_electron and pass_has_muon and pass_goodvertex

    # fill cut data
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

        cutdata['has_primary_electron/I']   = 1
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

    cutdata['max_muscore/F']    = maxMuScore
    cutdata['max_mucharge/F']   = maxMuQ
    cutdata['nMuTracks/I']      = nMuTracks
    
    return pass_event, cutdata