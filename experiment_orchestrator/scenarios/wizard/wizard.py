import os
import json
import numpy as np
import random
from collections import OrderedDict
from _wizard_definitions import definitions
from _wizard_definitions import Identifiers
from _wizard_definitions import Roles
from _generator import Generator


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
			Identifiers.dm,
			Identifiers.ba,
			Identifiers.ha,
			Identifiers.im
		]

		self.default_payload_size = {   # in bytes
			Identifiers.dm: 10,
			Identifiers.ba: 80,
			Identifiers.ha: 10,
			Identifiers.im: 10
		}

		self.nf_time_padding_min = {
			Identifiers.dm: 5,
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

		self.locations = {
			Identifiers.dm: "../demo_scenario/",
			Identifiers.ba: "../building_automation/",
			Identifiers.ha: "../home_automation/",
			Identifiers.im: "../industrial_monitoring/"
		}


	def _collect_info(self):
		print("WELCOME to Scenario Generator. Please provide the config parameters:")
		print("-----------------------------")
		
		
		self.info['identifier'] = self.identifiers[input(
				"Pick a scenario (0 - {0}, 1 - {1}, 2 - {2}, 3 - {3}): ".format(Identifiers.dm, Identifiers.ba, Identifiers.ha, Identifiers.im)
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
			self.info['number_of_areas'] = (self.info['number_of_nodes'] - 1) / 10    # 10 = number of nodes per zone, -1 to account for ZC
			self.info['number_of_nodes'] = (self.info['number_of_areas'] * 10) + 1
			print "Number of nodes after calculation: {0}".format(self.info['number_of_nodes'])
			roles = definitions[identifier]   # Roles related to a single area
		else:
			roles = definitions[identifier]
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
		roles      = definitions[identifier]

		role = Roles.zc if identifier == Identifiers.ba else Roles.cu if identifier in (Identifiers.ha, Identifiers.dm) else Roles.g
		self.nodes["openbenchmark00"] = OrderedDict()
		self.nodes["openbenchmark00"]['role'] = role
		self.nodes["openbenchmark00"]['area'] = None
		self.nodes["openbenchmark00"]['traffic_sending_points'] = []
		roles[role]['nodes'].append("openbenchmark00")

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
							self.nodes[generic_id]['traffic_sending_points'] = []

							roles[role]['nodes'].append(generic_id)
							id_suffix += 1

		else:
			id_suffix = 1

			for role in [role for role in roles if role != Roles.cu and role != Roles.g]:
				for i in range(0, roles[role]['number']):
					generic_id = "{0}{1}".format(self.id_prefix, "%02d"%id_suffix)

					self.nodes[generic_id] = OrderedDict()
					self.nodes[generic_id]['role'] = role
					self.nodes[generic_id]['area'] = 0
					self.nodes[generic_id]['traffic_sending_points'] = []
					roles[role]['nodes'].append(generic_id)

					id_suffix += 1


	def _generate_time_instants(self):
		for key in self.nodes:
			roles      = definitions[self.info['identifier']]
			role       = self.nodes[key]['role']
			dest_types = roles[role]['dest_type']

			node_pool = {}
			if dest_types != None:
				confirmables = roles[role]['confirmable']
				for destination in dest_types:
					node_group = []
					
					for generic_id in roles[destination]['nodes']:
						if self.nodes[generic_id]['area'] == None or self.nodes[key]['area'] == None or self.nodes[generic_id]['area'] == self.nodes[key]['area']:
							node_group.append({
									'id':          generic_id,
									'confirmable': confirmables[destination]
								})

					node_pool[destination] = node_group[:]
				
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