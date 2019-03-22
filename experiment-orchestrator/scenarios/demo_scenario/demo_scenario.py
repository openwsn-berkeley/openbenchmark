import os
import json
from scenarios.scenario import Scenario


class DemoScenario(Scenario):

	SCENARIO_IDENTIFIER = 'demo-scenario'
	CONFIG_FILES        = {
		"main"  : os.path.join(os.path.dirname(__file__), "_config.json"),
		"iotlab": os.path.join(os.path.dirname(__file__), "_iotlab_config.json"),
		"wilab" : os.path.join(os.path.dirname(__file__), "_wilab_config.json"),
	}

	def __init__(self, sut_command):
		super(DemoScenario, self).__init__(sut_command)
		super(DemoScenario, self)._read_config(self.CONFIG_FILES)
		self._instantiate_nodes()