import os,sys
from array import array
import numpy as np
import ROOT as rt
from ROOT import std
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

def get_data_dict_from_keypointreco( kpreco, iolcv ):

    # get the keypoint data
    npts = kpreco.output_pt_v.size()
    kppos = np.zeros( (npts,3) )
    kpavepos = np.zeros( (npts,3) )
    kpmaxpos = np.zeros( (npts,3) )
    kpmaxscore = np.zeros( npts )
    kpavescore = np.zeros( npts )
    kpnpts = np.zeros( npts, dtype=np.int64 )
    kptype = np.zeros( npts, dtype=np.int64 )

    # for cosmic
    evimg = iolcv.get_data( larcv.kProductImage2D, "thrumu" )
    kp_thrumu_pixsum  = np.zeros( (npts,3) )
    kp_thrumu_nplanes = np.zeros( npts, dtype=np.int64 )
    
    for ikp in range( npts ):
        kpcluster = kpreco.output_pt_v.at(ikp)
        for v in range(3):
            kppos[ikp,v] = kpcluster.center_pt_v.at(v)
            kpavepos[ikp,v] = kpcluster.center_avg_pt_v.at(v)
            kpmaxpos[ikp,v] = kpcluster.max_pt_v.at(v)
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

        xyz = std.vector("float")(3)
        for v in range(3):
            xyz[v] = kpmaxpos[ikp,v]
        nplanes_thrumu = 0
        for p in range(3):
            thrumu_pixsum = ptprojection.getPixelSumAroundProjPoint( xyz, evimg.as_vector().at(p), 2, 10.0 )
            if thrumu_pixsum>20.0:
                nplanes_thrumu += 1
            kp_thrumu_pixsum[ikp,p] = thrumu_pixsum
        kp_thrumu_nplanes[ikp] = nplanes_thrumu
        
    return {"num_keypoints":npts,
            "pos_fitted":kppos,
            "pos_ave":kpavepos,
            "pos_max":kpmaxpos,
            "maxscore":kpmaxscore,
            "avescore":kpavescore,
            "nclusterpts":kpnpts,
            "thrumu_nplanes":kp_thrumu_nplanes,
            "thrumu_pixsum":kp_thrumu_pixsum,
            "type":kptype}
    
def reco_nu_keypoints( ioll, iolcv, _kpreco_nu, input_spacepoint_tree="taggerfilterhit" ):
    _kpreco_nu.clear_output()
    _kpreco_nu.set_verbosity( larcv.msg.kNORMAL )
    _kpreco_nu.set_input_larmatch_tree_name( input_spacepoint_tree )
    _kpreco_nu.set_sigma( 10.0 )
    _kpreco_nu.set_max_dbscan_dist( 0.7 )
    _kpreco_nu.set_larmatch_threshold( 0.5 )

    _kpreco_nu.set_min_cluster_size(   10, 0 )
    _kpreco_nu.set_keypoint_threshold( 0.2, 0 )
    
    #_kpreco_nu.set_min_cluster_size(   10, 1 )
    #_kpreco_nu.set_keypoint_threshold( 0.2, 1 )

    _kpreco_nu.set_output_tree_name( "keypoint" )
    _kpreco_nu.set_keypoint_type( 0 ) #larflow.kNuVertex
    _kpreco_nu.set_lfhit_score_index( 17 )
    _kpreco_nu.process( ioll )

    dataout = get_data_dict_from_keypointreco( _kpreco_nu, iolcv )
    return dataout
        

