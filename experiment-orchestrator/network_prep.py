import time
import sys
import json
import colorama
from utils import Utils

from scenarios.demo_scenario.demo_scenario import DemoScenario
from scenarios.building_automation.building_automation import BuildingAutomation
from scenarios.home_automation.home_automation import HomeAutomation
from scenarios.industrial_monitoring.industrial_monitoring import IndustrialMonitoring

from helpers.reflash.reflash import IotlabReflash
from helpers.reflash.reflash import WilabReflash


class NetworkPrep:

	scenarios = {
		"demo-scenario"         : DemoScenario,
		"building-automation"   : BuildingAutomation,
		"home-automation"       : HomeAutomation,
		"industrial-monitoring" : IndustrialMonitoring
	}

	reflash = {
		"iotlab": IotlabReflash,
		"wilab": WilabReflash
	}

	def __init__(self, sut_command_payload):
		# Get scenario instance based on the SUT command payload
		sut_command   = json.loads(sut_command_payload)

		Utils.date = sut_command['date']
		Utils.testbed = sut_command['testbed']
		Utils.firmware = sut_command['firmware']

		Utils.id_to_eui64 = self._get_node_map(sut_command['nodes'])
		Utils.eui64_to_id = {v: k for k, v in Utils.id_to_eui64.items()}
		
		self.reflash[Utils.testbed](sut_command['scenario']).remove_unused()
		
		Utils.scenario    = self.scenarios[sut_command['scenario']](sut_command) 
		self.scenario = Utils.scenario


	def start(self):
		try:
			if not self._configure_transmit_power():
				raise Exception("Failed to configure transmission power. Exiting...")
			sys.stdout.write("{0}[NETWORK PREP] {1}\n{2}".format(
				colorama.Fore.GREEN,
				"Transmission power configured successfully", 
				colorama.Style.RESET_ALL
			))

			if not json.loads(self._trigger_network_formation())["success"]:
				raise Exception("Failed to trigger network formation. Exiting...")
			sys.stdout.write("{0}[NETWORK PREP] {1}\n{2}".format(
				colorama.Fore.GREEN,
				"Network formation triggered successfully", 
				colorama.Style.RESET_ALL
			))
		
		except Exception, e:
			sys.stdout.write("{0}[NETWORK PREP] {1}\n{2}".format(
				colorama.Fore.RED,
				str(e), 
				colorama.Style.RESET_ALL
			))
			sys.exit()

	def _configure_transmit_power(self):
		success_num = 0
		for node in self.scenario.nodes:
			conf_tx_resp = node.command_exec(payload={
					'source': node.eui64,
					'power' : node.transmission_power
				}, command='configureTransmitPower', blocking=True)	   # Blocks until response is received or timeout

			conf_tx_resp = json.loads(conf_tx_resp)
			
			if conf_tx_resp['success']:
				success_num += 1

		return success_num == len(self.scenario.nodes)

	def _trigger_network_formation(self):
		for node in self.scenario.nodes:
			if node.generic_id == "openbenchmark00":
				return node.command_exec(payload={
						'source': node.eui64,
				}, command='triggerNetworkFormation', blocking=True)   # Blocks until response is received or timeout


	def _get_node_map(self, sut_nodes_field):
		grouped_nodes = {}
		for eui64, node_id in sut_nodes_field.items():
			if node_id not in grouped_nodes:
				grouped_nodes[node_id] = []

			grouped_nodes[node_id].append(eui64)

		node_dict = {}
		for key, nodes in grouped_nodes.items():
			if len(nodes) > 1:
				suffix = 0
				for eui64 in nodes:
					node_dict["{0}-{1}".format(key, suffix)] = eui64
					suffix += 1
			else:
				node_dict[key] = nodes[0]

		return node_dict