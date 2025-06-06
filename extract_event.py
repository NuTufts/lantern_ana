import os,sys
import numpy as np

import ROOT as rt
from ROOT import std
from larlite import larlite
from larcv import larcv
from ublarcvapp import ublarcvapp

from plotly.subplots import make_subplots
import plotly.graph_objects as go

from lantern_ana.helpers.image2d_cropping import crop_around_postion


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Get file using run, subrun, event (and fileid)")
    parser.add_argument('-dl','--dlmerged',required=True,type=str)
    parser.add_argument('-k','--kps-reco',required=True,type=str)    
    parser.add_argument('-r','--run',default=None,type=int)
    parser.add_argument('-s','--subrun',default=None,type=int)
    parser.add_argument('-e','--event',default=None,type=int)
    parser.add_argument('-vx','--vertex-x',type=float,default=None)
    parser.add_argument('-vy','--vertex-y',type=float,default=None)
    parser.add_argument('-vz','--vertex-z',type=float,default=None)
    parser.add_argument('-nt','--ntracks',type=int,default=None)
    parser.add_argument('-ns','--nshowers',type=int,default=None)    
    args = parser.parse_args()

    
    iolcv = larcv.IOManager(larcv.IOManager.kBOTH,'larcv',larcv.IOManager.kTickBackward)
    #iolcv.reverse_all_products()
    # iolcv.specify_data_read( larcv.data.kProductImage2D, 'wire' )
    # iolcv.specify_data_read( larcv.data.kProductImage2D, 'thrumu' )
    # iolcv.specify_data_read( larcv.data.kProductImage2D, 'larflow' )
    # iolcv.specify_data_read( larcv.data.kProductImage2D, 'instance' )
    # iolcv.specify_data_read( larcv.data.kProductImage2D, 'segment' )
    iolcv.add_in_file( args.dlmerged )
    iolcv.set_out_file( 'test_out_larcv.root' )
    iolcv.initialize()
    nentries = iolcv.get_n_entries()

    """
    Example of typical larlite offerings
  KEY: TTree	mceventweight_eventweight4to4aFix_tree;1	mceventweight Tree by eventweight4to4aFix
  KEY: TTree	mceventweight_eventweightLEE_tree;1	mceventweight Tree by eventweightLEE
  KEY: TTree	mcflux_generator_tree;1	mcflux Tree by generator
  KEY: TTree	mcshower_mcreco_tree;1	mcshower Tree by mcreco
  KEY: TTree	mctrack_mcreco_tree;1	mctrack Tree by mcreco
  KEY: TTree	MCTree;1	MC infomation
  KEY: TTree	mctruth_corsika_tree;1	mctruth Tree by corsika
  KEY: TTree	mctruth_generator_tree;1	mctruth Tree by generator
  KEY: TTree	opflash_opflashBeam_tree;1	opflash Tree by opflashBeam
  KEY: TTree	opflash_opflashCosmic_tree;1	opflash Tree by opflashCosmic
  KEY: TTree	opflash_simpleFlashBeam::OverlayStage1OpticalDLrerun_tree;1	opflash Tree by simpleFlashBeam::OverlayStage1OpticalDLrerun
  KEY: TTree	opflash_simpleFlashBeam_tree;1	opflash Tree by simpleFlashBeam
  KEY: TTree	opflash_simpleFlashCosmic::OverlayStage1OpticalDLrerun_tree;1	opflash Tree by simpleFlashCosmic::OverlayStage1OpticalDLrerun
  KEY: TTree	opflash_simpleFlashCosmic_tree;1	opflash Tree by simpleFlashCosmic
  KEY: TTree	ophit_ophitBeam::OverlayStage1OpticalDLrerun_tree;1	ophit Tree by ophitBeam::OverlayStage1OpticalDLrerun
  KEY: TTree	ophit_ophitBeamCalib_tree;1	ophit Tree by ophitBeamCalib
  KEY: TTree	ophit_ophitCosmic::OverlayStage1OpticalDLrerun_tree;1	ophit Tree by ophitCosmic::OverlayStage1OpticalDLrerun
  KEY: TTree	ophit_ophitCosmicCalib_tree;1	ophit Tree by ophitCosmicCalib
    """
    larlite_products = [
        ('mcshower','mcreco'),
        ('mctrack','mcreco'),
        ('mctruth','generator'),
        ('mctruth','corsika'),
        ('opflash','opflashBeam'),
        ('opflash','opflashCosmic')
    ]
         
    ioll = larlite.storage_manager( larlite.storage_manager.kBOTH )
    ioll.add_in_filename( args.dlmerged )
    ioll.set_out_filename( "test_out_larlite.root" )
    for (datatype,treename) in larlite_products:
        ioll.set_data_to_read( datatype, treename )
        ioll.set_data_to_write( datatype, treename )
    ioll.open()

    recoFile = rt.TFile( args.kps_reco, 'open' )
    recoTree = recoFile.Get('KPSRecoManagerTree')
    nentries_reco = recoTree.GetEntries()
    print("Num Entries in Reco Tree: ",nentries_reco)

    recoOutFile = rt.TFile( "test_out_reco.root", "recreate" )
    recoOutTree = rt.TTree("KPSRecoManagerTree","Copy of reco tree")
    nuvertex_store = std.vector('larflow::reco::NuVertexCandidate')()
    recoOutTree.Branch( "nuvetoed_v", nuvertex_store )

    for i in range(nentries):
        iolcv.read_entry(i)
        ioll.go_to(i, False)
        nuvertex_store.clear()

        ev_wire = iolcv.get_data( "image2d", "wire" )
        wire_v = ev_wire.as_vector()

        run = iolcv.event_id().run()
        subrun = iolcv.event_id().subrun()
        event = iolcv.event_id().event()
        print("Entry[",i,"] run=",run," subrun=",subrun," event=",event)

        if run==args.run and subrun==args.subrun and event==args.event:
            print(f"Found Matching entry: ({run},{subrun},{event})")
            mcpg = ublarcvapp.mctools.MCPixelPGraph()
            mcpg.buildgraph( iolcv, ioll )
            mcpg.printAllNodeInfo()
            #mcpg.printGraph(0,False)

            nbytes = recoTree.GetEntry(i)
            print("Number of bytes in reco tree entry: ",nbytes)
            nuvtx_v = recoTree.nuvetoed_v
            num_nu_candidates = nuvtx_v.size()
            print("Number of candidates in entry: ",num_nu_candidates)

            # match the vertex
            given_vtx = np.array( [args.vertex_x, args.vertex_y, args.vertex_z] )
            for ivtx in range(num_nu_candidates):
                nuvtx = nuvtx_v.at(ivtx)                
                pos = np.array( [nuvtx.pos[v] for v in range(3)] )
                d = given_vtx-pos
                dd = np.sqrt(np.sum((d*d)))

                nshowers = nuvtx.shower_v.size()
                ntracks  = nuvtx.track_v.size()
                print("RecoVertex[",ivtx,"]")
                print("  Nshowers=",nshowers)
                print("  Ntracks=",ntracks)
                print("  dist to selected: ",dd," cm")
                if dd<0.3 and nshowers==args.nshowers and ntracks==args.ntracks:                    
                    print("Matched Reco Vertex!")
                    nuvertex_store.push_back( nuvtx )

                    # copy images so we can reverse it
                    rwire_v = std.vector("larcv::Image2D")()
                    for p in range(wire_v.size()):
                        rimg = larcv.Image2D(wire_v.at(p))
                        rimg.reverseTimeOrder()
                        rwire_v.push_back(rimg)

                    histname = "run%d_subrun%d_event%d_vertex%d"%(args.run, args.subrun, args.event, ivtx)
                    recoOutFile.cd()
                    hist_crop, crop_dict = crop_around_postion( rwire_v, given_vtx, 256, 256, histname )
                    #for h in hist_crop:
                    #    h.Write()

            # test
            import lardly
            from lardly.ubdl.det3d_truth_plot import make_traces as truth_make_traces
            from lardly.ubdl.det3d_recoshower_plot import make_traces as reco_make_traces
            from lardly.ubdl.det3d_viewer import make_default_plot


            
            fig3d = make_default_plot()
            mctraces = truth_make_traces( ioll, iolcv, recoOutTree )
            recotraces = reco_make_traces( ioll, iolcv, recoOutTree )
            for trace in mctraces:
                fig3d.add_trace( trace )
            for trace in recotraces:
                fig3d.add_trace( trace )
            #fig3d.write_html( histname+"_det3d.html" )

            fig2d = make_subplots( rows=1, cols=3 )
            for n in range(3):
                meta = crop_dict['meta'][n]
                img_np = crop_dict['npimg'][n]
                plot = go.Heatmap(name="Plane %d"%(n),
                                  z=np.transpose(img_np,(1,0)),
                                  y=np.linspace(meta.min_x(),meta.max_x(),img_np.shape[0]),
                                  x=np.linspace(meta.min_y(),meta.max_y(),img_np.shape[1]))
                fig2d.add_trace( plot, row=1, col=n+1 )
            #fig2d.write_html( histname+"_wireimages.html" )

            # div1 = offline_plot(fig3d, include_plotlyjs=False, output_type='div')
            # div2 = offline_plot(fig2d, include_plotlyjs=False, output_type='div')
            # # Create HTML structure to hold the figures
            # html_content = htmltools.HTML(
            #     htmltools.tags.html(
            #         htmltools.tags.head(
            #             htmltools.tags.script(src="https://cdn.plot.ly/plotly-2.27.0.min.js")
            #         ),
            #         htmltools.tags.body(
            #             htmltools.HTML(div1),
            #             htmltools.HTML(div2)
            #         )
            #     )
            # )
            # Save combined HTML to a file
            with open(histname+"_multiple.html", "w") as f:
                f.write( fig3d.to_html(full_html=False,include_plotlyjs='cdn'))
                f.write( fig2d.to_html(full_html=False,include_plotlyjs=False))
            
            # copy over data into output larcv file
            iolcv.save_entry()
            ioll.go_to(i,True) # reload and save
            recoOutTree.Fill()

            # copy over data into output larlite file
                      
            # Get out of loop
            break
            
            
    iolcv.finalize()
    ioll.close()
    recoOutFile.Write()
    recoOutFile.Close()

    print("END")
            
                    
