import { createRouter, createWebHistory } from 'vue-router';
import Landing from '../pages/LandingPage.vue';
import Login from '../pages/LoginPage.vue';
import Registration from '../pages/RegistrationPage.vue';
import AdminDashboard from '../pages/AdminDashboard.vue';
import UserDashboard from '../pages/UserDashboard.vue';


const routes = [
    { path: '/', name: 'Landing', component: Landing},
    { path: '/login', name: 'Login', component: Login},
    { path: '/register', name: 'Registration', component: Registration},
    { path: '/admin_dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' }},
    { path: '/user_dashboard', name: 'UserDashboard', component: UserDashboard, meta: { requiresAuth: true, role: 'user'}}
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');

    if (to.meta.requiresAuth){
        if(!token){
            return next('/login');
        }
        if (to.meta.role && to.meta.role !==role){
            return next('/');
        }
    }
    next();
});

export default router;