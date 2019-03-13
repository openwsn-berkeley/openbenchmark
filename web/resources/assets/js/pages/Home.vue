<template>
    <div class="parent row">
        <sidebar></sidebar>
        <div id="root" style="margin-left: 80px">
            <intro id="intro" v-observe-visibility="{
                   callback: visibilityChanged,
                   intersection: {
                       root,
                       threshold
                   }
            }"></intro>
            <scenarios id="scenarios"  v-observe-visibility="{
                   callback: visibilityChanged,
                   intersection: {
                       root,
                       threshold
                   }
            }"></scenarios>
            <graphs id="graphs"  v-if="dataFlowStarted" v-observe-visibility="{
                   callback: visibilityChanged,
                   intersection: {
                       root,
                       threshold
                   }
            }"></graphs>
        </div>
    </div>
</template>

<script>
    import ExampleComponent from './../components/ExampleComponent.vue'
    import Intro from './../components/landing/Intro.vue'
    import Scenarios from './../components/landing/Scenarios.vue'
    import Graphs from './../components/landing/Graphs.vue'
    import Sidebar from './../components/reusables/Sidebar.vue'

    let thisComponent;
    let socketConnected = false;

    export default {
        components: {
            ExampleComponent,
            Intro,
            Scenarios,
            Graphs,
            Sidebar
        },
        data: function () {
            return {
                dataFlowStarted: true,
                sidebarScroll: false,
                root: document.getElementById('root'),
                threshold: 0.05
            }
        },

        methods: {
            registerChannel: function() {
                this.$socket.emit('channelRegistration', 1); //Second param should be a dynamically added id
                console.log("Channel registered!");
            },
            forwardMessage: function(topic, data) {
                this.$eventHub.$emit(topic, data);
            },

            scrollContent(anchor) {
                this.$eventHub.$emit('SCROLL', anchor);
            },

            visibilityChanged (isVisible, entry) {
                if (isVisible && !this.sidebarScroll)
                    this.scrollContent(entry.target.id);
            }
        },

        mounted() {
            this.$eventHub.$on("SCROLL", payload => {
                window.scroll({
                    top: document.getElementById(payload).offsetTop,
                    left: 0,
                    behavior: 'smooth'
                });
                setTimeout(() => {
                    thisComponent.sidebarScroll = false;
                }, 300)
            });
            this.$eventHub.$on("SIDEBAR_SCROLL", payload => {
                thisComponent.sidebarScroll = true;
            });
            this.$eventHub.$on("LOG_MODIFICATION", payload => {
                this.dataFlowStarted = true;
            });
            this.$eventHub.$on("EXP_TERMINATE", payload => {
                this.dataFlowStarted = false;
            });
        },

        created() {
            thisComponent = this;

            this.$socket.on('connect', function() {
                console.log('Socket connected!');
                thisComponent.registerChannel();

                socketConnected = true;
            });

            this.$socket.on('NODE_RESERVATION', function(data) {
                thisComponent.forwardMessage('NODE_RESERVATION', data);
                console.log('NODE_RESERVATION: ' + data);
            });
            this.$socket.on('RESERVATION_SUCCESS', function(data) {
                thisComponent.forwardMessage('RESERVATION_SUCCESS', data);
                console.log('RESERVATION_SUCCESS: ' + data);
            });
            this.$socket.on('RESERVATION_STATUS_RETRY', function(data) {
                thisComponent.forwardMessage('RESERVATION_STATUS_RETRY', data);
                console.log('RESERVATION_STATUS_RETRY: ' + data);
            });
            this.$socket.on('RESERVATION_FAIL', function(data) {
                thisComponent.forwardMessage('RESERVATION_FAIL', data);
                console.log('RESERVATION_FAIL: ' + data);
            });

            this.$socket.on('NODE_BOOTED', function(data) {
                thisComponent.forwardMessage('NODE_BOOTED', data);
                console.log('NODE_BOOTED: ' + data);
            });
            this.$socket.on('BOOT_RETRY', function(data) {
                thisComponent.forwardMessage('BOOT_RETRY', data);
                console.log('BOOT_RETRY: ' + data);
            });
            this.$socket.on('BOOT_FAIL', function(data) {
                thisComponent.forwardMessage('BOOT_FAIL', data);
                console.log('BOOT_FAIL: ' + data);
            });

            this.$socket.on('NODE_ACTIVE', function(data) {
                thisComponent.forwardMessage('NODE_ACTIVE', data);
                console.log('NODE_ACTIVE: ' + data);
            });
            this.$socket.on('NODE_ACTIVE_FAIL', function(data) {
                thisComponent.forwardMessage('NODE_ACTIVE_FAIL', data);
                console.log('NODE_ACTIVE_FAIL: ' + data);
            });

            this.$socket.on('LOG_MODIFICATION', function(data) {
                thisComponent.forwardMessage('LOG_MODIFICATION', data);
                console.log('LOG_MODIFICATION: ' + data);
            });

            this.$socket.on('EXP_TERMINATE', function(data) {
                thisComponent.forwardMessage('EXP_TERMINATE', data);
                console.log('EXP_TERMINATE: ' + data);
            });

            setTimeout(function() {
                if (!socketConnected) {
                    thisComponent.registerChannel();
                }
            }, 200);
        }
    }
</script>

<style src="./../../sass/layout/margins.css"></style>
<style src="./../../sass/layout/paddings.css"></style>
<style src="./../../sass/layout/positioning.css"></style>
<style src="./../../sass/styles/text-styles.css"></style>
<style src="./../../sass/styles/buttons.css"></style>
<style src="./../../sass/styles/colors.css"></style>
<style src="./../../sass/styles/animations.css"></style>
<style src="./../../sass/styles/cards.css"></style>

<style scoped>
    .parent {
        position: relative;
    }
</style>