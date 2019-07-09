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

		self.pauses = {
			"reserve"  :   5,
			"flash"    :  50,
			"sut-start": 180 
		}

		self.pause = self.pauses[self.test_type] if self.test_type in self.pauses else 5
		self.is_data_arriving = False

		self.client.connect(self.BROKER)
		self.client.loop_start()


	def on_connect(self, client, userdata, flags, rc):
		if self.test_type in ['reserve', 'flash']:
			self.client.subscribe('{0}/deviceType/mote/deviceId/+/notif/frommoteserialbytes'.format(self.testbed))
			print "[TEST] flash subscribing..."
		elif self.test_type == 'sut-start':
			print "[TEST] sut-start subscribing..."
			self.client.subscribe('openbenchmark/command/startBenchmark')

	def on_message(self, client, userdata, message):
		self.is_data_arriving = True

	def check_data(self):
		print "[TEST] Waiting for the data: {0} seconds".format(self.pause)
		time.sleep(self.pause)
		self.client.loop_stop()
		self.client.disconnect()
		return self.is_data_arriving