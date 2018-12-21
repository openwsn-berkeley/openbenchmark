import argparse
import ConfigParser
import os
import base64

from reservation import IoTLABReservation

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
	        choices    = ['iotlab', 'opentestbed'],
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


class IoTLAB(Controller):

	def __init__(self):
		super(IoTLAB, self).__init__()

		self.USERNAME = os.environ["user"] if "user" in os.environ else self.configParser.get('exp-config', 'user')
		self.PRIVATE_SSH = os.environ["private_ssh"] if "private_ssh" in os.environ else ""
		self.HOSTNAME = 'saclay.iot-lab.info'

		self.EXP_DURATION = 30 # Duration in minutes
		self.NODES = "saclay,a8,106+107" # To be read from scenario config

		self.FIRMWARE = os.path.join(os.path.dirname(__file__), 'firmware')
		self.BROKER = self.configParser.get('exp-config', 'broker')

		self.reservation = IoTLABReservation(self.USERNAME, self.HOSTNAME, self.EXP_DURATION, self.NODES)
		self.add_private_key()

	def add_private_key(self):
		if self.PRIVATE_SSH != "":
			private_ssh_file = os.path.join(os.path.expanduser("~"), ".ssh", "id_rsa")

			private_ssh_decoded = base64.b64decode(self.PRIVATE_SSH)

			with open(private_ssh_file, "w") as f:
				f.write(private_ssh_decoded)


TESTBEDS = {
	"iotlab": IoTLAB
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
	elif action == 'otbox':
		print 'Starting OTBox'
		OTBoxStartup(USERNAME, HOSTNAME, testbed).start()
	elif action == 'otbox-flash':
		print 'Flashing OTBox'
		OTBoxFlash(firmware, BROKER, testbed).flash()
	elif action == 'ov-start':
		print 'Starting OV'
		OVStartup().start()
	elif action == 'ov-monitor':
		print 'Starting OV log monitoring'
		OVLogMonitor().start()


if __name__ == '__main__':
	main()

