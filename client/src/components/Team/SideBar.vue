<template>
  <div
    class="w-full lg:w-1/3 bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.02]">
    <!-- Team Stats Section -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3 text-blue-600" fill="none" viewBox="0 0 24 24"
          stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
        </svg>
        <h2 class="text-2xl font-bold text-gray-800">Team Performance</h2>
      </div>

      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-blue-50 rounded-lg p-4 shadow-inner">
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Total Points</span>
              <span class="font-bold text-blue-600 text-lg">{{ totalPoints }}</span>
            </div>
          </div>
          <div class="bg-blue-50 rounded-lg p-4 shadow-inner">
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Average Points</span>
              <span class="font-bold text-blue-600 text-lg">{{ averagePoints.toFixed(1) }}</span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="bg-blue-50 rounded-lg p-4 shadow-inner">
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Highest Score</span>
              <span class="font-bold text-blue-600 text-lg">{{ highestPoints }}</span>
            </div>
          </div>
          <div class="bg-blue-50 rounded-lg p-4 shadow-inner">
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Overall Rank</span>
              <span class="font-bold text-blue-600 text-lg">{{ overallRank }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upcoming Fixtures Section -->
    <div class="mb-8">
      <div class="flex items-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3 text-green-600" fill="none" viewBox="0 0 24 24"
          stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <h2 class="text-2xl font-bold text-gray-800">Upcoming Fixtures</h2>
      </div>
      <div class="space-y-2">
        <div v-for="(fixture, index) in upcomingFixtures.slice(0, 3)" :key="index"
          class="bg-green-50 rounded-lg p-3 flex justify-between items-center hover:bg-green-100 transition-colors">
          <span class="text-gray-700">{{ fixture.home_team.name }} vs {{ fixture.away_team.name }}</span>
          <span class="text-gray-500">{{ formatDate(fixture.match_date ?? fixture.datetime) }}</span>

        </div>
        <div v-if="upcomingFixtures.length === 0" class="text-gray-500 text-center">
          No upcoming fixtures
        </div>
      </div>
    </div>

    <!-- Top Performers Section -->
    <div>
      <div class="flex items-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3 text-yellow-600" fill="none" viewBox="0 0 24 24"
          stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
        <h2 class="text-2xl font-bold text-gray-800">Top Performers</h2>
      </div>
      <div class="space-y-2">
        <div v-for="(performer, index) in topPerformers.slice(0, 3)" :key="index"
          class="bg-yellow-50 rounded-lg p-3 flex justify-between items-center hover:bg-yellow-100 transition-colors">
          <span class="text-gray-700">{{ performer.name }}</span>
          <span class="text-gray-500">{{ performer.points }} pts</span>
        </div>
        <div v-if="topPerformers.length === 0" class="text-gray-500 text-center">
          No top performers yet
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Fixture, Result, Performer } from "@/helpers/types/team";

const props = defineProps<{
  totalPoints: Number;
  averagePoints: Number;
  highestPoints: Number;
  overallRank: Number;
  upcomingFixtures: Fixture[];
  recentResults: Result[];
  topPerformers: Performer[];
}>();

const formatDate = (dateStr?: string) => {
  if (!dateStr) return "TBD";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  }).format(date);
};

</script>

<style scoped>
.hover\:scale-\[1\.02\]:hover {
  transform: scale(1.02);
}
</style>