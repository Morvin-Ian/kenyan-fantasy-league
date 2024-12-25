<template>
    <div class="relative w-24">
      <!-- Main Card -->
      <div 
        @click="showDetails = !showDetails"
        class="bg-green-900 rounded-lg p-2 text-center cursor-pointer relative"
      >
        <!-- Jersey Image -->
        <div class="relative mb-1">
          <img :src="`${ulinzi}`" :alt="`${player.team} jersey`" class="w-20 h-20 mx-auto" />
          <!-- Captain Badge -->
          <div v-if="player.isCaptain || player.isViceCaptain"
            class="absolute -top-1 -right-1 w-5 h-5 bg-yellow-400 rounded-full flex items-center justify-center text-xs font-bold text-black">
            {{ player.isCaptain ? 'C' : 'V' }}
          </div>
        </div>
        <!-- Player Name -->
        <p class="text-white text-sm font-semibold truncate px-1">{{ player.name }}</p>
        <!-- Points -->
        <p class="text-white text-sm font-semibold mt-1">{{ player.points }}</p>
      </div>
  
      <!-- Details Modal -->
      <div v-if="showDetails" 
        class="absolute z-50 top-full left-1/2 transform -translate-x-1/2 mt-2 w-48 bg-white rounded-lg shadow-lg p-3">
        <div class="flex justify-between items-center mb-2">
          <h3 class="font-semibold text-gray-900">{{ player.name }}</h3>
          <button @click="showDetails = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Form</span>
            <span class="font-medium">{{ player.form || '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Price</span>
            <span class="font-medium">£{{ player.price || '-' }}m</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Next</span>
            <span class="font-medium">{{ player.nextFixture || '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Selected</span>
            <span class="font-medium">{{ player.selectedBy || '-' }}</span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import gor from "../../assets/images/jerseys/gor.png"
  import ulinzi from "../../assets/images/jerseys/ulinzi.png"
  import afc from "../../assets/images/jerseys/afc.png"
  import tusker from "../../assets/images/jerseys/tusker.png"
  
  const showDetails = ref(false)
  
  const props = defineProps({
    player: {
      type: Object,
      required: true,
    }
  })
  </script>