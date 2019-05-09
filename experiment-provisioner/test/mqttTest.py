import paho.mqtt.client as mqtt
import time

class MQTTTest: 

	BROKER = 'broker.mqttdashboard.com'
	CLIENT = 'exp-auto-test'

	def __init__(self, testbed, test_type):
		self.testbed 		   = testbed
		self.test_type         = test_type
		self.client  		   = mqtt.Client(self.CLIENT) 
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message

		self.pause = 30 if self.test_type == 'otbox-flash' else 360
		self.is_data_arriving = False

		self.client.connect(self.BROKER)
		self.client.loop_start()


	def on_connect(self, client, userdata, flags, rc):
		if self.test_type == 'otbox-flash':
			self.client.subscribe('{0}/deviceType/mote/deviceId/+/notif/frommoteserialbytes'.format(self.testbed))
		elif self.test_type == 'ov-start':
			self.client.subscribe('openbenchmark/experimentId/+/command/sendPacket')

	def on_message(self, client, userdata, message):
		self.is_data_arriving = True

	def check_data(self):
		time.sleep(self.pause)
		self.client.loop_stop()
		self.client.disconnect()
		return self.is_data_arriving