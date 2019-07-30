import subprocess
import os
import time
import threading
import json
from mqtt_client import MQTTClient

openwsn_dir = os.path.join(os.path.dirname(__file__), "..", "..", "openwsn")
ov_dir      = os.path.join(openwsn_dir, "openvisualizer")
coap_dir    = os.path.join(openwsn_dir, "coap")
ob_dir      = os.path.join(os.path.dirname(__file__), "..")
orch_dir    = os.path.join(os.path.dirname(__file__), "..", "experiment_orchestrator")
sc_conf_dir = os.path.join(ob_dir, "scenario-config")

class SUTStartup:

	def __init__(self, user_id, scenario, testbed, simulator, orch_only, ov_only, ov_repo, ov_branch, coap_repo, coap_branch):
		self.testbed     = testbed
		self.scenario    = scenario
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

			thread_orch = threading.Thread(target=self._start_ov, args=[False])
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
			self.mqtt_client.push_debug_log('ORCHESTRATOR', line.rstrip())


	def _start_ov(self, async = True):
		if self.testbed == 'opensim':
			self._start_open_sim(async)
		else:
			self._start_ov_regular(async)

	def _start_ov_regular(self, async):
		print "[SUT_STARTUP] Starting OpenVisualizer"
		self.mqtt_client.push_debug_log('SUT_STARTUP', "Starting OpenVisualizer")
		pipe = subprocess.Popen(['sudo', 'scons', 'runweb', '--port=8080', '--benchmark={0}'.format(self.scenario), '--testbed={0}'.format(self.testbed), '--mqtt-broker-address={0}'.format(self.mqtt_client.broker), '--opentun-null'], cwd=ov_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

		if not async:
			for line in iter(pipe.stdout.readline, b''):
				print(">>> " + line.rstrip())
				self.mqtt_client.push_debug_log('OPENVISUALIZER', line.rstrip())

	def _get_node_num(self):
		scenario_config_json = os.path.join(sc_conf_dir, self.scenario, '_config.json')
		with open(scenario_config_json, 'r') as f:
			config_obj = json.loads(f.read())
			return config_obj['number_of_nodes']

	def _start_open_sim(self, async):
		print "[SUT_STARTUP] Starting OpenSim"
		self.mqtt_client.push_debug_log('SUT_STARTUP', "Starting OpenSim")
		pipe = subprocess.Popen(['sudo', 'scons', 'runweb', '--sim', '--simCount={0}'.format(self._get_node_num()), '--port=8080', '--benchmark={0}'.format(self.scenario), '--mqtt-broker-address={0}'.format(self.mqtt_client.broker), '--opentun-null'], cwd=ov_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

		if not async:
			for line in iter(pipe.stdout.readline, b''):
				print(">>> " + line.rstrip())
				self.mqtt_client.push_debug_log('OPENVISUALIZER', line.rstrip())


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