import os
import argparse
import json


class Interface:
	# Serves as a mediator between scenario config files and Laravel backend

	def __init__(self):
		self.config_files = {
			"building-automation": {
				"main"  : os.path.join("building_automation", "_config.json"),
				"iotlab": os.path.join("building_automation", "_iotlab_config.json"),
				"wilab" : os.path.join("building_automation","_wilab_config.json")
			},
			"home-automation": {
				"main"  : os.path.join("home_automation", "_config.json"),
				"iotlab": os.path.join("home_automation", "_iotlab_config.json"),
				"wilab" : os.path.join("home_automation","_wilab_config.json")
			},
			"industrial-monitoring": {
				"main"  : os.path.join("industrial_monitoring", "_config.json"),
				"iotlab": os.path.join("industrial_monitoring", "_iotlab_config.json"),
				"wilab" : os.path.join("industrial_monitoring","_wilab_config.json")
			},
		}

		args = self._get_args()
		self._print_data(args['scenario'], args['testbed'])


	def _print_data(self, scenario, testbed):
		self._read_config(scenario, testbed)
		print self.config_node_data

	def _get_args(self):
		parser = argparse.ArgumentParser()
		self._add_parser_args(parser)
		args = parser.parse_args()

		return {
			'scenario': args.scenario,
			'testbed' : args.testbed
		}

	def _add_parser_args(self, parser):
		parser.add_argument('--scenario', 
	        dest     = 'scenario',
	        choices  = ['building-automation', 'home-automation', 'industrial-monitoring'],
	        required = True,
	        action   = 'store'
		)
		parser.add_argument('--testbed', 
	        dest     = 'testbed',
	        choices  = ['iotlab', 'wilab'],
	        required = True,
	        action   = 'store'
		)
	
	def _read_config(self, scenario, testbed):
		self.config_node_data = {}
		main_config_file    = self.config_files[scenario]['main']
		testbed_config_file = self.config_files[scenario][testbed]

		with open(main_config_file, 'r') as f:
			with open(testbed_config_file, 'r') as tf:
				self.main_config    = json.load(f)
				self.testbed_config = json.load(tf)
				
				generic_node_data   = self.main_config['nodes']

				for generic_id in generic_node_data:
					# Attaching testbed specific data to generic node data
					node_data = generic_node_data[generic_id]
					node_data['node_id'] = self.testbed_config[generic_id]['node_id']
					node_data['transmission_power_dbm'] = self.testbed_config[generic_id]['transmission_power_dbm']

					self.config_node_data[generic_id] = node_data
					del self.config_node_data[generic_id]['traffic_sending_points']



if __name__ == "__main__":
	Interface()