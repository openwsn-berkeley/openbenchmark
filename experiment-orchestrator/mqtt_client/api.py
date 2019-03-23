import sys
import time
import json
import threading
import random
import string
import colorama
from mqtt_client import MQTTClient
from _condition_object import ConditionObject


class API:

	# The MQTT API request payload is assigned with a unique token, which should be returned in the response payload
	# The purpose of the token is to properly match responses with their respective requests

	def __init__(self, timeout):
		self.mqtt_client      = MQTTClient.create()
		self.condition_object = ConditionObject.create()
		self.timeout          = timeout

	def _wait(self, token):
		self.condition_object.append_variable(token=token)
		
		cv = self.condition_object.condition_variables[token]['condition_var']
		cv.acquire()
		cv.wait(self.timeout)
		cv.release()

		payload = self.condition_object.condition_variables[token]['payload']
		self.condition_object.remove_variable(token=token)

		if payload != '':
			sys.stdout.write("{0}[API] {1}\n{2}".format(
				colorama.Fore.GREEN if json.loads(payload)['success'] else colorama.Fore.RED, 
				payload, 
				colorama.Style.RESET_ALL
			))
		else:
			payload = json.dumps({
				"token"  : token,
				"success": False,
				"reason" : "timeout"
			})
			sys.stdout.write("{0}[API] {1}\n{2}".format(
				colorama.Fore.RED,
				payload, 
				colorama.Style.RESET_ALL
			))
		
		return payload


	##### API implementation #####
	def _assign_token(self, payload):
		token = ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(4)])
		payload['token']       = token
		payload['packetToken'] = [0] + [int(elem.encode("hex"), 16) for elem in token]
		return payload

	def command_exec(self, command, payload, blocking):
		if blocking: 
			return self._publish_command(payload, command)

		threading.Thread(target=self._publish_command, args=[payload, command]).start()
		return ''

	def _publish_command(self, payload, command):
		# Publishes MQTT command and puts thread into waiting state until notified or timeout
		payload = self._assign_token(payload)
		self.mqtt_client.publish(
			command,
			payload
		)
		return self._wait(payload['token'])