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
            <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Claim History</h1>
            <p class="text-gray-600 dark:text-gray-400">View your submitted claims and their status</p>
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

          <!-- Claims List -->
          <div class="space-y-4">
            <div v-for="claim in filteredClaims" :key="claim.id" class="claim-card cursor-pointer" @click="toggleClaim(claim.id)">
              <!-- Claim Summary -->
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center justify-between">
                    <div>
                      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ claim.claimNumber }}</h3>
                      <p class="text-sm text-gray-600 dark:text-gray-400">{{ claim.hospitalName }} • {{ getClaimTypeText(claim.type) }} • Rp {{ formatCurrency(claim.amount) }}</p>
                    </div>
                    <div class="flex items-center gap-3">
                      <span :class="getStatusClass(claim.status)">{{ getStatusText(claim.status) }}</span>
                      <svg class="w-5 h-5 text-gray-400 transition-transform" :class="{ 'rotate-180': expandedClaims.has(claim.id) }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Expanded Details -->
              <div v-if="expandedClaims.has(claim.id)" class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <div class="flex flex-col lg:flex-row gap-6">
                  <!-- Claim Details -->
                  <div class="flex-1">
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p class="text-xs text-gray-500 dark:text-gray-400">Jenis Klaim</p>
                        <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ getClaimTypeText(claim.type) }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-gray-500 dark:text-gray-400">Jumlah Klaim</p>
                        <p class="text-sm font-medium text-gray-900 dark:text-gray-100">Rp {{ formatCurrency(claim.amount) }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-gray-500 dark:text-gray-400">Masuk</p>
                        <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatDate(claim.checkIn) }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-gray-500 dark:text-gray-400">Keluar</p>
                        <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatDate(claim.checkOut) }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Progress Timeline -->
                  <div class="lg:w-80">
                    <div class="flex items-center justify-between mb-4">
                      <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">Progress Status</h4>
                      <button @click="showDocumentModal(claim.id)" class="px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors">
                        Unduh Dokumen
                      </button>
                    </div>
                    <div :class="{ 'is-last-step': true }">
                      <div v-for="(step, index) in claim.progress" :key="index"
                        :class="['progress-step', getProgressClass(step.status), { 'with-connector': index !== 0, 'connector-completed': index !== 0 && claim.progress[index-1].status === 'completed', 'is-last': index === claim.progress.length - 1 }]" 
                        :style="{ 'align-items': 'flex-start', 'margin-bottom': index === claim.progress.length - 1 ? '0' : '1rem' }">
                        <div :class="['progress-circle', getProgressClass(step.status)]">
                          <svg v-if="step.status === 'completed'" class="w-4 h-4" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M6.75,15h-.002c-.227,0-.442-.104-.583-.281L2.165,9.719c-.259-.324-.207-.795,.117-1.054,.325-.259,.796-.206,1.054,.117l3.418,4.272L14.667,3.278c.261-.322,.732-.373,1.055-.111,.322,.261,.372,.733,.111,1.055L7.333,14.722c-.143,.176-.357,.278-.583,.278Z" fill="currentColor"/>
                          </svg>
                          <span v-else-if="step.status === 'active'">{{ index + 1 }}</span>
                          <span v-else>{{ index + 1 }}</span>
                        </div>
                        <div class="ml-4 flex-1">
                          <div class="flex items-start justify-between">
                            <div class="flex items-center gap-2">
                              <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ step.title }}</p>
                              <p v-if="step.date" class="text-xs text-gray-500 dark:text-gray-400">{{ formatDateTime(step.date) }}</p>
                            </div>
                          </div>
                          <p v-if="step.notes" class="text-xs text-gray-600 dark:text-gray-400 mt-1">{{ step.notes }}</p>
                          <div v-if="step.title === 'Keputusan' && claim.status === 'rejected'" class="mt-2 ctq43">
                            <button @click="editClaim(claim)" class="btn-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-300">
                              <svg class="w-3 h-3 mr-2 fill-current opacity-50 shrink-0" viewBox="0 0 16 16">
                                <path d="M11.7.3c-.4-.4-1-.4-1.4 0l-10 10c-.2.2-.3.4-.3.7v4c0 .6.4 1 1 1h4c.3 0 .5-.1.7-.3l10-10c.4-.4.4-1 0-1.4l-4-4zM4.6 14H2v-2.6l6-6L10.6 8l-6 6zM12 6.6L9.4 4 11 2.4 13.6 5 12 6.6z" />
                              </svg>
                              <span class="text-xs">
                                Edit Claim
                              </span>
                            </button>
                          </div>
                        </div>
                      </div>
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

      <!-- Document Download Modal -->
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="closeModal"></div>
        <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-lg max-w-md w-full mx-4">
          <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Unduh Dokumen</h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <div class="p-4">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">Pilih dokumen yang akan diunduh untuk claim {{ selectedClaim?.claimNumber }}:</p>
            <div class="space-y-2">
              <div v-for="doc in selectedClaim?.documents" :key="doc.id" class="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <div>
                    <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ doc.name }}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ doc.size }} • {{ doc.type }}</p>
                  </div>
                </div>
                <button @click="downloadDocument(doc)" class="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
                  Download
                </button>
              </div>
            </div>
          </div>
          <div class="flex justify-end gap-2 p-4 border-t border-gray-200 dark:border-gray-700">
            <button @click="closeModal" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
              Cancel
            </button>
            <button @click="downloadAllDocuments" class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
              Download All
            </button>
            <!-- Edit Form Submit -->
             <div class="ctq43">
                 <button @click="submitClaim" class="btn bg-white border-gray-200 text-gray-800">
                   <svg width="16" height="16" viewBox="0 0 16 16">
                   <path d="M11.7.3c-.4-.4-1-.4-1.4 0l-10 10c-.2.2-.3.4-.3.7v4c0 .6.4 1 1 1h4c.3 0 .5-.1.7-.3l10-10c.4-.4.4-1 0-1.4l-4-4zM4.6 14H2v-2.6l6-6L10.6 8l-6 6zM12 6.6L9.4 4 11 2.4 13.6 5 12 6.6z"></path>
                     </svg>
                     <span>Edit Claim</span>
                 </button>
             </div>
          </div>
        </div>


      </div>


    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from '../partials/Sidebar.vue'