def reco_shower_keypoints( ioll, iolcv, _kpreco_shower, input_spacepoint_tree="taggerfilterhit" ):

    # neutrino interaction shower
    _kpreco_shower.clear_output()
    _kpreco_shower.set_input_larmatch_tree_name( input_spacepoint_tree )
    _kpreco_shower.set_output_tree_name( "keypoint" )
    _kpreco_shower.set_sigma( 10.0 )
    _kpreco_shower.set_max_dbscan_dist( 0.7 )
    _kpreco_shower.set_larmatch_threshold( 0.5 )
    
    _kpreco_shower.set_min_cluster_size(   10, 0 )
    _kpreco_shower.set_keypoint_threshold( 0.2, 0 )
    #_kpreco_shower.set_min_cluster_size(   10, 1 )    
    #_kpreco_shower.set_keypoint_threshold( 0.2, 1 )
    
    _kpreco_shower.set_keypoint_type( 3 )
    _kpreco_shower.set_lfhit_score_index( 20 ) # // (v2 larmatch-minkowski network nu-shower-score index in hit)
    _kpreco_shower.process( ioll )
    
    #// neutrino+cosmic interaction michel
    #_kpreco_shower.clear_output()      
    _kpreco_shower.set_keypoint_type( 4 )
    _kpreco_shower.set_lfhit_score_index( 21 ) # // (v2 larmatch-minkowski network michel-shower-score index in hit)
    _kpreco_shower.process( ioll )
    
    #// neutrino+cosmic interaction delta
    #_kpreco_shower.clear_output()
    _kpreco_shower.set_keypoint_type( 5 )
    _kpreco_shower.set_lfhit_score_index( 22 ) # // (v2 larmatch-minkowski network delta-shower-score index in hit)
    _kpreco_shower.process( ioll )

    dataout = get_data_dict_from_keypointreco( _kpreco_shower, iolcv )
    return dataout

def reco_track_keypoints( ioll, iolcv, _kpreco_track, input_spacepoint_tree="taggerfilterhit" ):

    # neutrino interaction track: we have track starts and ends
    _kpreco_track.clear_output();      
    _kpreco_track.set_input_larmatch_tree_name( input_spacepoint_tree );
    _kpreco_track.set_sigma( 10.0 );
    _kpreco_track.set_max_dbscan_dist( 0.7 )
    _kpreco_track.set_larmatch_threshold( 0.5 )    
    _kpreco_track.set_min_cluster_size(   10, 0 )
    _kpreco_track.set_keypoint_threshold( 0.2, 0 )
    #_kpreco_track.set_min_cluster_size(   10, 1 )    
    #_kpreco_track.set_keypoint_threshold( 0.2, 1 )
    # neutrino interaction track start
    _kpreco_track.set_output_tree_name( "keypoint" )
    _kpreco_track.set_keypoint_type( 1 ) # (int)larflow::kTrackStart );
    _kpreco_track.set_lfhit_score_index( 18 ) # // (v2 larmatch-minkowski network track-start-score index in hit)
    _kpreco_track.process( ioll )
    # neutrino interaction track end
    #_kpreco_track.clear_output()      
    _kpreco_track.set_output_tree_name( "keypoint" )
    _kpreco_track.set_keypoint_type( 2 ) # (int)larflow::kTrackEnd );
    _kpreco_track.set_lfhit_score_index( 19 )  # // (v2 larmatch-minkowski network track-end-score index in hit)
    _kpreco_track.process( ioll )

    dataout = get_data_dict_from_keypointreco( _kpreco_track, iolcv )
    return dataout

def reduce_trackstarts_with_nu_keypoints( true_kp_pos, true_kp_types ):

    if np.sum(true_kp_types[:,0]==0)==0:
        return true_kp_pos, true_kp_types
    
    nu_kp_pos_v = true_kp_pos[ true_kp_types[:,0]==0, : ]
    trackstartpos = true_kp_pos[ true_kp_types[:,0]==1, : ]
    trackendpos   = true_kp_pos[ true_kp_types[:,0]==2, : ]    
    
    ntrue = true_kp_types.shape[0]
    true_filter = np.full( ntrue, True )
    
    for ikp in range(nu_kp_pos_v.shape[0]):

        nu_kp_pos = nu_kp_pos_v[ikp,:]

        start_dist2nupos = np.sqrt(np.sum(np.power(trackstartpos-nu_kp_pos,2),axis=1))
        start_distfilter = start_dist2nupos>1.0
        true_filter[true_kp_types[:,0]==1]= start_distfilter
        
        end_dist2nupos = np.sqrt(np.sum(np.power(trackendpos-nu_kp_pos,2),axis=1))
        end_distfilter = end_dist2nupos>1.0
        true_filter[true_kp_types[:,0]==2] = end_distfilter

    print("reduce_trackstarts_with_nu_keypoints")
    print(true_filter)

    return true_kp_pos[true_filter,:], true_kp_types[true_filter,:]

