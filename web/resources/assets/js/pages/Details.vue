<template>
    <div class="parent col-direction">
        <span class="ml-3 mt-1 row-direction flex-space-between">
            <span>
                <i class="fas fa-arrow-left clickable" @click="back()"></i>
                <span class="ml-1">KPIs for experiment <span class="bold">{{id}}</span>, firmware: <span class="bold">{{headerData.firmware}}</span></span>
            </span>
            
            <span class="align-right mr-3">
                <span class="bold">{{testbeds[headerData.testbed]}}, </span>
                <span class="bold">{{scenarios[headerData.scenario]}}, </span>
                <span class="bold">{{headerData.date}}</span>
            </span>
        </span>
        <div id="root">
            <graphs id="graphs" :experiment-id="id"></graphs>
        </div>
    </div>
</template>

<script>
    import Graphs from './../components/landing/Graphs.vue'

    let thisComponent;
    let socketConnected = false;

    export default {
        props: ['id'],

        components: {
            Graphs
        },

        data: function () {
            return {
                headerData: {},

                testbeds: {
                    "iotlab": "IoT-LAB",
                    "wilab": "w-iLab.t"
                },
                scenarios: {
                    "demo-scenario": "Demo Scenario",
                    "home-automation": "Home Automation",
                    "building-automation": "Building Automation",
                    "industrial-monitoring": "Industrial Monitoring"
                }
            }
        },

        methods: {
            back() {
                this.$router.back()
            }
        },

        mounted() {
            this.$eventHub.$on("LOG_DATA_FETCHED", payload => {
                thisComponent.headerData = payload
            });
        },

        created() {
            thisComponent = this;
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
<style src="./../../sass/styles/radio.css"></style>
<style src="./../../sass/styles/vuebar.css"></style>

<style scoped>
    .parent {
        background-color: #eeeeee;
        height: 100vh;
    }

    #root {
        width: 100%;
        height: 85%;
    }
</style>