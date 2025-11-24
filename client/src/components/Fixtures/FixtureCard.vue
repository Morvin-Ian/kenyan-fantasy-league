<template>
  <div
    class="p-4 sm:p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
  >
    <!-- Match Header -->
    <div class="text-center mb-4">
      <div class="flex items-center justify-center gap-2 mb-2">
        <div
          class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium"
          :class="{
            'bg-red-100 text-red-700': match.status === 'live',
            'bg-orange-100 text-orange-700': match.status === 'postponed',
            'bg-green-100 text-green-700': match.status === 'completed',
            'bg-blue-100 text-blue-700': match.status === 'upcoming'
          }"
        >
          <svg
            v-if="match.status === 'live'"
            class="w-3 h-3 mr-1 animate-pulse"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <circle cx="12" cy="12" r="8" />
          </svg>
          <svg
            v-else-if="match.status === 'postponed'"
            class="w-3 h-3 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
          <svg
            v-else-if="match.status === 'completed'"
            class="w-3 h-3 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <svg
            v-else
            class="w-3 h-3 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          {{ matchStatusText }}
        </div>
        <div
          v-if="match.status !== 'live'"
          class="inline-flex items-center bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-xs font-medium"
        >
          {{ formatDate(match.match_date) }}
        </div>
      </div>
      <div class="text-gray-500 text-sm">
        <span v-if="match.status !== 'live'">{{ formatTime(match.match_date) }} • </span>
        <span>{{ match.venue }}</span>
      </div>
    </div>

    <!-- Teams and Score -->
    <div class="flex items-center justify-between mb-4">
      <!-- Home Team -->
      <div class="flex items-center space-x-3 flex-1 min-w-0">
        <img
          :src="match.home_team.logo_url"
          :alt="match.home_team.name"
          class="w-12 h-12 rounded-full object-cover border-2 border-gray-100"
        />
        <div class="min-w-0 flex-1">
          <div class="font-semibold text-gray-900 text-sm truncate">
            {{ match.home_team.name }}
          </div>
          <div class="text-gray-500 text-xs">Home</div>
        </div>
      </div>

      <!-- Score -->
      <div class="mx-4 flex-shrink-0">
        <div v-if="match.status === 'live' || match.status === 'completed'" class="text-center">
          <div class="flex items-center space-x-3">
            <div class="text-2xl font-bold text-gray-900">
              {{ match.home_team_score || 0 }}
            </div>
            <div class="text-gray-400 font-bold">-</div>
            <div class="text-2xl font-bold text-gray-900">
              {{ match.away_team_score || 0 }}
            </div>
          </div>
          <div v-if="match.status === 'live'" class="text-xs text-red-600 font-medium mt-1 animate-pulse">
            LIVE
          </div>
        </div>
        <div v-else class="text-gray-400 font-semibold text-sm">
          VS
        </div>
      </div>

      <!-- Away Team -->
      <div class="flex items-center space-x-3 flex-1 min-w-0 justify-end">
        <div class="min-w-0 flex-1 text-right">
          <div class="font-semibold text-gray-900 text-sm truncate">
            {{ match.away_team.name }}
          </div>
          <div class="text-gray-500 text-xs">Away</div>
        </div>
        <img
          :src="match.away_team.logo_url"
          :alt="match.away_team.name"
          class="w-12 h-12 rounded-full object-cover border-2 border-gray-100"
        />
      </div>
    </div>

    <!-- Events Summary -->
    <div v-if="match.status === 'completed' && match.events_summary" class="mb-4 pt-4 border-t border-gray-100">
      <div class="flex justify-center space-x-6 text-xs text-gray-600">
        <div class="flex items-center space-x-1">
          <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
          <span>{{ match.events_summary.goals }} Goals</span>
        </div>
        <div class="flex items-center space-x-1">
          <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <span>{{ match.events_summary.assists }} Assists</span>
        </div>
        <div class="flex items-center space-x-1">
          <svg class="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
            <rect width="18" height="18" x="3" y="3" rx="2"/>
          </svg>
          <span>{{ match.events_summary.yellow_cards + match.events_summary.red_cards }} Cards</span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-wrap gap-2">
      <!-- View Lineup -->
      <button
        v-if="hasLineups"
        @click="emit('view-lineup', match)"
        class="flex-1 sm:flex-none inline-flex items-center justify-center space-x-2 px-3 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors border border-green-200 text-sm font-medium"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <span>Lineup</span>
      </button>

      <!-- Upload Lineup -->
      <button
        v-if="(match.status !== 'postponed') && isAdmin"
        @click="emit('open-upload', match)"
        class="flex-1 sm:flex-none inline-flex items-center justify-center space-x-2 px-3 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors border border-blue-200 text-sm font-medium"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <span>Upload First 11</span>
      </button>

      <!-- Match Events (Admin) -->
      <button
        v-if="(match.status === 'completed' || match.status === 'live') && isAdmin"
        @click="emit('open-events', match)"
        class="flex-1 sm:flex-none inline-flex items-center justify-center space-x-2 px-3 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors border border-purple-200 text-sm font-medium"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <span>Upload Details</span>
      </button>

      <!-- View Events -->
      <button
        v-if="(match.status === 'completed' || match.status === 'live') && hasEvents"
        @click="emit('view-events', match)"
        class="flex-1 sm:flex-none inline-flex items-center justify-center space-x-2 px-3 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors border border-gray-200 text-sm font-medium"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        <span>View Details</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import type { Fixture } from "@/helpers/types/team";

const props = defineProps<{
  match: Fixture;
}>();

const emit = defineEmits<{
  (e: "open-upload", fixture: Fixture): void;
  (e: "view-lineup", fixture: Fixture): void;
  (e: "open-events", fixture: Fixture): void;
  (e: "view-events", fixture: Fixture): void;
}>();

const isAdmin = computed(() => {
  return useAuthStore().user?.is_admin;
});

const hasLineups = computed(() => 
  props.match.lineups && props.match.lineups.length > 0
);

const hasEvents = computed(() => 
  props.match.events_summary && 
  (props.match.events_summary.goals > 0 || 
   props.match.events_summary.assists > 0 || 
   props.match.events_summary.yellow_cards > 0 || 
   props.match.events_summary.red_cards > 0)
);


const matchStatusText = computed(() => {
  switch (props.match.status) {
    case 'live': return 'LIVE';
    case 'completed': return 'COMPLETED';
    case 'postponed': return 'POSTPONED';
    default: return 'UPCOMING';
  }
});

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  });
};

const formatTime = (dateString: string) => {
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
};
</script>