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

		function sendEvent(topic, payload) {
			eventHub.$emit(topic, payload)

			// If the message has arrived on the KPI topic, notify the experiment id which the KPI has arrived for
			// This is used for updating experiment logs list  
			let topicSegments = topic.split('/')
			if (topicSegments[topicSegments.length - 1] == 'kpi') {
				let eventTopic = "openbenchmark/newKpi"
				let eventPayload = topicSegments[4]
				eventHub.$emit(eventTopic, eventPayload) 
			}
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
	  		sendEvent(message.destinationName, message.payloadString)
		}
	}

}