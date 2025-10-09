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
          <!-- Page header -->
          <div class="mb-8">
            <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Approver - Claims Approval</h1>
            <p class="text-gray-600 dark:text-gray-400">Review and approve submitted insurance claims</p>
          </div>

          <!-- Filters and Search -->
          <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-6 mb-6">
            <div class="flex flex-col sm:flex-row gap-4">
              <!-- Search -->
              <div class="flex-1">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search claims..."
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
              </div>
              
              <!-- Status Filter -->
              <div class="relative">
                <select
                  v-model="statusFilter"
                  class="px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 min-w-32"
                >
                  <option value="">All Status</option>  
                  <option value="proses">Proses</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
              
              <!-- Claim Type Filter -->
              <div class="relative">
                <select
                  v-model="typeFilter"
                  class="px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 min-w-32"
                >
                  <option value="">All Types</option>
                  <option value="rawat-inap">Rawat Inap</option>
                  <option value="rawat-jalan">Rawat Jalan</option>
                  <option value="pra-pasca-rawat-inap">Pra/Pasca Rawat Inap</option>
                  <option value="kehamilan-melahirkan">Kehamilan/Melahirkan</option>
                  <option value="santunan-harian">Santunan Harian</option>
                  <option value="gigi">Gigi</option>
                  <option value="penyakit-kritis">Penyakit Kritis</option>
                  <option value="medical-checkup">Medical Check-up</option>
                  <option value="lainnya">Lainnya</option>
                </select>
              </div>
              
              <!-- Sort -->
              <div class="relative">
                <select
                  v-model="sortBy"
                  class="px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 min-w-36"
                >
                  <option value="date-desc">Latest First</option>
                  <option value="date-asc">Oldest First</option>
                  <option value="amount-desc">Highest Amount</option>
                  <option value="amount-asc">Lowest Amount</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-12 text-center">
            <!-- Blue spinner: solid blue border with transparent top for the spinning effect -->
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent dark:border-blue-300 dark:border-t-transparent mb-4"></div>
            <p class="text-gray-600 dark:text-gray-400">Loading claims data...</p>
          </div>

          <!-- Claims List -->
          <div v-else class="space-y-4">
            <div v-for="claim in filteredClaims" :key="claim.id" class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-6">
              <!-- Claim Summary -->
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center justify-between">
                    <div>
                      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ claim.claimNumber }}</h3>
                      <p class="text-sm text-gray-600 dark:text-gray-400">{{ claim.patientName }} • {{ claim.hospitalName }}</p>
                      <p class="text-sm text-gray-600 dark:text-gray-400">{{ getClaimTypeText(claim.type) }} • Rp {{ formatCurrency(claim.amount) }}</p>
                    </div>
                    <div class="flex items-center gap-3">
                      <span :class="getStatusClass(claim.status)">{{ getStatusText(claim.status) }}</span>
                      <button @click="openClaimDetail(claim)" class="btn bg-gray-900 text-gray-100 hover:bg-gray-800 dark:bg-gray-100 dark:text-gray-800 dark:hover:bg-gray-200 transition-all duration-200 ease-in-out transform dark:hover:bg-gray-800 dark:hover:text-white hover:shadow-lg dark:hover:border-gray-200">
                          <svg class="fill-current shrink-0 xs:hidden" width="16" height="16" viewBox="0 0 16 16">
                              <path d="M15 7H9V1c0-.6-.4-1-1-1S7 .4 7 1v6H1c-.6 0-1 .4-1 1s.4 1 1 1h6v6c0 .6.4 1 1 1s1-.4 1-1V9h6c.6 0 1-.4 1-1s-.4-1-1-1z" />
                          </svg>
                          <span class="max-xs:sr-only">Review Claim</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-if="!loading && filteredClaims.length === 0" class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-12 text-center">
            <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <p class="text-gray-500 dark:text-gray-400">No claims found matching your criteria.</p>
            <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">Try adjusting your filters or search terms.</p>
          </div>
        </div>
      </main>

      <Banner :claimDetailOpen="showDetailModal" />
    </div>

    <ClaimDetail 
      :show="showDetailModal" 
      :claim="selectedClaim" 
      @close="closeDetailModal"
      @approve="approveClaim"
      @reject="rejectClaim"
      @view-document="downloadDocument"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Sidebar from '../partials/Sidebar.vue'
import Header from '../partials/Header.vue'
import Banner from '../partials/Chatbot.vue'
import ClaimDetail from '../partials/ClaimDetail.vue'

