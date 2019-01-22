Workflow:

1. Entry point (control.py), upon being invoked, subscribes to `openbenchmark/command/startBenchmark` (all MQTT dataflow is being managed by `MQTTClient` class defined in `mqtt_client.py`)

2. When experiment has started, SUT sends the following JSON payload on the MQTT topic mentioned in (1):
	```
		{
	        "api_version"  : "0.0.1",
	        "token"        : "123",
	        "date"         : "Sun Dec 2 14:41:13 UTC 2018",
	        "firmware"     : "OpenWSN-42a4007db7",
	        "testbed"      : "w-iLab.t"
	        "nodes"        : [  "00-12-4b-00-14-b5-b6-44",
	                            "00-12-4b-00-14-b5-b6-45",
	                            "00-12-4b-00-14-b5-b6-46"
	                         ]
	        "scenario"     : "building-automation"
	    }
	```

3. Entry point generates a unique experiment ID and sends the response to the SUT in the following format:
	```
		{
	        "token"        : "123",
	        "success"      : true,
	        "experimentId" : "1880b5363d7"
    	}
	```

4. Upon sending the acknowledgement, subscription to topic (1) is cancelled and a proper scenario object is instantiated based on the parameters taken from the JSON response in (2)

5. Based on the `nodes` field from the JSON response in (2), passed to the scenario object in (4), and data from `ConfigParser` object (defined in `_config_parser.py`), a list of node objects is formed. The list of node objects is a member variable of a scenario class

6. TO BE CONTINUED
