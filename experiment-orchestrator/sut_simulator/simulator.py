import sys
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


class Simulator(object):

    _instance = None

    @staticmethod
    def create():
        if Simulator._instance == None:
            Simulator._instance = Simulator()
        return Simulator._instance

    def __init__(self, broker="broker.mqttdashboard.com"):
        self.experiment_id      = Utils.experiment_id
        self.broker             = broker
        self.co                 = ConditionObject.create()

        self.bench_init_timeout = 3    #[s]

        self.sut_command_payload = {
            "api_version"  : "0.0.1",
            "token"        : "123",
            "date"         : "Sun Dec 2 14:41:13 UTC 2018",
            "firmware"     : "OpenWSN-42a4007db7",
            "testbed"      : "iotlab",
            "nodes"        : {  
                                "a8-100": "00-12-4b-00-14-b5-b6-44",
                                "a8-101": "00-12-4b-00-14-b5-b6-45",
                                "a8-102": "00-12-4b-00-14-b5-b6-46",
                                "a8-103": "00-12-4b-00-14-b5-b6-47"
                             },
            "scenario"     : "building-automation"
        }

        self.events = [
            "packetSent",
            "packetReceived"
            #"networkFormationCompleted",
            #"syncronizationCompleted",
            #"secureJoinCompleted",
            #"bandwidthAssigned",
            #"radioDutyCycleMeasurement"
        ]

        self.sent = []

        self.sub_topics = {
            "startBenchmark": "openbenchmark/response/startBenchmark",
            "sendPacket": "openbenchmark/experimentId/{0}/command/sendPacket".format(self.experiment_id),
        }
        self.pub_topics = {
            "startBenchmark": "openbenchmark/command/startBenchmark",
            "sendPacket": "openbenchmark/experimentId/{0}/response/sendPacket".format(self.experiment_id),
            "performanceData": "openbenchmark/experimentId/{0}/nodeId/00-12-4b-00-14-b5-b6-44/performanceData".format(self.experiment_id)
        }

        self._mqtt_client_setup() 


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

    def _generate_sut_event_payload(self):
        event = self.events[random.randint(0, len(self.events)-1)]
        sut_event_payload = {
            "event"    : event,
            "timestamp": time.time(),
        }
        
        if event == "radioDutyCycleMeasurement":
            sut_event_payload["dutyCycle"] = random.uniform(0, 1)

        elif event in ["packetSent", "packetReceived"]:
            if event == 'packetSent':
                token = [random.randint(0, 255) for i in range(15)]
                if  random.randint(1, 10) % 3 != 0:   # Simulate packet drop with probability of 0.3
                    self.sent.append(token)
                else:
                    sys.stdout.write("[SUT SIMULATOR] Droping packet...\n")

            elif event == 'packetReceived':
                rand_position = random.randint(0, len(self.sent)-1) if len(self.sent) > 0 else -1
                token = self.sent[rand_position] if rand_position > -1 else []
                if rand_position > -1:
                    del self.sent[rand_position]

            sut_event_payload["packetToken"] = token
            sut_event_payload["source"]      = "00-12-4b-00-14-b5-b6-44"
            sut_event_payload["destination"] = "00-12-4b-00-14-b5-b6-45"
            sut_event_payload["hopLimit"]    = 255

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
            sys.stdout.write("[SUT SIMULATOR] `sendPacket` event generated\n")
        except Exception, e:
            print "[SUT SIMULATOR] Exception: " + str(e)