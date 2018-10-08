<template>
    <div class="top-container">
        <ol class="track-progress">
            <li :class="{done: nodesReserved, todo: !nodesReserved}">
                <em>1</em>
                <span>Reserving</span>
            </li>
            <li :class="{done: allBooted, todo: !allBooted}">
                <em>2</em>
                <span>Booting</span>
            </li>
            <li :class="{done: allActive, todo: !allActive}">
                <em>3</em>
                <span>Flashing</span>
            </li>
            <li :class="{done: dataFlowStarted, todo: !dataFlowStarted}">
                <em>4</em>
                <span>Pending</span>
            </li>
        </ol>
    </div>
</template>

<script>
    export default {
        props: [
            'nodesReserved',
            'allBooted',
            'allActive',
            'dataFlowStarted'
        ],

        data: function () {
            return {
                //Data goes here
            }
        }
    }
</script>

<style scoped>
    .top-container {
        width: 112%;
    }

    body {
        background: #6699CC;
        padding-top: 20px;
    }

    .track-progress {
        margin: 0;
        padding: 10px 10px 0 10px;
        background: white;
        height: 80px;
    }
    .track-progress li {
        list-style-type: none;
        display: inline-block;
        position: relative;
        font: 14px/14px Helvetica, sans-serif;
        text-transform: uppercase;
        text-align: center;
        color: #bbb;
        border-bottom: 4px #bbb solid;
        line-height: 3em;
        width: 25%;
        float: left;
    }
    .track-progress li:after {
        content: "\00a0\00a0";
        /*non-breaking space */
    }
    .track-progress li:before {
        position: relative;
        bottom: -2.5em;
        float: left;
        left: 50%;
        line-height: 1em;
    }
    @media (max-width: 800px) {
        .track-progress li {
            font-size: 0.7em;
        }
    }
    .track-progress li span {
        padding-left: 0.75em;
    }
    @media (max-width: 640px) {
        .track-progress li span {
            display: none;
        }
    }
    .track-progress li.done {
        color: #bbb;
        font-weight: bold;
        border-bottom: 4px #6699CC solid;
    }
    .track-progress li.done:before {
        content: "";
        background: #6699CC;
        height: 1.2em;
        width: 1.2em;
        line-height: 1.2em;
        border: none;
        border-radius: 1.2em;
    }
    .track-progress li.todo:before {
        content: "";
        background: white;
        border: 0.25em solid #bbb;
        height: 0.8em;
        width: 0.8em;
        border-radius: 0.8em;
    }
    .track-progress em {
        display: none;
        font-weight: 700;
        padding-left: 0.75em;
    }
    @media (max-width: 640px) {
        .track-progress em {
            display: inline;
        }
    }

    p {
        margin: 0 auto;
        max-width: 500px;
        width: 75%;
        margin-top: 25px;
        font: 18px/28px 'Open Sans',sans-serif;
        color: #eee;
    }
    p em {
        display: block;
        font-size: 23px;
        font-weight: 700;
        font-style: normal;
        color: white;
    }

</style>