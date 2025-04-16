# Lantern Analysis Documentation

## Registered Cut Functions

### fiducial_cuts.py

#### `fiducial_cut(ntuple, params)`

Cut events where the vertex is outside the fiducial volume.

Parameters:
- ntuple: The event ntuple
- params: Dictionary with optional parameters:
    - 'width': Margin from detector edges (default: 10 cm)
    - 'applyscc': Apply Space Charge Correction (default: True)
    
Returns:
- True if the vertex is inside the fiducial volume, False otherwise

### finalstate_mode_defs.py

#### `isFS_true_CCmu0p0pi(ntuple, params)`

Use the truth to tag the final state as numu CC with primary mu + 0 proton + 0 charged pion + 0 gamma + 0 X

params:
 - muKE: muon KE threshold (default: 0 MeV)
 - pKE: proton KE threshold (default: 0 MeV)
 - piKE: charged pion KE threshold (default: 0 MeV)
 - gKE: gamma KE threshold (default: 0 MeV)
 - xKE: other charged meson KE threshold (default: 0 MeV)

#### `isFS_true_CCmu1p0pi(ntuple, params)`

Use the truth to tag the final state as numu CC with primary mu + 0 proton + 0 charged pion + 0 gamma + 0 X

params:
 - muKE: muon KE threshold (default: 0 MeV)
 - pKE: proton KE threshold (default: 0 MeV)
 - piKE: charged pion KE threshold (default: 0 MeV)
 - gKE: gamma KE threshold (default: 0 MeV)
 - xKE: other charged meson KE threshold (default: 0 MeV)

#### `isFS_true_CCmuMp0pi(ntuple, params)`

Use the truth to tag the final state as numu CC with primary mu + 0 proton + 0 charged pion + 0 gamma + 0 X

params:
 - muKE: muon KE threshold (default: 0 MeV)
 - pKE: proton KE threshold (default: 0 MeV)
 - piKE: charged pion KE threshold (default: 0 MeV)
 - gKE: gamma KE threshold (default: 0 MeV)
 - xKE: other charged meson KE threshold (default: 0 MeV)

#### `isFS_true_CCmu0p1pi(ntuple, params)`

Use the truth to tag the final state as numu CC with primary mu + 0 proton + 0 charged pion + 0 gamma + 0 X

params:
 - muKE: muon KE threshold (default: 0 MeV)
 - pKE: proton KE threshold (default: 0 MeV)
 - piKE: charged pion KE threshold (default: 0 MeV)
 - gKE: gamma KE threshold (default: 0 MeV)
 - xKE: other charged meson KE threshold (default: 0 MeV)

### truth_finalstate_mode_tags.py

#### `tag_truth_finalstate_mode(ntuple, params)`

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

## Utility and Helper Functions

### SampleDataset.py

#### `pot()`

No documentation available.

#### `load_from_config(config_dict, input_dir_list)`

No documentation available.

### bookfile_parser.py

#### `make_dict_from_file(bookfile)`

No documentation available.

### boundarytests.py

#### `get_uboone_tpc_bounds()`

No documentation available.

#### `is_inside_tpc(pos)`

Test if inside the canonical uboone TPC boundary

### cut_factory.py

#### `register_cut(func)`

Decorator to register a cut function with the CutFactory.
The function name is used as the cut identifier.

#### `auto_discover_cuts()`

Automatically discover and import all cut modules in the cuts directory.
This allows for automatic registration of decorated cut functions.

#### `list_available_cuts()`

Return a list of all registered cut names.

#### `add_cut(name, params)`

Add a cut to the list to be applied per event.
Store params to be passed to the cut function when run.

Parameters:
- name: Name of the registered cut function to use
- params: Dictionary with parameters to control the cut behavior

#### `apply_cuts(ntuple, return_on_fail)`

Apply all registered cuts in order.

