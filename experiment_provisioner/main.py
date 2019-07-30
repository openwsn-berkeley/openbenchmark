import ConfigParser
import os
import base64
import json
import yaml
import string
import random
import subprocess
import atexit

from lxml import etree
from abc import abstractmethod
from reservation import IoTLABReservation
from reservation import WilabReservation
from reservation import OpenSimReservation

from otbox_flash import OTBoxFlash
from sut_startup import SUTStartup
from fw_compiler import FWCompiler

from mqtt_client import MQTTClient


class Controller(object):

	CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "conf.txt")
	SCENARIO_CONFIG = os.path.join(os.path.dirname(__file__), "..", "scenario-config")
	DEFAULT_FIRMWARE = '03oos_openwsn_prog'

	def __init__(self):
		self.configParser = ConfigParser.RawConfigParser()   
		self.configParser.read(self.CONFIG_FILE)

		self.OV_REPO     = self.configParser.get('dependencies', 'ov-repo')
		self.OV_BRANCH   = self.configParser.get('dependencies', 'ov-branch')
		self.COAP_REPO   = self.configParser.get('dependencies', 'coap-repo')
		self.COAP_BRANCH = self.configParser.get('dependencies', 'coap-branch')
		self.OTB_REPO    = self.configParser.get('dependencies', 'otb-repo')
		self.OTB_TAG     = self.configParser.get('dependencies', 'otb-tag')

	def _get_duration(self, scenario):
		config_file = os.path.join(self.SCENARIO_CONFIG, scenario, "_config.json")
		duration_min = -1

		with open(config_file, 'r') as f:
			config_obj = json.load(f)
			duration_min = config_obj['duration_min']

		return duration_min

	def print_log(self, message):
		self.mqtt_client.push_debug_log("[PROVISIONER]", message)
		print("[PROVISIONER] {0}".format(message))

	@abstractmethod
	def add_files_from_env(self):
		pass



class IoTLAB(Controller):

	def __init__(self, user_id, scenario, action):
		super(IoTLAB, self).__init__()

		self.CONFIG_SECTION = 'iotlab'
		self.scenario = scenario

		self.USERNAME = os.environ["user"] if "user" in os.environ else self.configParser.get(self.CONFIG_SECTION, 'user')
		self.PRIVATE_SSH = os.environ["private_ssh"] if "private_ssh" in os.environ else ""
		self.HOSTNAME = 'saclay.iot-lab.info'

		self.NODES = self._get_nodes()
		self.EXP_DURATION = self._get_duration(self.scenario) + 10

		self.add_files_from_env()
		self.reservation = IoTLABReservation(user_id, self.USERNAME, self.HOSTNAME, self.OTB_REPO, self.OTB_TAG, self.EXP_DURATION, self.NODES)

		self.mqtt_client = MQTTClient.create('iotlab', user_id)
		atexit.register(self._stop_mqtt)

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

	def _stop_mqtt(self):
		self.mqtt_client.clear_state()



