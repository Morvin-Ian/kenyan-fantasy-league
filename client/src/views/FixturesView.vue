<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-gray-50 to-blue-50 p-4 md:p-8 font-sans">
    <div class="max-w-6xl mx-auto">
      <!-- Header Section with League Logo -->
      <div class="bg-white rounded-xl shadow-xl overflow-hidden mb-6">
        <div class="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6">
          <div class="flex flex-col md:flex-row justify-between items-center">
            <div class="flex items-center mb-4 md:mb-0">
              <div class="bg-white p-2 rounded-full shadow-lg mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 class="text-3xl font-extrabold tracking-wide">
                  Football Fixtures
                </h1>
                <p class="text-blue-100 mt-1">Stay updated with all matches</p>
              </div>
            </div>
            
            <div class="flex flex-col sm:flex-row items-center space-y-3 sm:space-y-0 sm:space-x-4">
              <select 
                v-model="selectedLeague" 
                class="bg-white text-gray-700 px-4 py-2 rounded-lg border border-blue-200 shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-auto"
              >
                <option v-for="league in leagues" :key="league.id" :value="league.id">
                  {{ league.name }}
                </option>
              </select>
              <input 
                v-model="dateFilter" 
                type="date" 
                class="bg-white text-gray-700 px-4 py-2 rounded-lg border border-blue-200 shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-auto"
              />
            </div>
          </div>
        </div>
        
        <!-- Season Progress Bar -->
        <div class="px-6 py-4 border-b border-gray-200 bg-white">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm text-gray-500">Season Progress</span>
            <span class="text-sm font-medium text-blue-600">Gameweek {{ currentGameweek }}/38</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div class="bg-blue-600 h-2.5 rounded-full" :style="`width: ${(currentGameweek / 38) * 100}%`"></div>
          </div>
        </div>

        <!-- Gameweek Navigation -->
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
          <button 
            @click="previousGameweek" 
            class="text-blue-600 px-4 py-2 rounded-lg font-semibold transition flex items-center hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="currentGameweek <= 1"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            Previous
          </button>
          
          <div class="flex space-x-1">
            <span 
              v-for="week in 5" 
              :key="week"
              :class="[
                'w-8 h-8 flex items-center justify-center rounded-full cursor-pointer transition-all',
                currentGameweek === week + (currentGameweek - 3 > 0 ? currentGameweek - 3 : 0) 
                  ? 'bg-blue-600 text-white font-bold' 
                  : 'text-gray-600 hover:bg-blue-100'
              ]"
              @click="currentGameweek = week + (currentGameweek - 3 > 0 ? currentGameweek - 3 : 0)"
            >
              {{ week + (currentGameweek - 3 > 0 ? currentGameweek - 3 : 0) }}
            </span>
          </div>
          
          <button 
            @click="nextGameweek" 
            class="text-blue-600 font-semibold px-4 py-2 rounded-lg transition flex items-center hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="currentGameweek >= 38"
          >
            Next
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Content Container -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Live Matches Panel -->
        <div class="md:col-span-3 bg-white rounded-xl shadow-lg overflow-hidden mb-6">
          <div class="bg-red-600 px-6 py-3 flex justify-between items-center">
            <h2 class="text-lg font-bold text-white flex items-center">
              <span class="relative flex h-3 w-3 mr-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                <span class="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
              </span>
              LIVE MATCHES
            </h2>
            <span class="text-white text-sm bg-red-700 px-2 py-1 rounded">2 Games</span>
          </div>
          
          <div class="p-4">
            <div class="bg-gradient-to-r from-red-50 to-white p-4 rounded-lg shadow-md mb-4 border border-red-100 transform hover:scale-[1.01] transition-all">
              <div class="flex flex-col sm:flex-row items-center justify-between">
                <div class="flex items-center space-x-4 mb-4 sm:mb-0">
                  <div class="flex flex-col items-center">
                    <div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden border-2 border-blue-200">
                      <span class="font-bold text-xl text-gray-600">RM</span>
                    </div>
                    <span class="font-medium text-gray-600 mt-1">Real Madrid</span>
                  </div>
                  
                  <div class="flex flex-col items-center">
                    <div class="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-semibold mb-1">LIVE</div>
                    <div class="text-3xl font-bold text-gray-800">0 - 0</div>
                    <div class="text-red-600 text-sm font-medium">32'</div>
                  </div>
                  
                  <div class="flex flex-col items-center">
                    <div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden border-2 border-blue-200">
                      <span class="font-bold text-xl text-gray-600">FCB</span>
                    </div>
                    <span class="font-medium text-gray-600 mt-1">Barcelona</span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-4">
                  <button class="bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
                    </svg>
                    Watch Live
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Upcoming Fixtures Section -->
        <div class="md:col-span-2">
          <div class="bg-white rounded-xl shadow-lg overflow-hidden mb-6">
            <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-3">
              <h2 class="text-lg font-bold text-white">Upcoming Fixtures</h2>
            </div>
            
            <div class="p-6">
              <div v-for="(dayFixtures, date) in groupedFixtures" :key="date" class="mb-8">
                <h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                  </svg>
                  {{ formatDate(date) }}
                </h2>
                
                <div class="space-y-4">
                  <div 
                    v-for="fixture in dayFixtures" 
                    :key="fixture.id" 
                    class="bg-white p-4 rounded-lg shadow border border-gray-100 hover:border-blue-200 transition transform hover:scale-[1.01] hover:shadow-md"
                  >
                    <div class="flex flex-col sm:flex-row items-center justify-between">
                      <div class="flex items-center justify-between w-full sm:w-auto sm:space-x-8">
                        <div class="flex flex-col items-center">
                          <div class="w-14 h-14 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden border border-gray-200 mb-2">
                            <span class="font-bold text-gray-600">{{ fixture.homeTeam.name.substring(0, 2) }}</span>
                          </div>
                          <span class="font-medium text-gray-600 text-sm">{{ fixture.homeTeam.name }}</span>
                        </div>
                        
                        <div class="flex flex-col items-center justify-center px-4">
                          <span class="text-blue-800 font-bold text-lg">vs</span>
                          <span class="text-gray-500 text-sm mt-1">{{ fixture.time }}</span>
                          <div class="mt-1 px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                            {{ fixture.status }}
                          </div>
                        </div>
                        
                        <div class="flex flex-col items-center">
                          <div class="w-14 h-14 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden border border-gray-200 mb-2">
                            <span class="font-bold text-gray-600">{{ fixture.awayTeam.name.substring(0, 2) }}</span>
                          </div>
                          <span class="font-medium text-gray-600 text-sm">{{ fixture.awayTeam.name }}</span>
                        </div>
                      </div>
                      
                      <div class="mt-4 sm:mt-0">
                        <button class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                          </svg>
                          Details
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Results Section -->
        <div class="md:col-span-1">
          <div class="bg-white rounded-xl shadow-lg overflow-hidden mb-6">
            <div class="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-3">
              <h2 class="text-lg font-bold text-white flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Recent Results
              </h2>
            </div>
            
            <div class="p-4">
              <div class="space-y-4">
                <div 
                  v-for="result in completedFixtures" 
                  :key="result.id" 
                  class="bg-gray-50 p-4 rounded-lg shadow-md border border-gray-100 hover:border-gray-300 transition transform hover:scale-[1.01]"
                >
                  <div class="flex flex-col items-center">
                    <div class="text-sm text-gray-500 mb-2">{{ formatDate(result.date) }} - {{ result.time }}</div>
                    
                    <div class="grid grid-cols-3 items-center w-full mb-3">
                      <div class="flex flex-col items-center justify-center">
                        <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-1 border border-gray-200">
                          <span class="font-bold text-gray-600">{{ result.homeTeam.name.substring(0, 2) }}</span>
                        </div>
                        <span class="text-sm font-medium text-gray-600">{{ result.homeTeam.name }}</span>
                      </div>
                      
                      <div class="flex items-center justify-center">
                        <div class="bg-gray-200 px-4 py-2 rounded text-center">
                          <div class="text-2xl font-bold text-gray-800">{{ result.homeScore }} - {{ result.awayScore }}</div>
                          <div class="text-xs text-gray-500 mt-1">FINAL</div>
                        </div>
                      </div>
                      
                      <div class="flex flex-col items-center justify-center">
                        <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-1 border border-gray-200">
                          <span class="font-bold text-gray-600">{{ result.awayTeam.name.substring(0, 2) }}</span>
                        </div>
                        <span class="text-sm font-medium text-gray-600">{{ result.awayTeam.name }}</span>
                      </div>
                    </div>
                    
                    <button class="w-full bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-800 transition mt-2 flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 0l-2 2a1 1 0 101.414 1.414L8 10.414l1.293 1.293a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                      Match Stats
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Team News and Updates -->
          <div class="bg-white rounded-xl shadow-lg overflow-hidden">
            <div class="bg-gradient-to-r from-indigo-600 to-indigo-700 px-6 py-3">
              <h2 class="text-lg font-bold text-white">News & Updates</h2>
            </div>
            
            <div class="p-4">
              <div class="space-y-4">
                <div class="bg-gray-50 p-4 rounded-lg border border-gray-100 hover:border-indigo-200 transition transform hover:scale-[1.01]">
                  <div class="text-sm text-indigo-600 font-medium mb-1">INJURY UPDATE</div>
                  <h3 class="font-bold text-gray-800 mb-2">Kane out for 3 weeks with ankle injury</h3>
                  <p class="text-sm text-gray-600 mb-2">The striker is expected to miss the next three matches due to an ankle injury sustained during training.</p>
                  <div class="text-xs text-gray-500">2 hours ago</div>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-lg border border-gray-100 hover:border-indigo-200 transition transform hover:scale-[1.01]">
                  <div class="text-sm text-indigo-600 font-medium mb-1">TRANSFER NEWS</div>
                  <h3 class="font-bold text-gray-800 mb-2">Manchester United eyeing young midfielder</h3>
                  <p class="text-sm text-gray-600 mb-2">Reports suggest United are preparing a bid for the 19-year-old sensation in the upcoming transfer window.</p>
                  <div class="text-xs text-gray-500">8 hours ago</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Footer -->
      <div class="mt-6 text-center text-gray-500 text-sm">
        <p>© 2025 Football Fixtures • All Rights Reserved</p>
        <div class="flex justify-center space-x-4 mt-2">
          <a href="#" class="hover:text-blue-600 transition">Terms</a>
          <a href="#" class="hover:text-blue-600 transition">Privacy</a>
          <a href="#" class="hover:text-blue-600 transition">Contact</a>
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
const currentGameweek = ref(12);  // Changed to mid-season for better progress bar visualization

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
  if (currentGameweek.value < 38) {
    currentGameweek.value++;
  }
};
</script>