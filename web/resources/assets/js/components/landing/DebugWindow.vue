<template>
	<div class="parent col">
		<div class="row" :class="{gray: ind%2===0}" v-for="(item, ind) in outputs">
			<span class="debug-row col-1 tag">{{item.tag}}</span>
			<span class="debug-row col-7 message">{{item.message}}</span>
			<span class="debug-row col-1 time">{{item.time}}</span>
		</div>
	</div>
</template>

<script>
	export default {
		data: function() {
			return {
				outputs: [
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"},
					{tag: "TAG", message: "Message of the debug output", time: "15:02:15"}
				]
			}
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