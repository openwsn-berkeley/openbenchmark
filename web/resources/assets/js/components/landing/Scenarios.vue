<template>
    <div class="parent">

        <modal name="alert-dialog" width="400px" height="170px">
            <div class="dialog-loader row h-center v-center" v-if="dialogLoader">
                <i class="fas fa-circle-notch fa-3x fa-spin"></i>
            </div>
            <span class="dialog-content" :class="{'dialog-content-disabled': dialogLoader}">
                <h3 class="dialog-title bold">{{dialog.title}}</h3>
                <div class="buttons row h-center" v-if="dialog.buttons.length === 2">
                    <button id="ok-btn" class="main-btn btn-small btn-width-half ml-1" @click="dialog.action" :disabled="dialogLoader">{{dialog.buttons[0]}}</button>
                    <button id="cancel-btn" class="main-btn btn-small btn-width-half btn-danger mr-1" @click="closeModal('alert-dialog')" :disabled="dialogLoader">{{dialog.buttons[1]}}</button>
                </div>
                <div class="buttons row v-center" v-if="dialog.buttons.length === 1">
                    <button class="main-btn btn-small" @click="closeModal('alert-dialog')" :disabled="dialogLoader">{{dialog.buttons[0]}}</button>
                </div>
            </span>
        </modal>

        <modal name="modal-progress-bar" width="90%" height="165px">
            <!-- Remains here temporarily. Will be moved later -->
            <div class="row h-center v-center col-direction mt-2" v-if="currentStep == 3">
                <h3 class="mt-0 mb-0" style="margin-bottom: 5px">Experiment started! <span class="pulse clickable" @click.prevent="scrollContent">Monitor the progress in real time</span></h3>
                <i class="fas fa-check-circle fa-3x primary-light"></i>
            </div>
        </modal>

        <modal name="testbed-pick">
            <div class="modal-content row col-direction h-center">
                <span class="bold align-left mt-1 ml-1">Select a testbed: </span>

                <div class="testbed mt-1" :class="{'testbed-selected': testbedSelected === index}" @click="selectTestbed(index)" v-for="(testbed, index) in testbeds">
                    <img class="logo-sm mb-1" style="height: 55px" :src="testbedIcons[testbed.identifier]">
                </div>

                <button class="modal-btn main-btn btn-small" @click="closeModal('testbed-pick')">OK</button>
            </div>
        </modal>

        <modal name="scenario-pick">
            <div class="modal-content row col-direction h-center">
                <span class="bold align-left mt-1 ml-1 mb-1">Select a scenario: </span>

                <div class="scenario mb-1 ml-3" :class="{'scenario-selected': scenarioSelected === index}" @click="selectScenario(index)" v-for="(scenario, index) in scenarios">
                    <div class="row" style="width:100%">
                        <div class="row col-2 v-center">
                            <i class="fas fa-2x" :class="scenarioIcons[scenario.identifier]"></i>
                        </div>
                        <div class="row col-10 h-center">
                            <span class="dark-gray ml-1" :class="{'scenario-selected': scenarioSelected === index}">{{scenario.name}}</span>
                        </div>
                    </div>
                </div>

                <button class="modal-btn main-btn btn-small" @click="closeModal('scenario-pick')">OK</button>
            </div>
        </modal>

        <modal name="firmware-pick">
            <div class="modal-content row col-direction h-center">
                <span class="bold align-left mt-1 ml-1 mb-1">Upload firmware (or choose the default): </span>
                
                <div class="row-direction v-center mt-1" style="width: 100%">
                    <file-upload-simple :allow-upload="useOpenWSNFirmware" @click.native="useOpenWSNFirmware = false"></file-upload-simple>
                    <div class="testbed row ml-1 h-center" :class="{'testbed-selected': useOpenWSNFirmware}" @click="revertToDefaultFw()">
                        <img class="logo-sm" style="height: 55px" src="images/openwsn_cropped.png">
                    </div>
                </div>

                <button class="modal-btn main-btn btn-small" @click="closeModal('firmware-pick')">OK</button>
            </div>
        </modal>

        <div class="row" style="height: 80vh">
            <div class="relative card bordered col-5 mr-1 mt-1">
                
                <div class="row">
                    <div class="col-2 pl-1 col-direction">
                        <h4>Scenario: </h4>
                        <span v-if="scenarioSelected == -1">Choose scenario</span>
                        <span class="bold" v-else>{{scenarios[scenarioSelected].name}}</span>
                        <span class="clickable primary-light" @click="showModal('scenario-pick')">Change</span>
                    </div>
                    <div class="col-2 pl-1 col-direction">
                        <h4>Testbed: </h4>
                        <span v-if="testbedSelected == -1">Choose testbed</span>
                        <span class="bold" v-else>{{testbeds[testbedSelected].name}}</span>
                        <span class="clickable primary-light" @click="showModal('testbed-pick')">Change</span>
                    </div>
                </div>

                <div class="separator gray-gradient ml-1 mt-2 mb-1"/>

                <div class="row">
                    <div class="col-2 pl-1 col-direction">
                        <h4>Firmware: </h4>
                        <span v-if="firmware === undefined">Default OpenWSN firmware</span>
                        <span class="bold" v-else>{{firmware.origName}}</span>
                        <span class="clickable primary-light" @click="showModal('firmware-pick')">Change</span>
                    </div>
                </div>

                <div class="separator gray-gradient ml-1 mt-2 mb-1"/>

                <h4 class="mt-2 mb-1 ml-1">Selected node: </h4>
                <div class="row card pl-1 pr-1 row-direction" v-if="selectedNode.length !== 0">
                    <div class="row col-direction">
                        <span class="mt-0 node-property">OpenBenchmark ID:</span>
                        <span class="mt-0 node-property">Testbed ID:</span>
                        <span class="mt-0 node-property">Transmission power:</span>
                        <span class="mt-0 node-property">Role:</span>
                    </div>
                    <div class="row col-direction pl-2">
                        <span class="bold node-property">{{selectedNode.id}}</span>
                        <span class="bold node-property">{{selectedNode.name}}</span>
                        <span class="bold node-property">{{selectedNode.transmissionPower}}</span>
                        <span class="bold node-property">{{selectedNode.roleFull}}</span>
                    </div>
                </div>
                <div class="row card pl-1 pr-1 row-direction" v-else>
                    <span>No node selected</span>
                </div>

                <div class="buttons row h-center">
                    <!-- Condition for enabling the start button -->
                    <!-- v-if="scenarioSelected !== -1 && testbedSelected !== -1" -->
                    <!-- Condition for disabling the start button -->
                    <!-- :disabled="currentStep > -2 -->
                    <button id="start-btn" class="main-btn btn-small btn-width-half ml-1"  @click="processStart()" :disabled="currentStep > -2">Start</button>
                    <button id="terminate-btn" class="main-btn btn-small btn-width-half btn-danger mr-1" @click="showDialog('termination')" :disabled="currentStep === -2">Terminate</button>
                </div>

            </div>

            <div class="card bordered col-7 mt-1 row-direction h-center v-center">
                <d3-network 
                    :net-nodes="value.nodes" 
                    :net-links="value.links" 
                    :options="options" 
                    v-if="scenarioSelected !== -1 && testbedSelected !== -1" @node-click="selectNode"/>
                <i class="fas fa-project-diagram fa-5x light-gray" v-else/>
            </div>

        </div>

        <div class="row ml-1 mt-1 mr-2 h-center v-center" v-if="currentStep > -2">
            <progress-bar :current-step="currentStep"></progress-bar>
        </div>

    </div>
