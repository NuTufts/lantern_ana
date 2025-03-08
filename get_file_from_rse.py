import os,sys
import lantern_photon
from lantern_photon.sampledefs import get_sample_info
from lantern_photon.fileutils.bookfile_parser import make_dict_from_file

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Get file using run, subrun, event (and fileid)")
    parser.add_argument('-d','--data-sample',required=True,type=str)
    parser.add_argument('-r','--run',default=None,type=int)
    parser.add_argument('-s','--subrun',default=None,type=int)
    parser.add_argument('-e','--event',default=None,type=int)
    parser.add_argument('-fid','--fileid',default=None,type=int)
    args = parser.parse_args()

    sample_info = get_sample_info( args.data_sample )
    bookfile = sample_info[ 'bookfile' ]
    bookdict = make_dict_from_file( f"bookkeep/{bookfile}" )
    
    if args.fileid is not None:
        basename = bookdict[args.fileid]['fname']
        zfileid = "%06d"%(args.fileid)
        dlmerged_path = sample_info['dlmerged_data_dir']+"/%s/%s"%(zfileid[:2],zfileid[2:4])+"/"+basename
        print("dlmerged path: ",dlmerged_path)

        recofilename = basename.replace("merged_dlreco","larflowreco_fileid%04d"%(args.fileid)).replace(".root","_kpsrecomanagerana.root")
        reco_path = sample_info['reco_dir']+"/%03d"%(args.fileid/100)+"/"+recofilename
        print("reco filename: ",reco_path)
