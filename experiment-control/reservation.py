from abc import abstractmethod

from socket_io_handler import SocketIoHandler
from exp_terminate import ExpTerminate

import paramiko
import json
import time


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

	def __init__(self, user, domain, duration, nodes):
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
		if self.check_experiment():
			output = self.ssh_command_exec('iotlab-experiment get -p')
			json_output = json.loads(output)['nodes']
			return json_output
		else:
			return []


	# Abstract method implementations

	def reserve_experiment(self):
		if self.check_experiment():
			self.socketIoHandler.publish('NODE_RESERVATION', 'Experiment exists')
		else:
			output = self.ssh_command_exec('iotlab-experiment submit -n a8_exp -d ' + str(self.duration) + ' -l ' + self.nodes)
			if output != self.CMD_ERROR:
				self.experiment_id = json.loads(output)['id']
				self.socketIoHandler.publish('NODE_RESERVATION', 'All nodes reserved')


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
		ExpTerminate().exp_terminate()

				
			
		
