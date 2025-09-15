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
            <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Admin - Claims Approval</h1>
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
                  <option value="pengajuan">Pengajuan</option>
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

          <!-- Claims List -->
          <div class="space-y-4">
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
                      <button @click="openClaimDetail(claim)" class="btn bg-violet-500 hover:bg-blue-700 text-white">
                        Review Claim
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-if="filteredClaims.length === 0" class="bg-white dark:bg-gray-800 shadow-xs rounded-xl p-12 text-center">
            <p class="text-gray-500 dark:text-gray-400">No claims found matching your criteria.</p>
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
import { ref, computed, onMounted } from 'vue'
import Sidebar from '../partials/Sidebar.vue'
import Header from '../partials/Header.vue'
import Banner from '../partials/AIAssistant.vue'
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

    // Mock data for admin review
    const mockClaims = [
      {
        id: 1,
        claimNumber: 'CLM-2024-001',
        patientName: 'Feri Hussen',
        policyNumber: 'POL-001-2024',
        hospitalName: 'RS Siloam Kebon Jeruk',
        type: 'rawat-inap',
        amount: 7720000,
        checkIn: '2024-01-15',
        checkOut: '2024-01-18',
        status: 'proses',
        submittedDate: '2024-01-19T10:30:00',
        documents: [
          { id: 1, name: 'Invoice Rumah Sakit.pdf', size: '1.8 MB' },
          { id: 2, name: 'Form Medis Dokter.pdf', size: '2.4 MB' }
        ],
        aiAnalysis: {
          recommendation: 'APPROVE - All documents are complete and valid. Diagnosis matches treatment and costs are reasonable.',
          confidence: 92,
          riskScore: 2,
          details: [
            { category: 'Administrative Validation', finding: 'All required fields present and complete' },
            { category: 'Diagnosis Validation', finding: 'Hypertension (ICD X: I10) correctly coded and consistent' },
            { category: 'Treatment Validation', finding: 'Treatments appropriate for diagnosis' },
            { category: 'Cost Analysis', finding: 'Invoice total (7,720,000 IDR) reasonable for treatment type' }
          ]
        }
      },
      {
        id: 2,
        claimNumber: 'CLM-2024-002',
        patientName: 'Siti Rahayu',
        policyNumber: 'POL-002-2024',
        hospitalName: 'RSUD Fatmawati',
        type: 'rawat-jalan',
        amount: 3500000,
        checkIn: '2024-02-01',
        checkOut: '2024-02-01',
        status: 'proses',
        submittedDate: '2024-02-03T16:20:00',
        documents: [
          { id: 1, name: 'Invoice Rumah Sakit.pdf', size: '890 KB' },
          { id: 2, name: 'Form Medis Dokter.pdf', size: '1.2 MB' }
        ],
        aiAnalysis: {
          recommendation: 'REVIEW REQUIRED - Missing some documentation, costs seem high for outpatient treatment.',
          confidence: 67,
          riskScore: 6,
          details: [
            { category: 'Administrative Validation', finding: 'Some required fields missing in documentation' },
            { category: 'Cost Analysis', finding: 'Costs appear elevated for outpatient treatment type' },
            { category: 'Treatment Validation', finding: 'Treatment plan needs verification' }
          ]
        }
      },
    //   {
    //     id: 4,
    //     claimNumber: 'CLM-2024-004',
    //     hospitalName: 'RS Mayapada',
    //     type: 'kehamilan-melahirkan',
    //     amount: 12000000,
    //     checkIn: '2024-02-15',
    //     checkOut: '2024-02-17',
    //     status: 'pengajuan',
    //     submittedDate: '2024-02-18T14:45:00',
    //     progress: [
    //       { title: 'Pengajuan', status: 'active', date: '2024-02-18T14:45:00', notes: 'Menunggu kelengkapan dokumen tambahan' },
    //       { title: 'Proses', status: 'pending', date: null, notes: null },
    //       { title: 'Keputusan', status: 'pending', date: null, notes: null }
    //     ],
    //     documents: [
    //       { id: 1, name: 'Invoice Rumah Sakit.pdf', size: '2.2 MB', type: 'PDF', url: '/documents/invoice-4.pdf' },
    //       { id: 2, name: 'Form Medis Dokter.pdf', size: '3.1 MB', type: 'PDF', url: '/documents/medical-form-4.pdf' }
    //     ]
    //   }
    ]

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

    const downloadDocument = (document) => {
      console.log('Viewing document:', document.name)
      alert(`Opening ${document.name} for review`)
    }

    const approveClaim = (notes) => {
      if (!notes.trim()) {
        alert('Please add review notes before approving')
        return
      }
      
      const claimIndex = claims.value.findIndex(c => c.id === selectedClaim.value.id)
      if (claimIndex !== -1) {
        claims.value[claimIndex].status = 'approved'
      }
      
      console.log('Claim approved:', {
        claimId: selectedClaim.value.id,
        notes: notes,
        aiRecommendation: selectedClaim.value.aiAnalysis.recommendation
      })
      
      alert('Claim has been approved successfully!')
      closeDetailModal()
    }

    const rejectClaim = (notes) => {
      if (!notes.trim()) {
        alert('Please add review notes before rejecting')
        return
      }
      
      const claimIndex = claims.value.findIndex(c => c.id === selectedClaim.value.id)
      if (claimIndex !== -1) {
        claims.value[claimIndex].status = 'rejected'
      }
      
      console.log('Claim rejected:', {
        claimId: selectedClaim.value.id,
        notes: notes,
        aiRecommendation: selectedClaim.value.aiAnalysis.recommendation
      })
      
      alert('Claim has been rejected.')
      closeDetailModal()
    }

    onMounted(() => {
      claims.value = mockClaims
    })

    return {
      sidebarOpen,
      searchQuery,
      statusFilter,
      typeFilter,
      sortBy,
      filteredClaims,
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