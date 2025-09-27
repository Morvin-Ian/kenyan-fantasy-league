<template>
  <div class="flex space-x-1 bg-gray-100 p-1 rounded-lg sm:rounded-xl mb-4 sm:mb-6">
    <button @click="emit('update-tab', 'upcoming')" :class="{
      'bg-white text-gray-900 shadow-sm': activeTab === 'upcoming',
      'text-gray-600 hover:text-gray-900': activeTab !== 'upcoming'
    }" class="flex-1 py-2 px-2 sm:py-2.5 sm:px-4 text-xs sm:text-sm font-medium rounded-md sm:rounded-lg transition-all duration-200">
      <div class="flex items-center justify-center space-x-1 sm:space-x-2">
        <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
        <span class="hidden xs:inline">Upcoming & Live</span>
        <span class="xs:hidden">Upcoming</span>
        <span v-if="upcomingCount > 0"
          class="inline-flex items-center justify-center px-1.5 py-0.5 sm:px-2 sm:py-1 text-xs font-bold leading-none text-white bg-blue-600 rounded-full min-w-[20px]">
          {{ upcomingCount }}
        </span>
      </div>
    </button>

    <button @click="emit('update-tab', 'finished')" :class="{
      'bg-white text-gray-900 shadow-sm': activeTab === 'finished',
      'text-gray-600 hover:text-gray-900': activeTab !== 'finished'
    }" class="flex-1 py-2 px-2 sm:py-2.5 sm:px-4 text-xs sm:text-sm font-medium rounded-md sm:rounded-lg transition-all duration-200">
      <div class="flex items-center justify-center space-x-1 sm:space-x-2">
        <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>Finished</span>
        <span v-if="finishedCount > 0"
          class="inline-flex items-center justify-center px-1.5 py-0.5 sm:px-2 sm:py-1 text-xs font-bold leading-none text-white bg-green-600 rounded-full min-w-[20px]">
          {{ finishedCount }}
        </span>
      </div>
    </button>

    <button @click="emit('update-tab', 'postponed')" :class="{
      'bg-white text-gray-900 shadow-sm': activeTab === 'postponed',
      'text-gray-600 hover:text-gray-900': activeTab !== 'postponed'
    }" class="flex-1 py-2 px-2 sm:py-2.5 sm:px-4 text-xs sm:text-sm font-medium rounded-md sm:rounded-lg transition-all duration-200">
      <div class="flex items-center justify-center space-x-1 sm:space-x-2">
        <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
        </svg>
        <span class="hidden xs:inline">Postponed</span>
        <span class="xs:hidden">Postp.</span>
        <span v-if="postponedCount > 0"
          class="inline-flex items-center justify-center px-1.5 py-0.5 sm:px-2 sm:py-1 text-xs font-bold leading-none text-white bg-orange-600 rounded-full min-w-[20px]">
          {{ postponedCount }}
        </span>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  activeTab: string;
  upcomingCount: number;
  finishedCount: number;
  postponedCount: number;
}>();

const emit = defineEmits<{
  (e: 'update-tab', value: string): void;
}>();
</script>