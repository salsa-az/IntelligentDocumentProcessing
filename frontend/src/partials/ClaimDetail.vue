<template>
  <div v-if="show" class="fixed inset-y-0 right-0 z-50 w-96 bg-white dark:bg-gray-800 shadow-2xl border-l border-gray-200 dark:border-gray-700 overflow-y-auto">
    <!-- Panel Header -->
    <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Claim Details</h2>
      <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <!-- Panel Content -->
    <div class="p-6">
      <!-- Claim Header -->
      <div class="mb-6">
        <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">{{ claim?.claimNumber }}</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">{{ formatDate(claim?.submittedDate) }}</p>
        <div class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">Rp {{ formatCurrency(claim?.amount) }}</div>
        <span :class="getStatusClass(claim?.status)">{{ getStatusText(claim?.status) }}</span>
      </div>

      <!-- Patient Information -->
      <div class="mb-6">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 uppercase tracking-wide">Patient Information</h4>
        <div class="space-y-3">
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Patient Name</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ claim?.patientName }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Policy Number</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ claim?.policyNumber }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Hospital</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ claim?.hospitalName }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Claim Type</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ getClaimTypeText(claim?.type) }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Treatment Period</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatDate(claim?.checkIn) }} - {{ formatDate(claim?.checkOut) }}</span>
          </div>
        </div>
      </div>

      <!-- Documents -->
      <div class="mb-6">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 uppercase tracking-wide">Documents</h4>
        <div class="space-y-2">
          <div v-for="doc in claim?.documents" :key="doc.id" class="bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="flex items-center justify-between p-3 cursor-pointer" @click="toggleDocument(doc.id)">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                  <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ doc.name }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ doc.size }}</p>
                </div>
              </div>
              <svg class="w-4 h-4 text-gray-400 transition-transform" :class="{ 'rotate-180': expandedDocs.has(doc.id) }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </div>
            
            <!-- Expanded Content -->
            <div v-if="expandedDocs.has(doc.id)" class="px-3 pb-3">
              <div class="bg-white dark:bg-gray-800 rounded p-3 text-xs">
                <!-- Dynamic content based on doc_type and doc_contents -->
                <div v-if="doc.doc_type === 'doctor form' && doc.doc_contents">
                  <h6 class="font-semibold mb-2">Form Dokter</h6>
                  <div class="space-y-2">
                    <!-- Handle the actual flat structure from your database -->
                    <div>
                      <strong>Data Administrasi Pasien</strong><br>
                      <span v-if="doc.doc_contents['Tanggal Masuk']">
                        Tanggal Masuk: {{ doc.doc_contents['Tanggal Masuk'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Tanggal Keluar']">
                        Tanggal Keluar: {{ doc.doc_contents['Tanggal Keluar'] }}
                      </span>
                    </div>
                    
                    <div>
                      <strong>Hubungan Dokter–Pasien</strong><br>
                      <span v-if="doc.doc_contents['dokterKeluarga_Ya'] === ':selected:' || doc.doc_contents['dokterKeluarga_Tidak'] === ':selected:'">
                        Apakah Anda dokter keluarga pasien?: {{ doc.doc_contents['dokterKeluarga_Ya'] === ':selected:' ? 'Ya' : 'Tidak' }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Jenis Hubungan']">
                        Hubungan keluarga dengan pasien: {{ doc.doc_contents['Jenis Hubungan'] }}
                      </span>
                    </div>
                    
                    <div>
                      <strong>Diagnosis</strong><br>
                      <span v-if="doc.doc_contents['Diagnosis Masuk']">
                        Diagnosis Masuk: {{ doc.doc_contents['Diagnosis Masuk'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Diagnosis Keluar']">
                        Diagnosis Keluar: {{ doc.doc_contents['Diagnosis Keluar'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Diagnosis Utama ICD X']">
                        Diagnosis Utama + Kode: {{ doc.doc_contents['Diagnosis Utama ICD X'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Diagnosis Penyerta ICD X']">
                        Diagnosis Penyerta + Kode: {{ doc.doc_contents['Diagnosis Penyerta ICD X'] }}
                      </span>
                    </div>
                    
                    <div>
                      <strong>Riwayat Medis & Keluhan</strong><br>
                      <span v-if="doc.doc_contents['Penyakit Lain']">
                        Penyakit terkait: {{ doc.doc_contents['Penyakit Lain'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Keluhan Utama']">
                        Keluhan utama & kronologi: {{ doc.doc_contents['Keluhan Utama'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Keluhan Tambahan']">
                        Keluhan tambahan: {{ doc.doc_contents['Keluhan Tambahan'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Field_Lainnya']">
                        Penyakit/keluhan lain terkait kondisi saat ini: {{ doc.doc_contents['Field_Lainnya'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Waktu Gejala Muncul']">
                        Sejak kapan keluhan dirasakan: {{ doc.doc_contents['Waktu Gejala Muncul'] }} (perkiraan durasi {{ doc.doc_contents['Perkiraan Lama Penyebab (bulan)'] }} bulan)<br>
                      </span>
                      <span v-if="doc.doc_contents['Pernah Mengalami Sebelumnya']">
                        Pernah mengalami kondisi serupa sebelum tanggal perawatan: {{ doc.doc_contents['Pernah Mengalami Sebelumnya'] }}
                      </span>
                    </div>
                    
                    <div>
                      <strong>Rujukan & Indikasi Rawat Inap</strong><br>
                      <span v-if="doc.doc_contents['Rujukan Dari']">
                        Pasien dirujuk oleh: {{ doc.doc_contents['Rujukan Dari'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Indikasi Rawat Inap']">
                        Indikasi rawat inap: {{ doc.doc_contents['Indikasi Rawat Inap'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Dapat Terjadi Singkat']">
                        Perkembangan diagnosis: {{ doc.doc_contents['Dapat Terjadi Singkat'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Perkiraan Lama Penyebab (bulan)']">
                        Estimasi lamanya keluhan ada: {{ doc.doc_contents['Perkiraan Lama Penyebab (bulan)'] }} bulan
                      </span>
                    </div>
                    
                    <div>
                      <strong>Pemeriksaan & Tindakan</strong><br>
                      <span v-if="doc.doc_contents['Pemeriksaan Fisik']">
                        Pemeriksaan fisik/penunjang: {{ doc.doc_contents['Pemeriksaan Fisik'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Terapi & Tindakan']">
                        Terapi/prosedur: {{ doc.doc_contents['Terapi & Tindakan'] }}
                      </span>
                    </div>
                    
                    <div>
                      <strong>Data Dokter Penanggung Jawab</strong><br>
                      <span v-if="doc.doc_contents['Nama Dokter']">
                        Nama Dokter: {{ doc.doc_contents['Nama Dokter'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['SIP Dokter']">
                        SIP: {{ doc.doc_contents['SIP Dokter'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Telepon Dokter']">
                        Nomor Telepon: {{ doc.doc_contents['Telepon Dokter'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Email Dokter']">
                        Email: {{ doc.doc_contents['Email Dokter'] }}<br>
                      </span>
                      <span v-if="doc.doc_contents['Tanggal Form']">
                        Tanggal: {{ doc.doc_contents['Tanggal Form'] }}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div v-else-if="doc.doc_type === 'invoice' && doc.doc_contents">
                  <h6 class="font-semibold mb-2">Invoice Rumah Sakit</h6>
                  <div class="space-y-1">
                    <!-- Handle the actual structure from your database -->
                    <div v-if="doc.doc_contents['Invoice #1']" class="mb-0.5">
                      <div v-if="doc.doc_contents['Invoice #1']['Invoice Id']">
                        <strong>Nomor Invoice:</strong> {{ doc.doc_contents['Invoice #1']['Invoice Id'] }}
                      </div>
                      <div v-if="doc.doc_contents['Invoice #1']['Invoice Date']">
                        <strong>Tanggal Invoice:</strong> {{ doc.doc_contents['Invoice #1']['Invoice Date'] }}
                      </div>
                      <div v-if="doc.doc_contents['Invoice #1']['Customer Name']">
                        <strong>Nama Pasien:</strong> {{ doc.doc_contents['Invoice #1']['Customer Name'] }}
                      </div>
                      <div v-if="doc.doc_contents['Invoice #1']['Invoice Date']">
                        <strong>Tanggal Layanan/Rawat:</strong> {{ doc.doc_contents['Invoice #1']['Invoice Date'] }}
                      </div>
                      <div v-if="doc.doc_contents['Invoice #1']['Items']">
                        <strong>Rincian Biaya:</strong> {{ doc.doc_contents['Invoice #1']['Items'].length }} item(s) terdaftar
                        <div v-for="(item, index) in doc.doc_contents['Invoice #1']['Items']" :key="index" class="ml-2 mt-1">
                        • {{ item.Description || 'Deskripsi tidak tersedia' }} : <em>Rp {{ formatCurrency(item.Amount || 0) }}</em>
                        </div>
                      </div>
                      <div v-if="doc.doc_contents['Invoice #1']['Invoice Total']">
                        <strong>Total Tagihan:</strong> Rp {{ formatCurrency(doc.doc_contents['Invoice #1']['Invoice Total']) }}
                      </div>
                      <div>
                        <strong>Mata Uang:</strong> IDR (Rupiah Indonesia)
                      </div>
                      <div v-if="doc.doc_contents['Invoice #1']['Vendor Name']">
                        <strong>Nama Penyedia Layanan:</strong> {{ doc.doc_contents['Invoice #1']['Vendor Name'].replace('\n', ' ') }}
                      </div>
                      <div v-if="doc.doc_contents['Invoice #1']['Vendor Address Recipient']">
                        <strong>Alamat Penyedia Layanan:</strong> {{ doc.doc_contents['Invoice #1']['Vendor Address Recipient'] }}
                      </div>
                      <div v-if="doc.doc_contents['Invoice #1']['Subtotal']">
                        <strong>Subtotal:</strong> Rp {{ formatCurrency(doc.doc_contents['Invoice #1']['Subtotal']) }}
                      </div>
                      <div v-if="doc.doc_contents['Invoice #1']['Amount Due']">
                        <strong>Amount Due:</strong> Rp {{ formatCurrency(doc.doc_contents['Invoice #1']['Amount Due']) }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-else-if="doc.doc_type === 'report lab' && doc.doc_contents">
                  <h6 class="font-semibold mb-2">Hasil Pemeriksaan Laboratorium</h6>
                  <div class="space-y-3">
                    <!-- Handle actual lab report structure -->
                    <div v-if="doc.doc_contents['0']" class="space-y-3">
                      <!-- Lab Information -->
                      <div>
                        <h6 class="font-semibold text-purple-800 dark:text-purple-300 mb-2">Informasi Laboratorium</h6>
                        <div>
                          <div v-if="doc.doc_contents['0']['Lab name']">
                            <strong>Nama Lab:</strong> {{ doc.doc_contents['0']['Lab name'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['Lab address']">
                            <strong>Alamat Lab:</strong> {{ doc.doc_contents['0']['Lab address'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['Report Date']">
                            <strong>Tanggal Laporan:</strong> {{ doc.doc_contents['0']['Report Date'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['Registration Date']">
                            <strong>Tanggal Registrasi:</strong> {{ doc.doc_contents['0']['Registration Date'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['No. registration']">
                            <strong>No. Registrasi:</strong> {{ doc.doc_contents['0']['No. registration'] }}
                          </div>
                        </div>
                      </div>

                      <!-- Patient Information -->
                      <div>
                        <h6 class="font-semibold text-blue-800 dark:text-blue-300 mb-2">Informasi Pasien</h6>
                        <div>
                          <div v-if="doc.doc_contents['0']['Patient Name']">
                            <strong>Nama Pasien:</strong> {{ doc.doc_contents['0']['Patient Name'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['Patient Age']">
                            <strong>Umur:</strong> {{ doc.doc_contents['0']['Patient Age'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['Patient Gender']">
                            <strong>Jenis Kelamin:</strong> {{ doc.doc_contents['0']['Patient Gender'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['patient Address'] || doc.doc_contents['0']['Patient address']">
                            <strong>Alamat:</strong> {{ doc.doc_contents['0']['patient Address'] || doc.doc_contents['0']['Patient address'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['Patient Contact']">
                            <strong>Kontak:</strong> {{ doc.doc_contents['0']['Patient Contact'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['ID Patient in lab']">
                            <strong>ID Pasien Lab:</strong> {{ doc.doc_contents['0']['ID Patient in lab'] }}
                          </div>
                        </div>
                      </div>

                      <!-- Doctor Information -->
                      <div>
                        <h6 class="font-semibold text-green-800 dark:text-green-300 mb-2">Informasi Dokter</h6>
                        <div>
                          <div v-if="doc.doc_contents['0']['Doctor Name']">
                            <strong>Dokter Pengirim:</strong> {{ doc.doc_contents['0']['Doctor Name'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['Doctor address']">
                            <strong>Alamat Dokter:</strong> {{ doc.doc_contents['0']['Doctor address'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['Person Responsible']">
                            <strong>Dokter Penanggung Jawab:</strong> {{ doc.doc_contents['0']['Person Responsible'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['Person validated']">
                            <strong>Validator:</strong> {{ doc.doc_contents['0']['Person validated'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['validator signature']">
                            <strong>Tanda Tangan Validator:</strong> {{ doc.doc_contents['0']['validator signature'] }}
                          </div>
                        </div>
                      </div>

                      <div>
                        <h6 class="font-semibold text-yellow-800 dark:text-yellow-300 mb-2">Informasi Pemeriksaan</h6>
                        <div>
                          <div v-if="doc.doc_contents['0']['speciment']">
                            <strong>Tanggal Spesimen:</strong> {{ doc.doc_contents['0']['speciment'] }}
                          </div>
                          <div v-if="doc.doc_contents['0']['Result test']">
                            <strong>Hasil Tes:</strong> {{ doc.doc_contents['0']['Result test'] }}
                          </div>
                          <div v-else>
                            <strong>Hasil Tes:</strong> <span class="text-gray-500 italic">Data hasil tes sedang diproses</span>
                          </div>
                        </div>
                      </div>

                      <!-- Additional Lab Data -->
                      <div v-if="Object.keys(doc.doc_contents['0']).some(key => !['Lab name', 'Lab address', 'Report Date', 'Registration Date', 'No. registration', 'Patient Name', 'Patient Age', 'Patient Gender', 'patient Address', 'Patient address', 'Patient Contact', 'ID Patient in lab', 'Doctor Name', 'Doctor address', 'Person Responsible', 'Person validated', 'validator signature', 'speciment', 'Result test'].includes(key))" class="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
                        <h6 class="font-semibold text-gray-800 dark:text-gray-300 mb-2">Data Tambahan</h6>
                        <div class="space-y-1 text-sm">
                          <div v-for="(value, key) in doc.doc_contents['0']" :key="key">
                            <div v-if="!['Lab name', 'Lab address', 'Report Date', 'Registration Date', 'No. registration', 'Patient Name', 'Patient Age', 'Patient Gender', 'patient Address', 'Patient address', 'Patient Contact', 'ID Patient in lab', 'Doctor Name', 'Doctor address', 'Person Responsible', 'Person validated', 'validator signature', 'speciment', 'Result test'].includes(key) && value && value !== 'None'">
                              <strong>{{ key }}:</strong> {{ value }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Fallback if no data in '0' key -->
                    <div v-else class="text-sm text-gray-600 dark:text-gray-400">
                      <p>Data laboratorium tidak tersedia atau sedang diproses.</p>
                    </div>
                  </div>
                </div>
                
                <div v-else-if="doc.doc_type === 'additional doc' && doc.doc_contents">
                  <h6 class="font-semibold mb-2 text-green-600">Dokumen Tambahan</h6>
                  <div class="space-y-3">
                    <!-- Handle additional document - could be key-value pairs or other structure -->
                    <div v-if="doc.doc_contents.Nama || doc.doc_contents.Umur">
                      <strong class="text-gray-700 dark:text-gray-300">Data Pasien:</strong>
                      <div class="ml-2 mt-1 space-y-1">
                        <div v-if="doc.doc_contents.Nama">
                          <strong>Nama:</strong> {{ doc.doc_contents.Nama }}
                        </div>
                        <div v-if="doc.doc_contents.Umur">
                          <strong>Umur:</strong> {{ doc.doc_contents.Umur }}
                        </div>
                        <div v-if="doc.doc_contents['Jenis Kelamin']">
                          <strong>Jenis Kelamin:</strong> {{ doc.doc_contents['Jenis Kelamin'] }}
                        </div>
                        <div v-if="doc.doc_contents.Pekerjaan">
                          <strong>Pekerjaan:</strong> {{ doc.doc_contents.Pekerjaan }}
                        </div>
                        <div v-if="doc.doc_contents.Alamat">
                          <strong>Alamat:</strong> {{ doc.doc_contents.Alamat }}
                        </div>
                      </div>
                    </div>
                    
                    <!-- Show extracted text content if available -->
                    <div v-if="doc.doc_contents._metadata && doc.doc_contents._metadata.pages">
                      <strong class="text-gray-700 dark:text-gray-300">Isi Dokumen:</strong>
                      <div class="ml-2 mt-1">
                        <div class="text-xs text-gray-600 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 p-2 rounded max-h-32 overflow-y-auto">
                          <div v-for="line in doc.doc_contents._metadata.pages['1'].lines.slice(0, 10)" :key="line">
                            {{ line }}
                          </div>
                          <div v-if="doc.doc_contents._metadata.pages['1'].lines.length > 10" class="text-gray-500 italic">
                            ... dan {{ doc.doc_contents._metadata.pages['1'].lines.length - 10 }} baris lainnya
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Fallback for documents without extracted content -->
                <div v-else>
                  <h6 class="font-semibold mb-2">{{ doc.name }}</h6>
                  <div class="text-sm text-gray-600 dark:text-gray-400">
                    <p>Document content extraction in progress...</p>
                    <p class="mt-2">Document Type: {{ doc.doc_type || 'Unknown' }}</p>
                  </div>
                </div>
              </div>
              
              <div class="mt-3 flex justify-end">
                <button @click="downloadDocument(doc)" class="flex items-center px-3 py-1 text-xs bg-violet-500 text-white rounded hover:bg-violet-600 transition-colors">
                    <svg class="w-3 h-3 mr-2" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                      <path d="M8 12c.3 0 .5-.1.7-.3L14.4 6 13 4.6l-4 4V0H7v8.6l-4-4L1.6 6l5.7 5.7c.2.2.4.3.7.3ZM15 14H1v2h14v-2Z" fill="currentColor"></path>
                    </svg>
                    Download
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Analysis -->
      <div class="mb-6">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 uppercase tracking-wide">AI Analysis</h4>
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-4">
          <div class="flex items-start space-x-3">
            <svg class="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
            <div>
              <h5 class="font-medium text-blue-900 dark:text-blue-100 mb-2">AI Recommendation</h5>
              <p class="text-sm text-blue-800 dark:text-blue-200 mb-1">{{ claim?.aiAnalysis?.recommendation }}</p>
              <!-- <div class="text-xs text-blue-700 dark:text-blue-300">
                <p><strong>Confidence:</strong> {{ claim?.aiAnalysis?.confidence }}%</p>
                <p><strong>Risk Score:</strong> {{ claim?.aiAnalysis?.riskScore }}/10</p>
              </div> -->
            </div>
          </div>
        </div>

        <div class="space-y-3 mb-6">
          <div v-for="detail in claim?.aiAnalysis?.details" :key="detail.category" class="border-l-4 border-gray-300 pl-3">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ detail.category }}</p>
            <p class="text-xs text-gray-600 dark:text-gray-400 text-justify">{{ detail.finding }}</p>
          </div>
        </div>
      </div>

      <!-- Admin Decision -->
      <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3 uppercase tracking-wide">Approver Decision</h4>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Decision Notes</label>
            <textarea v-model="notes" rows="3" class="form-textarea w-full" placeholder="Add your review notes..."></textarea>
          </div>
          <div class="flex space-x-3">
            <button @click="$emit('approve', notes)" class="flex-1 btn bg-green-600 hover:bg-green-700 text-white">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              Approve
            </button>
            <button @click="$emit('reject', notes)" class="flex-1 btn bg-red-600 hover:bg-red-700 text-white">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
              Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'ClaimDetail',
  props: {
    show: Boolean,
    claim: Object
  },
  emits: ['close', 'approve', 'reject', 'download-document'],
  setup(props, { emit }) {
    const notes = ref('')
    const expandedDocs = ref(new Set())

    watch(() => props.show, (newVal) => {
      if (newVal) {
        notes.value = ''
      }
    })

    const toggleDocument = (docId) => {
      if (expandedDocs.value.has(docId)) {
        expandedDocs.value.delete(docId)
      } else {
        expandedDocs.value.add(docId)
      }
    }

    const downloadDocument = async (doc) => {
      try {
        const response = await fetch(doc.url || `/api/documents/${doc.id}`)
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = doc.name
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Download failed:', error)
        alert('Failed to download document')
      }
    }

    const getStatusClass = (status) => {
      const baseClass = 'status-badge '
      switch (status) {
        case 'pengajuan': return baseClass + 'status-pengajuan'
        case 'proses': return baseClass + 'status-proses'
        case 'approved': return baseClass + 'status-approved'
        case 'rejected': return baseClass + 'status-rejected'
        default: return baseClass + 'status-pengajuan'
      }
    }

    const getStatusText = (status) => {
      switch (status) {
        case 'pengajuan': return 'Pengajuan'
        case 'proses': return 'Proses'
        case 'approved': return 'Disetujui'
        case 'rejected': return 'Ditolak'
        default: return status
      }
    }

    const getClaimTypeText = (type) => {
      const typeMap = {
        'rawat-inap': 'Rawat Inap',
        'rawat-jalan': 'Rawat Jalan',
        'pra-pasca-rawat-inap': 'Pra/Pasca Rawat Inap',
        'kehamilan-melahirkan': 'Kehamilan/Melahirkan',
        'santunan-harian': 'Santunan Harian',
        'gigi': 'Gigi',
        'penyakit-kritis': 'Penyakit Kritis',
        'medical-checkup': 'Medical Check-up',
        'lainnya': 'Lainnya'
      }
      return typeMap[type] || 'Lainnya'
    }

    const formatCurrency = (amount) => {
      if (!amount) return ''
      // Handle both string and number inputs
      const numAmount = typeof amount === 'string' ? parseFloat(amount.replace(/[^\d.-]/g, '')) : amount
      return new Intl.NumberFormat('id-ID').format(numAmount)
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('id-ID', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    }

    return {
      notes,
      expandedDocs,
      toggleDocument,
      downloadDocument,
      getStatusClass,
      getStatusText,
      getClaimTypeText,
      formatCurrency,
      formatDate
    }
  }
}
</script>