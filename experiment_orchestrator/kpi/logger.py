import sys
sys.path.append("..")

import json
import os
import colorama

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
			'kpi'      : os.path.join(os.path.dirname(__file__), 'kpis', 'kpi_{0}.log'.format(self.experiment_id)),
			'raw'      : os.path.join(os.path.dirname(__file__), 'raw', 'raw_{0}.log'.format(self.experiment_id)),
			'kpi_cache': os.path.join(os.path.dirname(__file__), 'kpis', '.cache', 'cached_kpi_{0}.json'.format(self.experiment_id))
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
			self.cache_kpi(payload)
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

		json_form = {
			"header": {
				"date"         : self.date,
				"experiment_id": self.experiment_id,
				"testbed"      : self.testbed,
				"firmware"     : self.firmware,
				"scenario"     : self.scenario
			},
			"general_data": {

			},
			"data": {

			}
		}

		with open(self.logs['kpi_cache'], 'a') as f:
			f.write(json.dumps(json_form))


	def cache_kpi(self, payload):
		#try:
		with open(self.logs['kpi_cache'], 'r') as f:
			json_obj = json.loads(f.read())
					
			if "node_id" in payload:
				node_id   = payload["node_id"]
				kpi       = payload["kpi"]
				timestamp = payload["timestamp"]
				value     = payload["value"]
				
				if node_id not in json_obj["data"]:
					json_obj["data"][node_id] = {}

				if kpi not in json_obj["data"][node_id]:
					json_obj["data"][node_id][kpi] = {}
					json_obj["data"][node_id][kpi]["timestamp"] = []
					json_obj["data"][node_id][kpi]["value"]     = []

				json_obj["data"][node_id][kpi]["timestamp"].append(timestamp)
				json_obj["data"][node_id][kpi]["value"].append(value)
				
			else:
				kpi       = payload["kpi"]
				timestamp = payload["timestamp"]
				json_obj["general_data"][kpi] = timestamp

			with open(self.logs['kpi_cache'], 'w') as f:
					f.write(json.dumps(json_obj))
		'''
		except Exception, e:
			sys.stdout.write("{0}[LOGGER] {1}\n{2}".format(
				colorama.Fore.RED,
				str(e), 
				colorama.Style.RESET_ALL
			))'''
