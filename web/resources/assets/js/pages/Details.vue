<template>
    <div class="parent col-direction">
        <span class="ml-3 mt-1">KPIs for experiment <span class="bold">{{id}}</span></span>
        <div id="root">
            <graphs id="graphs" :experiment-id="id"></graphs>
        </div>
    </div>
</template>

<script>
    import Graphs from './../components/landing/Graphs.vue'

    let thisComponent;
    let socketConnected = false;

    export default {
        props: ['id'],

        components: {
            Graphs
        },

        data: function () {
            return {
                
            }
        },

        methods: {
            
        },

        mounted() {
            console.log(this.id)
        },

        created() {
            thisComponent = this;
        }
    }
</script>

<style src="./../../sass/layout/margins.css"></style>
<style src="./../../sass/layout/paddings.css"></style>
<style src="./../../sass/layout/positioning.css"></style>
<style src="./../../sass/styles/text-styles.css"></style>
<style src="./../../sass/styles/buttons.css"></style>
<style src="./../../sass/styles/colors.css"></style>
<style src="./../../sass/styles/animations.css"></style>
<style src="./../../sass/styles/cards.css"></style>
<style src="./../../sass/styles/radio.css"></style>
<style src="./../../sass/styles/vuebar.css"></style>

<style scoped>
    .parent {
        background-color: #eeeeee;
        height: 100vh;
    }

    #root {
        width: 100%;
        height: 85%;
    }
</style>