<template>
  <div class="bg-gradient-to-br from-gray-50 to-white p-3 md:p-8 min-h-screen">
    <div class=" mx-auto">
      <!-- Header -->
      <div class="text-center mb-6 md:mb-10 pt-4 md:pt-6">
        <h1 class="text-3xl md:text-5xl font-bold text-gray-900 tracking-tight mb-2 md:mb-4">
          <span class="bg-clip-text font-bold text-transparent bg-gradient-to-r from-gray-900 to-gray-800">Football Elite</span>
        </h1>
        <p class="text-sm md:text-base text-gray-600 max-w-2xl mx-auto px-2">Discover the extraordinary plays and exceptional talents shaping the beautiful game worldwide</p>
      </div>

      <!-- Featured Players Section -->
      <div class="bg-white rounded-xl md:rounded-3xl shadow-lg md:shadow-xl p-4 md:p-8 border border-gray-100 mb-4 md:mb-8 overflow-hidden relative">
        <div class="absolute top-0 left-0 w-full h-48 pointer-events-none"></div>
        
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 md:mb-8 gap-3">
          <h2 class="text-xl md:text-3xl font-bold text-gray-600 tracking-tight flex items-center">
            <span class="mr-2 md:mr-3">⚽</span> Star Performers
          </h2>
          <button class="bg-gradient-to-r from-indigo-500 to-blue-600 text-white px-3 md:px-5 py-2 md:py-2.5 rounded-full hover:from-indigo-600 hover:to-blue-700 transition transform hover:scale-105 hover:shadow-lg font-medium text-xs md:text-sm flex items-center">
            <span>Explore All Players</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 md:h-4 md:w-4 ml-1 md:ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          <div 
            v-for="player in featuredPlayers"
            :key="player.id"
            class="bg-white rounded-xl md:rounded-2xl p-4 md:p-6 shadow-md hover:shadow-lg transition-all duration-300 group border border-gray-100 overflow-hidden relative"
          >
            <!-- Subtle gradient background on hover -->
            <div class="absolute inset-0 group-hover:to-indigo-50 transition-opacity duration-500 opacity-0 group-hover:opacity-100"></div>
            
            <div class="flex items-center space-x-3 md:space-x-4 mb-4 md:mb-6 relative">
              <div class="w-14 h-14 md:w-20 md:h-20 rounded-full overflow-hidden border-2 md:border-4 border-indigo-100 group-hover:border-indigo-200 transition transform group-hover:scale-105 shadow-md">
                <img :src="player.image" :alt="player.name" class="w-full h-full object-cover" />
              </div>
              <div>
                <h3 class="text-lg md:text-xl font-bold text-gray-900">{{ player.name }}</h3>
                <p class="text-xs md:text-sm text-gray-500">{{ player.team }}</p>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-2 md:gap-3">
              <div 
                v-for="stat in [
                  { label: 'Goals', value: player.stats.goals, icon: '🥅' },
                  { label: 'Assists', value: player.stats.assists, icon: '👟' },
                  { label: 'Rating', value: `${player.stats.rating}`, icon: '⭐' }
                ]"
                :key="stat.label"
                class="bg-gray-50 rounded-lg md:rounded-xl p-2 md:p-3 text-center hover:bg-indigo-50 transition-all duration-300 border border-gray-100"
              >
                <p class="text-xs text-gray-500 mb-0 md:mb-1 flex justify-center items-center">
                  <span class="mr-1">{{ stat.icon }}</span>
                  {{ stat.label }}
                </p>
                <p class="font-bold text-indigo-700 text-base md:text-lg">{{ stat.value }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Featured Goals Section -->
      <div class="bg-white rounded-xl md:rounded-3xl shadow-lg md:shadow-xl p-4 md:p-8 border border-gray-100 overflow-hidden relative mb-4 md:mb-8">
        <div class="absolute top-0 left-0 w-full h-48 pointer-events-none"></div>
        
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 md:mb-8 gap-3">
          <h2 class="text-xl md:text-3xl font-bold text-gray-600 tracking-tight flex items-center">
            <span class="mr-2 md:mr-3">🏆</span> Spectacular Goals
          </h2>
          <button class="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-3 md:px-5 py-2 md:py-2.5 rounded-full hover:from-blue-600 hover:to-indigo-700 transition transform hover:scale-105 hover:shadow-lg font-medium text-xs md:text-sm flex items-center">
            <span>Watch All Highlights</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 md:h-4 md:w-4 ml-1 md:ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-8">
          <div 
            v-for="goal in featuredGoals"
            :key="goal.id"
            class="bg-white rounded-xl md:rounded-2xl overflow-hidden shadow-md hover:shadow-lg transition-all duration-300 group border border-gray-100"
          >
            <div class="relative">
              <iframe 
                :src="`https://www.youtube.com/embed/${goal.videoId}`"
                :title="`${goal.scorer} Goal`"
                class="w-full aspect-video"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
              />
              <div class="absolute top-2 md:top-3 right-2 md:right-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-2 md:px-4 py-0.5 md:py-1 rounded-full text-xs md:text-sm shadow-md flex items-center">
                <span class="w-1.5 h-1.5 md:w-2 md:h-2 bg-white rounded-full mr-1 md:mr-2 animate-pulse"></span>
                {{ goal.matchType }}
              </div>
            </div>

            <div class="p-3 md:p-6">
              <div class="flex justify-between items-center mb-2 md:mb-4">
                <span class="text-base md:text-xl font-bold text-gray-900">{{ goal.scorer }}</span>
                <span class="bg-gray-100 text-gray-700 px-2 md:px-3 py-0.5 md:py-1 rounded-full text-xs md:text-sm font-medium">{{ goal.minute }}'</span>
              </div>
              <p class="text-xs md:text-sm text-gray-600 mb-3 md:mb-6">{{ goal.match }}</p>

              <div class="flex space-x-4 md:space-x-6 border-t border-gray-100 pt-2 md:pt-4">
                <div class="flex items-center space-x-1 md:space-x-2 group cursor-pointer">
                  <HeartIcon class="w-4 h-4 md:w-5 md:h-5 text-pink-500 group-hover:text-pink-600 group-hover:scale-110 transition-all" />
                  <span class="text-xs md:text-sm text-gray-600 group-hover:text-gray-900 transition-colors">{{ goal.likes }}</span>
                </div>
                <div class="flex items-center space-x-1 md:space-x-2 group cursor-pointer">
                  <MessageCircleIcon class="w-4 h-4 md:w-5 md:h-5 text-blue-500 group-hover:text-blue-600 group-hover:scale-110 transition-all" />
                  <span class="text-xs md:text-sm text-gray-600 group-hover:text-gray-900 transition-colors">{{ goal.comments }}</span>
                </div>
                <div class="flex items-center space-x-1 md:space-x-2 ml-auto group cursor-pointer">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5 text-indigo-500 group-hover:text-indigo-600 group-hover:scale-110 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                  </svg>
                  <span class="text-xs md:text-sm text-gray-600 group-hover:text-gray-900 transition-colors">Share</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { HeartIcon, MessageCircleIcon } from 'lucide-vue-next';
import player3 from "@/assets/images/player3.png";
import player2 from "@/assets/images/player2.png";
import player1 from "@/assets/images/player1.png";

const featuredPlayers = [
  {
    id: 1,
    name: "Marcus Rashford",
    team: "Manchester United",
    image: player3,
    stats: {
      goals: 12,
      assists: 5,
      rating: 8.4
    }
  },
  {
    id: 2,
    name: "Jude Bellingham",
    team: "Real Madrid",
    image: player2,
    stats: {
      goals: 15,
      assists: 8,
      rating: 9.1
    }
  },
  {
    id: 3,
    name: "Erling Haaland",
    team: "Manchester City",
    image: player1,
    stats: {
      goals: 18,
      assists: 3,
      rating: 8.9
    }
  }
];

const featuredGoals = [
  {
    id: 1,
    scorer: "Jude Bellingham",
    match: "El Clásico: Real Madrid vs Barcelona",
    minute: "78",
    matchType: "La Liga",
    likes: "15.2K",
    comments: "1.2K",
    videoId: "Zc_vFPdHU48"
  },
  {
    id: 2,
    scorer: "Marcus Rashford",
    match: "Manchester Derby: United vs City",
    minute: "34",
    matchType: "Premier League",
    likes: "12.8K",
    comments: "986",
    videoId: "f7ENx8tWEHo"
  }
];

</script>

<style scoped>
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>