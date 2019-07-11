<template>
    <div class="parent row">

        <modal name="alert-dialog" width="400px" height="170px">
            <div class="dialog-loader row h-center v-center" v-if="dialogLoader">
                <i class="fas fa-circle-notch fa-3x fa-spin"></i>
            </div>
            <span class="dialog-content" :class="{'dialog-content-disabled': dialogLoader}">
                <h3 class="dialog-title bold">{{dialog.title}}</h3>
                <div class="buttons row h-center" v-if="dialog.buttons.length === 2">
                    <button id="ok-btn" class="main-btn btn-small btn-width-half ml-1" @click="dialog.action" :disabled="dialogLoader">{{dialog.buttons[0]}}</button>
                    <button id="cancel-btn" class="main-btn btn-small btn-width-half btn-danger mr-1" @click="closeDialog()" :disabled="dialogLoader">{{dialog.buttons[1]}}</button>
                </div>
                <div class="buttons row v-center" v-if="dialog.buttons.length === 1">
                    <button class="main-btn btn-small" @click="closeModal('alert-dialog')" :disabled="dialogLoader">{{dialog.buttons[0]}}</button>
                </div>
            </span>
        </modal>

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

    const axios = require('axios');

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
                threshold: 0.05,

                dialog: {
                    "title": "",
                    "buttons": []
                },
                dialogLoader: false
            }
        },

        methods: {
            scrollContent(anchor) {
                this.$eventHub.$emit('SCROLL', anchor);
            },

            visibilityChanged (isVisible, entry) {
                if (isVisible && !this.sidebarScroll)
                    this.scrollContent(entry.target.id);
            },

            showDialog(key) {
                let dialogs = {
                    "termination": {
                        "title": "Are you sure you want to terminate the experiment?", 
                        "buttons": ["YES", "NO"],
                        "action": this.dialogTerminationOK
                    },
                    "missing-params": {
                        "title": "You must select a testbed and a scenario",
                        "buttons": ["OK"],
                        "action": undefined
                    }
                }
                this.dialog = dialogs[key]
                this.showModal('alert-dialog')
            },
            closeDialog(key) {
                this.closeModal('alert-dialog')

                if (key === "termination")
                    this.$eventHub.$emit("DIALOG_TERMINATION", '')
            },

            showModal(name) {
                this.$modal.show(name)
            },
            closeModal(name) {
                this.$modal.hide(name)
                this.dialogLoader = false
            },

            dialogTerminationOK() {
                this.dialogLoader = true
                this.processTerminate()
            },
            processTerminate() {
                axios.get('/api/terminate')
                    .then(function (response) {
                        // handle success
                        console.log(response);
                    })
                    .catch(function (error) {
                        // handle error
                        console.log("Error: " + error);
                    })
                    .then(function () {
                        // executes always
                    });
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

            this.$eventHub.$on("SHOW_DIALOG", payload => {
                thisComponent.showDialog(payload)
            });
            this.$eventHub.$on("CLOSE_DIALOG", payload => {
                thisComponent.closeDialog(payload)
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

    .buttons {
        position: absolute;
        bottom: 15px;
        width: 100%
    }
    #start-btn, #ok-btn {
        margin-right: 7px;
    }

    .dialog-title {
        position: absolute;
        top: 15px;
        left: 50%;
        transform: translateX(-50%);
        width: 70%;
        text-align: center;
    }
    .dialog-loader {
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.7);
        color: #1f6fb2;
    }
    .dialog-content {

    }
    .dialog-content-disabled {
        opacity: 0.3
    }

</style>