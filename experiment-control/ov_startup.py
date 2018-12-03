import subprocess
import os
from distutils import spawn as s

# OpenVisualizer (scons) needs to run with sudo privileges.
# This creates a problem with dependencies if Python is executed within a virtualenv, as using sudo will bypass the environment variables
# Therefore, we explicitly invoke scons using the Python path from the virtualenv before sudo is invoked
pythonPath = s.find_executable("python")
sconsPath = s.find_executable("scons")

ovDir = os.path.join(os.path.dirname(__file__), "..", "openvisualizer")

class OVStartup:

	def start(self):
		subprocess.Popen(['sudo', pythonPath, sconsPath, 'runweb', '--port=8080', '--testbed=iotlab', '--broker=broker.mqttdashboard.com', '--root=random'], cwd=ovDir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
