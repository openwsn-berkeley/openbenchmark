import sys
from mqtt_client.api import API

class Node:

	# Node class instantiated upon receving the necessary data from `startBenchmark` command
	# Data for node instantiation is a combination of _config.json data and data received from SUT in `startBenchmark` command payload
	def __init__(self, params):
		self.generic_id         = params['generic_id']
		self.node_id            = params['node_id']
		self.eui64              = params['eui64']
		self.role               = params['role']
		self.area               = params['area'],
		self.sending_points     = params['sending_points']   # dictionary {time_sec: `Int`, destination: `String`}
		self.transmission_power = params['transmission_power']
		self.api                = API(timeout=10)

	def command_exec(self, payload, command='sendPacket', blocking=False):
		return self.api.command_exec(command, payload, blocking)