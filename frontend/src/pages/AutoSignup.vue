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

            <!-- Step 2: Processing -->
            <div v-if="currentStep === 1" class="rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8">
              <div class="text-center">
                <div class="flex justify-center mb-6">
                  <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-violet-500"></div>
                </div>
                <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-4">Processing Documents</h2>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
                  We're extracting information from your documents. This may take a few moments...
                </p>
              </div>
            </div>

            <!-- Step 3: Review & Edit Auto-filled Information -->
            <div v-if="currentStep === 2" class="rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8">
              <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-6">Review & Edit Information</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
                Review the auto-filled information below and make any necessary corrections.
              </p>

              <form class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="nomorPolis">Nomor Polis <span class="text-red-500">*</span></label>
                    <input 
                      id="nomorPolis" 
                      v-model="form.nomorPolis" 
                      class="form-input w-full" 
                      type="text" 
                      required 
                      :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('nomorPolis') }"
                    />
                    <p v-if="autoFilledFields.includes('nomorPolis')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1" for="nomorKartu">Nomor Kartu <span class="text-red-500">*</span></label>
                    <input 
                      id="nomorKartu" 
                      v-model="form.nomorKartu" 
                      class="form-input w-full" 
                      type="text" 
                      required 
                      :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('nomorKartu') }"
                    />
                    <p v-if="autoFilledFields.includes('nomorKartu')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="nomorPeserta">Nomor Peserta <span class="text-red-500">*</span></label>
                    <input 
                      id="nomorPeserta" 
                      v-model="form.nomorPeserta" 
                      class="form-input w-full" 
                      type="text" 
                      required 
                      :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('nomorPeserta') }"
                    />
                    <p v-if="autoFilledFields.includes('nomorPeserta')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1" for="namaPemegang">Nama Pemegang Polis <span class="text-red-500">*</span></label>
                    <input 
                      id="namaPemegang" 
                      v-model="form.namaPemegang" 
                      class="form-input w-full" 
                      type="text" 
                      required 
                      :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('namaPemegang') }"
                    />
                    <p v-if="autoFilledFields.includes('namaPemegang')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
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
                  <input 
                    id="namaPeserta" 
                    v-model="form.namaPeserta" 
                    class="form-input w-full" 
                    type="text" 
                    :required="!isPemegangPolis" 
                    :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('namaPeserta') }"
                  />
                  <p v-if="autoFilledFields.includes('namaPeserta')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
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
                  <input 
                    id="nik" 
                    v-model="form.nik" 
                    class="form-input w-full" 
                    type="text" 
                    required 
                    :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('nik') }"
                  />
                  <p v-if="autoFilledFields.includes('nik')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium mb-1" for="tanggalLahir">Tanggal Lahir <span class="text-red-500">*</span></label>
                    <Datepicker 
                      v-model="form.tanggalLahir"
                      :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('tanggalLahir') }"
                    />
                    <p v-if="autoFilledFields.includes('tanggalLahir')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1" for="jenisKelamin">Jenis Kelamin <span class="text-red-500">*</span></label>
                    <select 
                      id="jenisKelamin" 
                      v-model="form.jenisKelamin" 
                      class="form-select w-full" 
                      required
                      :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('jenisKelamin') }"
                    >
                      <option value="">Pilih Jenis Kelamin</option>
                      <option value="laki-laki">Laki-laki</option>
                      <option value="perempuan">Perempuan</option>
                    </select>
                    <p v-if="autoFilledFields.includes('jenisKelamin')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1" for="statusPernikahan">Status Pernikahan <span class="text-red-500">*</span></label>
                  <select 
                    id="statusPernikahan" 
                    v-model="form.statusPernikahan" 
                    class="form-select w-full" 
                    required
                    :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('statusPernikahan') }"
                  >
                    <option value="">Pilih Status</option>
                    <option value="belum-menikah">Belum Menikah</option>
                    <option value="menikah">Menikah</option>
                    <option value="cerai">Cerai</option>
                    <option value="janda-duda">Janda/Duda</option>
                  </select>
                  <p v-if="autoFilledFields.includes('statusPernikahan')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1" for="alamat">Alamat <span class="text-red-500">*</span></label>
                  <textarea 
                    id="alamat" 
                    v-model="form.alamat" 
                    class="form-textarea w-full" 
                    rows="3" 
                    required
                    :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('alamat') }"
                  ></textarea>
                  <p v-if="autoFilledFields.includes('alamat')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1" for="nomorTelepon">Nomor Telepon <span class="text-red-500">*</span></label>
                  <input 
                    id="nomorTelepon" 
                    v-model="form.nomorTelepon" 
                    class="form-input w-full" 
                    type="tel" 
                    required 
                    :class="{ 'bg-violet-50 border-violet-200 dark:bg-gray-800 dark:border-gray-600': autoFilledFields.includes('nomorTelepon') }"
                  />
                  <p v-if="autoFilledFields.includes('nomorTelepon')" class="text-xs text-violet-600 mt-1">Auto-filled from document</p>
                </div>
              </form>

              <div class="flex justify-between mt-8">
                <button 
                  @click="currentStep = 0" 
                  class="px-6 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Back to Upload
                </button>
                <button 
                  @click="proceedToFinalStep" 
                  class="btn bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
                >
                  Continue to Final Step
                </button>
              </div>
            </div>

            <!-- Step 4: Final Registration -->
            <div v-if="currentStep === 3" class="rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8">
              <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-6">Complete Registration</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
                Enter your email and password to complete your registration.
              </p>

              <form @submit.prevent="handleSignup" class="space-y-6">
                <div>
                  <label class="block text-sm font-medium mb-1" for="email">Email <span class="text-red-500">*</span></label>
                  <input id="email" v-model="form.email" class="form-input w-full" type="email" required />
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1" for="password">Password <span class="text-red-500">*</span></label>
                  <input id="password" v-model="form.password" class="form-input w-full" type="password" required />
                </div>

                <div>
                  <label class="block text-sm font-medium mb-1" for="confirmPassword">Konfirmasi Password <span class="text-red-500">*</span></label>
                  <input id="confirmPassword" v-model="form.confirmPassword" class="form-input w-full" type="password" required />
                </div>

                <div class="space-y-4">
                  <label class="flex items-center">
                    <input type="checkbox" v-model="dataDeclaration" class="form-checkbox" required />
                    <span class="text-sm ml-2">Dengan ini saya menyatakan bahwa seluruh data dan/atau informasi yang saya sampaikan adalah benar</span>
                  </label>
                </div>

                <div class="flex justify-between mt-8">
                  <button 
                    type="button"
                    @click="currentStep = 2" 
                    class="px-6 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Back to Review
                  </button>
                  <button 
                    type="submit"
                    :disabled="!form.email || !form.password || !form.confirmPassword || !dataDeclaration"
                    class="btn bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Complete Registration
                  </button>
                </div>
              </form>
            </div>

            <!-- Footer -->
            <div v-if="currentStep === 0" class="pt-5 mt-6 border-t border-gray-200 dark:border-gray-700/60">
              <div class="text-sm">
                Sudah mempunyai akun? <router-link class="font-medium text-violet-500 hover:text-violet-600 dark:hover:text-violet-400" to="/signin">Sign In</router-link>
              </div>
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
  name: 'AutoSignup',
  components: {
    Datepicker,
  },
  data() {
    return {
      currentStep: 0,
      steps: [
        'Upload Documents',
        'Processing',
        'Review Information', 
        'Complete Registration'
      ],
      uploadedFiles: {
        insuranceCard: null,
        idCard: null
      },
      processingProgress: 0,
      processingStatus: 'Initializing...',
      extractedData: {},
      autoFilledFields: [],
      isPemegangPolis: false,
      dataDeclaration: false,
      form: {
        nomorPolis: '',
        // namaPerusahaan: '',
        nomorKartu: '',
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
  methods: {
    handleInsuranceCardUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.uploadedFiles.insuranceCard = file;
      }
    },
    handleIdCardUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.uploadedFiles.idCard = file;
      }
    },
    removeInsuranceCard() {
      this.uploadedFiles.insuranceCard = null;
      if (this.$refs.insuranceCardFile) {
        this.$refs.insuranceCardFile.value = '';
      }
    },
    removeIdCard() {
      this.uploadedFiles.idCard = null;
      if (this.$refs.idCardFile) {
        this.$refs.idCardFile.value = '';
      }
    },
    async processDocuments() {
    this.currentStep = 1;
    this.processingProgress = 0;
    this.processingStatus = 'Uploading documents...';
    
    const steps = [
        { progress: 25, status: 'Uploading documents...' },
        { progress: 50, status: 'Processing insurance card...' },
        { progress: 75, status: 'Analyzing ID card...' },
        { progress: 100, status: 'Processing complete!' }
    ];

    try {
        const formData = new FormData();
        if (this.uploadedFiles.insuranceCard) {
        formData.append('insurance_card', this.uploadedFiles.insuranceCard);
        }
        if (this.uploadedFiles.idCard) {
        formData.append('id_card', this.uploadedFiles.idCard);
        }

        // Simulate processing progress
        for (let step of steps) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        this.processingProgress = step.progress;
        this.processingStatus = step.status;
        }

        const response = await fetch('http://localhost:5000/api/extract-registration-info', {
        method: 'POST',
        body: formData
        });

        if (response.ok) {
        const result = await response.json();
        if (result.status === 'success') {
            this.applyExtractedData(result.data);
        }
        
        setTimeout(() => {
            this.currentStep = 2;
        }, 1000);
        } else {
        throw new Error('Failed to process documents');
        }

    } catch (error) {
        console.error('Error processing documents:', error);
        this.processingStatus = 'Processing failed. Please try again.';
        
        setTimeout(() => {
        this.currentStep = 2;
        }, 2000);
    }
    },
    applyExtractedData(data) {
      this.extractedData = data;
      this.autoFilledFields = [];
      
      console.log('Extracted data received:', data);
      console.log('Birth date field:', data.birth_date);
      console.log('Tempat/Tgl Lahir field:', data['Tempat/Tgl Lahir']);

      // Map extracted data to form fields
      const fieldMapping = {
        'nomorPolis': data.policy_number,
        // 'namaPerusahaan': data.insurance_company,
        'nomorKartu': data.card_number,
        'nomorPeserta': data.participant_number,
        'namaPemegang': data.full_name,
        'namaPeserta': data.full_name,
        'nik': data.nik,
        'tanggalLahir': this.formatBirthDate(data.birth_date || data['Tempat/Tgl Lahir']),
        'jenisKelamin': this.mapGender(data.gender),
        'statusPernikahan': this.mapMaritalStatus(data.marital_status),
        'alamat': this.buildAddress(data)
      };

      // Apply extracted data to form and track auto-filled fields
      for (const [formField, extractedValue] of Object.entries(fieldMapping)) {
        if (extractedValue && extractedValue.trim && extractedValue.trim()) {
          this.form[formField] = extractedValue.trim();
          this.autoFilledFields.push(formField);
        }
      }
    },
    
    formatBirthDate(dateStr) {
      if (!dateStr) return '';
      console.log('Formatting birth date:', dateStr);
      // Extract date from "JAKARTA, 18- 02- 1986" format
      const match = dateStr.match(/,\s*(\d{1,2})\s*-\s*(\d{1,2})\s*-\s*(\d{4})/);
      if (match) {
        const day = match[1].padStart(2, '0');
        const month = match[2].padStart(2, '0');
        const year = match[3];
        const formatted = `${year}-${month}-${day}`;
        console.log('Formatted date:', formatted);
        return formatted;
      }
      console.log('No match found for date format');
      return '';
    },
    
    mapGender(gender) {
      if (!gender) return '';
      const g = gender.toLowerCase();
      if (g.includes('laki') || g.includes('male')) return 'laki-laki';
      if (g.includes('perempuan') || g.includes('female')) return 'perempuan';
      return '';
    },
    
    mapMaritalStatus(status) {
      if (!status) return '';
      const s = status.toLowerCase();
      if (s.includes('kawin') || s.includes('married')) return 'menikah';
      if (s.includes('belum') || s.includes('single')) return 'belum-menikah';
      if (s.includes('cerai') || s.includes('divorced')) return 'cerai';
      return '';
    },
    
    buildAddress(data) {
      const parts = [];
      if (data.address) parts.push(data.address);
      if (data.rt_rw) parts.push(`RT/RW ${data.rt_rw}`);
      if (data.kelurahan) parts.push(data.kelurahan);
      if (data.kecamatan) parts.push(data.kecamatan);
      return parts.join(', ');
    },
    proceedToFinalStep() {
      this.currentStep = 3;
    },
    async handleSignup() {
      // Validate passwords match
      if (this.form.password !== this.form.confirmPassword) {
        alert('Passwords do not match');
        return;
      }

      try {
        const registrationData = {
          ...this.form,
          isPemegangPolis: this.isPemegangPolis
        };
        
        const response = await fetch('http://localhost:5000/api/signup', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(registrationData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
          // Store token and user data
          localStorage.setItem('token', result.token);
          localStorage.setItem('user', JSON.stringify(result.user));
          
          alert('Registration successful!');
          this.$router.push('/customer-dashboard');
        } else {
          alert(result.error || 'Registration failed');
        }
      } catch (error) {
        console.error('Registration error:', error);
        alert('Registration failed. Please try again.');
      }
    }
  }
}
</script>