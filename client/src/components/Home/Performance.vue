<template>
  <div class="bg-gradient-to-br from-gray-50 to-blue-50 p-8 rounded-2xl mx-4 shadow-lg mb-8 p-6 md:p-10">
    <div class="max-w-10xl mx-auto space-y-5">
      <!-- Featured Players Section -->
      <div class="bg-white/80 backdrop-blur-lg rounded-2xl shadow-2xl p-6 md:p-8 border border-gray-100">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-2xl font-bold text-gray-800 tracking-tight">Top Performers</h2>
          <button class="bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600 transition transform hover:scale-105">
            Explore All Players
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div 
            v-for="player in featuredPlayers"
            :key="player.id"
            class="bg-white rounded-2xl p-5 shadow-lg hover:shadow-xl transition-all group"
          >
            <div class="flex items-center space-x-4 mb-4">
              <div class="w-20 h-20 rounded-full overflow-hidden border-4 border-indigo-100 group-hover:border-indigo-200 transition">
                <img :src="player.image" :alt="player.name" class="w-full h-full object-cover" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-indigo-900">{{ player.name }}</h3>
                <p class="text-sm text-gray-500">{{ player.team }}</p>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <div 
                v-for="stat in [
                  { label: 'Goals', value: player.stats.goals },
                  { label: 'Assists', value: player.stats.assists },
                  { label: 'Rating', value: `${player.stats.rating}/10` }
                ]"
                :key="stat.label"
                class="bg-indigo-50 rounded-xl p-3 text-center"
              >
                <p class="text-xs text-gray-600 mb-1">{{ stat.label }}</p>
                <p class="font-bold text-indigo-800">{{ stat.value }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Featured Goals Section -->
      <div class="bg-white/80 backdrop-blur-lg rounded-2xl shadow-2xl p-6 md:p-8 border border-gray-100">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-2xl font-bold text-gray-800 tracking-tight">Spectacular Goals</h2>
          <button class="bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600 transition transform hover:scale-105">
            Watch All Highlights
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div 
            v-for="goal in featuredGoals"
            :key="goal.id"
            class="bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-all group"
          >
            <div class="relative">
              <iframe 
                :src="`https://www.youtube.com/embed/${goal.videoId}`"
                :title="`${goal.scorer} Goal`"
                class="w-full aspect-video"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
              />
              <div class="absolute top-3 right-3 bg-emerald-500/80 text-white px-3 py-1 rounded-full text-sm">
                {{ goal.matchType }}
              </div>
            </div>

            <div class="p-5">
              <div class="flex justify-between items-center mb-3">
                <span class="text-lg font-bold text-gray-800">{{ goal.scorer }}</span>
                <span class="text-sm text-gray-600">{{ goal.minute }}' Minute</span>
              </div>
              <p class="text-gray-600 mb-4">{{ goal.match }}</p>

              <div class="flex space-x-4">
                <div class="flex items-center space-x-2">
                  <HeartIcon class="w-5 h-5 text-red-400" />
                  <span class="text-sm text-gray-600">{{ goal.likes }}</span>
                </div>
                <div class="flex items-center space-x-2">
                  <MessageCircleIcon class="w-5 h-5 text-blue-400" />
                  <span class="text-sm text-gray-600">{{ goal.comments }}</span>
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
/* Add custom styles if needed */
</style>