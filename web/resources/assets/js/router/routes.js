import Home from './../pages/Home.vue';

const routes = [
	{ path: '/', component: Home},
    { path: '/:id', component: Home, props: true },
    { path: '/home/:id', component: Home, props: true },
];

export default routes;