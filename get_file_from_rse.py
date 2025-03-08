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
    parser.add_argument('--prefix',default=None,help='if provided, we prepend this path to the booking file path')
    parser.add_argument('-o','--out',default=None,help='if provided, put names of files into this text file')
                        
    args = parser.parse_args()

    sample_info = get_sample_info( args.data_sample )
    bookfile = sample_info[ 'bookfile' ]
    bookfile_path = f"bookkeep/{bookfile}"
    if args.prefix is not None:
        bookfile_path = args.prefix + "/" + bookfile_path
    bookdict = make_dict_from_file( bookfile_path )
    
    if args.fileid is not None:
        basename = bookdict[args.fileid]['fname']
        zfileid = "%06d"%(args.fileid)
        dlmerged_path = sample_info['dlmerged_data_dir']+"/%s/%s"%(zfileid[:2],zfileid[2:4])+"/"+basename
        print("dlmerged path: ",dlmerged_path)

        recofilename = basename.replace("merged_dlreco","larflowreco_fileid%04d"%(args.fileid)).replace(".root","_kpsrecomanagerana.root")
        reco_path = sample_info['reco_dir']+"/%03d"%(args.fileid/100)+"/"+recofilename
        print("reco filename: ",reco_path)

        if args.out is not None and os.path.exists(args.out)==False:
            with open( args.out, 'w' ) as fout:
                print(dlmerged_path," ",reco_path,file=fout)
