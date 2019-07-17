import sys

from abc import abstractmethod
from cryptography.utils import CryptographyDeprecationWarning
from helpers.iotlab.otbox_startup import OTBoxStartup
from mqtt_client import MQTTClient

import os
import paramiko
import json
import time
import subprocess
import warnings


class Reservation:
    @abstractmethod
    def reserve_experiment(self):
        pass

    @abstractmethod
    def check_experiment(self):
        pass

    @abstractmethod
    def terminate_experiment(self):
        pass


class IoTLABReservation(Reservation):
    CMD_ERROR = "cmd_error"
    SSH_RETRY_TIME = 240
    RETRY_PAUSE = 10

    def __init__(self, user_id, user, domain, broker, otb_repo, otb_tag, duration=None, nodes=None):
        warnings.simplefilter(
            action='ignore',
            category=CryptographyDeprecationWarning
        )

        self.mqtt_client = MQTTClient.create("iotlab", user_id)   # User ID specific to OpenBenchmark platform

        self.user     = user         # IoT-LAB acc username defined within the config file
        self.domain   = domain
        self.duration = duration
        self.nodes    = nodes
        self.broker   = broker

        self.otb_repo = otb_repo
        self.otb_tag  = otb_tag

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()

        paramiko_log_path = os.path.join(os.path.dirname(__file__), "logs")
        if not os.path.exists(paramiko_log_path):
            os.mkdir(paramiko_log_path)
        paramiko.util.log_to_file(os.path.join(paramiko_log_path, 'reservation_paramiko.log'))

        self.ssh_connect()

    def ssh_connect(self):
        self.client.connect(self.domain, username=self.user)

    def ssh_disconnect(self):
        self.client.close()

    def ssh_command_exec(self, command):
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            stdin.close()

            output = []
            for line in stdout.read().splitlines():
                output.append(line)

            error = []
            for line in stderr.read().splitlines():
                error.append(line)

            if len(error) > 0:
                print("Error: " + ''.join(error))
                raise Exception(self.CMD_ERROR)

            return ''.join(output)

        except:
            return self.CMD_ERROR

    def get_reserved_nodes(self):
        if self.check_experiment(True):
            output = self.ssh_command_exec('iotlab-experiment get -p')
            json_output = json.loads(output)['nodes']
            return json_output
        else:
            return []

    ####### Abstract method implementations #######

    def reserve_experiment(self):
        if self.check_experiment():
            print('Resources already reserved. Moving on...')
            self.mqtt_client.push_debug_log('NODE_RESERVATION', 'Resources already reserved. Moving on...')
        else:
            output = self.ssh_command_exec(
                'iotlab-experiment submit -n a8_exp -d ' + str(self.duration) + ' -l ' + self.nodes)
            if output != self.CMD_ERROR:
                self.experiment_id = json.loads(output)['id']
                self.mqtt_client.push_debug_log('NODE_RESERVATION', 'All nodes reserved')
                print('All nodes reserved')

                nodes = self.get_reserved_nodes()

                if len(nodes) > 0:
                    OTBoxStartup(self.user, self.domain, 'iotlab', self.get_reserved_nodes(), self.broker, self.mqtt_client, self.otb_repo, self.otb_tag).start()
                else:
                    self.mqtt_client.push_debug_log('RESERVATION_FAIL', 'Experiment startup failed')
                    print('Experiment startup failed')

    def check_experiment(self, loop=False):
        retries = 0
        num_of_retries = self.SSH_RETRY_TIME / self.RETRY_PAUSE

        json_output = []

        while True:

            output = self.ssh_command_exec('iotlab-experiment get -p')

            if output != self.CMD_ERROR:
                print("Experiment check: " + output)
                json_output = json.loads(output)['nodes']
                return True
            elif retries <= num_of_retries:
                print('Retrying... {0}/{1}'.format(retries, num_of_retries))
                self.mqtt_client.push_debug_log('RESERVATION_STATUS_RETRY', str(retries) + "/" + str(num_of_retries))
                retries += 1
                time.sleep(self.RETRY_PAUSE)
            else:
                print('Reservation fail: {0}/{1}'.format(retries, num_of_retries))
                self.mqtt_client.push_debug_log('RESERVATION_FAIL', str(retries) + "/" + str(num_of_retries))
                self.mqtt_client.push_notification("provisioned", False)
                break

            if not loop:
                break

        return False

    def terminate_experiment(self):
        self.ssh_command_exec('iotlab-experiment stop')
        print('Terminating the experiment...')
        self.mqtt_client.push_debug_log('EXP_TERMINATE', 'Terminating the experiment...')

        python_proc_kill = "sudo kill $(ps aux | grep '[p]ython' | awk '{print $2}')"
        delete_logs = "rm ~/soda/openvisualizer/openvisualizer/build/runui/*.log; rm ~/soda/openvisualizer/openvisualizer/build/runui/*.log.*;"

        self.mqtt_client.push_notification("terminated", True)
        
        subprocess.Popen(python_proc_kill, shell=True)
        time.sleep(3)
        subprocess.Popen(delete_logs, shell=True)


class WilabReservation(Reservation):

    def __init__(self, user_id, jfed_dir, run, delete, display):
        self.mqtt_client = MQTTClient.create("wilab", user_id)
        
        self.jfed_dir = jfed_dir
        self.actions = {
            "run": run,
            "delete": delete
        }

    def run_yml_action(self, action):
        self._start_display()

        pipe = subprocess.Popen(['sh', self.actions[action]], cwd=self.jfed_dir, stdin=subprocess.PIPE,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        for line in iter(pipe.stdout.readline, b''):
            output = line.rstrip()
            print(">>> " + output)
            self.mqtt_client.push_debug_log('WILAB_PROVISIONING', output)

        for line in iter(pipe.stderr.readline, b''):
            output = line.rstrip()
            print(">>> " + output)
            self.mqtt_client.push_debug_log('WILAB_PROVISIONING [ERROR]', output)

    def _start_display(self):
        pipe = subprocess.Popen(['xrandr', '-d', ':99'], stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        pipe.communicate()

        if pipe.returncode != 0:
            os.system('/usr/bin/Xvfb :99 &')

    ####### Abstract method implementation #######

    def reserve_experiment(self):
        self.run_yml_action(action="run")
        if self.check_experiment():
            print("w-iLab.t provisioning successful")
            self.mqtt_client.push_notification("provisioned", True)
        else:
            print("w-iLab.t provisioning failed")
            self.mqtt_client.push_notification("provisioned", False)

    def check_experiment(self):
        return self.mqtt_client.check_data_stream()

    def terminate_experiment(self):
        print('Terminating the experiment...')
        self.mqtt_client.push_debug_log('EXP_TERMINATE', 'Terminating the experiment...')
        self.run_yml_action(action="delete")
        self.mqtt_client.push_notification("terminated", True)