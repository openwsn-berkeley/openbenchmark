import time
import json
import threading
from mqtt_client import MQTTClient
from _condition_object import ConditionObject


class API:

	# The MQTT API request payload is assigned with a unique token, which should be returned in the response payload
	# The purpose of the token is to properly match responses with their respective requests

	def __init__(self, timeout):
		self.mqtt_client      = MQTTClient._create(1)
		self.condition_object = ConditionObject._create()
		self.token            = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(15))   # Token generated automatically as a string of 15 random alphanumerical characters
		self.timeout          = timeout

	def _wait(self):
		self.condition_object.append_variable(token=self.token)
		
		cv = self.condition_object.condition_variables[self.token]['condition_var']
		cv.acquire()
		cv.wait(self.timeout)
		cv.release()

		payload = self.condition_object.condition_variables[self.token]['payload']
		self.condition_object.remove_variable(token=self.token)

		if payload != '':
			return payload

		return json.dumps({
			"token"  : self.token,
			"success": False,
			"reason" : "timeout"
		})



	##### API implementation #####
	def _assign_token(self, payload):
		payload['token'] = self.token
		return payload

	def command_exec(self, command, payload):
		threading.Thread(target=getattr(self, command), args=(payload, )).start()

	def echo(self, payload):
		# Should publish MQTT command and put thread into waiting state until notified or timeout
		pass


	def send_packet(self, payload):
		# Publishes MQTT command and puts thread into waiting state until notified or timeout
		self.mqtt_client.publish(
			'sendPacket',
			self._assign_token(payload)
		)
		
		return self._wait()


	def configure_transmit_power(self, payload):
		# Should publish MQTT command and put thread into waiting state until notified or timeout
		pass