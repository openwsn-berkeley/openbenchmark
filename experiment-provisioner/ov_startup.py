import subprocess
import os
from mqtt_client import MQTTClient

ovDir = os.path.join(os.path.dirname(__file__), "..", "openvisualizer")

class OVStartup:

	def __init__(self):
		self.mqtt_client = MQTTClient.create("iotlab")

	def start(self):
		subprocess.Popen(['sudo', 'scons', 'runweb', '--port=8080', '--testbed=iotlab', '--mqttBroker=argus.paris.inria.fr'], cwd=ovDir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

	def data_stream_check(self):
		self.mqtt_client.check_data_stream()