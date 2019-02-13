import time
import sys
import json
import colorama
from utils import Utils

from scenarios.building_automation.building_automation import BuildingAutomation
from scenarios.home_automation.home_automation import HomeAutomation
from scenarios.industrial_monitoring.industrial_monitoring import IndustrialMonitoring


class NetworkPrep:

	scenarios = {
		"building-automation"   : BuildingAutomation,
		"home-automation"       : HomeAutomation,
		"industrial-monitoring" : IndustrialMonitoring
	}

	def __init__(self, sut_command_payload):
		# Get scenario instance based on the SUT command payload
		sut_command   = json.loads(sut_command_payload)

		Utils.id_to_eui64 = sut_command['nodes']
		Utils.eui64_to_id = {v: k for k, v in sut_command['nodes'].items()}
		Utils.scenario    = self.scenarios[sut_command['scenario']](sut_command) 

		self.scenario = Utils.scenario

		colorama.init()


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