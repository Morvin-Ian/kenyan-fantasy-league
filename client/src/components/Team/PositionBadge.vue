<template>
  <span 
    class="px-2 py-1 rounded-md text-xs font-bold uppercase"
    :class="{
      'bg-green-100 text-green-800': position === 'FWD',
      'bg-blue-100 text-blue-800': position === 'MID',
      'bg-purple-100 text-purple-800': position === 'DEF',
      'bg-red-100 text-red-800': position === 'GK'
    }"
  >
    {{ position }}
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{
  position: string  
}>();
</script>