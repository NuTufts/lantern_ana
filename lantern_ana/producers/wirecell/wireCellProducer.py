import os,sys

# lantern_ana/producers/numu_cc_producers.py
import numpy as np
import ROOT
from array import array
from lantern_ana.producers.producerBaseClass import ProducerBaseClass
from lantern_ana.producers.producer_factory import register
from lantern_ana.tags.tag_factory import TagFactory

@register
class wireCellProducer(ProducerBaseClass):
	"""
	Producer that handles various neutrino selection criteria, including:
	- CC νe selections (fully and partially contained)
	- CC νμ π0 selections (fully and partially contained)
	- NC π0 selections
	- CC νμ selections excluding π0 (fully and partially contained)
	"""
	
	def __init__(self, name, config):
		super().__init__(name, config)
		
		# Previous variables
		self.nue_score = array('f', [-999.0])
		self.numu_cc_flag = array('f', [-1.0])
		self.match_isFC = array('f', [-1.0])
		self.nueCC_full = array('i', [-1])
		self.nueCC_partial = array('i', [-1])
		
		# New variables for various selections
		# FC CC π0 selection
		self.fccc_pio = array('i', [-1])
		# PC CC π0 selection
		self.pccc_pio = array('i', [-1])
		# NC π0 selection
		self.nc_pio = array('i', [-1])
		# FC CC νμ excluding π0
		self.fccc_numu_exclpio = array('i', [-1])
		# PC CC νμ excluding π0
		self.pccc_numu_exclpio = array('i', [-1])

		# Variables for π0 selection criteria
		self.numu_score = array('f', [-999.0])
		self.pio_flag = array('f', [-1.0])
		self.pio_1_dis_1 = array('f', [-999.0])
		self.pio_1_energy_1 = array('f', [-999.0])
		self.pio_1_energy_2 = array('f', [-999.0])
		self.pio_1_dis_2 = array('f', [-999.0])
		self.pio_2_v_angle2 = array('f', [-999.0])
		self.pio_1_mass = array('f', [-999.0])

	def setDefaultValues(self):
		"""Set default values for all variables."""
		super().setDefaultValues()
		# Default values for previous variables
		self.nue_score[0] = -10.0
		self.numu_cc_flag[0] = -1.0
		self.match_isFC[0] = -1.0
		self.nueCC_full[0] = -1
		self.nueCC_partial[0] = -1
		
		# Default values for new selection flags
		self.fccc_pio[0] = -1
		self.pccc_pio[0] = -1
		self.nc_pio[0] = -1
		self.fccc_numu_exclpio[0] = -1
		self.pccc_numu_exclpio[0] = -1
		
		# Default values for π0 selection criteria
		self.numu_score[0] = -999.0
		self.pio_flag[0] = -1.0
		self.pio_1_dis_1[0] = -999.0
		self.pio_1_energy_1[0] = -999.0
		self.pio_1_energy_2[0] = -999.0
		self.pio_1_dis_2[0] = -999.0
		self.pio_2_v_angle2[0] = -999.0
		self.pio_1_mass[0] = -999.0

	def prepareStorage(self, output):
		"""Set up branches in the output ROOT TTree."""
		# Previous branches
		output.Branch(f"{self.name}_nue_score", self.nue_score, f"{self.name}_nue_score/F")
		output.Branch(f"{self.name}_numu_cc_flag", self.numu_cc_flag, f"{self.name}_numu_cc_flag/F")
		output.Branch(f"{self.name}_match_isFC", self.match_isFC, f"{self.name}_match_isFC/F")
		output.Branch(f"{self.name}_nueCC_full", self.nueCC_full, f"{self.name}_nueCC_full/I")
		output.Branch(f"{self.name}_nueCC_partial", self.nueCC_partial, f"{self.name}_nueCC_partial/I")
		
		# New branches for selections
		output.Branch(f"{self.name}_fccc_pio", self.fccc_pio, f"{self.name}_fccc_pio/I")
		output.Branch(f"{self.name}_pccc_pio", self.pccc_pio, f"{self.name}_pccc_pio/I")
		output.Branch(f"{self.name}_nc_pio", self.nc_pio, f"{self.name}_nc_pio/I")
		output.Branch(f"{self.name}_fccc_numu_exclpio", self.fccc_numu_exclpio, f"{self.name}_fccc_numu_exclpio/I")
		output.Branch(f"{self.name}_pccc_numu_exclpio", self.pccc_numu_exclpio, f"{self.name}_pccc_numu_exclpio/I")
		
		# Branches for π0 selection criteria
		output.Branch(f"{self.name}_numu_score", self.numu_score, f"{self.name}_numu_score/F")
		output.Branch(f"{self.name}_pio_flag", self.pio_flag, f"{self.name}_pio_flag/F")
		output.Branch(f"{self.name}_pio_1_dis_1", self.pio_1_dis_1, f"{self.name}_pio_1_dis_1/F")
		output.Branch(f"{self.name}_pio_1_energy_1", self.pio_1_energy_1, f"{self.name}_pio_1_energy_1/F")
		output.Branch(f"{self.name}_pio_1_energy_2", self.pio_1_energy_2, f"{self.name}_pio_1_energy_2/F")
		output.Branch(f"{self.name}_pio_1_dis_2", self.pio_1_dis_2, f"{self.name}_pio_1_dis_2/F")
		output.Branch(f"{self.name}_pio_2_v_angle2", self.pio_2_v_angle2, f"{self.name}_pio_2_v_angle2/F")
		output.Branch(f"{self.name}_pio_1_mass", self.pio_1_mass, f"{self.name}_pio_1_mass/F")

	def requiredInputs(self):
		"""Specify required inputs."""
		return ["gen2ntuple"]
	
	def processEvent(self, data, params):
		"""Process event and apply selections."""
		self.setDefaultValues()
		ismc = params.get('ismc', False)

		ntuple = data["gen2ntuple"]
		

		print(ntuple.match_isFC)
		print(ntuple.pio_flag)
		print(ntuple.pio_2_v_angle2)
		print("~~~")

		# Load the values from the ntuple
		self.nue_score[0] = ntuple.nue_score
		self.numu_cc_flag[0] = ntuple.numu_cc_flag
		self.match_isFC[0] = ntuple.match_isFC
		
		# Assume these π0 variables are already in the ntuple
		# In a real implementation, these would come from the ntuple or be calculated
		self.numu_score[0] = ntuple.numu_score
		self.pio_flag[0] = ntuple.pio_flag
		self.pio_1_dis_1[0] = ntuple.pio_1_dis_1
		self.pio_1_energy_1[0] = ntuple.pio_1_energy_1
		self.pio_1_energy_2[0] = ntuple.pio_1_energy_2
		self.pio_1_dis_2[0] = ntuple.pio_1_dis_2
		try: 
			self.pio_2_v_angle2[0] = ntuple.pio_2_v_angle2
		except: 
			pass 
		self.pio_1_mass[0] = ntuple.pio_1_mass
		
		# Original νeCC selections
		## Fully contained CC nue 
		if (self.nue_score[0] > 7.0 and self.numu_cc_flag[0] >= 0 and self.match_isFC[0] == 1): 
			self.nueCC_full[0] = 1
			
		## Partially contained CC nue
		if (self.nue_score[0] > 7.0 and self.numu_cc_flag[0] >= 0 and self.match_isFC[0] == 0): 
			self.nueCC_partial[0] = 1
		
		# Check if the event passes the νeCC selection criteria (used as exclusion for other selections)
		passes_nueCC_selection = self.nue_score[0] >= 7.0 and self.numu_cc_flag[0] >= 0

		# Apply π0 selection criteria
		passes_pio_selection = (
			self.pio_flag[0] == 1 and
			self.pio_1_dis_1[0] < 9 and
			self.pio_1_energy_1[0] > 40 and
			self.pio_1_energy_2[0] > 25 and
			self.pio_1_dis_1[0] < 110 and
			self.pio_1_dis_2[0] < 120 and
			0 < self.pio_2_v_angle2[0] < 174 and
			22 < self.pio_1_mass[0] < 300 and
			not passes_nueCC_selection
		)
		
		# FC CC π0 selection
		if (
			self.match_isFC[0] == 1 and
			self.numu_score[0] > 0.9 and
			passes_pio_selection and
			self.nue_score[0] < 7.0 and
			self.numu_cc_flag[0] < 0
		):
			self.fccc_pio[0] = 1
		
		# PC CC π0 selection (same as FC CC π0 except match_isFC is 0 instead of 1)
		if (
			self.match_isFC[0] == 0 and
			self.numu_score[0] > 0.9 and
			passes_pio_selection and
			self.nue_score[0] < 7.0 and
			self.numu_cc_flag[0] < 0
		):
			self.pccc_pio[0] = 1
		
		# NC π0 selection (numu_score < 0 and no fully contained cut)
		if (
			self.numu_score[0] < 0 and
			passes_pio_selection and
			self.nue_score[0] < 7.0 and
			self.numu_cc_flag[0] < 0
		):
			self.nc_pio[0] = 1
		
		# FC CCνμ excluding CCπ0
		if (
			self.numu_score[0] > 0.9 and
			self.match_isFC[0] == 1 and
			not (self.fccc_pio[0] == 1) and  # Not in π0 selection
			self.nue_score[0] < 7.0 and
			self.numu_cc_flag[0] < 0
		):
			self.fccc_numu_exclpio[0] = 1
		
		# PC CCνμ excluding CCπ0
		if (
			self.numu_score[0] > 0.9 and
			self.match_isFC[0] == 0 and
			not (self.pccc_pio[0] == 1) and  # Not in π0 selection
			self.nue_score[0] < 7.0 and
			self.numu_cc_flag[0] < 0
		):
			self.pccc_numu_exclpio[0] = 1
		
		# Return output dictionary with selection results
		out_dict = {
			"nue_score": self.nue_score[0],
			"numu_cc_flag": self.numu_cc_flag[0],
			"match_isFC": self.match_isFC[0],
			"nueCC_full": self.nueCC_full[0],
			"nueCC_partial": self.nueCC_partial[0],
			"fccc_pio": self.fccc_pio[0],
			"pccc_pio": self.pccc_pio[0],
			"nc_pio": self.nc_pio[0],
			"fccc_numu_exclpio": self.fccc_numu_exclpio[0],
			"pccc_numu_exclpio": self.pccc_numu_exclpio[0],
		}

		return out_dict