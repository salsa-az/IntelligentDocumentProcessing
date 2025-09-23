<template>
  <main class="bg-white dark:bg-gray-900">
    <div class="relative flex">
      <!-- Content -->
      <div class="w-full">
        <div class="min-h-[100dvh] h-full flex flex-col justify-center">
          <div class="max-w-sm mx-auto w-full px-4 py-8">
            <!-- Logo -->
            <div class="flex justify-center mb-8">
              <svg class="fill-violet-500" xmlns="http://www.w3.org/2000/svg" width="48" height="48">
                <path d="M31.956 14.8C31.372 6.92 25.08.628 17.2.044V5.76a9.04 9.04 0 0 0 9.04 9.04h5.716ZM14.8 26.24v5.716C6.92 31.372.63 25.08.044 17.2H5.76a9.04 9.04 0 0 1 9.04 9.04Zm11.44-9.04h5.716c-.584 7.88-6.876 14.172-14.756 14.756V26.24a9.04 9.04 0 0 1 9.04-9.04ZM.044 14.8C.63 6.92 6.92.628 14.8.044V5.76a9.04 9.04 0 0 1-9.04 9.04H.044Z" />
              </svg>
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
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 500))
        
        const user = authenticateUser(this.form.email, this.form.password)
        
        if (user) {
          // Store user in localStorage
          localStorage.setItem('user', JSON.stringify(user))
          
          // Redirect based on role
          if (user.role === 'customer') {
            this.$router.push('/customer-dashboard')
          } else if (user.role === 'approver') {
            this.$router.push('/claim-approval')
          } else {
            this.$router.push('/dashboard')
          }
        } else {
          this.errorMessage = 'Email atau password salah. Silakan coba lagi.'
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