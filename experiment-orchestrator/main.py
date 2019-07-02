import sys
import os
import threading
import random
import string
import json
import argparse
import colorama
import time
from utils import Utils
from network_prep import NetworkPrep
from sut_simulator.simulator import Simulator
from mqtt_client.mqtt_client import MQTTClient
from kpi.processing import KPIProcessing
from mqtt_client._condition_object import ConditionObject
from scheduler import Scheduler


class Main():

	def __init__(self):
		Utils.experiment_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))

		self._take_arguments()

		colorama.init()

		print "[MAIN] Starting MQTT client"
		self.mqtt_client = MQTTClient.create()

		if self.simulator:
			self.mqtt_client.push_debug_log("[ORCHESTRATOR]", 'Starting simulator')
			thread = threading.Thread(target=self._start_simulator)
			thread.daemon = True
			thread.start()

		self.co = ConditionObject.create()
		self.mqtt_client.push_debug_log("[ORCHESTRATOR]", 'Acquiring lock...')
		self.co.start_benchmark_cv.acquire()
		self.co.start_benchmark_cv.wait()
		self.co.start_benchmark_cv.release()
		self.mqtt_client.push_debug_log("[ORCHESTRATOR]", 'Lock released on `startBenchmark` command')
		self.sut_command_payload = self.co.sut_command_payload

		self.mqtt_client.push_debug_log("[ORCHESTRATOR]", self.sut_command_payload)

		# give SUT some time subscribe to the topics before firing
		time.sleep(5)

		self._start_network_prep()
		thread = threading.Thread(target=self._start_kpi_processing)
		thread.daemon = True
		thread.start()

		time_padding = 0.1 if self.simulator else Utils.scenario.main_config['nf_time_padding_min']
		self.mqtt_client.push_debug_log("[ORCHESTRATOR]", "Scheduler will start in {0} minutes...".format(time_padding))

		self.mqtt_client.push_notification("network-configured", True)

		time.sleep(time_padding*60)
		self._start_scheduler()
		
		
	def _take_arguments(self):
		parser = argparse.ArgumentParser()
		self._add_parser_args(parser)
		args = parser.parse_args()

		self.simulator = args.simulator
		self.testbed   = args.testbed
		self.scenario  = args.scenario

		if self.simulator and (self.testbed == None or self.scenario == None):
			parser.error('--simulator requires both --testbed and --scenario')
			self.mqtt_client.push_debug_log("[ORCHESTRATOR]", "Error: --simulator requires both --testbed and --scenario")

		Utils.user_id = args.user_id

	def _add_parser_args(self, parser):
		parser.add_argument('--user-id', 
	        dest       = 'user_id',
	        default    = 0,
	        required   = False,
	        action     = 'store'
	    )
		parser.add_argument('--simulator', 
	        dest       = 'simulator',
	        default    = False,
	        action     = 'store_true'
	    )
		parser.add_argument('--testbed', 
	        dest       = 'testbed',
	        choices    = ['iotlab', 'wilab', 'opensim'],
	        default    = 'iotlab',
	        action     = 'store'
		)
		parser.add_argument('--scenario', 
	        dest       = 'scenario',
	        choices    = ['demo-scenario', 'building-automation', 'home-automation', 'industrial-monitoring'],    # building-automation, home-automation, industrial-monitoring
	        action     = 'store'
		)


	def _start_network_prep(self):
		NetworkPrep(json.dumps(self.sut_command_payload)).start()

	def _start_kpi_processing(self):
		KPIProcessing().start()

	def _start_scheduler(self):
		Scheduler().start()

	def _start_simulator(self):
		Simulator.create(testbed=self.testbed, scenario=self.scenario)

	
if __name__ == "__main__":
	Main()