<template>
  <div
    class="w-full lg:w-1/3 bg-gradient-to-br from-white via-blue-50 to-indigo-100 rounded-2xl sm:rounded-3xl shadow-lg sm:shadow-2xl border border-white/50 backdrop-blur-sm transform transition-all duration-500 hover:scale-[1.01] sm:hover:scale-[1.02] hover:shadow-xl sm:hover:shadow-3xl mx-2 sm:mx-0">
    <!-- Header Section with Team Info -->
    <div class="p-3 sm:p-4 lg:p-6 border-b border-blue-100/50">
      <div class="flex items-center justify-between mb-2 sm:mb-4">
        <div class="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
          <div class="min-w-0 flex-1">
            <h2 class="text-lg sm:text-xl lg:text-2xl font-bold text-gray-800 truncate">{{ fantasyStore.userTeam[0].name
            }}</h2>
            <p class="text-xs sm:text-sm text-gray-500">Manager Dashboard</p>
          </div>
        </div>
        <div class="text-right flex-shrink-0">
          <div class="text-xs text-gray-400 uppercase tracking-wide">Gameweek</div>
          <div class="text-sm sm:text-base lg:text-lg font-bold text-indigo-600">{{ fantasyStore.userTeam[0].gameweek }}
          </div>
        </div>
      </div>
    </div>

    <!-- Team Value & Bank -->
    <div
      class="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl sm:rounded-2xl mx-3 sm:mx-4 lg:mx-6 p-3 sm:p-4 mb-4 sm:mb-6 border border-gray-200">
      <div class="flex items-center justify-between mb-2 sm:mb-3">
        <h3 class="text-sm sm:text-base font-semibold text-gray-800 flex items-center">
          Team Value
        </h3>
        <span class="text-sm sm:text-base font-bold text-gray-800">KES {{ team.budget }}m</span>
      </div>
      <div class="space-y-1 sm:space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs sm:text-sm text-gray-600">Balance</span>
         <span class="text-xs sm:text-sm font-semibold text-green-600">
          KES {{ remaining.toFixed(1) }}m
        </span>
      </div>
        <div class="flex items-center justify-between">
          <span class="text-xs sm:text-sm text-gray-600">Formation</span>
          <span class="text-xs sm:text-sm font-semibold text-green-600">{{ team.formation
          }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-xs sm:text-sm text-gray-600">Free Transfers</span>
          <span class="text-xs sm:text-sm font-semibold text-green-600">{{ team.free_transfers
          }}</span>
        </div>
      </div>
    </div>

    <!-- Quick Stats Grid -->
    <div class="p-3 sm:p-4 lg:p-6">
      <div class="grid grid-cols-2 gap-2 sm:gap-3 lg:gap-4 mb-4 sm:mb-6">
        <div
          class="group bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl sm:rounded-2xl p-2 sm:p-3 lg:p-4 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
          <div class="flex items-center justify-between">
            <div class="min-w-0 flex-1">
              <div class="text-blue-100 text-xs uppercase tracking-wide mb-1">Total Points</div>
              <div class="font-bold text-lg sm:text-xl lg:text-2xl truncate">
                {{ team.total_points }}
              </div>
            </div>
            <div
              class="w-6 h-6 sm:w-8 sm:h-8 lg:w-10 lg:h-10 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 ml-2">
              <svg class="w-3 h-3 sm:w-4 sm:h-4 lg:w-5 lg:h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z">
                </path>
              </svg>
            </div>
          </div>
        </div>


        <div
          class="group bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl sm:rounded-2xl p-2 sm:p-3 lg:p-4 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
          <div class="flex items-center justify-between">
            <div class="min-w-0 flex-1">
              <div class="text-orange-100 text-xs uppercase tracking-wide mb-1">Best Week</div>

              <!-- Show best week data if available -->
              <div v-if="team.best_week" class="font-bold text-lg sm:text-xl lg:text-2xl truncate">
                {{ team.best_week }} pts
              </div>

              <!-- Show message if no best week yet -->
              <div v-else class="text-xs sm:text-sm lg:text-base text-orange-100 opacity-90">
                Haven't played yet
              </div>
            </div>
            <div
              class="w-6 h-6 sm:w-8 sm:h-8 lg:w-10 lg:h-10 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 ml-2">
              <svg class="w-3 h-3 sm:w-4 sm:h-4 lg:w-5 lg:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
            </div>
          </div>
        </div>

      </div>

      <!-- Recent Form -->
      <!-- <div class="mb-4 sm:mb-6">
        <h3 class="text-sm sm:text-base font-semibold text-gray-800 mb-2 sm:mb-3 flex items-center">
          Recent Form (Last 5)
        </h3>
        <div class="flex space-x-1 sm:space-x-2">
          <div v-for="(score, index) in recentForm" :key="index"
            class="flex-1 text-center py-1 sm:py-2 rounded-md sm:rounded-lg font-semibold text-xs sm:text-sm transition-all duration-200 hover:scale-105"
            :class="getFormClass(score)">
            {{ score }}
          </div>
        </div>
      </div> -->

      <!-- Action Buttons -->
      <div class="space-y-2 sm:space-y-3">
        <button @click="showTransferPopup = true"
          class="w-full bg-white text-blue-600 font-bold py-2 sm:py-3 px-4 sm:px-6 rounded-lg sm:rounded-xl border-2 border-blue-600 shadow-lg hover:bg-blue-50 transition-all duration-300 transform hover:scale-[1.02] focus:outline-none focus:ring-4 focus:ring-blue-300 flex items-center justify-center space-x-2">
          <span class="text-sm sm:text-base">Transfer/Switch Players</span>
        </button>
      </div>
    </div>

    <!-- Transfer Instructions Popup - IMPROVED RESPONSIVE VERSION -->
    <div v-if="showTransferPopup"
      class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-start sm:items-center justify-center z-50 p-2 sm:p-4 overflow-y-auto"
      @click="showTransferPopup = false">

      <!-- Mobile: Full height container with padding -->
      <div
        class="w-full max-w-sm sm:max-w-md lg:max-w-lg min-h-full sm:min-h-0 flex flex-col sm:block pt-4 sm:pt-0 pb-4 sm:pb-0"
        @click.stop>

        <div
          class="bg-white rounded-xl sm:rounded-2xl shadow-2xl flex-1 sm:flex-initial transform transition-all duration-300 scale-100 overflow-hidden">

          <!-- Popup Header - More compact on mobile -->
          <div class="bg-gradient-to-r from-blue-500 to-blue-600 p-4 sm:p-6 text-white">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
                <div
                  class="w-8 h-8 sm:w-10 sm:h-10 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
                  </svg>
                </div>
                <div class="min-w-0">
                  <h3 class="text-base sm:text-lg font-bold truncate">Make Transfers</h3>
                  <p class="text-blue-100 text-xs sm:text-sm truncate">How to transfer players</p>
                </div>
              </div>
              <button @click="showTransferPopup = false"
                class="w-8 h-8 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center transition-colors duration-200 flex-shrink-0 ml-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- Popup Content - Scrollable on mobile -->
          <div class="p-4 sm:p-6 flex-1 overflow-y-auto">
            <div class="space-y-3 sm:space-y-4">

              <!-- Step 1 - More compact on mobile -->
              <div
                class="flex items-start space-x-3 sm:space-x-4 p-3 sm:p-4 bg-blue-50 rounded-lg sm:rounded-xl border border-blue-200">
                <div
                  class="w-6 h-6 sm:w-8 sm:h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs sm:text-sm font-bold flex-shrink-0">
                  1
                </div>
                <div class="min-w-0 flex-1">
                  <h4 class="font-semibold text-gray-800 mb-1 text-sm sm:text-base">Select Player to Transfer Out</h4>
                  <p class="text-xs sm:text-sm text-gray-600 leading-relaxed">Click on any player card in your squad
                    that you want to replace.</p>
                </div>
              </div>

              <!-- Step 2 -->
              <div
                class="flex items-start space-x-3 sm:space-x-4 p-3 sm:p-4 bg-green-50 rounded-lg sm:rounded-xl border border-green-200">
                <div
                  class="w-6 h-6 sm:w-8 sm:h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-xs sm:text-sm font-bold flex-shrink-0">
                  2
                </div>
                <div class="min-w-0 flex-1">
                  <h4 class="font-semibold text-gray-800 mb-1 text-sm sm:text-base">Click Transfer Button</h4>
                  <p class="text-xs sm:text-sm text-gray-600 leading-relaxed">After selecting a player, click the
                    "Transfer" button that appears on their card.</p>
                </div>
              </div>

              <!-- Step 3 -->
              <div
                class="flex items-start space-x-3 sm:space-x-4 p-3 sm:p-4 bg-purple-50 rounded-lg sm:rounded-xl border border-purple-200">
                <div
                  class="w-6 h-6 sm:w-8 sm:h-8 bg-purple-500 text-white rounded-full flex items-center justify-center text-xs sm:text-sm font-bold flex-shrink-0">
                  3
                </div>
                <div class="min-w-0 flex-1">
                  <h4 class="font-semibold text-gray-800 mb-1 text-sm sm:text-base">Choose Replacement</h4>
                  <p class="text-xs sm:text-sm text-gray-600 leading-relaxed">Browse and select a new player to add to
                    your squad from the available options.</p>
                </div>
              </div>
            </div>

            <!-- Transfer Info - More compact spacing -->
            <div
              class="mt-4 sm:mt-6 p-3 sm:p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg sm:rounded-xl border border-yellow-200">
              <div class="flex items-center space-x-2 mb-2 sm:mb-3">
                <svg class="w-4 h-4 sm:w-5 sm:h-5 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <h4 class="font-semibold text-yellow-800 text-sm sm:text-base">Transfer Information</h4>
              </div>
              <div class="text-xs sm:text-sm text-yellow-700 space-y-1">
                <p>• You have <span class="font-semibold">{{ team.free_transfers }}</span> free
                  transfer(s) this gameweek</p>
                <p>• Additional transfers cost 4 points each</p>
                <p>• Available budget: <span class="font-semibold">KES {{ inBank.toFixed(1) }}m</span></p>
              </div>
            </div>
          </div>

          <!-- Action Button - Sticky bottom on mobile -->
          <div class="p-4 sm:p-6 pt-0 bg-white">
            <button @click="showTransferPopup = false"
              class="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-4 sm:px-6 rounded-lg sm:rounded-xl shadow-lg hover:from-blue-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-[1.02] focus:outline-none focus:ring-4 focus:ring-blue-300 text-sm sm:text-base">
              Got It! Let's Make Transfers
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useFantasyStore } from '@/stores/fantasy';

const fantasyStore = useFantasyStore();
const showTransferPopup = ref(false);

const props = defineProps<{
  totalPoints: number;
  averagePoints: number;
  highestPoints: number;
  overallRank: number | null;
  team: string | null;
  teamValue?: number;
  inBank?: number;
  currentGameweek?: number;
  recentForm?: number[];
}>();

const inBank = computed(() => props.inBank || 0.5);
const recentForm = computed(() => props.recentForm || [65, 78, 45, 89, 56]);

const formatRank = (rank: number | null) => {
  if (!rank) return "No rank";
  if (rank >= 1000000) return `${(rank / 1000000).toFixed(1)}M`;
  if (rank >= 1000) return `${(rank / 1000).toFixed(1)}K`;
  return rank.toString();
};

const getFormClass = (score: number) => {
  if (score >= 80) return 'bg-green-500 text-white shadow-lg';
  if (score >= 60) return 'bg-yellow-500 text-white shadow-lg';
  if (score >= 40) return 'bg-orange-500 text-white shadow-lg';
  return 'bg-red-500 text-white shadow-lg';
};

const team = fantasyStore.userTeam[0]
const budget = Number(team.budget)
const remaining = 70.0 - budget
</script>