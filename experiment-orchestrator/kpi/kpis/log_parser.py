import os
import json
import argparse


class LogParser:

	def __init__(self):
		self._get_args()


	def _add_parser_args(self, parser):
		parser.add_argument('--action',
			dest       = 'action',
			choices    = ['log-list', 'data-fetch'],
			default    = 'log-list',
			action     = 'store'
		)
		parser.add_argument('--experiment-id', 
	        dest       = 'experiment_id',
	        action     = 'store'
		)

	def _get_args(self):
		parser = argparse.ArgumentParser()
		self._add_parser_args(parser)
		args = parser.parse_args()

		self.action        = args.action
		self.experiment_id = args.experiment_id

		if self.action == 'data-fetch' and self.experiment_id == None:
			parser.error('--action=data-fetch requires --experiment-id param')


	def fetch_data(self):
		if self.action == 'log-list':
			return self._fetch_log_list()
		return self._fetch_log_data()

	
	def _fetch_log_list(self):
		files = [f for f in os.listdir('.') if os.path.isfile(f) and f != os.path.basename(__file__)]
		return {
			"logs": files
		}

	def _fetch_log_data(self):
		return {
			"data": {}   # Read data from cache
		}



def main():
	print json.dumps(LogParser().fetch_data())

if __name__ == '__main__':
	main()