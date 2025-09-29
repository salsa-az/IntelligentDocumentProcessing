<template>
  <main class="bg-white dark:bg-gray-900">
    <div class="relative flex">
      <!-- Content -->
      <div class="w-full">
        <div class="min-h-[100dvh] h-full flex flex-col justify-center">
          <div class="max-w-2xl mx-auto w-full px-4 py-8">
            <!-- Logo -->
            <div class="flex justify-center">
              <svg class="fill-violet-500" xmlns="http://www.w3.org/2000/svg" width="48" height="48">
                <path d="M31.956 14.8C31.372 6.92 25.08.628 17.2.044V5.76a9.04 9.04 0 0 0 9.04 9.04h5.716ZM14.8 26.24v5.716C6.92 31.372.63 25.08.044 17.2H5.76a9.04 9.04 0 0 1 9.04 9.04Zm11.44-9.04h5.716c-.584 7.88-6.876 14.172-14.756 14.756V26.24a9.04 9.04 0 0 1 9.04-9.04ZM.044 14.8C.63 6.92 6.92.628 14.8.044V5.76a9.04 9.04 0 0 1-9.04 9.04H.044Z" />
              </svg>
            </div>

            <div class="flex justify-center mb-8">
              <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Registration</h1>
            </div>

            <!-- Progress Steps -->
            <div class="mb-8">
              <div class="flex items-center justify-center space-x-4">
                <div v-for="(step, index) in steps" :key="index" class="flex items-center">
                  <div :class="['w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium', 
                    currentStep > index ? 'bg-violet-500 text-white' : 
                    currentStep === index ? 'bg-violet-100 text-violet-600 border-2 border-violet-500' : 
                    'bg-gray-200 text-gray-500']">
                    <svg v-if="currentStep > index" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                    </svg>
                    <span v-else>{{ index + 1 }}</span>
                  </div>
                  <div v-if="index < steps.length - 1" :class="['ml-4 mr-4 h-0.5 w-20', currentStep > index ? 'bg-violet-500' : 'bg-gray-200']"></div>
                </div>
              </div>
              <div class="flex justify-center mt-2">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ steps[currentStep] }}</span>
              </div>
            </div>

            <!-- Step 1: Document Upload -->
            <div v-if="currentStep === 0" class="rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8">
              <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-6">Upload Documents for Auto-Fill</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">Upload your insurance card and ID card to automatically fill your registration information.</p>
              
              <div class="space-y-6">
                <!-- Insurance Card Upload -->
                <div>
                  <label class="block text-sm font-medium mb-2">Insurance Card</label>
                  <div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-violet-400 transition-colors">
                    <input 
                      type="file" 
                      ref="insuranceCardFile" 
                      @change="handleInsuranceCardUpload" 
                      accept="image/*,.pdf"
                      class="hidden"
                    >
                    <div v-if="!uploadedFiles.insuranceCard" @click="$refs.insuranceCardFile.click()" class="cursor-pointer">
                      <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                      </svg>
                      <p class="mt-2 text-sm text-gray-600">Click to upload insurance card</p>
                      <p class="text-xs text-gray-500">PNG, JPG, PDF up to 10MB</p>
                    </div>
                    <div v-else class="flex items-center justify-between">
                      <div class="flex items-center">
                        <svg class="h-8 w-8 text-violet-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 0v12h8V4H6z" clip-rule="evenodd" />
                        </svg>
                        <span class="ml-2 text-sm text-gray-700">{{ uploadedFiles.insuranceCard.name }}</span>
                      </div>
                      <button @click="removeInsuranceCard" class="text-red-500 hover:text-red-700">
                        <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>

                <!-- ID Card Upload -->
                <div>
                  <label class="block text-sm font-medium mb-2">ID Card (KTP)</label>
                  <div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-violet-400 transition-colors">
                    <input 
                      type="file" 
                      ref="idCardFile" 
                      @change="handleIdCardUpload" 
                      accept="image/*,.pdf"
                      class="hidden"
                    >
                    <div v-if="!uploadedFiles.idCard" @click="$refs.idCardFile.click()" class="cursor-pointer">
                      <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                      </svg>
                      <p class="mt-2 text-sm text-gray-600">Click to upload ID card</p>
                      <p class="text-xs text-gray-500">PNG, JPG, PDF up to 10MB</p>
                    </div>
                    <div v-else class="flex items-center justify-between">
                      <div class="flex items-center">
                        <svg class="h-8 w-8 text-violet-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 0v12h8V4H6z" clip-rule="evenodd" />
                        </svg>
                        <span class="ml-2 text-sm text-gray-700">{{ uploadedFiles.idCard.name }}</span>
                      </div>
                      <button @click="removeIdCard" class="text-red-500 hover:text-red-700">
                        <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="flex justify-between mt-8">
                <router-link to="/signin" class="px-6 py-2 text-sm text-gray-600 hover:text-gray-800">
                  Already have account? Sign In
                </router-link>
                <button 
                  @click="processDocuments" 
                  :disabled="!uploadedFiles.insuranceCard && !uploadedFiles.idCard"
                  class="btn bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Process Documents
                </button>
              </div>
            </div>
              <form @submit.prevent="handleSignup">
                <div class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="nomorPolis">Nomor Polis <span class="text-red-500">*</span></label>
                    <input id="nomorPolis" v-model="form.nomorPolis" class="form-input w-full" type="text" required />
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1" for="namaPerusahaan">Nama Perusahaan Asuransi <span class="text-red-500">*</span></label>
                    <input id="namaPerusahaan" v-model="form.namaPerusahaan" class="form-input w-full" type="text" required />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="nomorPeserta">Nomor Peserta <span class="text-red-500">*</span></label>
                    <input id="nomorPeserta" v-model="form.nomorPeserta" class="form-input w-full" type="text" required />
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1" for="namaPemegang">Nama Pemegang Polis <span class="text-red-500">*</span></label>
                    <input id="namaPemegang" v-model="form.namaPemegang" class="form-input w-full" type="text" required />
                  </div>
                </div>

                <div>
                  <label class="flex items-center mb-4">
                    <input type="checkbox" v-model="isPemegangPolis" class="form-checkbox" />
                    <span class="text-sm ml-2">Saya adalah pemegang polis</span>
                  </label>
                </div>

                <div v-if="!isPemegangPolis">
                  <label class="block text-sm font-medium mb-1" for="namaPeserta">Nama Peserta (jika bukan pemegang polis) <span class="text-red-500">*</span></label>
                  <input id="namaPeserta" v-model="form.namaPeserta" class="form-input w-full" type="text" :required="!isPemegangPolis" />
                </div>

                <div v-if="!isPemegangPolis">
                  <label class="block text-sm font-medium mb-1" for="hubungan">Hubungan dengan Pemegang Polis <span class="text-red-500">*</span></label>
                  <select id="hubungan" v-model="form.hubungan" class="form-select w-full" :required="!isPemegangPolis">
                    <option value="">Pilih Hubungan</option>
                    <option value="suami">Suami</option>
                    <option value="istri">Istri</option>
                    <option value="anak">Anak</option>
                    <option value="orang-tua">Orang Tua</option>
                    <option value="lainnya">Lainnya</option>
                  </select>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" for="treatmentStartDate">Tanggal Efektif<span class="text-red-500">*</span></label>
                    <Datepicker />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" for="treatmentEndDate">Tanggal Kedaluarsa<span class="text-red-500">*</span></label>
                    <Datepicker />
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium mb-1" for="nik">NIK <span class="text-red-500">*</span></label>
                  <input id="nik" v-model="form.nik" class="form-input w-full" type="text" required />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="tanggalLahir">Tanggal Lahir <span class="text-red-500">*</span></label>
                    <input id="tanggalLahir" v-model="form.tanggalLahir" class="form-input w-full" type="date" required />
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1" for="jenisKelamin">Jenis Kelamin <span class="text-red-500">*</span></label>
                    <select id="jenisKelamin" v-model="form.jenisKelamin" class="form-select w-full" required>
                      <option value="">Pilih Jenis Kelamin</option>
                      <option value="laki-laki">Laki-laki</option>
                      <option value="perempuan">Perempuan</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1" for="statusPernikahan">Status Pernikahan <span class="text-red-500">*</span></label>
                  <select id="statusPernikahan" v-model="form.statusPernikahan" class="form-select w-full" required>
                    <option value="">Pilih Status</option>
                    <option value="belum-menikah">Belum Menikah</option>
                    <option value="menikah">Menikah</option>
                    <option value="cerai">Cerai</option>
                    <option value="janda-duda">Janda/Duda</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1" for="alamat">Alamat <span class="text-red-500">*</span></label>
                  <textarea id="alamat" v-model="form.alamat" class="form-textarea w-full" rows="3" required></textarea>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="email">Email <span class="text-red-500">*</span></label>
                    <input id="email" v-model="form.email" class="form-input w-full" type="email" required />
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1" for="nomorTelepon">Nomor Telepon <span class="text-red-500">*</span></label>
                    <input id="nomorTelepon" v-model="form.nomorTelepon" class="form-input w-full" type="tel" required />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1" for="password">Password <span class="text-red-500">*</span></label>
                  <input id="password" v-model="form.password" class="form-input w-full" type="password" required />
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1" for="confirmPassword">Konfirmasi Password <span class="text-red-500">*</span></label>
                  <input id="confirmPassword" v-model="form.confirmPassword" class="form-input w-full" type="password" required />
                </div>
              </div>

              <div class="space-y-4 mt-6">
                <!-- <label class="flex items-center">
                  <input type="checkbox" v-model="agreeTerms" class="form-checkbox" required />
                  <span class="text-sm ml-2">I agree with the <a class="underline hover:no-underline" href="#0">Terms and Conditions</a></span>
                </label> -->
                <label class="flex items-center">
                  <input type="checkbox" v-model="dataDeclaration" class="form-checkbox" required />
                  <span class="text-sm ml-2">Dengan ini saya menyatakan bahwa seluruh data dan/atau informasi yang saya sampaikan adalah benar</span>
                </label>
              </div>

              <div class="flex flex-wrap items-center justify-between mt-6">
                <button class="btn bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white w-full shadow-lg hover:shadow-xl transition-all duration-200">Sign Up</button>
              </div>
              </form>
            </div>

            <!-- Footer -->
            <div class="pt-5 mt-6 border-t border-gray-200 dark:border-gray-700/60">
              <div class="text-sm">
                Sudah mempunyai akun? <router-link class="font-medium text-violet-500 hover:text-violet-600 dark:hover:text-violet-400" to="/signin">Sign In</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
  </main>
