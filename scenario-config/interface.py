import os
import argparse
import json


class Interface:
	# Serves as a mediator between scenario config files and Laravel backend

	def __init__(self):
		self.scenarios = {
			"demo-scenario": {
				"full_title": "Demo scenario",
				"config": {
					"main"  : os.path.join(os.path.dirname(__file__), "demo-scenario", "_config.json"),
					"iotlab": os.path.join(os.path.dirname(__file__), "demo-scenario", "_iotlab_config.json"),
					"wilab" : os.path.join(os.path.dirname(__file__), "demo-scenario", "_wilab_config.json")
				}
			},
			"building-automation": {
				"full_title": "Building automation",
				"config": {
					"main"  : os.path.join(os.path.dirname(__file__), "building-automation", "_config.json"),
					"iotlab": os.path.join(os.path.dirname(__file__), "building-automation", "_iotlab_config.json"),
					"wilab" : os.path.join(os.path.dirname(__file__), "building-automation","_wilab_config.json")
				}
			},
			"home-automation": {
				"full_title": "Home automation",
				"config": {
					"main"  : os.path.join(os.path.dirname(__file__), "home-automation", "_config.json"),
					"iotlab": os.path.join(os.path.dirname(__file__), "home-automation", "_iotlab_config.json"),
					"wilab" : os.path.join(os.path.dirname(__file__), "home-automation","_wilab_config.json")
				}
			},
			"industrial-monitoring": {
				"full_title": "Industrial monitoring",
				"config": {
					"main"  : os.path.join(os.path.dirname(__file__), "industrial-monitoring", "_config.json"),
					"iotlab": os.path.join(os.path.dirname(__file__), "industrial-monitoring", "_iotlab_config.json"),
					"wilab" : os.path.join(os.path.dirname(__file__), "industrial-monitoring","_wilab_config.json")
				}
			},
		}

		self.testbeds = {
			"iotlab": "IoT-LAB",
			"wilab" : "w-iLab.t" 
		}

		args = self._get_args()
		self._action(args)



	def _action(self, args):
		if args['generate_json']:
			self._generate_json_data()
		else:
			self._read_json_data(args)

	def _get_args(self):
		parser = argparse.ArgumentParser()
		self._add_parser_args(parser)
		args = parser.parse_args()

		generate_json = args.generate_json
		param = args.param
		scenario = args.scenario
		testbed = args.testbed

		if not generate_json and param == None:
			parser.error('--param is required')

		if not generate_json and param == 'nodes' and (scenario == None or testbed == None):
			parser.error('Both --scenario and --testbed are required')

		return {
			'generate_json': args.generate_json,
			'param'   : args.param,
			'scenario': args.scenario,
			'testbed' : args.testbed
		}

	def _add_parser_args(self, parser):
		parser.add_argument('--generate-json', 
	        dest     = 'generate_json',
	        default  = False,
	        action   = 'store_true'
		)
		parser.add_argument('--testbed', 
	        dest     = 'testbed',
	        choices  = [key for key in self.testbeds],
	        action   = 'store'
		)
		parser.add_argument('--scenario', 
	        dest     = 'scenario',
	        choices  = [key for key in self.scenarios],
	        action   = 'store'
		)
		parser.add_argument('--param',
			dest     = 'param',
			choices  = ['scenarios', 'testbeds', 'nodes'],
			action   = 'store'
		)

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