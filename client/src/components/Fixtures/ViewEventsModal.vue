<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold text-gray-900">Match Events</h2>
            <p class="text-sm text-gray-600 mt-1">
              {{ fixture?.home_team?.name }} {{ fixture?.home_team_score }} - {{ fixture?.away_team_score }} {{ fixture?.away_team?.name }}
            </p>
            <p class="text-xs text-gray-500 mt-1">
              {{ formatDate(fixture?.match_date) }} • {{ fixture?.venue }}
            </p>
          </div>
          <button 
            @click="close"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6">
        <!-- Events Timeline -->
        <div v-if="hasEvents" class="space-y-4">
          <!-- Goals -->
          <EventSection 
            v-if="goals.length > 0"
            title="Goals" 
            icon="⚽" 
            :events="goals"
            color="green"
          />

          <!-- Assists -->
          <EventSection 
            v-if="assists.length > 0"
            title="Assists" 
            icon="🅰️" 
            :events="assists"
            color="blue"
          />

          <!-- Yellow Cards -->
          <EventSection 
            v-if="yellowCards.length > 0"
            title="Yellow Cards" 
            icon="🟨" 
            :events="yellowCards"
            color="yellow"
          />

          <!-- Red Cards -->
          <EventSection 
            v-if="redCards.length > 0"
            title="Red Cards" 
            icon="🟥" 
            :events="redCards"
            color="red"
          />

          <!-- Substitutions -->
          <EventSection 
            v-if="substitutions.length > 0"
            title="Substitutions" 
            icon="🔄" 
            :events="substitutions"
            color="purple"
          />
        </div>

        <!-- No Events State -->
        <div v-else class="text-center py-12">
          <div class="max-w-sm mx-auto">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 class="text-lg font-semibold text-gray-800 mb-2">No Events Recorded</h3>
            <p class="text-gray-500 text-sm">Match events will appear here once they are recorded.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import EventSection from './EventSection.vue'
import type { Fixture } from "@/helpers/types/team"

interface Props {
  isOpen: boolean
  fixture: Fixture | null
}

const props = defineProps<Props>()
const emit = defineEmits(['close'])

const hasEvents = computed(() => {
  return props.fixture?.events && props.fixture.events.length > 0
})

const goals = computed(() => {
  return props.fixture?.events?.filter(event => event.type === 'goal') || []
})

const assists = computed(() => {
  return props.fixture?.events?.filter(event => event.type === 'assist') || []
})

const yellowCards = computed(() => {
  return props.fixture?.events?.filter(event => event.type === 'yellow_card') || []
})

const redCards = computed(() => {
  return props.fixture?.events?.filter(event => event.type === 'red_card') || []
})

const substitutions = computed(() => {
  return props.fixture?.events?.filter(event => event.type === 'substitution') || []
})

const close = () => {
  emit('close')
}

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return 'Date not available'
  return new Date(dateString).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>