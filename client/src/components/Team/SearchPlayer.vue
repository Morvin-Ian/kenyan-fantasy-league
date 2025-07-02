<template>
  <div v-if="showSearchModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-3xl p-4 sm:p-8 w-full max-w-5xl mx-4 shadow-2xl relative max-h-[90vh] flex flex-col">
      <button @click="$emit('close-modal')" class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 z-10">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      <div
        class="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl overflow-hidden border border-indigo-100 flex-grow overflow-y-auto">
        <!-- Header -->
        <div class="relative p-6 sm:p-8 bg-gradient-to-r from-blue-900 to-indigo-800 overflow-hidden">
          <div class="absolute inset-0 opacity-20">
            <svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M38.1,-65.3C46.1,-55.9,47.6,-39.5,53.8,-25.6C60,-11.7,70.8,-0.3,71.8,11.5C72.8,23.3,63.9,35.5,53.3,45.9C42.6,56.4,30.2,65.1,15.9,70.5C1.7,75.9,-14.4,78.1,-26.8,72.2C-39.3,66.4,-48.1,52.5,-57.5,38.8C-66.9,25.1,-76.8,11.6,-77.7,-2.8C-78.6,-17.2,-70.3,-32.4,-58.6,-42.4C-46.8,-52.4,-31.6,-57.2,-18.2,-64.7C-4.9,-72.2,6.7,-82.4,19.2,-80.8C31.8,-79.3,45.2,-66,54.6,-50.8C63.9,-35.7,73.1,-18.9,75.9,0.1C78.6,19.1,74.9,40.1,64.2,54.9C53.4,69.7,35.7,78.3,18.6,80.1C1.4,81.9,-15.1,77,-31.6,71.5C-48.1,66,-64.6,59.9,-75.4,48.2C-86.2,36.5,-91.3,19.2,-90.9,2.3C-90.6,-14.6,-84.7,-29.3,-76.4,-43C-68.1,-56.7,-57.4,-69.4,-43.8,-75.7C-30.3,-82,-15.1,-81.8,0,-81.8C15.2,-81.8,30.3,-82,38.1,-65.3Z"
                transform="translate(250 250)" />
            </svg>
          </div>
          <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold text-white relative z-10 flex flex-wrap items-center">
            <span class="mr-3 text-3xl sm:text-4xl">⚽</span> Fantasy Player Search
          </h1>
          <p class="text-blue-100 mt-2 max-w-2xl text-sm sm:text-base">Find and add the best players to your fantasy
            team.</p>
        </div>

        <!-- Search and Filters -->
        <div class="p-4 sm:p-6 md:p-8 bg-gradient-to-b from-blue-50 to-white border-b border-blue-100">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            <div class="relative group transform transition-all duration-300 hover:scale-105">
              <input v-model="filters.name" type="text" placeholder="Search by name"
                class="w-full pl-12 pr-4 py-3.5 rounded-xl border border-blue-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 shadow-sm group-hover:shadow-md" />
              <svg xmlns="http://www.w3.org/2000/svg"
                class="absolute left-4 top-3.5 h-6 w-6 text-blue-400 transition-all duration-300 group-hover:text-blue-600"
                fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <div class="relative group transform transition-all duration-300 hover:scale-105">
              <select v-model="filters.position"
                class="w-full py-3.5 pl-12 pr-4 rounded-xl border border-blue-200 focus:ring-2 focus:ring-blue-500 transition-all duration-300 shadow-sm group-hover:shadow-md appearance-none">
                <option value="">All Positions</option>
                <option value="GKP">Goalkeeper</option>
                <option value="DEF">Defender</option>
                <option value="MID">Midfielder</option>
                <option value="FWD">Striker</option>
              </select>
              <svg xmlns="http://www.w3.org/2000/svg"
                class="absolute left-4 top-3.5 h-6 w-6 text-blue-400 transition-all duration-300 group-hover:text-blue-600"
                fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
              </svg>
            </div>
            <div class="relative group transform transition-all duration-300 hover:scale-105">
              <select v-model="filters.team"
                class="w-full py-3.5 pl-12 pr-4 rounded-xl border border-blue-200 focus:ring-2 focus:ring-blue-500 transition-all duration-300 shadow-sm group-hover:shadow-md appearance-none">
                <option value="">All Teams</option>
                <option v-for="team in kplStore.teams" :key="team.id" :value="team.name">{{ team.name }}</option>
              </select>
              <svg xmlns="http://www.w3.org/2000/svg"
                class="absolute left-4 top-3.5 h-6 w-6 text-blue-400 transition-all duration-300 group-hover:text-blue-600"
                fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
              </svg>
            </div>
            <button @click="clearFilters"
              class="group bg-white hover:bg-red-50 border border-red-200 text-red-500 rounded-xl transition-all duration-300 flex items-center justify-center px-4 py-3.5 shadow-sm hover:shadow-md transform hover:scale-105">
              <svg xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 mr-2 group-hover:rotate-90 transition-all duration-500" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              Clear Filters
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex justify-center items-center p-16">
          <div class="relative w-24 h-24">
            <div class="absolute top-0 left-0 w-24 h-24 border-4 border-blue-200 rounded-full animate-ping"></div>
            <div
              class="absolute top-0 left-0 w-24 h-24 border-4 border-blue-500 rounded-full animate-spin border-t-transparent">
            </div>
            <div class="absolute inset-0 flex items-center justify-center text-blue-500">⚽</div>
          </div>
        </div>

        <!-- Player Table -->
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gradient-to-r from-blue-100 to-indigo-100">
              <tr>
                <th class="px-4 sm:px-6 md:px-8 py-4 text-left text-blue-800 font-semibold">Player</th>
                <th class="px-4 sm:px-6 md:px-8 py-4 text-left text-blue-800 font-semibold">Position</th>
                <th class="px-4 sm:px-6 md:px-8 py-4 text-left text-blue-800 font-semibold">Age</th>
                <th class="px-4 sm:px-6 md:px-8 py-4 text-left text-blue-800 font-semibold">Jersey</th>
                <th class="px-4 sm:px-6 md:px-8 py-4 text-left text-blue-800 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(player, index) in paginatedPlayers" :key="player.id"
                class="border-b hover:bg-blue-50 transition-all duration-300"
                :class="{ 'animate-fadeIn': showAnimation }" :style="{ animationDelay: `${index * 50}ms` }">
                <td class="px-4 sm:px-6 md:px-8 py-4">
                  <div class="flex items-center">
                    <div
                      class="flex-shrink-0 h-10 w-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold mr-3 shadow-md hidden sm:flex">
                      {{ player.name.charAt(0) }}
                    </div>
                    <div>
                      <div class="font-bold text-gray-900 text-sm sm:text-base">{{ player.name }}</div>
                      <div class="text-blue-600 text-xs sm:text-sm flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 sm:h-4 sm:w-4 mr-1" fill="none"
                          viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {{ player.team.name }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-4 sm:px-6 md:px-8 py-4">
                  <span class="px-2 sm:px-3 py-1 rounded-full text-xs font-semibold shadow-sm whitespace-nowrap" :class="{
                    'bg-yellow-100 text-yellow-800 border border-yellow-200': player.position === 'GKP',
                    'bg-blue-100 text-blue-800 border border-blue-200': player.position === 'DEF',
                    'bg-green-100 text-green-800 border border-green-200': player.position === 'MID',
                    'bg-red-100 text-red-800 border border-red-200': player.position === 'FWD',
                  }">
                    {{ getPositionName(player.position) }}
                  </span>
                </td>
                <td class="px-4 sm:px-6 md:px-8 py-4">{{ player.age ?? '-' }}</td>
                <td class="px-4 sm:px-6 md:px-8 py-4">
                  <span v-if="player.jersey_number"
                    class="inline-flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-800 rounded-full font-medium">{{
                      player.jersey_number }}</span>
                  <span v-else>-</span>
                </td>
                <td class="px-4 sm:px-6 md:px-8 py-4">
                  <button @click="selectPlayerForTransfer(player)"
                    class="px-3 sm:px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg transition-all duration-300 hover:shadow-lg hover:from-blue-600 hover:to-indigo-700 transform hover:-translate-y-1 flex items-center text-xs sm:text-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24"
                      stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Add
                  </button>
                </td>
              </tr>
              <tr v-if="paginatedPlayers.length === 0">
                <td colspan="6" class="text-center py-16 text-gray-500 bg-blue-50/50">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-blue-300 mb-4" fill="none"
                    viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p class="text-lg font-medium">No players found matching your criteria</p>
                  <button @click="clearFilters" class="text-blue-500 underline mt-2 hover:text-blue-700">Clear filters
                    and try again</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="!loading"
          class="flex flex-col sm:flex-row justify-between items-center p-4 sm:p-6 md:p-8 bg-gradient-to-b from-white to-blue-50 border-t border-blue-100">
          <div class="flex items-center mb-4 sm:mb-0">
            <div class="text-sm text-gray-500">
              Showing {{ paginatedPlayersStart }} to {{ paginatedPlayersEnd }} of {{ filteredPlayers.length }} players
            </div>
            <div class="ml-4 flex items-center">
              <label for="playersPerPage" class="text-sm text-gray-500 mr-2">Per page:</label>
              <select id="playersPerPage" v-model="playersPerPage" @change="currentPage = 1"
                class="bg-white border border-blue-200 text-gray-700 rounded-md py-1 px-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="15">15</option>
                <option value="20">20</option>
              </select>
            </div>
          </div>
          <div class="flex flex-wrap justify-center gap-2">
            <button @click="currentPage = 1" :disabled="currentPage === 1"
              class="w-10 h-10 flex items-center justify-center rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed text-blue-700"
              :class="currentPage === 1 ? 'bg-blue-50' : 'bg-blue-100 hover:bg-blue-200'">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
              <span class="sr-only">First Page</span>
            </button>
            <button @click="currentPage = currentPage - 1" :disabled="currentPage === 1"
              class="flex-shrink-0 h-10 px-3 sm:px-4 bg-blue-100 text-blue-700 rounded-lg transition-all duration-300 hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 sm:mr-1" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              <span class="hidden sm:inline">Prev</span>
            </button>
            <div class="flex space-x-1">
              <button v-for="page in displayedPages" :key="page" @click="currentPage = page"
                class="w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-300 text-sm"
                :class="currentPage === page ? 'bg-blue-600 text-white shadow-lg scale-110' : 'bg-blue-100 text-blue-700 hover:bg-blue-200'">
                {{ page }}
              </button>
            </div>
            <button @click="currentPage = currentPage + 1" :disabled="currentPage === totalPages"
              class="flex-shrink-0 h-10 px-3 sm:px-4 bg-blue-100 text-blue-700 rounded-lg transition-all duration-300 hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center">
              <span class="hidden sm:inline">Next</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 sm:ml-1" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
            <button @click="currentPage = totalPages" :disabled="currentPage === totalPages"
              class="w-10 h-10 flex items-center justify-center rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed text-blue-700"
              :class="currentPage === totalPages ? 'bg-blue-50' : 'bg-blue-100 hover:bg-blue-200'">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
              <span class="sr-only">Last Page</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from "vue";
