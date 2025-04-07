<template>
    <button
      @click="$emit('click')"
      class="w-full py-3 rounded-lg text-sm font-semibold transition-all duration-300 
            flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      :class="{
        'bg-blue-500 text-white hover:bg-blue-600': color === 'blue',
        'bg-green-500 text-white hover:bg-green-600': color === 'green',
        'bg-yellow-500 text-white hover:bg-yellow-600': color === 'yellow',
        'bg-gray-100 text-gray-800 border border-gray-300': active
      }"
      :disabled="disabled"
    >
      <component :is="icon" class="h-5 w-5" />
      <slot />
    </button>
  </template>
  
  <script setup lang="ts">
  const props = defineProps<{
    color: string
    icon?: object | string 
    active?: boolean       
    disabled?: boolean     
  }>();
  </script>