import Home from './../pages/Home.vue';
import Login from './../pages/Login.vue';

const routes = [
	{ path: '/', component: Home},
    { path: '/home/:id', component: Home, props: true },
    { path: '/login', component: Login}
];

export default routes;