import { useKplStore } from "@/stores/kpl";
import type { Player } from "@/helpers/types/team";
import { FantasyPlayer } from "@/helpers/types/fantasy";

const props = defineProps<{
  showSearchModal: boolean;
  selectedPlayer: FantasyPlayer | null;
}>();

const emit = defineEmits<{
  (e: 'close-modal'): void;
  (e: 'select-player', player: Player): void;
}>();

const kplStore = useKplStore();

watch(
  () => props.selectedPlayer,
  { immediate: true }
);

watch(
  () => [props.showSearchModal, props.selectedPlayer],
  ([isOpen, selectedPlayer]) => {
    if (isOpen && selectedPlayer) {
      filters.position = selectedPlayer.position || "";
      triggerAnimation();
    }
  },
  { immediate: true }
);

const filters = reactive({
  name: "",
  position: "",
  team: "",
});

type PositionKey = 'GKP' | 'DEF' | 'MID' | 'FWD';

const positionMap: Record<PositionKey, string> = {
  GKP: "Goalkeeper",
  DEF: "Defender",
  MID: "Midfielder",
  FWD: "Forward",
};

const getPositionName = (position: string): string => {
  const validPosition = position as PositionKey;
  return positionMap[validPosition] || position;
};

const showAnimation = ref(false);
const loading = ref(true);
const currentPage = ref(1);
const playersPerPage = ref(5);

