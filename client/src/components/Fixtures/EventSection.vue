<template>
  <div class="border border-gray-200 rounded-lg">
    <!-- Section Header -->
    <div class="flex items-center space-x-3 p-4 border-b border-gray-100 bg-gray-50 rounded-t-lg">
      <span class="text-xl">{{ icon }}</span>
      <h3 class="font-semibold text-gray-900">{{ title }}</h3>
      <span class="text-xs text-gray-500 bg-white px-2 py-1 rounded-full">
        {{ events.length }}
      </span>
    </div>

    <!-- Events List -->
    <div class="divide-y divide-gray-100">
      <div 
        v-for="(event, index) in events" 
        :key="event.event_id || index"
        class="p-4 hover:bg-gray-50 transition-colors"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <!-- Team Badge -->
            <div 
              class="w-3 h-3 rounded-full"
              :class="{
                'bg-red-500': event.team_id === event.fixture?.home_team?.id,
                'bg-blue-500': event.team_id === event.fixture?.away_team?.id
              }"
            ></div>
            
            <!-- Player Name -->
            <span class="font-medium text-gray-900">{{ event.player_name }}</span>
            
            <!-- Team Name -->
            <span class="text-sm text-gray-500">{{ event.team_name }}</span>
          </div>

          <!-- Event Details -->
          <div class="flex items-center space-x-4 text-sm text-gray-500">
            <!-- Minute -->
            <span v-if="event.minute" class="bg-gray-100 px-2 py-1 rounded">
              {{ event.minute }}'
            </span>
            
            <!-- Count (for multiple events) -->
            <span v-if="event.count && event.count > 1" class="bg-gray-100 px-2 py-1 rounded">
              ×{{ event.count }}
            </span>
          </div>
        </div>

        <!-- Additional Info for Substitutions -->
        <div v-if="event.type === 'substitution'" class="mt-2 pl-6 text-sm text-gray-600">
          <div class="flex items-center space-x-2">
            <span class="text-red-500">⬇️ {{ event.player_out }}</span>
            <span class="text-gray-400">→</span>
            <span class="text-green-500">⬆️ {{ event.player_in }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Event {
  type: string
  player_name: string
  player_id: string
  team_id: string
  team_name: string
  count?: number
  minute?: number
  event_id?: string
  player_out?: string
  player_in?: string
  fixture?: {
    home_team?: {
      id: string
    }
    away_team?: {
      id: string
  }}
}

interface Props {
  title: string
  icon: string
  events: Event[]
  color?: string
}

defineProps<Props>()
</script>