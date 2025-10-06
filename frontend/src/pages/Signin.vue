<template>
  <main class="bg-white dark:bg-gray-900">
    <div class="relative flex">
      <!-- Content -->
      <div class="w-full">
        <div class="min-h-[100dvh] h-full flex flex-col justify-center">
          <div class="max-w-sm mx-auto w-full px-4 py-8">
            <!-- Logo -->
            <div class="flex justify-center mb-8">
              <img src="/src/images/logo.svg" alt="App Logo" class="w-8 h-8 lg:w-10 lg:h-10" />
                <span class="ml-2 text-lg font-semibold text-gray-800 dark:text-gray-100 lg:opacity-0 lg:sidebar-expanded:opacity-100 2xl:opacity-100 duration-200">Nexclaim</span>
            </div>

            <!-- Form -->
            <div class="rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8">
              <!-- Demo Credentials
              <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
                <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">Demo Credentials:</h3>
                <div class="text-xs text-blue-700 dark:text-blue-300 space-y-1">
                  <div><strong>Customer:</strong> customer@example.com / password123</div>
                  <div><strong>Approver:</strong> approver@example.com / password123</div>
                </div>
              </div> -->

              <!-- Error Message -->
              <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg">
                <p class="text-sm text-red-700 dark:text-red-300">{{ errorMessage }}</p>
              </div>

              <form @submit.prevent="handleSignin">
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="email">Email Address <span class="text-red-500">*</span></label>
                    <input id="email" v-model="form.email" class="form-input w-full" type="email" required />
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1" for="password">Password <span class="text-red-500">*</span></label>
                    <input id="password" v-model="form.password" class="form-input w-full" type="password" required />
                  </div>
                </div>
                <div class="flex items-center justify-between mt-6">
                  <div class="mr-1">
                    <label class="flex items-center">
                      <input type="checkbox" class="form-checkbox" />
                      <span class="text-sm ml-2">Ingat Saya</span>
                    </label>
                  </div>
                  <router-link class="text-sm underline hover:no-underline" to="/reset-password">Lupa Password?</router-link>
                </div>
                <div class="flex flex-wrap items-center justify-between mt-6">
                  <button :disabled="loading" class="btn bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white ml-3 w-full shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50">
                    {{ loading ? 'Signing In...' : 'Sign In' }}
                  </button>
                </div>
              </form>
            </div>
            <!-- Footer -->
            <div class="pt-5 mt-6 border-t border-gray-200 dark:border-gray-700/60">
              <div class="text-sm">
                Belum mempunyai akun? <router-link class="font-medium text-violet-500 hover:text-violet-600 dark:hover:text-violet-400" to="/signup">Sign Up</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import { authenticateUser } from '../utils/dummyUsers.js'

export default {
  name: 'Signin',
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      loading: false,
      errorMessage: ''
    }
  },
  methods: {
    async handleSignin() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        const response = await fetch('http://localhost:5000/api/signin', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: this.form.email,
            password: this.form.password
          })
        })
        
        const data = await response.json()
        
        if (response.ok && data.status === 'success') {
          // Store user and token in localStorage
          localStorage.setItem('user', JSON.stringify(data.user))
          localStorage.setItem('token', data.token)
          
          // Redirect based on role
          if (data.user.role === 'customer') {
            this.$router.push('/customer-dashboard')
          } else if (data.user.role === 'approver') {
            this.$router.push('/claim-approval')
          } else {
            this.$router.push('/dashboard')
          }
        } else {
          // Fallback to dummy users if API fails
          const dummyUser = authenticateUser(this.form.email, this.form.password)
          if (dummyUser) {
            localStorage.setItem('user', JSON.stringify(dummyUser))
            if (dummyUser.role === 'customer') {
              this.$router.push('/customer-dashboard')
            } else if (dummyUser.role === 'approver') {
              this.$router.push('/claim-approval')
            }
          } else {
            this.errorMessage = data.error || 'Email atau password salah. Silakan coba lagi.'
          }
        }
      } catch (error) {
        this.errorMessage = 'Terjadi kesalahan. Silakan coba lagi.'
        console.error('Sign in error:', error)
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    // Check if user is already logged in
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (user.id) {
      if (user.role === 'customer') {
        this.$router.push('/customer-dashboard')
      } else if (user.role === 'approver') {
        this.$router.push('/claim-approval')
      } else {
        this.$router.push('/dashboard')
      }
    }
  }
}
</script>