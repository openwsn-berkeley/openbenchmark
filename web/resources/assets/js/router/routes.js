import Home from './../pages/Home.vue';
import Details from './../pages/Details.vue';
import Login from './../pages/Login.vue';

const routes = [
	{ path: '/', component: Home},
    { path: '/home/:id', component: Home, props: true },
    { path: '/login', component: Login},
    { path: '/details/:id', component: Details, props: true},
];

export default routes;