<template>
    <div class="parent row">
        <sidebar></sidebar>
        <div id="root" style="margin-left: 80px">
            <div id="intro" class="section" v-observe-visibility="{
                       callback: visibilityChanged,
                       intersection: {
                           root,
                           threshold
                       }
                    }">
                <logs-list></logs-list>
            </div>
            <div id="scenarios" class="section" v-observe-visibility="{
                       callback: visibilityChanged,
                       intersection: {
                           root,
                           threshold
                       }
                    }">
                <scenarios :experiment-id="id"></scenarios>
            </div>
        </div>
    </div>
</template>

<script>
    import ExampleComponent from './../components/ExampleComponent.vue'
    import Intro from './../components/landing/Intro.vue'
    import LogsList from './../components/landing/LogsList.vue'
    import Scenarios from './../components/landing/Scenarios.vue'
    import Graphs from './../components/landing/Graphs.vue'
    import Sidebar from './../components/reusables/Sidebar.vue'

    let thisComponent;
    let socketConnected = false;

    export default {
        props: ['id'],

        components: {
            ExampleComponent,
            Intro,
            LogsList,
            Scenarios,
            Graphs,
            Sidebar
        },

        data: function () {
            return {
                sidebarScroll: false,
                root: document.getElementById('root'),
                threshold: 0.05
            }
        },

        methods: {
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

    #root {
        width: 100%;
    }

    .section {
        height: 100vh;
    }
</style>