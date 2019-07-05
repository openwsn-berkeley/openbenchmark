import sys
sys.path.append("..")

import json
import paho.mqtt.client as mqtt
from utils import Utils
from _condition_object import ConditionObject


class MessageType:
	command         = "command"
	response        = "response"
	performanceData = "performanceData"


class MQTTClient:

	# MQTTClient is a singleton class to avoid creating an instance of MQTTClient for each node

	# Commands sent FROM the SUT: `Start Benchmark`
	# Commands sent TO the SUT: `Send Packet`, `Configure Transmit Power`
	# Commands sent in both directions: `Echo`

	_instance = None

	@staticmethod
	def create():
		if MQTTClient._instance == None:
			MQTTClient._instance = MQTTClient()
		return MQTTClient._instance


	def __init__(self):
		self.broker           = Utils.broker
		self.condition_object = ConditionObject.create()

		self.experiment_id    = Utils.experiment_id

		self.sub_topics = {
			"startBenchmark": "openbenchmark/command/startBenchmark",  # Subscribing on the command (receiving)
			"echo": "openbenchmark/experimentId/{0}/+/echo".format(self.experiment_id),   # Subscribing on both
			"sendPacket": "openbenchmark/experimentId/{0}/response/sendPacket".format(self.experiment_id),
			"configureTransmitPower": "openbenchmark/experimentId/{0}/response/configureTransmitPower".format(self.experiment_id),
			"triggerNetworkFormation": "openbenchmark/experimentId/{0}/response/triggerNetworkFormation".format(self.experiment_id)
		}
		self.pub_topics = {
			"startBenchmark": "openbenchmark/response/startBenchmark",  # Publishing on response (after receving)
			"echoCommand": "openbenchmark/experimentId/{0}/command/echo".format(self.experiment_id),   # Can publish on both
			"echoResponse": "openbenchmark/experimentId/{0}/response/echo".format(self.experiment_id), ###
			"sendPacket": "openbenchmark/experimentId/{0}/command/sendPacket".format(self.experiment_id),
			"configureTransmitPower": "openbenchmark/experimentId/{0}/command/configureTransmitPower".format(self.experiment_id),
			"triggerNetworkFormation": "openbenchmark/experimentId/{0}/command/triggerNetworkFormation".format(self.experiment_id),
			"notifications": "openbenchmark/{0}/notifications".format(Utils.user_id),
			"kpi": "openbenchmark/{0}/kpi".format(Utils.user_id),
			"raw": "openbenchmark/{0}/raw".format(Utils.user_id),
			"debug": "openbenchmark/{0}/debug".format(Utils.user_id)
		}
		self.epe_sub_topics = {  # Experiment Performance Events
			"performanceData": "openbenchmark/experimentId/{0}/nodeId/+/performanceData".format(self.experiment_id)
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
			sys.stdout.write("[MQTT CLIENT] Subscribing to: {0}\n".format(self.sub_topics[key]))
			self.client.subscribe(self.sub_topics[key])
		for key in self.epe_sub_topics:
			sys.stdout.write("[MQTT CLIENT] Subscribing to: {0}\n".format(self.epe_sub_topics[key]))
			self.client.subscribe(self.epe_sub_topics[key])

	def publish(self, topic, payload, custom=False):
		if not custom:
			self.client.publish(self.pub_topics[topic], json.dumps(payload))
		else:
			self.client.publish(topic, json.dumps(payload))


	##### MQTT client listeners #####
	def _on_connect(self, client, userdata, flags, rc):
		sys.stdout.write("[MQTT CLIENT] Connected to the broker. Subscribing...\n")
		self.subscribe()

	def _on_disconnect(self, client, userdata, rc):
		sys.stdout.write("[MQTT CLIENT] Disconnecting from the broker...\n")
		self.client.loop_stop()

	def _on_subscribe(self, client, obj, mid, granted_qos):
		self.successful_subs += 1
		if self.successful_subs == len(self.sub_topics) + len(self.epe_sub_topics):
			self.successful_subs = 0
			sys.stdout.write("[MQTT CLIENT] Subscribed to all\n")

			
	def _on_message(self, client, userdata, message):
		topic   = message.topic
		payload = message.payload.decode('string-escape').strip('"')

		topic_arr = topic.split("/")
		topic_arr_len = len(topic_arr)

		if topic_arr[topic_arr_len - 1] == MessageType.performanceData:   # It's an Experiment Performance Event
			self._on_performanceData(payload)
		else:
			if topic_arr[topic_arr_len - 2] == MessageType.command:   # It's a command
				message_key  = topic_arr[topic_arr_len - 1]
				message_type = MessageType.command
			elif topic_arr[topic_arr_len - 2] == MessageType.response:   # It's a response
				message_key  = topic_arr[topic_arr_len - 1]
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
			sys.stdout.write("[MQTT CLIENT] Exception: {0}\n".format(e))
			

	def _on_startBenchmark_command(self, payload):
		# Should start network preparation module
		payload_obj = json.loads(payload)

		self.publish('startBenchmark', {
		        "token"        : payload_obj['token'],
		        "success"      : True,
		        "experimentId" : self.experiment_id
			})

		self.condition_object.sut_command_payload = payload_obj
		
		self.condition_object.start_benchmark_cv.acquire()
		self.condition_object.start_benchmark_cv.notifyAll()
		self.condition_object.start_benchmark_cv.release()


	def _on_echo_response(self, payload):
		self.notify_api_response(payload)

	def _on_echo_command(self, payload):
		# Should send echo response
		pass

	def _on_sendPacket_response(self, payload):
		self.notify_api_response(payload)

	def _on_configureTransmitPower_response(self, payload):
		self.notify_api_response(payload)

	def _on_triggerNetworkFormation_response(self, payload):
		self.notify_api_response(payload)

	def _on_performanceData(self, payload):
		# Here we implement the logic for feeding the performance data into the KPI calculation module
		cv = self.condition_object.exp_event_cv
		queue = self.condition_object.exp_event_queue

		if cv != None:
			queue.put(json.loads(payload))
			cv.acquire()
			cv.notifyAll()
			cv.release()

	def push_notification(self, step_identifier, success):
		try:
			if step_identifier not in ['network-configured', 'orchestration-started']:
				raise Exception("Notification parameter not recognized")

			self.publish("notifications", {
					"type": "notification", 
					"content": {
						"step"   : step_identifier,
						"success": success
					}
				})

		except Exception, e:
			sys.stdout.write("[MQTT CLIENT] Message: {0}\n".format(e))

	def push_kpi(self, payload):
		self.publish("kpi", {
			"type": "kpi",
			"content": payload
		})

	def push_raw(self, payload):
		self.publish("raw", {
			"type": "raw",
			"content": payload
		})

	def push_debug_log(self, action, log_entry, console_print = True):
		self.publish("debug", {
			"action": action,
			"log_entry": log_entry
		})
		if console_print:
			print("{0} {1}".format(action, log_entry))