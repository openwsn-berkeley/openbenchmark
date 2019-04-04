from socketIO_client_nexus import SocketIO

class SocketIoHandler:

	SOCKET_IO_URL = 'http://localhost'
	SOCKET_IO_PORT = 3000

	def __init__(self):
		self.socketIO = SocketIO(self.SOCKET_IO_URL, self.SOCKET_IO_PORT)

	def publish(self, topic, message):
		self.socketIO.emit(topic, message)