import os
import base64
import json
import time

from mqtt_client import MQTTClient

CLIENT = 'exp-auto'

class OTBoxFlash:

	def __init__(self, user_id, firmware, testbed):
		self.firmware_path     = os.path.join(os.path.dirname(__file__), 'firmware', firmware)
		self.testbed           = testbed

		self.mqtt_client       = MQTTClient.create(testbed, user_id)

		self.time_padding      = 10  # [s]

	def flash(self):
		# {0}/deviceType/mote/deviceId/all/cmd/program
		if self.testbed != 'opensim':
			try:
				with open(self.firmware_path) as f:
					data = f.read()
					payload = {
						'hex': base64.b64encode(data),
						'description': ''
					}

					print("Sending {0} firmware to motes".format(self.firmware_path))
					self.mqtt_client.push_debug_log('FW_FLASHING', "Sending {0} firmware to motes".format(self.firmware_path))
					self.mqtt_client.flash(payload)

					print("[FW_FLASHING] Waiting {0} seconds...".format(self.time_padding))
					self.mqtt_client.push_debug_log('FW_FLASHING', "Waiting {0} seconds...".format(self.time_padding))
					time.sleep(self.time_padding)

					self.mqtt_client.push_notification("flashed", True)

			except Exception, e:
				print("An exception occured: {0}".format(str(e)))
				self.mqtt_client.push_debug_log('FW_FLASHING_ERROR', str(e))
				self.mqtt_client.push_notification("flashed", False)

		else:
			self.mqtt_client.push_notification("flashed", True)