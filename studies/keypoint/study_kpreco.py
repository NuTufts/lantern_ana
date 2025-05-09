import os,sys
import numpy as np
import ROOT as rt
from larlite import larlite
from larcv import larcv
from ublarcvapp import ublarcvapp
from larflow import larflow
import larmatch
from larmatch.data.larmatch_hdf5_writer import LArMatchHDF5Writer

def prepare_hits( iolcv, ioll, input_spacepoint_tree="larmatch" ):

    wcfilter = larflow.reco.KeypointFilterByWCTagger()
    wcfilter.set_verbosity( larcv.msg.kINFO )
    wcfilter.set_input_larmatch_tree_name( input_spacepoint_tree )
    wcfilter.set_output_filteredhits_tree_name( "taggerfilterhit" )
    wcfilter.set_save_rejected_hits( True )
    wcfilter.process_hits( iolcv, ioll )

    return 0

def get_data_dict_from_keypointreco( kpreco ):

    # get the keypoint data
    npts = kpreco.output_pt_v.size()
    kppos = np.zeros( (npts,3) )
    kpavepos = np.zeros( (npts,3) )
    kpmaxscore = np.zeros( npts )
    kpavescore = np.zeros( npts )
    kpnpts = np.zeros( npts, dtype=np.int64 )
    kptype = np.zeros( npts, dtype=np.int64 )
    for ikp in range( npts ):
        kpcluster = kpreco.output_pt_v.at(ikp)
        for v in range(3):
            kppos[ikp,v] = kpcluster.center_pt_v.at(v)
            kpavepos[ikp,v] = kpcluster.center_avg_pt_v.at(v)
        kpmaxscore[ikp] = kpcluster.max_score
        kptype[ikp] = kpcluster._cluster_type

        n = kpcluster.pt_pos_v.size()
        kpnpts[ikp] = n
        ptpos = np.zeros( (n,3) )
        ptscore = np.zeros( n )
        for i in range(n):
            for v in range(3):
                ptpos[i,v] = kpcluster.pt_pos_v.at(i).at(v)
            ptscore[i] = kpcluster.pt_score_v.at(i)
        ptd = np.sum(np.power(ptpos-kpavepos[ikp,:],2),axis=1)
        weight = 1.0/(1.0e-3 + ptd*ptd )
        sumweight = np.sum(weight)
        #print("ptscore")
        #print(ptscore)
        #print("ptd")
        #print(ptd)
        #print("weight")
        #print(weight)
        #print("sumweight")
        #print(sumweight)
        if sumweight>0.0:
            weighted_score = np.sum(weight*ptscore)/sumweight
            kpavescore[ikp] = weighted_score            
        else:
            pass

        
    return {"num_keypoints":npts,
            "pos_fitted":kppos,
            "pos_ave":kpavepos,
            "maxscore":kpmaxscore,
            "avescore":kpavescore,
            "nclusterpts":kpnpts,
            "type":kptype}
    
def reco_nu_keypoints( ioll, _kpreco_nu, input_spacepoint_tree="taggerfilterhit" ):
    _kpreco_nu.clear_output()
    _kpreco_nu.set_verbosity( larcv.msg.kINFO );
    _kpreco_nu.set_input_larmatch_tree_name( input_spacepoint_tree );
    _kpreco_nu.set_sigma( 10.0 );
    _kpreco_nu.set_min_cluster_size(   20, 0 );
    _kpreco_nu.set_keypoint_threshold( 0.2, 0 );
    _kpreco_nu.set_max_dbscan_dist( 0.7 )
    _kpreco_nu.set_min_cluster_size(   10, 1 );
    _kpreco_nu.set_keypoint_threshold( 0.2, 1 );
    _kpreco_nu.set_larmatch_threshold( 0.5 );
    _kpreco_nu.set_output_tree_name( "keypoint" );
    _kpreco_nu.set_keypoint_type( 0 ) #larflow.kNuVertex
    _kpreco_nu.set_lfhit_score_index( 17 )
    _kpreco_nu.process( ioll );

    dataout = get_data_dict_from_keypointreco( _kpreco_nu )
    return dataout
        

