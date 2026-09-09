# flashPEProducer.py
"""
Custom Producer: flashPEProducer

Purpose: Extract raw flash PE variables for studying run-to-run changes in PMT response.

Branch locations in the input ROOT files:
  nuselection/NeutrinoSelectionFilter (friend tree):
    _opfilter_pe_beam, _opfilter_pe_veto, flash_pe_flash_matching

  singlephotonana/vertex_tree (friend tree):
    m_flash_optfltr_pe_beam/tot, m_flash_optfltr_pe_veto/tot
    reco_num_flashes, reco_num_flashes_in_beamgate
    reco_flash_total_pe, reco_flash_total_pe_in_beamgate
    reco_flash_time, reco_flash_time_in_beamgate, reco_flash_time_width
    reco_flash_abs_time, reco_flash_frame
    reco_flash_ycenter, reco_flash_ycenter_in_beamgate, reco_flash_ywidth
    reco_flash_zcenter, reco_flash_zcenter_in_beamgate, reco_flash_zwidth

For vector branches, scalar summaries are extracted for the brightest (max PE) flash
in each category. -9999 sentinels indicate the branch was absent or no flashes exist.

Example usage in YAML config:
    producers:
      flashpe:
        type: flashPEProducer
        config: {}
"""

import numpy as np
from typing import Dict, Any, List
from array import array
import ROOT
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register

