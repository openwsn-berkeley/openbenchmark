class Identifiers:
	building_automation   = 'building_automation'
	home_automation       = 'home_automation'
	industrial_monitoring = 'industrial_monitoring'


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
			Identifiers.building_automation,
			Identifiers.home_automation,
			Identifiers.industrial_monitoring
		]

		self.definitions = {
			Identifiers.building_automation   : {'ms': 3, 'es': 4, 'a': 2, 'ac': 1, 'zc': 1},   # Data per area
			Identifiers.home_automation       : {'ms': 49.0, 'es': 21.0, 'a': 30.0, 'cu': 1},         # All % except CU
			Identifiers.industrial_monitoring : {'s': 90.0, 'bs': 10.0, 'cu': 1}				    # All % except CU
		} 

		self.info  = {}
		self._collect_info()


	def _collect_info(self):
		print("WELCOME to Scenario Generator. Please provide the config parameters:")
		print("-----------------------------")
		
		
		self.info['identifier'] = self.identifiers[input(
				"Pick a scenario (0 - 'building-automation', 1 - 'home-automation', 2 - 'industrial-monitoring'): "
			)]
		
		self.info['duration_min'] = input("Duration in minutes (e.g. 30): ")
		self.info['number_of_nodes'] = input("Number of nodes (e.g. 70): ")

		self._generate_node_array()


	def _calculate_number_of_nodes(self):
		identifier = self.info['identifier']

		if identifier == Identifiers.building_automation:
			print "All extra nodes that cannot form an entire area will be disregarded"
			self.info['number_of_areas'] = self.info['number_of_nodes'] / 10    # 10 = number of nodes per zone
			self.info['number_of_nodes'] = self.info['number_of_areas'] * 10
			print "Number of nodes after calculation: {0}".format(self.info['number_of_nodes'])
			self.roles = self.definitions[identifier]   # Roles related to a single area
		else:
			self.roles = {}                             # Roles related to the entire network
			definition = self.definitions[identifier]
			node_sum = 0

			for key in definition:
				if key != 'cu':
					role            = key
					percent         = definition[key]
					self.roles[key] = int( ((percent/100) * self.info['number_of_nodes'])//1 )
				else:
					self.roles[key] = definition[key]

				node_sum += self.roles[key]

			if node_sum != self.info['number_of_nodes']:
				print "Number of nodes reduced after rounding." 
				print "Number of nodes after calculation: {0}".format(node_sum)
				self.info['number_of_nodes'] = node_sum


	def _define_nodes(self):
		identifier = self.info['identifier']
		self.nodes = {}

		if identifier == Identifiers.building_automation:
			for area_ind in range(0, self.info['number_of_areas']):
				for role in self.roles:
					self.nodes["{0}{1}".format(self.id_prefix, "%02d"%self.roles[role])]
					self.nodes['role']           = role
					self.nodes['area']           = area_ind
					self.nodes['sending_points'] = {}

		else:
			for role in self.roles:
				self.nodes["{0}{1}".format(self.id_prefix, "%02d"%self.roles[role])]
				self.nodes['role']           = role
				self.nodes['area']           = 1
				self.nodes['sending_points'] = {}


	def _generate_time_instants(self):
		# Iterates each node
		# Generates time instants according to the traffic distribution
		# Assigns destination by picking a random node from a group defined by the scenario
		pass

	def _generate_testbed_specific_template(self):
		# Generates template for tying generic node id with testbed specific id
		# Should be edited manually
		pass

	def _output_json(self):
		# Save the generated data to a JSON file at the location depending on the scenario
		pass


def main():
	Wizard()

if __name__ == '__main__':
	main()