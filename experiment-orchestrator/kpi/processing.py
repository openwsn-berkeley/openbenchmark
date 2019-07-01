import sys
sys.path.append('..')

import time
import json
import threading
from logger import Logger
from utils import Utils
from timeout_buffer import TimeoutBuffer
from mqtt_client._condition_object import ConditionObject
from scenarios.scenario import Scenario


class KPIProcessing:

	def __init__(self):
		# Temporarily hardcoded
		self.logger           = Logger.create({
				'date'         : Utils.date,
				'experiment_id': Utils.experiment_id,
				'testbed'      : Utils.testbed,
				'firmware'     : Utils.firmware,
				'nodes'        : Utils.id_to_eui64,
				'scenario'     : Utils.scenario.SCENARIO_IDENTIFIER
			})

		self.condition_object = ConditionObject.create()
		self.cv               = self.condition_object.exp_event_cv
		self.cv_packet_drop   = self.condition_object.packet_drop_cv
		self.queue            = self.condition_object.exp_event_queue
		self.queue_pck_drop   = self.condition_object.packet_drop_queue

		# Buffer_1 - for buffering `packetSent` events
		# Buffer_2 - for buffering `packetReceived` events
		# Buffer_2 does not expire because packetReceived events should get their packetSent events eventually
		self.buffer_1         = TimeoutBuffer(timeout=60, expire=True)   # in seconds
		self.buffer_2         = TimeoutBuffer(timeout=60, expire=False)  # in seconds

		self.packet_memory    = {'sent': {}, 'dropped': {}}   # { "sent": {"node_id": {"dest_node_id": `Int`}, "dropped": {...} }

		self.event_to_method  = {
			"packetSent"               : self._packet_sent,
			"packetReceived"           : self._packet_received,
			"networkFormationCompleted": self._networkFormationTime,
			"synchronizationCompleted" : self._synchronizationPhase,
			"secureJoinCompleted"      : self._secureJoinPhase,
			"bandwidthAssigned"        : self._bandwidthAssignment,
			"radioDutyCycleMeasurement": self._radioDutyCycle,
			"clockDriftMeasurement"    : None
		}


	def start(self):   # Should be started upon startBenchmark command
		threading.Thread(target=self._epe_monitor).start()
		threading.Thread(target=self._packet_drop_event).start()


	def _epe_monitor(self):
		while True:
			if self.queue.empty():
				self.cv.acquire()
				self.cv.wait()     # Released when the queue has a new item
				self.cv.release()

			payload = self.queue.get()
			self._process_event(payload)

	def _packet_drop_event(self):
		while True:
			if self.queue_pck_drop.empty():
				self.cv_packet_drop.acquire()
				self.cv_packet_drop.wait()     # Released when the queue has a new item
				self.cv_packet_drop.release()

			payload = self.queue_pck_drop.get()
			self._increment('dropped', payload['node_id'], payload['dest_node_id'])

			self._log_reliability(payload)


	def _process_event(self, payload):
		# Should implement logic for event payload processing and updating log file
		if payload['event'] in ["packetSent", "packetReceived"]:
			payload['node_id'] = Utils.eui64_to_id[payload['source']]
			payload['dest_node_id'] = Utils.eui64_to_id[payload['destination']]

		self.logger.log('raw', payload)
		self._kpi_calculate(payload)

	def _increment(self, inc_type, node_id, dest_node_id):
		if node_id not in self.packet_memory[inc_type]:
			self.packet_memory[inc_type][node_id] = {
				dest_node_id: 0
			}
		self.packet_memory[inc_type][node_id][dest_node_id] += 1

	def _get_num(self, num_type, node_id, dest_node_id):
		if node_id in self.packet_memory[num_type] and dest_node_id in self.packet_memory[num_type][node_id]:
			return self.packet_memory[num_type][node_id][dest_node_id]
		return 0


	# Methods for calculating KPI
	def _kpi_calculate(self, payload):
		self.event_to_method[payload['event']](payload)

	def _log_latency(self, payload, origin_packet):
		# Log latency only if packet received before timeout
		if origin_packet != None:
			latency = abs(payload['timestamp'] - origin_packet['timestamp'])
			
			self.logger.log('kpi', {
					'kpi'         : 'latency',
					'eui64'       : payload['source'],
					'node_id'     : payload['node_id'],
					'dest_eui64'  : payload['destination'],
					'dest_node_id': payload['dest_node_id'],
					'timestamp'   : payload['timestamp'],
					'value'       : round(latency, 2)
				})

	def _log_reliability(self, payload):
		num_of_sent    = self._get_num('sent', payload['node_id'], payload['dest_node_id'])
		num_of_dropped = self._get_num('dropped', payload['node_id'], payload['dest_node_id'])

		if num_of_sent > 0:    # Preventing division by zero
			self.logger.log('kpi', {
					'kpi'         : 'reliability',
					'eui64'       : payload['source'],
					'node_id'     : payload['node_id'],
					'dest_eui64'  : payload['destination'],
					'dest_node_id': payload['dest_node_id'],
					'timestamp'   : payload['timestamp'],
					'value'       : round(1 - float(num_of_dropped) / float(num_of_sent), 2)
				})


	def _packet_sent(self, payload):
		# Check buffer_2 and calculate KPI if present. Otherwise, put in buffer_1
		origin_packet = self.buffer_2.find(payload['packetToken'])
		
		if origin_packet != None:
			self._log_latency(payload, origin_packet)
			self._log_reliability(payload)
		else:	
			self.buffer_1.put(payload)
			self._increment('sent', payload['node_id'], payload['dest_node_id'])

	def _packet_received(self, payload):
		# Check buffer_1 and calculate KPI if present. Otherwise, put in buffer_2
		origin_packet = self.buffer_1.find(payload['packetToken'])

		if origin_packet != None:
			self._log_latency(payload, origin_packet)
			self._log_reliability(payload)
		else:
			self.buffer_2.put(payload)
			
	def _networkFormationTime(self, event_obj):
		print str(event_obj)
		self.logger.log('kpi', {
				'kpi'      : 'networkFormationTime',
				'timestamp': event_obj['timestamp'],
				'value'    : 1
			})

	def _synchronizationPhase(self, event_obj):
		self.logger.log('kpi', {
				'kpi'      : 'syncronizationPhase',
				'timestamp': event_obj['timestamp'],
				'value'    : 1
			})

	def _secureJoinPhase(self, event_obj):
		self.logger.log('kpi', {
				'kpi'      : 'secureJoinPhase',
				'timestamp': event_obj['timestamp'],
				'value'    : 1
			})

	def _bandwidthAssignment(self, event_obj):
		self.logger.log('kpi', {
				'kpi'      : 'bandwidthAssignment',
				'node_id'  : Utils.eui64_to_id[event_obj['source']],
				'eui64'    : event_obj['source'],
				'timestamp': event_obj['timestamp'],
				'value'    : 1
			})

	def _radioDutyCycle(self, event_obj):
		self.logger.log('kpi', {
				'kpi'      : 'radioDutyCycle',
				'eui64'    : event_obj['source'],
				'node_id'  : Utils.eui64_to_id[event_obj['source']],
				'timestamp': event_obj['timestamp'],
				'value'    : float(event_obj['dutyCycle'].strip('%'))
			}) 