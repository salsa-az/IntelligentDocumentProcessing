<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Authenticating with Microsoft...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthCallback',
  async mounted() {
    try {
      // Check session status from backend
      const response = await fetch('/api/session-status', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        
        if (data.status === 'authenticated') {
          // Store user in localStorage
          localStorage.setItem('user', JSON.stringify(data.user))
          
          // Redirect based on role
          if (data.user.role === 'approver') {
            this.$router.push('/claim-approval')
          } else if (data.user.role === 'customer') {
            this.$router.push('/customer-dashboard')
          } else {
            this.$router.push('/dashboard')
          }
        } else {
          this.$router.push('/signin?error=session_invalid')
        }
      } else {
        this.$router.push('/signin?error=auth_failed')
      }
    } catch (error) {
      console.error('Session check error:', error)
      this.$router.push('/signin?error=network_error')
    }
  }
}
</script>