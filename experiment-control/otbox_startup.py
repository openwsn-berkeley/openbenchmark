import paramiko
import json
import subprocess
import time
import threading
import os

from socket_io_handler import SocketIoHandler
from reservation import Reservation

class OTBoxStartup:

	CMD_ERROR                = "cmd_error"
	SSH_RETRY_TIME           = 600
	RETRY_PAUSE              =   6
	MQTT_PAUSE               =  20
	EUI64_RETREIVAL_TIMEOUT  =   5

	CLIENT                   = "OpenBenchmark"
	
	eui_retreival_started    = False

	timer                    =   0 #used for measuring the amount of time between status messages


	def __init__(self, user, domain, testbed):
		self.user            = user
		self.domain          = domain
		self.testbed         = testbed

		self.socketIoHandler = SocketIoHandler()

		self.client          = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.client.load_system_host_keys()

		self.ssh_connect()

		self.booted_nodes    = []
		self.active_nodes    = []

		self.reservation     = Reservation(user, domain)
		self.nodes           = self.reservation.get_reserved_nodes(True)
		
        # Fetch the latest version of opentestbed software in the shared A8 director of the SSH frontend
		self.ssh_command_exec('cd A8; rm -rf opentestbed; git clone https://github.com/bozidars27/opentestbed.git; cd opentestbed; git checkout origin/opentestbed-extension;')


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
				raise Exception(self.CMD_ERROR)

			return ''.join(output)

		except:
			return self.CMD_ERROR


	def boot_wait(self):
		for ind, node in enumerate(self.nodes):

			node_name = 'node-' + node.split('.')[0]
			print("Probing node: " + node_name)

			retries = 0
			num_of_retries = self.SSH_RETRY_TIME / self.RETRY_PAUSE

			while True:
				try:
					boot_op = self.ssh_command_exec('ssh -o "StrictHostKeyChecking no" root@' + node_name + ' "cd A8;"')
				except:
					print 'Error executing command: ssh -o "StrictHostKeyChecking no" root@' + node_name

				if boot_op == self.CMD_ERROR and retries <= num_of_retries:
					print("Node " + node_name + ": retrying")
					self.socketIoHandler.publish('BOOT_RETRY', node_name + ": " + str(retries) + "/" + str(num_of_retries))
					retries += 1
					time.sleep(self.RETRY_PAUSE)
				elif retries > num_of_retries:
					self.socketIoHandler.publish('BOOT_FAIL', node_name)
					break
				else:
					self.socketIoHandler.publish('NODE_BOOTED', node_name)
					self.booted_nodes.append(node)
					break

	def start(self):
		print("OTBox startup commencing...")
		self.boot_wait()

		try:
			for ind, node in enumerate(self.booted_nodes):
				node_name = 'node-' + node.split('.')[0]
				print("Starting otbox.py on " + node_name + "...")
                                self.ssh_command_exec('ssh -o "StrictHostKeyChecking no" root@' + node_name + ' "source /etc/profile; cd A8; cd opentestbed; pip install requests; killall python; python otbox.py --testbed=iotlab --broker=broker.mqttdashboard.com >& otbox-' + node_name + '.log &"')
				self.active_nodes.append(node)
				self.socketIoHandler.publish('NODE_ACTIVE', node_name)
		except:
			self.socketIoHandler.publish('NODE_ACTIVE_FAIL', node_name)
			print("Exception happened!")