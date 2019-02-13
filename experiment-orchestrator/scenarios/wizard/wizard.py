import os
import json
import numpy as np
import random
from collections import OrderedDict
from _generator import Generator


class Identifiers:
	ba = 'building-automation'
	ha = 'home-automation'
	im = 'industrial-monitoring'

class Roles:
	ms = 'monitoring-sensor'
	es = 'event-sensor'
	a  = 'actuator'
	ac = 'area-controller'
	zc = 'zone-controller'
	cu = 'control-unit'
	s  = 'sensor'
	bs = 'bursty-sensor'
	g  = 'gateway'


class Wizard:

	def __init__(self):
		self._param_setup()
		self._collect_info()
		self._calculate_number_of_nodes()
		self._define_nodes()
		self._generate_time_instants()
		self._generate_testbed_specific_template()
		self._output_json()


	def _param_setup(self):
		self.id_prefix = "openbenchmark"

		self.identifiers = [
			Identifiers.ba,
			Identifiers.ha,
			Identifiers.im
		]

		self.default_payload_size = {   # in bytes
			Identifiers.ba: 80,
			Identifiers.ha: 10,
			Identifiers.im: 10
		}

		self.nf_time_padding_min = {
			Identifiers.ba: 5,
			Identifiers.ha: 5,
			Identifiers.im: 5,
		}


		self.info       = {}   # fields: identifier, duration_min, number_of_nodes, 
		self.nodes      = OrderedDict()
		self.specifics  = {
			"iotlab": {},
			"wilab":  {}
		}

		self.definitions = {
			Identifiers.ba: {   # Data per area except `zone-controller`
				Roles.ms: {'number': 3, 'nodes': [], 'dest_type': [Roles.ac],          'confirmable': [True],        'traffic_type': 'periodic', 'interval': [25, 35],     'packets_in_burst': 1},   # seconds
				Roles.es: {'number': 4, 'nodes': [], 'dest_type': [Roles.ac],          'confirmable': [True],        'traffic_type': 'poisson',  'mean': 10,               'packets_in_burst': 1},   # per hour
				Roles.a : {'number': 2, 'nodes': [], 'dest_type': [Roles.ac],          'confirmable': [True],        'traffic_type': 'periodic', 'interval': [25, 35],     'packets_in_burst': 1}, 
				Roles.ac: {'number': 1, 'nodes': [], 'dest_type': [Roles.a, Roles.zc], 'confirmable': [True, False], 'traffic_type': 'periodic', 'interval': [0.12, 0.14], 'packets_in_burst': 1},
				Roles.zc: {'number': 1, 'nodes': [], 'dest_type': None,                                              'traffic_type': None}
			},       
			Identifiers.ha: {   # All % except control-unit
				Roles.ms: {'number': 49.0, 'nodes': [], 'dest_type': [Roles.cu], 'confirmable': [False], 'traffic_type': 'periodic', 'interval': [180, 300], 'packets_in_burst': 1}, 
				Roles.es: {'number': 21.0, 'nodes': [], 'dest_type': [Roles.cu], 'confirmable': [True],  'traffic_type': 'poisson',  'mean': 10,             'packets_in_burst': 1}, 
				Roles.a : {'number': 30.0, 'nodes': [], 'dest_type': [Roles.cu], 'confirmable': [True],  'traffic_type': 'periodic', 'interval': [180, 300], 'packets_in_burst': 1}, 
				Roles.cu: {'number': 1,    'nodes': [], 'dest_type': [Roles.a],  'confirmable': [True],  'traffic_type': 'poisson',  'mean': 10,             'packets_in_burst': 5}
			},
			Identifiers.im : {   # All % except gateway
				Roles.s : {'number': 90.0, 'nodes': [], 'dest_type': [Roles.g], 'confirmable': [None], 'traffic_type': 'periodic', 'interval': [1, 60],    'packets_in_burst': 1}, 
				Roles.bs: {'number': 10.0, 'nodes': [], 'dest_type': [Roles.g], 'confirmable': [None], 'traffic_type': 'periodic', 'interval': [60, 3600], 'packets_in_burst': 1}, 
				Roles.g : {'number': 1,    'nodes': [], 'dest_type': None,                             'traffic_type': None}				
			}
		}

		self.locations = {
			Identifiers.ba: "../building_automation/",
			Identifiers.ha: "../home_automation/",
			Identifiers.im: "../industrial_monitoring/"
		}


	def _collect_info(self):
		print("WELCOME to Scenario Generator. Please provide the config parameters:")
		print("-----------------------------")
		
		
		self.info['identifier'] = self.identifiers[input(
				"Pick a scenario (0 - {0}, 1 - {1}, 2 - {2}): ".format(Identifiers.ba, Identifiers.ha, Identifiers.im)
			)]
		
		self.info['duration_min'] = input("Duration in minutes (e.g. 30): ")
		self.info['number_of_nodes'] = input("Number of nodes (e.g. 10): ")
		self.info['payload_size'] = self.default_payload_size[self.info['identifier']]
		self.info['nf_time_padding_min'] = self.nf_time_padding_min[self.info['identifier']]

		self.generator = Generator(self.info['duration_min'] * 60)


	def _calculate_number_of_nodes(self):
		identifier = self.info['identifier']

		if identifier == Identifiers.ba:
			print "All extra nodes that cannot form an entire area will be disregarded"
			self.info['number_of_areas'] = self.info['number_of_nodes'] / 10    # 10 = number of nodes per zone
			self.info['number_of_nodes'] = self.info['number_of_areas'] * 10
			print "Number of nodes after calculation: {0}".format(self.info['number_of_nodes'])
			roles = self.definitions[identifier]   # Roles related to a single area
		else:
			roles = self.definitions[identifier]
			node_sum = 0

			for key in roles:
				if key != Roles.cu and key != Roles.g:
					percent = roles[key]['number']
					roles[key]['number'] = int( round((percent/100) * (self.info['number_of_nodes']-1)) )

				print "{0}s: {1}".format(key, roles[key]['number'])
				node_sum += roles[key]['number']

			if node_sum != self.info['number_of_nodes']:
				print "Number of nodes after rounding reduced to: {0}".format(node_sum)
				self.info['number_of_nodes'] = node_sum


	def _define_nodes(self):
		identifier = self.info['identifier']
		roles      = self.definitions[identifier]

		self.nodes["openbenchmark00"] = OrderedDict()
		self.nodes["openbenchmark00"]['role'] = Roles.zc if identifier == Identifiers.ba else Roles.cu if identifier == Identifiers.ha else Roles.g
		self.nodes["openbenchmark00"]['area'] = 0
		self.nodes["openbenchmark00"]['traffic_sending_points'] = {}

		if identifier == Identifiers.ba:
			id_suffix = 1

			for area_ind in range(0, self.info['number_of_areas']):
				for role in roles:
					if role != Roles.zc:
						for i in range(0, roles[role]['number']):
							generic_id = "{0}{1}".format(self.id_prefix, "%02d"%id_suffix)

							self.nodes[generic_id] = OrderedDict()
							self.nodes[generic_id]['role'] = role
							self.nodes[generic_id]['area'] = area_ind
							self.nodes[generic_id]['traffic_sending_points'] = {}

							roles[role]['nodes'].append(generic_id)
							id_suffix += 1

		else:
			id_suffix = 1

			for role in roles:
				for i in range(0, roles[role]['number']):
					generic_id = "{0}{1}".format(self.id_prefix, "%02d"%id_suffix)

					self.nodes[generic_id] = OrderedDict()
					self.nodes[generic_id]['role'] = role
					self.nodes[generic_id]['area'] = 0
					self.nodes[generic_id]['traffic_sending_points'] = {}

					roles[role]['nodes'].append(generic_id)
					id_suffix += 1


	def _generate_time_instants(self):
		for key in self.nodes:
			roles = self.definitions[self.info['identifier']]
			role = self.nodes[key]['role']
			dest_types  = roles[role]['dest_type']

			node_pool = []
			if dest_types != None:
				confirmables = roles[role]['confirmable']
				for idx, destination in enumerate(dest_types):
					for node in roles[destination]['nodes']:
						node_pool.append({
								'id':          node,
								'confirmable': confirmables[idx]
							})

				sending_points = self.generator.generate(
					node_pool, 
					roles[role]
				)

				self.nodes[key]['traffic_sending_points'] = sending_points


	def _generate_testbed_specific_template(self):
		for key in self.nodes:
			for testbed in self.specifics:
				self.specifics[testbed][key] = {"node_id": "", "transmission_power_dbm": 0}
				self.specifics[testbed][key] = {"node_id": "", "transmission_power_dbm": 0}


	def _output_json(self):
		identifier = self.info['identifier']
		path       = self.locations[identifier]

		with open(os.path.abspath(os.path.join(path, '_config.json')), 'w') as f:
			content = OrderedDict()
			content['identifier']          = self.info['identifier']
			content['duration_min']        = self.info['duration_min']
			content['number_of_nodes']     = self.info['number_of_nodes'] 
			content['payload_size']        = self.info['payload_size']
			content['nf_time_padding_min'] = self.info['nf_time_padding_min']
			content['nodes']               = self.nodes
			f.write(json.dumps(content, indent=4))

		for testbed in self.specifics:
			with open(os.path.abspath(os.path.join(path, '_{0}_config.json'.format(testbed))), 'w') as f:
				f.write(json.dumps(self.specifics[testbed], indent=4, sort_keys=True))



def main():
	Wizard()

if __name__ == '__main__':
	main()