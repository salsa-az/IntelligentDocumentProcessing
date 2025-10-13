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
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Annual Claim Limit</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">Rp {{ formatCurrency(policyLimit) }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span class="text-sm text-gray-500 dark:text-gray-400">Claims Used ({{ currentYear }})</span>
            <span class="text-sm font-medium" :class="usagePercentage > 80 ? 'text-red-600' : usagePercentage > 60 ? 'text-yellow-600' : 'text-green-600'">Rp {{ formatCurrency(totalUsedAmount) }} ({{ usagePercentage }}%)</span>
          </div>
          <div class="flex justify-between py-2">
            <span class="text-sm text-gray-500 dark:text-gray-400">Remaining Limit</span>
            <span class="text-sm font-medium" :class="remainingLimit < claim?.amount ? 'text-red-600' : 'text-green-600'">Rp {{ formatCurrency(remainingLimit) }}</span>
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
                        • {{ item.Description || 'Deskripsi tidak tersedia' }} [{{ formattedInt(item.Quantity || 0) }}] : <em>Rp {{ formatCurrency(item.Amount || 0) }}</em>
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
                    <!-- Lab Information -->
                    <div v-if="doc.doc_contents['Lab name']">
                      <h6 class="font-semibold text-purple-800 dark:text-purple-300 mb-2">Informasi Laboratorium</h6>
                      <div class="text-xs space-y-1">
                        <div v-if="doc.doc_contents['Lab name']">
                          <strong>Nama Lab:</strong> {{ doc.doc_contents['Lab name'] }}
                        </div>
                        <div v-if="doc.doc_contents['Lab address']">
                          <strong>Alamat Lab:</strong> {{ doc.doc_contents['Lab address'] }}
                        </div>
                        <div v-if="doc.doc_contents['Report Date']">
                          <strong>Tanggal Laporan:</strong> {{ doc.doc_contents['Report Date'] }}
                        </div>
                        <div v-if="doc.doc_contents['Registration Date']">
                          <strong>Tanggal Registrasi:</strong> {{ doc.doc_contents['Registration Date'] }}
                        </div>
                      </div>
                    </div>

                    <!-- Patient Information -->
                    <div v-if="doc.doc_contents['Patient Name']">
                      <h6 class="font-semibold text-blue-800 dark:text-blue-300 mb-2">Informasi Pasien</h6>
                      <div class="text-xs space-y-1">
                        <div v-if="doc.doc_contents['Patient Name']">
                          <strong>Nama Pasien:</strong> {{ doc.doc_contents['Patient Name'] }}
                        </div>
                        <div v-if="doc.doc_contents['Patient Age']">
                          <strong>Umur:</strong> {{ doc.doc_contents['Patient Age'] }}
                        </div>
                        <div v-if="doc.doc_contents['Patient Gender']">
                          <strong>Jenis Kelamin:</strong> {{ doc.doc_contents['Patient Gender'] }}
                        </div>
                        <div v-if="doc.doc_contents['patient Address']">
                          <strong>Alamat:</strong> {{ doc.doc_contents['patient Address'] }}
                        </div>
                        <div v-if="doc.doc_contents['Patient Contact']">
                          <strong>Kontak:</strong> {{ doc.doc_contents['Patient Contact'] }}
                        </div>
                      </div>
                    </div>

                    <!-- Result Test Table -->
                    <div v-if="doc.doc_contents['Result test'] && Array.isArray(doc.doc_contents['Result test'])">
                      <h6 class="font-semibold text-green-800 dark:text-green-300 mb-2">Hasil Pemeriksaan</h6>
                      <div class="overflow-x-auto">
                        <table class="min-w-full text-xs border border-gray-300 dark:border-gray-600">
                          <thead class="bg-gray-100 dark:bg-gray-700">
                            <tr>
                              <th class="border border-gray-300 dark:border-gray-600 px-2 py-1 text-left">Jenis Pemeriksaan</th>
                              <th class="border border-gray-300 dark:border-gray-600 px-2 py-1 text-left">Hasil</th>
                              <th class="border border-gray-300 dark:border-gray-600 px-2 py-1 text-left">Nilai Rujukan</th>
                              <th class="border border-gray-300 dark:border-gray-600 px-2 py-1 text-left">Satuan</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(test, index) in doc.doc_contents['Result test']" :key="index" 
                                :class="test['HASIL'] && test['HASIL'] !== 'None' && test['HASIL'].includes('*') ? 'bg-yellow-50 dark:bg-yellow-900/20' : ''">
                              <td class="border border-gray-300 dark:border-gray-600 px-2 py-1">{{ test['JENIS PEMERIKSAAN'] || '-' }}</td>
                              <td class="border border-gray-300 dark:border-gray-600 px-2 py-1 font-medium" 
                                  :class="test['HASIL'] && test['HASIL'].includes('*') ? 'text-red-600 dark:text-red-400' : ''">
                                {{ test['HASIL'] && test['HASIL'] !== 'None' ? test['HASIL'] : '-' }}
                              </td>
                              <td class="border border-gray-300 dark:border-gray-600 px-2 py-1">{{ test['NILAI RUJUKAN'] && test['NILAI RUJUKAN'] !== 'None' ? test['NILAI RUJUKAN'] : '-' }}</td>
                              <td class="border border-gray-300 dark:border-gray-600 px-2 py-1">{{ test['SATUAN'] && test['SATUAN'] !== 'None' ? test['SATUAN'] : '-' }}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>

                    <!-- Additional Information -->
                    <div v-if="doc.doc_contents['Person Responsible'] || doc.doc_contents['speciment']">
                      <h6 class="font-semibold text-gray-800 dark:text-gray-300 mb-2">Informasi Tambahan</h6>
                      <div class="text-xs space-y-1">
                        <div v-if="doc.doc_contents['Person Responsible']">
                          <strong>Dokter Penanggung Jawab:</strong> {{ doc.doc_contents['Person Responsible'] }}
                        </div>
                        <div v-if="doc.doc_contents['Person validated']">
                          <strong>Validator:</strong> {{ doc.doc_contents['Person validated'] }}
                        </div>
                        <div v-if="doc.doc_contents['speciment']">
                          <strong>Spesimen:</strong> {{ doc.doc_contents['speciment'] }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-else-if="doc.doc_type === 'additional document' && doc.doc_contents?.fields">
                  <h6 class="font-semibold mb-2 text-gray-900 dark:text-gray-100">Dokumen Tambahan</h6>
                  <div class="space-y-2">
                    <div v-for="(value, key) in doc.doc_contents.fields" :key="key" class="text-sm text-gray-700 dark:text-gray-300">
                      <div v-if="value && value !== 'None' && value !== ''">
                        <strong class="text-gray-900 dark:text-gray-100">{{ key }}:</strong> 
                        <span class="ml-1">{{ value }}</span>
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
                <button @click="openRawDocument(doc.id)" class="flex items-center px-3 py-1 text-xs bg-violet-500 text-white rounded hover:bg-violet-600 transition-colors">
                    <svg class="w-3 h-3 mr-2" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                      <path d="M14.5 2h-13C.7 2 0 2.7 0 3.5v9c0 .8.7 1.5 1.5 1.5h13c.8 0 1.5-.7 1.5-1.5v-9c0-.8-.7-1.5-1.5-1.5zM2 4h12v1H2V4zm0 3h8v1H2V7zm0 3h10v1H2v-1z" fill="currentColor"></path>
                    </svg>
                    Raw Document
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Claim Limit Warning -->
      <div v-if="claim?.rawData?.exceeds_limit" class="mb-6">
        <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div class="flex items-start space-x-3">
            <svg class="w-5 h-5 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
            <div>
              <h5 class="font-medium text-red-900 dark:text-red-100 mb-2">⚠️ Claim Limit Exceeded</h5>
              <div class="text-sm text-red-800 dark:text-red-200 space-y-1">
                <p><strong>Policy Limit:</strong> Rp {{ formatCurrency(claim.rawData.limit_info?.policy_limit) }}</p>
                <p><strong>Already Used:</strong> Rp {{ formatCurrency(claim.rawData.limit_info?.total_used) }}</p>
                <p><strong>Current Claim:</strong> Rp {{ formatCurrency(claim.rawData.limit_info?.current_claim) }}</p>
                <p><strong>Would Exceed By:</strong> Rp {{ formatCurrency(claim.rawData.limit_info?.would_exceed_by) }}</p>
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
        
        <!-- Show if already processed -->
        <div v-if="claim?.status === 'approved' || claim?.status === 'rejected'" class="mb-4 p-3 rounded-lg" :class="claim?.status === 'approved' ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'">
          <p class="text-sm font-medium" :class="claim?.status === 'approved' ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'">
            {{ claim?.status === 'approved' ? 'Claim Approved' : 'Claim Rejected' }}
          </p>
          <p class="text-xs mt-1" :class="claim?.status === 'approved' ? 'text-green-600 dark:text-green-300' : 'text-red-600 dark:text-red-300'">
            Previous decision notes: {{ claim?.rawData?.admin_notes || 'No notes provided' }}
          </p>
        </div>
        
        <!-- Show decision buttons only for pending claims or resubmitted claims -->
        <div v-if="claim?.status === 'proses' || claim?.rawData?.resubmitted" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Decision Notes</label>
            <textarea v-model="notes" rows="3" class="form-textarea w-full" placeholder="Add your review notes..."></textarea>
          </div>
          <div class="flex space-x-3">
            <div v-if="decisionMade" class="flex-1 btn bg-blue-600 text-white cursor-not-allowed">
              <svg class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              Processing...
            </div>
            <template v-else>
              <button @click="handleApprove" :disabled="!isApproveMatchesAI && !notes.trim()" class="flex-1 btn bg-green-600 hover:bg-green-700 text-white disabled:opacity-50">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Approve
              </button>
              <button @click="handleReject" :disabled="!isRejectMatchesAI && !notes.trim()" class="flex-1 btn bg-red-600 hover:bg-red-700 text-white disabled:opacity-50">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
                Reject
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>
    <!-- Add DocumentReview component -->
    <DocumentReview
      v-if="showRawDocument"
      :docId="selectedDocId"
      :show="showRawDocument"
      @close="closeRawDocument"
    />
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'
import { formatValue } from '../utils/Utils'
import DocumentReview from './DocumentReview.vue'

export default {
  name: 'ClaimDetail',
  components: {
    DocumentReview
  },
  props: {
    show: Boolean,
    claim: Object
  },
  emits: ['close', 'approve', 'reject'],
  setup(props, { emit }) {
    const notes = ref('')
    const expandedDocs = ref(new Set())
    const showRawDocument = ref(false)
    const selectedDocId = ref(null)
    const decisionMade = ref(false)
    const policyLimit = ref(0)
    const totalUsedAmount = ref(0)
    const currentYear = new Date().getFullYear()

    const openRawDocument = (docId) => {
      selectedDocId.value = docId
      showRawDocument.value = true
    }

    const closeRawDocument = () => {
      showRawDocument.value = false
      selectedDocId.value = null
    }

    watch(() => props.show, async (newVal) => {
      if (newVal && props.claim) {
        notes.value = ''
        decisionMade.value = false
        await fetchPolicyLimits()
      }
    })

    const fetchPolicyLimits = async () => {
      try {
        const response = await fetch(`/api/customer/${props.claim.customer_id}/policy-limits`, {
          credentials: 'include'
        })
        const data = await response.json()
        if (data.status === 'success') {
          policyLimit.value = data.policy_limit
          totalUsedAmount.value = data.total_used
        }
      } catch (error) {
        console.error('Error fetching policy limits:', error)
      }
    }

    const usagePercentage = computed(() => {
      if (policyLimit.value === 0) return 0
      return Math.round((totalUsedAmount.value / policyLimit.value) * 100)
    })

    const remainingLimit = computed(() => {
      return Math.max(0, policyLimit.value - totalUsedAmount.value)
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
        const response = await fetch(`/api/documents/${doc.doc_id}/download`)
        const result = await response.json()
        
        if (result.status === 'success') {
          const link = document.createElement('a')
          link.href = result.download_url
          link.download = result.filename
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        } else {
          alert('Failed to download document: ' + result.error)
        }
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

    const formattedInt = (value) => {
      if (!value) return '0'
      // Handle both string and number inputs, extract number and format as integer
      const numValue = typeof value === 'string' ? parseFloat(value.replace(/[^\d.-]/g, '')) : value
      return Math.floor(numValue).toString()
    }

    const isApproveMatchesAI = computed(() => {
      const rec = props.claim?.aiAnalysis?.recommendation?.toLowerCase()
      return rec?.includes('approve') || rec?.includes('setuju')
    })

    const isRejectMatchesAI = computed(() => {
      const rec = props.claim?.aiAnalysis?.recommendation?.toLowerCase()
      return rec?.includes('reject') || rec?.includes('tolak')
    })

    const handleApprove = () => {
      if (decisionMade.value) return
      if (!isApproveMatchesAI.value && !notes.value.trim()) return
      
      decisionMade.value = true
      emit('approve', notes.value || '')
    }

    const handleReject = () => {
      if (decisionMade.value) return
      if (!isRejectMatchesAI.value && !notes.value.trim()) return
      
      decisionMade.value = true
      emit('reject', notes.value || '')
    }

    return {
      notes,
      expandedDocs,
      toggleDocument,
      getStatusClass,
      getStatusText,
      getClaimTypeText,
      formatCurrency,
      formatDate,
      formattedInt,
      showRawDocument,
      selectedDocId,
      openRawDocument,
      closeRawDocument,
      isApproveMatchesAI,
      isRejectMatchesAI,
      handleApprove,
      handleReject,
      decisionMade,
      policyLimit,
      totalUsedAmount,
      currentYear,
      usagePercentage,
      remainingLimit
    }
  }
}
</script>