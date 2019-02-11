import threading
import Queue

class ConditionObject:

	_instance = None

	@staticmethod
	def create():
		if ConditionObject._instance == None:
			ConditionObject._instance = ConditionObject()
		return ConditionObject._instance
		

	def __init__(self):
		self.condition_variables = {}

		# Needed for Experiment Performance Events monitoring
		self.exp_event_cv = threading.Condition()
		self.exp_event_queue = Queue.Queue()

		# Needed for packet drop notification
		self.packet_drop_cv = threading.Condition()
		self.packet_drop_queue = Queue.Queue()

		# Needed for start benchmark notification
		self.start_benchmark_cv = threading.Condition()
		self.sut_command_payload = {}

	def append_variable(self, token):
		self.condition_variables[token] = {
			'condition_var': threading.Condition(),
			'payload': ''
		}

	def remove_variable(self, token):
		self.condition_variables.pop(token, None)