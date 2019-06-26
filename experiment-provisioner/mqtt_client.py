import sys

import json
import time
import paho.mqtt.client as mqtt


class MQTTClient:

	_instance = None

	@staticmethod
	def create(testbed, user_id):
		if MQTTClient._instance == None:
			MQTTClient._instance = MQTTClient(testbed, user_id)
		return MQTTClient._instance


	def __init__(self, testbed, user_id):
		self.user_id          = user_id
		self.testbed          = testbed
		self.broker           = 'broker.mqttdashboard.com' # Utils.broker

		self.experiment_id    = 'Notif'

		self.sub_topics = {
			"data-stream": "{0}/deviceType/mote/deviceId/+/notif/frommoteserialbytes".format(self.testbed)
		}
		self.pub_topics = {
			"notifications": "openbenchmark/{0}/notifications".format(self.user_id),
			"debug": "openbenchmark/{0}/debug".format(self.user_id)
		}

		self.data_stream_started = False

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

		# sys.stdout.write("[PROV MQTT CLIENT] Message on topic: {0}".format(topic))

		# Setting to `true` without checking any conditions because `data-stream` is the only subscription topic
		self.data_stream_started = True


	##### Public methodss #####
	def push_notification(self, step_identifier, success):
		try:
			if step_identifier not in ['provisioned', 'flashed', 'data-stream-started', 'terminated']:
				raise Exception("Notification parameter not recognized")

			self._publish("notifications", {
					"type": "notification", 
					"content": {
						"step"   : step_identifier,
						"success": success
					}
				})

		except Exception, e:
			sys.stdout.write("[PROV MQTT CLIENT] Message: {0}\n".format(e))

	def check_data_stream(self):
		self.data_stream_started = False
		current_iter        = 0
		max_iter_num        = 15
		iter_pause          = 5   # in seconds
		
		while current_iter < max_iter_num:
			if not self.data_stream_started:
				current_iter += 1
				self.push_debug_log("PROV_MQTT_CLIENT", "Waiting for data stream {0}/{1}".format(current_iter, max_iter_num))
				time.sleep(iter_pause)
			else:
				break

		self.push_debug_log("PROV_MQTT_CLIENT", "Data stream started" if self.data_stream_started else "Data stream failed to start")
		self.push_notification("data-stream-started", self.data_stream_started)
		return self.data_stream_started


	def push_debug_log(self, action, log_entry):
		self._publish("debug", {
				"action": action,
				"log_entry": log_entry
			})