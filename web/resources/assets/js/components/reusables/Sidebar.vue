<template>
    <div class="top-container">
        <nav class="sidebar-navigation">
            <ul>
                <li :class="{active: selectedId === 0}" @click="scrollContent('intro')">
                    <i class="fas fa-home"></i>
                    <span class="tooltip">Home</span>
                </li>
                <li :class="{active: selectedId === 1}" @click="scrollContent('scenarios')">
                    <i class="fas fa-cogs"></i>
                    <span class="tooltip">Configuration</span>
                </li>
                <li :class="{active: selectedId === 2}" @click="scrollContent('graphs')" v-if="dataFlowStarted">
                    <i class="fas fa-tachometer-alt"></i>
                    <span class="tooltip">Monitoring</span>
                </li>
            </ul>
            <ul class="bottom-list">
                <li @click="showDocs">
                    <i class="fas fa-book"></i>
                    <span class="tooltip">Documentation</span>
                </li>
            </ul>
        </nav>
    </div>
</template>

<script>
    export default {
        data: function () {
            return {
                dataFlowStarted: true,
                selectedId: 0
            }
        },

        methods: {
            select(id) {
                this.selectedId = id;
            },
            scrollContent(anchor) {
                this.$eventHub.$emit('SIDEBAR_SCROLL', '');
                this.$eventHub.$emit('SCROLL', anchor);
            },
            showDocs() {
                window.location.href = "/docs";
            }
        },

        mounted() {
            this.$eventHub.$on("SCROLL", payload => {
                switch (payload) {
                    case 'intro':
                        this.selectedId = 0;
                        break;
                    case 'scenarios':
                        this.selectedId = 1;
                        break;
                    case 'graphs':
                        this.selectedId = 2;
                        break;
                }
            });
            this.$eventHub.$on("LOG_MODIFICATION", payload => {
                this.dataFlowStarted = true;
            });
            this.$eventHub.$on("EXP_TERMINATE", payload => {
                this.dataFlowStarted = false;
            });
        }

    }
</script>

<style scoped>
    .top-container {
        position: fixed;
    }

    * {
        margin: 0;
        padding: 0;
        list-style: none;
        line-height: 1;
    }

    body {
        background-color: #F5F6F8;
        overflow: hidden;
    }

    .sidebar-navigation {
        display: inline-block;
        position: relative;
        min-height: 100vh;
        width: 80px;
        background-color: #313443;
        float: left;
    }
    .sidebar-navigation ul {
        text-align: center;
        color: white;
    }
    .sidebar-navigation ul li {
        padding: 28px 0;
        cursor: pointer;
        transition: all ease-out 120ms;
    }
    .sidebar-navigation ul li i {
        display: block;
        font-size: 24px;
        transition: all ease 450ms;
    }
    .sidebar-navigation ul li .tooltip {
        display: inline-block;
        position: absolute;
        background-color: #313443;
        padding: 8px 15px;
        border-radius: 3px;
        margin-top: -26px;
        left: 90px;
        opacity: 0;
        visibility: hidden;
        font-size: 13px;
        letter-spacing: .5px;
    }
    .sidebar-navigation ul li .tooltip:before {
        content: '';
        display: block;
        position: absolute;
        left: -4px;
        top: 10px;
        -webkit-transform: rotate(45deg);
        transform: rotate(45deg);
        width: 10px;
        height: 10px;
        background-color: inherit;
    }
    .sidebar-navigation ul li:hover {
        background-color: #22252E;
    }
    .sidebar-navigation ul li:hover .tooltip {
        visibility: visible;
        opacity: 1;
        font-weight: bold;
    }
    .sidebar-navigation ul li.active {
        background-color: #22252E;
    }
    .sidebar-navigation ul li.active i {
        color: #98D7EC;
    }

    .bottom-list {
    	position: absolute;
    	bottom: 0;
    	left: 50%;
    	transform: translateX(-50%);
    	width: 100%;
    }
</style>