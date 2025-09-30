<template>
  <div class="relative inline-flex">
    <button
      ref="trigger"
      class="inline-flex justify-center items-center group"
      aria-haspopup="true"
      @click.prevent="dropdownOpen = !dropdownOpen"
      :aria-expanded="dropdownOpen"
    >
      <img class="w-8 h-8 rounded-full" :src="profilePicture || UserAvatar" width="32" height="32" alt="User" />
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
            <svg class="shrink-0 fill-current mr-1" :class="isExactActive ? 'text-violet-500' : 'text-gray-400 dark:text-gray-500'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
              <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM12.735 14c.618 0 1.093-.561.872-1.139a6.002 6.002 0 0 0-11.215 0c-.22.578.254 1.139.872 1.139h9.47Z" />
            </svg>
              My Account
            </router-link>
          </li>
          <li v-if="currentUser?.role === 'customer'">
            <router-link class="font-medium text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white flex items-center py-1 px-3" to="/claim-history" @click="dropdownOpen = false">
              <svg class="w-3 h-3 fill-current text-gray-400 dark:text-gray-500 shrink-0 mr-2" viewBox="0 0 12 12">
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
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 fill-current text-gray-400 dark:text-gray-500 shrink-0 mr-1" viewBox="0 0 18 18"><title>arrow door out 3</title><g class="nc-icon-wrapper"><path d="M11.75,11.5c-.414,0-.75,.336-.75,.75v2.5c0,.138-.112,.25-.25,.25H5.448l1.725-1.069c.518-.322,.827-.878,.827-1.487V5.557c0-.609-.31-1.166-.827-1.487l-1.725-1.069h5.302c.138,0,.25,.112,.25,.25v2.5c0,.414,.336,.75,.75,.75s.75-.336,.75-.75V3.25c0-.965-.785-1.75-1.75-1.75H4.25c-.965,0-1.75,.785-1.75,1.75V14.75c0,.965,.785,1.75,1.75,1.75h6.5c.965,0,1.75-.785,1.75-1.75v-2.5c0-.414-.336-.75-.75-.75Z"/><path d="M17.78,8.47l-2.75-2.75c-.293-.293-.768-.293-1.061,0s-.293,.768,0,1.061l1.47,1.47h-4.189c-.414,0-.75,.336-.75,.75s.336,.75,.75,.75h4.189l-1.47,1.47c-.293,.293-.293,.768,0,1.061,.146,.146,.338,.22,.53,.22s.384-.073,.53-.22l2.75-2.75c.293-.293,.293-.768,0-1.061Z" data-color="color-2"/></g>
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