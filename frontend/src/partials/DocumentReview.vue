<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Dark overlay background -->
    <div class="absolute inset-0 bg-black/50"></div>
    
    <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-lg custom-modal flex z-10">
      <!-- Left Panel: Document Viewer (Scrollable) -->
      <div class="left-panel p-8 border-r border-gray-200 dark:border-gray-700 flex justify-center items-center overflow-hidden">
        <div v-if="loading" class="loader"></div>
        <div v-else class="pdf-wrapper">
          <!-- Use iframe to display the document using the SAS URL -->
          <iframe v-if="documentUrl" :src="documentUrl" class="pdf-embed" frameborder="0"></iframe>
        </div>
      </div>

      <!-- Right Panel: Metadata -->
      <div class="right-panel p-8 overflow-y-auto">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Document Metadata</h2>
        <div class="mt-4 space-y-2">
          <p><strong>Document ID:</strong> {{ metadata.doc_id }}</p>
          <p><strong>Document Type:</strong> {{ metadata.doc_type }}</p>
        </div>

        <!-- Download Button -->
        <div class="mt-4">
          <button class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors w-full mb-2">
            <a :href="documentUrl" target="_blank" rel="noopener">Download the document</a>
          </button>
        </div>

        <!-- Back Button -->
        <button @click="close" class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors w-full">
          Back
        </button>
      </div>

      <!-- Close Button -->
      <button @click="close" class="absolute top-2 right-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">✕</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  name: 'DocumentReview',
  props: {
    docId: {
      type: String,
      required: true,
    },
    show: {
      type: Boolean,
      required: true,
    },
  },
  emits: ['close'],
  setup(props, { emit }) {
    const documentUrl = ref('');
    const metadata = ref({ doc_id: '', doc_type: '' });
    const loading = ref(true);

    // Fetch document metadata and SAS URL
    const fetchDocumentData = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/documents/${props.docId}`);
        const data = await response.json();
        
        // Update metadata with document ID and type
        metadata.value = { doc_id: data.doc_id, doc_type: data.doc_type };
        
        // Get the SAS URL for the document
        documentUrl.value = data.doc_url;
      } catch (error) {
        console.error('Error fetching document data:', error);
      } finally {
        loading.value = false;
      }
    };

    const close = () => {
      emit('close');
    };

    onMounted(() => {
      fetchDocumentData();
    });

    return {
      documentUrl,
      metadata,
      loading,
      close,
    };
  },
};
</script>

<style scoped>
/* Styling for loading spinner */
.loader {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 2s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Left Panel: Document Viewer */
.left-panel {
  flex: 2;
  padding: 32px;
  border-right: 1px solid #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  height: 100%;
}

.right-panel {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  height: 100%;
}

/* PDF Wrapper: Make left panel scrollable */
.pdf-wrapper {
  width: 100%;
  height: 100%;
  max-height: 85vh; /* Maximum height of 85% of the viewport height */
  overflow-y: auto; /* Allow vertical scrolling if content exceeds max-height */
}

/* PDF and Image Scaling */
.pdf-embed {
  width: 100%;
  height: 100%; /* Take up the full available height */
  max-width: 100%;
  max-height: 100%;
}

/* Modal Styling */
.fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 50;
}

/* Fixed size for popup modal */
.custom-modal {
  width: 90vw; /* Fixed width for the entire modal */
  height: 90vh; /* Fixed height for the entire modal */
}

.overflow-y-auto {
  overflow-y: auto; /* Enables vertical scrolling if content exceeds height */
}

.max-h-full {
  max-height: 100%; /* Ensures the right panel has a flexible height */
}
</style>
