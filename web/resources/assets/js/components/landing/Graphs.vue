<template>
    <div class="top-content">
        
        <modal name="file-download">
            <div class="modal-content row col-direction h-center">
                <span class="bold align-left mt-1 ml-1">Choose a log file to download: </span>
                <div class="col-direction mt-1">
                    <label class="radio">
                        <input type="radio" name="log-file" @click="markFileType('kpi-json')" :value="'cached_kpi_' + experimentId + '.json'" checked>
                        <span>cached_kpi_{{experimentId}}.json</span>
                    </label>
                    <label class="radio">
                        <input type="radio" name="log-file" @click="markFileType('kpi')" :value="'kpi_' + experimentId + '.log'">
                        <span>kpi_{{experimentId}}.log</span>
                    </label>
                    <label class="radio">
                        <input type="radio" name="log-file" @click="markFileType('raw')" :value="'raw_' + experimentId + '.log'">
                        <span>raw_{{experimentId}}.log</span>
                    </label>
                </div>
                <a id="file-download-anchor" style="display: hidden"/>
                <button class="modal-btn main-btn btn-small" @click="downloadFile()">DOWNLOAD</button>
            </div>
        </modal>

        <div class="row" style="height: 100%">
            <div class="col-direction ml-1 mr-1 col-4" style="height: 100%;">

                <div class="node-card card bordered mb-1 col-direction">
                    <span class="bold mt-1 ml-1">Nodes: </span>
                    <div v-bar>   
                        <div class="ml-1">            
                            <label class="radio" v-for="key in Object.keys(dataset)" @click="selectedNodeKey = key">
                                <input type="radio" name="r" :value="key">
                                <span>{{key}}</span>
                            </label>
                        </div>
                    </div>
                </div>

                <div class="card col-direction bordered relative" style="width: 100%; height: 50%;">
                    <span class="mt-1" v-for="key in Object.keys(generalData)">
                        <span class="ml-1 mr-1">{{generalDataTitles[key]}}: <span class="bold">{{generalData[key]}}</span></span>
                    </span>

                    <i id="file-download" class="fas fa-file-download fa-2x clickable" @click="showModal('file-download')" v-if="experimentId !== undefined"></i>
                </div>

            </div>
            <div class="card col-direction bordered ml-1 mr-1 pt-1 pb-1 col-8 wrap v-center h-center">
                
                <div v-bar v-if="selectedNodeKey !== ''">   
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

                <i class="fas fa-chart-area fa-9x light-gray" v-else/>

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

                logType: "kpi-json",

                expStartTimestamp: -1,
                dataPerChart: 20,

                value: {
                    nodes: [],
                    links: []
                },

                selectedNodeKey: "",

                headerData: {},

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
                            "value":[0,0.5,1,0.75,0.85,0.8,0.9]
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
            /*** Parse data from the logs ***/
            showModal(name) {
                this.$modal.show(name)
            },

            closeModal(name) {
                this.$modal.hide(name)
            },

            loadData() {
                this.fetchDataFromLogs()
            },

            markFileType(fileType) {
                this.logType = fileType;
            },

            downloadFile() {
                let downloadUrl = '/api/download/' + thisComponent.experimentId + '/' + thisComponent.logType
                let fileDownloadAnchor = document.getElementById("file-download-anchor")

                fileDownloadAnchor.setAttribute('href', downloadUrl)

                fileDownloadAnchor.click()
                this.closeModal('file-download')
                this.logType = "kpi-json"
            },

            fetchDataFromLogs(experimentId) {
                axios.get('/api/logs/data-fetch/' + this.experimentId)
                    .then(function (response) {
                        thisComponent.headerData = response.data.message.header
                        thisComponent.generalData = response.data.message.general_data
                        thisComponent.dataset = response.data.message.data
                        thisComponent.$eventHub.$emit('LOG_DATA_FETCHED', thisComponent.headerData);
                    })
                    .catch(function (error) {
                        console.log(error);
                    })
                    .then(function() {
                        
                    });
            },
            /*** ***/

            /*** Parse data from MQTT topic ***/
            appendNodeData(id, label, timestamp, value) {
                if (id !== undefined) {
                    let newObj = this.clone(this.dataset)

                    if ( !(id in newObj) ) 
                        newObj[id] = {}

                    if ( !(label in newObj[id]) )
                        newObj[id][label] = {
                            "timestamp": [],
                            "value"    : []
                        }

                    newObj[id][label]["timestamp"].push(timestamp)
                    newObj[id][label]["value"].push(value)

                    console.log("Dataset expanded:")
                    console.log(JSON.stringify(newObj))

                    this.dataset = newObj

                } else   // General data not related to a single node
                    this.updateGeneralData(label, timestamp);
            },

            updateGeneralData(label, timestamp) {
                let newObj = this.clone(this.generalData)
                newObj[label] = timestamp
                this.generalData = newObj
                console.log("General data updated:")
                console.log(JSON.stringify(this.generalData))
            },

            parseLogData(obj) {
                let id        = obj.node_id;
                let label     = obj.kpi;
                let timestamp = obj.timestamp;
                let value     = obj.value;

                this.appendNodeData(id, label, timestamp, value);
            },

            clone(obj) {
                if (null == obj || "object" != typeof obj) return obj;
                var copy = obj.constructor();
                for (var attr in obj) {
                    if (obj.hasOwnProperty(attr)) copy[attr] = obj[attr];
                }
                return copy;
            },

            /// MQTT
            parseMqttEvent(payload) {
                let payloadObj = JSON.parse(payload)
                let type       = payloadObj["type"]

                if (type == "kpi") 
                    this.parseLogData(payloadObj["content"])
            }

        },

        mounted() {
            this.loadData();

            this.$eventHub.$on("openbenchmark/userId/1/experimentId/" + this.experimentId + "/kpi", payload => {
                thisComponent.parseMqttEvent(payload);
            });
        },

        created() {
            thisComponent = this;
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

    #file-download {
        position: absolute;
        bottom: 15px;
        left: 15px;
    }
</style>

<style>
    canvas {
        position: relative;
    }
</style>