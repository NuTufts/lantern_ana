from lantern_ana.cuts.cut_factory import register_cut
from lantern_ana.utils import KE_from_fourmom

from math import abs

def get_true_primary_particle_counts(ntuple,params):
    """
    Count number of each type of true primary particles.
    """
    eKE=params.get('eKE',0.0)
    muKE=params.get('muKE',0.0)
    piKE=params.get('piKE',0.0)
    pKE=params.get('pKE',0.0)
    gKE=params.get('gKE',0.0)
    xKE=params.get('xKE',0.0)

    thresholds={
        11:eKE,
        13:muKE,
        211:piKE,
        2212:pKE,
        22:gKE
    }

    counts = {}

    for i in range( ntuple.nTrueSimParts ):
        pdg = ntuple.trueSimPartPDG[i]
        KEmin = thresholds.get(abs(pdg),xKE)
        ke = KE_from_fourmom( ntuple.trueSimPartPx[i], ntuple.trueSimPartPy[i], 
                              ntuple.trueSimPartPz[i], ntuple.trueSimPartE[i] )
        if ke<KEmin:
            continue

        if pdg>2212:
            pid = 0 # other
        else:
            pid = pdg
        if pid not in counts:
            counts[pid]=0

        counts[pid]+=1

    return counts
        

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

    
        



