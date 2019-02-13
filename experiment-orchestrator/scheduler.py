import sys
import time
import json
import random
import string

from utils import Utils
from scenarios.scenario import Scenario
from scenarios.building_automation.building_automation import BuildingAutomation
from scenarios.home_automation.home_automation import HomeAutomation
from scenarios.industrial_monitoring.industrial_monitoring import IndustrialMonitoring

class Scheduler:

	nodes        = []   # Array of type `Node`
	schedule     = []   # Array of dictionaries {"time_sec": type `float`, "node": type `Node`, "destination_eui64: `String`"}

	scenarios = {
		"building-automation"   : BuildingAutomation,
		"home-automation"       : HomeAutomation,
		"industrial-monitoring" : IndustrialMonitoring
	}

	scheduler_delay = 5   #[s]

	def __init__(self, sut_command_payload):
		# Get scenario instance based on the SUT command payload
		sut_command   = json.loads(sut_command_payload)

		Utils.id_to_eui64 = sut_command['nodes']
		Utils.eui64_to_id = {v: k for k, v in sut_command['nodes'].items()}

		self.scenario = self.scenarios[sut_command['scenario']](sut_command) 

	def start(self):
		self._generate_schedule()
		self._start_schedule()


	# Used only within `generate_schedule`
	def _sort_schedule(self):
		self.schedule = sorted(self.schedule, key=lambda k: k["time_sec"])

	def _generate_schedule(self):
		for node in self.scenario.nodes:
			for sending_point in node.sending_points:
				time_sec         = sending_point["time_sec"]
				destination      = sending_point["destination"]
				confirmable      = sending_point["confirmable"]
				packets_in_burst = sending_point["packets_in_burst"] if "packets_in_burst" in sending_point else 1

				self.schedule.append({
					"time_sec"          : time_sec,
					"node"              : node,
					"destination_eui64" : Utils.id_to_eui64[ self.scenario.config_node_data[destination]['node_id'] ],
					"confirmable"       : confirmable,
					"packets_in_burst"  : packets_in_burst
				})

				self._sort_schedule()


	def _print_schedule(self):
		schedule_len = len(self.schedule)

		print "[SCHEDULER] Starting schedule:"
		for i in range(0, schedule_len):
			print "{0} at {1}: from {2} to {3}".format(
				self.schedule[i]["node"].node_id, 
				self.schedule[i]["time_sec"],
				self.schedule[i]["node"].eui64,
				self.schedule[i]["destination_eui64"]
			)

		return schedule_len


	def _start_schedule(self):
		schedule_len = self._print_schedule()
		sys.stdout.write("[SCHEDULER] Starting scheduler in {0} seconds...\n".format(self.scheduler_delay))
		time.sleep(self.scheduler_delay)

		for i in range(0, schedule_len):
			currently_on = self.schedule[i]
			
			if i < schedule_len - 1:
				next_on      = self.schedule[i+1]
				sleep_interval = next_on["time_sec"] - currently_on["time_sec"]
			else:
				sleep_interval = -1

			# Assigning `sendPacket` payload as defined by the documentation
			currently_on["node"].command_exec(payload={
					'source'          : currently_on["node"].eui64,
					'destination'     : currently_on["destination_eui64"],
					'packetPayloadLen': self.scenario.main_config['payload_size'],
					'confirmable'     : currently_on["confirmable"],
					'packetsInBurst'  : currently_on["packets_in_burst"] 
				})

			if sleep_interval == -1:
				sys.stdout.write("[SCHEDULER] Currently on: {0}/{1}. Last event\n".format(i+1, schedule_len))
			else:
				sys.stdout.write("[SCHEDULER] Currently on: {0}/{1}. Next event in {2} seconds\n".format(i+1, schedule_len, sleep_interval))
				time.sleep(sleep_interval)