<template>
    <div class="parent">
        <div class="row">
            <div class="col-5 pr-5 pl-5">

                <h4>Scenario: </h4>
                <div class="row">
                    <div class="scenario col-direction" :class="{'scenario-selected': scenarioSelected === index}" @click="selectScenario(index)" v-for="(scenario, index) in scenarios">
                        <i class="fas fa-3x text-center" :class="scenarioIcons[scenario.identifier]"></i>
                        <span class="text-center">{{scenario.name}}</span>
                    </div>
                </div>

                <div class="justified bold" v-if="value !== null">
                    <ul>
                        <li v-for="item in value.description">
                            {{item}}
                        </li>
                    </ul>
                </div>

                <h4>Testbed: </h4>
                <div class="row ml-3">
                    <div class="testbed col-direction" :class="{'testbed-selected': testbedSelected === index}" @click="selectTestbed(index)" v-for="(testbed, index) in testbeds">
                        <img class="logo-sm mr-2" style="height: 55px" :src="testbedIcons[testbed.identifier]">
                    </div>
                </div>

                <div class="row">
                    <file-upload-simple :allow-upload="useOpenWSNFirmware" @click.native="useOpenWSNFirmware = false"></file-upload-simple>
                    <div class="testbed" style="position: relative" :class="{'testbed-selected': useOpenWSNFirmware}" @click="useOpenWSNFirmware = true">
                        <img class="logo-sm ml-2" style="position: absolute; bottom: 0; height: 55px" src="images/openwsn_cropped.png">
                    </div>
                </div>

                <button class="main-btn btn-width-full mt-2" v-if="scenarioSelected !== -1 && testbedSelected !== -1 && !dataFlowStarted" @click="processStart()" :disabled="processStarted">Start experiment</button>

                <button class="main-btn btn-width-full btn-danger mt-2" v-if="dataFlowStarted" @click="processTerminate()">Terminate experiment</button>

            </div>

            <div class="col-7">
                <d3-network style="height: 78%" :net-nodes="value.nodes" :net-links="value.links" :options="options" v-if="value !== null"/>
                <div class="row pl-3 pr-3 h-center v-center col-direction" v-if="processStarted && !dataFlowStarted">
                    <h3 class="primary pulse mb-0" v-if="!dataFlowStarted">Starting experiment...</h3>
                    <progress-bar
                            :nodes-reserved="nodesReserved"
                            :all-booted="allBooted"
                            :all-active="allActive"
                            :data-flow-started="dataFlowStarted"></progress-bar>
                </div>
                <div class="row h-center v-center col-direction mt-1" v-if="dataFlowStarted">
                    <h3 class="mt-0 mb-0" style="margin-bottom: 5px">Experiment started! <span class="pulse clickable" @click.prevent="scrollContent">Monitor the progress in real time</span></h3>
                    <i class="fas fa-check-circle fa-3x primary-light"></i>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
    import D3Network from 'vue-d3-network';
    import FileUploadSimple from './../reusables/FileUploadSimple.vue';

    const axios = require('axios');

    let thisComponent;

    export default {
        components: {
            D3Network,
            FileUploadSimple
        },

        data: function () {
            return {
                stepsCompleted: -1,

                processStarted: false,
                nodesReserved: false,
                dataFlowStarted: false,

                scenarios: [],
                scenarioSelected: -1,
                scenarioIcons: {
                    "home-automation": "fa-home",
                    "building-automation": "fa-building",
                    "industrial-monitoring": "fa-industry",
                },

                testbeds: [],
                testbedSelected: -1,
                testbedIcons: {
                    "iotlab": "https://www.iot-lab.info/wp-content/themes/alienship-1.2.5-child/templates/parts/fit-iotlab3.png",
                    "wilab": "images/w-ilabt.png"
                },
            
                useOpenWSNFirmware: true,

                multiselectOptions: [],
                
                value: {
                    nodes: [],
                    links: []
                },

                canvas: false,

                gatewayIcon: '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="24" height="32" viewBox="0 0 24 32"><path d="M12 30c-6.626 0-12-1.793-12-4 0-1.207 0-2.527 0-4 0-0.348 0.174-0.678 0.424-1 1.338 1.723 5.99 3 11.576 3s10.238-1.277 11.576-3c0.25 0.322 0.424 0.652 0.424 1 0 1.158 0 2.387 0 4 0 2.207-5.375 4-12 4zM12 22c-6.626 0-12-1.793-12-4 0-1.208 0-2.526 0-4 0-0.212 0.080-0.418 0.188-0.622v0c0.061-0.128 0.141-0.254 0.236-0.378 1.338 1.722 5.99 3 11.576 3s10.238-1.278 11.576-3c0.096 0.124 0.176 0.25 0.236 0.378v0c0.107 0.204 0.188 0.41 0.188 0.622 0 1.158 0 2.386 0 4 0 2.207-5.375 4-12 4zM12 14c-6.626 0-12-1.792-12-4 0-0.632 0-1.3 0-2 0-0.636 0-1.296 0-2 0-2.208 5.374-4 12-4s12 1.792 12 4c0 0.624 0 1.286 0 2 0 0.612 0 1.258 0 2 0 2.208-5.375 4-12 4zM12 4c-4.418 0-8 0.894-8 2s3.582 2 8 2 8-0.894 8-2-3.582-2-8-2z"></path></svg>'
            }
        },

        methods: {
            fetch(param) {
                axios.get('/api/general/' + param)
                    .then(function (response) {
                        thisComponent[param] = response.data;
                    })
                    .catch(function (error) {
                        console.log("Error: " + error);
                    });
            },

            fetchNodes() {
                if (this.scenarioSelected != -1 && this.testbedSelected != -1) {

                    let scenario = this.scenarios[this.scenarioSelected].identifier;
                    let testbed  = this.testbeds[this.testbedSelected].identifier;

                    axios.get('/api/general/nodes/' + scenario + '/' + testbed)
                        .then(function (response) {
                            let data = response.data;
                            data['nodes'].forEach(function(element) {
                                if (['area-controller', 'zone-controller', 'control-unit', 'gateway'].includes(element.role))
                                    element.svgSym = thisComponent.gatewayIcon;
                            });
                            thisComponent.value = data;
                            console.log(JSON.stringify(thisComponent.value));
                        })
                        .catch(function (error) {
                            console.log("Error: " + error);
                        });  
                }
            },

            scrollContent() {
                this.$eventHub.$emit('SCROLL', 'graphs');
            },

            selectScenario(ind) {
                this.scenarioSelected = ind;
                //this.value = this.multiselectOptions[this.scenarioSelected];
                this.fetchNodes();
            },
            selectTestbed(ind) {
                this.testbedSelected = ind;
                this.fetchNodes();
            },

            processStart() {
                axios.get('/api/start-exp')
                    .then(function (response) {
                        // handle success
                        console.log(response);
                    })
                    .catch(function (error) {
                        // handle error
                        console.log("Error: " + error);
                    })
                    .then(function () {
                        // always executed
                    });

                this.processStarted = true;

                let nodes = this.value['nodes'];
                let num = nodes.length;

                for (let i=0; i<num; i++) {
                    nodes[i]['_cssClass'] = 'node-loading';
                }
            },
            processTerminate() {
                axios.get('/api/terminate-exp')
                    .then(function (response) {
                        // handle success
                        console.log(response);
                    })
                    .catch(function (error) {
                        // handle error
                        console.log("Error: " + error);
                    })
                    .then(function () {
                        // always executed
                    });
            },

            markNode(node, field, value) {
                //booted, active, failed
                let nodes = this.value['nodes'];
                let num = nodes.length;

                for (let i=0; i<num; i++) {
                    if (nodes[i]['name'] === node) {
                        switch(field) {
                            case 'booted':
                                nodes[i]['booted'] = value;
                                nodes[i]['_cssClass'] = 'node-booted';
                                break;

                            case 'active':
                                nodes[i]['active'] = value;
                                nodes[i]['_cssClass'] = 'node-on';
                                break;

                            case 'failed':
                                nodes[i]['failed'] = value;
                                nodes[i]['_cssClass'] = 'node-failed';
                                break;
                        }
                    }
                }

            },
        },

        computed:{
            options(){
                let nodeSize;
                let force;

                nodeSize = 35;
                force    = 1500;

                return {
                    force: force,
                    size: {w:600, h:600},
                    nodeSize: nodeSize,
                    nodeLabels: true,
                    canvas: this.canvas
                }
            },

            allBooted() {
                let nodes = this.value['nodes'];
                let numOfBooted = 0;

                nodes.forEach(element => {
                    if (element['booted'])
                        numOfBooted++;
                });

                return numOfBooted === nodes.length;
            },
            bootFailed() { //Currently not used
                let nodes = this.value['nodes'];
                let hasFailed = false;

                nodes.forEach(element => {
                    if (element['failed'])
                        hasFailed = true;
                });

                return hasFailed;
            },
            allActive() {
                let nodes = this.value['nodes'];
                let numOfActive = 0;

                nodes.forEach(element => {
                    if (element['active'])
                        numOfActive++;
                });

                return numOfActive === nodes.length;
            }
        },

        created() {
            thisComponent = this;
        },

        mounted() {
            this.fetch('scenarios');
            this.fetch('testbeds');

            this.$eventHub.$on("RESERVATION_SUCCESS", payload => {
                thisComponent.nodesReserved = true
            });

            this.$eventHub.$on("NODE_BOOTED", payload => {
                thisComponent.markNode(payload, 'booted', true);
            });
            this.$eventHub.$on("BOOT_FAIL", payload => {
                thisComponent.markNode(payload, 'failed', true);
            });

            this.$eventHub.$on("NODE_ACTIVE", payload => {
                thisComponent.markNode(payload, 'active', true);
            });
            this.$eventHub.$on("NODE_ACTIVE_FAILED", payload => {
                thisComponent.markNode(payload, 'failed', true);
            });

            this.$eventHub.$on("LOG_MODIFICATION", payload => {
                thisComponent.dataFlowStarted = true;

                thisComponent.selectScenario(0);
                let nodes = thisComponent.value['nodes'];
                let num = nodes.length;

                for (let i=0; i<num; i++) {
                    nodes[i]['_cssClass'] = 'node-on';
                }
            });

            this.$eventHub.$on("EXP_TERMINATE", payload => {
                this.processStarted = false;
                this.nodesReserved = false;
                this.dataFlowStarted = false;

                let nodes = this.value['nodes'];
                let num = nodes.length;

                for (let i=0; i<num; i++) {
                    nodes[i]['_cssClass'] = 'node-off';
                }
            });
        }
    }
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
<style src="vue-d3-network/dist/vue-d3-network.css"></style>