def reco_shower_keypoints( ioll, _kpreco_shower, input_spacepoint_tree="taggerfilterhit" ):

    # neutrino interaction shower
    _kpreco_shower.clear_output();
    _kpreco_shower.set_input_larmatch_tree_name( input_spacepoint_tree );
    _kpreco_shower.set_output_tree_name( "keypoint" );
    _kpreco_shower.set_sigma( 10.0 );    
    _kpreco_shower.set_min_cluster_size(   20, 0 );
    _kpreco_shower.set_keypoint_threshold( 0.5, 0 );
    _kpreco_shower.set_min_cluster_size(   10, 1 );    
    _kpreco_shower.set_keypoint_threshold( 0.5, 1 );    
    _kpreco_shower.set_larmatch_threshold( 0.5 );
    _kpreco_shower.set_keypoint_type( 3 );
    _kpreco_shower.set_lfhit_score_index( 20 ); # // (v2 larmatch-minkowski network nu-shower-score index in hit)
    _kpreco_shower.process( ioll );
    #// neutrino+cosmic interaction michel
    _kpreco_shower.clear_output();      
    _kpreco_shower.set_keypoint_type( 4 );
    _kpreco_shower.set_lfhit_score_index( 21 ); # // (v2 larmatch-minkowski network michel-shower-score index in hit)
    _kpreco_shower.process( ioll );
    #// neutrino+cosmic interaction delta
    _kpreco_shower.clear_output();      
    _kpreco_shower.set_keypoint_type( 5 );
    _kpreco_shower.set_lfhit_score_index( 22 ); # // (v2 larmatch-minkowski network delta-shower-score index in hit)
    _kpreco_shower.process( ioll );

    dataout = get_data_dict_from_keypointreco( _kpreco_shower )
    return dataout

def reco_track_keypoints( ioll, _kpreco_track, input_spacepoint_tree="taggerfilterhit" ):

    # neutrino interaction track: we have track starts and ends
    _kpreco_track.clear_output();      
    _kpreco_track.set_input_larmatch_tree_name( input_spacepoint_tree );
    _kpreco_track.set_sigma( 10.0 );    
    _kpreco_track.set_min_cluster_size(   20, 0 );
    _kpreco_track.set_keypoint_threshold( 0.5, 0 );
    _kpreco_track.set_min_cluster_size(   10, 1 );    
    _kpreco_track.set_keypoint_threshold( 0.5, 1 );    
    _kpreco_track.set_larmatch_threshold( 0.5 );
    # neutrino interaction track start
    _kpreco_track.set_output_tree_name( "keypoint" );              
    _kpreco_track.set_keypoint_type( 1 ) # (int)larflow::kTrackStart );
    _kpreco_track.set_lfhit_score_index( 18 ); # // (v2 larmatch-minkowski network track-start-score index in hit)
    _kpreco_track.process( ioll );
    # neutrino interaction track end
    _kpreco_track.clear_output();      
    _kpreco_track.set_output_tree_name( "keypoint" );              
    _kpreco_track.set_keypoint_type( 2 ) # (int)larflow::kTrackEnd );
    _kpreco_track.set_lfhit_score_index( 19 )  # // (v2 larmatch-minkowski network track-end-score index in hit)
    _kpreco_track.process( ioll );

    dataout = get_data_dict_from_keypointreco( _kpreco_track )
    return dataout

