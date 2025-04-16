# lantern_ana/cuts/muon_track_cuts.py
from lantern_ana.cuts.cut_factory import register_cut

@register_cut
def has_muon_track(ntuple, params):
    """
    Cut that requires at least one reconstructed primary track identified as a muon
    with kinetic energy above a specified threshold.
    
    Parameters:
    - ntuple: The event ntuple
    - params: Dictionary with optional parameters:
        - 'ke_threshold': Minimum kinetic energy in MeV (default: 50)
        
    Returns:
    - True if at least one muon track is found above the threshold, False otherwise
    """
    # Get threshold
    ke_threshold = params.get('ke_threshold', 50.0)
    
    # Check if vertex was found
    if not hasattr(ntuple, 'foundVertex') or ntuple.foundVertex != 1:
        return False
    
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

