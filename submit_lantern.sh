#!/bin/bash
#SBATCH --partition=wongjiradlab
#SBATCH --time=1:00:00
#SBATCH --job-name=lantern_ana
#SBATCH --output=lantern_ana_%j.out
#SBATCH --error=lantern_ana_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB

# Change to working directory
cd /cluster/tufts/wongjiradlabnu/zimani01/lantern/lantern_ana/

# Load Singularity
module load singularity

# Start Singularity Container and setup environment
source start_tufts_container.sh
source setenv_tufts_container.sh

# Run the analysis
bash -c "run_lantern_ana.py all_runs_mmr/run3mil/run3mil_numu_detsys.yaml"