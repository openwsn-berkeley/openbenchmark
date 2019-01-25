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
				'date'         : '25. 1. 2019',
				'experiment_id': '1',
				'testbed'      : 'IoT-LAB',
				'firmware'     : '03oos_openwsn_prog',
				'nodes'        : ['a8-100', 'a8-101', 'a8-102', 'a8-103'],
				'scenario'     : 'Home Automation'
			})

		self.condition_object = ConditionObject.create()
		self.cv               = self.condition_object.exp_event_cv
		self.queue            = self.condition_object.exp_event_queue

		self.buffer           = TimeoutBuffer(timeout=120)   # in seconds

		self.event_to_method  = {
			"packetSent"               : self._packet_sent,
			"packetReceived"           : self._packet_received,
			"networkFormationCompleted": self._networkFormationTime,
			"syncronizationCompleted"  : self._synchronizationPhase,
			"secureJoinCompleted"      : self._secureJoinPhase,
			"bandwidthAssigned"        : self._bandwidthAssignment,
			"radioDutyCycleMeasurement": self._radioDutyCycle,
			"clockDriftMeasurement"    : None
		}


	def start(self):   # Should be started upon startBenchmark command
		threading.Thread(target=self._epe_monitor).start()


	def _epe_monitor(self):
		while True:
			if self.queue.empty():
				self.cv.acquire()
				self.cv.wait()     # Released when the queue has a new item
				self.cv.release()

			complete_payload = self.queue.get()
			self._process_event(complete_payload)

	def _process_event(self, complete_payload):
		# Should implement logic for event payload processing and updating log file
		complete_payload['node_id'] = Utils.eui64_to_id[complete_payload['eui64']]
		self.logger.log('raw', complete_payload)
		self._kpi_calculate(complete_payload)


	# Methods for calculating KPI
	def _kpi_calculate(self, event_obj):
		self.event_to_method[event_obj['event_payload']['event']](event_obj)

	def _packet_sent(self, event_obj):
		self.buffer.put(event_obj)

	def _packet_received(self, event_obj):
		origin_packet = self.buffer.find(event_obj['event_payload']['packetToken'])
		
		# Log latency
		if origin_packet != None:
			latency = event_obj['event_payload']['timestamp'] - origin_packet['event_payload']['timestamp']
			self.logger.log('kpi', {
					'kpi': 'latency',
					'eui64': origin_packet['eui64'],
					'node_id': origin_packet['node_id'],
					'dest_eui64': event_obj['eui64'],
					'dest_node_id': event_obj['node_id'],
					'timestamp': event_obj['event_payload']['timestamp'],
					'value': latency
				})


	def _networkFormationTime(self, event_obj):
		self.logger.log('kpi', {
				'kpi'      : 'networkFormationTime',
				'eui64'    : event_obj['eui64'],
				'node_id'  : event_obj['node_id'],
				'timestamp': event_obj['event_payload']['timestamp'],
				'value'    : 1
			})

	def _synchronizationPhase(self, event_obj):
		self.logger.log('kpi', {
				'kpi'      : 'syncronizationPhase',
				'eui64'    : event_obj['eui64'],
				'node_id'  : Utils.eui64_to_id[event_obj['eui64']],
				'timestamp': event_obj['event_payload']['timestamp'],
				'value'    : 1
			})

	def _secureJoinPhase(self, event_obj):
		self.logger.log('kpi', {
				'kpi'      : 'secureJoinPhase',
				'eui64'    : event_obj['eui64'],
				'node_id'  : Utils.eui64_to_id[event_obj['eui64']],
				'timestamp': event_obj['event_payload']['timestamp'],
				'value'    : 1
			})

	def _bandwidthAssignment(self, event_obj):
		self.logger.log('kpi', {
				'kpi'      : 'bandwidthAssignment',
				'node_id'  : Utils.eui64_to_id[event_obj['eui64']],
				'eui64'    : event_obj['eui64'],
				'timestamp': event_obj['event_payload']['timestamp'],
				'value'    : 1
			})

	def _radioDutyCycle(self, event_obj):
		self.logger.log('kpi', {
				'kpi'      : 'radioDutyCycle',
				'eui64'    : event_obj['eui64'],
				'node_id'  : Utils.eui64_to_id[event_obj['eui64']],
				'timestamp': event_obj['event_payload']['timestamp'],
				'value'    : event_obj['event_payload']['dutyCycle']
			}) 