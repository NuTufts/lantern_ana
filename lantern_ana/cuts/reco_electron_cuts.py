from lantern_ana.cuts.cut_factory import register_cut

@register_cut
def has_primary_electron(ntuple, params):
    """
    Cut that requires at least one reconstructed primary electron or track be classified as an electron
    
    Parameters:
    - ntuple: The event ntuple
    - params: Dictionary with optional parameters:
        - 'ke_threshold': Minimum kinetic energy in MeV (default: 50)
        
    Returns:
    - True if at least one muon track is found above the threshold, False otherwise
    """
    # Get threshold
    ke_threshold = params.get('ke_threshold', 30.0)
    min_nhits = params.get('min_nhits',20)
    shower_charge_threshold = params.get('shower_charge_threshold',)

    
    # Check if vertex was found
    if not hasattr(ntuple, 'foundVertex') or ntuple.foundVertex != 1:
        return False
    
    """
    # from Matt's repository
    foundElectron = False
    elMaxQ = -1.
    elMaxQProc = -1
    elMaxQConf = -1.
    elMaxQCosTheta = -1.
    elMaxQVtxDist = -1.
    for iS in range(tnue.nShowers):
      if tnue.showerIsSecondary[iS] != 1 and tnue.showerClassified[iS] == 1 and tnue.showerPID[iS] == 11:
        foundElectron = True
        elConf = tnue.showerElScore[iS] - (tnue.showerPhScore[iS] + tnue.showerPiScore[iS])/2.
        if tnue.showerCharge[iS] > elMaxQ:
          elMaxQ = tnue.showerCharge[iS]
          elMaxQProc = tnue.showerProcess[iS]
          elMaxQConf = elConf
          elMaxQCosTheta = tnue.showerCosTheta[iS]
          elMaxQVtxDist = tnue.showerDistToVtx[iS]

    if not foundElectron:
      continue
    """

    # has primary electron shower
    has_prim_electron = False
    prim_idx_list = []
    prim_electron_data = {}
    elMaxQ = -1.0
    elMaxIdx = -1
    for idx in range(ntuple.nShowers):
        # needs to be a minimum of shower hits
        if ntuple.showerNHits[idx]<min_nhits:
            continue
        # needs to be a primary shower
        if ntuple.showerIsSecondary[idx]!=0:
            continue
        # needs to have been run through classifier
        if ntuple.showerClassified[idx]!=1:
            continue
        # highest LArPID score is electron type
        if ntuple.showerPID[idx]!=11:
            continue
        # electron confidence
        elConf = ntuple.showerElScore[idx] - (ntuple.showerPhScore[idx] + ntuple.showerPiScore[idx])/2.0
        # shower charge
        elQ = ntuple.showerCharge[idx]
        elprocess = ntuple.showerProcess[idx]
        elcostheta = ntuple.showerCosTheta[idx]
        elvtxdist  = ntuple.showerDistToVtx[idx]

        if elQ>elMaxQ:
            elMaxIdx = idx
            elMaxQ = elQ


    # Look for muon tracks above threshold
    for i in range(ntuple.nTracks):
        # Check if track was classified and identified as a muon
        if ntuple.trackClassified[i] == 1 and ntuple.trackPID[i] == 13:
            # Check if track energy is above threshold
            if ntuple.trackRecoE[i] >= ke_threshold:
                # Check if track is a primary particle (not secondary)
                if ntuple.trackIsSecondary[i] == 0:
                    return True
    
    # No qualifying muon track found
    return False