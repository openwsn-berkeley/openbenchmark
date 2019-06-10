<template>
	<div class="top-container" :class="{'black-overlay': !collapsed}">
		<div id="parent" class="container shadow" :class="{collapsed: collapsed}" :style="{height: computedHeight}" @click="action($event)">
			<span class="top-span" draggable="true" @mousedown="startDragging($event)"></span>
			<i id="terminal" class="fas fa-terminal" v-if="collapsed"></i>
			<i id="close" class="fas fa-times" v-if="!collapsed" @click="action($event)"></i>
			<span class="dialog-title" v-if="!collapsed">Debug output: </span>
			<div class="dialog-content">
				<debug-window class="debug-window" v-if="!collapsed"></debug-window>
			</div>
		</div>
	</div>
</template>

<script>
	import DebugWindow from './../landing/DebugWindow.vue';

	export default {
		components: {
			DebugWindow
		},

		data: function() {
			return {
				collapsed: true,
				height: 350
			}
		},

		computed: {
			computedHeight() {
				return (this.collapsed ? 40 : this.height) + "px"
			}
		},

		methods: {
			action(event, isCollapsed) {
				if (this.collapsed)
					this.collapsed = false
				else if (event.target.id === "close")
					this.collapsed = true

				event.stopPropagation()
			},
			startDragging(event) {
				document.addEventListener("mousemove", this.resize, false)
				document.addEventListener("mouseup", this.stopDragging, false)
			},
			resize(event) {
				this.height = event.clientY
			},
			stopDragging(event) {
				document.removeEventListener("mousemove", this.resize, false)
			}
		}
	}
</script>

<style scoped>
	.top-container {
		transition: 0.3s ease;
	}
	.container {
		position: fixed;
		bottom: 0;
		right: 0;
		width: 100vw;
		transition: 0.3s ease;
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