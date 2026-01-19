#!/bin/bash

#SBATCH --job-name=lanternana
#SBATCH --output=lanternana.tki.%j.%N.log
#SBATCH --mem-per-cpu=4000
#SBATCH --cpus-per-task=1
#SBATCH --time=1-00:00:00
#SBATCH --partition=wongjiradlab
#SBATCH --error=lanternana.tki.%j.%N.err

# set the location of your copy of the repo here
WORKDIR=/cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/lantern_ana/studies/numu_cc_tki/

# location of container
container=/cluster/tufts/wongjiradlabnu/larbys/larbys-container/u20.04_cu111_cudnn8_torch1.9.0_minkowski_npm.sif

# setup singularity on the node
module load apptainer/1.2.4-suid

# run job script inside container
apptainer exec --nv --bind /cluster:/cluster $container bash -c "cd ${WORKDIR} && source run_tki_analysis.sh"

