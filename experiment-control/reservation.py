import sys
sys.path.insert(0, 'helpers/iotlab')

from abc import abstractmethod

from socket_io_handler import SocketIoHandler

import os
import paramiko
import json
import time
import subprocess

from otbox_startup import OTBoxStartup


class Reservation:
	@abstractmethod
	def reserve_experiment(self):
		pass

	@abstractmethod
	def check_experiment(self):
		pass

	@abstractmethod
	def terminate_experiment(self):
		pass



class IoTLABReservation(Reservation):

	CMD_ERROR      = "cmd_error"
	SSH_RETRY_TIME = 120
	RETRY_PAUSE    = 10

	def __init__(self, user, domain, duration=None, nodes=None):
		self.user     = user
		self.domain   = domain
		self.duration = duration
		self.nodes    = nodes

		self.socketIoHandler = SocketIoHandler()

		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.client.load_system_host_keys()

		self.ssh_connect()

	def ssh_connect(self):
		self.client.connect(self.domain, username=self.user)

	def ssh_disconnect(self):
		self.client.close()

	def ssh_command_exec(self, command):
		try:
			stdin, stdout, stderr = self.client.exec_command(command)
			stdin.close()

			output = []
			for line in stdout.read().splitlines():
				output.append(line)

			error = []
			for line in stderr.read().splitlines():
				error.append(line)

			if len(error) > 0:
				print("Error: " + ''.join(error))
				raise Exception(self.CMD_ERROR)

			return ''.join(output)

		except:
			return self.CMD_ERROR


	def get_reserved_nodes(self):
		if self.check_experiment(True):
			output = self.ssh_command_exec('iotlab-experiment get -p')
			json_output = json.loads(output)['nodes']
			return json_output
		else:
			return []


	####### Abstract method implementations #######

	def reserve_experiment(self):
		if self.check_experiment():
			self.socketIoHandler.publish('NODE_RESERVATION', 'Experiment exists')
		else:
			output = self.ssh_command_exec('iotlab-experiment submit -n a8_exp -d ' + str(self.duration) + ' -l ' + self.nodes)
			if output != self.CMD_ERROR:
				self.experiment_id = json.loads(output)['id']
				self.socketIoHandler.publish('NODE_RESERVATION', 'All nodes reserved')

				nodes = self.get_reserved_nodes()

				if len(nodes) > 0:
					OTBoxStartup(self.user, self.domain, 'iotlab', self.get_reserved_nodes()).start()
				else:
					print('Experiment startup failed')


	def check_experiment(self, loop=False):
		retries = 0
		num_of_retries = self.SSH_RETRY_TIME / self.RETRY_PAUSE

		json_output = []

		while True:

			output = self.ssh_command_exec('iotlab-experiment get -p')

			if output != self.CMD_ERROR:
				print("Experiment check: " + output)
				json_output = json.loads(output)['nodes']
				return True
			elif retries <= num_of_retries:
				self.socketIoHandler.publish('RESERVATION_STATUS_RETRY', str(retries) + "/" + str(num_of_retries))
				retries += 1
				time.sleep(self.RETRY_PAUSE)
			else:
				self.socketIoHandler.publish('RESERVATION_FAIL', str(retries) + "/" + str(num_of_retries))
				break

			if not loop:
				break

		return False


	def terminate_experiment(self):
		self.ssh_command_exec('iotlab-experiment stop')
		self.socketIoHandler.publish('EXP_TERMINATE', '')
		
		python_proc_kill = "sudo kill $(ps aux | grep '[p]ython' | awk '{print $2}')"
		delete_logs = "rm ~/soda/openvisualizer/openvisualizer/build/runui/*.log; rm ~/soda/openvisualizer/openvisualizer/build/runui/*.log.*;"

		subprocess.Popen(python_proc_kill, shell=True)
		time.sleep(3)
		subprocess.Popen(delete_logs, shell=True)




class WilabReservation(Reservation):

	def __init__(self, jfed_dir, run, delete, display):
		self.jfed_dir = jfed_dir
		self.actions = {
			"run"    : run,
			"delete" : delete,
			"display": display
		}

	def run_yml_action(self, action):
		if action != 'display':
			self._start_display()

		pipe = subprocess.Popen(['sh', self.actions[action]], cwd=self.jfed_dir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		
		for line in iter(pipe.stdout.readline, b''):
			print(">>> " + line.rstrip())

	def _start_display(self):
		pipe = subprocess.Popen(['xrandr', '-d', ':99'], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		pipe.communicate()

		if pipe.returncode != 0:
			pipe = subprocess.Popen(['export', 'DISPLAY=:99'], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)



	####### Abstract method implementation #######

	def reserve_experiment(self):
		self.run_yml_action(action="run")

	def check_experiment(self):
		# TO-DO
		pass

	def terminate_experiment(self):
		self.run_yml_action(action="delete")

