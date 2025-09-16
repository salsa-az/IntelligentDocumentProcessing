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
      component: ResetPassword
    },
    {
      path: '/dashboard',
      component: Dashboard
    },
    {
      path: '/customer-dashboard',
      component: CustomerDashboard
    },
    {
      path: '/claim-form',
      component: FormClaim
    },
    {
      path: '/claim-history',
      component: ClaimHistory
    },
    {
      path: '/my-account',
      component: MyAccount
    },
    {
      path: '/claim-approval',
      component: ClaimApproval
    },
    {
      path: '/alert-demo',
      component: AlertDemo
    },
  ]
})

export default router
