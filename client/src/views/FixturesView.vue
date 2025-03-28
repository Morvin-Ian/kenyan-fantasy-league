<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 to-green-100 p-6">
    <div class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Fixtures Column -->
      <div class="lg:col-span-2">
        <div class="bg-white shadow-2xl rounded-2xl overflow-hidden">
          <!-- Header Section -->
          <div class="bg-green-700 text-white p-6 flex flex-col md:flex-row justify-between items-center">
            <div>
              <h1 class="text-4xl font-extrabold mb-2">Kenyan Premier League</h1>
              <p class="text-green-200 text-lg">Official Matchday Fixtures</p>
            </div>
            <div class="flex space-x-4 mt-4 md:mt-0">
              <router-link to="/standings"
                class="flex items-center bg-white text-green-700 px-5 py-3 rounded-xl hover:bg-green-50 transition-all shadow-md">
                <BarChart2Icon size="24" class="mr-2" />
                League Table
              </router-link>
            </div>
          </div>

          <div class="p-6">
            <div class="space-y-5">
              <div v-for="match in paginatedFixtures" :key="match.id"
                class="bg-gray-100 rounded-xl p-5 shadow-md hover:shadow-xl transition-all group">
                <div class="flex justify-between items-center">
                  <!-- Home Team -->
                  <div class="flex items-center space-x-4 w-1/3">
                    <img :src="match.home_team.logo_url" :alt="match.home_team.name"
                      class="w-16 h-16 rounded-full object-cover shadow-md group-hover:scale-110 transition-transform" />
                    <span class="font-bold text-gray-800 text-lg">{{ match.home_team.name }}</span>
                  </div>

                  <div class="text-center w-1/3">
                    <span class="bg-green-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                      {{ formatDatePart(match.match_date) }}
                    </span>
                    <div class="text-sm text-gray-600 mt-2">
                      {{ formatTimePart(match.match_date) }} | {{ match.venue }}
                    </div>
                  </div>

                  <!-- Away Team -->
                  <div class="flex items-center space-x-4 w-1/3 justify-end">
                    <span class="font-bold text-gray-800 text-lg">{{ match.away_team.name }}</span>
                    <img :src="match.away_team.logo_url" :alt="match.away_team.name"
                      class="w-16 h-16 rounded-full object-cover shadow-md group-hover:scale-110 transition-transform" />
                  </div>
                </div>

                <!-- Betting Odds -->
                <div class="mt-4 flex justify-between text-sm text-gray-600 border-t border-green-200 pt-3">
                  <div>
                    <span class="font-semibold text-green-700">Home Stats:</span>
                    12/5 Draw 11/5 Away 13/5
                  </div>
                  <div>
                    <span class="font-semibold text-green-700">Away Stats:</span>
                    12/5 Draw 11/5 Away 13/5
                  </div>
                </div>
              </div>
            </div>

            <!-- Pagination -->
            <div class="mt-6 flex justify-between items-center">
              <button @click="prevPage" :disabled="currentPage === 1"
                class="group px-6 py-3 bg-green-500 text-white rounded-full shadow-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-300 flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 transform group-hover:-translate-x-1" fill="none"
                  viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span>Previous</span>
              </button>
              <span class="text-gray-700 font-semibold">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
              <button @click="nextPage" :disabled="currentPage === totalPages"
                class="group px-6 py-3 bg-green-500 text-white rounded-full shadow-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-300 flex items-center space-x-2">
                <span>Next</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 transform group-hover:translate-x-1" fill="none"
                  viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar Columns -->
      <div class="space-y-6">
        <!-- Team Form Guide -->
        <div class="bg-white rounded-2xl shadow-xl p-6">
          <h2 class="text-2xl font-bold text-green-800 mb-4">Team Form</h2>
          <div class="space-y-3">
            <div v-for="team in topTeams" :key="team.name"
              class="flex justify-between items-center bg-green-50 rounded-lg p-3">
              <div class="flex items-center space-x-3">
                <img :src="team.logo" class="w-10 h-10 rounded-full" :alt="team.name" />
                <span class="font-semibold">{{ team.name }}</span>
              </div>
              <div class="flex space-x-1">
                <span v-for="result in team.lastFiveResults" :key="result"
                  class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold" :class="{
                    'bg-green-600': result === 'W',
                    'bg-gray-500': result === 'D',
                    'bg-red-600': result === 'L'
                  }">
                  {{ result }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Scorers -->
        <div class="bg-white rounded-2xl shadow-xl p-6">
          <h2 class="text-2xl font-bold text-green-800 mb-4">Top Scorers</h2>
          <div class="space-y-3">
            <div v-for="scorer in topScorers" :key="scorer.name"
              class="flex justify-between items-center bg-green-50 rounded-lg p-3">
              <div class="flex items-center space-x-3">
                <div>
                  <span class="font-semibold">{{ scorer.name }}</span>
                  <span class="text-sm text-gray-600 ml-2">{{ scorer.team }}</span>
                </div>
              </div>
              <span class="font-bold text-green-700">{{ scorer.goals }} Goals</span>
            </div>
          </div>
        </div>

        <!-- League Statistics -->
        <div class="bg-white rounded-2xl shadow-xl p-6">
          <h2 class="text-2xl font-bold text-green-800 mb-4">League Stats</h2>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-green-50 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-green-700">{{ leagueStats.totalGoals }}</div>
              <div class="text-sm text-gray-600">Total Goals</div>
            </div>
            <div class="bg-green-50 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-green-700">{{ leagueStats.averageGoalsPerMatch }}</div>
              <div class="text-sm text-gray-600">Avg Goals/Match</div>
            </div>
            <div class="bg-green-50 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-green-700">{{ leagueStats.homeWins }}%</div>
              <div class="text-sm text-gray-600">Home Wins</div>
            </div>
            <div class="bg-green-50 rounded-lg p-4 text-center">
              <div class="text-3xl font-bold text-green-700">{{ leagueStats.awayWins }}%</div>
              <div class="text-sm text-gray-600">Away Wins</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { BarChart2Icon, StarIcon } from 'lucide-vue-next';
import { useKplStore } from '@/stores/kpl';

const kplStore = useKplStore();
const { fixtures } = storeToRefs(kplStore);

const currentPage = ref(1);
const itemsPerPage = 5;

const totalPages = computed(() => Math.ceil(fixtures.value.length / itemsPerPage));

const paginatedFixtures = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return fixtures.value.slice(start, start + itemsPerPage);
});

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};

