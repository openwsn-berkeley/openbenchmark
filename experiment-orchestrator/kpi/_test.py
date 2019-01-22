import sys
sys.path.append('..')

import json
import time
import threading
import colorama
from processing import KPIProcessing
from mqtt_client.mqtt_client import MQTTClient
import paho.mqtt.client as mqtt

class Test:

    sut_event_payload = {
        "event"        : "packetSent",
        "timestamp"    : 2131,
        "packetToken"   : [124, 122, 34, 31],
        "source"       : "bbbb::0012:4b00:14b5:b648",
        "destination"  : "bbbb::1",
        "hopLimit"     : 255
    }

    def __init__(self, experiment_id, broker="broker.mqttdashboard.com"):
        self.experiment_id    = experiment_id
        self.broker           = broker

        self.sub_topics = {

        }
        self.pub_topics = {
            "performanceData": "openbenchmark/experimentId/{0}/nodeId/123/performanceData".format(self.experiment_id),
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


    def subscribe(self):
        for key in self.sub_topics:
            print "[TEST] Subscribing to: {0}".format(self.sub_topics[key])
            self.client.subscribe(self.sub_topics[key])

    def publish(self, topic, payload):
        self.client.publish(self.pub_topics[topic], json.dumps(payload))


    ##### MQTT client listeners #####
    def _on_connect(self, client, userdata, flags, rc):
        print("[TEST] Connected to the broker")
        threading.Thread(target=self.start_events).start()

    def _on_disconnect(self, client, userdata, rc):
        print("[TEST] Disconnecting from the broker...")
        self.client.loop_stop()


    def start_events(self):
        KPIProcessing().start()
        while True:
            self.publish('performanceData', json.dumps(self.sut_event_payload))
            time.sleep(3)



def main():
    Test(1)

if __name__ == '__main__':
    main()