const getPlayers = async () => {
  await kplStore.fetchPlayers();
};

if (kplStore.players.length === 0) {
  getPlayers();
}

const filteredPlayers = computed(() => {
  return (kplStore.players || []).filter((player) => {
    const matchesName = player.name.toLowerCase().includes(filters.name.toLowerCase());
    const matchesPosition = !filters.position || player.position === filters.position;
    const matchesTeam = !filters.team || player.team.name === filters.team;
    return matchesName && matchesPosition && matchesTeam;
  });
});

const totalPages = computed(() => Math.max(1, Math.ceil(filteredPlayers.value.length / playersPerPage.value)));

const paginatedPlayers = computed(() => {
  const start = (currentPage.value - 1) * playersPerPage.value;
  const end = start + playersPerPage.value;
  return filteredPlayers.value.slice(start, end);
});

const paginatedPlayersStart = computed(() => {
  if (filteredPlayers.value.length === 0) return 0;
  return (currentPage.value - 1) * playersPerPage.value + 1;
});

const paginatedPlayersEnd = computed(() => {
  return Math.min(currentPage.value * playersPerPage.value, filteredPlayers.value.length);
});

const displayedPages = computed(() => {
  const maxPagesToShow = window.innerWidth > 768 ? 5 : 3;
  let startPage = Math.max(1, currentPage.value - Math.floor(maxPagesToShow / 2));
  let endPage = Math.min(totalPages.value, startPage + maxPagesToShow - 1);
  if (endPage - startPage + 1 < maxPagesToShow) {
    startPage = Math.max(1, endPage - maxPagesToShow + 1);
  }
  const pages = [];
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  return pages;
});

