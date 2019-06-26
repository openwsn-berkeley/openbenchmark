import os
import subprocess
import random
import string

from mqtt_client import MQTTClient


class FWCompiler:

	def __init__(self, repo_url, branch, testbed, user_id):
		self.repo_url    = repo_url
		self.branch      = branch
		self.repo_name   = self._get_repo_name()
		self.testbed     = testbed
		self.user_id     = user_id  
		self.local_repo  = os.path.join(os.path.dirname(__file__), self.repo_name)
		self.mqtt_client = MQTTClient.create(testbed, user_id)

		self.board_names = {
			"iotlab" : "iot-lab_A8-M3",
			"wilab"  : "remote" 
		}

	def compile(self):
		self._clone_branch()
		fw_name = self._compile_fw()
		self._move_fw(fw_name)
		self._delete_branch()

		return fw_name


	def _clone_branch(self):
		self.mqtt_client.push_debug_log('FW_COMPILATION', 'Cloning the branch...')
		print("[FW_COMPILATION] Cloning the branch...")
		clone_fw_repo = "git clone -b {0} --single-branch {1}".format(self.branch, self.repo_url)
		subprocess.Popen(clone_fw_repo, shell=True)		

	def _compile_fw(self):
		fw_name = self._generate_random_fw_name()
		pipe = subprocess.Popen(['scons', 'board={0}'.format(self.board_names[self.testbed]), 'toolchain=armgcc', 'apps=cbenchmark', ], 
				cwd=self.local_repo, 
				stdin=subprocess.PIPE,
				stderr=subprocess.PIPE, 
				stdout=subprocess.PIPE
			)

        for line in iter(pipe.stdout.readline, b''):
            output = line.rstrip()
            print(">>> " + output)
            self.mqtt_client.push_debug_log('FW_COMPILATION', output)

        for line in iter(pipe.stderr.readline, b''):
            output = line.rstrip()
            print(">>> " + output)
            self.mqtt_client.push_debug_log('FW_COMPILATION [ERROR]', output)

	def _delete_branch(self):
		self.mqtt_client.push_debug_log('FW_COMPILATION', 'Removing the cloned repo...')
		print("[FW_COMPILATION] Removing the cloned repo...")
		del_dir = "rm -rf {0}".format(self.repo_name)
		subprocess.Popen(del_dir, shell=True)

	def _get_repo_name(self):
		url_split = self.url.split('/')
		return url_split[len(url_split) - 1].split('.')[0]

	def _generate_random_fw_name(self):
		letters = string.ascii_lowercase
		suffix  = ''.join(random.choice(letters) for i in range(10))
		return "{0}_{1}_{2}".format(self.repo_name, self.branch, suffix)