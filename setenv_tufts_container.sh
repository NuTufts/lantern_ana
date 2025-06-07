#!/bin/bash

#source /cluster/home/lantern_scripts/setup_lantern_container.sh
#source setenv.sh
source /usr/local/root/bin/thisroot.sh

LANTERN_ANA_REPO_DIR=$PWD
LANTERN_ANA_BIN_DIR=${LANTERN_ANA_REPO_DIR}/bin
[[ ":$PYTHONPATH:" != *":${LANTERN_ANA_REPO_DIR}:"* ]] && export PYTHONPATH="${LANTERN_ANA_REPO_DIR}:${PYTHONPATH}"
[[ ":$PATH:" != *":${LANTERN_ANA_BIN_DIR}:"* ]] && export PATH="${LANTERN_ANA_BIN_DIR}:${PATH}"

