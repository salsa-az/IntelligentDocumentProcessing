<template>
  <!-- AI Assistant Chat Widget -->
  <div class="fixed bottom-0 z-50 transition-all duration-300" :class="claimDetailOpen ? 'right-[24rem]' : 'right-2'">
    <!-- Expanded Chat Window -->
    <div v-if="isExpanded" class="bg-white dark:bg-gray-800 rounded-tl-lg rounded-tr-lg shadow-2xl border border-gray-200 dark:border-gray-700 w-96 h-screen flex flex-col">
      <!-- Chat Header -->
      <div class="bg-violet-500 text-white p-4 rounded-tl-lg rounded-tr-lg flex justify-between items-center">
        <div class="flex items-center">
          <div class="w-8 h-8 bg-white rounded-full flex items-center justify-center mr-3">
            <svg class="w-5 h-5 text-violet-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
            </svg>
          </div>
          <div>
            <h3 class="font-semibold">AI Asisten Klaim</h3>
            <p class="text-xs opacity-90">Tanya tentang klaim Anda</p>
          </div>
        </div>
        <button @click="toggleChat" class="text-white hover:text-gray-200">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"/>
          </svg>
        </button>
      </div>

      <!-- Chat Messages -->
      <div class="flex-1 p-4 overflow-y-auto bg-gray-50 dark:bg-gray-900">
        <div class="space-y-4">
          <!-- Welcome Message -->
          <div class="flex items-start">
            <div class="w-8 h-8 bg-violet-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
              </svg>
            </div>
            <div class="bg-white dark:bg-gray-800 rounded-lg p-3 max-w-xs">
              <p class="text-sm text-gray-800 dark:text-gray-200">Halo! Saya AI Asisten untuk membantu Anda dengan pertanyaan seputar klaim asuransi. Ada yang bisa saya bantu?</p>
            </div>
          </div>

          <!-- Chat Messages -->
          <div v-for="message in messages" :key="message.id" class="flex" :class="message.isUser ? 'justify-end' : 'items-start'">
            <div v-if="!message.isUser" class="w-8 h-8 bg-violet-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
              </svg>
            </div>
            <div class="rounded-lg p-3 max-w-xs" :class="message.isUser ? 'bg-violet-500 text-white' : 'bg-white dark:bg-gray-800'">
              <p class="text-sm" :class="message.isUser ? 'text-white' : 'text-gray-800 dark:text-gray-200'">{{ message.text }}</p>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="isTyping" class="flex items-start">
            <div class="w-8 h-8 bg-violet-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
              </svg>
            </div>
            <div class="bg-white dark:bg-gray-800 rounded-lg p-3">
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat Input -->
      <div class="p-4 border-t border-gray-200 dark:border-gray-700">
        <div class="flex space-x-2">
          <input 
            v-model="newMessage" 
            @keypress.enter="sendMessage"
            type="text" 
            placeholder="Ketik pertanyaan Anda..."
            class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 dark:bg-gray-700 dark:text-white"
          >
          <button 
            @click="sendMessage"
            :disabled="!newMessage.trim()"
            class="px-4 py-2 bg-violet-500 text-white rounded-lg hover:bg-violet-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Chat Toggle Button -->
    <button 
      v-if="!isExpanded"
      @click="toggleChat"
      class="bg-violet-500 hover:bg-violet-600 text-white shadow-lg transition-all duration-200 flex items-center justify-center w-30 h-12 rounded-tl-lg rounded-tr-lg mr-2"
    >
      <div class="flex items-center space-x-2.5">
        <svg class="w-6.5 h-6.5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd"/>
        </svg>
        <span class="text-lg font-medium">Chat</span>
      </div>
    </button>

    <!-- Notification Badge -->
    <div v-if="!isExpanded && hasNewMessage" class="absolute -top-2 -right-2 w-6 h-6 bg-violet-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
      {{ unreadCount }}
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'

