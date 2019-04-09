import sys

import json
import paho.mqtt.client as mqtt


class MQTTClient:

	_instance = None

	@staticmethod
	def create():
		if MQTTClient._instance == None:
			MQTTClient._instance = MQTTClient()
		return MQTTClient._instance


	def __init__(self):
		self.broker           = 'broker.mqttdashboard.com' # Utils.broker
		self.condition_object = ConditionObject.create()

		self.experiment_id    = 'Notif'

		self.sub_topics = {}
		self.pub_topics = {
			"notifications": "openbenchmark/notifications"
		}

		self._mqtt_client_setup()


	##### MQTT client setup #####
	def _mqtt_client_setup(self):
		self._mqtt_client_configure()
		self.client.connect(self.broker)
		self.client.loop_start()

	def _mqtt_client_configure(self):
		self.client               = mqtt.Client("OpenBenchmark{0}".format(self.experiment_id))
		self.client.on_connect    = self._on_connect
		self.client.on_disconnect = self._on_disconnect
		self.client.on_subscribe  = self._on_subscribe
		self.client.on_message    = self._on_message
		self.successful_subs      = 0
		

	def _subscribe(self):
		for key in self.sub_topics:
			sys.stdout.write("[PROV MQTT CLIENT] Subscribing to: {0}\n".format(self.sub_topics[key]))
			self.client.subscribe(self.sub_topics[key])
		for key in self.epe_sub_topics:
			sys.stdout.write("[PROV MQTT CLIENT] Subscribing to: {0}\n".format(self.epe_sub_topics[key]))
			self.client.subscribe(self.epe_sub_topics[key])

	def _publish(self, topic, payload, custom=False):
		if not custom:
			self.client.publish(self.pub_topics[topic], json.dumps(payload))
		else:
			self.client.publish(topic, json.dumps(payload))


	##### MQTT client listeners #####
	def _on_connect(self, client, userdata, flags, rc):
		sys.stdout.write("[PROV MQTT CLIENT] Connected to the broker. Subscribing...\n")
		self._subscribe()

	def _on_disconnect(self, client, userdata, rc):
		sys.stdout.write("[PROV MQTT CLIENT] Disconnecting from the broker...\n")
		self.client.loop_stop()

	def _on_subscribe(self, client, obj, mid, granted_qos):
		self.successful_subs += 1
		if self.successful_subs == len(self.sub_topics) + len(self.epe_sub_topics):
			self.successful_subs = 0
			sys.stdout.write("[PROV MQTT CLIENT] Subscribed to all\n")
			
	def _on_message(self, client, userdata, message):
		topic   = message.topic
		payload = message.payload.decode('string-escape').strip('"')

		sys.stdout.write("[PROV MQTT CLIENT] Topic: {0}\nMessage: {1}\n".format(topic, payload))


	##### Public methodss #####
	def push_notification(self, step_identifier, success):
		self._publish(
			"notifications",
			{
				"step"   : step_identifier,
				"success": success
			}
		)