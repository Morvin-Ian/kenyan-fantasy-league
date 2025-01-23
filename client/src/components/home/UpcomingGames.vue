<template>
  <div class="bg-gray-50 p-6  rounded-xl">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:justify-between items-start">
      <h2 class="text-2xl font-semibold text-gray-900 md:mr-4 mb-2 md:mb-0 text-left">Upcoming Matches</h2>
      <div class="flex items-center gap-4 justify-start">
        <a href="#" class="flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <span class="text-sm font-medium">Full Calendar</span>
        </a>
        <div class="flex gap-2">
          <button @click="scroll('left')"
            class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
          <button @click="scroll('right')"
            class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>
      </div>
    </div>



    <!-- Matches Container -->
    <div ref="scrollContainer" class="flex gap-4 overflow-x-auto pb-4 hide-scrollbar">
      <div v-for="game in games" :key="game.id" :class="[
        'flex-shrink-0 w-64 p-4 rounded-xl bg-white border transition-all',
        game.status === 'UPCOMING' ? 'border-blue-500 shadow-lg' : 'border-gray-200 shadow-md',
        game.status === 'POSTPONED' ? 'opacity-75' : ''
      ]">
        <div class="space-y-3">
          <!-- League & Status -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 bg-gray-100 rounded-full">
                <img src="../../assets/logo.png" alt="">
              </div>
              <span class="text-sm font-medium text-gray-600">{{ game.type }}</span>
            </div>
            <div :class="[
              'px-2 py-1 rounded-full text-xs font-semibold',
              {
                'bg-blue-100 text-blue-700': game.status === 'UPCOMING',
                'bg-gray-100 text-gray-600': game.status === 'ENDED' || game.status === 'POSTPONED'
              }
            ]">
              {{ game.status }}
            </div>
          </div>

          <!-- Teams -->
          <div class="space-y-1">
            <div class="text-sm font-medium text-gray-900">{{ game.homeTeam }}</div>
            <div class="text-sm font-medium text-gray-900">{{ game.awayTeam }}</div>
          </div>

          <!-- Date & Time -->
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <span>{{ formatDate(game.date) }}</span>
            <span>•</span>
            <span>{{ game.time }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const scrollContainer = ref(null)

const games = [
  {
    id: 1,
    homeTeam: "Manchester United",
    awayTeam: "Arsenal",
    date: "2024-12-28",
    time: "20:00",
    type: "Premier Leaguee",
    status: "ENDED"
  },
  {
    id: 2,
    homeTeam: "Real Madrid",
    awayTeam: "Barcelona",
    date: "2024-12-30",
    time: "21:00",
    type: "Premier League",
    status: "UPCOMING"
  },
  {
    id: 3,
    homeTeam: "Juventus",
    awayTeam: "Napoli",
    date: "2025-01-01",
    time: "19:45",
    type: "Premier League",
    status: "POSTPONED"
  },
  {
    id: 4,
    homeTeam: "PSG",
    awayTeam: "Marseille",
    date: "2025-01-05",
    time: "20:00",
    type: "Premier League",
    status: "POSTPONED"
  },
  {
    id: 4,
    homeTeam: "PSG",
    awayTeam: "Marseille",
    date: "2025-01-05",
    time: "20:00",
    type: "Premier League",
    status: "POSTPONED"
  },
  {
    id: 4,
    homeTeam: "PSG",
    awayTeam: "Marseille",
    date: "2025-01-05",
    time: "20:00",
    type: "Premier League",
    status: "POSTPONED"
  }
]

const scroll = (direction) => {
  if (scrollContainer.value) {
    const scrollAmount = 280 // Width of card + gap
    scrollContainer.value.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth'
    })
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  }).format(date)
}
</script>

<style scoped>
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>