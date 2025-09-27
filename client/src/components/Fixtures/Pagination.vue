<template>
  <div class="mt-6 sm:mt-8 flex justify-center items-center space-x-2 sm:space-x-3 md:space-x-4">
    <button @click="emit('prev-page')" :disabled="currentPage === 1"
            class="flex items-center space-x-1 sm:space-x-2 px-3 sm:px-4 py-2 bg-white text-gray-700 rounded-full border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm text-xs sm:text-sm">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5" fill="none" viewBox="0 0 24 24"
           stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      <span class="hidden sm:inline">Previous</span>
    </button>

    <div class="flex items-center space-x-1 sm:space-x-2 text-xs sm:text-sm">
      <span class="text-gray-600 hidden sm:inline">Page</span>
      <span class="bg-gray-600 text-white px-2 py-1 sm:px-3 sm:py-1 rounded-full font-bold">{{ currentPage }}</span>
      <span class="text-gray-600">of</span>
      <span class="text-gray-600 font-medium">{{ totalPages }}</span>
    </div>

    <button @click="emit('next-page')" :disabled="currentPage === totalPages"
            class="flex items-center space-x-1 sm:space-x-2 px-3 sm:px-4 py-2 bg-white text-gray-700 rounded-full border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm text-xs sm:text-sm">
      <span class="hidden sm:inline">Next</span>
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5" fill="none" viewBox="0 0 24 24"
           stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  currentPage: number;
  totalPages: number;
}>();

const emit = defineEmits<{
  (e: 'next-page'): void;
  (e: 'prev-page'): void;
}>();
</script>