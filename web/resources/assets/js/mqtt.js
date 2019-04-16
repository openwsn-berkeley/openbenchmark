import Paho from 'paho-mqtt';

let eventHub = null

export default class MQTTClient {

	constructor(hostname, port, vueEventHub) {
		this.subTopics = [
			"openbenchmark/notifications", 
			"openbenchmark/kpi"
		]

		eventHub = vueEventHub

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

	subscribe() {
		if (!this.client.isConnected())
			"MQTT Client not connected"
			
		try {
			for (let i = 0; i < this.subTopics.length; i++) {
				this.client.subscribe(this.subTopics[i])
				console.log("Subscribed to: " + this.subTopics[i])
			}
		
		} catch (err) {
			return err
		}

		return ""
	}

	test() {
		console.log("Printin' test!");
	}

}