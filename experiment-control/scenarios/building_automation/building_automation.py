import os
import json
from scenarios._scenario import Scenario


class BuildingAutomation(Scenario):

	SCENARIO_IDENTIFIER = 'building-automation'
	CONFIG_FILE         = os.path.join(os.path.dirname(__file__), "_config.json")

	def __init__(self, sut_command):
		super(BuildingAutomation, self).__init__(sut_command)
		self._read_config()
		self._instantiate_nodes()

	def _read_config(self):
		with open(self.CONFIG_FILE, 'r') as f:
			self.config_node_data = json.load(f)[self.testbed]['nodes']