<style scoped>
    .parent {
        height: 100vh;
        padding: 25px;
    }

    .scenario {
        color: rgba(200, 200, 200, .7);
        cursor: pointer;
        flex: 1;
        transition: 0.3s ease;
    }
    .scenario > span {
        margin-top: 5px;
    }
    .scenario-selected {
        color: #6699CC;
    }

    .testbed {
        cursor: pointer;
        transition: 0.3s ease;
    }
    .testbed:not(.testbed-selected) {
        filter: grayscale(100%) opacity(0.3);
    }
</style>

<style>
    .multiselect__option--highlight {
        background: #6699CC;
    }
</style>

<style>
    @keyframes loading {
        0% {fill: rgba(200, 200, 200, .7);}
        50% {fill: rgba(200, 200, 200, .3);}
        100% {fill: rgba(200, 200, 200, .7);}
    }

    /***** Role-related classes *****/
    .node {
        stroke-width: 3px;
    }
    .node:hover {
        stroke: rgb(220, 146, 2);
        fill: rgba(255, 197, 117);
        width: rgb(255, 180, 4);
        stroke-width: 4px;
    }
    .monitoring-sensor {
        stroke: rgb(75, 113, 147);
        fill: rgb(219, 226, 233);
    }
    .event-sensor {
        stroke: rgb(75, 113, 147);
        fill: rgb(129, 155, 179);
    }
    .actuator {
        stroke: rgb(75, 113, 147);
        fill: rgb(200, 200, 200);
    }
    .area-controller, .control-unit, .zone-controller, .gateway {
        stroke: rgb(75, 113, 147);
        fill: rgb(219, 226, 233);
        stroke-width: 2px;
    }
    .sensor {
        stroke: rgb(75, 113, 147);
        fill: rgb(219, 226, 233);
    }
    .bursty-sensor {
        stroke: rgb(75, 113, 147);
        fill: rgb(129, 155, 179);
    }
    /****/

    .node-off {
        stroke: rgba(100, 100, 100, .7);
        fill: rgba(200, 200, 200, .7);
        stroke-width: 3px;
        transition: fill .5s ease;
    }
    .node-loading {
        stroke: rgba(100, 100, 100, .7);
        fill: rgba(200, 200, 200, .7);
        stroke-width: 3px;
        transition: fill .5s ease;
        animation: loading 1s infinite;
    }
    .node-booted {
        stroke: rgba(102, 153, 204, 1);
        fill: rgba(200, 200, 200, .3);
        stroke-width: 3px;
        transition: fill .5s ease;
    }
    .node-on {
        stroke: rgba(66, 184, 131, 1);
        fill: rgba(200, 200, 200, .3);
        stroke-width: 3px;
        transition: fill .5s ease;
    }
    .node-fail {
        stroke: red;
        fill: rgba(200, 200, 200, .3);
        stroke-width: 3px;
        transition: fill .5s ease;
    }

    .node-join {
        stroke: rgba(66, 184, 131, 1);
        fill: rgba(122,205,168, 1);
        stroke-width: 3px;
        transition: fill .5s ease;
    }
    .dag-node-join {
        stroke: orange;
        fill: rgba(122,205,168, 1);
        stroke-width: 3px;
        transition: fill .5s ease;
    }

    /*.net {
        height: 78%;
    }*/
</style>