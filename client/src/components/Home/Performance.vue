<template>
  <div class="bg-gradient-to-br from-gray-50 to-blue-50 p-2 sm:p-4 md:p-6 lg:p-8 rounded-xl sm:rounded-2xl mx-1 sm:mx-2 md:mx-4 shadow-lg mb-3">
    <div class="mx-auto">
      <!-- Enhanced Header with Tagline -->
      <div class="animate-fade-in mb-6 sm:mb-8 md:mb-10 mt-3 sm:mt-4 md:mt-6 ml-2 sm:ml-3">
        <h1 class="text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-2 sm:mb-3 md:mb-4">
          Discover Kenya's <span class="text-transparent bg-clip-text bg-gradient-to-r from-gray-700 to-gray-900">Best Talent</span>
        </h1>
        <p class="text-xs sm:text-sm md:text-base text-gray-500 mt-1 sm:mt-1.5 md:mt-2">
          Explore the extraordinary plays and exceptional talents shaping Kenyan football
        </p>
      </div>

      <div class="animate-fade-in grid grid-cols-1 gap-4 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white rounded-xl sm:rounded-2xl shadow-lg border border-gray-100 p-3 sm:p-4 md:p-6">
          <div class="flex justify-between items-center mb-3 sm:mb-4">
            <h3 class="text-base sm:text-lg md:text-xl font-bold text-gray-900">Top Goal Scorers</h3>
            <button 
              @click="fetchTopScorers" 
              :disabled="isLoading"
              class="text-xs sm:text-sm bg-blue-100 text-blue-700 px-2 sm:px-3 py-1 rounded-lg hover:bg-blue-200 transition-colors"
            >
              {{ isLoading ? 'Refreshing...' : 'Refresh' }}
            </button>
          </div>
          
          <!-- Loading State -->
          <div v-if="isLoading" class="space-y-2 sm:space-y-3 md:space-y-4">
            <div v-for="i in 5" :key="i" class="grid grid-cols-8 items-center py-2 sm:py-2.5 md:py-3 border-b border-gray-100 px-1">
              <div class="col-span-1">
                <div class="h-4 w-4 bg-gray-200 rounded animate-pulse"></div>
              </div>
              <div class="col-span-3">
                <div class="h-4 w-20 bg-gray-200 rounded animate-pulse"></div>
              </div>
              <div class="col-span-2">
                <div class="h-4 w-16 bg-gray-200 rounded animate-pulse"></div>
              </div>
              <div class="col-span-1 text-center">
                <div class="h-4 w-6 bg-gray-200 rounded animate-pulse mx-auto"></div>
              </div>
              <div class="col-span-1 text-center">
                <div class="h-4 w-6 bg-gray-200 rounded animate-pulse mx-auto"></div>
              </div>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="text-center py-4">
            <p class="text-red-500 text-sm">{{ error }}</p>
            <button 
              @click="fetchTopScorers"
              class="mt-2 text-xs bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200 transition-colors"
            >
              Try Again
            </button>
          </div>

          <!-- Data State -->
          <div v-else class="space-y-2 sm:space-y-3 md:space-y-4">
            <!-- Header Row -->
            <div class="grid grid-cols-8 text-xs sm:text-sm font-medium text-gray-600 mb-1 sm:mb-2 px-1">
              <div class="col-span-1">#</div>
              <div class="col-span-3">Player</div>
              <div class="col-span-2">Team</div>
              <div class="col-span-1 text-center">Apps</div>
              <div class="col-span-1 text-center">Goals</div>
            </div>
            
            <!-- Player Rows -->
            <div 
              v-for="(player, index) in topScorers" 
              :key="player.player_id"
              class="grid grid-cols-8 items-center py-2 sm:py-2.5 md:py-3 border-b border-gray-100 px-1 hover:bg-gray-50 transition-colors"
            >
              <div class="col-span-1 font-bold text-xs sm:text-sm md:text-base text-gray-700">
                {{ index + 1 }}
              </div>
              <div class="col-span-3 flex items-center">
                <span class="text-xs sm:text-sm md:text-base font-medium text-gray-900 truncate">
                  {{ player.player_name }}
                </span>
              </div>
              <div class="col-span-2 flex items-center">
                <span class="text-xs sm:text-sm text-gray-600 truncate">
                  {{ player.team_name || 'No Team' }}
                </span>
              </div>
              <div class="col-span-1 text-center text-xs sm:text-sm md:text-base text-gray-600">
                {{ player.total_appearances || 0 }}
              </div>
              <div class="col-span-1 text-center font-bold text-gray-900 text-xs sm:text-sm md:text-base">
                {{ player.total_goals || 0 }}
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="topScorers.length === 0" class="text-center py-6">
              <p class="text-gray-500 text-sm">No goal scorers data available</p>
            </div>
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

onMounted(() => {
  // Only fetch if we don't have data yet
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
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}

@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.animate-slide-up {
  animation: slide-up 0.5s ease-out;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
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