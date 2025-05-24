from typing import Dict, List, Any, Optional, Union, Type
import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
#from lantern_ana.tags.tag_factory import TagFactory
from lantern_ana.utils import get_true_primary_particle_counts


@register
class NueInclusiveTruthSelectionProducer(ProducerBaseClass):
    """
    Producer that extracts variables for the CC nue inclusive selection.
    We use lantern_ana.utils.true_particle_counts.get_true_primary_particle_counts
        and as a result we inherit its parameters. But we use our own defaults

    producer args:
    - name : name given to the instance of this class (set by yaml config)
    - config: dictionary containing parameters to set the behavior of this selection

    config params:
    - eKE: kinetic energy threshold in MeV for primary electrons [default: 30.0 MeV]
    - muKE: kinetic energy threshold in MeV for primary muons [default:  30.0 MeV]
    - pKE: kinetic energy threshold in MeV for primary protons [default: 60.0 MeV]
    - piKE: kinetic energy threshold in MeV for primary pions [default: 30.0 MeV]
    - gKE: kinetic energy threshold in MeV for primary gammas (using initial kinetic energy, not energy deposited) [default: 20.0 MeV]
    - xKE: kinetic energy threshold in MeV for particles that do not include the above [default: 60.0 MeV]
    """
    def __init__(self, name, config):
        super().__init__(name, config)

        true_part_cfg = {}
        true_part_cfg['eKE']  = config.get('eKE',30.0)
        true_part_cfg['muKE'] = config.get('muKE',30.0)
        true_part_cfg['piKE'] = config.get('piKE',30.0)
        true_part_cfg['pKE']  = config.get('pKE',60.0)
        true_part_cfg['gKE']  = config.get('gKE',10.0)
        true_part_cfg['xKE']  = config.get('xKE',60.0)
        self.true_part_cfg = true_part_cfg

        self.particles = ['e','mu','p','pi','g','X']
        self.pids = { 'e':11, 'mu':13, 'p':2212, 'pi':111, 'g':22, 'X':0}
        self.countvars = {}
        for part in self.particles:
            self.countvars[part] = array.array('i',[0])
        self.is_CCnue_inclusive = array.array('i',[0])
        self.pid_list = [ self.pids[x] for x in self.particles ]
        self.particlename_from_pid = {}
        for pid in self.pid_list:
            for partname,v in self.pids.items():
                if v==pid:
                    self.particlename_from_pid[pid] = partname


    def prepareStorage(self, output: Any) -> None:
        """
        Prepare output storage for this producer.
        
        This method is called by the manager to set up storage for
        the producer's output (e.g., a branch in a ROOT TTree).
        
        Args:
            output: The output storage interface (e.g., a ROOT TTree)
        """
        tree = output
        for part in self.particles:
            tree.Branch(f"{self.name}_num_{part}",self.countvars[part],f"{self.name}_num_{part}/I")

    def setDefaultValues(self):
        """
        Set the default values for the variables we are making.
        """
        for part in self.particles:
            self.countvars[part][0] = 0
        self.is_CCnue_inclusive[0] = 0
    
    def productType(self) -> Type:
        """
        Get the type of the product produced by this producer.
        
        Returns:
            The Python type of the output product (default: float)
        """
        return dict
    
    def requiredInputs(self) -> List[str]:
        """
        Get a list of required input producer names and/or source dataset.
        
        Returns:
            List of names of producers whose outputs are required by this producer
        """
        return ["gen2ntuple"]
    
    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Any:
        """
        Process a single event using the provided data.
        
        Args:
            data: Dictionary mapping producer names to their outputs
            params: Additional parameters for this processing step
            
        Returns:
            The output of the producer for this event
        """
        ismc = params.get('ismc',False)
        self.setDefaultValues()
        if not ismc:
            # return empty outputs
            ret_vars = {'is_CCnue_inclusive':0}
            for part in self.particles:
                ret_vars[f'num_{part}'] = 0
            return ret_vars


        ntuple = data.get('gen2ntuple',None)
        if ntuple is None:
            raise ValueError('tree with name "gen2ntuple" not in data dict')

        counts = get_true_primary_particle_counts( ntuple, self.true_part_cfg )

        for pid in counts:
            apid = abs(pid)
            if apid in self.pid_list:
                particlename = self.particlename_from_pid[apid]
                self.countvars[particlename][0] += counts[pid]
            else:
                self.countvars['X'][0] += counts[pid]

        if self.countvars['e']==1 and self.countvars['mu']==0:
            self.is_CCnue_inclusive[0] = 1
        else:
            self.is_CCnue_inclusive[0] = 0


        ret_vars = {'is_CCnue_inclusive':self.is_CCnue_inclusive[0]}
        for part in self.particles:
            ret_vars[f'num_{part}'] = self.countvars[part]
        
        return ret_vars
        





