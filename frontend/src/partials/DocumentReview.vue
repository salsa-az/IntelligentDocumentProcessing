<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-lg w-3/4 h-3/4 flex">
      <!-- Left Panel: Document Viewer (Scrollable) -->
      <div class="w-2/3 p-4 border-r border-gray-200 dark:border-gray-700 flex justify-center items-center">
        <div class="pdf-wrapper">
          <!-- Use iframe to display the PDF -->
           <embed src="{{ documentUrl }}"></embed>  
            <p>Your browser does not support PDFs. <a :href="documentUrl" target="_blank" rel="noopener">Download the PDF</a>.</p>
        </div>
      </div>

      <!-- Right Panel: Metadata -->
      <div class="w-1/3 p-4 overflow-y-auto max-h-full">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Document Metadata</h2>
        <div class="mt-4 space-y-2">
          <p><strong>Document ID:</strong> {{ metadata.doc_id }}</p>
          <p><strong>Document Type:</strong> {{ metadata.doc_type }}</p>
          <!-- Download Button -->
          <button  class="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
            <a :href="documentUrl" target="_blank" rel="noopener">Download the PDF</a>
          </button>
        </div>
      </div>

      <!-- Close Button -->
      <button @click="close" class="absolute top-2 right-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
        ✕
      </button>
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

    // Fetch document and metadata
    const fetchDocumentData = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/documents/${props.docId}`);
        const data = await response.json();
        
        // Update metadata
        metadata.value = {
          doc_id: data.doc_id,
          doc_type: data.doc_type,
        };
        // Use the SAS URL returned by Flask
        documentUrl.value = data.doc_url;
      } catch (error) {
        console.error('Error fetching document data:', error);
      }
    };

    // Download the document when button is clicked
    const downloadDocument = () => {
      if (documentUrl.value) {
        // Open the SAS URL in a new tab to trigger the download
        const link = document.createElement('a');
        link.href = documentUrl.value;
        link.target = '_blank';
        link.click();
      }
    };

    // Close modal
    const close = () => {
      emit('close');
    };

    onMounted(() => {
      fetchDocumentData();
    });

    return {
      documentUrl,
      metadata,
      close,
      downloadDocument,
    };
  },
};
</script>

<style scoped>
/* Add styles to adjust the look of the modal */
.fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 50;
}

.w-1  {
  flex: 0 0 33.33333%; /* Ensures the right panel takes up 1/3 of the width */
}

.overflow-y-auto {
  overflow-y: auto; /* Enables vertical scrolling if content exceeds height */
}

.max-h-full {
  max-height: 100%; /* Ensures the right panel has a flexible height */
}

/* PDF Wrapper: Make left panel scrollable */
.pdf-wrapper {
  width: 100%;
  max-height: 80vh; /* Maximum height of 80% of the viewport height */
  overflow-y: auto; /* Allow vertical scrolling if content exceeds max-height */
}

.pdf-embed {
  width: 100%;
  height: auto;
  max-width: 90%; /* Adjust the maximum width of the PDF */
  max-height: 100%; /* Limit the height of the PDF */
}

/* Styling for the download button */
button {
  text-decoration: none;
}
</style>
