import numpy as np
import random


class Generator:

	def __init__(self, duration):
		self.exp_duration = duration    # In seconds


	def generate(self, node_pool, params):
		sending_points = []
		for destination in node_pool:
			sending_points += getattr(self, "_generate_{0}".format(params['traffic_type'][destination]))(
				destination, 
				node_pool[destination], 
				params
			)

		return sorted(sending_points, key=lambda k: k['time_sec'])


	def _generate_periodic(self, destination, nodes, params):
		bottom_interval  = params['traffic_properties']['interval'][0]
		top_interval     = params['traffic_properties']['interval'][1]
		packets_in_burst = params['packets_in_burst']
		current_instant  = 0
		sending_points   = []

		while 'current_instant is less than the exp_duration':
			interval = np.random.uniform(bottom_interval, top_interval)
			current_instant += interval

			if current_instant >= self.exp_duration:
				break
			
			node = random.choice(nodes)

			if packets_in_burst > 1:
				sending_points.append({
						'time_sec':         round(current_instant, 3),
						'destination':      node['id'],
						'confirmable':      node['confirmable'],
						'packets_in_burst': packets_in_burst
					})
			else:
				sending_points.append({
						'time_sec':    round(current_instant, 3),
						'destination': node['id'],
						'confirmable': node['confirmable'],
					})

		return sending_points


	def _generate_poisson(self, destination, nodes, params):
		mean               = params['traffic_properties']['mean'] * (self.exp_duration/60)  # per hour
		num_of_packets     = np.random.poisson(mean)
		packets_in_burst   = params['packets_in_burst']
		period             = 3600   # 1h in seconds
		top_interval       = 0
		sending_points     = []

		instants = [random.expovariate(1.0/mean) * (self.exp_duration/60) for i in range(0, num_of_packets)]
		instants = [instant for instant in instants if instant < self.exp_duration]

		for instant in instants:
			node = random.choice(nodes)
			if packets_in_burst > 1:
				sending_points.append({
						'time_sec':         round(instant, 3),
						'destination':      node['id'],
						'confirmable':      node['confirmable'],
						'packets_in_burst': packets_in_burst
					})
			else:
				sending_points.append({
						'time_sec':    round(instant, 3),
						'destination': node['id'],
						'confirmable': node['confirmable']
					})

		return sending_points