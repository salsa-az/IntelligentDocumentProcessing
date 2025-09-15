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
              <form @submit.prevent="handleReset">
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="email">Email Address <span class="text-red-500">*</span></label>
                    <input id="email" v-model="form.email" class="form-input w-full" type="email" required />
                  </div>
                </div>
                <div class="flex flex-wrap items-center justify-between mt-6">
                  <button class="btn bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white w-full shadow-lg hover:shadow-xl transition-all duration-200">Send Reset Link</button>
                </div>
              </form>
            </div>
            <!-- Footer -->
            <div class="pt-5 mt-6 border-t border-gray-200 dark:border-gray-700/60">
              <div class="text-sm">
                <router-link class="font-medium text-violet-500 hover:text-violet-600 dark:hover:text-violet-400" to="/signin">← Back to Sign In</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
export default {
  name: 'ResetPassword',
  data() {
    return {
      form: {
        email: ''
      }
    }
  },
  methods: {
    handleReset() {
      // Handle reset password logic
      console.log('Reset password for:', this.form.email)
      alert('Reset link sent to your email!')
    }
  }
}
</script>