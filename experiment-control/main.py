import argparse
import ConfigParser
import os
import base64

from abc import abstractmethod
from reservation import IoTLABReservation
from reservation import WilabReservation

from otbox_startup import OTBoxStartup
from otbox_flash import OTBoxFlash
from ov_startup import OVStartup
from ov_log_monitor import OVLogMonitor

class Controller(object):

	CONFIG_FILE = 'conf.txt'

	def __init__(self):
		self.configParser = ConfigParser.RawConfigParser()   
		self.configFilePath = os.path.join(os.path.dirname(__file__), self.CONFIG_FILE)
		self.configParser.read(self.configFilePath)

	def add_parser_args(self, parser):
		parser.add_argument('--action', 
	        dest       = 'action',
	        choices    = ['check', 'reserve', 'terminate', 'otbox-flash', 'ov-start', 'ov-monitor'],
	        required   = True,
	        action     = 'store'
		)
		parser.add_argument('--testbed', 
	        dest       = 'testbed',
	        choices    = ['iotlab', 'wilab'],
	        default    = 'iotlab',
	        action     = 'store'
		)
		parser.add_argument('--firmware', 
	        dest       = 'firmware',
	        default    = '03oos_openwsn_prog',
	        action     = 'store'
		)

	def get_args(self):
		parser = argparse.ArgumentParser()
		self.add_parser_args(parser)
		args = parser.parse_args()

		return {
			'action'  : args.action,
			'testbed' : args.testbed,
			'firmware': args.firmware
		}

	@abstractmethod
	def add_files_from_env(self):
		pass


class IoTLAB(Controller):

	def __init__(self):
		super(IoTLAB, self).__init__()

		self.CONFIG_SECTION = 'iotlab-config'

		self.USERNAME = os.environ["user"] if "user" in os.environ else self.configParser.get(self.CONFIG_SECTION, 'user')
		self.PRIVATE_SSH = os.environ["private_ssh"] if "private_ssh" in os.environ else ""
		self.HOSTNAME = 'saclay.iot-lab.info'

		self.EXP_DURATION = 30 # Duration in minutes
		self.NODES = "saclay,a8,106+107" # To be read from scenario config

		self.FIRMWARE = os.path.join(os.path.dirname(__file__), 'firmware')
		self.BROKER = self.configParser.get(self.CONFIG_SECTION, 'broker')

		self.reservation = IoTLABReservation(self.USERNAME, self.HOSTNAME, self.EXP_DURATION, self.NODES)
		self.add_files_from_env()

	def add_files_from_env(self):
		if self.PRIVATE_SSH != "":
			private_ssh_file = os.path.join(os.path.expanduser("~"), ".ssh", "id_rsa")
			private_ssh_decoded = base64.b64decode(self.PRIVATE_SSH)

			with open(private_ssh_file, "w") as f:
				f.write(private_ssh_decoded)


class Wilab(Controller):

	def __init__(self):
		super(Wilab, self).__init__()

		self.CONFIG_SECTION = 'wilab-config'

		# Checks if the following files' content has been set as env variables content
		# The content is encoded in Base64
		# Putting files in env variables is necessarry for supplying Travis builds with private data 
		self.CERTIFICATE_B64 = os.environ["certificate"] if "certificate" in os.environ else ""
		self.DELETE_B64 = os.environ["delete"] if "delete" in os.environ else ""
		self.RUN_B64 = os.environ["run"] if "run" in os.environ else ""

		# The nodes will be defined by RSpec file within ESpec directory.
		# Each scenario should have its own RSpec. RSpecs should be chosen based on scenario config
		self.JFED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'helpers', 'wilab', 'jfed_cli'))
		self.DELETE   = 'delete_experiment.sh' # Script for terminating the experiment
		self.RUN      = 'start_experiment.sh'  # Script for starting the experiment
		self.DISPLAY  = 'start_display.sh'     # Script for starting a fake display

		self.FIRMWARE = os.path.join(os.path.dirname(__file__), 'firmware')
		self.BROKER = self.configParser.get(self.CONFIG_SECTION, 'broker')

		self.reservation = WilabReservation(self.JFED_DIR, self.RUN, self.DELETE, self.DISPLAY)

	def add_files_from_env(self):
		if self.CERTIFICATE_B64 != "":
			file_decoded = base64.b64decode(self.CERTIFICATE_B64)
			with open(self.CERTIFICATE, "w") as f:
				f.write(file_decoded)

		if self.DELETE_B64 != "":
			file_decoded = base64.b64decode(self.DELETE_B64)
			with open(os.path.join(self.JFED_DIR, self.DELETE), "w") as f:
				f.write(file_decoded)

		if self.RUN_B64 != "":
			file_decoded = base64.b64decode(self.RUN_B64)
			with open(os.path.join(self.JFED_DIR, self.RUN), "w") as f:
				f.write(file_decoded)



TESTBEDS = {
	"iotlab": IoTLAB,
	"wilab": Wilab
}

def main():
	controller = Controller()

	args = controller.get_args()

	action = args['action']
	testbed = args['testbed']

	testbed = TESTBEDS[testbed]()
	firmware = '{0}/{1}'.format(testbed.FIRMWARE, args['firmware'])

	print 'Script started'
	
	if action == 'reserve':
		print 'Reserving nodes'
		testbed.reservation.reserve_experiment()
	elif action == 'check':
		print 'Checking experiment'
		testbed.reservation.check_experiment()
	elif action == 'terminate':
		print 'Terminating experiment'
		testbed.reservation.terminate_experiment()
	elif action == 'otbox-flash':
		print 'Flashing OTBox'
		OTBoxFlash(firmware, testbed.BROKER, args['testbed']).flash()
	elif action == 'ov-start':
		print 'Starting OV'
		OVStartup().start()
	elif action == 'ov-monitor':
		print 'Starting OV log monitoring'
		OVLogMonitor().start()


if __name__ == '__main__':
	main()

