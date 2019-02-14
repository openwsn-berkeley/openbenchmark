import sys
import os
sys.path.append("..")

import json
import time
import threading
import colorama
import random
from scheduler import Scheduler
from mqtt_client.mqtt_client import MQTTClient
import paho.mqtt.client as mqtt
from mqtt_client._condition_object import ConditionObject
from utils import Utils


class Events:
    packetSent     = "packetSent"
    packetReceived = "packetReceived"
    networkFormationCompleted = "networkFormationCompleted"
    syncronizationCompleted   = "syncronizationCompleted"
    secureJoinCompleted       = "secureJoinCompleted"
    bandwidthAssigned         = "bandwidthAssigned"
    radioDutyCycleMeasurement = "radioDutyCycleMeasurement"


class Simulator(object):

    _instance = None

    @staticmethod
    def create(testbed, scenario, broker="broker.mqttdashboard.com"):
        if Simulator._instance == None:
            Simulator._instance = Simulator(testbed, scenario, broker)
        return Simulator._instance

    def __init__(self, testbed, scenario, broker):
        self.experiment_id      = Utils.experiment_id
        self.testbed            = testbed
        self.broker             = broker
        self.scenario           = scenario
        self.co                 = ConditionObject.create()

        self.bench_init_timeout = 3    #[s]

        self.scenario_config_dirs = {
            "building-automation":   os.path.join(os.path.dirname(__file__), "..", "scenarios", "building_automation"),
            "home-automation":       os.path.join(os.path.dirname(__file__), "..", "scenarios", "home_automation"),
            "industrial-monitoring": os.path.join(os.path.dirname(__file__), "..", "scenarios", "industrial_monitoring")
        }

        self._form_sut_payload()

        self.sent = []

        self.sub_topics = {
            "startBenchmark": "openbenchmark/response/startBenchmark",
            "sendPacket": "openbenchmark/experimentId/{0}/command/sendPacket".format(self.experiment_id),
            "configureTransmitPower": "openbenchmark/experimentId/{0}/command/configureTransmitPower".format(self.experiment_id),
            "triggerNetworkFormation": "openbenchmark/experimentId/{0}/command/triggerNetworkFormation".format(self.experiment_id)
        }
        self.pub_topics = {
            "startBenchmark": "openbenchmark/command/startBenchmark",
            "sendPacket": "openbenchmark/experimentId/{0}/response/sendPacket".format(self.experiment_id),
            "configureTransmitPower": "openbenchmark/experimentId/{0}/response/configureTransmitPower".format(self.experiment_id),
            "triggerNetworkFormation": "openbenchmark/experimentId/{0}/response/triggerNetworkFormation".format(self.experiment_id),
            "performanceData": "openbenchmark/experimentId/{0}/nodeId/00-12-4b-00-14-b5-b6-44/performanceData".format(self.experiment_id)
        }

        self._mqtt_client_setup() 


    def _form_sut_payload(self):
        self.sut_command_payload = {
            "api_version"  : "0.0.1",
            "token"        : "123",
            "date"         : "Sun Dec 2 14:41:13 UTC 2018",
            "firmware"     : "OpenWSN-42a4007db7",
            "testbed"      : self.testbed,
            "scenario"     : self.scenario
        }

        testbed_config = os.path.join(self.scenario_config_dirs[self.scenario], "_{0}_config.json".format(self.testbed))

        with open(testbed_config, 'r') as f:
            config_obj  = json.loads(f.read())
            eui64_start = 44
            sut_nodes = {}
            for key in config_obj:
                sut_nodes[config_obj[key]['node_id']] = "00-12-4b-00-14-b5-b6-{0}".format(eui64_start)
                eui64_start += 1

            self.sut_command_payload['nodes'] = sut_nodes


    def _mqtt_client_setup(self):
        # Setup Test module MQTT Client
        self.mqtt_client_configure()
        self.client.connect(self.broker)
        self.client.loop_forever()

    def mqtt_client_configure(self):
        self.client               = mqtt.Client("SUTSimulator")
        self.client.on_connect    = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_subscribe  = self._on_subscribe
        self.client.on_message    = self._on_message
        self.successful_subs      = 0


    def subscribe(self):
    	for key in self.sub_topics:
            sys.stdout.write("[SUT SIMULATOR] Subscribing to: {0}\n".format(self.sub_topics[key]))
            self.client.subscribe(self.sub_topics[key])

    def publish(self, topic, payload):
        self.client.publish(self.pub_topics[topic], json.dumps(payload))

    def _generate_sut_event_payload(self, event=None):
        # If event is not specified choose at random
        if event == None:    
            event = [Events.packetSent, Events.packetReceived][random.randint(0, 1)]

        sut_event_payload = {
            "event"    : event,
            "timestamp": time.time(),
        }
        
        if event == Events.radioDutyCycleMeasurement:
            sut_event_payload["dutyCycle"] = random.uniform(0, 1)

        elif event in [Events.packetSent, Events.packetReceived]:
            if event == Events.packetSent:
                token = [random.randint(0, 255) for i in range(15)]
                if  random.randint(1, 10) % 3 != 0:   # Simulate packet drop with probability of 0.3
                    self.sent.append(token)
                else:
                    sys.stdout.write("[SUT SIMULATOR] Dropping packet...")

            elif event == Events.packetReceived:
                rand_position = random.randint(0, len(self.sent)-1) if len(self.sent) > 0 else -1
                token = self.sent[rand_position] if rand_position > -1 else []
                if rand_position > -1:
                    del self.sent[rand_position]

            sut_event_payload["packetToken"] = token
            sut_event_payload["source"]      = "00-12-4b-00-14-b5-b6-44"
            sut_event_payload["destination"] = "00-12-4b-00-14-b5-b6-45"
            sut_event_payload["hopLimit"]    = 255

        print "[SUT SIMULATOR] {0} event generated".format(event)

        return sut_event_payload


    ##### MQTT client listeners #####
    def _on_connect(self, client, userdata, flags, rc):
        sys.stdout.write("[SUT SIMULATOR] Connected to the broker. Subscribing...\n")
        self.subscribe()

    def _on_disconnect(self, client, userdata, rc):
        sys.stdout.write("[SUT SIMULATOR] Disconnecting from the broker...\n")
        self.client.loop_stop()

    def _on_subscribe(self, client, obj, mid, granted_qos):
        self.successful_subs += 1
        if self.successful_subs == len(self.sub_topics):
            self.successful_subs = 0
            sys.stdout.write("[SUT SIMULATOR] Subscribed to all\n")
            sys.stdout.write("[SUT SIMULATOR] Publishing `startBenchmark` command in {0} seconds...\n".format(self.bench_init_timeout))
            time.sleep(self.bench_init_timeout)
            self.publish('startBenchmark', self.sut_command_payload)

    def _on_message(self, client, userdata, message):
        topic   = message.topic
        payload = message.payload

        sys.stdout.write("{0}[SUT SIMULATOR] Message on {1}: {2}\n{3}".format(colorama.Fore.YELLOW, topic, payload, colorama.Style.RESET_ALL))

        if topic == self.sub_topics['startBenchmark']:
            self._on_startBenchmark(payload)
        elif topic == self.sub_topics['sendPacket']:
        	self._on_sendPacket(payload)
        elif topic == self.sub_topics['configureTransmitPower']:
            self._on_configureTransmitPower(payload)
        elif topic == self.sub_topics['triggerNetworkFormation']:
            self._on_triggerNetworkFormation(payload)
            

    def _on_startBenchmark(self, payload):
        sys.stdout.write("[SUT SIMULATOR] Start benchmark command sent and received. Subscribed to command topics\n")

    def _on_sendPacket(self, payload):
        try:
            payload_obj = json.loads(payload)
            self.publish('sendPacket', {
                    'token': payload_obj['token'],
                    'success': True    # if random.randint(0, 9) != 0 else False
                })
            
            self.publish('performanceData', json.dumps(self._generate_sut_event_payload()))
        except Exception, e:
            print "[SUT SIMULATOR] Exception: " + str(e)

    def _on_configureTransmitPower(self, payload):
        try:
            payload_obj = json.loads(payload)
            self.publish('configureTransmitPower', {
                    'token': payload_obj['token'],
                    'success': True    # if random.randint(0, 9) != 0 else False
                })
        except Exception, e:
            print "[SUT SIMULATOR] Exception: " + str(e)

    def _on_triggerNetworkFormation(self, payload):
        try:
            payload_obj = json.loads(payload)
            self.publish('triggerNetworkFormation', {
                    'token': payload_obj['token'],
                    'success': True    # if random.randint(0, 9) != 0 else False
                })
            
            self.publish('performanceData', json.dumps(self._generate_sut_event_payload('networkFormationCompleted')))
        except Exception, e:
            print "[SUT SIMULATOR] Exception: " + str(e)