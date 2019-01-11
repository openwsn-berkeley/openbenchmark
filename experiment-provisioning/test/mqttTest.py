import paho.mqtt.client as mqtt
import time

class MQTTTest: 

	BROKER = 'broker.mqttdashboard.com'
	CLIENT = 'exp-auto-test'

	is_data_arriving  = False

	PAUSE  = 5

	def __init__(self, testbed):
		self.testbed 		   = testbed
		self.client  		   = mqtt.Client(self.CLIENT) 
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message

		self.client.connect(self.BROKER)
		self.client.loop_start()

	def on_connect(self, client, userdata, flags, rc):
		self.client.subscribe('{0}/deviceType/mote/deviceId/+/notif/frommoteserialbytes'.format(self.testbed))

	def on_message(self, client, userdata, message):
		self.is_data_arriving = True

	def check_data(self):
		time.sleep(self.PAUSE)
		self.client.loop_stop()
		self.client.disconnect()
		return self.is_data_arriving

