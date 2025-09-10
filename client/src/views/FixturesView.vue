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
            <h2 class="text-2xl md:text-4xl font-black text-gray-600 flex items-center justify-center space-x-2 md:space-x-4"><span class="truncuate">Upcoming Fixtures</span></h2>
          </div>
          <div>
            <router-link to="/standings"
              class="inline-flex items-center bg-white text-gray-700 px-4 py-2 rounded-full hover:bg-gray-100 transition-colors duration-200 shadow-sm border border-gray-200 text-sm font-medium">
              <BarChart2Icon size="16" class="mr-2 text-gray-600" />
              View Table
            </router-link>
          </div>
        </div>
        <div class="space-y-4">
          <div v-for="match in paginatedFixtures" :key="match.id"
            class="bg-white rounded-2xl p-4 md:p-5 shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100 hover:border-gray-200">

            <div class="text-center mb-4">
              <div
                class="inline-flex items-center bg-gray-50 text-gray-700 px-3 py-1.5 rounded-full text-sm font-medium mb-2">
                <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                {{ formatDatePart(match.match_date) }}
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
                <div class="bg-gray-100 rounded-full p-2 sm:p-3">
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
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
          </svg>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">No Fixtures Available</h3>
          <p class="text-gray-500">Check back later for upcoming matches</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
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
  console.log(fixtures.value.length)
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
  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric"
  }).format(date);
};

const formatTimePart = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true
  }).format(date);
};
</script>
```