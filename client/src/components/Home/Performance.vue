<template>
  <div
    class="bg-gradient-to-br from-gray-50 to-blue-50 p-3 sm:p-4 md:p-6 lg:p-8 rounded-xl sm:rounded-2xl mx-1 sm:mx-2 md:mx-4 shadow-lg mb-3 w-full">
    
    <div class="w-full">
      
      <div class="animate-fade-in mb-6 sm:mb-8 ml-2">
        <h1 class="text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight">
          Discover Kenya's 
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-gray-700 to-gray-900">
            Best Talent
          </span>
        </h1>

        <p class="text-xs sm:text-sm md:text-base text-gray-500 mt-2">
          Explore the extraordinary plays and exceptional talents shaping Kenyan football.
        </p>
      </div>

      <div class="animate-fade-in bg-white rounded-xl sm:rounded-2xl shadow-lg border border-gray-100 p-4 sm:p-6 w-full">
        
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base sm:text-lg md:text-xl font-bold text-gray-900">
            Top Goal Scorers
          </h3>

          <button 
            @click="fetchTopScorers" 
            :disabled="isLoading"
            class="text-xs sm:text-sm bg-blue-100 text-blue-700 px-3 py-1.5 rounded-lg 
                   hover:bg-blue-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
            {{ isLoading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="isLoading" class="space-y-3">
          <div v-for="i in 5" :key="i"
            class="grid grid-cols-8 items-center py-2 sm:py-3 border-b border-gray-100">
            
            <div class="col-span-1"><div class="h-4 w-5 bg-gray-200 rounded animate-pulse"></div></div>
            <div class="col-span-3"><div class="h-4 w-24 bg-gray-200 rounded animate-pulse"></div></div>
            <div class="col-span-2"><div class="h-4 w-20 bg-gray-200 rounded animate-pulse"></div></div>
            <div class="col-span-1 text-center"><div class="h-4 w-6 bg-gray-200 rounded mx-auto animate-pulse"></div></div>
          </div>
        </div>

        <div v-else class="space-y-2">
          
          <div class="grid grid-cols-8 text-xs sm:text-sm font-medium text-gray-600 mb-2">
            <div class="col-span-1">#</div>
            <div class="col-span-3">Player</div>
            <div class="col-span-2">Team</div>
            <div class="col-span-1 text-center">Goals</div>
          </div>

          <div
            v-for="(player, index) in topScorers"
            :key="player.player_id"
            class="grid grid-cols-8 items-center py-3 border-b border-gray-100 hover:bg-gray-50 transition-all rounded-lg"
          >
            <div class="col-span-1 font-semibold text-gray-700 text-sm">{{ index + 1 }}</div>
            
            <div class="col-span-3">
              <span class="text-sm font-medium text-gray-900 truncate">
                {{ formatName(player.player_name) }}
              </span>
            </div>

            <div class="col-span-2">
              <span class="text-sm text-gray-600 truncate">
                {{ player.team_name || 'No Team' }}
              </span>
            </div>

            <div class="col-span-1 text-center font-bold text-gray-900 text-sm">
              {{ player.total_goals || 0 }}
            </div>
          </div>

          <div v-if="topScorers.length === 0" class="text-center py-6">
            <p class="text-gray-500 text-sm">No goal scorers data available</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>


<script setup>
import { useFantasyStore } from '@/stores/fantasy';
import { storeToRefs } from 'pinia';
import { onMounted } from 'vue';

const fantasyStore = useFantasyStore();
const { goalsLeaderboard: topScorers, isLoading, error } = storeToRefs(fantasyStore);

const fetchTopScorers = () => {
  fantasyStore.fetchTopGoalsScorers(5);
};

const formatName = (name) => {
  if (!name) return "";
  return name
    .trim()
    .replace(/\s+/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());
};

onMounted(() => {
  if (topScorers.value.length === 0) {
    fetchTopScorers();
  }
});
</script>

<style scoped>
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

@keyframes fade-in {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}

@keyframes slide-up {
  from {
    transform: translateY(20px);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-up {
  animation: slide-up 0.5s ease-out;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 0.5;
  }

  50% {
    opacity: 1;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Additional responsive utilities for very small screens */
@media (max-width: 320px) {
  .truncate {
    max-width: 80px;
  }
}

@media (min-width: 321px) and (max-width: 640px) {
  .truncate {
    max-width: 120px;
  }
}
</style>