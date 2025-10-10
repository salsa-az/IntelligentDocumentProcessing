<template>
  <div class="flex h-screen overflow-hidden">

    <!-- Sidebar -->
    <Sidebar :sidebarOpen="sidebarOpen" @close-sidebar="sidebarOpen = false" />

    <!-- Content area -->
    <div class="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
      
      <!-- Site header -->
      <Header :sidebarOpen="sidebarOpen" @toggle-sidebar="sidebarOpen = !sidebarOpen" />

      <main class="grow">
        <div class="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-9xl mx-auto">

          <!-- Dashboard actions -->
          <div class="sm:flex sm:justify-between sm:items-center mb-8">

            <!-- Left: Title -->
            <div class="mb-4 sm:mb-0">
              <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Dashboard Asuransi</h1>
            </div>

            <!-- Right: Actions -->
            <div class="grid grid-flow-col sm:auto-cols-max justify-start sm:justify-end gap-2">

              <!-- Filter button -->
              <!-- <FilterButton align="right" /> -->
              <!-- Datepicker built with flatpickr -->
              <!-- <Datepicker align="right" /> -->
              <!-- Submit Claim button -->
              <router-link to="/claim-form ">
                <button class="btn bg-gray-900 text-gray-100 hover:bg-gray-800 dark:bg-gray-100 dark:text-gray-800 dark:hover:bg-gray-200 transition-all duration-200 ease-in-out transform dark:hover:bg-gray-800 dark:hover:text-white hover:shadow-lg dark:hover:border-gray-200">
                    <svg class="fill-current shrink-0 xs:hidden" width="16" height="16" viewBox="0 0 16 16">
                        <path d="M15 7H9V1c0-.6-.4-1-1-1S7 .4 7 1v6H1c-.6 0-1 .4-1 1s.4 1 1 1h6v6c0 .6.4 1 1 1s1-.4 1-1V9h6c.6 0 1-.4 1-1s-.4-1-1-1z" />
                    </svg>
                    <span class="max-xs:sr-only">Ajukan Klaim</span>
                </button>
              </router-link>
              <!-- <button class="btn bg-blue-600 text-white hover:bg-blue-700">
                  <svg class="fill-current shrink-0 xs:hidden" width="16" height="16" viewBox="0 0 16 16">
                      <path d="M15 7H9V1c0-.6-.4-1-1-1S7 .4 7 1v6H1c-.6 0-1 .4-1 1s.4 1 1 1h6v6c0 .6.4 1 1 1s1-.4 1-1V9h6c.6 0 1-.4 1-1s-.4-1-1-1z" />
                  </svg>
                  <span class="max-xs:sr-only">Ajukan Klaim</span>
              </button> -->
            </div>

          </div>

          <!-- Greeting Card -->
          <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-6 mb-6 text-white">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold mb-1">Halo, {{ currentUser.name || 'User' }}</h2>
                <p class="text-blue-100 text-sm">Selamat datang kembali di dashboard asuransi Anda</p>
              </div>
              <div class="flex items-center space-x-4">
                <div class="text-right">
                  <div class="flex items-center text-sm text-blue-100">
                    <span class="bg-orange-500 text-white px-2 py-1 rounded text-xs font-medium mr-2 premium capitalize">{{ policyData.premiumType || 'Basic' }}</span>
                  </div>
                  <!-- <div class="text-xs text-blue-200">{{ policyData.policyNumber }}</div> -->
                </div>
              </div>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-500"></div>
          </div>

          <!-- Cards -->
          <div v-else class="grid grid-cols-12 gap-4">

            <!-- Policy Status -->
            <div class="col-span-12 sm:col-span-6">
              <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-5 overflow-hidden">
                <div class="flex items-center min-w-0">
                  <div class="flex-shrink-0">
                    <div class="flex items-center justify-center w-8 h-8 bg-violet-500 rounded-full">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-5 min-w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Total Claim Limit</dt>
                      <dd class="text-lg font-medium text-green-600 truncate">Rp {{ formatCurrency(policyData.claimLimit) }}</dd>
                      <dd class="text-sm text-gray-500 dark:text-gray-400 truncate">{{ policyData.premiumType || 'Basic' }} Plan</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <!-- Total Claim Amount -->
            <div class="col-span-12 sm:col-span-6">
              <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-5 overflow-hidden">
                <div class="flex items-center min-w-0">
                  <div class="flex-shrink-0">
                    <div class="flex items-center justify-center w-8 h-8 bg-blue-500 rounded-full">
                      <svg class="w-5.5 h-5.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-5 min-w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Total Jumlah Klaim</dt>
                      <dd class="text-lg font-medium text-gray-900 dark:text-gray-100 truncate">Rp {{ formatCurrency(totalClaimAmount) }}</dd>
                      <dd class="text-sm text-gray-500 dark:text-gray-400 truncate">Semua klaim yang diajukan</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <!-- Rejected Claims -->
            <div class="col-span-12 sm:col-span-4">
              <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-5 h-24 flex items-center overflow-hidden">
                <div class="flex items-center min-w-0 w-full">
                  <div class="flex-shrink-0">
                    <div class="flex items-center justify-center w-8 h-8 bg-red-500 rounded-full">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-3 min-w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Klaim Ditolak</dt>
                      <dd class="text-lg font-medium text-gray-900 dark:text-gray-100 truncate">{{ rejectedClaims.length }} Klaim</dd>
                      <dd class="text-sm text-gray-500 dark:text-gray-400 truncate">Rp {{ formatCurrency(rejectedAmount) }}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <!-- Approved Claims -->
            <div class="col-span-12 sm:col-span-4">
              <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-5 h-24 flex items-center overflow-hidden">
                <div class="flex items-center min-w-0 w-full">
                  <div class="flex-shrink-0">
                    <div class="flex items-center justify-center w-8 h-8 bg-green-500 rounded-full">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-3 min-w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Klaim Disetujui</dt>
                      <dd class="text-lg font-medium text-gray-900 dark:text-gray-100 truncate">{{ approvedClaims.length }} Klaim</dd>
                      <dd class="text-sm text-gray-500 dark:text-gray-400 truncate">Rp {{ formatCurrency(approvedAmount) }}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pending Claims -->
            <div class="col-span-12 sm:col-span-4">
              <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-5 h-24 flex items-center overflow-hidden">
                <div class="flex items-center min-w-0 w-full">
                  <div class="flex-shrink-0">
                    <div class="flex items-center justify-center w-8 h-8 bg-yellow-500 rounded-full">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-3 min-w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Klaim Menunggu</dt>
                      <dd class="text-lg font-medium text-gray-900 dark:text-gray-100 truncate">{{ pendingClaims.length }} Klaim</dd>
                      <dd class="text-sm text-gray-500 dark:text-gray-400 truncate">Rp {{ formatCurrency(pendingAmount) }}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <!-- Coverage Summary (Donut Chart) -->
            <div class="flex flex-col col-span-full sm:col-span-6 xl:col-span-4 bg-white dark:bg-gray-800 shadow-xs rounded-xl">
              <header class="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60">
                <h2 class="font-semibold text-gray-800 dark:text-gray-100">Cakupan Berdasarkan Jenis</h2>
              </header>
              <DoughnutChart :data="chartData" width="389" height="260" />
            </div>

            <!-- Recent Activity -->
            <div class="flex flex-col col-span-12 sm:col-span-6 xl:col-span-4 bg-white dark:bg-gray-800 shadow-xs rounded-xl overflow-hidden">
              <header class="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60">
                <h2 class="font-semibold text-gray-800 dark:text-gray-100 truncate">Aktivitas Terbaru</h2>
              </header>
              <div class="p-5 overflow-hidden">
                <div class="space-y-3">
                  <div v-for="activity in recentActivity" :key="activity.id" class="flex items-center space-x-3 min-w-0">
                    <div class="flex-shrink-0">
                      <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm text-gray-900 dark:text-gray-100 truncate">{{ activity.description }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ activity.date }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>





          </div>

        </div>
      </main>


    </div> 

  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import Sidebar from '../partials/Sidebar.vue'