@register
class flashPEProducer(ProducerBaseClass):

    _NSEL   = "nuselection/NeutrinoSelectionFilter"
    _SPHANA = "singlephotonana/vertex_tree"

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

        self._vars = {
            # --- nuselection/NeutrinoSelectionFilter ---
            'opfilter_pe_beam':             array('f', [0.0]),
            'opfilter_pe_veto':             array('f', [0.0]),
            'flash_pe_matched':             array('f', [0.0]),

            # --- singlephotonana/vertex_tree: optical filter alternates ---
            'm_opfilter_pe_beam':           array('d', [0.0]),
            'm_opfilter_pe_beam_tot':       array('d', [0.0]),
            'm_opfilter_pe_veto':           array('d', [0.0]),
            'm_opfilter_pe_veto_tot':       array('d', [0.0]),

            # --- flash counts ---
            'num_flashes':                  array('i', [0]),
            'num_flashes_beamgate':         array('i', [0]),

            # --- all-flash brightest-flash summaries ---
            'max_flash_pe':                 array('d', [0.0]),
            'max_flash_time':               array('d', [0.0]),
            'max_flash_abs_time':           array('d', [0.0]),
            'max_flash_frame':              array('i', [0]),
            'max_flash_time_width':         array('d', [0.0]),
            'max_flash_ycenter':            array('d', [0.0]),
            'max_flash_ywidth':             array('d', [0.0]),
            'max_flash_zcenter':            array('d', [0.0]),
            'max_flash_zwidth':             array('d', [0.0]),

            # --- in-beamgate brightest-flash summaries ---
            'max_flash_beamgate_pe':         array('d', [0.0]),
            'max_flash_beamgate_time':       array('d', [0.0]),
            'max_flash_beamgate_time_width': array('d', [0.0]),
            'max_flash_beamgate_ycenter':    array('d', [0.0]),
            'max_flash_beamgate_ywidth':     array('d', [0.0]),
            'max_flash_beamgate_zcenter':    array('d', [0.0]),
            'max_flash_beamgate_zwidth':     array('d', [0.0]),
        }

    def setDefaultValues(self):
        super().setDefaultValues()
        for varname, var in self._vars.items():
            if var.typecode == 'i':
                var[0] = 0
            else:
                var[0] = -9999.0

    def prepareStorage(self, output_tree):
        type_map = {'f': 'F', 'd': 'D', 'i': 'I'}
        for var_name, var_array in self._vars.items():
            branch_type = f"{self.name}_{var_name}/{type_map[var_array.typecode]}"
            output_tree.Branch(f"{self.name}_{var_name}", var_array, branch_type)

    def requiredInputs(self) -> List[str]:
        return ["gen2ntuple"]

    @staticmethod
    def _get(tree, branch, default=-9999.0):
        """Read a scalar branch from a TTree/TChain; return default on failure."""
        if tree is None:
            return default
        try:
            return getattr(tree, branch)
        except AttributeError:
            return default

    @staticmethod
    def _get_vec(tree, branch):
        """Return a list from a vector branch, or None on failure."""
        if tree is None:
            return None
        try:
            vec = getattr(tree, branch)
            return [vec[i] for i in range(vec.size())]
        except (AttributeError, TypeError):
            return None

    def _fill_brightest(self, pe_list, var_prefix, extra_vecs):
        """
        Find the index of the brightest flash in pe_list and fill output vars
        for that flash using the corresponding entries in extra_vecs.

        extra_vecs: dict mapping output var suffix -> list of values (same length as pe_list)
        """
        if not pe_list:
            self._vars[f'{var_prefix}_pe'][0] = 0.0
            for suffix in extra_vecs:
                default = 0 if self._vars[f'{var_prefix}_{suffix}'].typecode == 'i' else -9999.0
                self._vars[f'{var_prefix}_{suffix}'][0] = default
            return

        idx = int(np.argmax(pe_list))
        self._vars[f'{var_prefix}_pe'][0] = pe_list[idx]
        for suffix, vals in extra_vecs.items():
            if vals is not None and idx < len(vals):
                self._vars[f'{var_prefix}_{suffix}'][0] = vals[idx]
            else:
                default = 0 if self._vars[f'{var_prefix}_{suffix}'].typecode == 'i' else -9999.0
                self._vars[f'{var_prefix}_{suffix}'][0] = default

    def processEvent(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        ntuple = data["gen2ntuple"]

        nsel   = ntuple.GetFriend(self._NSEL)
        sphana = ntuple.GetFriend(self._SPHANA)

        # nuselection scalars
        self._vars['opfilter_pe_beam'][0] = self._get(nsel, '_opfilter_pe_beam')
        self._vars['opfilter_pe_veto'][0] = self._get(nsel, '_opfilter_pe_veto')
        self._vars['flash_pe_matched'][0] = self._get(nsel, 'flash_pe_flash_matching')

        # singlephotonana optical filter scalars
        self._vars['m_opfilter_pe_beam'][0]     = self._get(sphana, 'm_flash_optfltr_pe_beam')
        self._vars['m_opfilter_pe_beam_tot'][0] = self._get(sphana, 'm_flash_optfltr_pe_beam_tot')
        self._vars['m_opfilter_pe_veto'][0]     = self._get(sphana, 'm_flash_optfltr_pe_veto')
        self._vars['m_opfilter_pe_veto_tot'][0] = self._get(sphana, 'm_flash_optfltr_pe_veto_tot')

        # flash counts
        nflash          = self._get(sphana, 'reco_num_flashes', default=0)
        nflash_bg       = self._get(sphana, 'reco_num_flashes_in_beamgate', default=0)
        nflash          = int(nflash)   if nflash   != -9999.0 else 0
        nflash_bg       = int(nflash_bg) if nflash_bg != -9999.0 else 0
        self._vars['num_flashes'][0]          = nflash
        self._vars['num_flashes_beamgate'][0] = nflash_bg

        # all-flash vector branches
        pe_all      = self._get_vec(sphana, 'reco_flash_total_pe')
        time_all    = self._get_vec(sphana, 'reco_flash_time')
        abstime_all = self._get_vec(sphana, 'reco_flash_abs_time')
        frame_all   = self._get_vec(sphana, 'reco_flash_frame')
        twidth_all  = self._get_vec(sphana, 'reco_flash_time_width')
        yc_all      = self._get_vec(sphana, 'reco_flash_ycenter')
        yw_all      = self._get_vec(sphana, 'reco_flash_ywidth')
        zc_all      = self._get_vec(sphana, 'reco_flash_zcenter')
        zw_all      = self._get_vec(sphana, 'reco_flash_zwidth')

        self._fill_brightest(
            pe_all if pe_all else [], 'max_flash',
            {'time': time_all, 'abs_time': abstime_all, 'frame': frame_all,
             'time_width': twidth_all, 'ycenter': yc_all, 'ywidth': yw_all,
             'zcenter': zc_all, 'zwidth': zw_all}
        )

        # in-beamgate vector branches
        pe_bg      = self._get_vec(sphana, 'reco_flash_total_pe_in_beamgate')
        time_bg    = self._get_vec(sphana, 'reco_flash_time_in_beamgate')
        twidth_bg  = self._get_vec(sphana, 'reco_flash_time_width')   # no beamgate-specific version
        yc_bg      = self._get_vec(sphana, 'reco_flash_ycenter_in_beamgate')
        yw_bg      = self._get_vec(sphana, 'reco_flash_ywidth')        # no beamgate-specific version
        zc_bg      = self._get_vec(sphana, 'reco_flash_zcenter_in_beamgate')
        zw_bg      = self._get_vec(sphana, 'reco_flash_zwidth')        # no beamgate-specific version

        self._fill_brightest(
            pe_bg if pe_bg else [], 'max_flash_beamgate',
            {'time': time_bg, 'time_width': twidth_bg,
             'ycenter': yc_bg, 'ywidth': yw_bg,
             'zcenter': zc_bg, 'zwidth': zw_bg}
        )

        out = {varname: var[0] for varname, var in self._vars.items()}
        return out

    def finalize(self):
        super().finalize()
        return