Parameters:
- ntuple: The ntuple tree to run the cuts on
- return_on_fail: If True, return immediately when a cut fails

Returns:
- passes: Boolean indicating if all cuts passed
- results: Dictionary with cut names as keys and results as values

### cuts.py

#### `trueParticleTallies(ntuple)`

No documentation available.

#### `trueCutNC(ntuple, params)`

return true if NC

#### `trueCutMuons(ntuple)`

No documentation available.

#### `trueCutElectrons(ntuple)`

No documentation available.

#### `trueCutPionProton(ntuple)`

No documentation available.

#### `trueCutProtonInclusive(ntuple)`

No documentation available.

#### `trueCutFiducials(ntuple, fiducialData)`

No documentation available.

#### `trueCutBottomlessFiducial(ntuple, fiducialData)`

No documentation available.

#### `trueCutCosmic(ntuple)`

No documentation available.

#### `trueCutPhotons(ntuple)`

No documentation available.

#### `trueCheckPionKaon(ntuple)`

No documentation available.

#### `trueCheckParentTracker(ntuple)`

No documentation available.

#### `trueCutVertex(ntuple)`

No documentation available.

#### `trueCutEDep(ntuple, fiducialInfo)`

No documentation available.

#### `trueBottomlessPhotonList(ntuple, fiducial)`

No documentation available.

#### `trueCutOverlapPhotonList(ntuple, fiducial)`

No documentation available.

#### `trueCutMaxProtons(ntuple)`

No documentation available.

#### `trueTwoPhotonOpeningAngle(eventTree, simpartindex1, simpartindex2)`

No documentation available.

#### `histStack(histName, title, histList, POTSum, axisLabel)`

No documentation available.

#### `histStackDark(title, histList, POTSum, axisLabel)`

No documentation available.

#### `histStackTwoSignal(title, histList, POTSum, POTTarget, beamHist)`

No documentation available.

#### `histStackNoScale(title, histList, POTSum)`

No documentation available.

#### `histStackFill(title, histList, legendTitle, xTitle, yTitle, ntuplePOTSum)`

No documentation available.

#### `sStackFillS(title, hist, kColor, canvasTitle)`

No documentation available.

#### `sStackFillNS(title, hist, kColor, canvasTitle)`

No documentation available.

#### `efficiencyPlot(totalHist, signalHist, ratioHist, title, xTitle)`

No documentation available.

#### `scaleRecoEnergy(ntuple, recoIDs, recoIDs2)`

No documentation available.

#### `scaleTrueEnergy(ntuple, trueIDs)`

No documentation available.

#### `recoNoVertex(ntuple)`

No documentation available.

#### `recoFiducials(ntuple, fiducial)`

No documentation available.

#### `recoBottomlessFiducials(ntuple, fiducial)`

No documentation available.

#### `recoPhotonList(ntuple, threshold)`

No documentation available.

#### `recoPionProton(ntuple)`

No documentation available.

#### `recoProton(ntuple, threshold)`

No documentation available.

#### `recoPion(ntuple, threshold)`

No documentation available.

#### `recoNeutralCurrent(ntuple, threshold)`

No documentation available.

#### `recoCutMuons(ntuple, threshold)`

No documentation available.

#### `recoCutElectrons(ntuple, threshold)`

No documentation available.

#### `recoCutLowEnergy(recoList, ntuple)`

No documentation available.

#### `CCSeeker(ntuple, recoPhotons)`

No documentation available.

#### `recoCutElectronScore(ntuple, recoPhotons, recoPhotons2)`

No documentation available.

#### `recoCutShowerFromChargeScore(ntuple, recoPhotons, recoPhotons2)`

No documentation available.

#### `recoCutShowerfromNeutralScore(ntuple, recoPhotons, recoPhotons2)`

No documentation available.

#### `recoCutMuScore(ntuple, recoPhotons)`

No documentation available.

#### `recoCutCompleteness(ntuple, recoPhotons, recoPhotons2, completeness_threshold)`

