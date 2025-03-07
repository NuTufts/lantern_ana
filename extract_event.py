import os,sys
import ROOT
from larcv import larcv


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Get file using run, subrun, event (and fileid)")
    parser.add_argument('-dl','--dlmerged',required=True,type=str)
    parser.add_argument('-k','--kps-reco',required=True,type=str)    
    parser.add_argument('-r','--run',default=None,type=int)
    parser.add_argument('-s','--subrun',default=None,type=int)
    parser.add_argument('-e','--event',default=None,type=int)
    args = parser.parse_args()

    
    iolcv = larcv.IOManager(larcv.IOManager.kBOTH,'larcv',larcv.IOManager.kTickBackward)
    iolcv.reverse_all_products()
    iolcv.specify_data_read( larcv.data.kProductImage2D, 'wire' )
    iolcv.specify_data_read( larcv.data.kProductImage2D, 'thrumu' )
    iolcv.specify_data_read( larcv.data.kProductImage2D, 'larflow' )
    iolcv.specify_data_read( larcv.data.kProductImage2D, 'instance' )
    iolcv.specify_data_read( larcv.data.kProductImage2D, 'segment' )
    iolcv.add_in_file( args.dlmerged )
    iolcv.set_out_file( 'test_out_larcv.root' )
    iolcv.initialize()
    nentries = iolcv.get_n_entries()

    for i in range(nentries):
        iolcv.read_entry(i)
        run = iolcv.event_id().run()
        subrun = iolcv.event_id().subrun()
        event = iolcv.event_id().event()

        if run==args.run and subrun==args.subrun and event==args.event:
            print(f"Found Matching entry: ({run},{subrun},{event}")
            iolcv.save_entry()
    iolcv.finalize()

    print("END")
            
                    
