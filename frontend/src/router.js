import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './pages/Dashboard.vue'
import CustomerDashboard from './pages/CustomerDashboard.vue'
import FormClaim from './pages/FormClaim.vue'
import ClaimHistory from './pages/ClaimHistory.vue'
import Signin from './pages/Signin.vue'
import Signup from './pages/Signup.vue'
import ResetPassword from './pages/ResetPassword.vue'
import MyAccount from './pages/MyAccount.vue'
import ClaimApproval from './pages/ClaimApproval.vue'
import AlertDemo from './pages/AlertDemo.vue'

const routerHistory = createWebHistory()

const router = createRouter({
  history: routerHistory,
  routes: [
    {
      path: '/',
      redirect: '/signin'
    },
    {
      path: '/signin',
      component: Signin
    },
    {
      path: '/signup',
      component: Signup
    },
    {
      path: '/reset-password',
      component: ResetPassword,
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      component: Dashboard
    },
    {
      path: '/customer-dashboard',
      component: CustomerDashboard,
      meta: { requiresAuth: true, role: 'customer' } 
    },
    {
      path: '/claim-form',
      name: 'FormClaim',
      component: FormClaim,
      meta: { requiresAuth: true, role: 'customer' } 
    },
    {
      path: '/claim-history',
      component: ClaimHistory,
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/my-account',
      component: MyAccount,
      meta: { requiresAuth: true }
    },
    {
      path: '/claim-approval',
      component: ClaimApproval,
      meta: { requiresAuth: true, role: 'approver' }
    },
    {
      path: '/alert-demo',
      component: AlertDemo
    },
  ]
})

router.beforeEach((to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  
  if (to.meta.requiresAuth && !user.id) {
    next('/signin')
  } else if (to.meta.role && user.role !== to.meta.role) {
    next(user.role === 'approver' ? '/claim-approval' : '/customer-dashboard')
  } else {
    next()
  }
})

export default router
