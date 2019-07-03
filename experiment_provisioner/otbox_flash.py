import paho.mqtt.client as mqtt
import base64
import json

from mqtt_client import MQTTClient

CLIENT = 'exp-auto'

class OTBoxFlash:

	def __init__(self, user_id, firmware_path, broker, testbed):
		self.firmware_path     = firmware_path
		self.broker            = broker
		self.testbed           = testbed

		self.mqtt_client       = MQTTClient.create(testbed, user_id)
		self.client            = mqtt.Client(CLIENT)
		self.client.on_connect = self.on_connect

	def on_connect(self, client, userdata, flags, rc):
		print "Connected to broker: {0}".format(self.broker)
		self.flash_firmware()
		self.client.disconnect()

	def flash_firmware(self):
		# {0}/deviceType/mote/deviceId/all/cmd/program

		try:
			with open(self.firmware_path) as f:
				data = f.read()
				payload = {
					'hex': base64.b64encode(data),
					'description': ''
				}

				print("Sending {0} firmware to motes".format(self.firmware_path))
				self.mqtt_client.push_debug_log('FW_FLASHING', "Sending {0} firmware to motes".format(self.firmware_path))
				self.client.publish('{0}/deviceType/mote/deviceId/all/cmd/program'.format(self.testbed), json.dumps(payload))
				self.mqtt_client.push_notification("flashed", True)

		except Exception, e:
			print("An exception occured: {0}".format(str(e)))
			self.mqtt_client.push_debug_log('FW_FLASHING_ERROR', str(e))
			self.mqtt_client.push_notification("flashed", False)

	def flash(self):
		self.client.connect(self.broker)
		self.client.loop_forever()