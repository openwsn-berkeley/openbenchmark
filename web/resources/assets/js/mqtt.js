import Paho from 'paho-mqtt';

export default class MQTTClient {

	constructor(hostname, port, eventHub) {

		let client = new Paho.Client(
			'broker.mqttdashboard.com', 
			Number(8000), 
			"obWebClient" + Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 5)
		)

		let subOptions = {qos: 2}

		client.onConnectionLost = onConnectionLost
		client.onMessageArrived = onMessageArrived

		client.connect({onSuccess:onConnect})

		function subscribe() {
			client.subscribe("openbenchmark/1/notifications", subOptions)
			client.subscribe("openbenchmark/userId/1/experimentId/+/kpi", subOptions)
			client.subscribe("openbenchmark/1/debug", subOptions)
			client.subscribe("openbenchmark/1/headerLogged", subOptions)
			client.subscribe("openbenchmark/1/testtopic", subOptions)
		}

		/// Listeners ///
		function onConnect() {
			console.log("onConnect")
			subscribe()
			client.send("openbenchmark/1/testtopic", "Hello world!", 2)
		}

		function onConnectionLost(responseObject) {
			if (responseObject.errorCode !== 0) {
				console.log("onConnectionLost: " + responseObject.errorMessage)
			}
		}

		function onMessageArrived(message) {
	  		console.log("onMessageArrived: " + message.payloadString)
	  		eventHub.$emit(message.destinationName, message.payloadString)
		}
	}

}