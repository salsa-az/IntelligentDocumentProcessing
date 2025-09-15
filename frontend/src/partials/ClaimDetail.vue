<template>
  <div v-if="show" class="fixed inset-y-0 right-0 z-50 w-96 bg-white dark:bg-gray-800 shadow-2xl border-l border-gray-200 dark:border-gray-700 overflow-y-auto">
    <!-- Panel Header -->
    <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Claim Details</h2>
      <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <!-- Panel Content -->
    <div class="p-6">
      <!-- Claim Header -->
      <div class="mb-6">
        <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">{{ claim?.claimNumber }}</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">{{ formatDate(claim?.submittedDate) }}</p>
        <div class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">Rp {{ formatCurrency(claim?.amount) }}</div>
        <span :class="getStatusClass(claim?.status)">{{ getStatusText(claim?.status) }}</span>
      </div>

      <!-- Patient Information -->
      <div class="mb-6">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 uppercase tracking-wide">Patient Information</h4>
        <div class="space-y-3">
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Patient Name</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ claim?.patientName }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Policy Number</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ claim?.policyNumber }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Hospital</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ claim?.hospitalName }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Claim Type</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ getClaimTypeText(claim?.type) }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Treatment Period</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatDate(claim?.checkIn) }} - {{ formatDate(claim?.checkOut) }}</span>
          </div>
        </div>
      </div>

      <!-- Documents -->
      <div class="mb-6">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 uppercase tracking-wide">Documents</h4>
        <div class="space-y-2">
          <div v-for="doc in claim?.documents" :key="doc.id" class="bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="flex items-center justify-between p-3 cursor-pointer" @click="toggleDocument(doc.id)">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                  <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ doc.name }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ doc.size }}</p>
                </div>
              </div>
              <svg class="w-4 h-4 text-gray-400 transition-transform" :class="{ 'rotate-180': expandedDocs.has(doc.id) }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </div>
            
            <!-- Expanded Content -->
            <div v-if="expandedDocs.has(doc.id)" class="px-3 pb-3">
              <div class="bg-white dark:bg-gray-800 rounded p-3 text-xs">
                <div v-if="doc.name.includes('Form Medis')">
                  <h6 class="font-semibold mb-2">Form Dokter</h6>
                  <div class="space-y-2">
                    <div><strong>Data Administrasi Pasien</strong><br>
                    Tanggal Masuk: 07/03/2023<br>
                    Tanggal Keluar: 07/03/2023</div>
                    <div><strong>Hubungan Dokter–Pasien</strong><br>
                    Apakah Anda dokter keluarga pasien?: Tidak<br>
                    Hubungan keluarga dengan pasien: Tidak</div>
                    <div><strong>Diagnosis</strong><br>
                    Diagnosis Masuk: Nyeri dada<br>
                    Diagnosis Keluar: Hipertensi<br>
                    Diagnosis Utama + Kode: Hipertensi (I10)<br>
                    Diagnosis Penyerta + Kode: Demam tidak spesifik (R50.9)</div>
                    <div><strong>Riwayat Medis & Keluhan</strong><br>
                    Penyakit terkait: Tidak ada<br>
                    Keluhan utama & kronologi: Nyeri dada sejak 2 hari<br>
                    Keluhan tambahan: Pusing<br>
                    Penyakit/keluhan lain terkait kondisi saat ini: Tidak<br>
                    Sejak kapan keluhan dirasakan: 05/03/2023 (perkiraan durasi 2 bulan)<br>
                    Pernah mengalami kondisi serupa sebelum tanggal perawatan: Tidak</div>
                    <div><strong>Rujukan & Indikasi Rawat Inap</strong><br>
                    Pasien dirujuk oleh: Dr. Yusak Mangara Tua Siahaan, Sp.S (K)<br>
                    Indikasi rawat inap: Evaluasi keluhan neurologis dan kardiovaskular<br>
                    Perkembangan diagnosis: Tidak berkembang perlahan<br>
                    Estimasi lamanya keluhan ada: 2 bulan</div>
                    <div><strong>Pemeriksaan & Tindakan</strong><br>
                    Pemeriksaan fisik/penunjang: Tekanan darah tinggi<br>
                    Terapi/prosedur: Cardiprin 100 mg, Canderin 16 mg, dll.</div>
                    <div><strong>Data Dokter Penanggung Jawab</strong><br>
                    Nama Dokter: Ada<br>
                    SIP: Ada<br>
                    Nomor Telepon: Ada<br>
                    Email: Ada<br>
                    Tanda tangan & stempel: Ada<br>
                    Tanggal: 07/03/2023</div>
                  </div>
                </div>
                
                <div v-else-if="doc.name.includes('Invoice')">
                  <h6 class="font-semibold mb-2">Invoice Rumah Sakit</h6>
                  <div class="space-y-1">
                    <div><strong>Nomor Invoice:</strong> OIV2303070050</div>
                    <div><strong>Tanggal Invoice:</strong> 07/03/2023</div>
                    <div><strong>Nama Pasien:</strong> Feri Hussen</div>
                    <div><strong>Tanggal Layanan/Rawat:</strong> 07/03/2023</div>
                    <div><strong>Rincian Biaya:</strong> Ada (terperinci per layanan/prosedur)</div>
                    <div><strong>Total Tagihan:</strong> 7.720.000</div>
                    <div><strong>Mata Uang:</strong> Tidak tertulis (asumsi IDR – Rupiah Indonesia)</div>
                    <div><strong>Nama Penyedia Layanan:</strong> Siloam Hospitals</div>
                    <div><strong>Alamat Penyedia Layanan:</strong> Jl. Siloam No. 6, Lippo Village, Indonesia</div>
                    <div><strong>Kontak Penyedia Layanan:</strong> Tidak disebutkan eksplisit di invoice</div>
                    <div><strong>Instruksi/Metode Pembayaran:</strong> Tidak ditemukan</div>
                  </div>
                </div>
              </div>
              
              <div class="mt-3 flex justify-end">
                <button @click="downloadDocument(doc)" class="flex items-center px-3 py-1 text-xs bg-violet-500 text-white rounded hover:bg-violet-600 transition-colors">
                    <svg class="w-3 h-3 mr-2" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                      <path d="M8 12c.3 0 .5-.1.7-.3L14.4 6 13 4.6l-4 4V0H7v8.6l-4-4L1.6 6l5.7 5.7c.2.2.4.3.7.3ZM15 14H1v2h14v-2Z" fill="currentColor"></path>
                    </svg>
                    Download
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Analysis -->
      <div class="mb-6">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 uppercase tracking-wide">AI Analysis</h4>
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-4">
          <div class="flex items-start space-x-3">
            <svg class="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
            <div>
              <h5 class="font-medium text-blue-900 dark:text-blue-100 mb-2">AI Recommendation</h5>
              <p class="text-sm text-blue-800 dark:text-blue-200 mb-3">{{ claim?.aiAnalysis?.recommendation }}</p>
              <div class="text-xs text-blue-700 dark:text-blue-300">
                <p><strong>Confidence:</strong> {{ claim?.aiAnalysis?.confidence }}%</p>
                <p><strong>Risk Score:</strong> {{ claim?.aiAnalysis?.riskScore }}/10</p>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-3 mb-6">
          <div v-for="detail in claim?.aiAnalysis?.details" :key="detail.category" class="border-l-4 border-gray-300 pl-3">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ detail.category }}</p>
            <p class="text-xs text-gray-600 dark:text-gray-400">{{ detail.finding }}</p>
          </div>
        </div>
      </div>

      <!-- Admin Decision -->
      <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 uppercase tracking-wide">Admin Decision</h4>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Decision Notes</label>
            <textarea v-model="notes" rows="3" class="form-textarea w-full" placeholder="Add your review notes..."></textarea>
          </div>
          <div class="flex space-x-3">
            <button @click="$emit('approve', notes)" class="flex-1 btn bg-green-600 hover:bg-green-700 text-white">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              Approve
            </button>
            <button @click="$emit('reject', notes)" class="flex-1 btn bg-red-600 hover:bg-red-700 text-white">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
              Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'ClaimDetail',
  props: {
    show: Boolean,
    claim: Object
  },
  emits: ['close', 'approve', 'reject', 'download-document'],
  setup(props, { emit }) {
    const notes = ref('')
    const expandedDocs = ref(new Set())

    watch(() => props.show, (newVal) => {
      if (newVal) {
        notes.value = ''
      }
    })

    const toggleDocument = (docId) => {
      if (expandedDocs.value.has(docId)) {
        expandedDocs.value.delete(docId)
      } else {
        expandedDocs.value.add(docId)
      }
    }

    const downloadDocument = async (doc) => {
      try {
        const response = await fetch(doc.url || `/api/documents/${doc.id}`)
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = doc.name
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Download failed:', error)
        alert('Failed to download document')
      }
    }

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

    return {
      notes,
      expandedDocs,
      toggleDocument,
      downloadDocument,
      getStatusClass,
      getStatusText,
      getClaimTypeText,
      formatCurrency,
      formatDate
    }
  }
}
</script>