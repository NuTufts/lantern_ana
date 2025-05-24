# lantern_ana/producers/visualization_producer.py
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register

@register
class StackedHistProducer(ProducerBaseClass):
    """
    Producer that generates histogram of particular variable, where we sort and then stack based on other variables.
    Configuration parameters:
    - output_path: str providing name of ROOT file to store histograms in.
    - plot_var:  the variable we want to histogram
    - nbins: number of bins
    - xmin: minimum of x-axis
    - xmax: maximum of x-axis
    - tagvar: name of variable in the event we will inspect to sort event into histogram
    - split_vars: name of categories we will split events into. for each name, we will look for a list of tagvar values that assign event to category  
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.histograms = {}
        self.output_file = None
        
        # Configuration
        self.output_path = config.get("output_path", f"analysis_{name}_stacked_histograms.root")
        self.plotvar_name = config.get("plotvar_name",None)
        if self.plotvar_name is None:
            raise ValueError("Must specify 'plotvar_name' in config of StackedHistProducer (see lantern_ana.producers.stackedHist)")
        self.plotvar_key = config.get("plotvar_key",None)
        if self.plotvar_key is None:
            raise ValueError("Must specify 'plotvar_key' in config of StackedHistProducer (see lantern_ana.producers.stackedHist)")
        self.pass_cutresults = config.get('pass_cutresults',[])

        self.nbins = config["nbins"]
        self.xmin  = config["xmin"]
        self.xmax  = config["xmax"]
        self.tagvar_name = config["tagvar_name"]
        self.tagvar_key  = config["tagvar_key"]
        self.weight_name = config.get("weight_name",None)
        self.weight_key  = config.get("weight_key",None)
        if self.weight_name is not None and self.weight_key is None:
            raise ValueError("Must specify 'weight_key' in config if a weighting variable given (by parameter 'weight_name')")
        self.hist_title = config.get("title","")
        self.splitvars = config.get("split_vars",[])
        if type(self.splitvars) is not list or len(self.splitvars)==0:
            raise ValueError("Must specify list of categories to split hist events using config par 'split_vars'")

        self.tagvals = {}
        for catname in self.splitvars:
            self.tagvals[catname] = config.get(catname,[])


        self.output_file = ROOT.TFile(self.output_path, "RECREATE")

        # Initialize histograms
        self._initialize_histograms()
        
    def _initialize_histograms(self):
        """Initialize all histograms."""
        for catname in self.splitvars:
            hname = f"h_prod_{self.name}_{catname}"
            self.histograms[hname] = ROOT.TH1F(hname,self.hist_title,self.nbins,self.xmin,self.xmax)

        hname_uncat = f"h_prod_{self.name}_uncategorized"
        while hname_uncat in self.histograms:
            hname_uncat += "_"
        self.histograms[hname_uncat] = ROOT.TH1F(hname_uncat,self.hist_title,self.nbins,self.xmin,self.xmax)
        self.hname_uncat = hname_uncat
    
    def prepareStorage(self, output):
        """No tree branches needed for visualization producer."""
        pass
    
    def setDefaultValues(self):
        return super().setDefaultValues()

    def productType(self):
        """Return the type of product."""
        return dict
    
    def requiredInputs(self):
        """Specify required inputs."""
        inputs = ["gen2ntuple", self.plotvar_name, self.tagvar_name]+self.pass_cutresults
        if self.weight_name is not None:
            inputs.append( self.weight_name )
        return inputs
    
    def processEvent(self, data, params):
        """Fill histograms with event data."""
        # Extract data
        plotvar = data.get(self.plotvar_name, {})
        tagvar  = data.get(self.tagvar_name,{})

        #print(data)
        plotvalue = plotvar.get(self.plotvar_key,0.0)
        tagvalue  = tagvar.get(self.tagvar_key,None)
        #print(plotvalue," ",tagvalue)

        pass_to_fill = True
        for cutname in self.pass_cutresults:
            xcutresult = data.get(cutname,0)
            #print(f'cut[{cutname}]: {xcutresult}')
            if data.get(cutname,0)==0:
                pass_to_fill = False

        if not pass_to_fill:
            return {'filledhist':False,'foundcat':False}

        # get weight
        weight = 1.0
        if self.weight_name is not None and self.weight_key:
            weight = data.get(self.weight_name,1.0).get(self.weight_key)
        
        # search for category are we tagged into, and if found, fill histogram
        foundcat = False
        for catname in self.splitvars:
            if tagvalue in self.tagvals[catname]:
                hname = f"h_prod_{self.name}_{catname}"
                self.histograms[hname].Fill(plotvalue) # need way to pass weight!
                foundcat = True
        if not foundcat:
            self.histograms[self.hname_uncat].Fill(plotvalue)
        
        return {'filledhist':True,"foundcat": False}
    
    def finalize(self):
        """Save histograms to file."""
        # Activate histogram
        self.output_file.cd()
        
        # Write all histograms
        for name, hist in self.histograms.items():
            hist.Write()
        
        # Close file
        self.output_file.Close()
        print(f"Histograms saved to {self.output_path}")
