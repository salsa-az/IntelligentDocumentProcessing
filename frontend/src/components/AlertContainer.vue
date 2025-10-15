<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <div v-for="alert in alerts" :key="alert.id" role="alert">
      <div class="inline-flex text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-4 min-w-80">
        <div class="flex items-start space-x-3 flex-1">
          <div class="flex">
            <svg v-if="alert.type === 'success'" class="fill-green-600 w-4 h-4 mt-0.5 flex-shrink-0" width="16" height="16" viewBox="0 0 16 16">
              <path d="M8 0C3.6 0 0 3.6 0 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zM7 11.4L3.6 8 5 6.6l2 2 4-4L12.4 6 7 11.4z"></path>
            </svg>
            <svg v-else-if="alert.type === 'error'" class="fill-red-600 w-4 h-4 mt-0.5 flex-shrink-0" width="16" height="16" viewBox="0 0 16 16">
              <path d="M8 0C3.6 0 0 3.6 0 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm3.5 10.1l-1.4 1.4L8 9.4l-2.1 2.1-1.4-1.4L6.6 8 4.5 5.9l1.4-1.4L8 6.6l2.1-2.1 1.4 1.4L9.4 8l2.1 2.1z"></path>
            </svg>
            <svg v-else-if="alert.type === 'warning'" class="fill-yellow-600 w-4 h-4 mt-0.5 flex-shrink-0" width="16" height="16" viewBox="0 0 16 16">
              <path d="M8 0C3.6 0 0 3.6 0 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 12c-.6 0-1-.4-1-1s.4-1 1-1 1 .4 1 1-.4 1-1 1zm1-3H7V4h2v5z"></path>
            </svg>
            <svg v-else class="fill-blue-600 w-4 h-4 mt-0.5 flex-shrink-0" width="16" height="16" viewBox="0 0 16 16">
              <path d="M8 0C3.6 0 0 3.6 0 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm1 12H7V7h2v5zM8 6c-.6 0-1-.4-1-1s.4-1 1-1 1 .4 1 1-.4 1-1 1z"></path>
            </svg>
            <div class="ml-3">
              <div v-if="alert.title" class="text-gray-800 dark:text-gray-100 font-medium">{{ alert.title }}</div>
              <div class="text-gray-600 dark:text-gray-400">{{ alert.message }}</div>
            </div>
          </div>
          <button @click="removeAlert(alert.id)" class="ml-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 flex-shrink-0">
            <span class="sr-only">Close</span>
            <svg class="w-4 h-4" width="16" height="16" viewBox="0 0 16 16">
              <path d="M7.95 6.536l4.242-4.243a1 1 0 111.415 1.414L9.364 7.95l4.243 4.242a1 1 0 11-1.415 1.415L7.95 9.364l-4.243 4.243a1 1 0 01-1.414-1.415L6.536 7.95 2.293 3.707a1 1 0 011.414-1.414L7.95 6.536z"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAlert } from '../composables/useAlert.js'

export default {
  name: 'AlertContainer',
  setup() {
    const { alerts, removeAlert } = useAlert()

    return {
      alerts,
      removeAlert
    }
  }
}
</script>