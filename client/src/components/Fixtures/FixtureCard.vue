<template>
  <div
    class="p-3 sm:p-4 md:p-5 shadow-sm hover:shadow-md transition-all duration-200 border rounded-lg"
    :class="{
      'bg-white border-gray-100 hover:border-gray-200': match.status !== 'live' && match.status !== 'postponed',
      'bg-red-50': match.status === 'live',
      'bg-orange-50 border-orange-200 hover:border-orange-300': match.status === 'postponed'
    }"
  >
    <!-- Match Header -->
    <div class="text-center mb-3 sm:mb-4">
      <div class="flex flex-wrap items-center justify-center gap-2 mb-2">
        <div
          class="inline-flex items-center px-2 py-1 sm:px-3 sm:py-1.5 rounded-full text-xs sm:text-sm font-medium"
          :class="{
            'bg-red-100 text-red-700': match.status === 'live',
            'bg-orange-100 text-orange-700': match.status === 'postponed',
            'bg-gray-50 text-gray-700': match.status !== 'live' && match.status !== 'postponed'
          }"
        >
          <svg
            v-if="match.status === 'live'"
            class="w-3 h-3 sm:w-4 sm:h-4 mr-1 animate-pulse"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <circle cx="12" cy="12" r="8" />
          </svg>
          <svg
            v-else-if="match.status === 'postponed'"
            class="w-3 h-3 sm:w-4 sm:h-4 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
            ></path>
          </svg>
          <svg
            v-else
            class="w-3 h-3 sm:w-4 sm:h-4 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            ></path>
          </svg>
          {{ match.status === 'live' ? 'LIVE' : match.status === 'postponed' ? 'POSTPONED' : 'UPCOMING' }}
        </div>

        <div
          v-if="match.status !== 'live'"
          class="inline-flex items-center bg-gray-50 text-gray-700 px-2 py-1 sm:px-3 sm:py-1.5 rounded-full text-xs sm:text-sm font-medium"
        >
          {{ formatDatePart(match.match_date) }}
        </div>
      </div>

      <div class="text-gray-500 text-xs sm:text-sm leading-tight">
        <span v-if="match.status !== 'live'">{{ formatTimePart(match.match_date) }} • </span>
        <span v-else>LIVE • </span>
        <span class="hidden xs:inline">{{ match.venue }}</span>
        <span class="xs:hidden">{{ truncateVenue(match.venue) }}</span>
      </div>
    </div>

    <!-- Teams and Score -->
    <div class="flex items-center justify-between">
      <!-- Home Team -->
      <div class="flex items-center space-x-2 sm:space-x-3 md:space-x-4 flex-1 min-w-0">
        <div class="flex-shrink-0">
          <img
            :src="match.home_team.logo_url"
            :alt="match.home_team.name"
            class="w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-full object-cover shadow-md"
          />
        </div>
        <div class="min-w-0 flex-1">
          <div class="font-semibold text-gray-800 text-sm sm:text-base md:text-lg truncate">
            {{ match.home_team.name }}
          </div>
          <div class="text-gray-500 text-xs sm:text-sm">Home</div>
        </div>
      </div>

      <!-- Score/Versus -->
      <div class="flex-shrink-0 mx-2 sm:mx-3 md:mx-4">
        <div v-if="match.status === 'live' || match.status === 'completed'" class="text-center">
          <div class="flex items-center space-x-2 sm:space-x-3">
            <div class="text-xl sm:text-2xl md:text-3xl font-bold text-gray-800">
              {{ match.home_team_score || 0 }}
            </div>
            <div class="text-gray-400 font-bold text-sm">-</div>
            <div class="text-xl sm:text-2xl md:text-3xl font-bold text-gray-800">
              {{ match.away_team_score || 0 }}
            </div>
          </div>
          <div v-if="match.status === 'live'" class="text-xs text-red-600 font-medium mt-1 animate-pulse">LIVE</div>
          <div v-else-if="match.status === 'completed'" class="text-xs text-green-600 font-medium mt-1">
            FULL TIME
          </div>
        </div>
        <div v-else-if="match.status === 'postponed'" class="bg-orange-100 rounded-full p-1.5 sm:p-2 md:p-3">
          <div class="text-orange-600 font-bold text-xs sm:text-sm">PP</div>
        </div>
        <div v-else class="bg-gray-100 rounded-full p-1.5 sm:p-2 md:p-3">
          <div class="text-gray-600 font-bold text-xs sm:text-sm">VS</div>
        </div>
      </div>

      <!-- Away Team -->
      <div class="flex items-center space-x-2 sm:space-x-3 md:space-x-4 flex-1 min-w-0 justify-end">
        <div class="min-w-0 flex-1 text-right">
          <div class="font-semibold text-gray-800 text-sm sm:text-base md:text-lg truncate">
            {{ match.away_team.name }}
          </div>
          <div class="text-gray-500 text-xs sm:text-sm">Away</div>
        </div>
        <div class="flex-shrink-0">
          <img
            :src="match.away_team.logo_url"
            :alt="match.away_team.name"
            class="w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-full object-cover shadow-md"
          />
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex space-x-2 mt-3">
      <button
        v-if="hasLineups"
        @click="emit('view-lineup', match)"
        class="flex items-center space-x-1 px-3 py-1.5 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors border border-green-200 text-xs sm:text-sm font-medium"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="hidden sm:inline">View Lineup</span>
      </button>

      <button
        v-if="match.status !== 'completed' && match.status !== 'postponed'"
        @click="emit('open-upload', match)"
        class="flex items-center space-x-1 px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors border border-blue-200 text-xs sm:text-sm font-medium"
        title="Upload Lineup CSV"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <span class="hidden sm:inline">Upload Lineup</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Fixture } from "@/helpers/types/team";

const props = defineProps<{
  match: Fixture;
}>();

const emit = defineEmits<{
  (e: "open-upload", fixture: Fixture): void;
  (e: "view-lineup", fixture: Fixture): void;
}>();

const hasLineups = computed(() => props.match.lineups && props.match.lineups.length > 0);

const formatDatePart = (dateStr: string) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  }).format(date);
};

const formatTimePart = (dateStr: string) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  }).format(date);
};

const truncateVenue = (venue: string) => {
  if (!venue) return "";
  if (venue.length <= 15) return venue;
  return venue.substring(0, 12) + "...";
};
</script>
