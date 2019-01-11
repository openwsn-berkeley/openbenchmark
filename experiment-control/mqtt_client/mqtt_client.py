import sys
import json
from _condition_object import ConditionObject
import paho.mqtt.client as mqtt


class MessageType:
	command  = "command"
	response = "response"


class MQTTClient:

	# MQTTClient is a singleton class to avoid creating an instance of MQTTClient for each node

	# Commands sent FROM the SUT: `Start Benchmark`
	# Commands sent TO the SUT: `Send Packet`, `Configure Transmit Power`
	# Commands sent in both directions: `Echo`

	_instance = None

	@staticmethod
	def _create(exp_id):
		if MQTTClient._instance == None:
			MQTTClient._instance = MQTTClient(experiment_id=exp_id)
		return MQTTClient._instance


	def __init__(self, experiment_id, broker="broker.mqttdashboard.com"):
		self.experiment_id    = experiment_id
		self.broker           = broker
		self.condition_object = ConditionObject._create()

		self.sub_topics = {
			"startBenchmark": "openbenchmark/command/startBenchmark",  # Subscribing on the command (receiving)
			"echo": "openbenchmark/experimentId/{0}/+/echo".format(self.experiment_id),   # Subscribing on both
			"sendPacket": "openbenchmark/experimentId/{0}/response/sendPacket".format(self.experiment_id),
			"configureTransmitPower": "openbenchmark/experimentId/{0}/response/configureTransmitPower".format(self.experiment_id)
		}
		self.pub_topics = {
			"startBenchmark": "openbenchmark/response/startBenchmark",  # Publishing on response (after receving)
			"echoCommand": "openbenchmark/experimentId/{0}/command/echo".format(self.experiment_id),   # Can publish on both
			"echoResponse": "openbenchmark/experimentId/{0}/response/echo".format(self.experiment_id), ###
			"sendPacket": "openbenchmark/experimentId/{0}/command/sendPacket".format(self.experiment_id),
			"configureTransmitPower": "openbenchmark/experimentId/{0}/command/configureTransmitPower".format(self.experiment_id)
		}

		self.mqtt_client_setup()


	##### MQTT client setup #####
	def mqtt_client_setup(self):
		self.mqtt_client_configure()
		self.client.connect(self.broker)
		self.client.loop_start()

	def mqtt_client_configure(self):
		self.client               = mqtt.Client("OpenBenchmark{0}".format(self.experiment_id))
		self.client.on_connect    = self._on_connect
		self.client.on_disconnect = self._on_disconnect
		self.client.on_subscribe  = self._on_subscribe
		self.client.on_message    = self._on_message
		self.successful_subs      = 0
		

	def subscribe(self):
		for key in self.sub_topics:
			print "Subscribing to: {0}".format(self.sub_topics[key])
			self.client.subscribe(self.sub_topics[key])

	def publish(self, topic, payload):
		self.client.publish(self.pub_topics[topic], json.dumps(payload))


	##### MQTT client listeners #####
	def _on_connect(self, client, userdata, flags, rc):
		print("Connected to the broker. Subscribing...")
		self.subscribe()

	def _on_disconnect(self, client, userdata, rc):
		print("Disconnecting from the broker...")
		self.client.loop_stop()

	def _on_subscribe(self, client, obj, mid, granted_qos):
		self.successful_subs += 1
		if self.successful_subs == len(self.sub_topics):
			self.successful_subs = 0
			print("Subscribed to all")

	def _on_message(self, client, userdata, message):
		topic   = message.topic
		payload = message.payload

		topic_arr = topic.split("response/")
		if len(topic_arr) == 1:   # It's a command
			message_key  = topic.split("command/")[0]
			message_type = MessageType.command
		else:   # It's a response
			message_key  = topic_arr[1]
			message_type = MessageType.response

		getattr(self, "_on_{0}_{1}".format(message_key, message_type))(payload)


	##### API callbacks #####
	# Every command should have its unique token so that requests and responses could match
	def notify_api_response(self, payload):
		try:
			payload_json = json.loads(payload)
			self.condition_object.condition_variables[str(payload_json['token'])]['payload'] = payload
			cv = self.condition_object.condition_variables[str(payload_json['token'])]['condition_var']
			cv.acquire()
			cv.notifyAll()
			cv.release()
		except Exception, e:
			print e

	def _on_startBenchmark_command(self, payload):
		# Should start scheduler and send startBenchmark response
		pass

	def _on_echo_response(self, payload):
		self.notify_api_response(payload)

	def _on_echo_command(self, payload):
		# Should send echo response
		pass

	def _on_sendPacket_response(self, payload):
		self.notify_api_response(payload)

	def _on_configureTransmitPower_response(self, payload):
		self.notify_api_response(payload)