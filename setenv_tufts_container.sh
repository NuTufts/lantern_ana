#!/bin/bash

source /cluster/home/lantern_scripts/setup_lantern_container.sh

LANTERN_ANA_REPO_DIR=$PWD
#echo ${LANTERN_ANA_REPO_DIR}
export PYTHONPATH=${LANTERN_ANA_REPO_DIR}:${PYTHONPATH}
