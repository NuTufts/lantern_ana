import os,sys

def make_dict_from_file( bookfile ):
    print("Parse bookkeeping file and return dict for file=",bookfile)
    bookdict = {}
    with open(bookfile,'r') as bfile:
        ll = bfile.readlines()
        for l in ll:
            l = l.strip()
            info=l.split()
            fileid=int(info[0])
            bookdict[fileid] = dict(
                fileid=fileid,
                nevents=int(info[1]),
                run_range=[int(info[2]),int(info[3])],
                subrun_range=[int(info[4]),int(info[5])],
                event_range=[int(info[6]),int(info[7])],
                fname=info[-1] )
    return bookdict
