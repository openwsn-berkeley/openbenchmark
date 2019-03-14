import Paho from 'paho-mqtt';

export default class MQTTClient {

	constructor(hostname, port) {
		this.client = new Paho.Client(hostname, Number(port), "webBrowserClient")
		this.configurePaho()
	}

	configurePaho() {
		console.log("Configuring Paho");

        // set callback handlers
        this.client.onConnectionLost = this.onConnectionLost;
        this.client.onMessageArrived = this.onMessageArrived;

        // connect the client
        this.client.connect({onSuccess: this.onConnect});
    }

    onConnect() {
	    console.log("Connected to broker!");
	}
	onConnectionLost(responseObject) {
	    if (responseObject.errorCode !== 0)
	        console.log("onConnectionLost: " + responseObject.errorMessage)
	}
	onMessageArrived(message) {
	    console.log("onMessageArrived: " + message.payloadString)
	}


	publish(topic, payload) {
		if (!this.client.isConnected())
			return "MQTT Client not connected"

		try {
			let message = new Paho.Message(payload)
		    message.destinationName = topic
		    this.client.send(message)
		} catch (err) {
			return err
		}

	    return ""
	}

	subscribe(topic) {
		if (!this.client.isConnected())
			"MQTT Client not connected"
			
		try {
			this.client.subscribe(topic)
			console.log("Subscribed to: " + topic)
		} catch (err) {
			return err
		}

		return ""
	}

	test() {
		console.log("Printin' test!");
	}

}