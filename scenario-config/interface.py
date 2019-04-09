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


	def _generate_json_data(self):
		data = {}
		data['scenarios'] = [{"identifier": key, "name": value["full_title"]} for key, value in self.scenarios.items()]
		data['testbeds'] = [{"identifier": key, "name": value} for key, value in self.testbeds.items()]

		for scenario in self.scenarios:
			data[scenario] = {}
			main_config_file = self.scenarios[scenario]['config']['main']

			for testbed in self.testbeds:
				data[scenario][testbed] = {}
				data[scenario][testbed]['nodes'] = {}
				testbed_config_file = self.scenarios[scenario]['config'][testbed]

				with open(main_config_file, 'r') as f:
					with open(testbed_config_file, 'r') as tf:
						main_config    = json.load(f)
						testbed_config = json.load(tf)
						
						generic_node_data = main_config['nodes']

						for generic_id in generic_node_data:
							# Attaching testbed specific data to generic node data
							node_data = generic_node_data[generic_id]
							node_data['node_id'] = testbed_config[generic_id]['node_id']
							node_data['transmission_power_dbm'] = testbed_config[generic_id]['transmission_power_dbm']

							data[scenario][testbed]['nodes'][generic_id] = node_data
							
							data[scenario][testbed]['nodes'][generic_id]['destinations'] = self._get_destination_nodes(
									data[scenario][testbed]['nodes'][generic_id]['traffic_sending_points']
								)

							del data[scenario][testbed]['nodes'][generic_id]['traffic_sending_points']

		general_data_json = os.path.join(os.path.dirname(__file__), "_general_data.json")
		with open(general_data_json, 'w') as f:
			f.write(json.dumps(data, indent=4, sort_keys=True))


	def _get_destination_nodes(self, traffic_sending_points):
		destinations = []
		for sending_point in traffic_sending_points:
			if sending_point['destination'] not in destinations:
				destinations.append(sending_point['destination'])

		return destinations


	def _read_json_data(self, args):
		general_data_json = os.path.join(os.path.dirname(__file__), "_general_data.json")
		with open(general_data_json, 'r') as f:
			json_obj = json.loads(f.read())

		if args['param'] == 'nodes':
			print(json.dumps(json_obj[args['scenario']][args['testbed']][args['param']], indent=4, sort_keys=True))
		else:	
			print(json.dumps(json_obj[args['param']], indent=4, sort_keys=True))



if __name__ == "__main__":
	Interface()