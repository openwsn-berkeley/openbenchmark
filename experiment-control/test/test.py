import subprocess
import os
import time
import json

mainDir                   = os.path.join(os.path.dirname(__file__), "..")

OV_START_PAUSE            = 20     # pause before starting OV
OV_MONITOR_START_PAUSE    = 20     # pause before starting OV log monitoring

LOG_CHECK_PAUSE           = 5
LOG_CHECK_RETRIES         = 15


def get_last_line(file_path):
	if os.path.isfile(file_path):
		return subprocess.check_output(['tail', '-1', file_path])
	else:
		return ""

def run_action(action):
	pipe = subprocess.Popen(['python', 'main.py', '--action={0}'.format(action)], cwd=mainDir, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

	res = pipe.communicate()
	retcode = pipe.returncode
	stderr = res[1]

	if stderr != "":
		print stderr

	return retcode

def check_ov_log():
	home_path = os.path.expanduser("~")
	log_file = os.path.join(home_path, "openvisualizer", "build", "runui", "networkEvent.log")

	data_recieved = False

	for i in range(0, LOG_CHECK_RETRIES):
		try:
			json_obj = json.loads(get_last_line(log_file))
			data_recieved = True
			break
		except Exception, e:
			print str(e)
			time.sleep(LOG_CHECK_PAUSE)

	return data_recieved
	


#Tests
def test_reservation():
	assert run_action('reserve') == 0

def test_otbox_startup():
	assert run_action('otbox') == 0

def test_firmware_flash():
	assert run_action('otbox-flash') == 0

def test_ov_start():
	time.sleep(OV_START_PAUSE)
	assert run_action('ov-start') == 0

def test_ov_monitor():
	time.sleep(OV_MONITOR_START_PAUSE)
	assert check_ov_log() == True




if __name__ == '__main__':
	test_reservation()
	test_otbox_startup()
	test_firmware_flash()
	test_ov_start()
	test_ov_monitor()