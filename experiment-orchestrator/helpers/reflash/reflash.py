import sys
sys.path.append("../..")

import os
import json
import base64

from abc import abstractmethod
from mqtt_client.mqtt_client import MQTTClient
from utils import Utils


class Reflash(object):

	SCENARIO_CONFIG = os.path.join(os.path.dirname(__file__), "..", "..", "scenarios")
	FIRMWARE_PATH   = os.path.join(os.path.dirname(__file__), "fw")

	def __init__(self, scenario):
		self.mqtt_client = MQTTClient.create()
		self.scenario    = scenario

	def remove_unused(self):
		nodes = self._get_unused_nodes()
		self._reflash_unused(nodes)
		self._remove_unused(nodes)

	def _reflash_unused(self, nodes):
		print "[REFLASH] Reverting unused nodes to eui64 retreival firmware..."
		for testbed_node_id in nodes:
			self._flash_eui64_firmware(
					Utils.id_to_eui64[testbed_node_id]
				)

	def _remove_unused(self, nodes):
		print "[REFLASH] Removing unused nodes from index..."
		for testbed_node_id in nodes:
			eui64 = Utils.id_to_eui64[testbed_node_id]
			del Utils.id_to_eui64[testbed_node_id]
			del Utils.eui64_to_id[eui64]

	def _flash_eui64_firmware(self, eui64):
		# {0}/deviceType/mote/deviceId/{1}/cmd/program
		try:
			print "[REFLASH] Flashing to {0}...".format(eui64)
			with open(os.path.join(self.FIRMWARE_PATH, "{0}_eui64_fw".format(self.testbed)), "r") as f:
				data = f.read()
				payload = {
					'hex': base64.b64encode(data),
					'description': ''
				}
				self.mqtt_client.publish(
					'{0}/deviceType/mote/deviceId/{1}/cmd/program'.format(self.testbed, eui64), 
					payload,
					custom=True
				)

		except Exception, e:
			print("An exception occured: {0}".format(str(e)))

	@abstractmethod
	def _get_unused_nodes(self):
		pass


class IotlabReflash(Reflash):
	def __init__(self, scenario):
		super(IotlabReflash, self).__init__(scenario)
		self.testbed = "iotlab"

	def _get_unused_nodes(self):
		return []


class WilabReflash(Reflash):

	def __init__(self, scenario):
		super(WilabReflash, self).__init__(scenario)
		self.testbed = "wilab"

	def _get_unused_nodes(self):
		config_file = os.path.join(self.SCENARIO_CONFIG, self.scenario.replace("-", "_"), "_{0}_config.json".format(self.testbed))
		
		with open(config_file, 'r') as f:
			config_obj = json.load(f)
			unused = []

			for generic_id in config_obj:	
				testbed_id_split = config_obj[generic_id]["node_id"].split("-")
				nuc_id = testbed_id_split[0] + "-" + testbed_id_split[1]
				suffix = testbed_id_split[2]
				
				pair_node_id = "{0}-{1}".format(nuc_id, abs(int(suffix) - 1))   # Inverting the last id digit (0/1)

				if pair_node_id not in config_obj:
					if len( [config_obj[generic_id]["node_id"] for generic_id in config_obj if config_obj[generic_id]["node_id"] == pair_node_id] ) == 0:
						unused.append(pair_node_id)

		return unused