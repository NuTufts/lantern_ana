#!/bin/bash

UBDL_DIR=/cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/ubdl
WORK_DIR=/cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/lantern_ana/studies/keypoint/

#FILELIST=/cluster/tufts/wongjiradlabnu/twongj01/gen2/dlgen2prod/larmatch_and_reco_scripts/filelists/filelist_mcc9_v40a_dl_run1_bnb_intrinsic_nue_overlay_CV.txt
FILELIST=${WORK_DIR}/submission_scripts/runid_list_mcc9_v28_wctagger_bnboverlay_kprecostudy.txt

NFILES=10
SAMPLE_NAME=mcc9_v28_wctagger_bnboverlay
OUTDIR=${WORK_DIR}/output/${SAMPLE_NAME}/

alias python=python3

cd ${UBDL_DIR}
source setenv_py3_container.sh
source configure_container.sh

maxFileCount=`wc -l < $FILELIST`
let firstfile="${SLURM_ARRAY_TASK_ID}*${NFILES}"
let lastfile="$firstfile+${NFILES}-1"
echo "firstfile=${firstfile}"
echo "lastfile=${lastfile}"

local_jobdir=`printf /tmp/lantern_kprecostudy_jobid%05d_${SAMPLE_NAME}_${SLURM_JOB_ID} ${SLURM_ARRAY_TASK_ID}`
#local_jobdir=`printf /tmp/lantern_kprecostudy_jobid%05d_${SAMPLE_NAME} ${SLURM_ARRAY_TASK_ID}`
mkdir -p $local_jobdir
mkdir -p $OUTDIR

# go to local dir
cd $local_jobdir
cp $WORK_DIR/run_larmatchme_mc.sh .
cp $WORK_DIR/study_kpreco.py .
chmod +x run_larmatchme_mc.sh

mkdir -p $OUTDIR

for n in $(seq $firstfile $lastfile); do
  if (($n > $maxFileCount)); then
    break
  fi
  let lineno="${n}+1"
  fileid=`sed -n ${lineno}p ${FILELIST} | awk '{ print $1 }'`
  dlmergedfile=`sed -n ${lineno}p ${FILELIST} | awk '{ print $2 }'`
  dlmergedbase=$(basename ${dlmergedfile})
  lmfile=`printf larmatch_${SAMPLE_NAME}_fileid%05d.root ${fileid}`
  out=`printf kpreco_study_${SAMPLE_NAME}_fileid%05d.root ${fileid}`
  
  echo "fileid: ${fileid}"
  echo "dlmergedfile: ${dlmergedfile}"
  echo "lmfile: ${lmfile}"
  echo "out: ${out}"

  if [ -n "$dlmergedfile" ]; then
      cp $dlmergedfile .        
      cmd="./run_larmatchme_mc.sh ${dlmergedbase} ${lmfile}"
      echo $cmd
      $cmd
      python3 study_kpreco.py $lmfile $dlmergedbase
      mv out_kpreco_study.root $out
      rm $dlmergedbase
      rm $lmfile
  fi
done
haddfile=`printf kpreco_study_${SAMPLE_NAME}_jobid%04d.root ${SLURM_ARRAY_TASK_ID}`
haddcmd="hadd -f $haddfile kpreco_study_${SAMPLE_NAME}_fileid*.root"
echo $haddcmd
$haddcmd

cpcmd="cp ${haddfile} ${OUTDIR}/"
echo $cpcmd
$cpcmd

cd /tmp
rm -r $local_jobdir

echo "DONE"




