import sys
from mqtt_client.api import API

class Node:

	# Node class instantiated upon receving the necessary data from `startBenchmark` command
	# Data for node instantiation is a combination of _config.json data and data received from SUT in `startBenchmark` command payload
	def __init__(self, node_id, eui64, node_type, area, sending_time):
		self.node_id      = node_id
		self.eui64        = eui64
		self.node_type    = node_type
		self.area         = area,
		self.sending_time = sending_time
		self.api          = API(timeout=10)

	def command_exec(self, payload, command='send_packet'):
		self.api.command_exec(command, payload)