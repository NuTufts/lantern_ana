#!/bin/bash

BINDING_FOLDERS=/cluster/tufts/,/cluster/tufts/
singularity shell --cleanenv -B ${BINDING_FOLDERS} /cluster/tufts/wongjiradlabnu/nutufts/containers/lantern_v2_me_06_03_prod/
