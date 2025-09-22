<template>
  <div class="relative inline-flex">
    <button
      ref="trigger"
      class="inline-flex justify-center items-center group"
      aria-haspopup="true"
      @click.prevent="dropdownOpen = !dropdownOpen"
      :aria-expanded="dropdownOpen"
    >
      <img class="w-8 h-8 rounded-full" :src="currentUser?.avatar || UserAvatar" width="32" height="32" alt="User" />
      <div class="flex items-center truncate">
        <span class="truncate ml-2 text-sm font-medium text-gray-600 dark:text-gray-100 group-hover:text-gray-800 dark:group-hover:text-white">{{ currentUser?.fullName || 'User' }}</span>
        <svg class="w-3 h-3 shrink-0 ml-1 fill-current text-gray-400 dark:text-gray-500" viewBox="0 0 12 12">
          <path d="M5.9 11.4L.5 6l1.4-1.4 4 4 4-4L11.3 6z" />
        </svg>
      </div>
    </button>
    <transition
      enter-active-class="transition ease-out duration-200 transform"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-out duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-show="dropdownOpen" class="origin-top-right z-10 absolute top-full min-w-44 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700/60 py-1.5 rounded-lg shadow-lg overflow-hidden mt-1" :class="align === 'right' ? 'right-0' : 'left-0'">
        <div class="pt-0.5 pb-2 px-3 mb-1 border-b border-gray-200 dark:border-gray-700/60">
          <div class="font-medium text-gray-800 dark:text-gray-100">{{ currentUser?.fullName || 'User' }}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400 italic">{{ currentUser?.role === 'customer' ? 'Customer' : currentUser?.role === 'approver' ? 'Approver' : 'User' }}</div>
        </div>
        <ul
          ref="dropdown"
          @focusin="dropdownOpen = true"
          @focusout="dropdownOpen = false"
        >
          <li>
            <router-link class="font-medium text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white flex items-center py-1 px-3" to="/my-account" @click="dropdownOpen = false">
              <svg class="w-3 h-3 fill-current text-gray-400 dark:text-gray-500 shrink-0 mr-1" viewBox="0 0 12 12">
                <path d="M6 8a3 3 0 100-6 3 3 0 000 6zM6 10c-2.67 0-8 1.34-8 4v1h16v-1c0-2.66-5.33-4-8-4z" />
              </svg>
              My Account
            </router-link>
          </li>
          <li v-if="currentUser?.role === 'customer'">
            <router-link class="font-medium text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white flex items-center py-1 px-3" to="/claim-history" @click="dropdownOpen = false">
              <svg class="w-3 h-3 fill-current text-gray-400 dark:text-gray-500 shrink-0 mr-1" viewBox="0 0 12 12">
                <path d="M10.5 0h-9A1.5 1.5 0 000 1.5v9A1.5 1.5 0 001.5 12h9a1.5 1.5 0 001.5-1.5v-9A1.5 1.5 0 0010.5 0zM10 7L8.207 5.207l-3 3-1.414-1.414 3-3L5 2h5v5z" />
              </svg>
              Claim History
            </router-link>
          </li>
          <li v-if="currentUser?.role === 'approver'">
            <router-link class="font-medium text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white flex items-center py-1 px-3" to="/claim-approval" @click="dropdownOpen = false">
              <svg class="w-3 h-3 fill-current text-gray-400 dark:text-gray-500 shrink-0 mr-1" viewBox="0 0 12 12">
                <path d="M10.5 0h-9A1.5 1.5 0 000 1.5v9A1.5 1.5 0 001.5 12h9a1.5 1.5 0 001.5-1.5v-9A1.5 1.5 0 0010.5 0zM10 7L8.207 5.207l-3 3-1.414-1.414 3-3L5 2h5v5z" />
              </svg>
              Claim Approval
            </router-link>
          </li>
          <li>
            <button 
              class="font-medium text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white flex items-center py-1 px-3 w-full text-left" 
              @click="handleSignOut"
            >
              <svg class="w-3 h-3 fill-current text-gray-400 dark:text-gray-500 shrink-0 mr-1" viewBox="0 0 12 12">
                <path d="M10.28 2.28L3.989 8.575 1.695 6.28A1 1 0 00.28 7.695l3 3a1 1 0 001.414 0l7-7A1 1 0 0010.28 2.28z" />
              </svg>
              Sign Out
            </button>
          </li>
        </ul>
      </div> 
    </transition>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import UserAvatar from '../images/user-avatar-32.png'

export default {
  name: 'DropdownProfile',
  props: ['align'],
  data() {
    return {
      UserAvatar: UserAvatar,
    }
  },  
  setup() {
    const router = useRouter()
    const { currentUser, logout } = useAuth()
    const dropdownOpen = ref(false)
    const trigger = ref(null)
    const dropdown = ref(null)

    // Handle sign out
    const handleSignOut = () => {
      logout()
      dropdownOpen.value = false
      router.push('/signin')
    }

    // close on click outside
    const clickHandler = ({ target }) => {
      if (!dropdownOpen.value || dropdown.value.contains(target) || trigger.value.contains(target)) return
      dropdownOpen.value = false
    }

    // close if the esc key is pressed
    const keyHandler = ({ keyCode }) => {
      if (!dropdownOpen.value || keyCode !== 27) return
      dropdownOpen.value = false
    }

    onMounted(() => {
      document.addEventListener('click', clickHandler)
      document.addEventListener('keydown', keyHandler)
    })

    onUnmounted(() => {
      document.removeEventListener('click', clickHandler)
      document.removeEventListener('keydown', keyHandler)
    })

    return {
      currentUser,
      dropdownOpen,
      trigger,
      dropdown,
      handleSignOut,
    }
  }
}
</script>