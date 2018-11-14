from socket_io_handler import SocketIoHandler
from exp_terminate import ExpTerminate

import paramiko
import json
import time

class Reservation:

	CMD_ERROR = "cmd_error"
	SSH_RETRY_TIME = 120
	RETRY_PAUSE = 10

	def __init__(self, user, domain):
		self.user = user
		self.domain = domain

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


	def reserve_experiment(self, duration, nodes):
		if self.check_experiment():
			self.socketIoHandler.publish('NODE_RESERVATION', 'Experiment exists')
		else:
			output = self.ssh_command_exec('iotlab-experiment submit -n a8_exp -d ' + str(duration) + ' -l ' + nodes)
			if output != self.CMD_ERROR:
				self.experiment_id = json.loads(output)['id']
				self.socketIoHandler.publish('NODE_RESERVATION', 'All nodes reserved')


	def get_reserved_nodes(self, logging):
		retries = 0
		num_of_retries = self.SSH_RETRY_TIME / self.RETRY_PAUSE

		json_output = []

		while True:

			output = self.ssh_command_exec('iotlab-experiment get -p')

			if output != self.CMD_ERROR:
				json_output = json.loads(output)['nodes']
				break
			elif retries <= num_of_retries:
				self.socketIoHandler.publish('RESERVATION_STATUS_RETRY', str(retries) + "/" + str(num_of_retries))
				retries += 1
				time.sleep(self.RETRY_PAUSE)
			else:
				self.socketIoHandler.publish('RESERVATION_FAIL', str(retries) + "/" + str(num_of_retries))
				break

		self.socketIoHandler.publish('RESERVATION_SUCCESS', output)
		return json_output

	def check_experiment(self):
		output = self.ssh_command_exec('iotlab-experiment get -p')
		print("Experiment check: " + output)
		return output != self.CMD_ERROR

	def terminate_experiment(self):
		self.ssh_command_exec('iotlab-experiment stop')
		self.socketIoHandler.publish('EXP_TERMINATE', '')
		ExpTerminate().exp_terminate()
