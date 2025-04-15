
mcc9_v40_bnb_nu_overlay_500k_CV_run3b_paths = {
    "dlmerged_data_dir":"/cluster/tufts/wongjiradlab/larbys/data/mcc9/detvar_highstats/mcc9_v40a_dl_run3b_bnb_nu_overlay_500k_CV/",
    "bookfile":"fileinfo_mcc9_v40a_dl_run3b_bnb_nu_overlay_500k_CV.txt",
    "reco_dir":"/cluster/tufts/wongjiradlabnu/nutufts/data/v3dev_lm_showerkp_retraining/mcc9_v40_bnb_nu_overlay_500k_CV_run3b/larflowreco/ana/",
    "fullname":"mcc9_v40_bnb_nu_overlay_500k_CV_run3b"
}


SAMPLES = {
    "run3_bnbnu":mcc9_v40_bnb_nu_overlay_500k_CV_run3b_paths
}

def get_sample_info( samplename ):
    if samplename in SAMPLES:
        return SAMPLES[samplename]

    samplenames = SAMPLES.keys()
    raise ValueError(f'given samplename={samplename} not in list: {samplenames}')