import Header from '../partials/Header.vue'
import Banner from '../partials/Chatbot.vue'

export default {
  name: 'ClaimHistory',
  components: {
    Sidebar,
    Header,
    Banner,
  },
  setup() {
    const router = useRouter()
    const sidebarOpen = ref(false)
    const searchQuery = ref('')
    const statusFilter = ref('')
    const typeFilter = ref('')
    const sortBy = ref('date-desc')
    const claims = ref([])
    const expandedClaims = ref(new Set())
    const showModal = ref(false)
    const selectedClaim = ref(null)

    // Mock data
    const mockClaims = [
      {
        id: 1,
        claimNumber: 'CLM-2024-001',
        hospitalName: 'RS Siloam Kebon Jeruk',
        type: 'rawat-inap',
        amount: 15000000,
        checkIn: '2024-01-15',
        checkOut: '2024-01-18',
        status: 'approved',
        submittedDate: '2024-01-19T10:30:00',
        progress: [
          { title: 'Pengajuan', status: 'completed', date: '2024-01-19T10:30:00', notes: 'Dokumen lengkap diterima' },
          { title: 'Proses', status: 'completed', date: '2024-01-20T14:15:00', notes: 'Verifikasi dokumen selesai' },
          { title: 'Keputusan', status: 'completed', date: '2024-01-22T09:45:00', notes: 'Klaim disetujui. Dana akan ditransfer dalam 3-5 hari kerja.' }
        ],
        documents: [
          { id: 1, name: 'Invoice Rumah Sakit.pdf', size: '1.8 MB', type: 'PDF', url: '/form/invoice-1.pdf' },
          { id: 2, name: 'Form Medis Dokter.pdf', size: '2.4 MB', type: 'PDF', url: '/form/dokter form-1.pdf' }
        ]
      },
      {
        id: 2,
        claimNumber: 'CLM-2024-002',
        hospitalName: 'RSUD Fatmawati',
        type: 'pra-pasca-rawat-inap',
        amount: 8500000,
        checkIn: '2024-02-01',
        checkOut: '2024-02-02',
        status: 'proses',
        submittedDate: '2024-02-03T16:20:00',
        progress: [
          { title: 'Pengajuan', status: 'completed', date: '2024-02-03T16:20:00', notes: 'Dokumen diterima' },
          { title: 'Proses', status: 'active', date: '2024-02-04T11:00:00', notes: 'Sedang dalam tahap verifikasi medis' },
          { title: 'Keputusan', status: 'pending', date: null, notes: null }
        ],
        documents: [
          { id: 1, name: 'Invoice Rumah Sakit.pdf', size: '890 KB', type: 'PDF', url: '/form/invoice-2.pdf' },
          { id: 2, name: 'Form Medis Dokter.pdf', size: '1.2 MB', type: 'PDF', url: '/form/dokter form-2.pdf' }
        ]
      },
      {
        id: 3,
        claimNumber: 'CLM-2024-003',
        hospitalName: 'RS Pondok Indah',
        type: 'rawat-jalan',
        amount: 2500000,
        checkIn: '2024-02-10',
        checkOut: '2024-02-10',
        status: 'rejected',
        submittedDate: '2024-02-11T08:15:00',
        progress: [
          { title: 'Pengajuan', status: 'completed', date: '2024-02-11T08:15:00', notes: 'Dokumen diterima' },
          { title: 'Proses', status: 'completed', date: '2024-02-12T13:30:00', notes: 'Verifikasi selesai' },
          { title: 'Keputusan', status: 'completed', date: '2024-02-13T10:20:00', notes: 'Klaim ditolak. Diagnosis tidak sesuai dengan polis. Silakan hubungi customer service untuk informasi lebih lanjut.' }
        ],
        documents: [
          { id: 1, name: 'Invoice Rumah Sakit.pdf', size: '456 KB', type: 'PDF', url: '/form/invoice-3.pdf' },
          { id: 2, name: 'Form Medis Dokter.pdf', size: '1.5 MB', type: 'PDF', url: '/form/dokter form-3.pdf' }
        ]
      },
      {
        id: 4,
        claimNumber: 'CLM-2024-004',
        hospitalName: 'RS Mayapada',
        type: 'kehamilan-melahirkan',
        amount: 12000000,
        checkIn: '2024-02-15',
        checkOut: '2024-02-17',
        status: 'rejected',
        submittedDate: '2024-02-18T14:45:00',
        progress: [
          { title: 'Pengajuan', status: 'completed', date: '2024-02-18T14:45:00', notes: 'Dokumen diterima' },
          { title: 'Proses', status: 'completed', date: '2024-02-19T10:30:00', notes: 'Verifikasi dokumen selesai' },
          { title: 'Keputusan', status: 'completed', date: '2024-02-20T15:20:00', notes: 'Klaim ditolak. Dokumen tidak lengkap - Invoice tidak sesuai format dan form medis tidak memiliki tanda tangan dokter yang valid.' }
        ],
        documents: [
          { id: 1, name: 'Invoice Siloam.pdf', size: '2.2 MB', type: 'PDF', url: '/form/invoice_siloam.pdf' },
          { id: 2, name: 'Dokter Form Siloam.pdf', size: '3.1 MB', type: 'PDF', url: '/form/dokter_form_siloam.pdf' }
        ]
      }
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
        'kehamilan-melahirkan': 'Kehamilan/ Melahirkan',
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

    const toggleClaim = (claimId) => {
      if (expandedClaims.value.has(claimId)) {
        expandedClaims.value.delete(claimId)
      } else {
        expandedClaims.value.add(claimId)
      }
    }

    const showDocumentModal = (claimId) => {
      selectedClaim.value = claims.value.find(claim => claim.id === claimId)
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
      selectedClaim.value = null
    }

    const downloadDocument = (document) => {
      window.open(document.url, '_blank')
    }

    const downloadAllDocuments = () => {
      if (selectedClaim.value?.documents) {
        selectedClaim.value.documents.forEach(doc => {
          window.open(doc.url, '_blank')
        })
      }
      closeModal()
    }

    const editClaim = (claim) => {
      router.push({
        name: 'FormClaim',
        query: { edit: claim.id }
      })
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
      expandedClaims,
      showModal,
      selectedClaim,
      getStatusClass,
      getStatusText,
      getProgressClass,
      getClaimTypeText,
      formatCurrency,
      formatDate,
      formatDateTime,
      toggleClaim,
      showDocumentModal,
      closeModal,
      downloadDocument,
      downloadAllDocuments,
      editClaim
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
