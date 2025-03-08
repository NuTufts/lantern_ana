#!/bin/bash

# slurm submission script for making larmatch training data

#SBATCH --job-name=extractevent
#SBATCH --output=extract_event_%j.log
#SBATCH --mem-per-cpu=8000
#SBATCH --time=8:00:00
#SBATCH --array=0-15
##SBATCH --partition=preempt
#SBATCH --partition=wongjiradlab
#SBATCH --partition=wongjiradlab
#SBATCH --error=extract_event.%j.%N.err

container=/cluster/tufts/wongjiradlabnu/twongjirad/gen2/photon_analysis/u20_.sif
UBDL_DIR=/cluster/tufts/wongjiradlabnu/twongjirad/gen2/photon_analysis/ubdl
LANTERN_PHOTON_DIR=/cluster/tufts/wongjiradlabnu/twongjirad/gen2/photon_analysis/lantern_photon
EVENT_LIST=${LANTERN_PHOTON_DIR}/run3_bnbnu_eventlist.txt
SAMPLE_NAME=run3_bnbnu
OUTPUT_DIR=${LANTERN_PHOTON_DIR}/output_extracted_events/

module load singularity/3.5.3
cd /cluster/tufts/

srun singularity exec ${container} bash -c "cd ${LANTER_PHOTON_DIR} && source run_extract_event.sh ${SAMPLE_NAME} ${UBDL_DIR} ${LANTERN_PHOTON_DIR} ${EVENT_LIST} ${OUTPUT_DIR}"


