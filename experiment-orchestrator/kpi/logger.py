import sys
sys.path.append("..")

import json
import os

from mqtt_client.mqtt_client import MQTTClient


class Logger:

	_instance = None

	@staticmethod
	def create(header):
		if Logger._instance == None:
			Logger._instance = Logger(header)
		return Logger._instance


	def __init__(self, header):
		self.date = header['date']
		self.experiment_id = header['experiment_id']
		self.testbed = header['testbed']
		self.firmware = header['firmware']
		self.nodes = header['nodes']
		self.scenario = header['scenario']

		self.mqtt_client = MQTTClient.create()

		self.logs = {
			'kpi': os.path.join(os.path.dirname(__file__), 'kpi.log'),
			'raw': os.path.join(os.path.dirname(__file__), 'raw.log')
		}

		self.log_header()


	def set_properties(self, header):
		self.date          = header['date']
		self.experiment_id = header['experimentId']
		self.testbed       = header['testbed']
		self.firmware      = header['firmware']
		self.nodes         = header['nodes']
		self.scenario      = header['scenario']


	def exists(self, log_type):
		return os.path.exists(self.logs[log_type]) 

	def delete(self, log_type):
		os.remove(self.logs[log_type])

	def reset(self, log_type):
		if self.exists(log_type):
			self.delete(log_type)


	def log(self, log_type, payload, reset=False):
		if reset:
			self.reset()

		if log_type == 'kpi':
			self.mqtt_client.push_kpi(payload)
		elif log_type == 'raw':
			self.mqtt_client.push_raw(payload)

		with open(self.logs[log_type], 'a') as f:
			f.write(json.dumps(payload) + "\n")


	def log_header(self):
		header = "Date: {0}\nExperiment ID: {1}\nTestbed: {2}\nFirmware: {3}\nNodes: {4}\nScenario: {5}".format(
				self.date,
				self.experiment_id,
				self.testbed,
				self.firmware,
				str(self.nodes),
				self.scenario
			)

		with open(self.logs['kpi'], 'a') as f:
			f.write(header)
			f.write("\n--------------------------------------\n")

		with open(self.logs['raw'], 'a') as f:
			f.write(header)
			f.write("\n--------------------------------------\n")