def analyze_nu_keypoints( true_nu_pos, nu_kpdata_dict ):

    # for each true kp, we get
    # - closest reco kp
    # - number of pts in closest kp
    # - max score of closest kp
    # - dist to center
    # - dist to ave score loc

    true_nu_metrics = []

    nreco = nu_kpdata_dict["num_keypoints"]
    ireco_good = np.zeros( nreco, dtype=np.int64 ) # which reco keypoints were matched to a true vertex

    reco_dist_center = []
    reco_dist_ave    = []

    for ikp in range(true_nu_pos.shape[0]):
        # loop for now
        # get closest nu keypoint
        truepos = true_nu_pos[ikp,:]
        if nu_kpdata_dict['num_keypoints']>0:
            dpos_center = np.sqrt(np.sum(np.power(nu_kpdata_dict["pos_fitted"]-truepos,2), axis=1 ))
            dpos_ave = np.sqrt(np.sum(np.power(nu_kpdata_dict["pos_ave"]-truepos,2), axis=1 ))
            reco_dist_ave.append( dpos_ave )
            reco_dist_center.append( dpos_center )
            print("truepos: ",truepos)
            print("recopos:")
            print(nu_kpdata_dict["pos_fitted"])
            print(dpos_center)
            closest = np.argmin( dpos_center )            
            print("index of closest reco keypoint: ",closest)            
            true_metrics = {'idx_closest':closest,
                            "dist2fitpos":dpos_center[closest],
                            "dist2avepos":dpos_ave[closest],
                            "nclusterpts":nu_kpdata_dict['nclusterpts'][closest],
                            "avescore":nu_kpdata_dict['avescore'][closest],
                            "maxscore":nu_kpdata_dict['maxscore'][closest]}
        else:
            true_metrics = {'idx_closest':-1,
                            "dist2fitpos":9999.0,
                            "dist2avepos":9999.0,
                            "nclusterpts":0,
                            "avescore":0.0,
                            "maxscore":0.0}
        true_nu_metrics.append( true_metrics )

    # reco analysis
    if len(reco_dist_center)>1:
        print(reco_dist_ave)
        rdist_ave = np.concatenate( reco_dist_ave, axis=1 )
        print("concat: ",rdist_ave)
        rdist_ave    = np.min( np.concatenate( reco_dist_ave, axis=1 ), axis=0 )
        print(rdist_ave)
        rdist_center = np.min( np.concatenate( reco_dist_center, axis=1 ), axis=0 )
    elif len(reco_dist_center)==1:
        rdist_center = reco_dist_center[0]
        rdist_ave    = reco_dist_ave[0]
    else:
        rdist_center = np.ones( nreco )*9999.0
        rdist_ave    = np.ones( nreco )*9999.0
    
    nu_kpdata_dict['rdist_center'] = rdist_center
    nu_kpdata_dict['rdist_ave'] = rdist_ave
        
    return {"true_nukp_metrics":true_nu_metrics,
            "reco_nukp_metrics":nu_kpdata_dict}

    
