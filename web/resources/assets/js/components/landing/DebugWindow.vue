<template>
	<div class="parent col">
		<div class="row" :class="{gray: ind%2===0}" v-for="(item, ind) in outputs">
			<span class="debug-row col-2 tag">{{item.tag}}</span>
			<span class="debug-row col-7 message">{{item.message}}</span>
			<span class="debug-row col-1 time">{{item.time}}</span>
		</div>
	</div>
</template>

<script>
	let thisComponent;

	export default {
		data: function() {
			return {
				outputs: [
					// Item example {tag: "TAG", message: "Message of the debug output", time: "15:02:15"}
				]
			}
		},

		methods: {
			parseMqttEvent(payload) {
				try {
					let payloadObj = JSON.parse(payload)
	                
					let tag = payloadObj["action"]
					let logEntry = payloadObj["log_entry"]
					let time = new Date().getCurrentDate();

					this.outputs.push({
						"tag": tag,
						"message": logEntry,
						"time": time
					})

				} catch (exception) {
					console.log(exception)
				}
			},
		},

		created() {
			thisComponent = this
		},

		mounted() {
			this.$eventHub.$on("openbenchmark/1/debug", payload => {
				thisComponent.parseMqttEvent(payload);
			});
		}
	}

</script>


<style scoped>
	.parent {
		height: 100%;
		overflow-y: auto;
	}
	.debug-row {
		padding-top: 5px;
		padding-bottom: 5px;
		padding-left: 33px;
	}
	.gray {
		background-color: #fafafa;
	}

	.tag {

	}
	.message {
		font-weight: bold;
	}
	.time {

	}
</style>