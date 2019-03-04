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

                canvas: false
            }
        },

        methods: {
            fetch(param) {
                axios.get('/api/general/' + param)
                    .then(function (response) {
                        thisComponent[param] = response.data;
                        if (thisComponent.testbeds.length > 0 && thisComponent.scenarios.length > 0)
                            thisComponent.fetch('nodes');
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
                            /*thisComponent.multiselectOptions.push({
                                'nodes': response.data
                            });*/
                            thisComponent.value = response.data;
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

            /*simulateExpStartup() {
                console.log("Simulation started");
                this.stepsCompleted++;

                let nodeNum = thisComponent.value.nodes.length;
                for (let i=0; i<nodeNum; i++) {
                    thisComponent.value.nodes[i]._cssClass = 'node-loading';
                }

                let sim = setInterval(function() {
                    thisComponent.stepsCompleted++;
                    console.log("Steps completed: " + thisComponent.stepsCompleted);

                    if (thisComponent.stepsCompleted === 4) {
                        clearInterval(sim);

                        let nodeNum = thisComponent.value.nodes.length;

                        for (let i=0; i<nodeNum; i++) {
                            thisComponent.sleep(1000*(i+1)).then(() => {
                                    thisComponent.value.nodes[i]._cssClass = 'node-on';

                                if (i === nodeNum-1)
                                    thisComponent.sleep(500).then(() => {
                                        thisComponent.stepsCompleted++;
                                    });
                            });
                        }
                    }

                }, 2000);
            },

            sleep(time) {
                return new Promise(resolve => setTimeout(resolve, time));
            }*/
        },

        computed:{
            options(){
                let nodeSize;
                let force;

                nodeSize = 35;
                force    = 1500;

                /*if (this.value.name === "Demo") {
                    nodeSize = 35;
                    force = 3000;
                } else if (this.value.name === "Smart office") {
                    nodeSize = 25;
                    force = 1000;
                } else {
                    nodeSize = 25;
                    force = 500;
                }*/

                return{
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