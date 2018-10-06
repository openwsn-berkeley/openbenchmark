<template>
    <div class="parent">
        <div class="row mb-2 h-center">
            <img class="logo" src="http://www.ucg.ac.me/skladiste_baneri/org_jedinica_13/baneri_237/soda_logo_transparent.png"/>
        </div>
        <div class="row" style="margin: 0 150px">
            <div class="col-3">
                <img class="image-lg" src="images/6tisch_no_text.png"/>
            </div>
            <div class="col-9 pl-2">
                <h2 class="uppercase">6TiSCH Open Data Action Benchmarking</h2>
                <p class="justified">Lorem ipsum dolor sit amet, hinc solum ei qui, modus salutandi temporibus pro at. Ad dicunt accusata pro. Prima omnes vulputate te pri, te adipisci repudiare dignissim mea. Ad cum quod elit blandit, has prima doctus ut. Quo utinam liberavisse ut.Vis no assentior expetendis, nam indoctum consectetuer no, velit nostrud his at. Ridens maiorum ei his. His in impedit feugait. Ei eos quidam possim equidem, dico tota convenire te sit. Suas quando facilis et qui, quem odio ut ius.Eruditi dissentiunt usu ea. Sea idque deseruisse an. Qui in movet erroribus, pri eu primis graeci offendit. Mollis petentium mea an. Per diam brute ei, ne nihil</p>
                <div class="row">
                    <img class="logo-sm mr-2" style="height: 55px" src="https://www.iot-lab.info/wp-content/themes/alienship-1.2.5-child/templates/parts/fit-iotlab3.png">
                    <img class="logo-sm mr-2" src="https://www.inria.fr/extension/site_inria/design/site_inria/images/logos/logo_INRIA_FR.svg">
                </div>
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