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
            <h1 class="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Akun Saya</h1>
          </div>

          <div class="bg-white dark:bg-gray-800 shadow-xs rounded-xl">
            
            <!-- Panel body -->
            <div class="p-6">
              <div class="grid grid-cols-12 gap-6">
                
                <!-- Profile section -->
                <div class="col-span-12 xl:col-span-4">
                  <div class="text-center">
                    <div class="inline-flex mb-4">
                      <img class="w-20 h-20 rounded-full" :src="currentUser?.avatar || '/src/images/user-avatar-32.png'" width="80" height="80" alt="User" />
                    </div>
                    <h2 class="text-xl leading-snug text-gray-800 dark:text-gray-100 font-bold mb-1">{{ currentUser?.fullName || 'User' }}</h2>
                    <div class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ currentUser?.policyType || 'Pemegang Polis' }}</div>
                    <button class="btn-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-300">
                      <svg class="w-4 h-4 fill-current opacity-50 shrink-0" viewBox="0 0 16 16">
                        <path d="M11.7.3c-.4-.4-1-.4-1.4 0l-10 10c-.2.2-.3.4-.3.7v4c0 .6.4 1 1 1h4c.3 0 .5-.1.7-.3l10-10c.4-.4.4-1 0-1.4l-4-4zM4.6 14H2v-2.6l6-6L10.6 8l-6 6zM12 6.6L9.4 4 11 2.4 13.6 5 12 6.6z" />
                      </svg>
                      <span class="ml-2">Ubah Foto</span>
                    </button>
                  </div>
                </div>

                <!-- Form section -->
                <div class="col-span-12 xl:col-span-8">
                  <form @submit.prevent="updateAccount">
                    <div class="grid grid-cols-12 gap-6">
                      
                      <!-- Personal Information -->
                      <div class="col-span-12">
                        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">Informasi Pribadi</h3>
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="fullName">Nama Lengkap <span class="text-red-500">*</span></label>
                        <input id="fullName" v-model="form.fullName" class="form-input w-full" type="text" required />
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
                      
                      <div class="col-span-12">
                        <label class="block text-sm font-medium mb-1" for="address">Alamat</label>
                        <textarea id="address" v-model="form.address" class="form-textarea w-full" rows="3"></textarea>
                      </div>

                      <!-- Policy Information -->
                      <div class="col-span-12">
                        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100 mt-6">Informasi Polis</h3>
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="insuranceComp">Nama Perusahan Asuransi</label>
                        <input id="insuranceComp" v-model="form.insuranceComp" class="form-input w-full" type="text" />
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="policyType">Jenis Polis</label>
                        <input id="policyType" v-model="form.policyType" class="form-input w-full" type="text" />
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="policyNumber">Nomor Polis</label>
                        <input id="policyNumber" v-model="form.policyNumber" class="form-input w-full" type="text" />
                      </div>
                      
                      <div class="col-span-12 sm:col-span-6">
                        <label class="block text-sm font-medium mb-1" for="participantNumber">Nomor Peserta</label>
                        <input id="participantNumber" v-model="form.participantNumber" class="form-input w-full" type="text" />
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
                      <!-- <button class="btn bg-blue-600 hover:bg-blue-700 text-white" type="submit">Simpan Perubahan</button> -->
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
      fullName: '',
      email: '',
      phone: '',
      birthDate: '',
      address: '',
      policyNumber: '',
      participantNumber: '',
      insuranceComp: '',
      policyType: '',
      emergencyName: '',
      emergencyPhone: '',
      currentPassword: '',
      newPassword: ''
    })

    // Initialize form with user data
    onMounted(() => {
      if (currentUser.value) {
        form.value = {
          fullName: currentUser.value.fullName || '',
          email: currentUser.value.email || '',
          phone: currentUser.value.phone || '',
          birthDate: currentUser.value.birthDate || '',
          address: currentUser.value.address || '',
          policyNumber: currentUser.value.policyNumber || '',
          participantNumber: currentUser.value.participantNumber || '',
          insuranceComp: currentUser.value.insuranceComp || '',
          policyType: currentUser.value.policyType || '',
          emergencyName: currentUser.value.emergencyName || '',
          emergencyPhone: currentUser.value.emergencyPhone || '',
          currentPassword: '',
          newPassword: ''
        }
      }
    })

    const updateAccount = () => {
      if (form.value.newPassword && !form.value.currentPassword) {
        alert('Masukkan password saat ini untuk mengubah password')
        return
      }
      
      // Update user data (excluding passwords for demo)
      const updateData = {
        fullName: form.value.fullName,
        email: form.value.email,
        phone: form.value.phone,
        birthDate: form.value.birthDate,
        address: form.value.address,
        policyNumber: form.value.policyNumber,
        participantNumber: form.value.participantNumber,
        insuranceComp: form.value.insuranceComp,
        policyType: form.value.policyType,
        emergencyName: form.value.emergencyName,
        emergencyPhone: form.value.emergencyPhone
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