import Header from '../partials/Header.vue'
import FilterButton from '../components/DropdownFilter.vue'
import Datepicker from '../components/Datepicker.vue'
import Banner from '../partials/Chatbot.vue'
import DoughnutChart from '../charts/DoughnutChart.vue'

export default {
  name: 'Dashboard',
  components: {
    Sidebar,
    Header,
    FilterButton,
    Datepicker,
    Banner,
    DoughnutChart,
  },
  setup() {
    const sidebarOpen = ref(false)
    const claims = ref([])
    const loading = ref(true)
    const currentUser = ref(JSON.parse(localStorage.getItem('user') || '{}'))

    // Policy data
    const policyData = ref({
      status: 'Active',
      policyNumber: 'P001',
      company: 'PT Asuransi Terpercaya',
      premiumType: 'Basic',
      claimLimit: 5000000
    })

    const coverageData = ref([
      { type: 'Rawat Inap', limit: 'Rp 100,000,000' },
      { type: 'Rawat Jalan', limit: 'Rp 25,000,000' },
      { type: 'Penyakit Kritis', limit: 'Rp 200,000,000' },
      { type: 'Medical Check-up', limit: 'Rp 5,000,000' }
    ])

    const premiumData = ref({
      nextDueDate: '15 Mar 2024',
      amount: 2500000,
      status: 'Paid'
    })

    const totalClaimAmount = computed(() => {
      return claims.value.reduce((total, claim) => total + claim.amount, 0)
    })

    const approvedClaims = computed(() => {
      return claims.value.filter(claim => claim.status === 'approved')
    })

    const approvedAmount = computed(() => {
      return approvedClaims.value.reduce((total, claim) => total + claim.amount, 0)
    })

    const pendingClaims = computed(() => {
      return claims.value.filter(claim => claim.status === 'proses' || claim.status === 'pengajuan')
    })

    const pendingAmount = computed(() => {
      return pendingClaims.value.reduce((total, claim) => total + claim.amount, 0)
    })

    const rejectedClaims = computed(() => {
      return claims.value.filter(claim => claim.status === 'rejected')
    })

    const rejectedAmount = computed(() => {
      return rejectedClaims.value.reduce((total, claim) => total + claim.amount, 0)
    })

    const recentActivity = computed(() => {
      return claims.value.slice(0, 3).map(claim => ({
        id: claim.claim_id,
        description: `Klaim ${claim.claim_id} - ${claim.hospitalName || 'Hospital'} (${getStatusText(claim.status)})`,
        date: formatDate(claim.claim_date)
      }))
    })

    const getStatusText = (status) => {
      const statusMap = {
        'approved': 'Disetujui',
        'rejected': 'Ditolak', 
        'proses': 'Dalam Proses'
      }
      return statusMap[status] || status
    }

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 1) return '1 hari yang lalu'
      if (diffDays < 7) return `${diffDays} hari yang lalu`
      if (diffDays < 30) return `${Math.ceil(diffDays / 7)} minggu yang lalu`
      return `${Math.ceil(diffDays / 30)} bulan yang lalu`
    }

    const chartData = computed(() => {
      const typeMap = {
        'rawat-inap': { name: 'Rawat Inap', color: '#1e40af', count: 0 },
        'rawat-jalan': { name: 'Rawat Jalan', color: '#0ea5e9', count: 0 },
        'pra-pasca-rawat-inap': { name: 'Pra/Pasca Rawat Inap', color: '#3b82f6', count: 0 },
        'kehamilan-melahirkan': { name: 'Kehamilan/Melahirkan', color: '#ec4899', count: 0 },
        'santunan-harian': { name: 'Santunan Harian', color: '#f59e0b', count: 0 },
        'gigi': { name: 'Gigi', color: '#10b981', count: 0 },
        'penyakit-kritis': { name: 'Penyakit Kritis', color: '#5b21b6', count: 0 },
        'medical-checkup': { name: 'Medical Checkup', color: '#9ca3af', count: 0 },
        'lainnya': { name: 'Lainnya', color: '#6b7280', count: 0 }
      }
      
      claims.value.forEach(claim => {
        const type = claim.claim_type || claim.type
        if (typeMap[type]) {
          typeMap[type].count += 1
        }
      })
      
      const types = Object.values(typeMap).filter(type => type.count > 0)
      
      return {
        labels: types.map(type => type.name),
        datasets: [{
          data: types.map(type => type.count),
          backgroundColor: types.map(type => type.color),
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      }
    })

    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('id-ID').format(amount)
    }

    const fetchClaims = async () => {
      loading.value = true
      try {
        const response = await fetch(`/api/customer-claim-history/${currentUser.value.id}`, {
          credentials: 'include'
        })
        const data = await response.json()
        if (data.status === 'success') {
          claims.value = data.claims.map(claim => ({
            ...claim,
            amount: claim.claim_amount,
            status: claim.claim_status.toLowerCase()
          }))
        }
      } catch (error) {
        console.error('Error fetching claims:', error)
      } finally {
        loading.value = false
      }
    }

    const fetchPolicyData = async () => {
      try {
        const response = await fetch(`/api/customer/${currentUser.value.id}/policy`, {
          credentials: 'include'
        })
        const data = await response.json()
        if (data.status === 'success' && data.policy) {
          policyData.value.premiumType = data.policy.insurance_plan_type || 'basic'
          policyData.value.claimLimit = data.policy.total_claim_limit || 5000000
        }
      } catch (error) {
        console.error('Error fetching policy:', error)
      }
    }

    onMounted(() => {
      document.title = 'Dashboard - NexClaim'
      fetchClaims()
      fetchPolicyData()
    })

    return {
      sidebarOpen,
      currentUser,
      totalClaimAmount,
      approvedClaims,
      approvedAmount,
      pendingClaims,
      pendingAmount,
      rejectedClaims,
      rejectedAmount,
      policyData,
      coverageData,
      premiumData,
      recentActivity,
      chartData,
      formatCurrency,
      loading
    }  
  }
}
</script>