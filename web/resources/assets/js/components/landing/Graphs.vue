<template>
    <div class="top-content">
        <div class="row" style="height: 100%">
            <div class="col-direction ml-1 mr-1 col-4" style="height: 100%;">

                <div class="node-card card mb-1 col-direction">
                    <span class="bold mt-1 ml-1">Nodes: </span>
                    <div v-bar>   
                        <div class="ml-1">            
                            <label class="radio" v-for="key in Object.keys(dataset)" @click="selectedNodeKey = key">
                                <input type="radio" name="r" :value="key" checked>
                                <span>{{key}}</span>
                            </label>
                        </div>
                    </div>
                </div>

                <div class="card col-direction" style="width: 100%; height: 50%;">
                    <span class="mt-1" v-for="key in Object.keys(generalData)">
                        <span class="bold ml-1 mr-1">{{generalDataTitles[key]}}:</span> {{generalData[key]}}
                    </span>
                </div>

            </div>
            <div class="card col-direction ml-1 mr-1 pt-1 col-8 wrap">
                
                <div v-bar>   
                    <div>
                        <span v-for="key in Object.keys(dataset)">
                            <span v-if="key === selectedNodeKey">
                                <span v-for="label in Object.keys(dataset[key])">
                                    <line-chart class="chart ml-3 mr-3"
                                                :label="label"
                                                :x-axis="dataset[key][label]['timestamp']"
                                                :y-axis="dataset[key][label]['value']"
                                                :width="700"
                                                :height="300"></line-chart>
                                </span>
                            </span>
                        </span>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<script>
    import LineChart from './../charts/LineChart.vue'
    import D3Network from 'vue-d3-network';
    import Paho from 'paho-mqtt';

    const axios = require('axios');

    let thisComponent;

    export default {
        components: {
            LineChart,
            D3Network
        },

        props: ['experiment-id'],

        data: function () {
            return {
                //client: new Paho.Client("broker.mqttdashboard.com", Number(8000), "webBrowserClient"),

                expStartTimestamp: -1,
                dataPerChart: 20,

                value: {
                    nodes: [],
                    links: []
                },

                selectedNodeKey: "",

                generalData: {
                    /* EXAMPLE ITEM: 
                    "networkFormationTime": 1560761378.408148, 
                    ... 
                    */
                },
                generalDataTitles: {
                    "networkFormationTime": "Network formation",
                    "syncronizationPhase" : "Synchronization",
                    "secureJoinPhase"     : "Secure join phase"
                },

                dataset: {
                    /* EXAMPLE ITEM:
                    "node-a8-106": {
                        "latency": {
                            "timestamp":[15388500.87438082,15388500.905358542,15388500.935934938,15388500.966604061,15388500.99736588,15388501.01802762,15388501.04889744],
                            "value":[0,0,0,0,0,0,0]
                        },
                        "reliabilty": {
                            "timestamp":[15388500.987090621],
                            "value":[100]
                        }
                    },
                    ...
                    */
                }
            }
        },

        methods: {
            loadData() {
                if (this.experimentId !== undefined) {
                    this.fetchDataFromLogs()
                }
            },

            fetchDataFromLogs(experimentId) {
                axios.get('/api/logs/data-fetch/' + this.experimentId)
                    .then(function (response) {
                        thisComponent.generalData = response.data.message.general_data
                        thisComponent.dataset = response.data.message.data
                    })
                    .catch(function (error) {
                        console.log(error);
                    })
                    .then(function() {
                        
                    });
            },

            relativeTimestampParse(timestamp) {
                //Converts relative timestamp to milliseconds or seconds since the experiment start
                //Timestamp in units of timeslots. Each timeslot is 10ms
                return (timestamp / 1000000).toFixed(2);
            },

            createBlankDataset() {
                //Creates a blank dataset for all the existing nodes in the 'nodes' field
                this.value.nodes.forEach(element => {
                    this.dataset.push({
                        id: element.name,
                        eui64: '',
                        nodeData: []
                    })
                });
            },

            appendNodeData(id, label, xVal, yVal) {
                //Appends to 'xAxis' and 'yAxis' of a 'nodeData' (of the node with the given 'eui64') element with the corresponding label
                //Creates new 'nodeData' element if the label does not exist
                if (id !== undefined) {
                    let node = this.getNodeByProperty('id', id);

                    console.log("Fetching node: " + id);
        
                    let num = node.nodeData.length;
                    let valueAppended = false;

                    for (let i=0; i<num; i++) {
                        if (node.nodeData[i].label === label) {
                            node.nodeData[i].xAxis.push(xVal);
                            node.nodeData[i].yAxis.push(yVal);

                            valueAppended = true;

                            if (node.nodeData[i].xAxis.length > this.dataPerChart) {
                                node.nodeData[i].xAxis.shift();
                                node.nodeData[i].yAxis.shift();
                            }
                        }
                    }

                    if (!valueAppended) {
                        node.nodeData.push({
                            label: label,
                            xAxis: [xVal],
                            yAxis: [yVal]
                        });
                    }
                } else {
                    this.updateGeneralData(label, xVal);
                }
            },

            updateGeneralData(label, xVal) {
                let hasElement = false;

                for (let i=0; i<this.generalData.length; i++) {
                    if (this.generalData[i]["identifier"] === label) {
                        this.generalData[i]["value"] = xVal;
                        hasElement = true;
                        break;    
                    } 
                }

                if (!hasElement && this.generalDataTitles.hasOwnProperty(label)) {
                    this.generalData.push({
                        "identifier": label,
                        "value": xVal
                    });
                }
            },

            nodeClick(event, nodeObject) {
                this.value.nodes.forEach(function(element) {
                    if (element === nodeObject) {
                        thisComponent.selectedNode = element;
                        element._cssClass += " selected";
                    } else {
                        element._cssClass = element.defaultCssClass;
                    }
                });
                nodeObject._cssClass += " selected";
                this.selectNodeData(nodeObject);
            },

            selectNodeData(node) {
                //Put dataset element with the given 'id' in 'selectedNode' variable (used for filling the UI with the data)
                this.selectedNode = node;
                console.log("Currently showing: " + JSON.stringify(this.getNodeByProperty('id', this.selectedNode)));
            },

            getNodeByProperty(property, val) {
                //Searches the dataset for an element with the given property with the given val
                let num = this.dataset.length;
                let result = {};

                for (let i=0; i<num; i++) {
                    if (property === 'id' && this.dataset[i].id === val) {
                        result = this.dataset[i];
                    } else if (property === 'eui64' && this.dataset[i].eui64 === val) {
                        result = this.dataset[i];
                    }
                }

                return result;
            },

            parseLogData(obj) {
                let id    = obj.node_id;
                let label = obj.kpi;
                let xVal  = obj.timestamp;
                let yVal  = obj.value;

                console.log("Parsing data: " + label + " " + yVal + " id: " + id);

                this.appendNodeData(id, label, this.timestampDiff(xVal), parseFloat(yVal));
            },

            timestampDiff(stmp) {
                let timestamp = stmp*1000;
                console.log("Timestamp: " + this.expStartTimestamp + "; Stmp: " + timestamp);
                return this.getDuration(new Date(this.expStartTimestamp), new Date(timestamp)).toString();
            },

            getDuration(d1, d2) {
                let d3 = new Date(d2 - d1);
                let d0 = new Date(0);

                return {
                    getHours: function(){
                        return d3.getHours() - d0.getHours();
                    },
                    getMinutes: function(){
                        return d3.getMinutes() - d0.getMinutes();
                    },
                    getSeconds: function(){
                        return d3.getSeconds() - d0.getSeconds();
                    },
                    getMilliseconds: function() {
                        return d3.getMilliseconds() - d0.getMilliseconds();
                    },
                    toString: function(){
                        return this.getMinutes() + ":" +
                            this.getSeconds() + ":" +
                            this.getMilliseconds();
                    },
                };
            },

            clone(obj) {
                if (null === obj || "object" !== typeof obj) return obj;
                let copy = obj.constructor();
                for (let attr in obj) {
                    if (obj.hasOwnProperty(attr)) copy[attr] = obj[attr];
                }
                return copy;
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
            onConnect() {
                // Once a connection has been made, make a subscription and send a message.
                //console.log("onConnect");
                //this.client.subscribe("browser/event");
                //let message = new Paho.Message("Browser connected to MQTT!");
                //message.destinationName = "browser/message";
                //this.client.send(message);
            },
            onConnectionLost(responseObject) {
                //if (responseObject.errorCode !== 0)
                 //   console.log("onConnectionLost: " + responseObject.errorMessage);
            },
            onMessageArrived(message) {
                //console.log("onMessageArrived: " + message.payloadString);
            },

            parseMqttEvent(payload) {
                let payloadObj = JSON.parse(payload)
                let type       = payloadObj["type"]

                if (type == "kpi") {
                    this.parseLogData(payloadObj["content"])
                }
            }

        },

        computed:{
            options() {
                return {
                    force: 500,
                    size: {w:350, h:320},
                    nodeSize: 20,
                    nodeLabels: true,
                    canvas: false
                }
            },
            currentData() {
                let currentNode = this.getNodeByProperty('id', this.selectedNode.id);
                return {
                    id:    currentNode.id,
                    eui64: currentNode.eui64,
                    isDag: currentNode.isDag
                }
            }
        },

        mounted() {
            this.subscribe();

            this.loadData();

            this.$eventHub.$on("MQTT", payload => {
                thisComponent.parseMqttEvent(payload);
            });

            this.$eventHub.$on("NODES_FETCHED", payload => {
                thisComponent.value = thisComponent.clone(payload);
                this.createBlankDataset();
            });

            this.$eventHub.$on("LOG_MODIFICATION", payload => {
                thisComponent.parseLogData(payload);
            });
        },

        created() {
            thisComponent = this;
            this.expStartTimestamp = new Date().valueOf();
        }
    }

</script>

<style scoped>
    .top-content {
        height: 100%;
        padding: 25px;
        background-color: #eeeeee;
    }
    .chart {
        width: 100%;
        height: 300px;
    }

    .node-card {
        width: 100%; 
        height: 50%;
    }

    .data-row {
        margin-top: 10px;
    }
</style>

<style>
    canvas {
        position: relative;
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
</style>