No documentation available.

#### `recoCutLongTracks(ntuple, fiducial)`

No documentation available.

#### `recoCutShortTracks(ntuple, threshold)`

No documentation available.

#### `recoCutManyTracks(ntuple, threshold)`

No documentation available.

#### `recoPhotonListFiducial(fiducial, ntuple, threshold)`

No documentation available.

#### `recoCutMaxInTime(ntuple, protonNo)`

No documentation available.

#### `recoPhotonListTracks(fiducial, ntuple, threshold)`

No documentation available.

#### `recoCutMuonCompleteness(eventTree)`

No documentation available.

#### `recoCutPrimary(ntuple, recoPhotons, recoPhotons2)`

No documentation available.

#### `recoCutTrackEnd(ntuple, recoPhotons, recoPhotons2)`

No documentation available.

#### `recoCutFarShowers(ntuple)`

No documentation available.

#### `recoCutOneProton(ntuple)`

No documentation available.

#### `kineticEnergyCalculator(ntuple, i)`

No documentation available.

#### `particleDistancesCalculator(eventTree, i)`

No documentation available.

#### `trueCCCut(eventTree)`

No documentation available.

#### `recoCCCut(eventTree)`

No documentation available.

#### `trueFiducialCut(eventTree, fiducialWidth)`

No documentation available.

#### `recoFiducialCut(eventTree, fiducialWidth)`

No documentation available.

#### `truePiPlusCut(eventTree)`

No documentation available.

#### `recoPiPlusCut(eventTree)`

No documentation available.

#### `trueProtonSelection(eventTree)`

No documentation available.

#### `recoProtonSelection(eventTree)`

No documentation available.

#### `truePhotonSelection(eventTree, fiducialWidth)`

No documentation available.

#### `truePhotonSelectionPiZero(eventTree, fiducialWidth)`

No documentation available.

#### `truePhotonSelectionOldNtuple(eventTree, fiducialWidth)`

No documentation available.

#### `recoPhotonSelection(eventTree, fiducialWidth)`

No documentation available.

#### `recoPhotonSelectionInvMass(eventTree, fiducialWidth)`

No documentation available.

#### `trueCCCutLoose(eventTree)`

No documentation available.

#### `recoCCCutLoose(eventTree)`

No documentation available.

#### `trueInvariantMassCalculations(eventTree, pi, truePhotonIndexList)`

No documentation available.

#### `recoInvariantMassCalculations(eventTree, recoProtonIndex, recoPhotonIndexList)`

No documentation available.

### finalstate_mode_defs.py

#### `get_true_primary_particle_counts(ntuple, params)`

Count number of each type of true primary particles.

### fromwall.py

#### `fromwall(start, pdir, fiducial_data, eps)`

No documentation available.

### image2d_cropping.py

#### `crop_around_postion(image2d_v, pos, row_width, col_width, histname)`

No documentation available.

### kinematics.py

#### `KE_from_fourmom(px, py, pz, E)`

No documentation available.

### larflowreco_ana_funcs.py

#### `getFiles(mdlTag, kpsfiles, mdlfiles)`

No documentation available.

#### `inRange(x, bnd)`

No documentation available.

#### `isFiducial(p)`

No documentation available.

#### `isFiducialBig(p)`

No documentation available.

#### `isInDetector(p)`

No documentation available.

#### `isFiducialWCSCE(p)`

No documentation available.

#### `getVertexDistance(pos3v, recoVtx)`

No documentation available.

#### `getTrackLength(track)`

No documentation available.

#### `getDistance(a, b)`

No documentation available.

#### `getDirection(a, b)`

No documentation available.

#### `getCosTVecAngle(a, b)`

No documentation available.

#### `getTVecAngle(a, b)`

No documentation available.

#### `getCosThetaBeamTrack(track)`

No documentation available.

#### `getCosThetaGravTrack(track)`

