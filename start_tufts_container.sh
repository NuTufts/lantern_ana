#!/bin/bash

#module load singularity/3.5.3
module load apptainer/1.2.4-suid

BINDING_FOLDERS=/cluster/tufts/,/cluster/tufts/
#singularity shell --cleanenv -B ${BINDING_FOLDERS} /cluster/tufts/wongjiradlabnu/nutufts/containers/lantern_v2_me_06_03_prod/
apptainer shell -B ${BINDING_FOLDERS} /cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/u20.04_cu111_cudnn8_torch1.9.0_minkowski.sif