</template>

<script>
    import D3Network from 'vue-d3-network';
    import FileUploadSimple from './../reusables/FileUploadSimple.vue';

    const axios = require('axios');

    let thisComponent;

    export default {
        props: ['experiment-id'],

        components: {
            D3Network,
            FileUploadSimple
        },

        data: function () {
            return {
                dialog: {
                    "title": "",
                    "buttons": []
                },
                dialogLoader: false,

                scenarios: [],
                scenarioSelected: -1,
                scenarioIcons: {
                    "demo-scenario": "fa-laptop",
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

                selectedNode: [],

                gatewayIcon: '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="24" height="32" viewBox="0 0 24 32"><path d="M12 30c-6.626 0-12-1.793-12-4 0-1.207 0-2.527 0-4 0-0.348 0.174-0.678 0.424-1 1.338 1.723 5.99 3 11.576 3s10.238-1.277 11.576-3c0.25 0.322 0.424 0.652 0.424 1 0 1.158 0 2.387 0 4 0 2.207-5.375 4-12 4zM12 22c-6.626 0-12-1.793-12-4 0-1.208 0-2.526 0-4 0-0.212 0.080-0.418 0.188-0.622v0c0.061-0.128 0.141-0.254 0.236-0.378 1.338 1.722 5.99 3 11.576 3s10.238-1.278 11.576-3c0.096 0.124 0.176 0.25 0.236 0.378v0c0.107 0.204 0.188 0.41 0.188 0.622 0 1.158 0 2.386 0 4 0 2.207-5.375 4-12 4zM12 14c-6.626 0-12-1.792-12-4 0-0.632 0-1.3 0-2 0-0.636 0-1.296 0-2 0-2.208 5.374-4 12-4s12 1.792 12 4c0 0.624 0 1.286 0 2 0 0.612 0 1.258 0 2 0 2.208-5.375 4-12 4zM12 4c-4.418 0-8 0.894-8 2s3.582 2 8 2 8-0.894 8-2-3.582-2-8-2z"></path></svg>',

                workflowSteps: [
                    "provisioned",
                    "flashed",
                    "network-configured",
                    "orchestration-started"
                ],

                currentStep: -2,   //If -2, process has not started yet; -1: process started, waiting for notifications
                taskFailed: false,

                firmware: undefined
                    //firmware: ...,
                    //firmware_orig_name: ...
            }
        },

        methods: {
            showDialog(key) {
                let dialogs = {
                    "termination": {
                        "title": "Are you sure you want to terminate the experiment?", 
                        "buttons": ["YES", "NO"],
                        "action": this.processTerminateDialogAction
                    },
                    "missing-params": {
                        "title": "You must select a testbed and a scenario",
                        "buttons": ["OK"],
                        "action": undefined
                    }
                }
                this.dialog = dialogs[key]
                this.showModal('alert-dialog')
            },

            showModal(name) {
                this.$modal.show(name)
            },
            closeModal(name) {
                this.$modal.hide(name)
            },

            fetch(param) {
                axios.get('/api/general/' + param)
                    .then(function (response) {
                        thisComponent[param] = response.data;
                    })
                    .catch(function (error) {
                        console.log(error);
                    })
                    .then(function() {
                        if (thisComponent.scenarios.length > 0 && thisComponent.testbeds.length > 0 && thisComponent.experimentId !== undefined) {
                            thisComponent.fetchConfiguration();
                        }
                    });
            },

            getParamIndex(arrayName, identifier) {
                let returnIndex = -1;

                thisComponent[arrayName].forEach(function(element, index) {
                    if (element.identifier === identifier) {
                        returnIndex = index;
                    }
                });

                return returnIndex;
            },

            fetchConfiguration() {
                axios.get('/api/experiment/' + thisComponent.experimentId)
                    .then(function (response) {
                            if (response.data.length > 0) {
                                let experiment = response.data[0];
                                
                                thisComponent.scenarioSelected = thisComponent.getParamIndex('scenarios', experiment.scenario);
                                thisComponent.testbedSelected  = thisComponent.getParamIndex('testbeds', experiment.testbed);

                                thisComponent.fetchNodes();
                            }
                        })
                        .catch(function (error) {
                            console.log(error);
                        })
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
                            thisComponent.$eventHub.$emit('NODES_FETCHED', data);
                        })
                        .catch(function (error) {
                            console.log("Error: " + error);
                        });  
                }
            },

            selectNode(event, nodeObject) {
                this.value.nodes.forEach(function(element) {
                    if (element === nodeObject) {
                        thisComponent.selectedNode = element;
                        element._cssClass += " selected";
                    } else {
                        element._cssClass = element.defaultCssClass;
                    }
                });
                nodeObject._cssClass += " selected";
            },

            scrollContent() {
                this.$eventHub.$emit('SCROLL', 'graphs');
            },

            selectScenario(ind) {
                this.scenarioSelected = ind;
                this.fetchNodes();
            },
            selectTestbed(ind) {
                this.testbedSelected = ind;
                this.fetchNodes();
            },

            processStart() {
                if (this.scenarioSelected === -1 || this.testbedSelected === -1) {
                    this.showDialog('missing-params')
                } else {
                    let scenario = this.scenarios[this.scenarioSelected].identifier
                    let testbed  = this.testbeds[this.testbedSelected].identifier
                    
                    let route = '/api/start/' + scenario + '/' + testbed + '/false'

                    if (this.firmware !== undefined) {
                        route += '/' + this.firmware.name
                    }

                    this.currentStep = -1

                    axios.get(route) 
                        .then(function (response) {
                            // handle success
                            console.log(response)
                        })
                        .catch(function (error) {
                            // handle error
                            console.log(error)
                            thisComponent.currentStep = -2
                        })

                    axios.post('/api/store', {
                            scenario         : scenario,
                            testbed          : testbed
                        }) 
                        .then(function (response) {
                            // handle success
                            console.log(response);
                        })
                        .catch(function (error) {
                            // handle error
                            console.log(error);
                        })
                }
            },
            processTerminate() {
                axios.get('/api/terminate')
                    .then(function (response) {
                        // handle success
                        console.log(response);
                    })
                    .catch(function (error) {
                        // handle error
                        console.log("Error: " + error);
                    })
                    .then(function () {
                        // executes always
                    });
            },

            processTerminateDialogAction() {
                this.dialogLoader = true
                this.processTerminate()
            },

            revertToDefaultFw() {
                this.useOpenWSNFirmware = true
                this.firmware = undefined
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

            /*** MQTT Configuration ***/
            subscribe() {
                let interval = setInterval( function() {
                    if (thisComponent.$mqttClient.subscribe() !== "") {
                        console.log("Retrying subscription in 1s...") 
                    } else {
                        clearInterval(interval)
                    }
                }, 1000);  
            },

            parseMqttEvent(payload) {
                let payloadObj = JSON.parse(payload)
                let type    = payloadObj["type"]
                let step    = payloadObj["content"]["step"]
                let success = payloadObj["content"]["success"]

                if (type == "notification" && success) {
                    this.currentStep = (step !== "terminated") ? this.workflowSteps.indexOf(step) : -2

                    if (step === "terminated") {
                        thisComponent.dialogLoader = false
                        thisComponent.closeModal('alert-dialog')
                    }
                } else if (type == "notification" && !success) {
                    this.currentStep = -2
                    this.taskFailed = true
                }

                console.log(this.currentStep);
            },

        },

        computed:{
            options(){
                let nodeSize;
                let force;

                nodeSize = 30;
                force = 800;

                return {
                    force: force,
                    size: {w:600, h:550},
                    nodeSize: nodeSize,
                    nodeLabels: true,
                    canvas: false
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

            this.$eventHub.$on("openbenchmark/1/notifications", payload => {
                thisComponent.parseMqttEvent(payload);
            });

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

            this.$eventHub.$on("FIRMWARE_UPLOADED", payload => {
                thisComponent.firmware = payload
                console.log(JSON.stringify(thisComponent.firmware))
                console.log("Firmware successfully uploaded: " + thisComponent.firmware.origName);
            });
        }
    }
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
<style src="vue-d3-network/dist/vue-d3-network.css"></style>

<style scoped>
    .parent {
        height: 100vh;
        padding-left: 25px;
        padding-right: 25px;
        background-color: #eeeeee;
    }

    .scenario {
        width: 50%;
        color: rgba(200, 200, 200, .7);
        cursor: pointer;
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

    .buttons {
        position: absolute;
        bottom: 15px;
        width: 100%
    }
    #start-btn, #ok-btn {
        margin-right: 7px;
    }
    #terminate-btn, #cancel-btn {
        margin-left: 7px;
    }

    .dialog-title {
        position: absolute;
        top: 15px;
        left: 50%;
        transform: translateX(-50%);
        width: 70%;
        text-align: center;
    }
    .dialog-loader {
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.7);
        color: #1f6fb2;
    }
    .dialog-content {

    }
    .dialog-content-disabled {
        opacity: 0.3
    }

    .node-property {
        margin-bottom: 5px;
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
    .node:hover, .selected {
        stroke: rgb(220, 146, 2);
        fill: rgba(255, 197, 117) !important;
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

    .net, .net-svg {
        width: 100% !important;
        height: 100% !important;
    }
</style>