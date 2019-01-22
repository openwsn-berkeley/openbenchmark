import json
import os

class Logger:

	_instance = None

	@staticmethod
	def create():
		if Logger._instance == None:
			Logger._instance = Logger()
		return Logger._instance

	
	def __init__(self):
		self.date = ''
		self.experiment_id = ''
		self.testbed = ''
		self.firmware = ''
		self.nodes = ''
		self.scenario = ''
		self.logs = {
			'kpi': os.path.join(os.path.dirname(__file__), 'kpi.log')
		}

	def set_properties(self, sut_command_payload):
		sut_command        = json.loads(sut_command_payload)
		self.date          = sut_command['date']
		self.experiment_id = sut_command['experimentId']
		self.testbed       = sut_command['testbed']
		self.firmware      = sut_command['firmware']
		self.nodes         = sut_command['nodes']
		self.scenario      = sut_command['scenario']


	def exists(self, log_type):
		return os.path.exists(self.logs[log_type]) 

	def delete(self, log_type):
		os.remove(self.logs[log_type])

	def reset(self, log_type):
		if self.exists(log_type):
			self.delete(log_type)

	# Logger should be able to match EUI64 address with Node ID!!!
	def log(self, log_type, payload, reset=False):
		if reset:
			self.reset()

		with open(self.logs[log_type], 'a') as f:
			f.write(json.dumps(payload) + "\n")