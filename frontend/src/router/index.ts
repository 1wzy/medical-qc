// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layouts/Layout.vue'
import Login from '@/views/Login.vue'
import RuleManage from '@/views/RuleManage.vue'
import RuleSetManage from '@/views/RuleSetManage.vue'
import BatchManage from '@/views/BatchManage.vue'
import DocumentUpload from '@/views/DocumentUpload.vue'
import ApiTest from '@/views/ApiTest.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    redirect: '/'
  },
  {
    path: '/rule',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      { path: 'manage', name: 'RuleManage', component: RuleManage },
      { path: 'set', name: 'RuleSetManage', component: RuleSetManage }
    ]
  },
  {
    path: '/upload',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'DocumentUpload', component: DocumentUpload }
    ]
  },
  {
    path: '/batches',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'BatchManage', component: BatchManage }
    ]
  },
  {
    path: '/api-test',
    component: Layout,
    meta: { requiresAuth: false }, // 测试页面不需要登录
    children: [
      { path: '', name: 'ApiTest', component: ApiTest }
    ]
  },
  // 兼容旧路由
  {
    path: '/rules',
    redirect: '/rule/manage'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：未登录时跳转到登录页
router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'

  // 如果访问需要认证的页面且未登录，跳转到登录页
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/')
    return
  }

  // 如果已登录但访问登录页（根路径），重定向到首页
  if (to.path === '/' && isLoggedIn) {
    next('/rule/manage')
    return
  }

  next()
})

export default router