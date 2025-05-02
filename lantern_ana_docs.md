# Lantern Analysis Framework Documentation

## Introduction

The Lantern Analysis Framework (lantern_ana) is a comprehensive Python-based system for analyzing data from liquid argon time projection chamber (LArTPC) neutrino experiments, with a focus on MicroBooNE data. The framework provides tools for loading ROOT ntuple files, selecting physics events, calculating derived quantities, and producing analysis results.

This documentation provides an overview of the framework's architecture and explains how to use it for physics analyses.

## Architecture

The framework is organized around several key components:

1. **Dataset System**: Handles loading and accessing data files
2. **Cut System**: Applies event selection criteria
3. **Producer System**: Calculates derived quantities
4. **Tag System**: Classifies events by physics types
5. **Core LanternAna Class**: Integrates all components and manages analysis workflow

### Dataset System

The Dataset system provides a consistent interface for accessing different types of data:

- `Dataset`: Abstract base class defining the interface
- `LanternNtupleDataset`: Implementation for Lantern ROOT ntuples
- `DatasetFactory`: Creates dataset instances from configuration

### Cut System

The Cut system enables physics-based event selection:

- Standalone functions that evaluate a single selection criterion
- Registration via decorators for automatic discovery
- Logical expressions for combining multiple cuts
- Cut statistics for efficiency measurements

### Producer System

The Producer system calculates derived quantities:

- Producers are classes that inherit from `ProducerBaseClass`
- Each producer handles one type of calculation
- Dependency resolution ensures correct execution order
- Output to ROOT trees and histograms

### Tag System

The Tag system classifies events:

- Tags are functions that label events based on physics properties
- Primarily used for truth-level categorization in Monte Carlo
- Useful for efficiency measurements and background studies

### LanternAna Class

The `LanternAna` class integrates all components:

- Configurable via YAML files
- Handles dataset loading and event processing
- Applies cuts and runs producers
- Manages output files and statistics
- Provides command-line interface

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nutufts/lantern_ana.git
   cd lantern_ana
   ```

2. Set up your environment:
   ```bash
   source setup.sh
   ```

### Basic Usage

1. Create a configuration YAML file (see Configuration section below)

2. Run the analysis:
   ```bash
   python -m lantern_ana.core.lantern_ana my_config.yaml
   ```

3. Analyze the results:
   - Check the output ROOT files using ROOT's TBrowser
   - Review the statistics.yaml file for selection efficiencies
   - Use the plotting scripts to visualize results

## Configuration

The framework is configured using YAML files, which specify datasets, cuts, producers, and analysis parameters.

### Example Configuration

```yaml
# Output directory for analysis results
output_dir: "./output"

# Maximum events to process (-1 for all)
max_events: 10000

# Dataset configurations
datasets:
  # Monte Carlo neutrino sample
  run3b_bnb_nu_overlay:
    type: LanternNtupleDataset
    filepaths:
      - /path/to/lantern_ntuple_file.root
    tree: EventTree
    ismc: true

# Cut configurations
cuts:
  fiducial_cut:
    width: 10.0
    applyscc: true
  has_muon_track:
    ke_threshold: 30.0

# Cut logic (how to combine cuts)
cut_logic: "fiducial_cut and has_muon_track"

# Producer configurations
producers:
  visible_energy:
    type: VisibleEnergyProducer
    config: {}
  muon_properties:
    type: MuonPropertiesProducer
    config: {}
```

### Configuration Sections

#### Datasets

The `datasets` section defines input data sources:

```yaml
datasets:
  sample_name:
    type: LanternNtupleDataset  # Dataset implementation
    filepaths:                  # List of ROOT files
      - /path/to/file1.root
      - /path/to/file2.root
    tree: EventTree             # Name of the TTree
    ismc: true                  # MC or data flag
    pot: 4.4e19                 # Optional fixed POT value
```

#### Cuts

The `cuts` section defines event selection criteria:

```yaml
cuts:
  cut_name:                     # Name of the registered cut
    param1: value1              # Parameters passed to the cut
    param2: value2
```

The `cut_logic` field specifies how to combine cuts using a logical expression:

```yaml
cut_logic: "(cut1 and cut2) or cut3"
```

#### Producers

The `producers` section defines calculations to be performed:

```yaml
producers:
  producer_name:                # Name for this producer instance
    type: ProducerClassName     # Class name of the producer
    config:                     # Configuration parameters
      param1: value1
      param2: value2
```

## Extending the Framework

### Adding a New Cut

1. Create a new Python file in the `lantern_ana/cuts/` directory:

```python
from lantern_ana.cuts.cut_factory import register_cut

