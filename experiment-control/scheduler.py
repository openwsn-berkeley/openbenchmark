import sys
import time
import json

from scenarios.building_automation.building_automation import BuildingAutomation
from scenarios.home_automation.home_automation import HomeAutomation
from scenarios.industrial_monitoring.industrial_monitoring import IndustrialMonitoring

class Scheduler:

	nodes    = []   # Array of type `Node`
	schedule = []   # Array of dictionaries {"time_point": type `float`, "node": type `Node`}

	scenarios = {
		"building-automation"   : BuildingAutomation,
		"home-automation"       : HomeAutomation,
		"industrial-monitoring" : IndustrialMonitoring
	}

	def __init__(self, sut_command_payload):
		# Get scenario instance based on the SUT command payload
		sut_command   = json.loads(sut_command_payload)

		self.scenario = self.scenarios[sut_command['scenario']](sut_command) 

		self._generate_schedule()
		self._start_schedule()


	def _generate_schedule(self):
		for node in self.scenario.nodes:
			for time_point in node.sending_time:
				self.schedule.append({
					"time_point": time_point, 
					"node"      : node
				})
				self._sort_schedule()

	# Used only within `generate_schedule`
	def _sort_schedule(self):
		self.schedule = sorted(self.schedule, key=lambda k: k["time_point"])

	def _print_schedule(self):
		schedule_len = len(self.schedule)

		print "[SCHEDULER] Starting schedule:"
		for i in range(0, schedule_len):
			print "'time_point': {0}, 'node_id': {1}".format(self.schedule[i]["time_point"], self.schedule[i]["node"].node_id)

		return schedule_len


	def _start_schedule(self):
		schedule_len = self._print_schedule()

		for i in range(0, schedule_len):
			currently_on = self.schedule[i]
			
			if i < schedule_len - 1:
				next_on      = self.schedule[i+1]
				sleep_interval = next_on["time_point"] - currently_on["time_point"]
			else:
				sleep_interval = -1

			currently_on["node"].command_exec(payload={
					'node_id': currently_on["node"].node_id
				})

			if sleep_interval == -1:
				print "[SCHEDULER] Currently on: {0}/{1}; Last event".format(i+1, schedule_len)	
			else:
				print "[SCHEDULER] Currently on: {0}/{1}; Next event in {2} seconds".format(i+1, schedule_len, sleep_interval)
				time.sleep(sleep_interval)