// Utility Functions
const formatDatePart = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", { weekday: "short", month: "short", day: "numeric" }).format(date);
};

const formatTimePart = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", { hour: "2-digit", minute: "2-digit", hour12: true }).format(date);
};

// Mock Data for Sidebar
const showFavorites = ref(false);
const toggleFavorites = () => {
  showFavorites.value = !showFavorites.value;
};

const topTeams = [
  {
    name: 'Gor Mahia',
    logo: '/path/to/gor-mahia-logo.png',
    lastFiveResults: ['W', 'W', 'D', 'L', 'W']
  },
  {
    name: 'AFC Leopards',
    logo: '/path/to/afc-leopards-logo.png',
    lastFiveResults: ['W', 'D', 'W', 'L', 'D']
  }
];

const topScorers = [
  {
    name: 'Michael Olunga',
    team: 'Gor Mahia',
    photo: '/path/to/olunga.jpg',
    goals: 15
  },
  {
    name: 'Clifton Miheso',
    team: 'AFC Leopards',
    photo: '/path/to/miheso.jpg',
    goals: 12
  }
];

const leagueStats = {
  totalGoals: 245,
  averageGoalsPerMatch: 2.7,
  homeWins: 62,
  awayWins: 38
};
</script>

<style scoped>
/* Additional custom styles can be added here if needed */
</style>