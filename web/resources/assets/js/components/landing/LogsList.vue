<template>
    <div class="parent col-direction pl-1 pr-1">
        <span id="exp-history" class="ml-2 mb-1 mt-1 bold">Experiment history:</span>
        <div class="row gray table-header">
            <span class="log-row col-2">Experiment ID</span>
            <span class="log-row col-3 bold">Date</span>
            <span class="log-row col-3 bold">Testbed</span>
            <span class="log-row col-3 bold">Scenario</span>
        </div>
        <div class="row hoverable" :class="{gray: ind%2===0}" v-for="(item, ind) in outputs" @click="showDetails(item.id)">
            <span class="log-row col-2">{{item.id}}</span>
            <span class="log-row col-3 bold">{{item.date}}</span>
            <span class="log-row col-3 bold">{{item.testbed}}</span>
            <span class="log-row col-3 bold">{{item.scenario}}</span>
        </div>
    </div>
</template>

<script>
    const axios = require('axios');

    let thisComponent;

    export default {
        data: function() {
            return {
                outputs: [
                    // Item example {id: "659xv", date: "17.06.2019 10:47:05", testbed: "IoT-LAB", scenario: "Demo scenario"}
                ],
            }
        },

        methods: {
            showDetails(id) {
                this.$router.push('details/' + id)
            },

            fetchLogs() {
                axios.get('/api/logs/log-list')
                    .then(function (response) {
                        thisComponent.outputs = thisComponent.sanitize(response.data.message.data)
                    })
                    .catch(function (error) {
                        console.log(error);
                    })
                    .then(function() {

                    });
            },

            sanitize(jsObject) {
                let newObj = []

                let scenarios = {
                    "demo-scenario"        : "Demo Scenario",
                    "home-automation"      : "Home Automation",
                    "building-automation"  : "Building Automation",
                    "industrial-monitoring": "Industrial Monitoring"
                }

                let testbeds = {
                    "iotlab": "IoT-LAB",
                    "wilab" : "w-iLab.t"
                }

                jsObject.forEach((el) => {
                    newObj.push({
                        "id"      : el.experiment_id,
                        "date"    : this.convertDate(el.date),
                        "firmware": el.firmware,
                        "scenario": scenarios[el.scenario],
                        "testbed" : testbeds[el.testbed]
                    })
                })

                return newObj
            },

            convertDate(date) {
                let datetime = new Date(Date.parse(date))
                let options = {
                    weekday: 'short', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric', 
                    hour: '2-digit', 
                    minute: '2-digit', 
                    second: '2-digit'
                }

                return datetime.toString().split("(")[0]
            }
        },

        created() {
            thisComponent = this
        },

        mounted() {
            this.fetchLogs()
        }
    }
</script>

<style scoped>
    .parent {
        height: 100vh;
        overflow-y: auto;
    }

    .row {
        transition: 0.3s ease;
    }
    .row.hoverable:hover {
        background-color: #eeeeee
    }

    .table-header {
        border-bottom: 2px solid #0e305d;
    }
    .log-row {
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 33px;
        cursor: pointer;
    }

    .gray {
        background-color: #fafafa;
    }
</style>