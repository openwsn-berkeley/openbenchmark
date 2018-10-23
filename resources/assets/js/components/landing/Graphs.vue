<template>
    <div class="top-content">
        <div class="row" style="height: 100%">
            <div class="col-direction ml-1 mr-1 col-4" style="height: 100%;">
                <div class="node-card card mb-1" style="width: 100%; height: 50%;">
                    <d3-network :net-nodes="nodes" :net-links="links" :options="options" @node-click="nodeClick"/>
                </div>
                <div class="card col-direction" style="width: 100%; height: 50%;">
                    <span class="mt-1" v-if="currentlyShowing !== ''">
                        <span class="bold ml-1 mr-1">Name: </span> {{currentData.id}}
                    </span>
                    <span class="data-row" v-if="currentlyShowing !== ''">
                        <span class="bold ml-1 mr-1">EUI-64: </span> {{currentData.eui64}}
                    </span>
                    <span class="data-row" v-if="currentlyShowing !== ''">
                        <span class="bold ml-1 mr-1">DAG Root?: </span> {{currentData.isDag}}
                    </span>
                    <!--<span class="data-row"><span class="bold ml-1 mr-1">Radio Duty Cycle: </span> 0.55%</span>-->
                </div>
            </div>
            <div class="card row ml-1 mr-1 pt-1 col-8 wrap" style="overflow-y: auto; overflow-x: hidden">

                <span v-for="node in dataset">
                    <span v-if="node.id === currentlyShowing">
                        <span v-for="item in node.nodeData">
                            <line-chart class="chart ml-3 mr-3"
                                        :label="item.label"
                                        :x-axis="item.xAxis"
                                        :y-axis="item.yAxis"
                                        :width="650"
                                        :height="300"></line-chart>
                        </span>
                    </span>
                </span>

                <!--
                <line-chart class="chart ml-3 mr-3"></line-chart>
                <line-chart class="chart ml-3 mr-3"></line-chart>
                <line-chart class="chart ml-3 mr-3"></line-chart>
                <line-chart class="chart ml-3 mr-3"></line-chart>-->
            </div>
        </div>
    </div>
</template>

<script>
    import LineChart from './../charts/LineChart.vue'
    import D3Network from 'vue-d3-network';

    let thisComponent;

    export default {
        components: {
            LineChart,
            D3Network
        },

        data: function () {
            return {
                expStartTimestamp: -1,
                dataPerChart: 20,

                name: 'Scenario 1',
                description: 'Scenario1: Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Donec odio. Quisque volutpat mattis eros. Nullam malesuada erat ut turpis. Suspendisse urna nibh, viverra non, semper suscipit, posuere a, pede.',
                nodes: [ //This should be created dynamically via eventBus from Scenarios.vue
                    { id: 1, name: 'node-a8-106', _cssClass: 'node-on'},
                    { id: 2, name: 'node-a8-107', _cssClass: 'node-on'},
                    //{ id: 3, name:'orange node', _color: 'orange' },
                    //{ id: 4, _color: '#0022ff'},
                    { id: 3, name: 'node-a8-102', _cssClass: 'node-on'},
                ],
                links: [
                    { sid: 1, tid: 2 },
                    { sid: 2, tid: 3 },
                ],

                currentlyShowing : '',

                dataset: [
                    /*{//Corresponds to a single node
                        "id":"node-a8-106",
                        "eui64":"05-43-32-ff-03-dc-a3-66",
                        "isDag": 0,
                        "nodeData":[
                            {
                                "label":"numRx",
                                "xAxis":[15388500.87438082,15388500.905358542,15388500.935934938,15388500.966604061,15388500.99736588,15388501.01802762,15388501.04889744],
                                "yAxis":[0,0,0,0,0,0,0]
                            },
                            {
                                "label":"dutycycle",
                                "xAxis":[15388500.987090621],
                                "yAxis":[100]
                            }
                        ]
                    }*/
                ],

                nodeSize:35,
                canvas:false
            }
        },

        methods: {
            relativeTimestampParse(timestamp) {
                //Converts relative timestamp to milliseconds or seconds since the experiment start
                //Timestamp in units of timeslots. Each timeslot is 10ms
                return (timestamp / 1000000).toFixed(2);
            },

            createBlankDataset() {
                //Creates a blank dataset for all the existing nodes in the 'nodes' field
                this.nodes.forEach(element => {
                    this.dataset.push({
                        id: element.name,
                        eui64: '',
                        nodeData: []
                    })
                });
            },
            appendNodeData(id, info, label, xVal, yVal) {
                //Appends to 'xAxis' and 'yAxis' of a 'nodeData' (of the node with the given 'eui64') element with the corresponding label
                //Creates new 'nodeData' element if the label does not exist
                let node = this.getNodeByProperty('id', id);

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

                node.eui64 = info['64bAddr'];
                node.isDag = (info.isDAGroot === 1) ? 'Yes' : 'No';
            },

            selectNodeData(id) {
                //Put dataset element with the given 'id' in 'currentlyShowing' variable (used for filling the UI with the data)
                this.currentlyShowing = id;
                console.log("Currently showing: " + JSON.stringify(this.getNodeByProperty('id', this.currentlyShowing)));
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

            parseLogData(payload) {
                let obj = JSON.parse(payload);

                let label = obj._type.split('.')[1];

                let id = obj._mote_info.serial.split('_')[1];

                //let xVal = this.relativeTimestampParse(obj._timestamp);
                let xVal = obj._timestamp;
                let yVal = obj[label];

                this.appendNodeData(id, obj._mote_info, label, this.timestampDiff(xVal), parseFloat(yVal));
            },

            nodeClick(event, node) {
                this.selectNodeData(node.name);
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
            }

        },

        computed:{
            options(){
                return{
                    force: 3000,
                    size: {w:350, h:320},
                    nodeSize: this.nodeSize,
                    nodeLabels: true,
                    canvas: this.canvas
                }
            },
            currentData() {
                let currentNode = this.getNodeByProperty('id', this.currentlyShowing);
                return {
                    id: currentNode.id,
                    eui64: currentNode.eui64,
                    isDag: currentNode.isDag
                }
            }
        },

        mounted() {
            this.$eventHub.$on("LOG_MODIFICATION", payload => {
                thisComponent.parseLogData(payload);
            });
        },

        created() {
            this.createBlankDataset();
            thisComponent = this;
            this.expStartTimestamp = new Date().valueOf();
        }
    }

</script>

<style scoped>
    .top-content {
        height: 93vh;
        padding: 25px;
        background-color: #eeeeee;
    }
    .chart {
        width: 100%;
        height: 300px;
    }

    .node-card {
        display: flex;
        align-items: center;
        justify-content: center;
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