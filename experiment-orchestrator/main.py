import sys
import os
import threading
import random
import string
import json
from utils import Utils
from sut_simulator.simulator import Simulator
from mqtt_client.mqtt_client import MQTTClient
from kpi.processing import KPIProcessing
from mqtt_client._condition_object import ConditionObject
from scheduler import Scheduler


class Main():

	def __init__(self, simulator=True, full_bgd=False):
		Utils.experiment_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))

		if simulator:
			print "[MAIN] Starting simulator"
			threading.Thread(target=self._start_simulator).start()

		print "[MAIN] Starting MQTT client"
		MQTTClient.create()

		self.co = ConditionObject.create()
		print "[MAIN] Acquiring lock..."
		self.co.start_benchmark_cv.acquire()
		self.co.start_benchmark_cv.wait()
		self.co.start_benchmark_cv.release()
		print "[MAIN] Lock released on `startBenchmark` command"
		self.sut_command_payload = self.co.sut_command_payload

		threading.Thread(target=self._start_scheduler).start()
		threading.Thread(target=self._start_kpi_processing).start()


	def _start_scheduler(self):
		Scheduler(json.dumps(self.sut_command_payload))

	def _start_kpi_processing(self):
		KPIProcessing().start()

	def _start_simulator(self):
		Simulator.create()

	
if __name__ == "__main__":
	try: 
		Main()
	except Exception, e:
		print("Exception: " + str(e))