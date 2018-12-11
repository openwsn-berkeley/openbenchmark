from abc import abstractmethod
from mqttTest import MQTTTest

import subprocess
import os
import time
import json


class Testbed():

	EXP_CHECK_PAUSE           = 10     # pause between exp initialization and check

	OV_START_PAUSE            = 20     # pause before starting OV
	OV_MONITOR_START_PAUSE    = 20     # pause before starting OV log monitoring

	LOG_CHECK_PAUSE           = 5
	LOG_CHECK_RETRIES         = 15

	mainDir                   = os.path.join(os.path.dirname(__file__), "..")
	log_file                  = os.path.join(os.path.dirname(__file__), "..", "..", "openvisualizer", "build", "runui", "networkEvent.log")

	# Main method
	def run_action(self, action):
		self.delay(action)

		pipe = subprocess.Popen(['python', 'main.py', '--action={0}'.format(action)], cwd=self.mainDir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		res = pipe.communicate()

		return_code = pipe.returncode
		stdout      = res[0]
		stderr      = res[1]
		
		print("\n\nAction: {0}\nReturn code: {1}\nSTDOUT: {2}\nSTDERR: {3}\n\n".format(action, return_code, stdout, stderr))

		return self.output_check(action, return_code = pipe.returncode, stdout = stdout, stderr = stderr)


	def delay(self, action):
		if action == 'ov-start':
			time.sleep(self.OV_START_PAUSE)
		elif action == 'ov-monitor':
			time.sleep(self.OV_MONITOR_START_PAUSE)
		elif action == 'check':
			time.sleep(self.EXP_CHECK_PAUSE)


	def output_check(self, action, return_code, stdout = "", stderr = ""):
		if action == 'reserve':
			return self.reserve(return_code, stdout, stderr)
		elif action == 'otbox':
			return self.otbox(return_code, stdout, stderr)
		elif action == 'otbox-flash':
			return self.otbox_flash(return_code, stdout, stderr)
		elif action == 'ov-start':
			return self.ov_start(return_code, stdout, stderr)
		elif action == 'ov-monitor':
			return self.check_ov_log()
		elif action == 'check':
			return self.exp_check(return_code, stdout, stderr)
		else:
			True


	def get_last_line(self):
		if os.path.isfile(self.log_file):
			return subprocess.check_output(['tail', '-1', self.log_file])
		else:
			return ""


	def check_ov_log(self):
		
		data_recieved = False

		for i in range(0, self.LOG_CHECK_RETRIES):
			try:
				json_obj = json.loads(self.get_last_line())
				data_recieved = True
				break
			except Exception, e:
				print str(e)
				time.sleep(self.LOG_CHECK_PAUSE)

		return data_recieved



	# Abstract methods
	@abstractmethod
	def reserve(self, return_code, stdout, stderr):
		pass

	@abstractmethod
	def otbox(self, return_code, stdout, stderr):
		pass

	@abstractmethod
	def otbox_flash(self, return_code, stdout, stderr):
		pass

	@abstractmethod
	def ov_start(self, return_code, stdout, stderr):
		pass

	@abstractmethod
	def exp_check(self, return_code, stdout, stderr):
		pass



###################### CHILD CLASSES ######################
  


class IoTLAB(Testbed):

	def reserve(self, return_code, stdout, stderr):
		return return_code == 0 and stderr == '' and self.run_action('check')

	def otbox(self, return_code, stdout, stderr):
		mqttTest = MQTTTest('iotlab')
		return return_code == 0 and stderr == '' and mqttTest.check_data()

	def otbox_flash(self, return_code, stdout, stderr):
		mqttTest = MQTTTest('iotlab')
		return return_code == 0 and stderr == '' and mqttTest.check_data()

	def ov_start(self, return_code, stdout, stderr):
		return return_code == 0 and stderr == ''

	def exp_check(self, return_code, stdout, stderr):
		line = stdout.split('Experiment check: ')[1].replace(" ", "")
		json_obj = None
		
		try:
			json_obj = json.loads(line)
		except Exception, e:
			json_obj = None

		return return_code == 0 and stderr == '' and json_obj != None
