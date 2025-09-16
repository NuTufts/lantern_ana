#!/bin/bash

# slurm submission script for making larmatch training data

#SBATCH --job-name=lantern_xsecfluxsys
#SBATCH --output=log_run_xsecflux_ana.log
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=4000
#SBATCH --time=4:00:00
#SBATCH --partition=wongjiradlab
##SBATCH --gres=gpu:p100:1
#SBATCH --error=griderr_run_xsecflux_ana.err

container=/cluster/tufts/wongjiradlabnu/larbys/larbys-container/u20.04_cu111_cudnn8_torch1.9.0_minkowski_npm.sif
LANTERN_ANA_DIR=/cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/lantern_ana/
WORKDIR=${LANTERN_ANA_DIR}/studies/xsecfluxsys/
CONFIG=${WORKDIR}/numu_run1_test.yaml

module load apptainer/1.2.4-suid
cd /cluster/tufts/
cd $WORKDIR

# mcc9_v13_bnbnue_corsika: 2000+461 files (train+valid split)
# running 5 files per job:  jobs 0-399 jobs needed for training set
# running 5 files per job:  jobs 400-493
apptainer exec --bind /cluster/tufts:/cluster/tufts ${container} bash -c "cd ${LANTERN_ANA_DIR} && source setenv_tufts_container.sh && cd ${WORKDIR} && ./run_xsecflux_ana.py ${CONFIG} >& aholog"


