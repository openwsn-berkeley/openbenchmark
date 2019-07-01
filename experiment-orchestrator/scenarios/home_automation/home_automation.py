import os
import json
from scenarios.scenario import Scenario


class HomeAutomation(Scenario):

	SCENARIO_IDENTIFIER = 'home-automation'

	def __init__(self, sut_command_payload):
		super(HomeAutomation, self).__init__(sut_command_payload)

		self.CONFIG_FILES = {
			"main"  : os.path.join(self.scenario_config, self.SCENARIO_IDENTIFIER, "_config.json"),
			"iotlab": os.path.join(self.scenario_config, self.SCENARIO_IDENTIFIER, "_iotlab_config.json"),
			"wilab" : os.path.join(self.scenario_config, self.SCENARIO_IDENTIFIER, "_wilab_config.json"),
			"opensim": os.path.join(self.scenario_config, self.SCENARIO_IDENTIFIER, "_opensim_config.json")
		}

		super(HomeAutomation, self)._read_config(self.CONFIG_FILES)

		self._instantiate_nodes()