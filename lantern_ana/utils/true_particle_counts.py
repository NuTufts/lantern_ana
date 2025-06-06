from lantern_ana.utils import KE_from_fourmom

def get_true_primary_particle_counts(ntuple,params):
    """
    Count number of each type of true primary particles.
    Can apply a threshold on the true (relativistic) kinetic energy in MeV.
    Anything that is not a {electron, muon, charged pion, gamma} is labeled by X

    params:
    - eKE: kinetic energy threshold in MeV for primary electrons [default: 0.0 MeV]
    - muKE: kinetic energy threshold in MeV for primary muons [default: 0.0 MeV]
    - pKE: kinetic energy threshold in MeV for primary protons [default: 0.0 MeV]
    - piKE: kinetic energy threshold in MeV for primary pions [default: 0.0 MeV]
    - gKE: kinetic energy threshold in MeV for primary gammas (using initial kinetic energy, not energy deposited) [default: 0.0 MeV]
    - xKE: kinetic energy threshold in MeV for particles that do not include the above [default: 0.0 MeV]
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
    indices = {}

    for i in range( ntuple.nTrueSimParts ):
        if ntuple.trueSimPartProcess[i]!=0:
            # skip none-primary particles
            continue
        
        pdg = ntuple.trueSimPartPDG[i]
        KEmin = thresholds.get(abs(pdg),xKE)
        #print('  ',pdg,': ',ntuple.trueSimPartE[i])
        ke = KE_from_fourmom( ntuple.trueSimPartPx[i], ntuple.trueSimPartPy[i], 
                              ntuple.trueSimPartPz[i], ntuple.trueSimPartE[i] )
        if ke<KEmin:
            continue

        # pass energy threshold

        if pdg>2212:
            pid = 0 # other
        else:
            pid = pdg
        if pid not in counts:
            counts[pid]=0

        counts[pid]+=1

        if pid not in indices:
            indices[pid] = []
        indices[pid].append(i)

    counts['indices'] = indices
    return counts