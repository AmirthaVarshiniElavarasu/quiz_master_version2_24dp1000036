import { createRouter, createWebHistory } from 'vue-router';
import Landing from '../pages/LandingPage.vue';
import Login from '../pages/LoginPage.vue';
import Registration from '../pages/RegistrationPage.vue';
import AdminDashboard from '../pages/AdminDashboard.vue';
import UserDashboard from '../pages/UserDashboard.vue';
import QuizDashboard from '../pages/QuizDashboard.vue';
import QuestionsPage from '../pages/QuestionsPage.vue';
import UserScore from '../pages/UserScore.vue';
import UserQuiz from '../pages/UserQuiz.vue';
import SummaryPage from '../pages/SummaryPage.vue';
import UnauthorizedPage from '../pages/UnauthorizedPage.vue';


const routes = [
    { path: '/', name: 'Landing', component: Landing},
    { path: '/login', name: 'Login', component: Login},
    { path: '/register', name: 'Registration', component: Registration},
    { path: '/admin_dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' }},
    { path: '/user_dashboard', name: 'UserDashboard', component: UserDashboard, meta: { requiresAuth: true, role: 'user'}},
    { path: '/quiz_dashboard', name: 'QuizDashboard', component: QuizDashboard, meta: { requiresAuth: true, role: 'admin'}},
    { path: '/questions/:quiz_id', name: 'Questions', component: QuestionsPage, meta: { requiresAuth: true, role: 'admin'}},
    { path: '/user/score/:id', name: 'UserScore', component: UserScore, meta: { requiresAuth: true, role: 'user'}},
    { path: '/user/startquiz/:quiz_id', name: 'UserQuiz', component: UserQuiz, meta: { requiresAuth: true, role: 'user'}},
    { path: '/Summary_dashboard', name: 'SummaryPage ', component: SummaryPage, meta: {requiresAuth: true, allowedRoles: ['admin', 'user']}},
    { path: '/unauthorized', name: 'Unauthorized', component: UnauthorizedPage }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (to.meta.requiresAuth) {
    if (!token) {
      return next('/login');
    }

    if (to.meta.allowedRoles && !to.meta.allowedRoles.includes(role)) {
      return next('/unauthorized'); 
    }
  }

  next();
});


export default router;