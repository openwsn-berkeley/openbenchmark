import os
import json
import argparse
import time
import datetime


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
		files = [f for f in os.listdir(os.path.join(os.path.dirname(__file__), '.cache')) if os.path.isfile(os.path.join(os.path.dirname(__file__), '.cache', f)) and f[0] != "."]
		data = []

		for file in files:
			with open(os.path.join(os.path.dirname(__file__), '.cache', file), 'r') as f:
				header = json.loads(f.read())["header"]
				data.append({
						"date"          : header["date"],
						"experiment_id" : header["experiment_id"],
						"firmware"      : header["firmware"],
						"testbed"       : header["testbed"],
						"scenario"      : header["scenario"]
					})
		
		return json.dumps({
			"data": sorted(data, key=lambda k: self._date_to_timestamp(k['date']), reverse = True)
		})
		
	def _date_to_timestamp(self, date):
		return time.mktime(datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %Z %Y").timetuple())


	def _fetch_log_data(self):
		log_file = os.path.join(os.path.dirname(__file__), ".cache", "cached_kpi_{0}.json".format(self.experiment_id))

		if os.path.isfile(log_file):
			with open(log_file, 'r') as f:
				return f.read()

		return json.dumps({})



def main():
	print LogParser().fetch_data()

if __name__ == '__main__':
	main()