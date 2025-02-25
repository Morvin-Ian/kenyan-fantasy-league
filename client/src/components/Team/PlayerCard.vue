<template>
    <div
      class="relative w-20 sm:w-22 md:w-24 lg:w-24 xl:w-28 transition-all duration-200"
    >
      <!-- Main Card -->
      <div
        @click="showDetails = !showDetails"
        class="player-card bg-gradient-to-br from-green-700 to-green-900 hover:from-green-600 hover:to-green-800 rounded-lg p-2 sm:p-3 text-center cursor-pointer relative transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1 overflow-hidden"
      >
        <div class="absolute -top-6 -right-6 w-12 h-12 bg-green-500 opacity-10 rounded-full"></div>
        <div class="absolute -bottom-6 -left-6 w-12 h-12 bg-green-500 opacity-10 rounded-full"></div>
        
        <!-- Jersey Image Container -->
        <div class="relative mb-2 flex justify-center items-center">
          <div class="absolute inset-0 bg-green-800 opacity-20 rounded-full"></div>
          <img
            :src="getJerseyImage"
            :alt="`${player.team} jersey`"
            class="w-12 h-15 sm:w-18 sm:h-18 md:w-12 md:h-12 lg:w-16 lg:h-16 object-contain transition-all duration-300 transform hover:scale-105 relative z-10"
          />
          <!-- Captain/Vice-Captain Badge -->
          <div
            v-if="player.isCaptain || player.isViceCaptain"
            class="captain-badge absolute -top-1 -right-1 w-4 h-4 sm:w-5 sm:h-5 bg-yellow-400 rounded-full flex items-center justify-center text-xs font-bold text-black shadow-md border border-yellow-200"
          >
            {{ player.isCaptain ? "C" : "V" }}
          </div>
        </div>
        
        <!-- Divider -->
        <div class="w-full h-px bg-gradient-to-r from-transparent via-green-400 to-transparent opacity-50 my-1"></div>
        
        <!-- Player Name -->
        <p
          class="text-white text-xs sm:text-sm font-medium lg:font-semibold truncate px-1 leading-tight"
        >
          {{ player.name }}
        </p>
        
        <!-- Points with shine effect -->
        <div class="points-container relative mt-1 bg-green-800 bg-opacity-40 rounded-full py-1 px-2">
          <div class="shine-effect"></div>
          <p
            class="text-white text-xs sm:text-sm font-semibold leading-tight"
          >
            {{ player.points }} pts
          </p>
        </div>
        
      </div>
    </div>
  </template>

<script setup>
import { ref, computed } from "vue";
import gor from "../../assets/images/jerseys/gor.png";
import ulinzi from "../../assets/images/jerseys/ulinzi.png";
import afc from "../../assets/images/jerseys/afc.png";
import tusker from "../../assets/images/jerseys/tusker.png";

const showDetails = ref(false);

const props = defineProps({
    player: {
        type: Object,
        required: true,
    },
});

const getJerseyImage = computed(() => {
    const teamImages = {
        GOR: gor,
        ULINZI: ulinzi,
        AFC: afc,
        TUSKER: tusker,
    };
    return teamImages[props.player.team] || gor; // Default to gor if team not found
});
</script>

<style scoped>
/* Progressive enhancement for hover states */
@media (hover: hover) {
    .bg-gradient-to-br:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }
}

/* Smooth transitions for all interactive elements */
.transition-all {
    transition-property: all;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 300ms;
}

/* Enhance the badge with a subtle pulse animation */
@keyframes pulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
    100% {
        transform: scale(1);
    }
}

.bg-yellow-400 {
    animation: pulse 2s infinite;
}
</style>
