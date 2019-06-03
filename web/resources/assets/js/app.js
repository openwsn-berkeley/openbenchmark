import routes from './router/routes.js';
import MQTTClient from './mqtt.js';
import VueSocketio from 'vue-socket.io-extended';
import io from 'socket.io-client';
import { ObserveVisibility } from 'vue-observe-visibility'
import Vuebar from 'vuebar';
import VModal from 'vue-js-modal';
import VueRouter from 'vue-router';

//require('./bootstrap');

window.Vue = require('vue');
Vue.use(VueRouter);

Vue.prototype.$eventHub = new Vue();
Vue.prototype.$mqttClient = new MQTTClient('broker.mqttdashboard.com', 8000, Vue.prototype.$eventHub); //this.$mqttClient.publish(), this.$mqttClient.subscribe()

Vue.component('arrow', require('./components/reusables/Arrow.vue').default);
Vue.component('multiselect', require('vue-multiselect').default);
Vue.component('progress-bar', require('./components/reusables/ProgressBar.vue').default);

Vue.use(Vuebar);

Vue.directive('observe-visibility', ObserveVisibility);

Vue.use(VModal)

// Date class extension
Object.defineProperty(Date.prototype, "getCurrentDate", {
	value: function getCurrentDate(timeOnly = true) {
		let day   = this.getDate().pad()
		let month = (this.getMonth() + 1).pad() // getMonth() is zero-based
		let year  = this.getFullYear()
		let hours = this.getHours().pad()
		let mins  = this.getMinutes().pad()
		let secs  = this.getSeconds().pad()

		if (timeOnly)
			return hours + ":" + mins + ":" + secs;
		return day + "." + month + "." + year + " " + hours + ":" + mins + ":" + secs;
	},
	writeable: true,
	configurable: true
})

Object.defineProperty(Number.prototype, "pad", {
	value: function(size = 2) {
		let mString = String(this)
	    while (mString.length < (size || 2)) {mString = "0" + mString;}
	    return mString
	},
	writeable: true,
	configurable: true
})

/**
 * Next, we will create a fresh Vue application instance and attach it to
 * the page. Then, you may begin adding components to this application
 * or customize the JavaScript scaffolding to fit your unique needs.
 */

const router = new VueRouter({
    routes,
    mode: 'history'
});

const app = new Vue({
    router
}).$mount('#app');