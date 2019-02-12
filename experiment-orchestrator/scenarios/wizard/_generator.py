import numpy as np
import random


class Generator:

	def __init__(self, duration):
		self.exp_duration = duration    # In seconds


	def generate(self, node_pool, params):
		return getattr(self, "_generate_{0}".format(params['traffic_type']))(node_pool, params)


	def _generate_periodic(self, node_pool, params):
		bottom_interval  = params['interval'][0]
		top_interval     = params['interval'][1]
		packets_in_burst = params['packets_in_burst']
		current_instant  = 0
		sending_points   = []

		while 'current_instant is less than the exp_duration':
			interval = np.random.uniform(bottom_interval, top_interval)
			current_instant += interval

			if current_instant >= self.exp_duration:
				break

			node = random.choice(node_pool)

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

		return sorted(sending_points, key=lambda k: k['time_sec'])


	def _generate_poisson(self, node_pool, params):
		mean               = params['mean']   # per hour
		packets_in_burst   = params['packets_in_burst']
		period             = 3600   # 1h in seconds
		top_interval       = 0
		sending_points     = []

		# No do-while loop here because of the list comprehension filter on current_instants
		while top_interval < self.exp_duration:
			bottom_interval  = top_interval
			top_interval     = bottom_interval + period
			num_of_packets   = np.random.poisson(mean)

			current_instants = [random.expovariate(1.0/mean) * 60 for i in range(0, num_of_packets)]
			current_instants = [instant for instant in current_instants if instant < self.exp_duration]

			for instant in current_instants:
				node = random.choice(node_pool)
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

		return sorted(sending_points, key=lambda k: k['time_sec'])