No documentation available.

#### `getCosThetaBeamShower(showerTrunk)`

No documentation available.

#### `getCosThetaGravShower(showerTrunk)`

No documentation available.

#### `getCosThetaBeamVector(x, y, z)`

No documentation available.

#### `getCosThetaGravVector(x, y, z)`

No documentation available.

#### `getSCECorrectedPos(point, sce)`

No documentation available.

### pionEnergyEstimator.py

#### `Eval(length)`

No documentation available.

### plotmaker.py

#### `load_ntuples()`

No documentation available.

#### `addHist(name, hist_template, fill_var_fn, selection_fn, get_weight_fn)`

No documentation available.

#### `runloop()`

to get variables, 

### reco_photon_def.py

#### `getRecoPhotonList(ntuple, fiducial, showerE_threshold, tracksize_threshold, completeness_threshold)`

No documentation available.

### sampledefs.py

#### `get_sample_info(samplename)`

No documentation available.

### singlephoton_1gXp.py

#### `run_1g1p_reco_selection_cuts(eventTree, classificationThreshold, showerE_threshold, showerFromTrack_sizethreshold, fiducialData, return_on_fail)`

No documentation available.

### singlephoton_truth.py

#### `truthdef_1gamma_cuts(eventTree, photonEDepThreshold, fiducialData, return_on_fail)`

No documentation available.

#### `make_truthtag(eventTree, photoEDepThreshold, fiducialData)`

No documentation available.

### spacecharge.py

#### `apply_sce_correction(pos)`

Remove the space-charge effect using MicroBooNE reverse SCE tool

Parameters:
- pos: reconstructed (x,y,z) position inside the TPC

Returns:
- tuple with (x,y,z) values

### tag_factory.py

#### `register_tag(func)`

Decorator to register a tag function with the tagFactory.
The function name is used as the tag identifier.

#### `auto_discover_tags()`

Automatically discover and import all tag modules in the tags directory.
This allows for automatic registration of decorated tag functions.

#### `list_available_tags()`

Return a list of all registered tag names.

#### `add_tag(name, params)`

Add a tag to the list to be applied per event.
Store params to be passed to the tag function when run.

Parameters:
- name: Name of the registered tag function to use
- params: Dictionary with parameters to control the tag behavior

#### `apply_tags(ntuple)`

Apply all registered tags in order.

Parameters:
- ntuple: The ntuple tree to run the tags on

Returns:
- passes: Boolean indicating if all tags passed
- results: Dictionary with tag names as keys and results as values

### test_sce.py

#### `make_offset_array()`

No documentation available.

### true_particle_counts.py

#### `get_true_primary_particle_counts(ntuple, params)`

Count number of each type of true primary particles.
Can apply a threshold on the true (relativistic) kinetic energy in MeV.
Anything that is not a {electron, muon, charged pion, gamma} is labeled by X

### truth_photon_def.py

#### `truePhotonList(ntuple, fiducial, threshold, vtx_radius)`

No documentation available.

## Tag Definitions

### singlephoton_truth.py

#### `photon_analysis_truthtags`

```python
[
    "outFV:0g",
    "outFV:1g",
    "outFV:2g",
    "outFV:Mg",
    "inFV:0g",
    "inFV:Mg",
    "inFV:1g1mu",
    "inFV:1g1e",
    "inFV:1gNpi",
    "inFV:1g0p",
    "inFV:1g1p",
    "inFV:1gMp",
    "inFV:2g1mu",
    "inFV:2g1e",
    "inFV:2gNpi",
    "inFV:2g0p",
    "inFV:2g1p",
    "inFV:2gMp",
    "other",
]
```

#### `truthdef_MBphotonsinglering_tags`

```python
[
    "outFV:1g",
    "inFV:1g0p",
    "inFV:1g1p",
    "inFV:1gMp",
]
```

### tag_factory.py

#### `tags`

```python
[
]
```

