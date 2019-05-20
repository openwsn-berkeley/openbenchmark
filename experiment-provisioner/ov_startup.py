import subprocess
import os
import time
import threading
from mqtt_client import MQTTClient

ov_dir   = os.path.join(os.path.dirname(__file__), "..", "openvisualizer")
orch_dir = os.path.join(os.path.dirname(__file__), "..", "experiment-orchestrator")


class OVStartup:

	def __init__(self, user_id, scenario, testbed, broker, simulator):
		self.testbed   = testbed
		self.scenario  = scenario
		self.broker    = broker
		self.simulator = simulator
		self.user_id   = user_id

		self.mqtt_client = MQTTClient.create(self.testbed, self.user_id)


	def start(self):
		if self.simulator:
			self._start_orchestrator()
		else:
			thread_orch = threading.Thread(target=self._start_orchestrator)
			thread_orch.start()
		
			self._start_ov()

	def data_stream_check(self):
		self.mqtt_client.check_data_stream()

	def _start_orchestrator(self):
		print "[OV STARTUP] Starting orchestrator"
		self.mqtt_client.push_debug_log('OV_STARTUP', "Starting orchestrator")

		if self.simulator:
			pipe = subprocess.Popen(['python', 'main.py', '--simulator', '--testbed={0}'.format(self.testbed), '--scenario={0}'.format(self.scenario), '--user-id={0}'.format(self.user_id)], cwd=orch_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		else:
			pipe = subprocess.Popen(['python', 'main.py', '--user-id={0}'.format(self.user_id)], cwd=orch_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

		for line in iter(pipe.stdout.readline, b''):
			print(">>> " + line.rstrip())


	def _start_ov(self):
		print "[OV STARTUP] Starting OpenVisualizer"
		self.mqtt_client.push_debug_log('OV_STARTUP', "Starting OpenVisualizer")

		subprocess.Popen(['sudo', 'scons', 'runweb', '--port=8080', '--benchmark={0}'.format(self.scenario), '--testbed={0}'.format(self.testbed), '--mqttBroker={0}'.format(self.broker)], cwd=ov_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)