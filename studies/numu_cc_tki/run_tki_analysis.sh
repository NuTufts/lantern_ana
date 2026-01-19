#!/bin/bash

cd /cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/
source setenv_no_libtorchcpp.sh

cd /cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/lantern_ana/
source setenv_lantern_ana.sh

cd /cluster/tufts/wongjiradlabnu/twongj01/gen2/photon_analysis/lantern_ana/studies/numu_cc_tki/

run_lantern_ana.py run3b_1mil_tki_analysis.yaml
