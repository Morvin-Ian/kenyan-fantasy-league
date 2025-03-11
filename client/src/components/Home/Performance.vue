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

      <!-- Table Standings Section (Updated with scrollable for mobile) -->
      <div class="bg-white rounded-xl md:rounded-3xl shadow-lg md:shadow-xl p-4 md:p-8 border border-gray-100 overflow-hidden relative">
        <div class="absolute top-0 left-0 w-full h-48 pointer-events-none"></div>
        
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 md:mb-8 gap-3">
          <h2 class="text-xl md:text-3xl font-bold text-gray-800 tracking-tight flex items-center">
            <span class="mr-2 md:mr-3">📊</span> League Standings
          </h2>
          <div class="flex space-x-2">
            <button class="bg-indigo-500 text-white px-3 md:px-4 py-1.5 md:py-2 rounded-full font-medium text-xs md:text-sm">FKF League</button>
            <button class="bg-gray-100 text-gray-700 px-3 md:px-4 py-1.5 md:py-2 rounded-full font-medium text-xs md:text-sm hover:bg-gray-200 transition-colors">Super League</button>
          </div>
        </div>
        
        <!-- Mobile and Desktop Table View (Scrollable on small screens) -->
        <div class="overflow-x-auto relative">
          <table class="w-full min-w-full table-auto">
            <thead>
              <tr class="border-b border-gray-100">
                <th class="py-3 px-4 text-left text-gray-600 font-medium">#</th>
                <th class="py-3 px-4 text-left text-gray-600 font-medium">Team</th>
                <th class="py-3 px-4 text-center text-gray-600 font-medium">MP</th>
                <th class="py-3 px-4 text-center text-gray-600 font-medium">W</th>
                <th class="py-3 px-4 text-center text-gray-600 font-medium">D</th>
                <th class="py-3 px-4 text-center text-gray-600 font-medium">L</th>
                <th class="py-3 px-4 text-center text-gray-600 font-medium">GF</th>
                <th class="py-3 px-4 text-center text-gray-600 font-medium">GA</th>
                <th class="py-3 px-4 text-center text-gray-600 font-medium">GD</th>
                <th class="py-3 px-4 text-center text-gray-600 font-medium">PTS</th>
                <th class="py-3 px-4 text-center text-gray-600 font-medium">Form</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(team, index) in standings" 
                :key="team.id"
                class="border-b border-gray-50 hover:bg-gray-50 transition-colors"
                :class="{'bg-indigo-50/50': index < 4}"
              >
                <td class="py-3 md:py-4 px-2 md:px-4 font-medium text-sm" :class="{'text-indigo-600': index < 4, 'text-red-500': index > 16}">{{ index + 1 }}</td>
                <td class="py-3 md:py-4 px-2 md:px-4">
                  <div class="flex items-center space-x-2 md:space-x-3">
                    <img :src="team.logo" alt="Team logo" class="w-5 h-5 md:w-6 md:h-6" />
                    <span class="font-medium text-gray-900 text-sm">{{ team.name }}</span>
                  </div>
                </td>
                <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-sm">{{ team.played }}</td>
                <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-sm">{{ team.won }}</td>
                <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-sm">{{ team.drawn }}</td>
                <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-sm">{{ team.lost }}</td>
                <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-sm">{{ team.goalsFor }}</td>
                <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-sm">{{ team.goalsAgainst }}</td>
                <td class="py-3 md:py-4 px-2 md:px-4 text-center font-medium text-sm" :class="{'text-green-500': team.goalDifference > 0, 'text-red-500': team.goalDifference < 0}">{{ team.goalDifference }}</td>
                <td class="py-3 md:py-4 px-2 md:px-4 text-center font-bold text-gray-900 text-sm">{{ team.points }}</td>
                <td class="py-3 md:py-4 px-2 md:px-4">
                  <div class="flex justify-center space-x-1">
                    <span 
                      v-for="result in team.form" 
                      :key="result"
                      class="w-5 h-5 md:w-6 md:h-6 rounded-full flex items-center justify-center text-xs text-white font-medium"
                      :class="{
                        'bg-green-500': result === 'W',
                        'bg-gray-400': result === 'D',
                        'bg-red-500': result === 'L'
                      }"
                    >
                      {{ result }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Visual indicator that table scrolls horizontally (mobile only) -->
        <div class="flex justify-center mt-3 md:hidden">
          <div class="flex space-x-1 items-center text-xs text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span>Swipe right to see more</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </div>
      
      <!-- Quick Access Navigation - Mobile Only -->
      <div class="fixed bottom-0 left-0 right-0 bg-white shadow-lg border-t border-gray-100 p-2 flex justify-around items-center md:hidden z-10">
        <button class="flex flex-col items-center justify-center py-1 px-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span class="text-xs mt-1 text-gray-600">Home</span>
        </button>
        <button class="flex flex-col items-center justify-center py-1 px-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span class="text-xs mt-1 text-gray-600">Stats</span>
        </button>
        <button class="flex flex-col items-center justify-center py-1 px-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-xs mt-1 text-gray-600">Videos</span>
        </button>
        <button class="flex flex-col items-center justify-center py-1 px-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <span class="text-xs mt-1 text-gray-600">News</span>
        </button>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { HeartIcon, MessageCircleIcon } from 'lucide-vue-next';
import { ref } from 'vue';
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

const trendingMatches = [
  {
    id: 1,
    league: "Champions League",
    time: "Today, 20:45",
    status: "live",
    homeTeam: {
      name: "Bayern",
      logo: "/api/placeholder/64/64",
      score: 2
    },
    awayTeam: {
      name: "PSG",
      logo: "/api/placeholder/64/64",
      score: 1
    },
    viewers: "1.2M watching"
  },
  {
    id: 2,
    league: "Premier League",
    time: "Today, 18:30",
    status: "FT",
    homeTeam: {
      name: "Arsenal",
      logo: "/api/placeholder/64/64",
      score: 3
    },
    awayTeam: {
      name: "Liverpool",
      logo: "/api/placeholder/64/64",
      score: 2
    },
    viewers: "842K watched"
  },
  {
    id: 3,
    league: "La Liga",
    time: "Tomorrow, 21:00",
    status: "Upcoming",
    homeTeam: {
      name: "Barcelona",
      logo: "/api/placeholder/64/64",
      score: 0
    },
    awayTeam: {
      name: "Atletico",
      logo: "/api/placeholder/64/64",
      score: 0
    },
    viewers: "523K interested"
  }
];

const standings = [
  {
    id: 1,
    name: "Manchester City",
    logo: "/api/placeholder/64/64",
    played: 27,
    won: 19,
    drawn: 6,
    lost: 2,
    goalsFor: 67,
    goalsAgainst: 24,
    goalDifference: 43,
    points: 63,
    form: ["W", "W", "D", "W", "W"]
  },
  {
    id: 2,
    name: "Arsenal",
    logo: "/api/placeholder/64/64",
    played: 27,
    won: 18,
    drawn: 4,
    lost: 5,
    goalsFor: 62,
    goalsAgainst: 24,
    goalDifference: 38,
    points: 58,
    form: ["W", "W", "W", "L", "W"]
  },
  {
    id: 3,
    name: "Liverpool",
    logo: "/api/placeholder/64/64",
    played: 27,
    won: 17,
    drawn: 7,
    lost: 3,
    goalsFor: 61,
    goalsAgainst: 26,
    goalDifference: 35,
    points: 58,
    form: ["L", "D", "W", "W", "W"]
  },
  {
    id: 4,
    name: "Aston Villa",
    logo: "/api/placeholder/64/64",
    played: 27,
    won: 16,
    drawn: 4,
    lost: 7,
    goalsFor: 55,
    goalsAgainst: 37,
    goalDifference: 18,
    points: 52,
    form: ["W", "W", "L", "W", "D"]
  },
  {
    id: 5,
    name: "Tottenham",
    logo: "/api/placeholder/64/64",
    played: 27,
    won: 14,
    drawn: 5,
    lost: 8,
    goalsFor: 53,
    goalsAgainst: 41,
    goalDifference: 12,
    points: 47,
    form: ["L", "L", "W", "W", "L"]
  },
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