import testbed


TESTBEDS = [
	testbed.IoTLAB
]


def general_test(action):
	res = []

	for Testbed in TESTBEDS:
		testbed = Testbed()
		if action != 'ov-monitor':
			res.append(testbed.run_action(action))
		else:
			res.append(testbed.check_ov_log())

	return all(res)

# Tests
def test_reservation():
	assert general_test('reserve')

def test_firmware_flash():
	assert general_test('otbox-flash')

def test_ov_start():
	assert general_test('ov-start')

def test_ov_monitor():
	assert general_test('ov-monitor')