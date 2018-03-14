import HomeComponent from './components/Home/HomeComponent';

const URLS = {
    base: () => '/',
};

const ROUTES = [
    {
        exact: true,
        path: URLS.base(),
        component: HomeComponent,
        name: 'home',
    },
];

export {ROUTES, URLS};
