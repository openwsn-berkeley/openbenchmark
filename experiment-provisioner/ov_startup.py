import subprocess
import os

ovDir = os.path.join(os.path.dirname(__file__), "..", "..", "openwsn", "openvisualizer")

class OVStartup:

	def start(self):
		subprocess.Popen(['sudo', 'scons', 'runweb', '--port=8080', '--testbed=iotlab', '--mqttBroker=argus.paris.inria.fr'], cwd=ovDir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
