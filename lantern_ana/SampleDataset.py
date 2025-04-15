import os
import ROOT as rt

class SampleDataset:
    """
    class to represent sample data stored in an ntuple file.
    """
    def __init__(self, ntuple_path, ismc=False):
        self.ntuple_path = ntuple_path
        print("Loading ntuple data: ",self.ntuple_path)
        self.rfile = rt.TFile(self.ntuple_path,'open')
        self.ntuple = self.rfile.Get("EventTree")
        self.nentries = self.ntuple.GetEntries()
        
        self.ismc = ismc
        self.pot = 0.0        
        if ismc:
            pottree = self.rfile.Get("potTree")
            for i in range(pottree.GetEntries()):
                pottree.GetEntry(i)
                self.pot += pottree.totGoodPOT
        else:
            self.pot = 0.0

    def __len__(self):
        return self.nentries

    def pot(self):
        return self.pot

    def load_from_config( config_dict, input_dir_list=None ):
        filepath = config_dict['filename']
        if filepath[0]!='/':
            # not an absolute path, look for directory
            if input_dir_list is not None:
                for input_dir in input_dir_list:
                    trial_path = input_dir + "/" + filepath
                    if os.path.exists(trial_path):
                        filepath = trial_path
                        break
        dataset = SampleDataset(filepath, ismc=config_dict['ismc'])
        return dataset
            
            
        