const clearFilters = () => {
  filters.name = "";
  filters.position = props.selectedPlayer?.position || "";
  filters.team = "";
  currentPage.value = 1;
  triggerAnimation();
};

const selectPlayerForTransfer = (player: Player) => {
  emit('select-player', player);
};

const triggerAnimation = () => {
  showAnimation.value = false;
  setTimeout(() => {
    showAnimation.value = true;
  }, 50);
};

watch(
  () => [filters.name, filters.position, filters.team],
  () => {
    currentPage.value = 1;
    triggerAnimation();
  },
  { deep: true }
);

watch(filteredPlayers, () => {
  if (currentPage.value > totalPages.value && totalPages.value > 0) {
    currentPage.value = totalPages.value;
  }
});

watch(playersPerPage, () => {
  currentPage.value = 1;
  triggerAnimation();
});

onMounted(async () => {
  loading.value = true;
  if (kplStore.teams.length === 0) {
    await kplStore.fetchTeams();
  }

  loading.value = false;
  triggerAnimation();

  window.addEventListener('resize', () => {
    currentPage.value = currentPage.value;
  });
});
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.5s ease-out forwards;
  opacity: 0;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #93c5fd;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #60a5fa;
}

@media (max-width: 640px) {
  table {
    font-size: 0.75rem;
  }
}
</style>