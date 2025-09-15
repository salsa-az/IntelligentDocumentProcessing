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
            <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Form Klaim Asuransi</h1>
            <p class="text-gray-600 dark:text-gray-400">Ajukan klaim asuransi Anda dengan dokumen yang diperlukan</p>
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
                      <input id="nomorPolis" type="text" v-model="form.nomorPolis" readonly class="form-input w-full">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="namaPerusahaan">Nama Perusahaan Asuransi</label>
                      <input id="namaPerusahaan" type="text" v-model="form.namaPerusahaan" readonly class="form-input w-full">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="nomorPeserta">Nomor Peserta</label>
                      <input id="nomorPeserta" type="text" v-model="form.nomorPeserta" readonly class="form-input w-full">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="namaPemegang">Nama Pemegang Polis</label>
                      <input id="namaPemegang" type="text" v-model="form.namaPemegang" readonly class="form-input w-full">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="nik">NIK</label>
                      <input id="nik" type="text" v-model="form.nik" readonly class="form-input w-full">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="tanggalLahir">Tanggal Lahir</label>
                      <input id="tanggalLahir" type="date" v-model="form.tanggalLahir" readonly class="form-input w-full">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="jenisKelamin">Jenis Kelamin</label>
                      <input id="jenisKelamin" type="text" v-model="form.jenisKelamin" readonly class="form-input w-full">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="statusPernikahan">Status Pernikahan</label>
                      <input id="statusPernikahan" type="text" v-model="form.statusPernikahan" readonly class="form-input w-full">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="email">Email</label>
                      <input id="email" type="email" v-model="form.email" readonly class="form-input w-full">
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="nomorTelepon">Nomor Telepon</label>
                      <input id="nomorTelepon" type="tel" v-model="form.nomorTelepon" readonly class="form-input w-full">
                    </div>
                    <div class="md:col-span-2">
                      <label class="block text-sm font-medium mb-1" for="alamat">Alamat</label>
                      <textarea id="alamat" v-model="form.alamat" readonly rows="2" class="form-textarea w-full"></textarea>
                    </div>
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
                      <Datepicker />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" for="treatmentEndDate">Tanggal Keluar Perawatan <span class="text-red-500">*</span></label>
                      <Datepicker />
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
                      <label class="block text-sm font-medium mb-1" for="hospitalInvoice">Invoice Tagihan Rumah Sakit <span class="text-red-500">*</span></label>
                      <input id="hospitalInvoice" type="file" @change="handleFileUpload($event, 'hospitalInvoice')" accept=".pdf,.jpg,.jpeg,.png" required class="form-input w-full">
                      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Upload invoice/tagihan rumah sakit (PDF, JPG, PNG)</p>
                    </div>
                    <div>
                      <label class="block text-sm font-medium mb-1" for="doctorForm">Surat Form yang Diisi Dokter <span class="text-red-500">*</span></label>
                      <input id="doctorForm" type="file" @change="handleFileUpload($event, 'doctorForm')" accept=".pdf,.jpg,.jpeg,.png" required class="form-input w-full">
                      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Upload surat form yang telah diisi dokter (PDF, JPG, PNG)</p>
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
                  <button type="submit" class="btn bg-violet-500 hover:bg-violet-600 text-white shadow-lg transition-all duration-200">
                    Ajukan Klaim
                  </button>
                </div>

          </form>
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
import Datepicker from '../components/Datepicker.vue'

export default {
  name: 'FormClaim',
  components: {
    Sidebar,
    Header,
    Banner,
    Datepicker,
  },
  setup() {
    const sidebarOpen = ref(false)
    
    const form = ref({
      // Auto-filled profile data
      nomorPolis: 'POL-001-2024',
      namaPerusahaan: 'PT Asuransi Terpercaya',
      nomorPeserta: 'PST-001-2024',
      namaPemegang: 'John Doe',
      nik: '1234567890123456',
      tanggalLahir: '1990-01-01',
      jenisKelamin: 'Laki-laki',
      statusPernikahan: 'Menikah',
      alamat: 'Jl. Contoh No. 123, Jakarta',
      email: 'john.doe@example.com',
      nomorTelepon: '081234567890',
      
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

    const submitClaim = async () => {
      try {
        const formData = new FormData()
        
        // Add form fields
        formData.append('claimType', form.value.claimType)
        formData.append('claimAmount', form.value.claimAmount)
        formData.append('currency', form.value.currency)
        formData.append('customerId', 'CU001') // Default customer ID
        
        // Add files
        if (form.value.hospitalInvoice) {
          formData.append('hospitalInvoice', form.value.hospitalInvoice)
        }
        if (form.value.doctorForm) {
          formData.append('doctorForm', form.value.doctorForm)
        }
        
        const response = await fetch('http://localhost:5000/api/submit-claim', {
          method: 'POST',
          body: formData
        })
        
        const result = await response.json()
        
        if (response.ok) {
          alert(`Klaim berhasil diajukan! ID: ${result.claim_id}`)
          // Reset form or redirect
        } else {
          alert(`Error: ${result.error}`)
        }
      } catch (error) {
        alert(`Error: ${error.message}`)
      }
    }

    return {
      sidebarOpen,
      form,
      handleFileUpload,
      submitClaim
    }
  }
}
</script>

