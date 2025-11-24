<template>
  <button
    @click="$emit('click')"
    class="group relative w-full py-3.5 px-4 rounded-3xl text-sm font-semibold transition-all duration-300 ease-out
           flex items-center justify-center  disabled:opacity-50 disabled:cursor-not-allowed
           transform hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-4 focus:ring-opacity-50
           shadow-lg hover:shadow-xl backdrop-blur-sm border border-opacity-20"
    :class="buttonClasses"
    :disabled="disabled"
  >
    <div class="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
         :class="gradientOverlay"></div>
    
    <span class="z-10 relative">
      <slot />
    </span>
    
    <div v-if="active" class="absolute inset-0 rounded-xl animate-pulse bg-white bg-opacity-10"></div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  color: string
  icon?: object | string
  active?: boolean
  disabled?: boolean
}>();

const emit = defineEmits<{
  click: []
}>();

const buttonClasses = computed(() => {
  const baseClasses = 'relative overflow-hidden';
  
  if (props.active) {
    return `${baseClasses} bg-gradient-to-r from-gray-50 to-gray-100 text-gray-900 border-gray-300 shadow-inner`;
  }
  
  switch (props.color) {
    case 'blue':
      return `${baseClasses} bg-gradient-to-r from-blue-500 to-blue-600 text-white border-blue-400 
              hover:from-blue-600 hover:to-blue-700 focus:ring-blue-300`;
    case 'green':
      return `${baseClasses} bg-gradient-to-r from-green-500 to-green-600 text-white border-green-400 
              hover:from-green-600 hover:to-green-700 focus:ring-green-300`;
    case 'yellow':
      return `${baseClasses} bg-gradient-to-r from-yellow-500 to-yellow-600 text-white border-yellow-400 
              hover:from-yellow-600 hover:to-yellow-700 focus:ring-yellow-300`;
    case 'purple':
      return `${baseClasses} bg-gradient-to-r from-purple-500 to-purple-600 text-white border-purple-400 
              hover:from-purple-600 hover:to-purple-700 focus:ring-purple-300`;
    case 'red':
      return `${baseClasses} bg-gradient-to-r from-red-500 to-red-600 text-white border-red-400 
              hover:from-red-600 hover:to-red-700 focus:ring-red-300`;
    default:
      return `${baseClasses} bg-gradient-to-r from-gray-500 to-gray-600 text-white border-gray-400 
              hover:from-gray-600 hover:to-gray-700 focus:ring-gray-300`;
  }
});

const gradientOverlay = computed(() => {
  switch (props.color) {
    case 'blue':
      return 'bg-gradient-to-r from-blue-400 to-blue-500';
    case 'green':
      return 'bg-gradient-to-r from-green-400 to-green-500';
    case 'yellow':
      return 'bg-gradient-to-r from-yellow-400 to-yellow-500';
    case 'purple':
      return 'bg-gradient-to-r from-purple-400 to-purple-500';
    case 'red':
      return 'bg-gradient-to-r from-red-400 to-red-500';
    default:
      return 'bg-gradient-to-r from-gray-400 to-gray-500';
  }
});
</script>