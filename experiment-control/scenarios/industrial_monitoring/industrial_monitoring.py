import os
import json
from scenarios._scenario import Scenario


class IndustrialMonitoring(Scenario):

	SCENARIO_IDENTIFIER = 'industrial-monitoring'
	CONFIG_FILE         = os.path.join(os.path.dirname(__file__), "_config.json")

	def __init__(self, sut_command_payload):
		super(IndustrialMonitoring, self).__init__(sut_command_payload)
		self._read_config()
		self._instantiate_nodes()

	def _read_config(self):
		with open(self.CONFIG_FILE, 'r') as f:
			self.config_node_data = json.load(f)[self.testbed]['nodes']