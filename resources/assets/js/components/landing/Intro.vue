<template>
    <div class="parent">
        <!-- <div class="row mb-2 h-center">
            <img class="logo" src="http://www.ucg.ac.me/skladiste_baneri/org_jedinica_13/baneri_237/soda_logo_transparent.png"/>
        </div> -->
        <div class="row" style="margin: 0 150px">
            <div class="col-3">
                <img class="image-lg" src="https://twatteyne.files.wordpress.com/2013/10/logo_6tisch.png"/>
            </div>
            <div class="col-9 pl-2">
                <h2 class="uppercase">Benchmark your 6TiSCH implementation</h2>
                <p class="justified">How many times have you come across an academic paper with unfair evaluation methodology? We aim at standardizing how performance evaluation of 6TiSCH low-power networking technology is done. Upload your 6TiSCH firmware and we will test it in industry-relevant test scenarios on experimental testbeds. You can monitor the network key performance indicators in real time and get an exhaustive performance report of your 6TiSCH firmware implementation.</p>
            </div>
        </div>
        <div class="row" style="margin: 30px 160px 30px 160px">
            <div class="card col" style="flex: 5">
                <h4>Brought to you by:</h4>
                <img class="logo-sm mr-2" style="margin-bottom: 3px" src="http://www.ucg.ac.me/skladiste_baneri/org_jedinica_13/baneri_237/soda_logo_transparent.png">
                <img class="logo-sm mr-2" src="images/ucg.png">
            </div>
            <div class="card pl-5" style="flex: 1">
                <h4>Funded by:</h4>
                <img class="logo" src="https://fed4fire.eu/wp-content/uploads/sites/10/2017/01/fed4fire_logo_extended.png">
            </div>
        </div>
        <div class="scroll-down row h-center mt-1" @click="scrollContent">
            <arrow></arrow>
        </div>
    </div>
</template>

<script>
    export default {
        data: function () {
            return {
                //Data goes here
            }
        },
        methods: {
            scrollContent() {
                this.$eventHub.$emit('SCROLL', 'scenarios');
            }
        }
    }
</script>

<style scoped>
    .parent {
        padding: 25px;
        height: 100vh;
    }

    .logo {
        width: 250px;
        height: auto;
    }
    .logo-sm {
        width: 150px;
        height: auto;
    }
    .image-lg {
        width: 350px;
        height: auto;
    }

    .scroll-down {
        height: 80px;
        cursor: pointer;
    }

</style>