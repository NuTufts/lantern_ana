import os,sys,time
import re
from typing import Dict, Any, List, Optional, Type
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
import numpy as np
import ROOT as rt


# Example implementation of a ROOT-based dataset
@register
class UBDetSysProducer(ProducerBaseClass):
    """
    Implementation of Dataset for ROOT files.
    """
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        """
        We must histogram the intersection of two simulated files:
          - a "central value" simulation which was made using the default parameters of the simulation model
          - a "variation" simulation where one simulation model parameter has been changed by "one sigma amount" (of its prior)
        The difference in the number of events that pass is the fractional uncertainty on the expected number of events in each bin.

        Because we are calculating uncertainties on the expected number per bin, we need a bin definition.
        This must match in other places the systematic uncertainties are calculated, namely the flux and cross section systematics.

        Upon initialization of this producer we need to:
          - load the CV file ane make a (run,subrun,event) -> entry index map. This map is how we will enforce the intersection of events processed
          - define the histograms we will fill, one for the CV and one for the variation
        
        After the event loop is run (by the lantern_ana application), we will use the finalize method to
          - save the histograms to a ROOT file
          - for each pair of (variable,variation) we estimate the 1-sigma std-dev of the expectation due to a model parameter
            using the :1 distance between the CV and the variation 

        Example of bin_config block:
        
        bin_config: 
          visible_energy: # bins of visible energy of the neutrino interaction
            formula: visible_energy
            numbins: 30
            minvalue: 0.0
            maxvalue: 3000.0
            apply_to_datasets: ['run1_bnb_nu_overlay_mcc9_v28_wctagger']
            criteria: ['pass_numu_cc_inclusive']
        
        Args:
            name: A unique identifier for this dataset
            config: Dictionary containing configuration parameters:
             - todo: document parameters
        """
        super().__init__(name, config)

        # name for variations to estimate in this instance of producer
        self.variation_names = config.get('variations_to_include',[])
        if len(self.variation_names)==0:
            raise ValueError("No variations given to estimate")

        # get run, subrun, event branches in the variation rootfiles
        self.run_branchname    = config.get('run')
        self.subrun_branchname = config.get('subrun')
        self.event_branchname  = config.get('event')
        self.index_branchnames = {
            'run':self.run_branchname,
            'subrun':self.subrun_branchname,
            'event':self.event_branchname
        }

        # get tree name in variation files
        self.var_treename = config.get('variation_treename')

        # for each variation we need some info
        var_rootfile_dict = config.get('variation_rootfiles',{})
        self.var_info = {}
        for var in self.variation_names:
            if var not in var_rootfile_dict:
                raise ValueError(f"Variation[{var}] does not have a rootfile")
            var_rootfile = var_rootfile_dict[var]
            var_rsemap   = self._build_sample_entry_index(var_rootfile, self.var_treename,self.index_branchnames)
            var_tfile    = rt.TFile( var_rootfile )
            var_ttree    = var_tfile.Get(self.var_treename)
            self.var_info[var] = {
                "rootfile":var_rootfile_dict[var],
                "rsemap":var_rsemap,
                "nunion":0,
                "tfile":var_tfile,
                "ttree":var_ttree
            }

        # name of the central value sample
        self.cv_dataset = config.get('central_value_dataset')

        self._bin_config_list = config.get('bin_config')

        self.outfile = rt.TFile(f"{self.name}_{self.cv_dataset}.root",'recreate')

        # cap weight value: sometimes a crazy large weight occurs
        self.maxvalidweight = config.get('maxvalidweight',100)

        # event selection criterion
        self.cut_formulas = config.get('cut_formulas',{})
        self.event_selection_critera = config.get('event_selection_critera',[])

    def _build_sample_entry_index(self,rootfile,treename,index_branchnames):
        """
        Open file and make (run,subrun,event) --> index dictionary
        """
        try:
            # open file
            rfile = rt.TFile( rootfile )
            # get ttree
            ttree = rfile.Get(treename)
            # disable all but run, subrun, event branches to speed up read through file
            ttree.SetBranchStatus("*", 0)
            ttree.SetBranchStatus(index_branchnames['run'], 1)
            ttree.SetBranchStatus(index_branchnames['subrun'], 1)
            ttree.SetBranchStatus(index_branchnames['event'], 1)            
            nentries = ttree.GetEntries()
            print(f"Loaded variation tree '{treename}' with {nentries} entries: {rootfile}")
        except:
            raise RuntimeError(f'Failed to make RSE to index map for variation file"{rootfile}".')

        tstart = time.time()
        rsedict = {}
        # TODO: use a tqdm loop here?
        for iientry in range(nentries):
            #if (iientry%100000==0):
            #    print("  building index. entry ",iientry)
            ttree.GetEntry(iientry)
            run    = eval(f"ttree.{index_branchnames['run']}")
            subrun = eval(f"ttree.{index_branchnames['subrun']}")
            event  = eval(f"ttree.{index_branchnames['event']}")
            rse = (run,subrun,event)
            rsedict[rse] = iientry
            if iientry%100000==0:
                print("  building RSE-entry map. entry ",iientry," rse=",rse)

        dt_index = time.time()-tstart
        print(f'  Time to make variation index: {dt_index:.2f}. Number of entries: {nentries}')
        rfile.Close()
        return rsedict


    def setDefaultValues(self):
        super().setDefaultValues()
        return

    def prepareStorage(self, output: Any) -> None:
        """
        Set up what to save in the output ROOT TTree. Here, we're saving histograms and covariances.

        # TODO
        #  - for each entry in the config list bin_config, define a histogram for each variable. 
        #  - we define a TH1D to store the information. Mostly to use the find bin function
        #  - make a copy of a histogram for seach sample
        #  - for each (var,sample) histogram, we make 3 copies: one for sum[w], sum[w^2], N
        #  - need a global index for each histogram, this way we can build a covariance matrix
        """

        self.outfile.cd()
        self.histograms = {} # keys are (histname,variation)

        for histname in self._bin_config_list:
            vardict = self._bin_config_list[histname]
            nbins = vardict['numbins']
            hname_cv = f"h{histname}__CVCV"
            hcv = rt.TH1D(hname_cv,"",nbins, vardict['minvalue'],vardict['maxvalue'])
            self.histograms[(histname,'CVCV','cv')] = hcv
            for var in self.variation_names:
                # we save a histogram to
                # 1. help us look up the bin position for this observable
                # 2. store the central value and the number of entries per bin
                hname = f"h{histname}__{var}"
                for x in ['cv','var']:
                    h = rt.TH1D(hname+f"__{x}","",nbins, vardict['minvalue'],vardict['maxvalue'])
                    self.histograms[(histname,var,x)] = h

        print("Number of histograms defined: ",len(self.histograms))
        
        return

    def requiredInputs(self) -> List[str]:
        """Specify required inputs."""
        return ["gen2ntuple"]

    # def _load_sample_weight_tree(self, datasetname ):
    #     if self._current_sample_tchain is not None:
    #         if datasetname != self._current_sample_name:
    #             self._current_sample_tchain.Close()
    #         else:
    #             return # already loaded

    #     self._current_sample_tchain = rt.TChain( self._tree_name )
    #     if datasetname not in self._sample_filepaths:
    #         raise ValueError(f"Could not find sample name, '{datasetname}' in file path dictionary parameter")

    #     self._current_sample_tchain.Add(self._sample_filepaths[datasetname])
    #     nentries = self._current_sample_tchain.GetEntries()
    #     print("Loaded weight tree for dataset: ",datasetname)


    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if event is signal nue CC inclusive."""
        ntuple = data["gen2ntuple"]
        datasetname = params.get('dataset_name')
        if datasetname != self.cv_dataset:
            return {}
        ismc = params.get('ismc', False)
        if ismc==False:
            return {}

        # first evaluate if this entry pass the selection
        # evaluate all the selection formulas
        # in order to decide if this event is something we are going to fill
        # select_results = {}
        # for cutname,cutformula in self.cut_formulas.items():
        #     # Extract placeholders from the formula (strings inside {})
        #     placeholders = re.findall(r'\{([^}]+)\}', cutformula)

        #     # Create clean expression and namespace
        #     clean_expression = cutformula
        #     namespace = {}
        #     for placeholder in placeholders:
        #         # Create a simple variable name from the placeholder
        #         var_name = placeholder.replace('.', '_').replace('[', '_').replace(']', '')
        #         clean_expression = clean_expression.replace(f"{{{placeholder}}}", var_name)
        #         # Evaluate the placeholder to get the actual value
        #         namespace[var_name] = eval(placeholder)

        #     # Evaluate the clean expression with the namespace
        #     select_results[cutname] = eval(clean_expression, namespace)
        
        # cv_passes = True
        # for cutname in self.event_selection_critera:
        #     if select_results[cutname]==False:
        #         cv_passes = False
        #         break
        cv_passes = self._process_selection_cut( ntuple )
        #print('cv_passes: ',cv_passes)

        var_cut_result = {}
        var_has_entry = {}
        for var in self.variation_names:
            var_info = self.var_info[var]
            run    = eval(f"ntuple.{self.index_branchnames['run']}")
            subrun = eval(f"ntuple.{self.index_branchnames['subrun']}")
            event  = eval(f"ntuple.{self.index_branchnames['event']}") 
            rse = (run,subrun,event)
            if rse in var_info['rsemap']:
                var_has_entry[var] = True
                var_entry = var_info['rsemap'][rse]
                nbytes = var_info['ttree'].GetEntry(var_entry)
                if nbytes>0:
                    var_passes = self._process_selection_cut( var_info['ttree'] )
                else:
                    var_passes = False
                var_cut_result[var] = var_passes
            else:
                var_has_entry[var]  = False
                var_cut_result[var] = None
        #print("Var cut result: ",var_cut_result)
        #print("Var has entry: ",var_has_entry)

        for var in self.variation_names:
            if var_has_entry[var]==True:
                self.var_info[var]['nunion'] += 1

        # Fill the histograms
        eventweight = ntuple.eventweight_weight

        for histname in self._bin_config_list:
            histdict = self._bin_config_list[histname]

            if cv_passes:
                x_cv = self._process_variable_formula( ntuple, histdict['formula'] )
                # fill the CV histogram
                self.histograms[ (histname,'CVCV','cv') ].Fill( x_cv, eventweight )
            else:
                x_cv = None 

            for var in self.variation_names:
                
                if var_has_entry[var]==True:
                    # we only have possibility to fill CV or var hist if var has entry that CV does
                    if cv_passes==True:
                        hcv = self.histograms[ (histname,var,'cv') ]
                        hcv.Fill( x_cv, eventweight )
                    
                    if var_cut_result[var]==True:
                        hvar = self.histograms[ (histname,var,'var') ]
                        var_tree = self.var_info[var]['ttree']
                        x_var = self._process_variable_formula( var_tree, histdict['formula'] )
                        hvar.Fill( x_var, eventweight )
               
        return {}

    def _process_selection_cut( self, ntuple ):

        # in order to decide if this event is something we are going to fill
        select_results = {}
        for cutname,cutformula in self.cut_formulas.items():
            # Extract placeholders from the formula (strings inside {})
            placeholders = re.findall(r'\{([^}]+)\}', cutformula)

            # Create clean expression and namespace
            clean_expression = cutformula
            namespace = {}
            for placeholder in placeholders:
                # Create a simple variable name from the placeholder
                var_name = placeholder.replace('.', '_').replace('[', '_').replace(']', '')
                clean_expression = clean_expression.replace(f"{{{placeholder}}}", var_name)
                # Evaluate the placeholder to get the actual value
                namespace[var_name] = eval(placeholder)

            # Evaluate the clean expression with the namespace
            select_results[cutname] = eval(clean_expression, namespace)

        passes = True
        for cutname,result in select_results.items():
            if result==False:
                passes = False
                break

        return passes

    def _process_variable_formula( self, ntuple, varformula ):
        # sample does apply to this variable, so we get the observable variable value
        x = eval(f'ntuple.{varformula}')   
        return x


    def finalize(self):
        print("write detsys histograms: N=",len(self.histograms))
        self.outfile.cd()
        for var in self.variation_names:
            print(f" Intersection of CV and variation[{var}] MC event sets: Number=",self.var_info[var]['nunion'])
        for h in self.histograms:
            self.histograms[h].Write()
        self.outfile.Close()
        
        
