<template>
    <div class="parent col-direction pl-1 pr-1">
        <span id="exp-history" class="ml-2 mb-1 mt-1 bold">Experiment history:</span>
        <div class="row gray table-header">
            <span class="log-row col-2">Experiment ID</span>
            <span class="log-row col-3 bold">Date</span>
            <span class="log-row col-3 bold">Testbed</span>
            <span class="log-row col-3 bold">Scenario</span>
        </div>
        <div class="row hoverable" :class="{gray: ind%2===0}" v-for="(item, ind) in outputs">
            <span class="log-row col-2">{{item.id}}</span>
            <span class="log-row col-3 bold">{{item.date}}</span>
            <span class="log-row col-3 bold">{{item.testbed}}</span>
            <span class="log-row col-3 bold">{{item.scenario}}</span>
        </div>
    </div>
</template>

<script>
    let thisComponent;

    export default {
        data: function() {
            return {
                outputs: [
                    // Item example {id: "659xv", date: "17.06.2019 10:47:05", testbed: "IoT-LAB", scenario: "Demo scenario"}
                    {id: "659xv", date: "17.06.2019 10:47:05", testbed: "IoT-LAB", scenario: "Demo scenario"},
                    {id: "659xv", date: "17.06.2019 10:47:05", testbed: "IoT-LAB", scenario: "Demo scenario"},
                    {id: "659xv", date: "17.06.2019 10:47:05", testbed: "IoT-LAB", scenario: "Demo scenario"},
                    {id: "659xv", date: "17.06.2019 10:47:05", testbed: "IoT-LAB", scenario: "Demo scenario"},
                    {id: "659xv", date: "17.06.2019 10:47:05", testbed: "IoT-LAB", scenario: "Demo scenario"}
                ]
            }
        },

        methods: {
            
        },

        created() {
            thisComponent = this
        },

        mounted() {
            
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