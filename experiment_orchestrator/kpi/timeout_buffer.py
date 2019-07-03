import sys
sys.path.append('..')

import collections
import threading
import colorama
from mqtt_client._condition_object import ConditionObject

class TimeoutBuffer():

	def __init__(self, timeout, expire=True):
		self.timeout  = timeout
		self.buffer   = {}
		self.lock     = threading.Lock()
		self.expire   = expire

		self.condition_object = ConditionObject.create()
		self.cv_packet_drop   = self.condition_object.packet_drop_cv
		self.queue_pck_drop   = self.condition_object.packet_drop_queue

	def _expire(self, packet_token):
		token = ''.join(str(elem) for elem in packet_token)
		with self.lock:
			if self.buffer[token] != None:
				self.queue_pck_drop.put(self.buffer[token])
				self.buffer[token] = None

				sys.stdout.write("{0}[TIMEOUT BUFFER] {1}\n{2}".format(
					colorama.Fore.RED, 
					"Packet timeout: {0}".format(packet_token), 
					colorama.Style.RESET_ALL
				))

				self.cv_packet_drop.acquire()
				self.cv_packet_drop.notifyAll()
				self.cv_packet_drop.release()


	def put(self, item):
		with self.lock:
			token = ''.join(str(elem) for elem in item['packetToken'])
			self.buffer[token] = item
			if self.expire:
				threading.Timer(self.timeout, self._expire, [token]).start()

	def find(self, packet_token):
		token = ''.join(str(elem) for elem in packet_token)
		if token != '' and token in self.buffer and self.buffer[token] != None:
			packet = self.buffer[token]
			self.buffer[token] = None
			return packet
		return None