from socket_io_handler import SocketIoHandler
import subprocess
import time

class ExpTerminate:

	def __init__(self):
		self.PYTHON_PROC_KILL = "sudo kill $(ps aux | grep '[p]ython' | awk '{print $2}')"
		self.DELETE_LOGS = "rm ~/soda/openvisualizer/openvisualizer/build/runui/*.log; rm ~/soda/openvisualizer/openvisualizer/build/runui/*.log.*;"

	def exp_terminate(self):
		subprocess.Popen(self.PYTHON_PROC_KILL, shell=True)
		time.sleep(3)
		subprocess.Popen(self.DELETE_LOGS, shell=True)