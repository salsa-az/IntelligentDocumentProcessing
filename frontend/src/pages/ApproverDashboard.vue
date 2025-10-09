<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <Sidebar :sidebarOpen="sidebarOpen" @close-sidebar="sidebarOpen = false" />

    <!-- Content area -->
    <div class="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
      <!-- Site header -->
      <Header :sidebarOpen="sidebarOpen" @toggle-sidebar="sidebarOpen = !sidebarOpen" />

      <main class="grow">
        <div class="px-4 sm:px-6 lg:px-8 py-2 w-full max-w-9xl mx-auto">
          <!-- Page header -->
          <div class="mb-8">
            <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Analytics Dashboard</h1>
            <p class="text-gray-600 dark:text-gray-400">Monitor claims and performance metrics</p>
          </div>

          <!-- Power BI Dashboard -->
          <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-3">
            <iframe 
              title="IDP_Report" 
              width="100%" 
              height="600" 
              src="https://app.fabric.microsoft.com/reportEmbed?reportId=e63a983d-e25c-4f42-9c4b-339a6c8b5c16&autoAuth=true&ctid=4df3b246-bbff-4955-a9ad-350ddff8edff&actionBarEnabled=true&reportCopilotInEmbed=true" 
              frameborder="0" 
              allowFullScreen="true"
            ></iframe>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import Sidebar from '../partials/Sidebar.vue'
import Header from '../partials/Header.vue'

export default {
  name: 'ApproverDashboard',
  components: {
    Sidebar,
    Header
  },
  setup() {
    const sidebarOpen = ref(false)
    
    return {
      sidebarOpen
    }
  }
}
</script>
