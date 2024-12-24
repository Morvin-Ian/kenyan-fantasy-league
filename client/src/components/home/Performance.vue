<template>
  <div class="space-y-8">
    <!-- Featured Players Section -->
    <div class="bg-gray-50 p-4 md:p-6 rounded-xl">
      <div class="flex flex-wrap justify-between items-center mb-6 gap-2">
        <h2 class="text-lg md:text-2xl font-bold text-gray-900">Featured Players</h2>
        <button class="text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors">
          View all players
        </button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="player in featuredPlayers" :key="player.id"
          class="bg-white rounded-xl p-4 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-gray-200 overflow-hidden">
              <img :src="player.image" :alt="player.name" class="w-full h-full object-cover" />
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 text-sm sm:text-base">
                {{ player.name }}
              </h3>
              <p class="text-xs sm:text-sm text-gray-600">{{ player.team }}</p>
            </div>
          </div>

          <div class="mt-4 grid grid-cols-3 gap-2">
            <div class="text-center p-2 bg-gray-50 rounded-lg">
              <p class="text-xs text-gray-600">Goals</p>
              <p class="font-semibold text-gray-900 text-sm">
                {{ player.stats.goals }}
              </p>
            </div>
            <div class="text-center p-2 bg-gray-50 rounded-lg">
              <p class="text-xs text-gray-600">Assists</p>
              <p class="font-semibold text-gray-900 text-sm">
                {{ player.stats.assists }}
              </p>
            </div>
            <div class="text-center p-2 bg-gray-50 rounded-lg">
              <p class="text-xs text-gray-600">Rating</p>
              <p class="font-semibold text-gray-900 text-sm">
                {{ player.stats.rating }}/10
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Featured Goals Section -->
    <div class="bg-gray-50 p-4 md:p-6 rounded-xl">
      <div class="flex flex-wrap justify-between items-center mb-6 gap-2">
        <h2 class="text-lg md:text-2xl font-bold text-gray-900">Featured Goals</h2>
        <button class="text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors">
          View all goals
        </button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div v-for="goal in featuredGoals" :key="goal.id"
          class="bg-white rounded-xl overflow-hidden border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <div class="aspect-video bg-gray-200">
            <!-- Placeholder for video thumbnail -->
            <div class="absolute inset-0 flex items-center justify-center relative">
              <iframe width="853" height="480" src="https://www.youtube.com/embed/_q1KiLWGY_o"
                title="The Money Test You Need To Take." frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                referrerpolicy="strict-origin-when-cross-origin" allowfullscreen
                class="w-full h-[200px] sm:h-[300px] md:h-[480px] transition-all"></iframe>
            </div>
          </div>

          <div class="p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-900">
                {{ goal.minute }}'
              </span>
              <span class="px-2 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-600">
                {{ goal.matchType }}
              </span>
            </div>

            <h3 class="font-medium text-gray-900 mb-1 text-sm sm:text-base">
              {{ goal.scorer }}
            </h3>
            <p class="text-xs sm:text-sm text-gray-600 mb-2">
              {{ goal.match }}
            </p>

            <div class="flex items-center gap-3">
              <div class="flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2">
                  <path
                    d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3">
                  </path>
                </svg>
                <span class="text-xs sm:text-sm text-gray-600">
                  {{ goal.likes }}
                </span>
              </div>
              <div class="flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2">
                  <path
                    d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z">
                  </path>
                </svg>
                <span class="text-xs sm:text-sm text-gray-600">
                  {{ goal.comments }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
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
]

const featuredGoals = [
  {
    id: 1,
    scorer: "Jude Bellingham",
    match: "Real Madrid vs Barcelona",
    minute: "78",
    matchType: "La Liga",
    likes: "15.2K",
    comments: "1.2K"
  },
  {
    id: 2,
    scorer: "Marcus Rashford",
    match: "Manchester United vs Arsenal",
    minute: "34",
    matchType: "Premier League",
    likes: "12.8K",
    comments: "986"
  }
]
</script>