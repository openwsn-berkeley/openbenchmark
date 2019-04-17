import subprocess
import os
import time
from mqtt_client import MQTTClient

ov_dir   = os.path.join(os.path.dirname(__file__), "..", "openvisualizer")
orch_dir = os.path.join(os.path.dirname(__file__), "..", "experiment-orchestrator")


class OVStartup:

	def __init__(self, scenario, testbed, broker, simulator):
		self.testbed   = testbed
		self.scenario  = scenario
		self.broker    = broker
		self.simulator = simulator

		self.orchestartor_wait = 5    # in seconds

		self.mqtt_client = MQTTClient.create(self.testbed)


	def start(self):
		self._start_orchestrator()
		if not self.simulator:
			time.sleep(self.orchestartor_wait)
			self._start_ov()

	def data_stream_check(self):
		self.mqtt_client.check_data_stream()

	def _start_orchestrator(self):
		print "[OV STARTUP] Starting orchestrator"
		if self.simulator:
			pipe = subprocess.Popen(['python', 'main.py', '--simulator', '--testbed={0}'.format(self.testbed), '--scenario={0}'.format(self.scenario)], cwd=orch_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		else:
			pipe = subprocess.Popen(['python', 'main.py'], cwd=orch_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

		for line in iter(pipe.stdout.readline, b''):
			print(">>> " + line.rstrip())

		for line in iter(pipe.stderr.readline, b''):
			print(">>> " + line.rstrip())


	def _start_ov(self):
		print "[OV STARTUP] Starting openvisualizer"
		subprocess.Popen(['sudo', 'scons', 'runweb', '--port=8080', '--benchmark={0}'.format(self.scenario), '--testbed={0}'.format(self.testbed), '--mqttBroker={0}'.format(self.broker)], cwd=ov_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)