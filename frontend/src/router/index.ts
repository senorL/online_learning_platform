import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue') },
    {
      path: '/',
      component: () => import('../views/LayoutView.vue'),
      children: [
        { 
          path: '', 
          redirect: () => {
            const role = localStorage.getItem('role')
            return role === 'admin' ? '/admin/questions' : '/courses'
          }
        },
        { path: 'courses', name: 'Courses', component: () => import('../views/CourseListView.vue') },
        { path: 'quiz', name: 'Quiz', component: () => import('../views/QuizView.vue') },
        { path: 'wrong-book', name: 'WrongBook', component: () => import('../views/WrongBookView.vue') },
        { path: 'heatmap', name: 'Heatmap', component: () => import('../views/HeatmapView.vue') },
        { path: 'ranking', name: 'Ranking', component: () => import('../views/RankingView.vue') },
        { path: 'profile', name: 'Profile', component: () => import('../views/ProfileView.vue') },
        { path: 'admin', redirect: '/admin/questions' },
        { path: 'admin/:tab', name: 'Admin', component: () => import('../views/AdminView.vue') },
      ],
    },
  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
