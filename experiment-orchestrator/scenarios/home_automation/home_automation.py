import os
import json
from scenarios._scenario import Scenario

class HomeAutomation(Scenario):

	SCENARIO_IDENTIFIER = 'home-automation'
	CONFIG_FILE         = os.path.join(os.path.dirname(__file__), "_config.json")

	def __init__(self, sut_command_payload):
		super(HomeAutomation, self).__init__(sut_command_payload)
		super(HomeAutomation, self)._read_config(self.CONFIG_FILE)
		self._instantiate_nodes()