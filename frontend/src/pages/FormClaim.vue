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
            <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">
              {{ isEditing ? 'Edit Klaim Asuransi' : 'Form Klaim Asuransi' }}
            </h1>
            <p class="text-gray-600 dark:text-gray-400">
              {{ isEditing ? 'Edit klaim yang ditolak dengan dokumen yang diperlukan' : 'Ajukan klaim asuransi Anda dengan dokumen yang diperlukan' }}
            </p>
          </div>

          <!-- Form -->
          <form @submit.prevent="submitClaim">
                
                <!-- Informasi Profil -->
                <div class="mb-8">
                  <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Informasi Profil (Terisi Otomatis)</h2>
                  <!-- <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">(Pilih asuransi utama jika ada lebih dari satu asuransi)</p>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">(Verifikasi apakah data diri perlu diubah)</p> -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium mb-1" for="nomorPolis">Nomor Polis</label>
                      <input id="nomorPolis" type="text" v-model="form.nomorPolis" readonly class="form-input w-full bg-gray-50 dark:bg-gray-700">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="namaPerusahaan">Nama Perusahaan Asuransi</label>
                      <input id="namaPerusahaan" type="text" v-model="form.namaPerusahaan" readonly class="form-input w-full bg-gray-50 dark:bg-gray-700 ">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="nomorPeserta">Nomor Peserta</label>
                      <input id="nomorPeserta" type="text" v-model="form.nomorPeserta" readonly class="form-input w-full bg-gray-50 dark:bg-gray-700">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="namaPemegang">Nama Pemegang Polis</label>
                      <input id="namaPemegang" type="text" v-model="form.namaPemegang" readonly class="form-input w-full bg-gray-50 dark:bg-gray-700">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="nik">NIK</label>
                      <input id="nik" type="text" v-model="form.nik" readonly class="form-input w-full bg-gray-50 dark:bg-gray-700">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="tanggalLahir">Tanggal Lahir</label>
                      <input id="tanggalLahir" type="date" v-model="form.tanggalLahir" readonly class="form-input w-full bg-gray-50 dark:bg-gray-700">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="jenisKelamin">Jenis Kelamin</label>
                      <input id="jenisKelamin" type="text" v-model="form.jenisKelamin" readonly class="form-input w-full bg-gray-50 dark:bg-gray-700">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="statusPernikahan">Status Pernikahan</label>
                      <input id="statusPernikahan" type="text" v-model="form.statusPernikahan" readonly class="form-input w-full bg-gray-50 dark:bg-gray-700">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="email">Email</label>
                      <input id="email" type="email" v-model="form.email" readonly class="form-input w-full bg-gray-50 dark:bg-gray-700">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="nomorTelepon">Nomor Telepon</label>
                      <input id="nomorTelepon" type="tel" v-model="form.nomorTelepon" readonly class="form-input w-full bg-gray-50 dark:bg-gray-700">
                    </div>
                    <!-- <div class="md:col-span-2">
                      <label class="block text-sm font-medium mb-1" for="alamat">Alamat</label>
                      <textarea id="alamat" v-model="form.alamat" readonly rows="2" class="form-textarea w-full bg-gray-50 dark:bg-gray-700"></textarea>
                    </div> -->
                  </div>
                </div>
                
                <!-- A. Jenis Klaim -->
                <div class="mb-8">
                  <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">A. Jenis Klaim</h2>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" for="claimType">Pilih Jenis Klaim <span class="text-red-500">*</span></label>
                    <select id="claimType" v-model="form.claimType" required class="form-select w-full">
                      <option value="">Pilih jenis klaim</option>
                      <option value="rawat-inap">Rawat Inap</option>
                      <option value="rawat-jalan">Rawat Jalan</option>
                      <option value="pra-pasca-rawat-inap">Pra/Pasca Rawat Inap</option>
                      <option value="kehamilan-melahirkan">Kehamilan/Melahirkan</option>
                      <option value="santunan-harian">Santunan Harian</option>
                      <option value="gigi">Gigi</option>
                      <option value="penyakit-kritis">Penyakit Kritis Katastropik</option>
                      <option value="medical-checkup">Medical Check-up</option>
                      <option value="lainnya">Lainnya</option>
                    </select>
                  </div>
                  <div v-if="form.claimType === 'lainnya'" class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" for="otherClaimType">Sebutkan Jenis Klaim Lainnya <span class="text-red-500">*</span></label>
                    <input id="otherClaimType" type="text" v-model="form.otherClaimType" required class="form-input w-full" placeholder="Masukkan jenis klaim">
                  </div>
                </div>

                <!-- B. Detail Klaim -->
                <div class="mb-8">
                  <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">B. Detail Klaim</h2>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" for="treatmentStartDate">Tanggal Masuk Perawatan <span class="text-red-500">*</span></label>
                      <Datepicker v-model="form.treatmentStartDate"/>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" for="treatmentEndDate">Tanggal Keluar Perawatan <span class="text-red-500">*</span></label>
                      <Datepicker v-model="form.treatmentEndDate"/>
                    </div>
                  </div>
                </div>

                <!-- D. Jumlah Klaim -->
                <div class="mb-8">
                  <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">D. Jumlah Klaim</h2>
                  <div class="flex gap-4">
                    <div class="w-1/3">
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" for="currency">Mata Uang <span class="text-red-500">*</span></label>
                      <select id="currency" v-model="form.currency" required class="form-select w-full">
                        <option value="IDR">IDR</option>
                        <option value="USD">USD</option>
                        <option value="EUR">EUR</option>
                      </select>
                    </div>
                    <div class="flex-1">
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" for="claimAmount">Total Jumlah Klaim <span class="text-red-500">*</span></label>
                      <input id="claimAmount" type="number" v-model="form.claimAmount" required min="0" step="0.01" class="form-input w-full" placeholder="0.00">
                    </div>
                  </div>
                </div>

                <!-- Dokumen yang Perlu Diupload -->
                <div class="mb-8">
                  <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Dokumen yang Perlu Diupload</h2>
                  
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium mb-1" for="hospitalInvoice">
                        Invoice Tagihan Rumah Sakit 
                        <span class="text-red-500">{{ !isEditing ? '*' : '' }}</span>
                      </label>
                      <div class="flex items-center gap-4">
                        <input id="hospitalInvoice" type="file" @change="handleFileUpload($event, 'hospitalInvoice')" accept=".pdf,.jpg,.jpeg,.png" :required="!isEditing" class="form-input flex-1">
                        <button v-if="isEditing && getExistingDocument('invoice')" type="button" @click="viewDocument(getExistingDocument('invoice'))" class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors whitespace-nowrap">
                          Unduh
                        </button>
                      </div>
                      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Upload invoice/tagihan rumah sakit (PDF, JPG, PNG)</p>
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="doctorForm">
                        Surat Form yang Diisi Dokter 
                        <span class="text-red-500">{{ !isEditing ? '*' : '' }}</span>
                      </label>
                      <div class="flex items-center gap-4">
                        <input id="doctorForm" type="file" @change="handleFileUpload($event, 'doctorForm')" accept=".pdf,.jpg,.jpeg,.png" :required="!isEditing" class="form-input flex-1">
                        <button v-if="isEditing && getExistingDocument('form')" type="button" @click="viewDocument(getExistingDocument('form'))" class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors whitespace-nowrap">
                          Unduh
                        </button>
                      </div>
                      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Upload surat form yang telah diisi dokter (PDF, JPG, PNG)</p>
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="reportLab">
                        Hasil Pemeriksaan Laboratorium (Opsional)
                      </label>
                      <div class="flex items-center gap-4">
                        <input id="reportLab" type="file" @change="handleFileUpload($event, 'reportLab')" accept=".pdf,.jpg,.jpeg,.png" class="form-input flex-1">
                        <button v-if="isEditing && getExistingDocument('reportLab')" type="button" @click="viewDocument(getExistingDocument('reportLab'))" class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors whitespace-nowrap">
                          Unduh
                        </button>
                      </div>
                      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Upload hasil pemeriksaan laboratorium (PDF, JPG, PNG)</p>
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="additionalDoc">
                        Dokumen Pendukung Lainnya (Opsional)
                      </label>
                      <div class="flex items-center gap-4">
                        <input id="additionalDoc" type="file" @change="handleFileUpload($event, 'additionalDoc')" accept=".pdf,.jpg,.jpeg,.png" class="form-input flex-1">
                        <button v-if="isEditing && getExistingDocument('additionalDoc')" type="button" @click="viewDocument(getExistingDocument('additionalDoc'))" class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors whitespace-nowrap">
                          Unduh
                        </button>
                      </div>
                      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Upload dokumen pendukung lainnya (PDF, JPG, PNG) - Opsional</p>
                    </div>
                  </div>
                </div>

                <!-- C. Konfirmasi Persetujuan -->
                <div class="mb-8">
                  <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">C. Konfirmasi Persetujuan</h2>
                  <div class="flex items-start">
                    <input type="checkbox" v-model="form.agreement" required class="form-checkbox mt-1 mr-3">
                    <label class="text-sm">
                      Dengan ini saya menyatakan bahwa semua informasi yang diberikan adalah benar dan akurat. Saya memahami bahwa informasi palsu dapat mengakibatkan penolakan klaim dan konsekuensi hukum. Saya memberikan wewenang kepada perusahaan asuransi untuk memverifikasi informasi yang diberikan.
                    </label>
                  </div>
                </div>

                <!-- Submit Button -->
                <div class="flex justify-end">
                  <button type="submit" :disabled="isSubmitting" class="btn bg-gray-900 text-gray-100 hover:bg-gray-800 dark:bg-gray-100 dark:text-gray-800 dark:hover:bg-gray-200 transition-all duration-200 ease-in-out transform dark:hover:bg-gray-800 dark:hover:text-white hover:shadow-lg dark:hover:border-gray-200 disabled:opacity-50 disabled:cursor-not-allowed">
                      <svg v-if="isSubmitting" class="animate-spin w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                      </svg>
                      <svg v-else class="fill-current shrink-0 xs:hidden" width="16" height="16" viewBox="0 0 16 16">
                          <path d="M15 7H9V1c0-.6-.4-1-1-1S7 .4 7 1v6H1c-.6 0-1 .4-1 1s.4 1 1 1h6v6c0 .6.4 1 1 1s1-.4 1-1V9h6c.6 0 1-.4 1-1s-.4-1-1-1z" />
                      </svg>
                      <span class="max-xs:sr-only">
                        {{ isSubmitting ? 'Processing...' : (isEditing ? 'Update Klaim' : 'Ajukan Klaim') }}
                      </span>
                  </button>
                </div>

          </form>
        </div>
      </main>

    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Sidebar from '../partials/Sidebar.vue'
