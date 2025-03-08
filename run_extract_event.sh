#!/bin/bash

SAMPLE_NAME=$1
UBDL_DIR=$2
LANTERN_PHOTON_DIR=$3
EVENT_LIST=$4
OUTPUT_DIR=$5

# setup environment
# ubdl allows us to read larlite and larcv objects
# it also provides plotting methods from lardly
cd $UBDL_DIR
source setenv_py3.sh
source configure.sh
export PYTHONPATH=${LANTERN_PHOTON_DIR}:${PYTHONPATH}

stride=5
jobid=${SLURM_ARRAY_TASK_ID}
let startline=$(expr "${stride}*${jobid}")

jobdir=`printf "/tmp/extract_event_jobid%03d" $jobid`
mkdir ${jobdir}
cd ${jobdir}
mkdir -p ${OUTPUT_DIR}

for i in {1..5}
do
    let lineno=$startline+$i
    run=`sed -n ${lineno}p $EVENT_LIST | awk '{ print $1 }'`
    subrun=`sed -n ${lineno}p $EVENT_LIST | awk '{ print $2 }'`
    event=`sed -n ${lineno}p $EVENT_LIST | awk '{ print $3 }'`
    fileid=`sed -n ${lineno}p $EVENT_LIST | awk '{ print $4 }'`
    vx=`sed -n ${lineno}p $EVENT_LIST | awk '{ print $5 }'`
    vy=`sed -n ${lineno}p $EVENT_LIST | awk '{ print $6 }'`
    vz=`sed -n ${lineno}p $EVENT_LIST | awk '{ print $7 }'`
    ntracks=`sed -n ${lineno}p $EVENT_LIST | awk '{ print $8 }'`
    nshowers=`sed -n ${lineno}p $EVENT_LIST | awk '{ print $9 }'`
    
    python3 ${LANTERN_PHOTON_DIR}/get_file_from_rse.py -d ${SAMPLE_NAME} -f ${fileid} --prefix=${LANTERN_PHOTON_DIR} --out input_files.txt
    dlmerged=`head -n 1 input_files.txt | awk '{ print $1 }'`
    recofile=`head -n 1 input_files.txt | awk '{ print $2 }'`

    COMMAND="python3 ${LANTERN_PHOTON_DIR}/extract_event.py -dl ${dlmerged} -k ${recofile} -r ${run} -s ${subrun} -e ${event} -vx ${vx} -vy ${vy} -vz ${vz} -nt ${ntracks} -ns ${nshowers}"
    echo $COMMAND
    $COMMAND
done

cp *.html ${OUTPUT_DIR}/
cd /tmp
rm -r $jobdir


