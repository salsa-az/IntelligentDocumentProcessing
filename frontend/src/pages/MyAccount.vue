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
            <h1 class="text-3xl md:text-4xl text-gray-800 dark:text-gray-100 font-bold">Akun Saya</h1>
          </div>

          <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl">
            
            <!-- Panel body -->
            <div class="p-6">
              <div class="grid grid-cols-12 gap-6">
                
                <!-- Compact user header (profile picture removed) -->
                <div class="col-span-12">
                  <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
                    <div>
                      <h2 class="text-2xl md:text-3xl leading-snug text-gray-800 dark:text-gray-100 font-bold">{{ currentUser?.name || 'User' }}</h2>
                      <div class="text-sm text-gray-500 dark:text-gray-400">
                        <span v-if="currentUser?.role === 'customer'">{{ currentUser?.policyType || 'Pemegang Polis' }}</span>
                        <span v-if="currentUser?.role === 'approver'">{{ currentUser?.jobRole || 'Staff Internal' }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Form section (expanded to full width) -->
                <div class="col-span-12">
                  <!-- Profile Form -->
                  <form @submit.prevent="updateAccount">
                    <div class="grid grid-cols-12 gap-6">
                      
                      <!-- Personal Information -->
                      <div class="col-span-12">
                        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">Informasi Pribadi</h3>
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="name">Nama Lengkap <span class="text-red-500">*</span></label>
                        <input id="name" v-model="form.name" class="form-input w-full" type="text" required />
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="email">Email <span class="text-red-500">*</span></label>
                        <input id="email" v-model="form.email" class="form-input w-full" type="email" required />
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="phone">Nomor Telepon <span class="text-red-500">*</span></label>
                        <input id="phone" v-model="form.phone" class="form-input w-full" type="tel" required />
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="birthDate">Tanggal Lahir</label>
                        <input id="birthDate" v-model="form.birthDate" class="form-input w-full" type="date" />
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="nik">NIK</label>
                        <input id="nik" v-model="form.nik" class="form-input w-full" type="text" />
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="jenisKelamin">Jenis Kelamin</label>
                        <select id="jenisKelamin" v-model="form.jenisKelamin" class="form-select w-full">
                          <option value="">Pilih Jenis Kelamin</option>
                          <option value="laki-laki">Laki-laki</option>
                          <option value="perempuan">Perempuan</option>
                        </select>
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="statusPernikahan">Status Pernikahan</label>
                        <select id="statusPernikahan" v-model="form.statusPernikahan" class="form-select w-full">
                          <option value="">Pilih Status</option>
                          <option value="belum-menikah">Belum Menikah</option>
                          <option value="menikah">Menikah</option>
                          <option value="cerai">Cerai</option>
                          <option value="janda-duda">Janda/Duda</option>
                        </select>
                      </div>
                      
                      <div class="col-span-12">
                        <label class="block text-sm font-medium mb-1" for="address">Alamat</label>
                        <textarea id="address" v-model="form.address" class="form-textarea w-full" rows="3"></textarea>
                      </div>

                      <!-- Policy Information - Only show for customers -->
                      <div v-if="currentUser?.role === 'customer'" class="col-span-12">
                        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mt-6">Informasi Polis</h3>
                      </div>
                      
                      <div v-if="currentUser?.role === 'customer'" class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="nomorPolis">Nomor Polis</label>
                        <input id="nomorPolis" v-model="form.nomorPolis" class="form-input w-full" type="text" />
                      </div>
                      
                      <div v-if="currentUser?.role === 'customer'" class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="nomorKartu">Nomor Kartu</label>
                        <input id="nomorKartu" v-model="form.nomorKartu" class="form-input w-full" type="text" />
                      </div>
                      
                      <div v-if="currentUser?.role === 'customer'" class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="nomorPeserta">Nomor Peserta</label>
                        <input id="nomorPeserta" v-model="form.nomorPeserta" class="form-input w-full" type="text" />
                      </div>
                      
                      <div v-if="currentUser?.role === 'customer'" class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="namaPemegang">Nama Pemegang Polis</label>
                        <input id="namaPemegang" v-model="form.namaPemegang" class="form-input w-full" type="text" />
                      </div>

                      <!-- Role Information - Only show for approvers -->
                      <div v-if="currentUser?.role === 'approver'" class="col-span-12">
                        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mt-6">Informasi Jabatan</h3>
                      </div>
                      
                      <div v-if="currentUser?.role === 'approver'" class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="jobRole">Jabatan</label>
                        <input id="jobRole" v-model="form.jobRole" class="form-input w-full" type="text" />
                      </div>
                      
                      <div v-if="currentUser?.role === 'approver'" class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="insuranceComp">Perusahaan Asuransi</label>
                        <input id="insuranceComp" v-model="form.insuranceComp" class="form-input w-full" type="text" />
                      </div>

                      <!-- Emergency Contact -->
                      <!-- <div class="col-span-12">
                        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 mt-6">Kontak Darurat</h3>
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="emergencyName">Nama Kontak Darurat</label>
                        <input id="emergencyName" v-model="form.emergencyName" class="form-input w-full" type="text" />
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="emergencyPhone">Nomor Telepon Darurat</label>
                        <input id="emergencyPhone" v-model="form.emergencyPhone" class="form-input w-full" type="tel" />
                      </div> -->

                      <!-- Password Change -->
                      <div class="col-span-12">
                        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mt-6">Ubah Password</h3>
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="currentPassword">Password Saat Ini</label>
                        <input id="currentPassword" v-model="form.currentPassword" class="form-input w-full" type="password" />
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="newPassword">Password Baru</label>
                        <input id="newPassword" v-model="form.newPassword" class="form-input w-full" type="password" />
                      </div>

                    </div>
                    
                    <!-- Panel footer -->
                    <div class="flex justify-end mt-6 pt-5 border-t border-gray-200 dark:border-gray-700/60">
                      <button class="btn border-gray-200 dark:border-gray-700/60 hover:border-gray-300 dark:hover:border-gray-600 text-gray-800 dark:text-gray-300 mr-3" type="button">Batal</button>
                      <button type="submit" class="btn bg-gray-900 text-gray-100 hover:bg-gray-800 dark:bg-gray-100 dark:text-gray-800 dark:hover:bg-gray-200 transition-all duration-200 ease-in-out transform dark:hover:bg-gray-800 dark:hover:text-white hover:shadow-lg dark:hover:border-gray-200">
                          <svg class="fill-current shrink-0 xs:hidden" width="16" height="16" viewBox="0 0 16 16">
                              <path d="M15 7H9V1c0-.6-.4-1-1-1S7 .4 7 1v6H1c-.6 0-1 .4-1 1s.4 1 1 1h6v6c0 .6.4 1 1 1s1-.4 1-1V9h6c.6 0 1-.4 1-1s-.4-1-1-1z" />
                          </svg>
                          <span class="max-xs:sr-only">Simpan Perubahan</span>
                      </button>
                    </div>
                  </form>


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
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth.js'
import Sidebar from '../partials/Sidebar.vue'
import Header from '../partials/Header.vue'

export default {
  name: 'MyAccount',
  components: {
    Sidebar,
    Header,
  },
  setup() {
    const sidebarOpen = ref(false)
    const { currentUser, updateUser } = useAuth()
    
    const form = ref({
      name: '',
      email: '',
      phone: '',
      birthDate: '',
      address: '',
      // Customer-specific fields
      nomorPolis: '',
      nomorKartu: '',
      nomorPeserta: '',
      namaPemegang: '',
      nik: '',
      jenisKelamin: '',
      statusPernikahan: '',
      // Approver-specific fields
      jobRole: '',
      insuranceComp: '',
      // Common fields
      emergencyName: '',
      emergencyPhone: '',
      currentPassword: '',
      newPassword: ''
    })

    // Fetch fresh user data from API
    const fetchUserData = async () => {
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        if (user.id) {
          const response = await fetch(`http://localhost:5000/api/query?query=SELECT * FROM c WHERE c.customer_id = "${user.id}"&container=customer`)
          const userData = await response.json()
          if (userData && userData.length > 0) {
            const freshUser = userData[0]
            // Update localStorage with fresh data
            localStorage.setItem('user', JSON.stringify({...user, ...freshUser}))
            initializeForm(freshUser)
          } else {
            initializeForm(user)
          }
        }
      } catch (error) {
        console.error('Error fetching user data:', error)
        // Fallback to current user data
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        initializeForm(user)
      }
    }

    const initializeForm = (user) => {
      if (user) {
        form.value = {
          name: user.name || '',
          email: user.email || '',
          phone: user.phone || '',
          birthDate: user.dob || '',
          address: user.address || '',
          // Customer fields
          nomorPolis: user.policy_id || '',
          nomorKartu: user.cardNumber || '',
          nomorPeserta: user.customer_no || '',
          namaPemegang: user.name || '',
          nik: user.NIK || user.nik || '',
          jenisKelamin: user.gender === 'Female' ? 'perempuan' : user.gender === 'Male' ? 'laki-laki' : '',
          statusPernikahan: user.marital_status === 'Married' ? 'menikah' : user.marital_status === 'Single' ? 'belum-menikah' : user.marital_status === 'Divorced' ? 'cerai' : user.marital_status === 'Widowed' ? 'janda-duda' : '',
          // Approver fields
          jobRole: user.jobRole || '',
          insuranceComp: user.insuranceComp || '',
          // Common fields
          emergencyName: user.emergencyName || '',
          emergencyPhone: user.emergencyPhone || '',
          currentPassword: '',
          newPassword: ''
        }
      }
    }

    onMounted(() => {
      fetchUserData()
    })

    const updateAccount = () => {
      if (form.value.newPassword && !form.value.currentPassword) {
        alert('Masukkan password saat ini untuk mengubah password')
        return
      }
      
      // Base update data
      const updateData = {
        name: form.value.name,
        email: form.value.email,
        phone: form.value.phone,
        dob: form.value.birthDate,
        address: form.value.address,
        emergencyName: form.value.emergencyName,
        emergencyPhone: form.value.emergencyPhone
      }
      
      // Add role-specific fields
      if (currentUser.value?.role === 'customer') {
        updateData.nomorPolis = form.value.nomorPolis
        updateData.nomorKartu = form.value.nomorKartu
        updateData.nomorPeserta = form.value.nomorPeserta
        updateData.namaPemegang = form.value.namaPemegang
        updateData.nik = form.value.nik
        updateData.jenisKelamin = form.value.jenisKelamin
        updateData.statusPernikahan = form.value.statusPernikahan
      } else if (currentUser.value?.role === 'approver') {
        updateData.jobRole = form.value.jobRole
        updateData.insuranceComp = form.value.insuranceComp
      }
      
      updateUser(updateData)
      console.log('Updating account:', updateData)
      alert('Akun berhasil diperbarui!')
      
      // Clear password fields
      form.value.currentPassword = ''
      form.value.newPassword = ''
    }

    return {
      sidebarOpen,
      currentUser,
      form,
      updateAccount
    }
  }
}
</script>