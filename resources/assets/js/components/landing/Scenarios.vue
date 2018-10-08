<template>
    <div class="parent">
        <div class="row">
            <div class="col-5 pr-5 pl-5">
                <h4>Choose a scenario: </h4>
                <div class="row">
                    <div class="scenario col-direction" :class="{'scenario-selected': scenarioSelected === 0}" @click="selectScenario(0)">
                        <i class="fas fa-desktop fa-3x text-center"></i>
                        <span class="text-center">Demo</span>
                    </div>
                    <div class="scenario col-direction" :class="{'scenario-selected': scenarioSelected === 1}" @click="selectScenario(1)">
                        <i class="fas fa-building fa-3x text-center"></i>
                        <span class="text-center">Smart office</span>
                    </div>
                    <div class="scenario col-direction" :class="{'scenario-selected': scenarioSelected === 2}" @click="selectScenario(2)">
                        <i class="fas fa-industry fa-3x text-center"></i>
                        <span class="text-center">Smart factory</span>
                    </div>
                </div>
                <div class="justified bold" v-if="value !== null">
                    <ul>
                        <li v-for="item in value.description">
                            {{item}}
                        </li>
                    </ul>
                </div>
                <h4>Choose a testbed: </h4>
                <div class="row ml-3">
                    <div class="testbed col-direction" :class="{'testbed-selected': testbedSelected === 0}" @click="selectTestbed(0)">
                        <img class="logo-sm mr-2" style="height: 55px" src="https://www.iot-lab.info/wp-content/themes/alienship-1.2.5-child/templates/parts/fit-iotlab3.png">
                    </div>
                    <div class="testbed col-direction" :class="{'testbed-selected': testbedSelected === 1}" @click="selectTestbed(1)">
                        <img class="logo-sm mr-2" style="height: 55px" src="images/w-ilabt.png">
                    </div>
                </div>
                <file-upload-simple></file-upload-simple>
                <button class="main-btn btn-width-full mt-2" v-if="scenarioSelected !== -1 && testbedSelected !== -1" @click="processStart()">Start experiment</button>
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

                scenarioSelected: -1,
                testbedSelected: -1,

                value: null,
                multiselectOptions: [
                    {
                        name: 'Demo',
                        description: [
                            'Number of nodes: 3',
                            'Traffic pattern: Periodic, 10 s',
                            'Transmission power: 0 dBm',
                            'Interference: None'
                        ],
                        nodes: [
                            { id: 1, name: 'node-a8-106', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 2, name: 'node-a8-107', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            //{ id: 3, name:'orange node', _color: 'orange' },
                            //{ id: 4, _color: '#0022ff'},
                            { id: 3, name: 'node-a8-108', _cssClass: 'node-off', booted: false, failed: false, active: false},
                        ],
                        links: [
                            { sid: 1, tid: 2 },
                            { sid: 2, tid: 3 },
                        ],
                    },
                    {
                        name: 'Smart office',
                        description: [
                            'Number of nodes: 5',
                            'Traffic pattern: Periodic, 10 s',
                            'Transmission power: 0 dBm',
                            'Interference: None'
                        ],
                        nodes: [
                            { id: 1, name: 'node-a8-106', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 2, name: 'node-a8-107', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 3, name: 'node-a8-108', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 4, name: 'node-a8-109', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 5, name: 'node-a8-110', _cssClass: 'node-off', booted: false, failed: false, active: false},
                        ],
                        links: [
                            { sid: 1, tid: 2 },
                            { sid: 2, tid: 3 },
                            { sid: 3, tid: 4 },
                            { sid: 3, tid: 5 },
                        ],
                    },

                    {
                        name: 'Smart factory',
                        description: [
                            'Number of nodes: 10',
                            'Traffic pattern: Periodic, 10 s',
                            'Transmission power: 0 dBm',
                            'Interference: None'
                        ],
                        nodes: [
                            { id: 1, name: 'node-a8-106', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 2, name: 'node-a8-107', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 3, name: 'node-a8-108', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 4, name: 'node-a8-109', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 5, name: 'node-a8-110', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 6, name: 'node-a8-111', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 7, name: 'node-a8-112', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 8, name: 'node-a8-113', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 9, name: 'node-a8-114', _cssClass: 'node-off', booted: false, failed: false, active: false},
                            { id: 10, name: 'node-a8-115', _cssClass: 'node-off', booted: false, failed: false, active: false},
                        ],
                        links: [
                            { sid: 1, tid: 2 },
                            { sid: 2, tid: 3 },
                            { sid: 3, tid: 4 },
                            { sid: 3, tid: 5 },
                            { sid: 3, tid: 6 },
                            { sid: 6, tid: 7 },
                            { sid: 6, tid: 8 },
                            { sid: 8, tid: 9 },
                            { sid: 9, tid: 10 },
                        ],
                    }
                ],

                nodeSize:35,
                canvas:false
            }
        },

        methods: {
            scrollContent() {
                this.$eventHub.$emit('SCROLL', 'graphs');
            },

            selectScenario(ind) {
                this.scenarioSelected = ind;
                this.value = this.multiselectOptions[this.scenarioSelected];
            },
            selectTestbed(ind) {
                this.testbedSelected = ind;
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

            markNode(node, field, value) {
                //booted, active, failed
                let nodes = this.value['nodes'];
                let num = nodes.length;

                for (let i=0; i<num; i++) {
                    if (nodes[i]['name'] === node) {
                        switch(field) {
                            case 'booted':
                                nodes[i]['booted'] = value;
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
                return{
                    force: 3000,
                    size: {w:600, h:450},
                    nodeSize: this.nodeSize,
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
                thisComponent.dataFlowStarted = true
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