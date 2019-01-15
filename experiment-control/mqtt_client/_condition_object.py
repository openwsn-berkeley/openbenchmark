import threading
import Queue

class ConditionObject:

	_instance = None

	@staticmethod
	def _create():
		if ConditionObject._instance == None:
			ConditionObject._instance = ConditionObject()
		return ConditionObject._instance
		

	def __init__(self):
		self.condition_variables = {}

		# Needed for Experiment Performance Events monitoring
		self.exp_event_cv = threading.Condition()
		self.exp_event_queue = Queue.Queue()

	def append_variable(self, token, payload=''):
		self.condition_variables[token] = {
			'condition_var': threading.Condition(),
			'payload': payload
		}

	def remove_variable(self, token):
		self.condition_variables.pop(token, None)