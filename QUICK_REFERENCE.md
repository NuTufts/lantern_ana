# Lantern Analysis Framework - Quick Reference 📚

*Essential information for using the refactored producer-first architecture*

## ⚡ Quick Start

### 1. Basic Analysis Script
```python
from lantern_ana import LanternAna

# Create and run analysis
ana = LanternAna("my_config.yaml")
ana.run()
```

### 2. Minimal Configuration Template
```yaml
output_dir: "./results"
max_events: 1000
producer_first_mode: True  # Use new architecture

datasets:
  my_data:
    type: RootDataset
    ismc: true
    process: true
    filepaths: [data.root]

producers:
  energy:
    type: VisibleEnergyProducer
    config: {}

cuts:
  simple_cut: {}

cut_logic: "{simple_cut}"
```

## 🏗️ Architecture Overview

```
Raw Data → Producers (calculate) → Cuts (decide) → Results
```

**Key Principle**: Producers CALCULATE, Cuts DECIDE

## 📊 Available Components

### Core Producers
| Producer | Purpose | Output Variables |
|----------|---------|------------------|
| `VisibleEnergyProducer` | Total visible energy | `evis` |
| `VertexPropertiesProducer` | Vertex information | `x`, `y`, `z`, `found`, `score`, `cosmicfrac`, etc. |
| `RecoElectronPropertiesProducer` | Electron candidates | `has_primary_electron`, `emax_*` variables |
| `RecoMuonTrackPropertiesProducer` | Muon tracks | `max_muscore`, `nMuTracks`, etc. |
| `trueNuPropertiesProducer` | True neutrino info | `Enu` |
| `eventWeightProducer` | Event weights | `weight` |
| `TruthModeProducer` | Event classification | `mode` |

### Common Cuts
| Cut | Purpose | Key Parameters |
|-----|---------|----------------|
| `true_nue_CCinc` | True νₑ CC events | `fv_params`, particle thresholds |
| `reco_nue_CCinc_refactored` | Reconstructed νₑ CC | `fv_params`, confidence cuts |
| `fiducial_cut` (function) | Fiducial volume | `width`, `apply_scc`, `usetruevtx` |
| `remove_true_nue_cc` | Background removal | `applyto` |

## 🔧 Configuration Guide

### Producer Configuration
```yaml
producers:
  producer_name:           # Your choice of name
    type: ProducerClass    # From available producers
    config:                # Producer-specific parameters
      parameter1: value1
      parameter2: value2
```

### Cut Configuration  
```yaml
cuts:
  cut_name:               # Your choice of name
    parameter1: value1    # Cut-specific parameters
    parameter2: value2

cut_logic: "{cut_name1} and {cut_name2}"  # Logical combination
```

### Cut Logic Examples
```yaml
cut_logic: "{cut1}"                    # Single cut
cut_logic: "{cut1} and {cut2}"         # Both must pass
cut_logic: "{cut1} or {cut2}"          # Either can pass  
cut_logic: "({cut1} or {cut2}) and {cut3}"  # Complex logic
cut_logic: "not {cut1}"                # Invert cut
```

## 📝 Writing Components

### Custom Producer Template
```python
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from array import array

@register
class MyProducer(ProducerBaseClass):
    def __init__(self, name, config):
        super().__init__(name, config)
        self.my_variable = array('f', [0.0])
    
    def prepareStorage(self, output):
        output.Branch(f"{self.name}_var", self.my_variable, f"{self.name}_var/F")
    
    def setDefaultValues(self):
        self.my_variable[0] = 0.0
    
    def requiredInputs(self):
        return ["gen2ntuple"]  # Or other producer names
    
    def processEvent(self, data, params):
        ntuple = data["gen2ntuple"]
        # Calculate your quantity
        self.my_variable[0] = some_calculation(ntuple)
        return {"var": self.my_variable[0]}
	
    def finalize(self):
    	""" no action needed after event loop """
        return
```

You can make a template for your producer using the following utility script:

```
$ generate_producer_template.py [producer_name]
```

```
Usage:
  generate_producer_template.py MyProducerName

Examples:
  python3 generate_producer_template.py TrackShowerRatioProducer
  python3 generate_producer_template.py EventTopologyProducer
  python3 generate_producer_template.py MissingEnergyProducer
```

### Custom Cut Template
```python
from lantern_ana.cuts.cut_factory import register_cut

@register_cut
def my_cut(ntuple, params):
    """
    My custom cut description.
    
    Parameters:
    - threshold: Minimum value to pass (default: 100.0)
    """
    threshold = params.get('threshold', 100.0)
    producer_data = params.get('producer_data', {})
    
    # Access producer outputs
    energy = producer_data.get('energy', {}).get('evis', 0.0)
    
    # Make decision
    return energy > threshold
```

## 🛠️ Common Tasks

### Add New Variable
1. Create producer that calculates it
2. Add producer to config
3. Use in cuts via `producer_data`

### Debug Analysis
```python
# More verbose logging
ana = LanternAna("config.yaml", log_level="DEBUG")

# Check available components
from lantern_ana.producers.producer_factory import ProducerFactory
print("Producers:", ProducerFactory.list_producers())

from lantern_ana.cuts.cut_factory import CutFactory  
print("Cuts:", CutFactory.list_available_cuts())
```

### Test Small Sample
```yaml
max_events: 100  # Start small for testing
```

### Check Results
```bash
# Your output directory will contain:
ls results/
# - dataset_TIMESTAMP.root (analysis tree with producer variables)
# - lantern_ana.log (detailed log file)
```

## 🔍 Producer Dependencies

Producers automatically run in dependency order:
```yaml
producers:
  basic_energy:
    type: VisibleEnergyProducer
    # No dependencies
  
  advanced_calc:
    type: MyAdvancedProducer
    # Depends on basic_energy (specified in requiredInputs())
```

The framework resolves dependencies automatically using networkx.

## 🎯 Best Practices

### For Undergrad Students
1. **Start Simple**: One dataset, one producer, one cut
2. **Test Incrementally**: Add complexity gradually  
3. **Use Examples**: Copy and modify existing analyses
4. **Read Logs**: They tell you what's happening
5. **Ask Questions**: Better to ask than guess

### Configuration Tips
```yaml
# Good: Descriptive names
producers:
  electron_properties:
    type: RecoElectronPropertiesProducer

# Good: Comments explaining choices  
cuts:
  high_energy_cut:
    min_energy: 500.0  # MeV, chosen based on signal/background studies
```

### Common Debugging
```bash
# If analysis fails to start:
python3 -c "import lantern_ana; print('OK')"  # Test import

# If no events pass cuts:
# - Check cut logic syntax
# - Add debug: true to cuts
# - Start with very loose cuts

# If producer not found:
# - Check @register decorator
# - Verify file is in producers/ directory
```

## 📖 Key Files

| File | Purpose |
|------|---------|
| `STUDENT_GUIDE.md` | Comprehensive tutorial |
| `REFACTORING_SUMMARY.md` | Technical implementation details |
| `studies/nue_cc_inclusive/` | Working example analysis |
| `test_refactored_analysis.py` | Framework test script |

## 🆘 Getting Help

1. **Check Examples**: Look at `studies/` directory
2. **Read Source**: Producer/cut source code is documented
3. **Debug Mode**: Use `log_level="DEBUG"`
4. **Ask Supervisor**: When stuck, ask for help!

---

*Remember: The framework is a tool to help you do physics. Focus on understanding the physics first, then worry about the technical details!* 🔬