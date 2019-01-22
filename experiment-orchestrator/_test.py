import sys
import json
import time
import threading
import colorama
from random import randint
from scheduler import Scheduler
from mqtt_client.mqtt_client import MQTTClient
import paho.mqtt.client as mqtt

# This test class simulates SUT responses by subscribing to the same MQTT topics
# and generating artificial responses upon receiving an API command

class Test:

    sut_command_payload = {
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

    def __init__(self, experiment_id, broker="broker.mqttdashboard.com"):
        self.experiment_id    = experiment_id
        self.broker           = broker

        self.sub_topics = {
            "sendPacket": "openbenchmark/experimentId/{0}/command/sendPacket".format(self.experiment_id),
            "test": "openbenchmark/test"
        }
        self.pub_topics = {
            "sendPacket": "openbenchmark/experimentId/{0}/response/sendPacket".format(self.experiment_id),
        }

        self.mqtt_client_setup()


    def mqtt_client_setup(self):
        # Create an MQTT client singleton instance and add a time padding
        MQTTClient.create(1)
        time.sleep(1)

        # Setup Test module MQTT Client
        self.mqtt_client_configure()
        self.client.connect(self.broker)
        self.client.loop_forever()

    def mqtt_client_configure(self):
        self.client               = mqtt.Client("SchedulerTest")
        self.client.on_connect    = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_subscribe  = self._on_subscribe
        self.client.on_message    = self._on_message
        self.successful_subs      = 0


    def subscribe(self):
        for key in self.sub_topics:
            print "[TEST] Subscribing to: {0}".format(self.sub_topics[key])
            self.client.subscribe(self.sub_topics[key])

    def publish(self, topic, payload):
        self.client.publish(self.pub_topics[topic], json.dumps(payload))


    ##### MQTT client listeners #####
    def _on_connect(self, client, userdata, flags, rc):
        print("[TEST] Connected to the broker. Subscribing...")
        self.subscribe()

    def _on_disconnect(self, client, userdata, rc):
        print("[TEST] Disconnecting from the broker...")
        self.client.loop_stop()

    def _on_subscribe(self, client, obj, mid, granted_qos):
        self.successful_subs += 1
        if self.successful_subs == len(self.sub_topics):
            self.successful_subs = 0
            print("[TEST] Subscribed to all. Starting scheduler...")
            threading.Thread(target=self.start_scheduler).start()

    def _on_message(self, client, userdata, message):
        topic   = message.topic
        payload = message.payload
        sys.stdout.write("{0}[TEST] Message on {1}: {2}\n{3}".format(colorama.Fore.YELLOW, topic, payload, colorama.Style.RESET_ALL))

        payload_obj = json.loads(payload)
        self.publish('sendPacket', {
                'token': payload_obj['token'],
                'success': True if randint(0, 9) != 0 else False
            })


    def start_scheduler(self):
        Scheduler(json.dumps(self.sut_command_payload))



def main():
    Test(1)

if __name__ == '__main__':
    main()