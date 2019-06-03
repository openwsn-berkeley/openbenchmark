<template>
    <div class="parent row">
        <sidebar></sidebar>
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

<style scoped>
    .parent {
        position: relative;
    }
</style>