def analyze_keypoints( true_pos, true_kptype, kpdata_dict ):

    # for each true kp, we get
    # - closest reco kp
    # - number of pts in closest kp
    # - max score of closest kp
    # - dist to center
    # - dist to ave score loc
    
    print("---------------------")
    print("ANALYSE KEYPOINTS")
    
    true_metrics_v = []

    nreco = kpdata_dict["num_keypoints"]
    ireco_good = np.zeros( nreco, dtype=np.int64 ) # which reco keypoints were matched to a true vertex

    reco_dist_center = []
    reco_dist_ave    = []

    for ikp in range(true_pos.shape[0]):
        # loop for now
        # get closest nu keypoint
        truepos = true_pos[ikp,:]
        truetype = true_kptype[ikp,0]
        truepid  = true_kptype[ikp,1]
        truetid  = true_kptype[ikp,2]
        if kpdata_dict['num_keypoints']>0:
            dpos_center = np.sqrt(np.sum(np.power(kpdata_dict["pos_fitted"]-truepos,2), axis=1 ))
            dpos_ave = np.sqrt(np.sum(np.power(kpdata_dict["pos_ave"]-truepos,2), axis=1 ))
            dpos_max = np.sqrt(np.sum(np.power(kpdata_dict["pos_max"]-truepos,2), axis=1 ))
            reco_dist_ave.append( np.expand_dims(dpos_ave,0) )
            reco_dist_center.append( np.expand_dims(dpos_center,0) )
            print("truepos: ",truepos)
            #print("recopos:")
            #print(kpdata_dict["pos_fitted"])
            #print(dpos_center)
            closest = np.argmin( dpos_ave )
            print("  index of closest reco keypoint: ",closest," dist=%.2f"%(dpos_ave[closest]),
                  " ave-score=%.2f"%(kpdata_dict['avescore'][closest]),
                  " max-score=%.2f"%(kpdata_dict['maxscore'][closest]))
                  
            true_metrics = {'idx_closest':closest,
                            "pos":truepos,
                            "type":truetype,
                            "pid":truepid,
                            "tid":truetid,
                            "dist2fitpos":dpos_center[closest],
                            "dist2avepos":dpos_ave[closest],
                            "dist2maxpos":dpos_max[closest],
                            "nclusterpts":kpdata_dict['nclusterpts'][closest],
                            "avescore":kpdata_dict['avescore'][closest],
                            "maxscore":kpdata_dict['maxscore'][closest],
                            "thrumu_pixsum":kpdata_dict['thrumu_pixsum'][closest],
                            "thrumu_nplanes":kpdata_dict['thrumu_nplanes'][closest]}
        else:
            true_metrics = {'idx_closest':-1,
                            "pos":truepos,
                            "type":truetype,
                            "pid":truepid,
                            "tid":truetid,
                            "dist2fitpos":9999.0,
                            "dist2avepos":9999.0,
                            "dist2maxpos":9999.0,
                            "nclusterpts":0,
                            "avescore":0.0,
                            "maxscore":0.0,
                            "thrumu_pixsum":[0.0,0.0,0.0],
                            "thrumu_nplanes":0}
        true_metrics_v.append( true_metrics )

    print("do reco analysis")
    #print("reco dist ave")
    #print(reco_dist_ave)
    #print("reco dist center")    
    #print(reco_dist_center)
        
    # reco analysis
    if len(reco_dist_ave)>1:
        x = np.concatenate( reco_dist_ave, axis=0 )
        print("c")
        print(" list of ",len(reco_dist_ave)," x ",reco_dist_ave[0].shape)
        print(" to ",x.shape)
        rdist_ave    = np.min( x, axis=0 )
        print(" min to ",rdist_ave.shape)
        rdist_center = np.min( np.concatenate( reco_dist_center, axis=0 ), axis=0 )
    elif len(reco_dist_ave)==1:
        rdist_center = reco_dist_center[0][0]
        rdist_ave    = reco_dist_ave[0][0]
    else:
        rdist_center = np.ones( nreco )*9999.0
        rdist_ave    = np.ones( nreco )*9999.0
    
    kpdata_dict['rdist_center'] = rdist_center
    kpdata_dict['rdist_ave'] = rdist_ave
        
    return {"true_metrics":true_metrics_v,
            "reco_metrics":kpdata_dict}

    
