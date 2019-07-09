import testbed


TESTBEDS = [
	testbed.IoTLAB
]


def general_test(action):
	res = []

	for Testbed in TESTBEDS:
		testbed = Testbed()
		res.append(testbed.run_action(action))

	return all(res)

# Tests
def test_reservation():
	assert general_test('reserve')

def test_firmware_flash():
	assert general_test('flash')

def test_ov_start():
	assert general_test('sut-start')