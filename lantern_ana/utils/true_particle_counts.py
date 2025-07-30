from lantern_ana.utils import KE_from_fourmom

def get_true_primary_particle_counts(ntuple,params):
    """
    Count number of each type of true primary particles.
    Can apply a threshold on the true (relativistic) kinetic energy in MeV.
    Anything that is not a {electron, muon, charged pion, gamma} is labeled by X

    params:
    - eKE: minimum kinetic energy threshold in MeV for primary electrons [default: 0.0 MeV]
    - muKE: minimum kinetic energy threshold in MeV for primary muons [default: 0.0 MeV]
    - pKE: minimum kinetic energy threshold in MeV for primary protons [default: 0.0 MeV]
    - piKE: minimum kinetic energy threshold in MeV for primary pions [default: 0.0 MeV]
    - gKE: minimum kinetic energy threshold in MeV for primary gammas (using initial kinetic energy, not energy deposited) [default: 0.0 MeV]
    - nKE: minimum kinetic energy threshold in MeV for primary neutrons (using initial kinetic energy, not energy deposited) [default: 0.0 MeV]
    - xKE: minimum kinetic energy threshold in MeV for particles that do not include the above [default: 0.0 MeV]

    - eKE_max: maximum kinetic energy threshold in MeV for primary electrons [default: float('inf')]
    - muKE_max: maximum kinetic energy threshold in MeV for primary muons [default: float('inf')]
    - pKE_max: maximum kinetic energy threshold in MeV for primary protons [default: float('inf')]
    - piKE_max: maximum kinetic energy threshold in MeV for primary pions [default: float('inf')]
    - gKE_max: maximum kinetic energy threshold in MeV for primary gammas (using initial kinetic energy, not energy deposited) [default: float('inf')]
    - nKE_max: maximum kinetic energy threshold in MeV for primary neutrons (using initial kinetic energy, not energy deposited) [default: float('inf')]
    - xKE_max: maximum kinetic energy threshold in MeV for particles that do not include the above [default: float('inf')]
    """
    eKE=params.get('eKE',0.0)
    muKE=params.get('muKE',0.0)
    piKE=params.get('piKE',0.0)
    pKE=params.get('pKE',0.0)
    gKE=params.get('gKE',0.0)
    nKE=params.get('nKE',0.0)
    xKE=params.get('xKE',0.0)

    eKE_max=params.get('eKE_max',float('inf'))
    muKE_max=params.get('muKE_max',float('inf'))
    piKE_max=params.get('piKE_max',float('inf'))
    pKE_max=params.get('pKE_max',float('inf'))
    gKE_max=params.get('gKE_max',float('inf'))
    nKE_max=params.get('nKE_max',float('inf'))
    xKE_max=params.get('xKE_max',float('inf'))

    thresholds={
        11: (eKE, eKE_max),
        13: (muKE, muKE_max),
        211: (piKE, piKE_max),
        2212: (pKE, pKE_max),
        2112: (nKE, nKE_max),
        22: (gKE, gKE_max)
    }

    counts = {}
    indices = {}

    for i in range( ntuple.nTrueSimParts ):
        if ntuple.trueSimPartProcess[i]!=0:
            # skip none-primary particles
            continue
        
        pdg = ntuple.trueSimPartPDG[i]
        KEmin, KEmax = thresholds.get(abs(pdg), (xKE, xKE_max))
        #print('  ',pdg,': ',ntuple.trueSimPartE[i])
        ke = KE_from_fourmom( ntuple.trueSimPartPx[i], ntuple.trueSimPartPy[i], 
                              ntuple.trueSimPartPz[i], ntuple.trueSimPartE[i] )
        if ke < KEmin or ke > KEmax:
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

    # separate loop through genie pdgs to check for neutral pions
    for i in range(ntuple.nTruePrimParts):

        pdg = ntuple.truePrimPartPDG[i]

        # Only process neutral pions
        if pdg != 111:
            continue

        if ntuple.truePrimPartProcess[i] != 0: # Skip non-primary neutral pions
            continue  

        if 111 not in counts:
            counts[111] = 0
        counts[111] += 1

        if 111 not in indices:
            indices[111] = []
        indices[111].append(i)


    counts['indices'] = indices
    return counts