<template>
  <div class="w-full lg:w-1/3 bg-gradient-to-br from-white via-blue-50 to-indigo-100 rounded-3xl shadow-2xl border border-white/50 backdrop-blur-sm transform transition-all duration-500 hover:scale-[1.02] hover:shadow-3xl">
    <!-- Header Section with Team Info -->
    <div class="p-6 border-b border-blue-100/50">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center space-x-3">
          <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-2xl font-bold text-gray-800">{{ team }}</h2>
            <p class="text-sm text-gray-500">Manager Dashboard</p>
          </div>
        </div>
        <div class="text-right">
          <div class="text-xs text-gray-400 uppercase tracking-wide">Gameweek</div>
          <div class="text-lg font-bold text-indigo-600">{{ currentGameweek }}</div>
        </div>
      </div>
    </div>

    <!-- Quick Stats Grid -->
    <div class="p-6">
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="group bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl p-4 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-blue-100 text-xs uppercase tracking-wide mb-1">Total Points</div>
              <div class="font-bold text-2xl">{{ totalPoints }}</div>
            </div>
            <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
              </svg>
            </div>
          </div>
        </div>

        <div class="group bg-gradient-to-r from-green-500 to-green-600 rounded-2xl p-4 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-green-100 text-xs uppercase tracking-wide mb-1">Average</div>
              <div class="font-bold text-2xl">{{ averagePoints.toFixed(1) }}</div>
            </div>
            <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
          </div>
        </div>

        <div class="group bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl p-4 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-purple-100 text-xs uppercase tracking-wide mb-1">Best Week</div>
              <div class="font-bold text-2xl">{{ highestPoints }}</div>
            </div>
            <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
            </div>
          </div>
        </div>

        <div class="group bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl p-4 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-orange-100 text-xs uppercase tracking-wide mb-1">Rank</div>
              <div class="font-bold text-xl">{{ formatRank(overallRank) }}</div>
            </div>
            <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 4v12l-4-2-4 2V4M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Team Value & Bank -->
      <div class="bg-gradient-to-r from-gray-50 to-gray-100 rounded-2xl p-4 mb-6 border border-gray-200">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-800 flex items-center">
            <svg class="w-5 h-5 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
            </svg>
            Team Value
          </h3>
          <span class="font-bold text-gray-800">£{{ teamValue.toFixed(1) }}m</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-600">In Bank</span>
          <span class="font-semibold text-green-600">£{{ inBank.toFixed(1) }}m</span>
        </div>
      </div>

      <!-- Recent Form -->
      <div class="mb-6">
        <h3 class="font-semibold text-gray-800 mb-3 flex items-center">
          <svg class="w-5 h-5 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          Recent Form (Last 5)
        </h3>
        <div class="flex space-x-2">
          <div v-for="(score, index) in recentForm" :key="index" 
               class="flex-1 text-center py-2 rounded-lg font-semibold text-sm transition-all duration-200 hover:scale-105"
               :class="getFormClass(score)">
            {{ score }}
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="space-y-3">
        <button class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold py-3 px-6 rounded-xl shadow-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-[1.02] focus:outline-none focus:ring-4 focus:ring-blue-300 flex items-center justify-center space-x-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
          </svg>
          <span>View Team</span>
        </button>
        
        <button class="w-full bg-white text-blue-600 font-semibold py-3 px-6 rounded-xl border-2 border-blue-600 shadow-lg hover:bg-blue-50 transition-all duration-300 transform hover:scale-[1.02] focus:outline-none focus:ring-4 focus:ring-blue-300 flex items-center justify-center space-x-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
          </svg>
          <span>Transfers</span>
        </button>

        <button class="w-full bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 font-semibold py-3 px-6 rounded-xl shadow-lg hover:from-gray-200 hover:to-gray-300 transition-all duration-300 transform hover:scale-[1.02] focus:outline-none focus:ring-4 focus:ring-gray-300 flex items-center justify-center space-x-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <span>Statistics</span>
        </button>
      </div>


    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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

// Default values for optional props
const teamValue = computed(() => props.teamValue || 100.0);
const inBank = computed(() => props.inBank || 0.5);
const currentGameweek = computed(() => props.currentGameweek || 1);
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
</script>