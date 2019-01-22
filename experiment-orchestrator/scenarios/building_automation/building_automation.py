import os
import json
from scenarios.scenario import Scenario


class BuildingAutomation(Scenario):

	SCENARIO_IDENTIFIER = 'building-automation'
	CONFIG_FILE         = os.path.join(os.path.dirname(__file__), "_config.json")

	def __init__(self, sut_command):
		super(BuildingAutomation, self).__init__(sut_command)
		super(BuildingAutomation, self)._read_config(self.CONFIG_FILE)
		self._instantiate_nodes()