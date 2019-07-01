import sys
import time
import json
import random
import string
import threading
import collections

from utils import Utils
from mqtt_client.mqtt_client import MQTTClient


class Scheduler:

	nodes        = []                    # Array of type `Node`
	schedule     = collections.deque()   # Thread-safe array of dictionaries {"time_sec": type `float`, "node": type `Node`, "destination_eui64: `String`"}

	scheduler_delay = 5   #[s]

	def __init__(self):
		self.scenario = Utils.scenario
		self.mqtt_client = MQTTClient.create()

	def start(self):
		self._generate_schedule()
		self._start_schedule()

	# Used only within `generate_schedule`
	def _sort_schedule(self):
		self.schedule = sorted(self.schedule, key=lambda k: k["time_sec"])

	def _process_node_arr_chunk(self, chunk):
		for node in chunk:
			for sending_point in node.sending_points:
				time_sec         = sending_point["time_sec"]
				destination      = sending_point["destination"]
				confirmable      = sending_point["confirmable"]
				packets_in_burst = sending_point["packets_in_burst"] if "packets_in_burst" in sending_point else 1

				self.schedule.append({
					"time_sec"          : time_sec,
					"node"              : node,
					"destination_eui64" : Utils.id_to_eui64[ self.scenario.config_node_data[destination]['node_id'] ],
					"confirmable"       : confirmable,
					"packets_in_burst"  : packets_in_burst
				})

	def _generate_schedule(self):
		total_size = len(self.scenario.nodes)
		chunk_size = total_size / 4   # Divides the list into four chunks
		arr_chunks = []

		iter_val      = 0
		current_chunk = 1
		chunk         = []
		while iter_val < total_size:
			if iter_val == current_chunk * chunk_size:
				current_chunk += 1
				arr_chunks.append(chunk[:])
				chunk = []

			chunk.append(self.scenario.nodes[iter_val])
			iter_val += 1

		if len(chunk) > 0:
			arr_chunks.append(chunk)

		for chunk in arr_chunks:
			thread = threading.Thread(target=self._process_node_arr_chunk, args=[chunk])
			thread.daemon = True
			thread.start()
			thread.join()

		self._sort_schedule()


	def _print_schedule(self):
		schedule_len = len(self.schedule)

		self.mqtt_client.push_debug_log("[SCHEDULER]", "Starting schedule:")
		for i in range(0, schedule_len):
			print "{0} at {1}: from {2} to {3}".format(
				self.schedule[i]["node"].node_id, 
				self.schedule[i]["time_sec"],
				self.schedule[i]["node"].eui64,
				self.schedule[i]["destination_eui64"]
			)

		return schedule_len


	def _start_schedule(self):
		schedule_len = self._print_schedule()
		self.mqtt_client.push_debug_log("[SCHEDULER]", "Starting scheduler in {0} seconds...\n".format(self.scheduler_delay), False)
		sys.stdout.write("[SCHEDULER] Starting scheduler in {0} seconds...\n".format(self.scheduler_delay))
		time.sleep(self.scheduler_delay)

		self.mqtt_client.push_notification("orchestration-started", True)

		for i in range(0, schedule_len):
			currently_on = self.schedule[i]
			
			if i < schedule_len - 1:
				next_on      = self.schedule[i+1]
				sleep_interval = next_on["time_sec"] - currently_on["time_sec"]
			else:
				sleep_interval = -1

			# Assigning `sendPacket` payload as defined by the documentation
			currently_on["node"].command_exec(payload={
					'source'          : currently_on["node"].eui64,
					'destination'     : currently_on["destination_eui64"],
					'packetPayloadLen': self.scenario.main_config['payload_size'],
					'confirmable'     : currently_on["confirmable"],
					'packetsInBurst'  : currently_on["packets_in_burst"] 
				})

			if sleep_interval == -1:
				self.mqtt_client.push_debug_log("[SCHEDULER]", "Currently on: {0}/{1}. Last event\n".format(i+1, schedule_len), False)
				sys.stdout.write("[SCHEDULER] Currently on: {0}/{1}. Last event\n".format(i+1, schedule_len))
			else:
				self.mqtt_client.push_debug_log("[SCHEDULER]", "Currently on: {0}/{1}. Last event\n".format(i+1, schedule_len), False)
				sys.stdout.write("[SCHEDULER] Currently on: {0}/{1}. Next event in {2} seconds\n".format(i+1, schedule_len, sleep_interval))
				time.sleep(sleep_interval)