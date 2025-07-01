<template>
  <div class="min-h-screen p-6">
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
    </div>

    <div v-else class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <div class="bg-white shadow-md rounded-lg overflow-hidden">
          <div class="border-b p-6 flex flex-col md:flex-row justify-between items-center">
            <div>
              <h1 class="text-3xl font-bold text-gray-800">Kenyan Premier League</h1>
              <p class="text-gray-500 text-lg">Official Matchday Fixtures</p>
            </div>
            <div class="mt-4 md:mt-0">
              <router-link to="/standings"
                class="flex items-center bg-gray-100 text-gray-700 px-5 py-3 rounded-lg hover:bg-gray-200 transition-all">
                <BarChart2Icon size="20" class="mr-2" />
                League Table
              </router-link>
            </div>
          </div>

          <div v-if="fixtures.length > 0" class="p-6">
            <div class="space-y-4">
              <div v-for="match in paginatedFixtures" :key="match.id"
                class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all">
                <div class="flex justify-between items-center">
                  <!-- Home Team -->
                  <div class="flex items-center space-x-3 w-1/3">
                    <img :src="match.home_team.logo_url" :alt="match.home_team.name"
                      class="w-12 h-12 rounded-full object-cover" />
                    <span class="font-medium text-gray-800">{{ match.home_team.name }}</span>
                  </div>

                  <div class="text-center w-1/3">
                    <span class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                      {{ formatDatePart(match.match_date) }}
                    </span>
                    <div class="text-sm text-gray-500 mt-2">
                      {{ formatTimePart(match.match_date) }} | {{ match.venue }}
                    </div>
                  </div>

                  <!-- Away Team -->
                  <div class="flex items-center space-x-3 w-1/3 justify-end">
                    <span class="font-medium text-gray-800">{{ match.away_team.name }}</span>
                    <img :src="match.away_team.logo_url" :alt="match.away_team.name"
                      class="w-12 h-12 rounded-full object-cover" />
                  </div>
                </div>

                <!-- Betting Odds -->
                <div class="mt-4 flex justify-between text-sm text-gray-500 border-t border-gray-100 pt-3">
                  <div>
                    <span class="font-medium">Home Stats:</span>
                    12/5 Draw 11/5 Away 13/5
                  </div>
                  <div>
                    <span class="font-medium">Away Stats:</span>
                    12/5 Draw 11/5 Away 13/5
                  </div>
                </div>
              </div>
            </div>

            <!-- Pagination -->
            <div class="mt-6 flex justify-between items-center">
              <button @click="prevPage" :disabled="currentPage === 1"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-all flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span>Previous</span>
              </button>
              <span class="text-gray-600">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
              <button @click="nextPage" :disabled="currentPage === totalPages"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-all flex items-center space-x-2">
                <span>Next</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <div v-else class="p-6 text-center text-gray-500">
            No fixtures available
          </div>
        </div>
      </div>

      <!-- Sidebar Columns -->
      <div class="space-y-6">
        <div class="bg-white rounded-lg shadow-md p-5">
          <h2 class="text-xl font-bold text-gray-800 mb-4">Team Form</h2>
          <div class="space-y-3">
            <div v-for="team in topTeams" :key="team.name"
              class="flex justify-between items-center border border-gray-100 rounded-lg p-3">
              <div class="flex items-center space-x-3">
                <img :src="team.logo" class="w-8 h-8 rounded-full" :alt="team.name" />
                <span class="font-medium">{{ team.name }}</span>
              </div>
              <div class="flex space-x-1">
                <span v-for="result in team.lastFiveResults" :key="result"
                  class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold" :class="{
                    'bg-green-500': result === 'W',
                    'bg-gray-400': result === 'D',
                    'bg-red-500': result === 'L'
                  }">
                  {{ result }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Scorers -->
        <div class="bg-white rounded-lg shadow-md p-5">
          <h2 class="text-xl font-bold text-gray-800 mb-4">Top Scorers</h2>
          <div class="space-y-3">
            <div v-for="scorer in topScorers" :key="scorer.name"
              class="flex justify-between items-center border border-gray-100 rounded-lg p-3">
              <div class="flex items-center space-x-3">
                <div>
                  <span class="font-medium">{{ scorer.name }}</span>
                  <span class="text-sm text-gray-500 ml-2">{{ scorer.team }}</span>
                </div>
              </div>
              <span class="font-medium text-gray-700">{{ scorer.goals }} Goals</span>
            </div>
          </div>
        </div>

        <!-- League Statistics -->
        <div class="bg-white rounded-lg shadow-md p-5">
          <h2 class="text-xl font-bold text-gray-800 mb-4">League Stats</h2>
          <div class="grid grid-cols-2 gap-4">
            <div class="border border-gray-100 rounded-lg p-4 text-center">
              <div class="text-2xl font-bold text-gray-700">{{ leagueStats.totalGoals }}</div>
              <div class="text-sm text-gray-500">Total Goals</div>
            </div>
            <div class="border border-gray-100 rounded-lg p-4 text-center">
              <div class="text-2xl font-bold text-gray-700">{{ leagueStats.averageGoalsPerMatch }}</div>
              <div class="text-sm text-gray-500">Avg Goals/Match</div>
            </div>
            <div class="border border-gray-100 rounded-lg p-4 text-center">
              <div class="text-2xl font-bold text-gray-700">{{ leagueStats.homeWins }}%</div>
              <div class="text-sm text-gray-500">Home Wins</div>
            </div>
            <div class="border border-gray-100 rounded-lg p-4 text-center">
              <div class="text-2xl font-bold text-gray-700">{{ leagueStats.awayWins }}%</div>
              <div class="text-sm text-gray-500">Away Wins</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { BarChart2Icon } from 'lucide-vue-next';
import { useKplStore } from '@/stores/kpl';

const kplStore = useKplStore();
const { fixtures } = storeToRefs(kplStore);
const isLoading = ref(false);

watch(() => fixtures.value, (newFixtures) => {
  if (newFixtures.length === 0) {
    fetchFixtures();
  }
}, { immediate: true });

async function fetchFixtures() {
  try {
    isLoading.value = true;
    await kplStore.fetchFixtures();
  } catch (error) {
    console.error("Failed to fetch fixtures:", error);
  } finally {
    isLoading.value = false;
  }
}

const currentPage = ref(1);
const itemsPerPage = 5;

const totalPages = computed(() => Math.ceil(fixtures.value.length / itemsPerPage) || 1);

const paginatedFixtures = computed(() => {
  if (fixtures.value.length === 0) return [];
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
    goals: 15
  },
  {
    name: 'Clifton Miheso',
    team: 'AFC Leopards',
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