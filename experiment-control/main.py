import argparse
import ConfigParser
import os
import base64
import json
import xml.etree
import xml.etree.ElementTree as ET

from lxml import etree
from abc import abstractmethod
from reservation import IoTLABReservation
from reservation import WilabReservation

from otbox_startup import OTBoxStartup
from otbox_flash import OTBoxFlash
from ov_startup import OVStartup
from ov_log_monitor import OVLogMonitor

class Controller(object):

	CONFIG_FILE = 'conf.txt'
	SCENARIO_CONFIG = os.path.join(os.path.dirname(__file__), "..", "scenario-config")

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
		parser.add_argument('--scenario', 
	        dest       = 'scenario',
	        choices    = ['building-automation', 'home-automation', 'industrial-monitoring'],
	        required   = True,
	        action     = 'store'
		)

	def get_args(self):
		parser = argparse.ArgumentParser()
		self.add_parser_args(parser)
		args = parser.parse_args()

		return {
			'action'  : args.action,
			'testbed' : args.testbed,
			'firmware': args.firmware,
			'scenario': args.scenario
		}

	@abstractmethod
	def add_files_from_env(self):
		pass


class IoTLAB(Controller):

	def __init__(self, scenario):
		super(IoTLAB, self).__init__()

		self.CONFIG_SECTION = 'iotlab-config'
		self.scenario = scenario

		self.USERNAME = os.environ["user"] if "user" in os.environ else self.configParser.get(self.CONFIG_SECTION, 'user')
		self.PRIVATE_SSH = os.environ["private_ssh"] if "private_ssh" in os.environ else ""
		self.HOSTNAME = 'saclay.iot-lab.info'

		self.EXP_DURATION = 30 # Duration in minutes
		self.NODES = self._get_nodes()

		self.FIRMWARE = os.path.join(os.path.dirname(__file__), 'firmware')
		self.BROKER = self.configParser.get(self.CONFIG_SECTION, 'broker')

		self.reservation = IoTLABReservation(self.USERNAME, self.HOSTNAME, self.BROKER, self.EXP_DURATION, self.NODES)
		self.add_files_from_env()

	def add_files_from_env(self):
		if self.PRIVATE_SSH != "":
			private_ssh_file = os.path.join(os.path.expanduser("~"), ".ssh", "id_rsa")
			private_ssh_decoded = base64.b64decode(self.PRIVATE_SSH)

			with open(private_ssh_file, "w") as f:
				f.write(private_ssh_decoded)

	def _get_nodes(self):
		# e.g. "saclay,a8,106+107"
		config_file = os.path.join(self.SCENARIO_CONFIG, self.scenario, "_iotlab_config.json")
		
		with open(config_file, 'r') as f:
			config_obj = json.load(f)
			nodes_str = 'saclay,a8,'

			for generic_id in config_obj:
				nodes_str += config_obj[generic_id]["node_id"].split("-")[2] + "+"

			return nodes_str.rstrip("+")


class Wilab(Controller):

	def __init__(self, scenario):
		super(Wilab, self).__init__()

		self.CONFIG_SECTION = 'wilab-config'
		self.scenario = scenario

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

		self._rspec_update()

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

	def _rspec_update(self):
		rspec_file = os.path.join(self.JFED_DIR, "opentestbed", "deployment", "otb.rspec")

		tree = etree.parse(rspec_file)
		xml_root = tree.getroot()

		nucs = self._get_nucs()
		for nuc_id in nucs:
			xml_root.append(self._rspec_node(nuc_id))

		tree.write(rspec_file, xml_declaration=True, encoding='UTF-8', pretty_print=True)

	def _rspec_node(self, nuc_id):
		node = etree.Element(
			"node", 
			client_id="sensor{0}".format(nuc_id.split("-")[1]),
			exclusive="true",
			component_manager_id="urn:publicid:IDN+wilab1.ilabt.iminds.be+authority+cm",
			component_id="urn:publicid:IDN+wilab1.ilabt.iminds.be+node+{0}".format(nuc_id)
		)
		node.append(etree.Element("silver_type", name="raw-pc"))
		node.append(etree.Element("ansible_group", xmlns="http://jfed.iminds.be/rspec/ext/jfed/1", name="sensor"))
		
		return node

	def _get_nucs(self):
		config_file = os.path.join(self.SCENARIO_CONFIG, self.scenario, "_wilab_config.json")
		nucs = []

		with open(config_file, 'r') as f:
			config_obj = json.load(f)

			for generic_id in config_obj:
				testbed_id_split = config_obj[generic_id]["node_id"].split("-")
				nuc_id = testbed_id_split[0] + "-" + testbed_id_split[1]

				if nuc_id not in nucs:
					nucs.append(nuc_id)

		return nucs





TESTBEDS = {
	"iotlab": IoTLAB,
	"wilab": Wilab
}

def main():
	controller = Controller()

	args = controller.get_args()

	action   = args['action']
	testbed  = args['testbed']
	scenario = args['scenario']

	testbed  = TESTBEDS[testbed](scenario)
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

