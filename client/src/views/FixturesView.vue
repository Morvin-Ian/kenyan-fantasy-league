<template>
  <div class="">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <div v-if="isLoading" class="flex justify-center items-center h-64">
        <div class="relative">
          <div class="animate-spin rounded-full h-16 w-16 border-4 border-gray-200"></div>
          <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-gray-600 absolute top-0"></div>
        </div>
      </div>

      <div v-else-if="fixtures.length > 0" class="space-y-4 sm:space-y-6">
        <div class="flex justify-between items-center mb-6 sm:mb-8">
          <div>
            <h2 class="text-2xl md:text-4xl font-black text-gray-600 flex items-center justify-center space-x-2 md:space-x-4">
              <span class="truncuate">Fixtures</span>
            </h2>
          </div>
          <div>
            <router-link to="/standings"
              class="inline-flex items-center bg-white text-gray-700 px-4 py-2 rounded-full hover:bg-gray-100 transition-colors duration-200 shadow-sm border border-gray-200 text-sm font-medium">
              View Table
            </router-link>
          </div>
        </div>

        <!-- Tabs Navigation -->
        <div class="flex space-x-1 bg-gray-100 p-1 rounded-xl mb-6">
          <button
            @click="activeTab = 'upcoming'"
            :class="{
              'bg-white text-gray-900 shadow-sm': activeTab === 'upcoming',
              'text-gray-600 hover:text-gray-900': activeTab !== 'upcoming'
            }"
            class="flex-1 py-2.5 px-4 text-sm font-medium rounded-lg transition-all duration-200 relative">
            <div class="flex items-center justify-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
              <span>Upcoming & Live</span>
              <span v-if="upcomingAndLiveFixtures.length > 0" 
                class="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-blue-600 rounded-full">
                {{ upcomingAndLiveFixtures.length }}
              </span>
            </div>
          </button>
          <button
            @click="activeTab = 'finished'"
            :class="{
              'bg-white text-gray-900 shadow-sm': activeTab === 'finished',
              'text-gray-600 hover:text-gray-900': activeTab !== 'finished'
            }"
            class="flex-1 py-2.5 px-4 text-sm font-medium rounded-lg transition-all duration-200">
            <div class="flex items-center justify-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>Finished</span>
              <span v-if="finishedFixtures.length > 0" 
                class="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-green-600 rounded-full">
                {{ finishedFixtures.length }}
              </span>
            </div>
          </button>
          <button
            @click="activeTab = 'postponed'"
            :class="{
              'bg-white text-gray-900 shadow-sm': activeTab === 'postponed',
              'text-gray-600 hover:text-gray-900': activeTab !== 'postponed'
            }"
            class="flex-1 py-2.5 px-4 text-sm font-medium rounded-lg transition-all duration-200">
            <div class="flex items-center justify-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
              <span>Postponed</span>
              <span v-if="postponedFixtures.length > 0" 
                class="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-orange-600 rounded-full">
                {{ postponedFixtures.length }}
              </span>
            </div>
          </button>
        </div>

        <!-- Tab Content -->
        <div class="space-y-4">
          <!-- Upcoming & Live Tab -->
          <div v-if="activeTab === 'upcoming'">
            <div v-if="paginatedUpcomingFixtures.length === 0" class="text-center py-12">
              <div class="max-w-sm mx-auto">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <h3 class="text-lg font-semibold text-gray-800 mb-2">No Upcoming Fixtures</h3>
                <p class="text-gray-500 text-sm">Check back later for scheduled matches</p>
              </div>
            </div>
            <div v-else>
              <div v-for="match in paginatedUpcomingFixtures" :key="match.id"
                class="bg-white  p-4 md:p-5 shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100 hover:border-gray-200"
                :class="{ 'bg-red-50': match.status === 'live' }">

                <div class="text-center mb-4">
                  <div class="flex items-center justify-center space-x-2 mb-2">
                    <div
                      class="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium"
                      :class="{
                        'bg-red-100 text-red-700': match.status === 'live',
                        'bg-gray-50 text-gray-700': match.status !== 'live'
                      }">
                      <svg v-if="match.status === 'live'" class="w-4 h-4 mr-1.5 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="8"/>
                      </svg>
                      <svg v-else class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                      </svg>
                      {{ match.status === 'live' ? 'LIVE' : 'UPCOMING' }}
                    </div>
                    <div v-if="match.status !== 'live'" 
                      class="inline-flex items-center bg-gray-50 text-gray-700 px-3 py-1.5 rounded-full text-sm font-medium">
                      {{ formatDatePart(match.match_date) }}
                    </div>
                  </div>
                  <div v-if="match.status !== 'live'" class="text-gray-500 text-xs sm:text-sm">
                    {{ formatTimePart(match.match_date) }} • {{ match.venue }}
                  </div>
                  <div v-else class="text-gray-500 text-xs sm:text-sm">
                    LIVE • {{ match.venue }}
                  </div>
                </div>

                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-3 sm:space-x-4 flex-1">
                    <div class="relative">
                      <img :src="match.home_team.logo_url" :alt="match.home_team.name"
                        class="w-12 h-12 sm:w-14 sm:h-14 rounded-full object-cover shadow-md" />
                    </div>
                    <div class="text-left">
                      <div class="font-semibold text-gray-800 text-base sm:text-lg">{{ match.home_team.name }}</div>
                      <div class="text-gray-500 text-xs sm:text-sm">Home</div>
                    </div>
                  </div>

                  <div class="flex-shrink-0 mx-2 sm:mx-4">
                    <!-- Show scores if live -->
                    <div v-if="match.status === 'live'" class="text-center">
                      <div class="flex items-center space-x-3">
                        <div class="text-2xl sm:text-3xl font-bold text-gray-800">
                          {{ match.home_team_score || 0 }}
                        </div>
                        <div class="text-gray-400 font-bold text-sm">-</div>
                        <div class="text-2xl sm:text-3xl font-bold text-gray-800">
                          {{ match.away_team_score || 0 }}
                        </div>
                      </div>
                      <div class="text-xs text-red-600 font-medium mt-1 animate-pulse">LIVE</div>
                    </div>
                    <!-- Show VS if upcoming -->
                    <div v-else class="bg-gray-100 rounded-full p-2 sm:p-3">
                      <div class="text-gray-600 font-bold text-xs sm:text-sm">VS</div>
                    </div>
                  </div>

                  <div class="flex items-center space-x-3 sm:space-x-4 flex-1 justify-end">
                    <div class="text-right">
                      <div class="font-semibold text-gray-800 text-base sm:text-lg">{{ match.away_team.name }}</div>
                      <div class="text-gray-500 text-xs sm:text-sm">Away</div>
                    </div>
                    <div class="relative">
                      <img :src="match.away_team.logo_url" :alt="match.away_team.name"
                        class="w-12 h-12 sm:w-14 sm:h-14 rounded-full object-cover shadow-md" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Finished Tab -->
          <div v-if="activeTab === 'finished'">
            <div v-if="paginatedFinishedFixtures.length === 0" class="text-center py-12">
              <div class="max-w-sm mx-auto">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <h3 class="text-lg font-semibold text-gray-800 mb-2">No Finished Matches</h3>
                <p class="text-gray-500 text-sm">Completed matches will appear here</p>
              </div>
            </div>
            <div v-else>
              <div v-for="match in paginatedFinishedFixtures" :key="match.id"
                class="bg-white p-4 md:p-5 shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100 hover:border-gray-200">

                <div class="text-center mb-4">
                  <div class="flex items-center justify-center space-x-2 mb-2">
                    <div class="inline-flex items-center bg-gray-50 text-gray-700 px-3 py-1.5 rounded-full text-sm font-medium">
                      {{ formatDatePart(match.match_date) }}
                    </div>
                  </div>
                  <div class="text-gray-500 text-xs sm:text-sm">
                    {{ formatTimePart(match.match_date) }} • {{ match.venue }}
                  </div>
                </div>

                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-3 sm:space-x-4 flex-1">
                    <div class="relative">
                      <img :src="match.home_team.logo_url" :alt="match.home_team.name"
                        class="w-12 h-12 sm:w-14 sm:h-14 rounded-full object-cover shadow-md" />
                    </div>
                    <div class="text-left">
                      <div class="font-semibold text-gray-800 text-base sm:text-lg">{{ match.home_team.name }}</div>
                      <div class="text-gray-500 text-xs sm:text-sm">Home</div>
                    </div>
                  </div>

                  <div class="flex-shrink-0 mx-2 sm:mx-4">
                    <div class="text-center">
                      <div class="flex items-center space-x-3">
                        <div class="text-2xl sm:text-3xl font-bold text-gray-800">
                          {{ match.home_team_score || 0 }}
                        </div>
                        <div class="text-gray-400 font-bold text-sm">-</div>
                        <div class="text-2xl sm:text-3xl font-bold text-gray-800">
                          {{ match.away_team_score || 0 }}
                        </div>
                      </div>
                      <div class="text-xs text-green-600 font-medium mt-1">FULL TIME</div>
                    </div>
                  </div>

                  <div class="flex items-center space-x-3 sm:space-x-4 flex-1 justify-end">
                    <div class="text-right">
                      <div class="font-semibold text-gray-800 text-base sm:text-lg">{{ match.away_team.name }}</div>
                      <div class="text-gray-500 text-xs sm:text-sm">Away</div>
                    </div>
                    <div class="relative">
                      <img :src="match.away_team.logo_url" :alt="match.away_team.name"
                        class="w-12 h-12 sm:w-14 sm:h-14 rounded-full object-cover shadow-md" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Postponed Tab -->
          <div v-if="activeTab === 'postponed'">
            <div v-if="paginatedPostponedFixtures.length === 0" class="text-center py-12">
              <div class="max-w-sm mx-auto">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
                <h3 class="text-lg font-semibold text-gray-800 mb-2">No Postponed Matches</h3>
                <p class="text-gray-500 text-sm">Postponed matches will appear here</p>
              </div>
            </div>
            <div v-else>
              <div v-for="match in paginatedPostponedFixtures" :key="match.id"
                class="bg-orange-50 p-4 md:p-5 shadow-sm hover:shadow-md transition-all duration-200 border border-orange-200 hover:border-orange-300">

                <div class="text-center mb-4">
                  <div class="flex items-center justify-center space-x-2 mb-2">
                    <div class="inline-flex items-center bg-orange-100 text-orange-700 px-3 py-1.5 rounded-full text-sm font-medium">
                      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                      </svg>
                      POSTPONED
                    </div>
                    <div class="inline-flex items-center bg-gray-50 text-gray-700 px-3 py-1.5 rounded-full text-sm font-medium">
                      {{ formatDatePart(match.match_date) }}
                    </div>
                  </div>
                  <div class="text-gray-500 text-xs sm:text-sm">
                    Originally: {{ formatTimePart(match.match_date) }} • {{ match.venue }}
                  </div>
                </div>

                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-3 sm:space-x-4 flex-1">
                    <div class="relative">
                      <img :src="match.home_team.logo_url" :alt="match.home_team.name"
                        class="w-12 h-12 sm:w-14 sm:h-14 rounded-full object-cover shadow-md" />
                    </div>
                    <div class="text-left">
                      <div class="font-semibold text-gray-800 text-base sm:text-lg">{{ match.home_team.name }}</div>
                      <div class="text-gray-500 text-xs sm:text-sm">Home</div>
                    </div>
                  </div>

                  <div class="flex-shrink-0 mx-2 sm:mx-4">
                    <div class="bg-orange-100 rounded-full p-2 sm:p-3">
                      <div class="text-orange-600 font-bold text-xs sm:text-sm">PP</div>
                    </div>
                  </div>

                  <div class="flex items-center space-x-3 sm:space-x-4 flex-1 justify-end">
                    <div class="text-right">
                      <div class="font-semibold text-gray-800 text-base sm:text-lg">{{ match.away_team.name }}</div>
                      <div class="text-gray-500 text-xs sm:text-sm">Away</div>
                    </div>
                    <div class="relative">
                      <img :src="match.away_team.logo_url" :alt="match.away_team.name"
                        class="w-12 h-12 sm:w-14 sm:h-14 rounded-full object-cover shadow-md" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="mt-8 flex justify-center items-center space-x-3 sm:space-x-4">
          <button @click="prevPage" :disabled="currentPage === 1"
            class="flex items-center space-x-2 px-4 py-2 bg-white text-gray-700 rounded-full border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            <span class="hidden sm:inline">Previous</span>
          </button>

          <div class="flex items-center space-x-2 text-sm">
            <span class="text-gray-600 hidden sm:inline">Page</span>
            <span class="bg-gray-600 text-white px-3 py-1 rounded-full font-bold">{{ currentPage }}</span>
            <span class="text-gray-600">of</span>
            <span class="text-gray-600 font-medium">{{ totalPages }}</span>
          </div>

          <button @click="nextPage" :disabled="currentPage === totalPages"
            class="flex items-center space-x-2 px-4 py-2 bg-white text-gray-700 rounded-full border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm">
            <span class="hidden sm:inline">Next</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <div v-else class="text-center py-16">
        <div class="max-w-md mx-auto">
          <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
          </svg>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">No Fixtures Available</h3>
          <p class="text-gray-500">Check back later for upcoming matches</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useKplStore } from '@/stores/kpl';

