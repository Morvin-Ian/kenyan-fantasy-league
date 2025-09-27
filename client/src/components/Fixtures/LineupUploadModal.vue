<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="closeModal"></div>

      <!-- Modal panel -->
      <div class="inline-block w-full max-w-md p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium leading-6 text-gray-900">
            Upload Lineup CSV
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Team Selection -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Select Team</label>
          <div class="space-y-2">
            <label class="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50" :class="{'bg-blue-50 border-blue-300': selectedTeam === 'home'}">
              <input type="radio" v-model="selectedTeam" value="home" class="text-blue-600 focus:ring-blue-500">
              <img :src="fixture.home_team.logo_url" :alt="fixture.home_team.name" class="w-8 h-8 rounded-full">
              <span class="font-medium text-gray-900">{{ fixture.home_team.name }}</span>
            </label>
            <label class="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50" :class="{'bg-blue-50 border-blue-300': selectedTeam === 'away'}">
              <input type="radio" v-model="selectedTeam" value="away" class="text-blue-600 focus:ring-blue-500">
              <img :src="fixture.away_team.logo_url" :alt="fixture.away_team.name" class="w-8 h-8 rounded-full">
              <span class="font-medium text-gray-900">{{ fixture.away_team.name }}</span>
            </label>
          </div>
        </div>

        <!-- File Upload -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">CSV File</label>
          <div class="flex items-center justify-center w-full">
            <label class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer hover:bg-gray-50 border-gray-300 hover:border-gray-400 transition-colors" :class="{'border-blue-300 bg-blue-50': isDragging}">
              <div class="flex flex-col items-center justify-center pt-5 pb-6">
                <svg class="w-8 h-8 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="mb-2 text-sm text-gray-500">
                  <span class="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p class="text-xs text-gray-500">CSV only (MAX. 10MB)</p>
              </div>
              <input 
                type="file" 
                ref="fileInput"
                accept=".csv" 
                class="hidden" 
                @change="handleFileSelect"
                @dragenter="isDragging = true"
                @dragleave="isDragging = false"
                @drop="handleDrop"
              >
            </label>
          </div>
          
          <!-- Selected file info -->
          <div v-if="selectedFile" class="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm font-medium text-green-800">{{ selectedFile.name }}</span>
              </div>
              <button @click="removeFile" class="text-green-600 hover:text-green-800">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p class="text-xs text-green-600 mt-1">Size: {{ (selectedFile.size / 1024).toFixed(2) }} KB</p>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center space-x-2">
            <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-sm font-medium text-red-800">{{ error }}</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex space-x-3">
          <button 
            @click="closeModal" 
            class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="uploadLineup" 
            :disabled="!selectedFile || !selectedTeam || isUploading"
            :class="{
              'opacity-50 cursor-not-allowed': !selectedFile || !selectedTeam || isUploading,
              'hover:bg-blue-600 focus:ring-blue-500': selectedFile && selectedTeam && !isUploading
            }"
            class="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-500 border border-transparent rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors"
          >
            <span v-if="isUploading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Uploading...
            </span>
            <span v-else>Upload Lineup</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useKplStore } from '@/stores/kpl'

interface Props {
  isOpen: boolean
  fixture: any
}

interface Emits {
  (e: 'close'): void
  (e: 'upload-success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const kplStore = useKplStore()

const selectedTeam = ref<'home' | 'away' | null>(null)
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const error = ref('')
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement>()

const closeModal = () => {
  resetModal()
  emit('close')
}

const resetModal = () => {
  selectedTeam.value = null
  selectedFile.value = null
  error.value = ''
  isUploading.value = false
  isDragging.value = false
}

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    validateAndSetFile(file)
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = false
  
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    const file = event.dataTransfer.files[0]
    validateAndSetFile(file)
  }
}

const validateAndSetFile = (file: File) => {
  if (!file.name.toLowerCase().endsWith('.csv')) {
    error.value = 'Please select a CSV file'
    return
  }
  
  if (file.size > 10 * 1024 * 1024) { // 10MB limit
    error.value = 'File size must be less than 10MB'
    return
  }
  
  selectedFile.value = file
  error.value = ''
}

const removeFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const uploadLineup = async () => {
  if (!selectedFile.value || !selectedTeam.value) return
  
  isUploading.value = true
  error.value = ''
  
  try {
    const teamId = selectedTeam.value === 'home' 
      ? props.fixture.home_team.id 
      : props.fixture.away_team.id
    
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('fixture_id', props.fixture.id)
    formData.append('team_id', teamId)
    formData.append('side', selectedTeam.value)
    
    await kplStore.uploadLineupCsv(formData)
    
    emit('upload-success')
    closeModal()
    
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to upload lineup. Please try again.'
    console.error('Upload error:', err)
  } finally {
    isUploading.value = false
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    resetModal()
  }
})
</script>