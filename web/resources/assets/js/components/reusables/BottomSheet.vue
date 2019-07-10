<template>
	<div id="top-container" class="top-container transition-anim" :class="{'black-overlay': !collapsed}" @click="action($event)">
		<div id="parent" class="container transition-anim shadow" :class="{collapsed: collapsed}" :style="{height: computedHeight}" @click="action($event)">
			<span class="top-span" draggable="true" @mousedown="startDragging($event)"></span>
			<i id="terminal" class="fas fa-terminal" v-if="collapsed"></i>
			<i id="close" class="fas fa-times" v-if="!collapsed" @click="action($event)"></i>
			<span class="dialog-title bold" v-if="!collapsed">Debug output: </span>
			<div class="dialog-content">
				<debug-window class="debug-window" v-if="!collapsed" :outputs="outputs"></debug-window>
			</div>
		</div>
	</div>
</template>

<script>
	import DebugWindow from './../landing/DebugWindow.vue';

	let topContainer
	let thisComponent

	export default {
		components: {
			DebugWindow
		},

		data: function() {
			return {
				collapsed: true,
				height: 350,
				outputs: [
					// Item example {tag: "TAG", message: "Message of the debug output", time: "15:02:15"}
				]
			}
		},

		computed: {
			computedHeight() {
				return (this.collapsed ? 40 : this.height) + "px"
			}
		},

		methods: {
			action(event) {
				if (this.collapsed)
					this.collapsed = false
				else if (event.target.id === "close" || event.target.id === "top-container")
					this.collapsed = true

				event.stopPropagation()
			},
			startDragging(event) {
				if (topContainer.classList.contains('transition-anim')) 
					topContainer.classList.remove('transition-anim')

				document.addEventListener("mousemove", this.resize, false)
				document.addEventListener("mouseup", this.stopDragging, false)
			},
			resize(event) {
				this.height = window.innerHeight - event.clientY
			},
			stopDragging(event) {
				document.removeEventListener("mousemove", this.resize, false)
				topContainer.classList.add('transition-anim')
			},

			parseMqttEvent(payload) {
				try {
					let payloadObj = JSON.parse(payload)
	                
					let tag = payloadObj["action"]
					let logEntry = payloadObj["log_entry"]
					let time = new Date().getCurrentDate();

					this.outputs.unshift({
						"tag": tag,
						"message": logEntry,
						"time": time
					})

				} catch (exception) {
					console.log(exception)
				}
			}
		},

		created() {
			thisComponent = this
		},

		mounted() {
			topContainer = document.getElementById("parent")

			this.$eventHub.$on("openbenchmark/1/debug", payload => {
				thisComponent.parseMqttEvent(payload);
			});
		}
	}
</script>

<style scoped>
	.transition-anim {
		transition: 0.3s ease;
	}
	.container {
		position: fixed;
		bottom: 0;
		right: 0;
		width: 100vw;
		z-index: 3;
		background: white;
		border-top: 3px #0e305d solid;
	}
	.container > .fa-terminal {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		color: white;
	}
	.container > .fa-times {
		position: absolute;
		top: 0;
		right: 0;
		margin-top: 15px;
		margin-right: 15px;
		cursor: pointer;
		color: #0e305d;
		z-index: 4;
	}
	.top-span {
		position: absolute;
		top: 0;	
		width: 100%;
		height: 5px;
		background: transparent;
		cursor: n-resize;
	}


	.collapsed {
		width: 40px;
		right: 10px;
		bottom: 10px;
		border-radius: 50%;
		background: #0e305d;
		cursor: pointer;
	}

	.black-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
		z-index: 2;
		background: rgba(0, 0, 0, 0.5);
	}

	.dialog-title {
		position: absolute;
		top: 13px;
		left: 33px;
	}

	.dialog-content {
		position: absolute;
		top: 40px;
		left: 0;
		width: 100%;
		height: calc(100% - 40px);
	}
</style>