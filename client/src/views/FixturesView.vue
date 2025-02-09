<template>
    <div>
      <div class="bg-gradient-to-br from-gray-50 to-gray-100 p-6">
        <div class="bg-white w-full overflow-hidden rounded-2xl shadow-lg">
          <!-- Header Section -->
          <div class="bg-white text-gray-800 p-6 flex flex-col md:flex-row justify-between items-center">
            <div class="flex items-center mb-4 md:mb-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mr-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h1 class="text-3xl font-extrabold tracking-wide text-gray-600">
                Football Fixtures
              </h1>
            </div>
            <div class="flex items-center space-x-4">
              <select 
                v-model="selectedLeague" 
                class="bg-white text-gray-600 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option v-for="league in leagues" :key="league.id" :value="league.id">
                  {{ league.name }}
                </option>
              </select>
              <input 
                v-model="dateFilter" 
                type="date" 
                class="bg-white text-gray-600 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
  
          <!-- Gameweek Navigation -->
          <div class="p-6 border-b border-gray-200 flex justify-between items-center">
            <button 
              @click="previousGameweek" 
              class="text-blue-600 px-4 py-2 rounded-lg font-semibold transition flex items-center hover:bg-blue-50"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              Previous
            </button>
            <span class="font-semibold text-gray-700">Gameweek {{ currentGameweek }}</span>
            <button 
              @click="nextGameweek" 
              class="text-blue-600 font-semibold px-4 py-2 rounded-lg transition flex items-center hover:bg-blue-50"
            >
              Next
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
  
          <!-- Fixtures Section -->
          <div class="p-6">
            <div v-for="(dayFixtures, date) in groupedFixtures" :key="date" class="mb-8">
              <h2 class="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">
                {{ formatDate(date) }}
              </h2>
              <div class="grid gap-4">
                <div 
                  v-for="fixture in dayFixtures" 
                  :key="fixture.id" 
                  class="bg-gray-50 p-4 rounded-lg shadow-md flex flex-col md:flex-row items-center justify-between hover:bg-gray-100 transition"
                >
                  <div class="flex items-center space-x-6 w-full md:w-auto">
                    <div class="flex items-center space-x-4">
                      <img src="/logo.png" :alt="fixture.homeTeam.name" class="h-12 w-12">
                      <span class="font-semibold text-gray-500">{{ fixture.homeTeam.name }}</span>
                    </div>
                    <div class="text-center">
                      <span class="text-gray-500 text-sm">{{ fixture.time }}</span>
                      <div class="font-bold text-blue-600">
                        {{ fixture.status === 'LIVE' ? 'LIVE' : 'vs' }}
                      </div>
                    </div>
                    <div class="flex items-center space-x-4">
                      <img src="/logo.png" :alt="fixture.awayTeam.name" class="h-12 w-12">
                      <span class="font-semibold text-gray-500">{{ fixture.awayTeam.name }}</span>
                    </div>
                  </div>
                  <div class="flex items-center space-x-4 mt-4 md:mt-0">
                    <span 
                      :class="{
                        'bg-green-100 text-green-800': fixture.status === 'SCHEDULED',
                        'bg-red-100 text-red-800': fixture.status === 'LIVE',
                        'bg-gray-100 text-gray-800': fixture.status === 'COMPLETED'
                      }" 
                      class="px-3 py-1 rounded-full text-xs font-semibold"
                    >
                      {{ fixture.status }}
                    </span>
                    <button 
                      class="text-blue-600 font-semibold px-4 py-2 hover:text-blue-700 transition"
                    >
                      Details
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Results Section -->
          <div class="p-6 border-t border-gray-200">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Match Results</h2>
            <div class="grid gap-4">
              <div 
                v-for="result in completedFixtures" 
                :key="result.id" 
                class="bg-gray-50 p-4 rounded-lg shadow-md flex flex-col md:flex-row items-center justify-between hover:bg-gray-100 transition"
              >
                <div class="flex items-center space-x-6 w-full md:w-auto">
                  <div class="flex items-center space-x-4">
                    <img src="/logo.png" :alt="result.homeTeam.name" class="h-12 w-12">
                    <span class="font-semibold text-gray-500">{{ result.homeTeam.name }}</span>
                  </div>
                  <div class="text-center">
                    <span class="text-gray-500 text-sm">{{ result.time }}</span>
                    <div class="font-bold text-blue-600">
                      {{ result.homeScore }} - {{ result.awayScore }}
                    </div>
                  </div>
                  <div class="flex items-center space-x-4">
                    <img src="/logo.png" :alt="result.awayTeam.name" class="h-12 w-12">
                    <span class="font-semibold text-gray-500">{{ result.awayTeam.name }}</span>
                  </div>
                </div>
                <div class="flex items-center space-x-4 mt-4 md:mt-0">
                  <span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-800">
                    COMPLETED
                  </span>
                  <button 
                    class="text-blue-600 font-semibold px-4 py-2 hover:text-blue-700 transition"
                  >
                    Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  
  const leagues = [
    { id: 1, name: 'Premier League' },
    { id: 2, name: 'La Liga' },
    { id: 3, name: 'Bundesliga' }
  ];
  
  const selectedLeague = ref(1);
  const dateFilter = ref(null);
  const currentGameweek = ref(1);
  
  const fixtures = ref([
    {
      id: 1,
      date: '2024-02-15',
      time: '20:00',
      status: 'SCHEDULED',
      homeTeam: {
        name: 'Manchester United',
        logo: 'https://example.com/mu-logo.png'
      },
      awayTeam: {
        name: 'Liverpool',
        logo: 'https://example.com/liverpool-logo.png'
      }
    },
    {
      id: 2,
      date: '2024-02-15',
      time: '18:30',
      status: 'LIVE',
      homeTeam: {
        name: 'Real Madrid',
        logo: 'https://example.com/rm-logo.png'
      },
      awayTeam: {
        name: 'Barcelona',
        logo: 'https://example.com/barca-logo.png'
      }
    },
    {
      id: 3,
      date: '2024-02-16',
      time: '15:00',
      status: 'COMPLETED',
      homeTeam: {
        name: 'Bayern Munich',
        logo: 'https://example.com/bayern-logo.png'
      },
      awayTeam: {
        name: 'Borussia Dortmund',
        logo: 'https://example.com/dortmund-logo.png'
      },
      homeScore: 2,
      awayScore: 1
    }
  ]);
  
  const groupedFixtures = computed(() => {
    return fixtures.value.reduce((acc, fixture) => {
      if (!acc[fixture.date]) {
        acc[fixture.date] = [];
      }
      acc[fixture.date].push(fixture);
      return acc;
    }, {});
  });
  
  const completedFixtures = computed(() => {
    return fixtures.value.filter(fixture => fixture.status === 'COMPLETED');
  });
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long', 
      month: 'long', 
      day: 'numeric'
    });
  };
  
  const previousGameweek = () => {
    if (currentGameweek.value > 1) {
      currentGameweek.value--;
    }
  };
  
  const nextGameweek = () => {
    currentGameweek.value++;
  };
  </script>
  
  <style scoped>
  /* Add custom styles if needed */
  </style>