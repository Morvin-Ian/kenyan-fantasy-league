<template>
  <div :class="alertClasses">
    <div class="flex items-start">
      <svg
        :class="iconColor"
        class="h-5 w-5 mr-3 mt-0.5 flex-shrink-0"
        xmlns="http://www.w3.org/2000/svg" fill="none"
        viewBox="0 0 24 24" stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPath" />
      </svg>
      <div class="flex-1">
        <p class="text-sm font-medium leading-5">{{ text }}</p>
      </div>
    </div>
    <button
      v-if="dismissible"
      @click="handleDismiss"
      :class="iconColor"
      class="ml-4 inline-flex flex-shrink-0 hover:opacity-75 transition-opacity focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current rounded"
    >
      <span class="sr-only">Dismiss</span>
      <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" 
           viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>
<script setup>
import { computed, onMounted } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['error', 'success', 'warning', 'info'].includes(value)
  },
  text: {
    type: String,
    required: true
  },
  dismissible: {
    type: Boolean,
    default: true
  },
  autoDismiss: {
    type: Number,
    default: 0 // 0 means no auto dismiss, otherwise milliseconds
  }
})

const emit = defineEmits(['dismiss'])

// Auto dismiss
onMounted(() => {
  if (props.autoDismiss > 0) {
    setTimeout(() => {
      emit('dismiss')
    }, props.autoDismiss)
  }
})

// Computed classes
const alertClasses = computed(() => {
  const baseClasses = 'animate-fade-in p-4 rounded-lg shadow-sm border-l-4 flex items-start justify-between transition-all duration-300'
  const typeClasses = {
    error: 'bg-red-50 border-red-500 text-red-800',
    success: 'bg-green-50 border-green-500 text-green-800',
    warning: 'bg-yellow-50 border-yellow-500 text-yellow-800',
    info: 'bg-blue-50 border-blue-500 text-blue-800'
  }
  return `${baseClasses} ${typeClasses[props.type]}`
})

const iconPath = computed(() => {
  const icons = {
    error: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
    success: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    warning: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z',
    info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
  }
  return icons[props.type]
})

const iconColor = computed(() => {
  const colors = {
    error: 'text-red-500',
    success: 'text-green-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500'
  }
  return colors[props.type]
})

const handleDismiss = () => {
  emit('dismiss')
}
</script>