class Wilab(Controller):

	def __init__(self, user_id, scenario, action):
		super(Wilab, self).__init__()

		self.mqtt_client = MQTTClient.create('wilab', user_id)

		self.CONFIG_SECTION = 'wilab'
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
		self.DELETE   = 'stop_experiment.sh'   # Script for terminating the experiment
		self.RUN      = 'start_experiment.sh'  # Script for starting the experiment
		self.DISPLAY  = 'start_display.sh'     # Script for starting a fake display

		self.PASSWORD = self.configParser.get(self.CONFIG_SECTION, 'password')

		self.EXP_DURATION = self._get_duration(self.scenario) + 10

		self._rspec_update()
		self._set_broker()

		if action == 'reserve':
			self._update_yml_files()

		self.reservation = WilabReservation(user_id, self.JFED_DIR, self.RUN, self.DELETE, self.DISPLAY)
		atexit.register(self._stop_mqtt)

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
		sensor_id = 1

		parser = etree.XMLParser(remove_blank_text=True)
		tree = etree.parse(rspec_file, parser)
		xml_root = tree.getroot()

		for child in list(xml_root):
			xml_root.remove(child)

		xml_root.append(self._rspec_server())

		nucs = self._get_nucs()
		for nuc_id in nucs:
			xml_root.append(self._rspec_node(sensor_id, nuc_id))
			sensor_id += 1

		tree.write(rspec_file, xml_declaration=True, pretty_print=True)

	def _rspec_server(self):
		server_node = etree.Element(
			"node", 
			client_id="server",
			exclusive="true",
			component_manager_id="urn:publicid:IDN+wall2.ilabt.iminds.be+authority+cm"
		)

		sliver_type_node = etree.Element("sliver_type", name="raw-pc")
		sliver_type_node.append(etree.Element("disk_image", name="urn:publicid:IDN+wall2.ilabt.iminds.be+image+emulab-ops:UBUNTU18-64-STD"))

		server_node.append(sliver_type_node)
		server_node.append(etree.Element("location", xmlns="http://jfed.iminds.be/rspec/ext/jfed/1", x="213.0", y="155.0"))
		server_node.append(etree.Element("ansible_group", xmlns="http://jfed.iminds.be/rspec/ext/jfed/1", name="server"))
		
		return server_node

	def _rspec_node(self, sensor_id, nuc_id):
		node = etree.Element(
			"node", 
			client_id="{0}".format(nuc_id),
			exclusive="true",
			component_manager_id="urn:publicid:IDN+wilab1.ilabt.iminds.be+authority+cm",
			component_id="urn:publicid:IDN+wilab1.ilabt.iminds.be+node+{0}".format(nuc_id)
		)
		node.append(etree.Element("sliver_type", name="raw-pc"))
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

	def _set_broker(self):
		otbox_conf_file = os.path.join(self.JFED_DIR, "opentestbed", "deployment", "sensor", "sensor-supervisord.conf.j2")
		content = "[program:otbox]\ncommand     = /usr/local/bin/opentestbed -v\nenvironment = OTB_TESTBED='wilab', OTB_BROKER='{0}'\nautostart   = true\nautorestart = true\ndirectory = /tmp".format(self.mqtt_client.broker)

		with open(otbox_conf_file, 'w') as f:
			f.write(content)

	def _update_yml_files(self):
		start_exp_yml_temp = os.path.join(self.JFED_DIR, "start_experiment_temp.yml")
		stop_exp_yml_temp  = os.path.join(self.JFED_DIR, "stop_experiment_temp.yml")
		start_exp_yml      = os.path.join(self.JFED_DIR, "start_experiment.yml")
		stop_exp_yml       = os.path.join(self.JFED_DIR, "stop_experiment.yml")

		slice_name = "bench{0}".format(self._get_random_string())
		yml_conf = None

		with open(start_exp_yml_temp, 'r') as f:
			yml_conf = yaml.load(f, Loader=yaml.FullLoader)
			yml_conf['experiment']['slice']['sliceName'] = slice_name
			yml_conf['experiment']['slice']['expireTimeMin'] = 30
			yml_conf['user']['password'] = self.PASSWORD

		with open(start_exp_yml, 'w') as f:
			yaml.dump(yml_conf, f)

		with open(stop_exp_yml_temp, 'r') as f:
			yml_conf = yaml.load(f, Loader=yaml.FullLoader)
			yml_conf['slice']['sliceName'] = slice_name
			yml_conf['user']['password'] = self.PASSWORD

		with open(stop_exp_yml, 'w') as f:
			yaml.dump(yml_conf, f)

		subprocess.call('dos2unix *.yml', cwd=self.JFED_DIR, shell=True)
		subprocess.call('dos2unix *.sh', cwd=self.JFED_DIR, shell=True)		


	def _get_random_string(self, string_length = 5):
		letters = string.ascii_uppercase
		return ''.join(random.choice(letters) for i in range(string_length))

	def _stop_mqtt(self):
		self.mqtt_client.clear_state()



class OpenSim(Controller):
	def __init__(self, user_id, scenario, action):
		super(OpenSim, self).__init__()

		self.testbed = "opensim"
		self.user_id = user_id

		self.mqtt_client = MQTTClient.create(self.testbed, user_id)
		self.reservation = OpenSimReservation(user_id)

		atexit.register(self._stop_mqtt)

	
	def _stop_mqtt(self):
		self.mqtt_client.clear_state()



TESTBEDS = {
	"iotlab": IoTLAB,
	"wilab": Wilab,
	"opensim": OpenSim
}


def compileFW(controller, user_id, testbed, firmware, branch):
	# Default firmware is "openwsn" with testbed name suffix
	if testbed != 'opensim':
		if firmware is None:
			return controller.DEFAULT_FIRMWARE + '_' + testbed + '.ihex'
		elif branch is not None:
			return FWCompiler(testbed, user_id, firmware, branch).compile()
		else:
			return firmware
	else:
		if firmware is None:
			return FWCompiler(testbed, user_id).compile()
		else:
			return FWCompiler(testbed, user_id, firmware, branch).compile()

class Main():

	def __init__(self, user_id, simulator, action, testbed, scenario, firmware, branch):
		controller = Controller()

		testbedCtl  = TESTBEDS[testbed](user_id, scenario, action)

		if action == 'reserve':
			testbedCtl.print_log('Reserving nodes...')
			testbedCtl.reservation.reserve_experiment()

		elif action == 'check':
			testbedCtl.print_log('Experiment checking...')
			testbedCtl.reservation.check_experiment()

		elif action == 'terminate':
			testbedCtl.print_log('Terminating the experiment...')
			testbedCtl.reservation.terminate_experiment()

		elif action == 'flash':
			firmware = compileFW(controller, user_id, testbed, firmware, branch)

			assert firmware is not None

			if firmware != '':
				testbedCtl.print_log('Flashing firmware: {0}'.format(firmware))

			OTBoxFlash(user_id, firmware, testbed).flash()

		elif action == 'sut-start' or action == 'orchestrator' or action == 'ov':
			testbedCtl.print_log('Starting SUT...')
			SUTStartup(
				user_id, 
				scenario, 
				testbed, 
				simulator,
				action == 'orchestrator',
				action == 'ov', 
				testbedCtl.OV_REPO, 
				testbedCtl.OV_BRANCH, 
				testbedCtl.COAP_REPO,
				testbedCtl.COAP_BRANCH
			).start()