import { createRouter, createWebHistory } from 'vue-router'
import CustomerDashboard from './pages/CustomerDashboard.vue'
import FormClaim from './pages/FormClaim.vue'
import ClaimHistory from './pages/ClaimHistory.vue'
import Signin from './pages/Signin.vue'
// import ResetPassword from './pages/ResetPassword.vue'
import MyAccount from './pages/MyAccount.vue'
import ClaimApproval from './pages/ClaimApproval.vue'
import AutoSignup from './pages/AutoSignup.vue'
import ApproverDashboard from './pages/ApproverDashboard.vue'

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
      component: Signin,
      meta: { title: 'Sign In' }
    },
    {
      path: '/signup',
      component: AutoSignup,
      meta: { title: 'Sign Up' }
    },
    // {
    //   path: '/dashboard',
    //   component: Dashboard,
    //   meta: { title: 'Dashboard' }
    // },
    {
      path: '/customer-dashboard',
      component: CustomerDashboard,
      meta: { requiresAuth: true, role: 'customer', title: 'Customer Dashboard' } 
    },
    {
      path: '/claim-form',
      name: 'FormClaim',
      component: FormClaim,
      meta: { requiresAuth: true, role: 'customer', title: 'New Claim' } 
    },
    {
      path: '/claim-history',
      component: ClaimHistory,
      meta: { requiresAuth: true, role: 'customer', title: 'Claim History' }
    },
    {
      path: '/my-account',
      component: MyAccount,
      meta: { requiresAuth: true, title: 'My Account' }
    },
    {
      path: '/claim-approval',
      component: ClaimApproval,
      meta: { requiresAuth: true, role: 'approver', title: 'Claim Approval' }
    },
    {
      path: '/approver-dashboard',
      component: ApproverDashboard,
      meta: { requiresAuth: true, role: 'approver', title: 'Approver Dashboard' }
    },
    {
      path: '/auto-signup',
      component: AutoSignup,
      meta: { title: 'Auto Signup' }
    }
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
