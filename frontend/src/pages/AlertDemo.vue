<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <Sidebar :sidebarOpen="sidebarOpen" @close-sidebar="sidebarOpen = false" />

    <!-- Content area -->
    <div class="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
      <!-- Site header -->
      <Header :sidebarOpen="sidebarOpen" @toggle-sidebar="sidebarOpen = !sidebarOpen" />

      <main class="grow">
        <div class="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-4xl mx-auto">
          <!-- Page header -->
          <div class="mb-8">
            <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Alert Demo</h1>
            <p class="text-gray-600 dark:text-gray-400">Test all alert types and variations</p>
          </div>

          <!-- Alert Buttons -->
          <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-6 mb-6">
            <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Alert Types</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button 
                @click="showSuccessAlert"
                class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
              >
                Success Alert
              </button>
              <button 
                @click="showErrorAlert"
                class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Error Alert
              </button>
              <button 
                @click="showWarningAlert"
                class="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
              >
                Warning Alert
              </button>
              <button 
                @click="showInfoAlert"
                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Info Alert
              </button>
            </div>
          </div>

          <!-- Scenario Alerts -->
          <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-6 mb-6">
            <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Scenario Alerts</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button 
                @click="showClaimSubmittedAlert"
                class="px-4 py-2 bg-violet-600 text-white rounded hover:bg-violet-700 transition-colors"
              >
                Claim Submitted (Customer)
              </button>
              <button 
                @click="showClaimApprovedAlert"
                class="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 transition-colors"
              >
                Claim Approved (Admin)
              </button>
              <button 
                @click="showClaimRejectedAlert"
                class="px-4 py-2 bg-rose-600 text-white rounded hover:bg-rose-700 transition-colors"
              >
                Claim Rejected (Admin)
              </button>
              <button 
                @click="showSystemErrorAlert"
                class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
              >
                System Error
              </button>
            </div>
          </div>

          <!-- Multiple Alerts -->
          <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-6">
            <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Multiple Alerts</h2>
            <div class="flex gap-4">
              <button 
                @click="showMultipleAlerts"
                class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors"
              >
                Show Multiple Alerts
              </button>
              <button 
                @click="clearAllAlerts"
                class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
              >
                Clear All Alerts
              </button>
            </div>
          </div>
        </div>
      </main>

      <Banner />
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import Sidebar from '../partials/Sidebar.vue'
import Header from '../partials/Header.vue'
import Banner from '../partials/AIAssistant.vue'
import { useAlert } from '../composables/useAlert.js'

export default {
  name: 'AlertDemo',
  components: {
    Sidebar,
    Header,
    Banner,
  },
  setup() {
    const sidebarOpen = ref(false)
    const { showSuccess, showError, showWarning, showInfo, clearAllAlerts } = useAlert()

    const showSuccessAlert = () => {
      showSuccess(
        'Success!',
        'This is a success alert message. Everything went well!'
      )
    }

    const showErrorAlert = () => {
      showError(
        'Error Occurred',
        'This is an error alert message. Something went wrong!'
      )
    }

    const showWarningAlert = () => {
      showWarning(
        'Warning!',
        'This is a warning alert message. Please be careful!'
      )
    }

    const showInfoAlert = () => {
      showInfo(
        'Information',
        'This is an info alert message. Here is some useful information.'
      )
    }

    const showClaimSubmittedAlert = () => {
      showSuccess(
        'Klaim Berhasil Diajukan!',
        'Klaim Anda telah berhasil disubmit dengan ID: CLM-2024-001. Tim kami akan memproses klaim Anda dalam 1-3 hari kerja.'
      )
    }

    const showClaimApprovedAlert = () => {
      showSuccess(
        'Klaim Disetujui!',
        'Klaim CLM-2024-001 dari John Doe telah berhasil disetujui. Nasabah akan menerima notifikasi persetujuan.'
      )
    }

    const showClaimRejectedAlert = () => {
      showError(
        'Klaim Ditolak',
        'Klaim CLM-2024-002 dari Jane Smith telah ditolak. Nasabah akan menerima notifikasi penolakan beserta alasannya.'
      )
    }

    const showSystemErrorAlert = () => {
      showError(
        'Kesalahan Sistem',
        'Terjadi kesalahan koneksi. Silakan periksa koneksi internet Anda dan coba lagi.'
      )
    }

    const showMultipleAlerts = () => {
      showSuccess('First Alert', 'This is the first alert')
      setTimeout(() => showWarning('Second Alert', 'This is the second alert'), 500)
      setTimeout(() => showInfo('Third Alert', 'This is the third alert'), 1000)
      setTimeout(() => showError('Fourth Alert', 'This is the fourth alert'), 1500)
    }

    return {
      sidebarOpen,
      showSuccessAlert,
      showErrorAlert,
      showWarningAlert,
      showInfoAlert,
      showClaimSubmittedAlert,
      showClaimApprovedAlert,
      showClaimRejectedAlert,
      showSystemErrorAlert,
      showMultipleAlerts,
      clearAllAlerts
    }
  }
}
</script>