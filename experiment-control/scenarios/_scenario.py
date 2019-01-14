from abc import abstractproperty, abstractmethod
from _node import Node
import json


class Scenario(object):

	@abstractproperty
	def SCENARIO_IDENTIFIER(self):  # Fixed value depending on the instantiated child class 
		pass

	@abstractproperty
	def CONFIG_FILE(self):
		pass

	@abstractmethod
	def _read_config(self):          # Object which models scenario configuration
		pass

	def _find_node(self, node_id): ####
		for node in self.config_node_data:
			if node['node_id'] == node_id:
				return node
		return None
	
	def _instantiate_nodes(self):     # Instantiates node objects based on config objects and EUI-64 addresses read from database
		for sut_item in self.sut_node_data:
			node = self._find_node(sut_item['node_id'])
			self.nodes.append(Node(
				sut_item['node_id'],
				sut_item['eui_64'],
				node['type'],
				node['area'],
				node['sending_time']
			))


	def __init__(self, sut_command):
		self.testbed       = sut_command['testbed']   # Testbed and nodes data passed from the MQTT payload (see _README.md, step 2)
		self.sut_node_data = sut_command['nodes']     #
		self.nodes         = []                       # List of objects of type Node
		self.config_object = None                     # Instantiating nodes based on _config.json data and data received from SUT