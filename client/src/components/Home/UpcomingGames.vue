<template>
    <div class="bg-gradient-to-br from-gray-50 to-blue-50 p-4 sm:p-6 md:p-8 rounded-2xl mx-2 sm:mx-4 shadow-lg mb-3">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:justify-between items-start gap-4">
        <div class="animate-fade-in">
          <h2 class="text-xl sm:text-2xl font-bold text-gray-700 bg-clip-text">
            Upcoming Matches
          </h2>
          <p class="text-sm sm:text-base text-gray-500 mt-1 sm:mt-2">
            Stay updated with the latest fixtures
          </p>
        </div>
        <div class="flex items-center gap-2 sm:gap-4 justify-start">
          <router-link
            to="/fixtures"
            class="flex items-center gap-1 sm:gap-2 text-blue-600 hover:text-blue-700 transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-3 h-3 sm:w-4 sm:h-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <span class="text-xs sm:text-sm font-medium">Full Calendar</span>
          </router-link>
          <div class="flex gap-1 sm:gap-2">
            <button
              @click="scroll('left')"
              class="p-1 sm:p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-4 h-4 sm:w-5 sm:h-5 text-gray-600"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>
            <button
              @click="scroll('right')"
              class="p-1 sm:p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-4 h-4 sm:w-5 sm:h-5 text-gray-600"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
          </div>
        </div>
      </div>
  
      <!-- Matches Container -->
      <div ref="scrollContainer" class="flex gap-3 sm:gap-4 md:gap-6 overflow-x-auto pb-4 sm:pb-6 mt-4 hide-scrollbar">
        <div
          v-for="(game, index) in games"
          :key="game.id"
          :style="{ animationDelay: `${index * 100}ms` }"
          class="animate-slide-up flex-shrink-0 w-56 sm:w-64 md:w-72 rounded-xl sm:rounded-2xl bg-white border-2 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 group"
          :class="[
            game.status === 'UPCOMING' ? 'border-blue-400 shadow-lg' : 'border-gray-100 shadow-md',
            game.status === 'POSTPONED' ? 'opacity-75' : '',
          ]"
        >
          <div class="p-3 sm:p-4 md:p-6 space-y-3 sm:space-y-4">
            <!-- League & Status -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2 sm:gap-3">
                <div class="w-8 h-8 sm:w-10 sm:h-10 bg-gray-50 rounded-full p-2 group-hover:scale-110 transition-transform duration-300">
                  <img src="../../assets/logo.png" alt="" class="w-full h-full object-contain" />
                </div>
                <span class="text-xs sm:text-sm font-light text-gray-700">{{ game.type }}</span>
              </div>
              <div
                :class="[
                  'px-2 sm:px-3 py-1 rounded-full text-xs font-bold tracking-wide transition-colors duration-300',
                  {
                    'bg-blue-100 text-blue-700 group-hover:bg-blue-200': game.status === 'UPCOMING',
                    'bg-gray-100 text-gray-600 group-hover:bg-gray-200': game.status === 'ENDED',
                    'bg-red-50 text-red-600 group-hover:bg-red-100': game.status === 'POSTPONED',
                  },
                ]"
              >
                {{ game.status }}
              </div>
            </div>
  
            <!-- Teams -->
            <div class="space-y-1">
              <div class="text-xs sm:text-sm font-medium text-gray-900">
                {{ game.homeTeam }}
              </div>
              <div class="text-xs sm:text-sm font-medium text-gray-900">
                {{ game.awayTeam }}
              </div>
            </div>
  
            <!-- Date & Time -->
            <div class="flex items-center gap-2 pt-2 border-t border-gray-100">
              <div class="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm text-gray-500">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-3 h-3 sm:w-4 sm:h-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                <span>{{ formatDate(game.date) }}</span>
                <span class="text-gray-300">•</span>
                <span>{{ game.time }}</span>
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
      
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from "vue";
  
  const scrollContainer = ref<HTMLElement | null>(null);
  
  const games = [
    {
      id: 1,
      homeTeam: "Manchester United",
      awayTeam: "Arsenal",
      date: "2024-12-28",
      time: "20:00",
      type: "Premier League",
      status: "ENDED",
    },
    {
      id: 2,
      homeTeam: "Real Madrid",
      awayTeam: "Barcelona",
      date: "2024-12-30",
      time: "21:00",
      type: "Premier League",
      status: "UPCOMING",
    },
    {
      id: 3,
      homeTeam: "Juventus",
      awayTeam: "Napoli",
      date: "2025-01-01",
      time: "19:45",
      type: "Premier League",
      status: "POSTPONED",
    },
    {
      id: 4,
      homeTeam: "PSG",
      awayTeam: "Marseille",
      date: "2025-01-05",
      time: "20:00",
      type: "Premier League",
      status: "POSTPONED",
    },
    {
      id: 5,
      homeTeam: "Liverpool",
      awayTeam: "Chelsea",
      date: "2025-01-05",
      time: "20:00",
      type: "Premier League",
      status: "POSTPONED",
    },
    {
      id: 6,
      homeTeam: "Bayern Munich",
      awayTeam: "Dortmund",
      date: "2025-01-05",
      time: "20:00",
      type: "Premier League",
      status: "POSTPONED",
    },
    {
      id: 6,
      homeTeam: "Bayern Munich",
      awayTeam: "Dortmund",
      date: "2025-01-05",
      time: "20:00",
      type: "Premier League",
      status: "POSTPONED",
    },
    {
      id: 6,
      homeTeam: "Bayern Munich",
      awayTeam: "Dortmund",
      date: "2025-01-05",
      time: "20:00",
      type: "Premier League",
      status: "POSTPONED",
    },
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

  const scroll = (direction: "left" | "right") => {
    if (!scrollContainer.value) return;
  
    const scrollAmount = window.innerWidth < 640 ? 230 : 280;
    const isLeft = direction === "left";
  
    scrollContainer.value.scrollBy({
      left: isLeft ? -scrollAmount : scrollAmount,
      behavior: "smooth",
    });
  };
  
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    }).format(date);
  };
  </script>
  
  <style scoped>
  .hide-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  
  .hide-scrollbar::-webkit-scrollbar {
    display: none;
  }
  
  .animate-fade-in {
    animation: fadeIn 0.6s ease-out;
  }
  
  .animate-slide-in {
    animation: slideIn 0.6s ease-out;
  }
  
  .animate-slide-up {
    animation: slideUp 0.6s ease-out forwards;
    opacity: 0;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
  
    to {
      opacity: 1;
    }
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(20px);
    }
  
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
  
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* Add smooth transitions for all interactive elements */
  button,
  a {
    transition: all 0.3s ease;
  }
  
  @media (max-width: 640px) {
    .animate-slide-up {
      animation-duration: 0.5s;
    }
  }
  </style>