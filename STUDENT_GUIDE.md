# Lantern Analysis Framework - Student Guide 🎓

*A beginner-friendly guide to using the Lantern Analysis Framework for neutrino physics analysis*

## Table of Contents
1. [What is the Lantern Analysis Framework?](#what-is-the-lantern-analysis-framework)
2. [Key Concepts](#key-concepts)
3. [Framework Architecture](#framework-architecture)
4. [Getting Started](#getting-started)
5. [Understanding Configuration Files](#understanding-configuration-files)
6. [Writing Your First Analysis](#writing-your-first-analysis)
7. [Advanced Topics](#advanced-topics)
8. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
9. [Getting Help](#getting-help)

## What is the Lantern Analysis Framework?

The Lantern Analysis Framework is a Python-based system designed to analyze data from neutrino detectors, specifically the MicroBooNE experiment. Think of it as a sophisticated filtering and calculation system that helps you extract physics insights from raw detector data.

### Real-World Analogy
Imagine you're a detective investigating thousands of crime scenes (neutrino interactions). The framework is like:
- **Raw Data**: Security camera footage from all crime scenes
- **Producers**: Forensic experts who analyze evidence and calculate measurements
- **Cuts**: Decision criteria to identify which cases match your investigation
- **Results**: A final report with the cases that matter to your investigation

## Key Concepts

### 🔧 **Producers** (The Calculators)
Producers are like specialized calculators that measure specific quantities from the raw data:
- **What they do**: Calculate derived quantities (energy, angles, particle properties)
- **What they DON'T do**: Make decisions about which events to keep
- **Examples**: 
  - `VisibleEnergyProducer`: Calculates total energy deposited in the detector
  - `RecoElectronPropertiesProducer`: Analyzes electron candidate properties
  - `VertexPropertiesProducer`: Calculates vertex position and quality metrics

### ✂️ **Cuts** (The Decision Makers)
Cuts are like filters that decide which events are interesting for your analysis:
- **What they do**: Make yes/no decisions based on calculated quantities
- **What they DON'T do**: Calculate new quantities (they use producer outputs)
- **Examples**:
  - `true_nue_CCinc`: Selects true neutrino electron events
  - `fiducial_cut`: Keeps events inside the detector's active volume

### 📊 **Datasets**
Collections of data files containing neutrino interaction records:
- **MC (Monte Carlo)**: Simulated data where we know the "true" answer
- **Data**: Real detector recordings
- **Each event**: One potential neutrino interaction

## Framework Architecture

The framework follows a **Producer-First Architecture**:

```
Raw Data → Producers (calculate) → Cuts (decide) → Results
```

### Why This Design?
1. **Separation of Concerns**: Calculations and decisions are separate
2. **Reusability**: Producers can be used by multiple analyses
3. **Maintainability**: Easy to modify or debug individual components
4. **Performance**: No duplicate calculations

## Getting Started

### Prerequisites
- Python 3.6+
- ROOT (particle physics data analysis framework)
- Access to neutrino data files

### Basic Setup
```bash
# Navigate to the framework directory
cd /path/to/lantern_ana

# Set up the environment (this loads ROOT and other dependencies)
source setenv_lantern_ana.sh

# Test that everything works
python3 -c "import lantern_ana; print('✅ Framework loaded successfully!')"
```

### Your First Test
```bash
# Run the refactored analysis example
python3 test_refactored_analysis.py
```

If this runs without errors, you're ready to go! 🎉

## Understanding Configuration Files

Configuration files (`.yaml` format) tell the framework what to do. Think of them as recipes:

### Basic Structure
```yaml
# Basic settings
output_dir: "./my_analysis_results"  # Where to save results
max_events: 1000                     # How many events to process (-1 = all)
filter_events: True                  # Only save events that pass cuts

# Data to analyze
datasets:
  my_neutrino_data:
    type: RootDataset
    ismc: true                       # This is simulated data
    process: true                    # Yes, analyze this dataset
    filepaths:
     - path/to/my/data.root

# What to calculate (Producers run first)
producers:
  visible_energy:                    # Name you choose
    type: VisibleEnergyProducer     # Type from framework
    config: {}                      # Parameters (empty = defaults)
  
  electron_info:
    type: RecoElectronPropertiesProducer
    config:
      electron_quality_cuts:
        min_charge: 0.0

# What events to keep (Cuts use producer outputs)
cuts:
  fiducial_volume:
    width: 10.0                     # Stay 10cm from detector edges
    apply_scc: true                 # Apply space charge correction
  
# How to combine cuts
cut_logic: "{fiducial_volume}"      # Must pass fiducial cut
```

### Configuration Tips for Students
1. **Start Simple**: Begin with one dataset, one producer, one cut
2. **Use Comments**: Add `# explanation` to remember what each setting does
3. **Test Incrementally**: Add one new component at a time
4. **Save Versions**: Keep working configs with meaningful names like `analysis_v1.yaml`

## Writing Your First Analysis

### Step 1: Create Your Configuration File
```yaml
# my_first_analysis.yaml
output_dir: "./my_first_results"
max_events: 100  # Start small for testing!

datasets:
  test_data:
    type: RootDataset
    ismc: true
    process: true
    filepaths:
     - ntuple_mcc9_v28_wctagger_bnboverlay_v3dev_reco_retune.root

producers:
  energy:
    type: VisibleEnergyProducer
    config: {}

cuts:
  energy_cut:
    min_energy: 100.0  # Only events with >100 MeV

cut_logic: "{energy_cut}"
```

### Step 2: Run Your Analysis
```python
#!/usr/bin/env python3
# my_first_analysis.py

from lantern_ana import LanternAna

# Create analysis object
ana = LanternAna("my_first_analysis.yaml")

# Run the analysis
ana.run()

print("✅ Analysis complete! Check ./my_first_results/ for output files")
```

### Step 3: Run It!
```bash
python3 my_first_analysis.py
```

### Step 4: Check Your Results
```bash
ls my_first_results/
# You should see .root files with your processed data
```

## Advanced Topics

### Creating Custom Producers

Sometimes you need to calculate something specific. Here's how to create your own producer:

```python
# my_custom_producer.py
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from array import array

@register  # This makes it available to the framework
class MyCustomProducer(ProducerBaseClass):
    """
    A producer that calculates the ratio of track to shower energy.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.track_shower_ratio = array('f', [0.0])  # Output variable
    
    def prepareStorage(self, output):
        """Set up output tree branch."""
        output.Branch(f"{self.name}_ratio", self.track_shower_ratio, f"{self.name}_ratio/F")
    
    def setDefaultValues(self):
        """Reset variables before each event."""
        self.track_shower_ratio[0] = 0.0
    
    def requiredInputs(self):
        """What data this producer needs."""
        return ["gen2ntuple"]  # Needs the raw detector data
    
    def processEvent(self, data, params):
        """Calculate the track/shower energy ratio."""
        ntuple = data["gen2ntuple"]
        
        # Calculate total track energy
        track_energy = 0.0
        for i in range(ntuple.nTracks):
            if ntuple.trackIsSecondary[i] == 0:  # Primary tracks only
                track_energy += ntuple.trackRecoE[i]
        
        # Calculate total shower energy  
        shower_energy = 0.0
        for i in range(ntuple.nShowers):
            if ntuple.showerIsSecondary[i] == 0:  # Primary showers only
                shower_energy += ntuple.showerRecoE[i]
        
        # Calculate ratio (avoid division by zero)
        if shower_energy > 0:
            self.track_shower_ratio[0] = track_energy / shower_energy
        else:
            self.track_shower_ratio[0] = -1.0  # Flag for no showers
        
        return {"ratio": self.track_shower_ratio[0]}
```

### Creating Custom Cuts

```python
# my_custom_cuts.py
from lantern_ana.cuts.cut_factory import register_cut

@register_cut
def high_energy_muon_cut(ntuple, params):
    """
    Keep events with high-energy muon tracks.
    
    Parameters:
    - ntuple: Event data
    - params: Cut parameters including 'min_muon_energy'
    """
    min_energy = params.get('min_muon_energy', 500.0)  # Default 500 MeV
    
    # Look for high-energy muon tracks
    for i in range(ntuple.nTracks):
        if (ntuple.trackIsSecondary[i] == 0 and  # Primary track
            abs(ntuple.trackPID[i]) == 13 and    # Muon PID
            ntuple.trackRecoE[i] > min_energy):  # High energy
            return True
    
    return False  # No high-energy muons found
```

## Common Pitfalls and Solutions

### ❌ **Problem**: "Producer X not found"
**Solution**: Make sure your producer file is in the `lantern_ana/producers/` directory and uses the `@register` decorator.

### ❌ **Problem**: "Cut Y not registered"  
**Solution**: Check that your cut file is in `lantern_ana/cuts/` and uses `@register_cut`.

### ❌ **Problem**: "Circular dependency detected"
**Solution**: Check that producers don't depend on each other in a loop. Use `requiredInputs()` to specify dependencies.

### ❌ **Problem**: Analysis runs but no events pass cuts
**Solution**: 
1. Check your cut logic - maybe it's too restrictive
2. Add `debug: true` to cut parameters to see what's happening
3. Start with very loose cuts and tighten gradually

### ❌ **Problem**: "File not found" errors
**Solution**: Check that file paths in your YAML config are correct and accessible.

## Getting Help

### Debug Mode
Add this to your analysis script for more information:
```python
ana = LanternAna("config.yaml", log_level="DEBUG")
```

### Understanding Your Results
Your analysis produces ROOT files with:
- **Analysis tree**: One entry per event that passed cuts, with all producer variables
- **POT tree**: Information about the dataset (for normalization)

### Checking What's Available
```python
# List available producers
from lantern_ana.producers.producer_factory import ProducerFactory
print("Available producers:", ProducerFactory.list_producers())

# List available cuts  
from lantern_ana.cuts.cut_factory import CutFactory
print("Available cuts:", CutFactory.list_available_cuts())
```

### Example Analysis Templates

Check the `studies/` directory for working examples:
- `studies/nue_cc_inclusive/`: Electron neutrino analysis
- `studies/numu_cc_inclusive/`: Muon neutrino analysis

### Getting Support
1. **Documentation**: Read `REFACTORING_SUMMARY.md` for technical details
2. **Examples**: Look at existing analyses in `studies/`
3. **Code**: Read the source code - it's designed to be understandable!
4. **Ask Questions**: Don't hesitate to ask your supervisor or fellow students

## Final Tips for Success 🌟

1. **Start Small**: Begin with simple analyses and build complexity gradually
2. **Test Frequently**: Run on small event samples first
3. **Comment Your Code**: Future you will thank present you
4. **Version Control**: Keep track of your configurations and code changes
5. **Understand Physics**: The framework is a tool - understanding the physics is the goal!

Remember: Everyone was a beginner once. The best way to learn is by doing, making mistakes, and asking questions. Good luck with your neutrino physics journey! 🔬✨