const kplStore = useKplStore();
const { fixtures } = storeToRefs(kplStore);
const isLoading = ref(false);
const activeTab = ref('upcoming');

watch(() => fixtures.value, (newFixtures) => {
  if (newFixtures.length === 0) {
    fetchFixtures();
  }
}, { immediate: true });

async function fetchFixtures() {
  try {
    isLoading.value = true;
    await kplStore.fetchFixtures(true);
  } catch (error) {
    console.error("Failed to fetch fixtures:", error);
  } finally {
    isLoading.value = false;
  }
}

const currentPage = ref(1);
const itemsPerPage = 5;

// Filter fixtures by status
const upcomingAndLiveFixtures = computed(() => {
  return fixtures.value.filter(fixture => 
    fixture.status === 'upcoming' || fixture.status === 'live'
  );
});

const finishedFixtures = computed(() => {
  return fixtures.value
    .filter(fixture => fixture.status === 'completed')
    .sort((a, b) => new Date(b.match_date).getTime() - new Date(a.match_date).getTime());
});

const postponedFixtures = computed(() => {
  return fixtures.value.filter(fixture => fixture.status === 'postponed');
});

// Current active fixtures based on tab
const currentFixtures = computed(() => {
  if (activeTab.value === 'upcoming') return upcomingAndLiveFixtures.value;
  if (activeTab.value === 'finished') return finishedFixtures.value;
  if (activeTab.value === 'postponed') return postponedFixtures.value;
  return [];
});

const totalPages = computed(() => Math.ceil(currentFixtures.value.length / itemsPerPage) || 1);

const paginatedUpcomingFixtures = computed(() => {
  if (activeTab.value !== 'upcoming' || upcomingAndLiveFixtures.value.length === 0) return [];
  const start = (currentPage.value - 1) * itemsPerPage;
  return upcomingAndLiveFixtures.value.slice(start, start + itemsPerPage);
});

const paginatedFinishedFixtures = computed(() => {
  if (activeTab.value !== 'finished' || finishedFixtures.value.length === 0) return [];
  const start = (currentPage.value - 1) * itemsPerPage;
  return finishedFixtures.value.slice(start, start + itemsPerPage);
});

const paginatedPostponedFixtures = computed(() => {
  if (activeTab.value !== 'postponed' || postponedFixtures.value.length === 0) return [];
  const start = (currentPage.value - 1) * itemsPerPage;
  return postponedFixtures.value.slice(start, start + itemsPerPage);
});

// Reset pagination when switching tabs
watch(activeTab, () => {
  currentPage.value = 1;
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

const formatDatePart = (dateStr:string) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric"
  }).format(date);
};

const formatTimePart = (dateStr:string) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true
  }).format(date);
};
</script>