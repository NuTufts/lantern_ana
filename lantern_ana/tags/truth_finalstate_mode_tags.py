from lantern_ana.tags.tag_factory import register_tag
from lantern_ana.utils import get_true_primary_particle_counts

@register_tag
def tag_truth_finalstate_mode(ntuple,params):
    """
    Tag event by 

    params:
     - muKE: muon KE threshold (default: 0 MeV)
     - pKE: proton KE threshold (default: 0 MeV)
     - piKE: charged pion KE threshold (default: 0 MeV)
     - gKE: gamma KE threshold (default: 0 MeV)
     - xKE: other charged meson KE threshold (default: 0 MeV)
     - ignore_gammas: do not consider gamma count (default: False)
     - condense_nuemodes: use inclusive nue tags (default: True)
     - condense_numumodes: use inclusive numu tag (default: False)
     - condense_ncmodes: use inclusive NC tag (default: True)
    """

    counts = get_true_primary_particle_counts( ntuple, params )
    nmu = counts.get(13,0)+counts.get(-13,0)
    ne  = counts.get(11,0)+counts.get(-11,0)
    np  = min(counts.get(2212,0),2)
    npi = min(counts.get(211,0)+counts.get(-211,0),2)
    ng  = counts.get(22,0)
    nx  = counts.get(0,0)
    condense_ncmodes = params.get('condense_ncmodes',True)
    condense_nuemodes = params.get('condense_nuemodes',True)
    condense_numumodes = params.get('condense_numumodes',False)
    ignore_gammas = params.get('ignore_gammas',False)

    if ntuple.trueNuCCNC==0:
        ccnc = "CC"
    else:
        ccnc = "NC"

    # assemble tags
    tag=""
    if abs(ntuple.trueNuPDG)==12:
        tag="nue"
    elif abs(ntuple.trueNuPDG)==14:
        tag="numu"
    elif abs(ntuple.trueNuPDG)==16:
        tag="nutau"
    
    tag += ccnc

    if ntuple.trueNuCCNC==1 and not condense_ncmodes:
        tag += f'{np}p{npi}pi'
        if not ignore_gammas:
            tag += f'{ng}g'
        tag += f'{nx}x'
    elif ntuple.trueNuCCNC==0:
        # CC
        if abs(ntuple.trueNuPDG)==12 and not condense_nuemodes:
            tag += f'{np}p{npi}pi'
            if not ignore_gammas:
                tag += f'{ng}g'
            tag += f'{nx}x'
        elif abs(ntuple.trueNuPDG)==14 and not condense_numumodes:
            tag += f'{np}p{npi}pi'
            if not ignore_gammas:
                tag += f'{ng}g'
            tag += f'{nx}x'

    tag = tag.replace('2','M')

    return tag