@register_cut
def my_new_cut(ntuple, params):
    """
    Description of what this cut does.
    
    Parameters:
    - ntuple: The event ntuple
    - params: Dictionary with parameters:
        - param1: Description (default: value)
        
    Returns:
    - True if event passes the cut, False otherwise
    """
    threshold = params.get('threshold', 100.0)
    
    # Implement cut logic here
    passes_cut = ntuple.some_value > threshold
    
    return passes_cut
```

2. Use the cut in your configuration:

```yaml
cuts:
  my_new_cut:
    threshold: 150.0
```

### Adding a New Producer

1. Create a new Python file in the `lantern_ana/producers/` directory:

```python
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register

@register
class MyNewProducer(ProducerBaseClass):
    """
    Description of what this producer calculates.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        self.my_value = array('f', [0.0])
        
    def prepareStorage(self, output):
        """Set up branch in the output ROOT TTree."""
        output.Branch(f"{self.name}_value", self.my_value, f"{self.name}_value/F")
    
    def requiredInputs(self):
        """Specify required inputs."""
        return ["gen2ntuple"]
    
    def processEvent(self, data, params):
        """Calculate the value for this event."""
        ntuple = data["gen2ntuple"]
        
        # Perform calculation
        self.my_value[0] = calculate_something(ntuple)
        
        return {"value": self.my_value[0]}
```

2. Use the producer in your configuration:

```yaml
producers:
  my_calculation:
    type: MyNewProducer
    config:
      param1: value1
```

### Adding a New Dataset Type

1. Create a new Python file in the `lantern_ana/datasets/` directory:

```python
from lantern_ana.io.dataset_interface import Dataset, register_dataset

@register_dataset
class MyNewDataset(Dataset):
    """
    Dataset implementation for a new data format.
    """
    
    def __init__(self, name, config):
        super().__init__(name, config)
        # Initialize specific attributes
        
    def initialize(self):
        # Open files and prepare for reading
        
    def get_num_entries(self):
        # Return the number of entries
        
    def set_entry(self, entry):
        # Load the specified entry
        
    def get_data(self):
        # Return data for the current entry
```

2. Use the dataset in your configuration:

```yaml
datasets:
  my_data:
    type: MyNewDataset
    config_param1: value1
```

## Analysis Workflow

A typical analysis workflow consists of:

1. **Configuration**: Define datasets, cuts, and producers
2. **Event Loop**: Process each event in the datasets
3. **Cut Application**: Apply selection criteria to each event
4. **Producer Execution**: Calculate derived quantities for selected events
5. **Output Generation**: Fill trees and histograms with results
6. **Analysis**: Study the outputs to extract physics results

## Example Analysis

Here's an example of a complete charged-current neutrino event selection analysis:

### 1. Configuration File (numu_cc_analysis.yaml)

```yaml
# Output directory for analysis results
output_dir: "./output/numu_cc"

# Maximum events to process (-1 for all)
max_events: 100000

# Dataset configurations
datasets:
  run3b_bnb_nu_overlay:
    type: LanternNtupleDataset
    filepaths:
      - /path/to/lantern_ntuple_run3b_bnb_nu_overlay.root
    tree: EventTree
    ismc: true
  
  run3b_extbnb:
    type: LanternNtupleDataset
    filepaths:
      - /path/to/lantern_ntuple_run3b_extbnb.root
    tree: EventTree
    ismc: false
    nspills: 73174004

# Cut configurations
cuts:
  fiducial_cut:
    width: 10.0
    applyscc: true
  
  has_muon_track:
    ke_threshold: 30.0
    min_track_length: 10.0
  
  cosmic_rejection:
    max_cosmic_fraction: 0.5
    min_track_containment: 0.8

# Cut logic
cut_logic: "fiducial_cut and has_muon_track and cosmic_rejection"

# Producer configurations
producers:
  visible_energy:
    type: VisibleEnergyProducer
    config: {}
  
  muon_properties:
    type: MuonPropertiesProducer
    config: {}
  
  vertex_properties:
    type: VertexPropertiesProducer
    config: {}
  
  stacked_evis:
    type: StackedHistProducer
    config:
      output_path: "visible_energy_stacked.root"
      plotvar_name: "visible_energy"
      plotvar_key: "evis"
      tagvar_name: "truth_mode"
      tagvar_key: "mode"
      nbins: 50
      xmin: 0.0
      xmax: 3000.0
      title: "Visible Energy;Energy (MeV);Events"
      split_vars:
        - "numu_cc_qe"
        - "numu_cc_res"
        - "numu_cc_dis"
        - "numu_cc_coh"
        - "numu_cc_mec"
        - "nc"
        - "nue_cc"
      numu_cc_qe: ["numuCC0pQE"]
      numu_cc_res: ["numuCC0pRes", "numuCC1pRes"]
      numu_cc_dis: ["numuCC0pDIS", "numuCC1pDIS"]
      numu_cc_coh: ["numuCC0pCoh"]
      numu_cc_mec: ["numuCC0pMEC", "numuCC1pMEC"]
      nc: ["numuNC", "nueNC"]
      nue_cc: ["nueCC"]
  
  muon_angle:
    type: StackedHistProducer
    config:
      output_path: "muon_angle_stacked.root"
      plotvar_name: "muon_properties"
      plotvar_key: "angle"
      tagvar_name: "truth_mode"
      tagvar_key: "mode"
      nbins: 20
      xmin: -1.0
      xmax: 1.0
      title: "Muon cos(#theta);cos(#theta);Events"
      split_vars:
        - "numu_cc"
        - "nc"
        - "nue_cc"
      numu_cc: ["numuCC"]
      nc: ["numuNC", "nueNC"]
      nue_cc: ["nueCC"]

# Tag configurations
tags:
  truth_mode:
    muKE: 30.0
    pKE: 60.0
    piKE: 30.0
    gKE: 20.0
    ignore_gammas: false
    condense_nuemodes: true
```

### 2. Running the Analysis

```bash
# Run the analysis
python -m lantern_ana.core.lantern_ana numu_cc_analysis.yaml

# Create plots from the results
python -m lantern_ana.scripts.plot_results ./output/numu_cc/statistics.yaml ./output/numu_cc/plots
```

### 3. Analyzing the Results

After running the analysis, you'll have several outputs to examine:

- **ROOT Files**: Contain the analysis tree with selected events and calculated variables
- **Statistics File**: Contains selection efficiencies and cut statistics
- **Histograms**: Show distributions of physics quantities with stacked components
- **Plots**: Visualizations of selection efficiencies and physics distributions

### 4. Extracting Physics Results

With the processed data, you can extract physics results:

- Calculate selection efficiency as a function of energy
- Estimate background contamination
- Apply flux and detector corrections
- Extract cross-section measurements

## Advanced Topics

### Parallel Processing

For large datasets, you can run the analysis in parallel:

```bash
# Split analysis by dataset
python -m lantern_ana.core.lantern_ana numu_cc_analysis.yaml --dataset run3b_bnb_nu_overlay
python -m lantern_ana.core.lantern_ana numu_cc_analysis.yaml --dataset run3b_extbnb

# Merge results
python -m lantern_ana.scripts.merge_results ./output/numu_cc/run3b_*.root ./output/numu_cc/merged.root
```

### Systematic Uncertainties

To evaluate systematic uncertainties:

1. Create variations of your input files (e.g., with different detector parameters)
2. Run the analysis on each variation
3. Compare the results to estimate systematic uncertainties

```yaml
# Example systematic configuration
systematics:
  flux:
    variations:
      - name: "flux_up"
        weight_branch: "weight_flux_up"
      - name: "flux_down"
        weight_branch: "weight_flux_down"
  
  detector:
    variations:
      - name: "lce_up"
        input_files: "/path/to/lantern_ntuple_lce_up.root"
      - name: "lce_down"
        input_files: "/path/to/lantern_ntuple_lce_down.root"
```

### Custom Analysis Extensions

You can extend the framework with custom components:

- Create a subclass of `LanternAna` with additional functionality
- Add custom methods for specific analyses
- Create specialized producers for complex calculations

Example custom analysis class:

```python
from lantern_ana.core.lantern_ana import LanternAna

class NuMuCCAnalysis(LanternAna):
    """
    Specialized analysis class for CC muon neutrino studies.
    """
    
    def __init__(self, config_file, log_level="INFO"):
        super().__init__(config_file, log_level)
        
        # Add specialized producers
        self.add_energy_reconstruction()
    
    def add_energy_reconstruction(self):
        """Add energy reconstruction producers."""
        # Energy from track length
        from lantern_ana.producers.muon_energy import MuonEnergyProducer
        self.producer_manager.add_producer("muon_energy", MuonEnergyProducer, {})
        
        # Energy from calorimetry
        from lantern_ana.producers.calo_energy import CaloEnergyProducer
        self.producer_manager.add_producer("calo_energy", CaloEnergyProducer, {})
    
    def calculate_cross_section(self):
        """Calculate cross section from selected events."""
        # Implementation of cross-section calculation
        pass
```

## Common Analysis Examples

### Single Photon Selection

```yaml
# Cut configuration for single photon analysis
cuts:
  fiducial_cut:
    width: 10.0
    applyscc: true
  
  has_vertex:
    max_vertex_score: 0.8
  
  cosmic_rejection:
    max_cosmic_fraction: 0.3
  
  photon_selection:
    min_shower_energy: 50.0
    max_shower_energy: 1000.0
    min_photon_score: 0.7
  
  no_muons:
    max_muon_score: 0.3
  
  no_electrons:
    max_electron_score: 0.3

cut_logic: "fiducial_cut and has_vertex and cosmic_rejection and photon_selection and no_muons and no_electrons"
```

### π⁰ Selection

```yaml
# Cut configuration for π⁰ selection
cuts:
  fiducial_cut:
    width: 10.0
    applyscc: true
  
  has_vertex:
    max_vertex_score: 0.8
  
  two_photons:
    min_photons: 2
    max_photons: 2
    min_shower_energy: 30.0
    min_photon_score: 0.6
  
  invariant_mass:
    min_mass: 80.0
    max_mass: 200.0

cut_logic: "fiducial_cut and has_vertex and two_photons and invariant_mass"
```

### CC Inclusive Selection

```yaml
# Cut configuration for CC inclusive selection
cuts:
  fiducial_cut:
    width: 10.0
    applyscc: true
  
  has_vertex:
    max_vertex_score: 0.8
  
  cosmic_rejection:
    max_cosmic_fraction: 0.5
  
  track_containment:
    min_containment: 0.8
  
  has_track:
    min_track_length: 10.0
    min_track_score: 0.6

cut_logic: "fiducial_cut and has_vertex and cosmic_rejection and track_containment and has_track"
```

## Troubleshooting

### Common Issues and Solutions

#### Missing Datasets

**Problem**: `Dataset 'run3b_bnb_nu_overlay' not found`

**Solution**: Check the dataset configuration and ensure file paths are correct:
```yaml
datasets:
  run3b_bnb_nu_overlay:
    type: LanternNtupleDataset
    filepaths:
      - /correct/path/to/lantern_ntuple.root
```

#### Cut Registration Errors

**Problem**: `Cut 'my_cut' is not registered`

**Solution**: Ensure your cut is properly registered with the decorator:
```python
from lantern_ana.cuts.cut_factory import register_cut

@register_cut
def my_cut(ntuple, params):
    # Implementation
```

#### Producer Dependency Errors

**Problem**: `Circular dependency detected in producer configuration`

**Solution**: Check producer dependencies and ensure there are no circular references:
```python
def requiredInputs(self):
    # Fix circular dependency
    return ["gen2ntuple"]  # Not ["other_producer"] if that producer depends on this one
```

#### Memory Issues

**Problem**: Memory usage grows too large during processing

**Solution**: Process fewer events at a time or use parallel processing:
```yaml
max_events: 10000  # Process in smaller chunks
```

## Best Practices

1. **Start Small**: Begin with a small subset of data to test your configuration
2. **Validate Cuts**: Check cut efficiencies to ensure they're working as expected
3. **Monitor Producers**: Verify that producers are calculating correct values
4. **Use Logging**: Set appropriate log levels to aid debugging
5. **Version Control**: Keep track of configuration changes
6. **Document Analysis**: Comment your code and maintain analysis notes

## Reference

### Available Cuts

| Cut Name | Description | Parameters |
|----------|-------------|------------|
| `fiducial_cut` | Selects events with vertices in fiducial volume | `width`, `applyscc`, `usetruevtx` |
| `has_muon_track` | Selects events with muon-like tracks | `ke_threshold`, `min_track_length` |
| `cosmic_rejection` | Rejects cosmic ray events | `max_cosmic_fraction` |
| `track_containment` | Selects events with contained tracks | `min_containment` |
| `shower_energy` | Selects events with showers in energy range | `min_energy`, `max_energy` |
| `vertex_quality` | Selects events with good vertex reconstruction | `min_score` |

### Available Producers

| Producer Name | Description | Configuration Parameters |
|---------------|-------------|-------------------------|
| `VisibleEnergyProducer` | Calculates total visible energy | None |
| `MuonPropertiesProducer` | Extracts muon kinematics | None |
| `VertexPropertiesProducer` | Extracts vertex properties | None |
| `StackedHistProducer` | Creates stacked histograms | `plotvar_name`, `tagvar_name`, etc. |
| `ParticleIDProducer` | Calculates particle ID scores | `pdg_codes` |
| `EventClassificationProducer` | Classifies event topologies | `classification_types` |

### Available Tags

| Tag Name | Description | Parameters |
|----------|-------------|------------|
| `tag_truth_finalstate_mode` | Tags true final state | `muKE`, `pKE`, `piKE`, `gKE`, etc. |
| `tag_reco_topology` | Tags reconstructed topology | `topology_definitions` |
| `tag_interaction_type` | Tags interaction type | `interaction_definitions` |

## Support

For questions, bug reports, or feature requests, please contact the Lantern Analysis Framework team or open an issue in the GitHub repository.

---

Happy analyzing!