if __name__=="__main__":

    corsika_validation_list="/cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/ubdl/larflow/larmatchnet/dataprep/inputlists/mcc9_v13_bnbnue_corsika_validation.paired.list"
    
    input_larlite = "larmatchme_mcc9_v40a_dl_run1_bnb_intrinsic_nue_overlay_CV_fd8d0c21-1220-4c97-ae1c-b30711f9eeb6_larlite.root"
    input_larcv = "merged_dlreco_fd8d0c21-1220-4c97-ae1c-b30711f9eeb6.root"

    print("run study_kpreco",flush=True)
    preplm = LArMatchHDF5Writer(treename_for_adc_image="wire", use_triplet_skip_limit=False )
    preplm.kpana.set_verbosity( larcv.msg.kINFO )

    ioll = larlite.storage_manager( larlite.storage_manager.kBOTH )
    ioll.set_verbosity(2)    
    ioll.set_out_filename("out_kpreco_study_temp.root")
    ioll.set_data_to_read( larlite.data.kLArFlow3DHit, "larmatch" )    
    ioll.set_data_to_read( larlite.data.kMCShower, "mcreco" )
    ioll.set_data_to_read( larlite.data.kMCTrack, "mcreco" )
    ioll.set_data_to_read( larlite.data.kMCTruth, "generator" )
    ioll.set_data_to_read( larlite.data.kMCFlux,  "generator" )
    ioll.set_data_to_read( larlite.data.kTrigger, "triggersim" )
    ioll.set_data_to_read( larlite.data.kDAQHeaderTimeUBooNE, "daq" )
    ioll.add_in_filename( input_larlite )
    ioll.add_in_filename( input_larcv )        
    ioll.open()
    
    iolcv = larcv.IOManager( larcv.IOManager.kREAD, "larcv", larcv.IOManager.kTickBackward )
    iolcv.set_verbosity(2)
    iolcv.add_in_file( input_larcv )
    iolcv.specify_data_read( larcv.kProductImage2D, "wire" )
    iolcv.specify_data_read( larcv.kProductChStatus, "wire" )
    iolcv.specify_data_read( larcv.kProductImage2D, "ubspurn_plane0" )
    iolcv.specify_data_read( larcv.kProductImage2D, "ubspurn_plane1" )
    iolcv.specify_data_read( larcv.kProductImage2D, "ubspurn_plane2" )    
    iolcv.specify_data_read( larcv.kProductImage2D, "thrumu" )    
    iolcv.specify_data_read( larcv.kProductImage2D, "larflow" )
    iolcv.specify_data_read( larcv.kProductImage2D, "instance" )
    iolcv.specify_data_read( larcv.kProductImage2D, "segment" )
    iolcv.specify_data_read( larcv.kProductImage2D, "ancestor" )
    iolcv.reverse_all_products()
    iolcv.initialize()

    num_max_spacepoints=5000000
    nentries_larcv = iolcv.get_n_entries()
    start_entry = 0
    end_entry = nentries_larcv
    run_process_truthlabels=True

    kpreco_nu     = larflow.reco.KeypointReco()
    kpreco_shower = larflow.reco.KeypointReco()
    kpreco_track  = larflow.reco.KeypointReco()        
    
    # event loop                                                                                                                                                                                                                                          
    for ientry in range(start_entry,end_entry):
        print("=============================================",flush=True)
        print("[[ RUN ENTRY %d ]]"%(ientry),flush=True)
        ioll.go_to(ientry)
        iolcv.read_entry(ientry)

        ev_mcshower = ioll.get_data( larlite.data.kMCShower, "mcreco" )
        print("num mcshowers: ",ev_mcshower.size(),flush=True)

        mcpg = ublarcvapp.mctools.MCPixelPGraph()
        mcpg.set_cluster_neutrino_particles( True )
        mcpg.buildgraph( iolcv, ioll )
        mcpg.printGraph(0,True)
        
        # convert the data and store into self.entry_data
        preplm.larlite_larcv_to_hdf5_entry( ioll, iolcv, run_process_truthlabels, num_max_spacepoints )
        data = preplm.entry_data.pop(0)
        print(data['keypoint_truth_kptype_pdg_trackid'],flush=True)
        print(data['keypoint_truth_pos'],flush=True)
        
        result = prepare_hits( iolcv, ioll )
        ev_filtered_hits = ioll.get_data( larlite.data.kLArFlow3DHit, "taggerfilterhit" )
        print("number of hits passing thrumu pixel filter: ",ev_filtered_hits.size(),flush=True)

        # now we reco keypoints
        nu_kpdict = reco_nu_keypoints( ioll, kpreco_nu, input_spacepoint_tree="larmatch" )
        #shower_kpdict = reco_shower_keypoints( ioll, kpreco_shower, input_spacepoint_tree="larmatch" )
        #track_kpdict = reco_track_keypoints( ioll, kpreco_track, input_spacepoint_tree="larmatch" )

        # now we can analyze
        kptype_filter = data['keypoint_truth_kptype_pdg_trackid'][:,0]==0
        nu_truekp_pos = data['keypoint_truth_pos'][kptype_filter,:]
        print("number of true nu kp: ",nu_truekp_pos.shape[0])
        print(nu_truekp_pos)

        ana_out_dict = analyze_nu_keypoints( nu_truekp_pos, nu_kpdict )
        print("======================")
        print("true_nukp_metrics")
        for i,truedata in enumerate(ana_out_dict['true_nukp_metrics']):
            print("true kp[",i,"]")
            for k,v in truedata.items():
                print("[",k,"]: ",v)
        print("======================")
        print("reco_nukp_metrics")
        for k,v in ana_out_dict['reco_nukp_metrics'].items():
            print("[",k,"]")
            print(v)

        
        if True and ientry+1>=10:
            break




