import argparse
from experiment_provisioner.main import Main as ExpProvisioner

class OpenBenchmark:

	def __init__(self):
		pass

	def add_parser_args(self, parser):
		self.default_fws = {
			"iotlab": "03oos_openwsn_prog_iotlab",
			"wilab" : "03oos_openwsn_prog_wilab.ihex"
		}

		parser.add_argument('--user-id',   # User ID is tied to the OpenBenchmark account
			dest       = 'user_id',
			default    = 0,
			required   = False,
			action     = 'store'
		)
		parser.add_argument('--simulator', 
			dest       = 'simulator',
			default    = False,
			action     = 'store_true'
		)
		parser.add_argument('--action', 
			dest       = 'action',
			choices    = ['check', 'reserve', 'terminate', 'flash', 'ov-start'],
			required   = True,
			action     = 'store'
		)
		parser.add_argument('--testbed', 
			dest       = 'testbed',
			choices    = ['iotlab', 'wilab'],
			default    = 'iotlab',
			action     = 'store'
		)
		parser.add_argument('--firmware', 
			dest       = 'firmware',
			required   = False,
			action     = 'store',
		)
		parser.add_argument('--branch', 
			dest       = 'branch',
			required   = False,
			action     = 'store',
		)
		parser.add_argument('--scenario', 
			dest       = 'scenario',
			choices    = ['demo-scenario', 'building-automation', 'home-automation', 'industrial-monitoring'],
			default    = 'demo-scenario',
			action     = 'store'
		)

	def get_args(self):
		parser = argparse.ArgumentParser()
		self.add_parser_args(parser)
		args = parser.parse_args()

		return {
			'user_id'   : args.user_id,
			'simulator' : args.simulator,
			'action'    : args.action,
			'testbed'   : args.testbed,
			'firmware'  : args.firmware,
			'branch'    : args.branch,
			'scenario'  : args.scenario
		}


def main():
	openbenchmark = OpenBenchmark()
	args = openbenchmark.get_args()

	user_id   = args['user_id']
	simulator = args['simulator']
	action    = args['action']
	testbed   = args['testbed']
	scenario  = args['scenario']

	firmware  = args['firmware']
	branch    = args['branch']

	ExpProvisioner(user_id, simulator, action, testbed, scenario, firmware, branch)

if __name__ == '__main__':
	main()