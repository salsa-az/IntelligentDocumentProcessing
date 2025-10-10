import { ref, computed } from 'vue'


// Global reactive state
const currentUser = ref(null)

export const useAuth = () => {
  // Initialize user from localStorage
  const initializeUser = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        currentUser.value = JSON.parse(storedUser)
      } catch (error) {
        console.error('Error parsing stored user:', error)
        localStorage.removeItem('user')
      }
    }
  }

  // Login user
  const login = (user) => {
    currentUser.value = user
    localStorage.setItem('user', JSON.stringify(user))
  }

  // Logout user
  const logout = async () => {
    try {
      // Call backend logout API to clear session
      await fetch('/api/logout', {
        method: 'POST',
        credentials: 'include'
      })
    } catch (error) {
      console.error('Logout API error:', error)
    } finally {
      // Always clear frontend state
      currentUser.value = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      sessionStorage.clear()
    }
  }

  // Update user data
  const updateUser = (userData) => {
    if (currentUser.value) {
      currentUser.value = { ...currentUser.value, ...userData }
      localStorage.setItem('user', JSON.stringify(currentUser.value))
    }
  }

  // Refresh user data from storage
  const refreshUser = () => {
    // User data refresh now handled by backend session
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        currentUser.value = JSON.parse(storedUser)
      } catch (error) {
        console.error('Error parsing stored user:', error)
        localStorage.removeItem('user')
      }
    }
  }

  // Computed properties
  const isAuthenticated = computed(() => !!currentUser.value?.id)
  const userRole = computed(() => currentUser.value?.role || null)
  const isCustomer = computed(() => userRole.value === 'customer')
  const isApprover = computed(() => userRole.value === 'approver')

  // Initialize on first use
  if (!currentUser.value) {
    initializeUser()
  }

  return {
    currentUser: computed(() => currentUser.value),
    isAuthenticated,
    userRole,
    isCustomer,
    isApprover,
    login,
    logout,
    updateUser,
    refreshUser,
    initializeUser
  }
}