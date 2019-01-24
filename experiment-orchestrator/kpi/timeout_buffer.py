import collections
import threading

class TimeoutBuffer():

	def __init__(self, timeout):
		self.timeout = timeout
		self.buffer  = collections.deque()
		self.lock    = threading.Lock()

	def _expire(self):
		with self.lock:
			self.buffer.popleft()

	def put(self, item):
		with self.lock:
			self.buffer.append(item)
			threading.Timer(self.timeout, self._expire).start()

	def find(self, packet_token):
		for item in self.buffer:
			if item['event_payload']['packetToken'] == packet_token:
				return item    # Item not deleted from the deque, since it will expire and be removed anyway
		return None