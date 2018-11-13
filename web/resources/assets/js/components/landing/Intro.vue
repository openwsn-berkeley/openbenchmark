<template>
    <div class="parent">
        <!-- <div class="row mb-2 h-center">
            <img class="logo" src="http://www.ucg.ac.me/skladiste_baneri/org_jedinica_13/baneri_237/soda_logo_transparent.png"/>
        </div> -->
        <div class="row" style="margin: 0 100px">
            <div class="col-3">
                <img class="image-lg" src="https://twatteyne.files.wordpress.com/2013/10/logo_6tisch.png"/>
            </div>
            <div class="col-9 pl-2">
                <h2>BENCHMARK YOUR 6TiSCH IMPLEMENTATION</h2>
                <h4 style="font-size: 100%; font-style: italic">How many times have you come across an academic paper with unfair evaluation? </h4>
                <p class="justified">We aim at standardizing how performance evaluation of 6TiSCH low-power networking technology is done. Upload your 6TiSCH firmware and we will test it in industry-relevant test scenarios on experimental testbeds. You can monitor the network key performance indicators in real time and get an exhaustive performance report of your 6TiSCH firmware implementation.</p>
            </div>
        </div>
        <div style="position: relative; height: 120px; margin: 50px 100px 30px 110px">
            <img class="logo-sm" style="position: absolute; left: 0; margin-bottom: 3px" src="http://www.ucg.ac.me/skladiste_baneri/org_jedinica_13/baneri_237/soda_logo_transparent.png">
            <img class="logo-sm" style="position: absolute; left: 50%; transform:translateX(-50%)" src="images/ucg.png">
            <img class="logo" style="position: absolute; right: 0" src="https://fed4fire.eu/wp-content/uploads/sites/10/2017/01/fed4fire_logo_extended.png">
        </div>
        <div class="scroll-down row h-center mt-3" @click="scrollContent">
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
        width: 200px;
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