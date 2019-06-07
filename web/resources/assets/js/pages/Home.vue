<template>
    <div class="parent row">
        <sidebar></sidebar>
        <div id="root" style="margin-left: 80px">
            <intro id="intro" v-observe-visibility="{
                   callback: visibilityChanged,
                   intersection: {
                       root,
                       threshold
                   }
            }"></intro>
            <scenarios id="scenarios"  v-observe-visibility="{
                   callback: visibilityChanged,
                   intersection: {
                       root,
                       threshold
                   }
            }" :experiment-id="id"></scenarios>
            <graphs id="graphs"  v-if="dataFlowStarted" v-observe-visibility="{
                   callback: visibilityChanged,
                   intersection: {
                       root,
                       threshold
                   }
            }"></graphs>

            <bottom-sheet></bottom-sheet>
        </div>
    </div>
</template>

<script>
    import ExampleComponent from './../components/ExampleComponent.vue'
    import Intro from './../components/landing/Intro.vue'
    import Scenarios from './../components/landing/Scenarios.vue'
    import Graphs from './../components/landing/Graphs.vue'
    import Sidebar from './../components/reusables/Sidebar.vue'
    import BottomSheet from './../components/reusables/BottomSheet.vue'

    let thisComponent;
    let socketConnected = false;

    export default {
        props: ['id'],

        components: {
            ExampleComponent,
            Intro,
            Scenarios,
            Graphs,
            Sidebar,
            BottomSheet
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
            registerChannel: function() {
                this.$socket.emit('channelRegistration', 1); //Second param should be a dynamically added id
                console.log("Channel registered!");
            },
            forwardMessage: function(topic, data) {
                this.$eventHub.$emit(topic, data);
            },

            scrollContent(anchor) {
                this.$eventHub.$emit('SCROLL', anchor);
            },

            visibilityChanged (isVisible, entry) {
                if (isVisible && !this.sidebarScroll)
                    this.scrollContent(entry.target.id);
            }
        },

        mounted() {
            this.$eventHub.$on("SCROLL", payload => {
                window.scroll({
                    top: document.getElementById(payload).offsetTop,
                    left: 0,
                    behavior: 'smooth'
                });
                setTimeout(() => {
                    thisComponent.sidebarScroll = false;
                }, 300)
            });
            this.$eventHub.$on("SIDEBAR_SCROLL", payload => {
                thisComponent.sidebarScroll = true;
            });
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