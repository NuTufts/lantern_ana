# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lantern Analysis Framework (lantern_ana) is a Python-based system for analyzing data from liquid argon time projection chamber (LArTPC) neutrino experiments, specifically MicroBooNE data. The framework processes ROOT ntuple files from the gen2ntuple system to perform physics analyses.

## Environment Setup

This project requires the ubdl dependencies and runs inside containers. Key setup commands:

### On Tufts Cluster
```bash
# Start container
module load singularity/3.5.3
singularity shell --cleanenv /cluster/tufts/wongjiradlabnu/nutufts/containers/lantern_v2_me_06_03_prod/
# Or use helper script
./start_tufts_container.sh

# Setup environment
source setenv_tufts_container.sh
```

### General Environment Setup
```bash
# Setup Python path and environment
source setenv_lantern_ana.sh

# Test installation
python3 -c "import lantern_ana"
```

## Core Architecture

The framework uses a producer-first architecture with four main components:

### 1. Dataset System (`lantern_ana/io/`)
- `DatasetFactory`: Creates dataset instances from YAML configuration
- `LanternNtupleDataset`: Handles ROOT ntuple file access
- `SampleDataset`: Manages collections of files with metadata

### 2. Producer System (`lantern_ana/producers/`)
- Producers inherit from `ProducerBaseClass`
- Calculate derived physics quantities (vertex properties, energy estimates, etc.)
- `ProducerManager`: Handles execution order and dependency resolution
- `ProducerFactory`: Auto-discovers and instantiates producers
- Outputs stored in ROOT trees and histograms

### 3. Cut System (`lantern_ana/cuts/`)
- Standalone functions for event selection criteria
- `CutFactory`: Manages cut registration and logical combinations
- Cuts receive producer outputs via parameters in producer-first mode
- Supports complex logical expressions for combining cuts

### 4. Tag System (`lantern_ana/tags/`)
- Functions that classify events based on physics properties
- Primarily for truth-level Monte Carlo categorization
- `TagFactory`: Auto-discovers and manages tag functions

### 5. Main Analysis Class (`lantern_ana_class.py`)
- `EnhancedLanternAna`: Main framework orchestrator
- Configurable via YAML files
- Supports producer-first processing mode where producers run before cuts

## Configuration System

Analysis configured via YAML files with sections for:
- `datasets`: Data file specifications and metadata
- `producers`: Producer configurations and parameters
- `cuts`: Cut definitions and logical combinations
- `tags`: Event classification settings
- `output_dir`: Results output location
- `producer_first_mode`: Architecture mode (default: true)

## Running Analysis

### Basic Usage
```python
from lantern_ana import LanternAna

# Load configuration and run
ana = LanternAna("config.yaml")
ana.run()
```

### Command Line
```bash
# Run analysis with specific datasets
python -m lantern_ana.lantern_ana_class config.yaml --dataset dataset1 --dataset dataset2

# Set logging level
python -m lantern_ana.lantern_ana_class config.yaml --log-level DEBUG
```

## Key Workflow

1. **Initialization**: Framework discovers available producers, cuts, and tags
2. **Dataset Loading**: ROOT files loaded via dataset configuration
3. **Event Processing**: For each event:
   - Producers calculate derived quantities first
   - Cuts evaluate using producer outputs
   - Results stored in output ROOT trees
4. **Output**: Analysis trees with producer variables and cut results

## Component Development

### Adding Producers
- Inherit from `ProducerBaseClass`
- Implement `process()` method
- Place in `lantern_ana/producers/` for auto-discovery
- Define dependencies via `get_dependencies()`

### Adding Cuts
- Standalone functions with `@register_cut` decorator
- Place in `lantern_ana/cuts/` for auto-discovery
- Access producer data via `params['producer_data']`

### Adding Tags
- Functions with `@register_tag` decorator
- Place in `lantern_ana/tags/` for auto-discovery

## Dependencies
- Python 3 with ROOT, numpy, yaml, yamlinclude
- ubdl repository libraries (containerized)
- gen2ntuple for data format understanding