# Lantern Photon Analysis

These lantern_ana configs and plotting scripts are for developing the Lantern photon search.

Our target are 1-photon producing interactions in the MicroBooNE detector.

## Signal Defintions

Inclusive 1g+X:

* only 1 detectable photon inside the TPC FV. A detectable photon is one where the mininum cluster of ionization produced by a photon is at least 5 MeV. We use truth-backtracking to search for 3D clusters of ionization. We then project back to the pixels in the 3 planes and sum the image pixel values for the 3D cluster. We then convert the pixel sum into an MeV value. There must be > 5 MeV in 2 out of 3 planes.

1g+0X (MiniBooNE-like):

* This is a subset of the Inclusive 1g+X sample and so must pass the criteria above.
* We also require that all particles fall below the Cherenkov threshold in MiniBooNE (mineral oil)
    * muons: 150 MeV
    * protons: X MeV
    * electrons: 1 MeV
    * pions: 150 MeV