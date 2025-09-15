<template>
  <main class="bg-white dark:bg-gray-900">
    <div class="relative flex">
      <!-- Content -->
      <div class="w-full">
        <div class="min-h-[100dvh] h-full flex flex-col justify-center">
          <div class="max-w-lg mx-auto w-full px-4 py-8">
            <!-- Logo -->
            <div class="flex justify-center">
              <svg class="fill-violet-500" xmlns="http://www.w3.org/2000/svg" width="48" height="48">
                <path d="M31.956 14.8C31.372 6.92 25.08.628 17.2.044V5.76a9.04 9.04 0 0 0 9.04 9.04h5.716ZM14.8 26.24v5.716C6.92 31.372.63 25.08.044 17.2H5.76a9.04 9.04 0 0 1 9.04 9.04Zm11.44-9.04h5.716c-.584 7.88-6.876 14.172-14.756 14.756V26.24a9.04 9.04 0 0 1 9.04-9.04ZM.044 14.8C.63 6.92 6.92.628 14.8.044V5.76a9.04 9.04 0 0 1-9.04 9.04H.044Z" />
              </svg>
            </div>

            <div class="flex justify-center mb-8">
              <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Sign Up</h1>
            </div>

            <!-- Form -->
            <div class="rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8">
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