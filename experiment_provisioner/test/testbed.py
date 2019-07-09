from abc import abstractmethod
from mqttTest import MQTTTest

import subprocess
import os
import time
import json
import warnings


class Testbed():

	EXP_CHECK_PAUSE           = 10     # pause between exp initialization and check
	OV_START_PAUSE            = 20     # pause before starting OV
	mainDir                   = os.path.join(os.path.dirname(__file__), "..", "..")

	# Main method
	def run_action(self, action):
		self.delay(action)

		if (action != 'sut-start'):
			pipe = subprocess.Popen(['python', 'openbenchmark.py', '--action={0}'.format(action), '--user-id=1'], cwd=self.mainDir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
			res = pipe.communicate()

			return_code = pipe.returncode
			stdout      = res[0]
			stderr      = res[1]
			
			print("\n\nAction: {0}\nReturn code: {1}\nSTDOUT: {2}\nSTDERR: {3}\n\n".format(action, return_code, stdout, stderr))
			return self.output_check(action, return_code = pipe.returncode, stdout = stdout, stderr = stderr)

		else: 
			subprocess.Popen(['python', 'openbenchmark.py', '--action={0}'.format(action), '--user-id=1 &'], cwd=self.mainDir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
			return self.output_check(action, return_code = 0)



	def delay(self, action):
		if action == 'sut-start':
			time.sleep(self.OV_START_PAUSE)
		elif action == 'check':
			time.sleep(self.EXP_CHECK_PAUSE)


	def output_check(self, action, return_code, stdout = "", stderr = ""):
		if action == 'reserve':
			return self.reserve(return_code, stdout, stderr)
		elif action == 'flash':
			return self.flash(return_code, stdout, stderr)
		elif action == 'sut-start':
			return self.ov_start(return_code, stdout, stderr)
		elif action == 'check':
			return self.exp_check(return_code, stdout, stderr)
		else:
			True


	# Abstract methods
	@abstractmethod
	def reserve(self, return_code, stdout, stderr):
		pass

	@abstractmethod
	def flash(self, return_code, stdout, stderr):
		pass

	@abstractmethod
	def ov_start(self, return_code, stdout, stderr):
		pass



###################### CHILD CLASSES ######################
  


class IoTLAB(Testbed):

	def reserve(self, return_code, stdout, stderr):
		mqttTest = MQTTTest('iotlab', 'reserve')
		return return_code == 0 and stderr == '' and mqttTest.check_data()

	def flash(self, return_code, stdout, stderr):
		mqttTest = MQTTTest('iotlab', 'flash')
		return return_code == 0 and stderr == '' and mqttTest.check_data()

	def ov_start(self, return_code, stdout, stderr):
		mqttTest = MQTTTest('iotlab', 'sut-start')
		return return_code == 0 and stderr == '' and mqttTest.check_data()