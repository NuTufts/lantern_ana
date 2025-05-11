#!/bin/bash

# slurm submission script for running merged dlreco through larmatch and larflowreco
#SBATCH --job-name=studykpreco
#SBATCH --mem-per-cpu=8000
#SBATCH --time=8:00:00
#SBATCH --array=0
#SBATCH --cpus-per-task=3
#SBATCH --mem-per-cpu=4000
##SBATCH --partition=batch
#SBATCH --partition=wongjiradlab
##SBATCH --exclude=i2cmp006,s1cmp001,s1cmp002,s1cmp003,p1cmp041,c1cmp003,c1cmp004
##SBATCH --gres=gpu:p100:3
#SBATCH --error=griderr_study_kpreco.%j.%a.%N.log
#SBATCH --output=stdout_study_kpreco.%j.%a.%N.log

container=/cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/u20.04_cu111_torch1.9.0_minkowski.sif
BINDING=/cluster/tufts/wongjiradlabnu:/cluster/tufts/wongjiradlabnu,/cluster/tufts/wongjiradlab:/cluster/tufts/wongjiradlab
SCRIPT_DIR=/cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/lantern_ana/studies/keypoint/submission_scripts/

# ARGS
# (none)
module load singularity/3.5.3
singularity exec -B ${BINDING} ${container} bash -c "cd ${SCRIPT_DIR} && ./run_batch_study_kpreco.sh"

