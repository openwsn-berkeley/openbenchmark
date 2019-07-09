<template>
    <div class="parent col-direction pl-1 pr-1">
        <span id="exp-history" class="ml-2 mb-1 mt-1 bold">Experiment history:</span>
        <div class="row log-row gray table-header">
            <span class="active-ind-col"></span>
            <span class="col-2">Experiment ID</span>
            <span class="col-3 bold">Date</span>
            <span class="col-3 bold">Testbed</span>
            <span class="col-3 bold">Scenario</span>
        </div>
        <div class="row log-row hoverable" :class="{gray: ind%2===0}" v-for="(item, ind) in outputs" @click="showDetails(item.id)">
            <span class="row active-ind-col v-center h-center"><span class="active-ind" v-if="item.active"></span></span>
            <span class="col-2">{{item.id}}</span>
            <span class="col-3 bold">{{item.date}}</span>
            <span class="col-3 bold">{{item.testbed}}</span>
            <span class="col-3 bold">{{item.scenario}}</span>
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
                    // Item example {id: "659xv", date: "17.06.2019 10:47:05", testbed: "IoT-LAB", scenario: "Demo scenario", active: false}
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

            sanitize(jsArr) {
                let newArr = []

                jsArr.forEach((el) => {
                    newArr.push(this.sanitizeObj(el))
                })

                return newArr
            },

            sanitizeObj(jsObj) {
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

                return {
                    "id"      : jsObj.experiment_id,
                    "date"    : this.convertDate(jsObj.date),
                    "firmware": jsObj.firmware,
                    "scenario": scenarios[jsObj.scenario],
                    "testbed" : testbeds[jsObj.testbed],
                    "active"  : jsObj.active
                }
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
            },

            /// MQTT
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
                console.log(payloadObj.experiment_id)
                this.outputs.unshift(this.sanitizeObj({
                    experiment_id: payloadObj.experiment_id, 
                    date: payloadObj.date, 
                    firmware: payloadObj.firmware,
                    scenario: payloadObj.scenario,
                    testbed: payloadObj.testbed,
                    active: true
                }))
            },

            notifyExperimentActive(experimentId) {
                let newArr = []

                this.outputs.forEach(el => {
                    if (el.id === experimentId)
                        el.active = true

                    newArr.push(el)
                })

                this.outputs = newArr
            }
        },

        created() {
            thisComponent = this
        },

        mounted() {
            this.fetchLogs()

            this.$eventHub.$on("openbenchmark/1/headerLogged", payload => {
                thisComponent.parseMqttEvent(payload);
            });

            this.$eventHub.$on("openbenchmark/newKpi", payload => {
                thisComponent.notifyExperimentActive(payload);
            });
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
        cursor: pointer;
    }

    .gray {
        background-color: #fafafa;
    }

    .active-ind {
        display: inline-block;
        width: 15px;
        height: 15px;
        border-radius: 10px;
        background-color: #32CD32
    }
    .active-ind-col {
        width: 45px;
        padding: 0;
    }
</style>