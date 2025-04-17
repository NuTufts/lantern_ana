from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.utils import KE_from_fourmom
from lantern_ana.utils import get_true_primary_particle_counts

@register_cut
def isFS_true_CCmu0p0pi(ntuple,params):
    """
    Use the truth to tag the final state as numu CC with primary mu + 0 proton + 0 charged pion + 0 gamma + 0 X

    params:
     - muKE: muon KE threshold (default: 0 MeV)
     - pKE: proton KE threshold (default: 0 MeV)
     - piKE: charged pion KE threshold (default: 0 MeV)
     - gKE: gamma KE threshold (default: 0 MeV)
     - xKE: other charged meson KE threshold (default: 0 MeV)
    """

    counts = get_true_primary_particle_counts( ntuple, params )
    nmu = counts.get(13,0)+counts.get(-13,0)
    np  = counts.get(2212,0)
    npi = counts.get(211,0)+counts.get(-211,0)
    ng  = counts.get(22,0)
    nx  = countgs.get(0,0)

    if nmu==1 and np==0 and npi==0 and ng==0 and nx==0:
        return True
    else:
        return False


@register_cut
def isFS_true_CCmu1p0pi(ntuple,params):
    """
    Use the truth to tag the final state as numu CC with primary mu + 0 proton + 0 charged pion + 0 gamma + 0 X

    params:
     - muKE: muon KE threshold (default: 0 MeV)
     - pKE: proton KE threshold (default: 0 MeV)
     - piKE: charged pion KE threshold (default: 0 MeV)
     - gKE: gamma KE threshold (default: 0 MeV)
     - xKE: other charged meson KE threshold (default: 0 MeV)
    """

    counts = get_true_primary_particle_counts( ntuple, params )
    nmu = counts.get(13,0)+counts.get(-13,0)
    np  = counts.get(2212,0)
    npi = counts.get(211,0)+counts.get(-211,0)
    ng  = counts.get(22,0)
    nx  = counts.get(0,0)

    if nmu==1 and np==1 and npi==0 and ng==0 and nx==0:
        return True
    else:
        return False

@register_cut
def isFS_true_CCmuMp0pi(ntuple,params):
    """
    Use the truth to tag the final state as numu CC with primary mu + 0 proton + 0 charged pion + 0 gamma + 0 X

    params:
     - muKE: muon KE threshold (default: 0 MeV)
     - pKE: proton KE threshold (default: 0 MeV)
     - piKE: charged pion KE threshold (default: 0 MeV)
     - gKE: gamma KE threshold (default: 0 MeV)
     - xKE: other charged meson KE threshold (default: 0 MeV)
    """

    counts = get_true_primary_particle_counts( ntuple, params )
    nmu = counts.get(13,0)+counts.get(-13,0)
    np  = counts.get(2212,0)
    npi = counts.get(211,0)+counts.get(-211,0)
    ng  = counts.get(22,0)
    nx  = counts.get(0,0)

    if nmu==1 and np>1 and npi==0 and ng==0 and nx==0:
        return True
    else:
        return False

@register_cut
def isFS_true_CCmu0p1pi(ntuple,params):
    """
    Use the truth to tag the final state as numu CC with primary mu + 0 proton + 0 charged pion + 0 gamma + 0 X

    params:
     - muKE: muon KE threshold (default: 0 MeV)
     - pKE: proton KE threshold (default: 0 MeV)
     - piKE: charged pion KE threshold (default: 0 MeV)
     - gKE: gamma KE threshold (default: 0 MeV)
     - xKE: other charged meson KE threshold (default: 0 MeV)
    """

    counts = get_true_primary_particle_counts( ntuple, params )
    nmu = counts.get(13,0)+counts.get(-13,0)
    np  = counts.get(2212,0)
    npi = counts.get(211,0)+counts.get(-211,0)
    ng  = counts.get(22,0)
    nx  = counts.get(0,0)

    if nmu==1 and np==0 and npi==0 and ng==0 and nx==0:
        return True
    else:
        return False

    
        



