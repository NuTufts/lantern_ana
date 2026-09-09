"""
Producer that saves all POT-related variables from the ntuple files.

Per-event variables (requires singlephotonana/vertex_tree as a friend tree):
  pot_per_event    - POT per event (singlephotonana/vertex_tree)
  pot_per_subrun   - POT per subrun for the event's subrun (singlephotonana/vertex_tree)

File-level totals (computed once at init, constant per event).
Pass filepaths in the producer config to enable these:
  pot_lantern_totGoodPOT    - sum(lantern/potTree::totGoodPOT)
  pot_lantern_totPOT        - sum(lantern/potTree::totPOT)
  pot_nusel_subrun          - sum(nuselection/SubRun::pot)
  pot_singlephoton_subrun   - sum(singlephotonana/run_subrun_tree::subrun_pot)
  pot_wcp_tor875            - sum(wcpselection/T_pot::pot_tor875)
  pot_wcp_tor875good        - sum(wcpselection/T_pot::pot_tor875good)

Example YAML config:
  potinfo:
    type: potInfoProducer
    config:
      filepaths:
        - /path/to/file1.root
        - /path/to/file2.root
"""

import numpy as np
from typing import Dict, Any, List
from array import array

from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register


@register
class potInfoProducer(ProducerBaseClass):
    """
    Saves all POT-related ntuple variables for cross-method POT comparisons.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

        self._filepaths = config.get('filepaths', [])

        # Per-event variables (from singlephotonana/vertex_tree friend tree)
        self._pot_per_event  = array('d', [-1.0])
        self._pot_per_subrun = array('d', [-1.0])

        # File-level totals from subrun-level POT trees
        self._pot_lantern_totGoodPOT       = array('d', [-1.0])
        self._pot_lantern_totPOT           = array('d', [-1.0])
        self._pot_nusel_subrun             = array('d', [-1.0])
        self._pot_singlephoton_subrun      = array('d', [-1.0])
        self._pot_wcp_tor875               = array('d', [-1.0])
        self._pot_wcp_tor875good           = array('d', [-1.0])

        if self._filepaths:
            self._compute_file_level_pot()

    # ------------------------------------------------------------------
    def _compute_file_level_pot(self):
        """Sum all subrun-level POT trees across the configured file list."""
        try:
            import uproot
        except ImportError:
            print("Warning [potInfoProducer]: uproot not available; "
                  "file-level POT totals will remain -1.")
            return

        totals = {
            'pot_lantern_totGoodPOT':  0.0,
            'pot_lantern_totPOT':      0.0,
            'pot_nusel_subrun':        0.0,
            'pot_singlephoton_subrun': 0.0,
            'pot_wcp_tor875':          0.0,
            'pot_wcp_tor875good':      0.0,
        }

        for fpath in self._filepaths:
            try:
                with uproot.open(fpath) as f:
                    keys = f.keys()

                    if "lantern/potTree;1" in keys or "lantern/potTree" in keys:
                        t = f["lantern/potTree"]
                        t_keys = t.keys()
                        if "totGoodPOT" in t_keys:
                            totals['pot_lantern_totGoodPOT'] += float(
                                np.sum(t["totGoodPOT"].array(library="np")))
                        if "totPOT" in t_keys:
                            totals['pot_lantern_totPOT'] += float(
                                np.sum(t["totPOT"].array(library="np")))

                    if "nuselection/SubRun;1" in keys or "nuselection/SubRun" in keys:
                        t = f["nuselection/SubRun"]
                        if "pot" in t.keys():
                            totals['pot_nusel_subrun'] += float(
                                np.sum(t["pot"].array(library="np")))

                    spk = "singlephotonana/run_subrun_tree"
                    if spk + ";1" in keys or spk in keys:
                        t = f[spk]
                        if "subrun_pot" in t.keys():
                            totals['pot_singlephoton_subrun'] += float(
                                np.sum(t["subrun_pot"].array(library="np")))

                    if "wcpselection/T_pot;1" in keys or "wcpselection/T_pot" in keys:
                        t = f["wcpselection/T_pot"]
                        t_keys = t.keys()
                        if "pot_tor875" in t_keys:
                            totals['pot_wcp_tor875'] += float(
                                np.sum(t["pot_tor875"].array(library="np")))
                        if "pot_tor875good" in t_keys:
                            totals['pot_wcp_tor875good'] += float(
                                np.sum(t["pot_tor875good"].array(library="np")))

            except Exception as e:
                print(f"Warning [potInfoProducer]: could not read {fpath}: {e}")

        self._pot_lantern_totGoodPOT[0]  = totals['pot_lantern_totGoodPOT']
        self._pot_lantern_totPOT[0]      = totals['pot_lantern_totPOT']
        self._pot_nusel_subrun[0]        = totals['pot_nusel_subrun']
        self._pot_singlephoton_subrun[0] = totals['pot_singlephoton_subrun']
        self._pot_wcp_tor875[0]          = totals['pot_wcp_tor875']
        self._pot_wcp_tor875good[0]      = totals['pot_wcp_tor875good']

    # ------------------------------------------------------------------
    def setDefaultValues(self):
        self._pot_per_event[0]  = -1.0
        self._pot_per_subrun[0] = -1.0
        # File-level totals are set once at init and kept constant;
        # don't reset them here.

    def prepareStorage(self, output) -> None:
        """Register output branches in the analysis TTree."""
        def _branch(name, arr):
            output.Branch(f"{self.name}_{name}", arr, f"{self.name}_{name}/D")

        _branch("pot_per_event",           self._pot_per_event)
        _branch("pot_per_subrun",          self._pot_per_subrun)
        _branch("pot_lantern_totGoodPOT",  self._pot_lantern_totGoodPOT)
        _branch("pot_lantern_totPOT",      self._pot_lantern_totPOT)
        _branch("pot_nusel_subrun",        self._pot_nusel_subrun)
        _branch("pot_singlephoton_subrun", self._pot_singlephoton_subrun)
        _branch("pot_wcp_tor875",          self._pot_wcp_tor875)
        _branch("pot_wcp_tor875good",      self._pot_wcp_tor875good)

    def requiredInputs(self) -> List[str]:
        return ["gen2ntuple"]

    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        self.setDefaultValues()
        ntuple = data["gen2ntuple"]

        # Per-event POT from singlephotonana/vertex_tree (requires friend tree)
        if hasattr(ntuple, 'pot_per_event'):
            self._pot_per_event[0] = ntuple.pot_per_event
        if hasattr(ntuple, 'pot_per_subrun'):
            self._pot_per_subrun[0] = ntuple.pot_per_subrun

        return {
            'pot_per_event':           self._pot_per_event[0],
            'pot_per_subrun':          self._pot_per_subrun[0],
            'pot_lantern_totGoodPOT':  self._pot_lantern_totGoodPOT[0],
            'pot_lantern_totPOT':      self._pot_lantern_totPOT[0],
            'pot_nusel_subrun':        self._pot_nusel_subrun[0],
            'pot_singlephoton_subrun': self._pot_singlephoton_subrun[0],
            'pot_wcp_tor875':          self._pot_wcp_tor875[0],
            'pot_wcp_tor875good':      self._pot_wcp_tor875good[0],
        }

    def finalize(self):
        return
