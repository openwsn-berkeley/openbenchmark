<template>
    <div class="top-container">
        <ol class="track-progress">
            <li :class="{done: currentStep >= 0, 'in-progress': currentStep == -1, todo: currentStep < 0}">
                <em>1</em>
                <span>Provisioning</span>
            </li>
            <li :class="{done: currentStep >= 1, 'in-progress': currentStep == 0, todo: currentStep < 1}">
                <em>2</em>
                <span>Flashing</span>
            </li>
            <li :class="{done: currentStep >= 2, 'in-progress': currentStep == 1, todo: currentStep < 2}">
                <em>3</em>
                <span>Network Formation</span>
            </li>
            <li :class="{done: currentStep >= 3, 'in-progress': currentStep == 2, todo: currentStep < 3}">
                <em>4</em>
                <span>Orchestrating</span>
            </li>
        </ol>
    </div>
</template>

<script>
    export default {
        props: ['currentStep'],

        data: function () {
            return {
                //Data goes here
            }
        }
    }
</script>

<style scoped>
    .top-container {
        width: 100%;
    }

    body {
        padding-top: 20px;
    }

    .track-progress {
        margin: 0;
        padding: 10px 10px 0 10px;
        height: 80px;
    }
    .track-progress li {
        list-style-type: none;
        display: inline-block;
        position: relative;
        text-align: center;
        font-weight: bold;
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
        color: #777;
        font-weight: bold;
        border-bottom: 4px #6699CC solid;
    }
    .track-progress li.in-progress:before {
        color: #1f6fb2;
        animation: inProgressAnim 1s infinite;
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

    @keyframes inProgressAnim {
        0% {
            transform: scale(1);
        }
        25% {
            transform: scale(1.2);
        }
        75% {
            transform: scale(0.8);
        }
        100% {
            transform: scale(1);
        }
    }

</style>