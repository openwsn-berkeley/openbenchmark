from socket_io_handler import SocketIoHandler
from exp_terminate import ExpTerminate

import time
import subprocess
import json
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

socketIoHandler = SocketIoHandler()

logDir = os.path.join(os.path.dirname(__file__), "..", "openvisualizer", "build", "runui")

class MyHandler(FileSystemEventHandler):

	def __init__(self):
		self.last_timestamp = 0.0
		self.unix_timestamp = time.time()
		self.SHUT_DOWN_TIME = 20 #Max time since the last data, indicating that the experiment is over
		self.check_timestamp()

	def on_modified(self, event):
		try:
			last_line = self.get_last_line(event.src_path)
			last_line_timestamp = float(json.loads(last_line)['_timestamp'])

			if last_line_timestamp > self.last_timestamp:
				#print("event type: " + str(event.event_type) + " path : " + str(event.src_path))
				socketIoHandler.publish('LOG_MODIFICATION', last_line)
				self.last_timestamp = last_line_timestamp
				self.unix_timestamp = time.time()

		except Exception, e:
			socketIoHandler.publish('LOG_MODIFICATION', str(e))


	def check_timestamp(self):
	    threading.Timer(5, self.check_timestamp).start() # called every minute
	    if time.time() - self.unix_timestamp > self.SHUT_DOWN_TIME:
	    	socketIoHandler.publish('EXP_TERMINATE', '')
	    	ExpTerminate().exp_terminate()

	def get_last_line(self, file_path):
		if os.path.isfile(file_path):
			return subprocess.check_output(['tail', '-1', file_path])
		else:
			return ""


class OVLogMonitor:

	def __init__(self):
		self.event_handler = MyHandler()
		self.observer = Observer()

	def start(self):
		self.observer.schedule(self.event_handler, path=logDir, recursive=False)
		self.observer.start()

		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			self.observer.stop()

		self.observer.join()



