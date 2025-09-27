<template>
  <div class="flex flex-col sm:flex-row justify-between items-center gap-3 mb-4 sm:mb-6 md:mb-8">
    <div class="w-full sm:w-auto">
      <h2 class="text-xl sm:text-2xl md:text-4xl font-black text-gray-600 text-center sm:text-left">
        Fixtures
      </h2>
    </div>
    <div class="w-full sm:w-auto">
      <router-link to="/standings"
        class="w-full sm:w-auto inline-flex items-center justify-center text-gray-700 px-3 sm:px-4 py-2 rounded-full hover:bg-gray-100 transition-colors duration-200 shadow-sm border border-gray-200 text-xs sm:text-sm font-medium">
        View Table
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>