import Header from '../partials/Header.vue'
import Banner from '../partials/Chatbot.vue'
import Datepicker from '../components/Datepicker.vue'
import { useAlert } from '../composables/useAlert.js'

export default {
  name: 'FormClaim',
  components: {
    Sidebar,
    Header,
    Banner,
    Datepicker,
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const sidebarOpen = ref(false)
    const isEditing = ref(false)
    const existingDocuments = ref([])
    const isSubmitting = ref(false)
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
    
    const form = ref({
      // Auto-filled profile data from logged in user
      nomorPolis: '',
      namaPerusahaan: '',
      nomorPeserta: '',
      namaPemegang: '',
      nik: '',
      tanggalLahir: '',
      jenisKelamin: '',
      statusPernikahan: '',
      alamat: '',
      email: '',
      nomorTelepon: '',
      premiumPlan: '',
      claimLimit: 0,
      
      // Form fields
      claimType: '',
      otherClaimType: '',
      treatmentStartDate: '',
      treatmentEndDate: '',
      currency: 'IDR',
      claimAmount: '',
      hospitalInvoice: null,
      doctorForm: null,
      agreement: false
    })

    const handleFileUpload = (event, fieldName) => {
      const file = event.target.files[0]
      if (file) {
        // Validate tipe file dan size
        const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png']
        // const maxSize = 5 * 1024 * 1024 // 5MB
        
        if (!allowedTypes.includes(file.type)) {
          alert('File type not supported. Please upload PDF, JPG, or PNG files.')
          return
        }
        
        // if (file.size > maxSize) {
        //   alert('File size too large. Maximum size is 5MB.')
        //   return
        // }
        
        form.value[fieldName] = file
      }
    }

    // Mock claims data with profile info
    const mockClaims = [
      {
        id: 3,
        type: 'rawat-jalan',
        amount: 2500000,
        checkIn: '2024-02-10',
        checkOut: '2024-02-10',
        status: 'rejected',
        profile: {
          nomorPolis: 'P003',
          namaPerusahaan: 'PT Asuransi Mandiri',
          nomorPeserta: 'CUST3456',
          namaPemegang: 'Sari Dewi',
          nik: '3201029834567',
          tanggalLahir: '1990-08-15',
          jenisKelamin: 'Female',
          statusPernikahan: 'Single',
          alamat: 'Jl. Merdeka No. 45, Bandung',
          email: 'sari.dewi@email.com',
          nomorTelepon: '081234567891'
        },
        documents: [
          { id: 1, name: 'Invoice Rumah Sakit.pdf', size: '456 KB', type: 'PDF', url: '/form/invoice-3.pdf' },
          { id: 2, name: 'Form Medis Dokter.pdf', size: '1.5 MB', type: 'PDF', url: '/form/dokter form-3.pdf' }
        ]
      },
      {
        id: 4,
        type: 'kehamilan-melahirkan',
        amount: 12000000,
        checkIn: '2024-02-15',
        checkOut: '2024-02-17',
        status: 'rejected',
        profile: {
          nomorPolis: 'P004',
          namaPerusahaan: 'PT Asuransi Central Asia',
          nomorPeserta: 'CUST4567',
          namaPemegang: 'Maya Sari',
          nik: '3201029834568',
          tanggalLahir: '1988-12-20',
          jenisKelamin: 'Female',
          statusPernikahan: 'Married',
          alamat: 'Jl. Sudirman No. 78, Jakarta',
          email: 'maya.sari@email.com',
          nomorTelepon: '081234567892'
        },
        documents: [
          { id: 1, name: 'Invoice Siloam.pdf', size: '2.2 MB', type: 'PDF', url: '/form/invoice_siloam.pdf' },
          { id: 2, name: 'Dokter Form Siloam.pdf', size: '3.1 MB', type: 'PDF', url: '/form/dokter_form_siloam.pdf' }
        ]
      }
    ]

    const loadUserProfile = async () => {
      try {
        // First try to load from API
        const response = await fetch('/api/customer/profile', {
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include'
        })
        
        if (response.ok) {
          const result = await response.json()
          const customer = result.customer
          console.log('Customer profile loaded from API:', customer)
          
          // Auto-fill form with API data - mapping sesuai struktur database
          form.value.nomorPolis = customer.policy_id || ''
          form.value.namaPerusahaan = customer.insurance_company || 'PT XYZ Asuransi'
          form.value.nomorPeserta = customer.customer_no || ''
          form.value.namaPemegang = customer.name || ''
          form.value.nik = customer.NIK || ''
          form.value.tanggalLahir = customer.dob || ''
          form.value.jenisKelamin = customer.gender || ''
          form.value.statusPernikahan = customer.marital_status || ''
          form.value.alamat = customer.address || ''
          form.value.email = customer.email || ''
          form.value.nomorTelepon = customer.phone || ''
          
          // Set premium plan and claim limits
          form.value.premiumPlan = customer.premium_plan || 'basic'
          
          // Set claim limits based on premium plan
          const claimLimits = {
            'basic': 50000000,
            'premium': 100000000,
            'platinum': 200000000
          }
          form.value.claimLimit = claimLimits[customer.premium_plan] || 50000000
          
          return
        }
      } catch (error) {
        console.error('Error loading user profile from API:', error)
      }
      
      // Fallback to localStorage if API fails
      const userData = JSON.parse(localStorage.getItem('user') || '{}')
      console.log('Loading user data from localStorage:', userData)
      console.log('NIK from userData:', userData.NIK)
      console.log('policy_id from userData:', userData.policy_id)
      console.log('insurance_company from userData:', userData.insurance_company)
      
      if (userData && userData.id) {
        form.value.nomorPolis = userData.policy_id || ''
        form.value.namaPerusahaan = userData.insurance_company || 'PT XYZ Asuransi'
        form.value.nomorPeserta = userData.customer_no || ''
        form.value.namaPemegang = userData.name || ''
        form.value.nik = userData.NIK || ''
        form.value.tanggalLahir = userData.dob || ''
        form.value.jenisKelamin = userData.gender || ''
        form.value.statusPernikahan = userData.marital_status || ''
        form.value.alamat = userData.address || ''
        form.value.email = userData.email || ''
        form.value.nomorTelepon = userData.phone || ''
        form.value.premiumPlan = userData.premium_plan || 'basic'
        
        console.log('Form values after setting:', {
          nomorPolis: form.value.nomorPolis,
          namaPerusahaan: form.value.namaPerusahaan,
          nik: form.value.nik
        })
        
        // Set claim limits
        const claimLimits = {
          'basic': 50000000,
          'premium': 100000000,
          'platinum': 200000000
        }
        form.value.claimLimit = claimLimits[userData.premium_plan] || 50000000
      }
    }

    const loadClaimData = async () => {
      const editId = route.query.edit
      
      if (editId) {
        try {
          const response = await fetch(`http://localhost:5000/api/claims/${editId}`, {
            credentials: 'include'
          })
          const result = await response.json()
          
          if (result.status === 'success' && result.claim) {
            const claim = result.claim
            console.log('Raw claim data from API:', claim)
            
            // Only allow editing rejected claims
            if (claim.claim_status !== 'Rejected') {
              alert('Only rejected claims can be edited')
              router.push('/claim-history')
              return
            }
            
            isEditing.value = true
            

            // Load claim data with proper mapping
            form.value.claimType = claim.claim_type || ''
            form.value.claimAmount = claim.claim_amount || ''
            form.value.currency = claim.currency || 'IDR'
            form.value.treatmentStartDate = claim.date_checkin ? new Date(claim.date_checkin + 'T00:00:00') : ''
            form.value.treatmentEndDate = claim.date_checkout ? new Date(claim.date_checkout + 'T00:00:00') : ''
            form.value.namaPerusahaan = claim.insurance_company || ''
            
            // Load existing documents
            existingDocuments.value = claim.document_details || []
            
            console.log('Loaded claim data:', {
              claimType: form.value.claimType,
              claimAmount: form.value.claimAmount,
              currency: form.value.currency,
              treatmentStartDate: form.value.treatmentStartDate,
              treatmentEndDate: form.value.treatmentEndDate,
              namaPerusahaan: form.value.namaPerusahaan,
              documents: existingDocuments.value.length
            })
            
            console.log('Existing documents:', existingDocuments.value)
          }
        } catch (error) {
          console.error('Error fetching claim data:', error)
          alert('Failed to load claim data')
          router.push('/claim-history')
        }
      }
    }

    const getExistingDocument = (type) => {
      if (!existingDocuments.value.length) return null
      
      // Map document types from database to form types
      const typeMap = {
        'invoice': ['invoice'],
        'form': ['doctor form'],
        'reportLab': ['report lab'],
        'additionalDoc': ['additional document']
      }
      
      const searchTypes = typeMap[type] || []
      return existingDocuments.value.find(doc => 
        searchTypes.some(searchType => doc.doc_type === searchType)
      )
    }

    const viewDocument = (document) => {
      window.open(document.url, '_blank')
    }

    const { showSuccess, showError } = useAlert()

    const submitClaim = async () => {
      if (isSubmitting.value) return
      
      // Validate claim amount against limit
      const claimAmount = parseFloat(form.value.claimAmount)
      if (claimAmount > form.value.claimLimit) {
        showError(
          'Jumlah Klaim Melebihi Batas',
          `Jumlah klaim Rp ${formatCurrency(claimAmount)} melebihi batas maksimal Rp ${formatCurrency(form.value.claimLimit)} untuk paket ${form.value.premiumPlan}.`
        )
        return
      }
      
      isSubmitting.value = true
      try {
        const formData = new FormData()
        
        // Add form fields
        formData.append('claimType', form.value.claimType)
        formData.append('claimAmount', form.value.claimAmount)
        formData.append('currency', form.value.currency)
        formData.append('customerId', currentUser.id)
        formData.append('policyId', form.value.nomorPolis)
        // Ensure dates are in YYYY-MM-DD format for backend
        const formatDateForBackend = (date) => {
          if (!date) return new Date().toISOString().split('T')[0];
          if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date)) return date;
          if (date instanceof Date) return date.toISOString().split('T')[0];
          return date;
        };
        
        formData.append('treatmentStartDate', formatDateForBackend(form.value.treatmentStartDate))
        formData.append('treatmentEndDate', formatDateForBackend(form.value.treatmentEndDate))
        formData.append('insuranceCompany', form.value.namaPerusahaan)
        
        if (isEditing.value) {
          formData.append('claimId', route.query.edit)
          formData.append('isEdit', 'true')
        }
        
        // Add files
        if (form.value.hospitalInvoice) {
          formData.append('hospitalInvoice', form.value.hospitalInvoice)
        }
        if (form.value.doctorForm) {
          formData.append('doctorForm', form.value.doctorForm)
        }
        if (form.value.reportLab) {
          formData.append('reportLab', form.value.reportLab)
        }
        if (form.value.additionalDoc) {
          formData.append('additionalDoc', form.value.additionalDoc)
        }
        
        const token = localStorage.getItem('token')
        const response = await fetch('http://localhost:5000/api/submit-claim', {
          method: 'POST',
          credentials: 'include',
          body: formData
        })
        
        const result = await response.json()
        
        if (response.ok) {
          showSuccess(
            isEditing.value ? 'Klaim Berhasil Diupdate!' : 'Klaim Berhasil Diajukan!',
            isEditing.value 
              ? `Klaim ${result.claim_id} telah berhasil diupdate. Tim kami akan memproses ulang klaim Anda dalam 1-3 hari kerja.`
              : `Klaim Anda telah berhasil disubmit dengan ID: ${result.claim_id}. Tim kami akan memproses klaim Anda dalam 1-3 hari kerja.`
          )
          
          setTimeout(() => {
            router.push('/claim-history')
          }, 2000)
        } else {
          showError(
            isEditing.value ? 'Gagal Mengupdate Klaim' : 'Gagal Mengajukan Klaim',
            result.error || 'Terjadi kesalahan saat memproses klaim. Silakan coba lagi.'
          )
        }
      } catch (error) {
        showError(
          'Kesalahan Sistem',
          'Terjadi kesalahan koneksi. Silakan periksa koneksi internet Anda dan coba lagi.'
        )
      } finally {
        isSubmitting.value = false
      }
    }


    watch(() => form.value.treatmentStartDate, (newVal) => {
      if (newVal && isEditing.value) {
        console.log('Start date updated:', newVal)
      }
    })

    watch(() => form.value.treatmentEndDate, (newVal) => {
      if (newVal && isEditing.value) {
        console.log('End date updated:', newVal)
      }
    })


    
    onMounted(async () => {
      await loadUserProfile()
      await loadUserProfile()
      await loadClaimData()
    })

    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('id-ID').format(amount)
    }

    return {
      sidebarOpen,
      form,
      isEditing,
      isSubmitting,
      existingDocuments,
      handleFileUpload,
      viewDocument,
      getExistingDocument,
      submitClaim,
      formatCurrency
    }
  }
}
</script>
