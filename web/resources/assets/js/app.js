import routes from './router/routes.js';
import MQTTClient from './mqtt.js';
import VueSocketio from 'vue-socket.io-extended';
import io from 'socket.io-client';
import { ObserveVisibility } from 'vue-observe-visibility'
import Vuebar from 'vuebar';

import VueRouter from 'vue-router';

//require('./bootstrap');

window.Vue = require('vue');
Vue.use(VueRouter);

Vue.prototype.$eventHub = new Vue();
Vue.prototype.$mqttClient = new MQTTClient('broker.mqttdashboard.com', 8000); //this.$mqttClient.publish(), this.$mqttClient.subscribe()

Vue.component('arrow', require('./components/reusables/Arrow.vue'));
Vue.component('multiselect', require('vue-multiselect').default);
Vue.component('progress-bar', require('./components/reusables/ProgressBar.vue'));

//Vue.use(VueSocketio, io('http://89.188.32.132:3000'));
//Vue.use(VueSocketio, io('http://192.168.10.192:3000'));
Vue.use(VueSocketio, io('http://127.0.0.1:3000'));
Vue.use(Vuebar);

Vue.directive('observe-visibility', ObserveVisibility);

/**
 * Next, we will create a fresh Vue application instance and attach it to
 * the page. Then, you may begin adding components to this application
 * or customize the JavaScript scaffolding to fit your unique needs.
 */

const router = new VueRouter({
    routes
});

const app = new Vue({
    el: '#app',
    router: router
});