export default {
  name: 'AIAssistant',
  props: {
    claimDetailOpen: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const isExpanded = ref(false)
    const newMessage = ref('')
    const isTyping = ref(false)
    const hasNewMessage = ref(false)
    const unreadCount = ref(0)
    const messages = ref([])

    const aiResponses = [
      "Untuk klaim rawat inap, Anda perlu menyiapkan invoice rumah sakit dan surat keterangan dokter.",
      "Proses klaim biasanya memakan waktu 7-14 hari kerja setelah dokumen lengkap diterima.",
      "Pastikan semua dokumen dalam format PDF atau JPG dengan ukuran maksimal 5MB.",
      "Untuk klaim kecelakaan, diperlukan kronologi kejadian dan laporan polisi jika ada.",
      "Anda dapat mengecek status klaim melalui dashboard atau menghubungi customer service.",
      "Klaim gigi memiliki limit tahunan, pastikan cek polis Anda untuk detailnya.",
      "Untuk klaim kehamilan, ada masa tunggu 9 bulan dari tanggal polis aktif."
    ]

    const toggleChat = () => {
      isExpanded.value = !isExpanded.value
      if (isExpanded.value) {
        hasNewMessage.value = false
        unreadCount.value = 0
      }
    }

    const sendMessage = async (messageText = null) => {
      const message = messageText || newMessage.value.trim()
      if (!message) return

      // Add user message
      messages.value.push({
        id: Date.now(),
        text: message,
        isUser: true
      })

      if (!messageText) newMessage.value = ''

      // Show typing indicator
      isTyping.value = true

      try {
        // Call external chatbot API if available
        if (window.chatbotAPI) {
          const response = await window.chatbotAPI.sendMessage(message)
          isTyping.value = false
          messages.value.push({
            id: Date.now() + 1,
            text: response,
            isUser: false
          })
        } else {
          // Fallback to local responses
          await new Promise(resolve => setTimeout(resolve, 1500))
          isTyping.value = false
          const response = getAIResponse(message)
          messages.value.push({
            id: Date.now() + 1,
            text: response,
            isUser: false
          })
        }
      } catch (error) {
        isTyping.value = false
        messages.value.push({
          id: Date.now() + 1,
          text: 'Maaf, terjadi kesalahan. Silakan coba lagi.',
          isUser: false
        })
      }

      // Scroll to bottom
      await nextTick()
      const chatContainer = document.querySelector('.overflow-y-auto')
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight
      }
    }

    const getAIResponse = (userMessage) => {
      const msg = userMessage.toLowerCase()
      
      if (msg.includes('rawat inap') || msg.includes('hospitalisasi')) {
        return "Untuk klaim rawat inap, Anda perlu menyiapkan: 1) Invoice/tagihan rumah sakit, 2) Surat keterangan dokter, 3) Resume medis. Pastikan semua dokumen asli dan lengkap."
      }
      
      if (msg.includes('dokumen') || msg.includes('berkas')) {
        return "Dokumen yang diperlukan: Invoice rumah sakit, surat form dokter, dan kronologi kejadian (jika kecelakaan). Format file: PDF, JPG, PNG maksimal 5MB."
      }
      
      if (msg.includes('berapa lama') || msg.includes('proses')) {
        return "Proses klaim memakan waktu 7-14 hari kerja setelah semua dokumen lengkap diterima dan diverifikasi."
      }
      
      if (msg.includes('kecelakaan')) {
        return "Untuk klaim kecelakaan, diperlukan kronologi kejadian yang detail dan laporan polisi jika tersedia. Pastikan tanggal kejadian sesuai dengan dokumen medis."
      }
      
      if (msg.includes('gigi') || msg.includes('dental')) {
        return "Klaim gigi memiliki limit tahunan sesuai polis. Pastikan treatment dilakukan di provider yang bekerja sama dengan asuransi."
      }

      // Random response for other questions
      return aiResponses[Math.floor(Math.random() * aiResponses.length)]
    }

    // Expose methods for external integration
    const addMessage = (text, isUser = false) => {
      messages.value.push({
        id: Date.now(),
        text,
        isUser
      })
    }

    const clearMessages = () => {
      messages.value = []
    }

    return {
      isExpanded,
      newMessage,
      isTyping,
      hasNewMessage,
      unreadCount,
      messages,
      toggleChat,
      sendMessage,
      addMessage,
      clearMessages
    }
  }
}
</script>