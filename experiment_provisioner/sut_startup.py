import subprocess
import os
import time
import threading
from mqtt_client import MQTTClient

openwsn_dir = os.path.join(os.path.dirname(__file__), "..", "..", "openwsn")
ov_dir      = os.path.join(openwsn_dir, "openvisualizer")
coap_dir    = os.path.join(openwsn_dir, "coap")
orch_dir    = os.path.join(os.path.dirname(__file__), "..", "experiment_orchestrator")

class SUTStartup:

	def __init__(self, user_id, scenario, testbed, broker, simulator, orch_only, ov_only, ov_repo, ov_branch, coap_repo, coap_branch):
		self.testbed     = testbed
		self.scenario    = scenario
		self.broker      = broker
		self.simulator   = simulator
		self.orch_only   = orch_only
		self.ov_only     = ov_only
		self.user_id     = user_id
		self.ov_repo     = ov_repo
		self.ov_branch   = ov_branch
		self.coap_repo   = coap_repo
		self.coap_branch = coap_branch

		self.mqtt_client = MQTTClient.create(self.testbed, self.user_id)


	def start(self):
		if self.simulator or self.orch_only:
			self._start_orchestrator()
		elif self.ov_only:
			self._start_ov(False)
		else:
			self._load_dependencies()

			thread_orch = threading.Thread(target=self._start_ov)
			thread_orch.start()
		
			self._start_orchestrator()

	def data_stream_check(self):
		self.mqtt_client.check_data_stream()

	def _start_orchestrator(self):
		message = "[SUT_STARTUP] Starting orchestrator" if not self.simulator else "[SUT_STARTUP] Starting SUT simulator"
		print message 
		self.mqtt_client.push_debug_log('SUT_STARTUP', message)

		if self.simulator:
			pipe = subprocess.Popen(['python', 'main.py', '--simulator', '--testbed={0}'.format(self.testbed), '--scenario={0}'.format(self.scenario), '--user-id={0}'.format(self.user_id)], cwd=orch_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		else:
			pipe = subprocess.Popen(['python', 'main.py', '--user-id={0}'.format(self.user_id)], cwd=orch_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

		for line in iter(pipe.stdout.readline, b''):
			print(">>> " + line.rstrip())


	def _start_ov(self, async = True):
		print "[SUT_STARTUP] Starting OpenVisualizer"
		self.mqtt_client.push_debug_log('SUT_STARTUP', "Starting OpenVisualizer")
		pipe = subprocess.Popen(['scons', 'runweb', '--port=8080', '--benchmark={0}'.format(self.scenario), '--testbed={0}'.format(self.testbed), '--mqtt-broker-address={0}'.format(self.broker), '--opentun-null'], cwd=ov_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

		if not async:
			for line in iter(pipe.stdout.readline, b''):
				print(">>> " + line.rstrip())


	# Clone dependencies
	def _load_dependencies(self):
		self._delete_dependencies()
		self._clone_dependencies()

	def _delete_dependencies(self):
		self._print_log('Removing dependencies...')
		self._run_cmd('ov-delete')
		self._run_cmd('coap-delete')

	def _clone_dependencies(self):
		self._print_log('Cloning dependencies...')
		self._run_cmd('ov-clone')
		self._run_cmd('coap-clone')

	def _run_cmd(self, cmd):
		cmds = {
			"ov-clone"   : ['git', 'clone', '-b', self.ov_branch, '--single-branch', self.ov_repo],
			"coap-clone" : ['git', 'clone', '-b', self.coap_branch, '--single-branch', self.coap_repo],
			"ov-delete"  : ['sudo', 'rm', '-rf', ov_dir], 
			"coap-delete": ['sudo', 'rm', '-rf', coap_dir]
		}	

		pipe = subprocess.Popen(cmds[cmd], cwd=openwsn_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		
		for line in iter(pipe.stdout.readline, b''):
			output = line.rstrip()
			self._print_log(output)
			
		for line in iter(pipe.stderr.readline, b''):
			output = line.rstrip()
			self._print_log(output)

	def _print_log(self, message):
		self.mqtt_client.push_debug_log("[SUT_STARTUP]", message)
		print("[SUT_STARTUP] {0}".format(message))