export default {
  name: 'ClaimHistory',
  components: {
    Sidebar,
    Header,
    Banner,
    ClaimDetail,
  },
  setup() {
    const sidebarOpen = ref(false)
    const searchQuery = ref('')
    const statusFilter = ref('')
    const typeFilter = ref('')
    const sortBy = ref('date-desc')
    const claims = ref([])
    const showDetailModal = ref(false)
    const selectedClaim = ref(null)
  // show spinner until first backend response arrives
  const loading = ref(true)
  const refreshInterval = ref(null)

    // Get current admin user
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}')

    const fetchAllClaims = async () => {
      loading.value = true
      try {
        const response = await fetch('http://localhost:5000/api/claims/all-detailed')
        const result = await response.json()
        
        if (result.status === 'success') {
          claims.value = result.claims.map(claim => ({
            id: claim.claim_id,
            claimNumber: claim.claim_id,
            patientName: claim.customer_details?.name || claim.name || 'Unknown Patient',
            policyNumber: claim.policy_id,
            hospitalName: claim.insurance_company || 'Hospital Name',
            type: claim.claim_type,
            amount: claim.claim_amount,
            checkIn: extractDate(claim.claim_date),
            checkOut: extractDate(claim.claim_date, 1),
            status: mapStatus(claim.claim_status),
            submittedDate: claim.claim_date,
            documents: transformDocuments(claim.document_details || []),
            aiAnalysis: {
              recommendation: claim.AI_suggestion || 'Pending Analysis',
              reasoning: claim.AI_reasoning || 'Analysis in progress...',
              details: [
                { 
                  category: 'Administrative Validation', 
                  finding: 'Documents uploaded and processed' 
                },
                { 
                  category: 'AI Reasoning', 
                  finding: claim.AI_reasoning || 'In progress' 
                },
                {
                  category: 'Summary',
                  finding: claim.summary || 'N/A'
                }
              ]
            },
            customer_id: claim.customer_id,
            rawData: claim
          }))
        } else {
          console.error('Error fetching claims:', result.error)
          claims.value = []
        }
      } catch (error) {
        console.error('Error fetching claims:', error)
        claims.value = []
      } finally {
        loading.value = false
      }
    }

    const mapStatus = (status) => {
      const statusMap = {
        'Prosses': 'proses',
        'Proses' : 'proses',
        'Pending': 'pengajuan',
        'Approved': 'approved',
        'Rejected': 'rejected'
      }
      return statusMap[status] || 'pengajuan'
    }

    const extractDate = (dateString, addDays = 0) => {
      try {
        const date = new Date(dateString)
        if (addDays) {
          date.setDate(date.getDate() + addDays)
        }
        return date.toISOString().split('T')[0]
      } catch {
        return new Date().toISOString().split('T')[0]
      }
    }

    const transformDocuments = (documents) => {
      return documents.map(doc => {
        let name = 'Unknown Document'
        
        switch (doc.doc_type) {
          case 'invoice':
            name = 'Invoice Rumah Sakit'
            break
          case 'doctor form':
            name = 'Form Medis Dokter'
            break
          case 'report lab':
            name = 'Hasil Laboratorium'
            break
          case 'additional doc':
            name = 'Dokumen Tambahan'
            break
          default:
            name = `${doc.doc_type || 'Document'}`
            break
        }
        
        return {
          id: doc.doc_id,
          name: `${name}_${doc.claim_id}.pdf`,
          size: '1.2 MB',
          type: 'PDF',
          url: `/api/documents/${doc.doc_id}`,
          doc_type: doc.doc_type,
          doc_contents: doc.doc_contents || {}
        }
      })
    }

    const approveClaim = async (notes) => {
      try {
        const response = await fetch(`http://localhost:5000/api/claims/${selectedClaim.value.id}/update-status`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            status: 'Approved',
            admin_id: currentUser.id || 'ADMIN001',
            notes: notes
          })
        })
        
        const result = await response.json()
        
        if (result.status === 'success') {
          const claimIndex = claims.value.findIndex(c => c.id === selectedClaim.value.id)
          if (claimIndex !== -1) {
            claims.value[claimIndex].status = 'approved'
          }
          
          alert('Claim has been approved successfully!')
          closeDetailModal()
          await fetchAllClaims()
        } else {
          alert(`Error: ${result.error}`)
        }
      } catch (error) {
        console.error('Error approving claim:', error)
        alert('Error approving claim. Please try again.')
      }
    }

    const rejectClaim = async (notes) => {
      try {
        const response = await fetch(`http://localhost:5000/api/claims/${selectedClaim.value.id}/update-status`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            status: 'Rejected',
            admin_id: currentUser.id || 'ADMIN001',
            notes: notes
          })
        })
        
        const result = await response.json()
        
        if (result.status === 'success') {
          const claimIndex = claims.value.findIndex(c => c.id === selectedClaim.value.id)
          if (claimIndex !== -1) {
            claims.value[claimIndex].status = 'rejected'
          }
          
          alert('Claim has been rejected.')
          closeDetailModal()
          await fetchAllClaims()
        } else {
          alert(`Error: ${result.error}`)
        }
      } catch (error) {
        console.error('Error rejecting claim:', error)
        alert('Error rejecting claim. Please try again.')
      }
    }

    const filteredClaims = computed(() => {
      let filtered = claims.value

      // Search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(claim => 
          claim.claimNumber.toLowerCase().includes(query) ||
          claim.hospitalName.toLowerCase().includes(query) ||
          claim.type.toLowerCase().includes(query)
        )
      }

      // Status filter
      if (statusFilter.value) {
        filtered = filtered.filter(claim => claim.status === statusFilter.value)
      }

      // Type filter
      if (typeFilter.value) {
        if (typeFilter.value === 'lainnya') {
          const knownTypes = ['rawat-inap', 'rawat-jalan', 'pra-pasca-rawat-inap', 'kehamilan-melahirkan', 'santunan-harian', 'gigi', 'penyakit-kritis', 'medical-checkup']
          filtered = filtered.filter(claim => !knownTypes.includes(claim.type))
        } else {
          filtered = filtered.filter(claim => claim.type === typeFilter.value)
        }
      }

      // Sort
      filtered.sort((a, b) => {
        switch (sortBy.value) {
          case 'date-desc':
            return new Date(b.submittedDate) - new Date(a.submittedDate)
          case 'date-asc':
            return new Date(a.submittedDate) - new Date(b.submittedDate)
          case 'amount-desc':
            return b.amount - a.amount
          case 'amount-asc':
            return a.amount - b.amount
          default:
            return 0
        }
      })

      return filtered
    })

    const getStatusClass = (status) => {
      const baseClass = 'status-badge '
      switch (status) {
        case 'pengajuan': return baseClass + 'status-pengajuan'
        case 'proses': return baseClass + 'status-proses'
        case 'approved': return baseClass + 'status-approved'
        case 'rejected': return baseClass + 'status-rejected'
        default: return baseClass + 'status-pengajuan'
      }
    }

    const getStatusText = (status) => {
      switch (status) {
        case 'pengajuan': return 'Pengajuan'
        case 'proses': return 'Proses'
        case 'approved': return 'Disetujui'
        case 'rejected': return 'Ditolak'
        default: return status
      }
    }

    const getProgressClass = (status) => {
      return status
    }

    const getClaimTypeText = (type) => {
      const typeMap = {
        'rawat-inap': 'Rawat Inap',
        'rawat-jalan': 'Rawat Jalan',
        'pra-pasca-rawat-inap': 'Pra/Pasca Rawat Inap',
        'kehamilan-melahirkan': 'Kehamilan/Melahirkan',
        'santunan-harian': 'Santunan Harian',
        'gigi': 'Gigi',
        'penyakit-kritis': 'Penyakit Kritis',
        'medical-checkup': 'Medical Check-up',
        'lainnya': 'Lainnya'
      }
      return typeMap[type] || 'Lainnya'
    }

    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('id-ID').format(amount)
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('id-ID', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    }

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString('id-ID', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const openClaimDetail = (claim) => {
      console.log('Opening claim detail for:', claim)
      selectedClaim.value = claim
      showDetailModal.value = true
      console.log('showDetailModal:', showDetailModal.value)
    }

    const closeDetailModal = () => {
      showDetailModal.value = false
      selectedClaim.value = null
    }

    const handleClickOutside = (event) => {
      if (showDetailModal.value && modalRef.value && !modalRef.value.contains(event.target)) {
        closeDetailModal()
      }
    }

    const downloadDocument = (document) => {
      console.log('Viewing document:', document.name)
      alert(`Opening ${document.name} for review`)
    }

   onMounted(() => {
      fetchAllClaims()

      // Set up auto-refresh every 30 seconds and keep the id to clear later
      refreshInterval.value = setInterval(fetchAllClaims, 30000)
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      if (refreshInterval.value) clearInterval(refreshInterval.value)
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      sidebarOpen,
      searchQuery,
      statusFilter,
      typeFilter,
      sortBy,
      filteredClaims,
      loading,
      showDetailModal,
      selectedClaim,
      getStatusClass,
      getStatusText,
      getClaimTypeText,
      formatCurrency,
      formatDate,
      formatDateTime,
      openClaimDetail,
      closeDetailModal,
      downloadDocument,
      approveClaim,
      rejectClaim
    }
  }
}
</script>

<style scoped>
@import '../css/claim-history.css';

.progress-step {
  margin-bottom: 1rem;
}

.progress-step:last-child {
  margin-bottom: 0;
}
</style>