</template>

<script>

import Datepicker from '../components/Datepicker.vue'

export default {
  name: 'Signup',
  components: {
    // Sidebar,
    // Header,
    // Banner,
    Datepicker,
  },
  data() {
    return {
      isPemegangPolis: false,
      agreeTerms: false,
      dataDeclaration: false,
      form: {
        nomorPolis: '',
        namaPerusahaan: '',
        nomorPeserta: '',
        namaPemegang: '',
        namaPeserta: '',
        hubungan: '',
        nik: '',
        tanggalLahir: '',
        jenisKelamin: '',
        statusPernikahan: '',
        alamat: '',
        email: '',
        nomorTelepon: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  watch: {
    isPemegangPolis(newVal) {
      if (newVal) {
        this.form.namaPeserta = ''
        this.form.hubungan = ''
      }
    }
  },
  methods: {
    handleSignup() {
      if (this.form.password !== this.form.confirmPassword) {
        alert('Password tidak cocok!')
        return
      }
      
      if (!this.agreeTerms || !this.dataDeclaration) {
        alert('Mohon setujui syarat dan ketentuan serta pernyataan data')
        return
      }
      
      // Validate tertanggung fields if not pemegang polis
      if (!this.isPemegangPolis) {
        if (!this.form.namaPeserta || !this.form.hubungan) {
          alert('Mohon lengkapi data peserta dan hubungan dengan pemegang polis')
          return
        }
      }
      
      // Handle sign up logic
      const signupData = {
        ...this.form,
        isPemegangPolis: this.isPemegangPolis
      }
      console.log('Sign up:', signupData)
      this.$router.push('/signin')
    }
  }
}
</script>