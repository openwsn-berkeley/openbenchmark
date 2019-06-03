<template>
    <div class="parent col-direction v-center h-center">
        <img src="images/bgd.jpg" style="position: fixed; width: 100vw; top: 0; left: 0;"/>
        <div class="card col-direction h-center pl-5 pr-5 pb-4">
            <img class="title-image" src="/images/6tisch_no_text.png">
            <span class="title bold">OpenBenchmark</span>
            <span class="bold align-left mt-2">Username</span>
            <div class="input-field-container">
                <span class="permanent-border"/>
                <input class="input-field" type="text">
                <span class="input-field-border"/>
            </div>
            <span class="bold align-left mt-1">Password</span>
            <div class="input-field-container">
                <span class="permanent-border"/>
                <input class="input-field" type="password">
                <span class="input-field-border"/>
            </div>
            <button class="main-btn mt-3">Sign in</button>
        </div>
    </div>
</template>

<script>
    import Sidebar from './../components/reusables/Sidebar.vue'

    let thisComponent;
    let socketConnected = false;

    export default {
        components: {
            Sidebar
        },

        data: function () {
            return {
                dataFlowStarted: true,
                sidebarScroll: false,
                root: document.getElementById('root'),
                threshold: 0.05
            }
        },

        methods: {

        },

        mounted() {

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
<style src="./../../sass/styles/input-fields.css"></style>

<style scoped>
    .parent {
        width: 100%;
        height: 100vh;
    }

    .card {
        width: 530px;
        height: auto;
        z-index: 3;
    }

    .title-image {
        width: 100px;
        margin-top: 25px;
    }

    .main-btn {
        height: 45px;
    }

</style>