if __name__=="__main__":

    corsika_validation_list="/cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/ubdl/larflow/larmatchnet/dataprep/inputlists/mcc9_v13_bnbnue_corsika_validation.paired.list"
    
    #input_larlite = "larmatchme_mcc9_v40a_dl_run1_bnb_intrinsic_nue_overlay_CV_fd8d0c21-1220-4c97-ae1c-b30711f9eeb6_larlite.root"
    #input_larcv = "merged_dlreco_fd8d0c21-1220-4c97-ae1c-b30711f9eeb6.root"
    input_larlite=sys.argv[1]
    input_larcv=sys.argv[2]

    print("run study_kpreco",flush=True)
    preplm = LArMatchHDF5Writer(treename_for_adc_image="wire", use_triplet_skip_limit=True )
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
    #start_entry = 1
    #end_entry = 3
    run_process_truthlabels=True

    kpreco_nu     = larflow.reco.KeypointReco()
    kpreco_shower = larflow.reco.KeypointReco()
    kpreco_track  = larflow.reco.KeypointReco()

    ptprojection = ublarcvapp.ubimagemod.PointImageProjection()

    for recoalg in [kpreco_nu,kpreco_shower,kpreco_track]:
        recoalg.set_verbosity(larcv.msg.kNORMAL)

    outroot = rt.TFile("out_kpreco_study.root", "recreate" )
    
    truekp_tree = rt.TTree("truekp","Metrics related to true keypoints")
    truekp_enu  = array('f',[0.0])    
    truekp_pos  = array('f',[0.0]*3)
    truekp_type = array('i',[0])
    truekp_pid  = array('i',[0])
    truekp_partKE   = array('f',[0.0])
    truekp_dist2ave = array('f',[0.0])
    truekp_dist2max = array('f',[0.0])    
    truekp_dist2fit = array('f',[0.0])
    truekp_avescore = array('f',[0.0])
    truekp_maxscore = array('f',[0.0])
    truekp_numpts   = array('i',[0])
    truekp_thrumu_pixsum = array('f',[0.0]*3)
    truekp_thrumu_nplanes = array('i',[0])
    truekp_tree.Branch("enu",truekp_enu,"enu/F")
    truekp_tree.Branch("pos",truekp_pos,"pos[3]/F")
    truekp_tree.Branch("kptype",truekp_type,"kptype/I")
    truekp_tree.Branch("pid",truekp_pid,"pid/I")
    truekp_tree.Branch("partKE",truekp_partKE,"partKE/F")        
    truekp_tree.Branch("dist2ave",truekp_dist2ave,"dist2ave/F")
    truekp_tree.Branch("dist2max",truekp_dist2max,"dist2max/F")    
    truekp_tree.Branch("dist2fit",truekp_dist2fit,"dist2fit/F")
    truekp_tree.Branch("avescore",truekp_avescore,"avescore/F")
    truekp_tree.Branch("maxscore",truekp_maxscore,"maxscore/F")
    truekp_tree.Branch("thrumu_pixsum",truekp_thrumu_pixsum,"thrumu_pixsum[3]/F")
    truekp_tree.Branch("thrumu_nplanes",truekp_thrumu_nplanes,"thrumu_nplanes/I")

    recokp_tree = rt.TTree("recokp","Metrics related to reco keypoints")
    recokp_pos  = array('f',[0.0]*3)
    recokp_type = array('i',[0])
    recokp_dist2true = array('f',[0.0])
    recokp_maxscore  = array('f',[0.0])
    recokp_avescore  = array('f',[0.0])
    recokp_thrumusum = array('f',[0.0]*3)
    recokp_thrumuplanes = array('i',[0]*3)
    recokp_nclusterpts = array('i',[0])
    recokp_tree.Branch("pos",recokp_pos,"pos[3]/F")
    recokp_tree.Branch("kptype",recokp_type,"kptype/I")
    recokp_tree.Branch("dist2true",recokp_dist2true,"dist2true/F")
    recokp_tree.Branch("maxscore",recokp_maxscore,"maxscore/F")
    recokp_tree.Branch("avescore",recokp_avescore,"avescore/F")
    recokp_tree.Branch("nclusterpts",recokp_nclusterpts,"nclusterpts/I")
    recokp_tree.Branch("thrumu_pixsum",recokp_thrumusum,"thrumu_pixsum[3]/F")
    recokp_tree.Branch("thrumu_nplanes",recokp_thrumuplanes,"thrumu_nplanes/I")
    
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

        print("===================================")
        print("Neutrino KP analysis")
        print("===================================")
        
        # now we reco keypoints
        nu_kpdict = reco_nu_keypoints( ioll, iolcv, kpreco_nu, input_spacepoint_tree="larmatch" )
        shower_kpdict = reco_shower_keypoints( ioll, iolcv, kpreco_shower, input_spacepoint_tree="larmatch" )
        track_kpdict = reco_track_keypoints( ioll, iolcv, kpreco_track, input_spacepoint_tree="larmatch" )

        # now we can analyze
        kptype_filter = data['keypoint_truth_kptype_pdg_trackid'][:,0]==0
        nu_truekp_pos = data['keypoint_truth_pos'][kptype_filter,:]
        print("number of true nu kp: ",nu_truekp_pos.shape[0])
        print(nu_truekp_pos)

        ana_out_dict = analyze_keypoints( nu_truekp_pos, data['keypoint_truth_kptype_pdg_trackid'][kptype_filter], nu_kpdict )
        print("======================")
        print("true_nukp_metrics")
        for i,truedata in enumerate(ana_out_dict['true_metrics']):
            print("true kp[",i,"]")
            for k,v in truedata.items():
                print("[",k,"]: ",v)
        print("======================")
        print("reco_nukp_metrics")
        for k,v in ana_out_dict['reco_metrics'].items():
            print("[",k,"]")
            print(v)


        print("===================================")
        print("Shower analysis")
        print("===================================")
        
        kptype_filter = data['keypoint_truth_kptype_pdg_trackid'][:,0]==3
        shower_truekp_pos = data['keypoint_truth_pos'][kptype_filter,:]
        print("number of true shower kp: ",shower_truekp_pos.shape[0])
        print(shower_truekp_pos)

        shower_kp3_dict = {}
        shower_kp3_filter = shower_kpdict['type']==3
        for k in shower_kpdict:
            if k in ["num_keypoints"]:
                continue
            shower_kp3_dict[k] = shower_kpdict[k][shower_kp3_filter]
            #print("showerkp3: ",k)
            #print(shower_kp3_dict[k])
        shower_kp3_dict['num_keypoints'] = shower_kp3_dict['type'].shape[0]
        print("Reco shower pos")
        print(shower_kp3_dict['pos_ave'])

        shower_ana_out_dict = analyze_keypoints( shower_truekp_pos, data['keypoint_truth_kptype_pdg_trackid'][kptype_filter], shower_kp3_dict )
        print("shower[type=3] reco kp results: ")
        for ikp in range( shower_kp3_dict['num_keypoints'] ):
            _maxscore = shower_kp3_dict['maxscore'][ikp]
            _avescore = shower_kp3_dict['avescore'][ikp]
            _mindist  = shower_kp3_dict['rdist_ave'][ikp]
            #print(_maxscore,_avescore,_mindist)
            print(" [",ikp,"] maxscore=%0.3f"%(_maxscore),
                  " avescore=%.3f"%(_avescore),
                  " mindist=%.3f"%(_mindist))
        

        print("===================================")
        print("Track analysis")
        print("===================================")
        filtered_track_pos, filtered_track_types = reduce_trackstarts_with_nu_keypoints( data['keypoint_truth_pos'], data['keypoint_truth_kptype_pdg_trackid'] )
        print("orig true type array")
        print(data['keypoint_truth_kptype_pdg_trackid'])
        print()
        print("filtered pos: ")
        print(filtered_track_pos)
        print()        
        print("filtered types: ")
        print(filtered_track_types)
        print()        
        track_kptype_filter = np.logical_or( filtered_track_types[:,0]==1, filtered_track_types[:,0]==2 )
        print(track_kptype_filter)
        track_ana_out = analyze_keypoints( filtered_track_pos[track_kptype_filter,:], filtered_track_types[track_kptype_filter], track_kpdict )
        print("track reco kp results: ")
        for ikp in range( track_kpdict['num_keypoints'] ):
            print(" [",ikp,"] maxscore=%0.3f"%(track_kpdict['maxscore'][ikp])," avescore=%.3f"%(track_kpdict['avescore'][ikp])," mindist=%.3f"%(track_kpdict['rdist_ave'][ikp]))
        #print(track_ana_out)

        # Fill output truekp tree
        for anaout in [ana_out_dict,shower_ana_out_dict,track_ana_out]:
            for truekp_metrics in anaout['true_metrics']:
                tid = int(truekp_metrics["tid"])
                node_t = mcpg.findTrackID( tid )
                nu_node_t = mcpg.findTrackID( 0 )
                truekp_enu[0] = nu_node_t.E_MeV
                print("true tid: ",tid," Enu:",nu_node_t.E_MeV)
                for v in range(3):
                    truekp_pos[v]  = truekp_metrics["pos"][v]
                truekp_type[0]     = truekp_metrics["type"]
                truekp_pid[0]      = truekp_metrics["pid"]
                truekp_dist2max[0] = truekp_metrics['dist2maxpos']
                truekp_dist2ave[0] = truekp_metrics['dist2avepos']
                truekp_dist2fit[0] = truekp_metrics['dist2fitpos']
                truekp_avescore[0] = truekp_metrics['avescore']
                truekp_maxscore[0] = truekp_metrics['maxscore']
                truekp_numpts[0]   = truekp_metrics['nclusterpts']
                truekp_partKE[0]   = 0.0
                try:
                    truekp_partKE[0] = node_t.E_MeV
                except:
                    pass
                for v in range(3):
                    truekp_thrumu_pixsum[v] = truekp_metrics['thrumu_pixsum'][v]
                truekp_thrumu_nplanes[0] = truekp_metrics['thrumu_nplanes']
                truekp_tree.Fill()
            reco_metrics = anaout['reco_metrics']
            for ikp in range(reco_metrics['num_keypoints']):
                for v in range(3):                    
                    recokp_pos[v] = reco_metrics['pos_ave'][ikp,v]
                    recokp_thrumusum[v] = reco_metrics['thrumu_pixsum'][ikp,v]
                recokp_type[0] = reco_metrics['type'][ikp]
                recokp_dist2true[0] = reco_metrics['rdist_ave'][ikp]
                recokp_maxscore[0]  = reco_metrics['maxscore'][ikp]
                recokp_avescore[0]  = reco_metrics['avescore'][ikp]                
                recokp_thrumuplanes[0] = reco_metrics['thrumu_nplanes'][ikp]
                recokp_tree.Fill()
        
                
        
        if False and ientry+1>=10:
            break

    outroot.cd()
    truekp_tree.Write()
    recokp_tree.Write()
    print("saved to ROOT")


