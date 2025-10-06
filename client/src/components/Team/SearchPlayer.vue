<template>
  <div v-if="showSearchModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-2xl p-2 sm:p-4 w-full max-w-4xl mx-2 shadow-lg relative max-h-[90vh] sm:max-h-[85vh] flex flex-col">
      <button @click="$emit('close-modal')" class="absolute top-4 right-4 sm:top-4 sm:right-4  text-red-500 hover:text-red-700 z-10 p-1">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      <div class="bg-white/95 backdrop-blur-sm rounded-2xl shadow-lg overflow-hidden border border-gray-200 flex-grow overflow-y-auto">
        <!-- Header -->
        <div class="relative p-2 sm:p-4 bg-gradient-to-r from-gray-700 to-gray-800 overflow-hidden">
          <div class="absolute inset-0 opacity-20">
            <svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M38.1,-65.3C46.1,-55.9,47.6,-39.5,53.8,-25.6C60,-11.7,70.8,-0.3,71.8,11.5C72.8,23.3,63.9,35.5,53.3,45.9C42.6,56.4,30.2,65.1,15.9,70.5C1.7,75.9,-14.4,78.1,-26.8,72.2C-39.3,66.4,-48.1,52.5,-57.5,38.8C-66.9,25.1,-76.8,11.6,-77.7,-2.8C-78.6,-17.2,-70.3,-32.4,-58.6,-42.4C-46.8,-52.4,-31.6,-57.2,-18.2,-64.7C-4.9,-72.2,6.7,-82.4,19.2,-80.8C31.8,-79.3,45.2,-66,54.6,-50.8C63.9,-35.7,73.1,-18.9,75.9,0.1C78.6,19.1,74.9,40.1,64.2,54.9C53.4,69.7,35.7,78.3,18.6,80.1C1.4,81.9,-15.1,77,-31.6,71.5C-48.1,66,-64.6,59.9,-75.4,48.2C-86.2,36.5,-91.3,19.2,-90.9,2.3C-90.6,-14.6,-84.7,-29.3,-76.4,-43C-68.1,-56.7,-57.4,-69.4,-43.8,-75.7C-30.3,-82,-15.1,-81.8,0,-81.8C15.2,-81.8,30.3,-82,38.1,-65.3Z"
                transform="translate(250 250)" />
            </svg>
          </div>
          <h1 class="text-base sm:text-xl font-semibold text-gray-100 relative z-10 my-3">Fantasy Player Search</h1>
          <p class="text-gray-300 mt-1 text-xs sm:text-sm hidden sm:block">Browse players to build your fantasy team.</p>
        </div>

        <!-- Search and Filters -->
        <div class="p-2 sm:p-4 bg-gradient-to-b from-gray-50 to-white border-b border-gray-200">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <div class="relative group transform transition-all duration-300 hover:scale-105">
              <input v-model="filters.name" type="text" placeholder="Search by name"
                class="w-full pl-6 sm:pl-8 pr-2 py-1.5 sm:py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-gray-400 shadow-sm group-hover:shadow-md text-xs sm:text-sm" />
              <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-2 top-2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400 group-hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <div class="relative group transform transition-all duration-300 hover:scale-105">
              <select v-model="filters.position" class="w-full py-1.5 sm:py-2 pl-6 sm:pl-8 pr-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-gray-400 shadow-sm group-hover:shadow-md appearance-none text-xs sm:text-sm">
                <option value="">All Positions</option>
                <option value="GKP">Goalkeeper</option>
                <option value="DEF">Defender</option>
                <option value="MID">Midfielder</option>
                <option value="FWD">Striker</option>
              </select>
              <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-2 top-2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400 group-hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
              </svg>
            </div>
            <div class="relative group transform transition-all duration-300 hover:scale-105">
              <select v-model="filters.team" class="w-full py-1.5 sm:py-2 pl-6 sm:pl-8 pr-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-gray-400 shadow-sm group-hover:shadow-md appearance-none text-xs sm:text-sm">
                <option value="">All Teams</option>
                <option v-for="team in kplStore.teams" :key="team.id" :value="team.name">{{ team.name }}</option>
              </select>
              <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-2 top-2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400 group-hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
              </svg>
            </div>
          </div>
          <button @click="clearFilters" class="mt-2 w-full bg-white hover:bg-gray-100 border border-gray-300 text-gray-600 rounded-lg transition-all duration-300 flex items-center justify-center px-2 py-1.5 shadow-sm hover:shadow-md transform hover:scale-105 text-xs sm:text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 sm:h-4 sm:w-4 group-hover:rotate-90 transition-all duration-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span class="ml-1">Clear Filters</span>
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex justify-center items-center p-4 sm:p-8">
          <div class="relative w-12 h-12 sm:w-16 sm:h-16">
            <div class="absolute top-0 left-0 w-full h-full border-2 sm:border-3 border-gray-200 rounded-full animate-ping"></div>
            <div class="absolute top-0 left-0 w-full h-full border-2 sm:border-3 border-gray-500 rounded-full animate-spin border-t-transparent"></div>
            <div class="absolute inset-0 flex items-center justify-center text-gray-500 text-base sm:text-lg">⚽</div>
          </div>
        </div>

        <!-- Player Table -->
        <div v-else class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead class="bg-gradient-to-r from-gray-100 to-gray-200">
              <tr>
                <th class="px-2 sm:px-4 py-2 text-left text-gray-700 font-semibold text-xs">Player</th>
                <th class="px-2 sm:px-4 py-2 text-left text-gray-700 font-semibold text-xs">Position</th>
                <th class="px-2 sm:px-4 py-2 text-left text-gray-700 font-semibold text-xs">Price</th>
                <th class="px-2 sm:px-4 py-2 text-left text-gray-700 font-semibold text-xs">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(player, index) in paginatedPlayers" :key="player.id" class="border-b hover:bg-gray-50 transition-all duration-300" :class="{ 'animate-fadeIn': showAnimation }" :style="{ animationDelay: `${index * 50}ms` }">
                <td class="px-2 sm:px-4 py-2">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-6 w-6 sm:h-8 sm:w-8 bg-gradient-to-br from-gray-500 to-gray-600 rounded-full flex items-center justify-center text-white font-bold mr-2 text-xs">
                      {{ player.name.charAt(0) }}
                    </div>
                    <div>
                      <div class="font-bold text-gray-900 text-xs sm:text-sm">{{ player.name }}</div>
                      <div class="text-gray-600 text-xs sm:flex items-center hidden">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5 sm:h-3 sm:w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        <span class="truncate max-w-[80px] sm:max-w-none">{{ player.team.name }}</span>
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-2 sm:px-4 py-2">
                  <span class="px-1.5 sm:px-2 py-0.5 rounded-full text-xs font-semibold shadow-sm whitespace-nowrap" :class="{
                    'bg-yellow-100 text-yellow-800 border border-yellow-200': player.position === 'GKP',
                    'bg-gray-100 text-gray-800 border border-gray-200': player.position === 'DEF',
                    'bg-green-100 text-green-800 border border-green-200': player.position === 'MID',
                    'bg-red-100 text-red-800 border border-red-200': player.position === 'FWD',
                  }">
                    {{ getPositionName(player.position) }}
                  </span>
                </td>
                <td class="px-2 sm:px-4 py-2">
                  <div class="flex items-center">
                    <span class="font-semibold text-gray-900 text-xs sm:text-sm">{{ parseFloat(player.current_value).toFixed(1) }}M</span>
                  </div>
                </td>
                <td class="px-2 sm:px-4 py-2">
                  <button @click="selectPlayerForTransfer(player)" class="px-2 sm:px-3 py-1 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-md transition-all duration-300 hover:shadow-lg hover:from-gray-600 hover:to-gray-700 transform hover:-translate-y-1 flex items-center text-xs">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 sm:h-4 sm:w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    <span class="hidden sm:inline">Add</span>
                  </button>
                </td>
              </tr>
              <tr v-if="paginatedPlayers.length === 0">
                <td colspan="4" class="text-center py-4 sm:py-8 text-gray-500 bg-gray-50/50">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 sm:h-12 sm:w-12 mx-auto text-gray-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p class="text-xs sm:text-sm font-medium">No players found</p>
                  <button @click="clearFilters" class="text-gray-500 underline mt-1 text-xs">Clear filters</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="!loading" class="flex flex-col sm:flex-row justify-between items-center p-2 sm:p-4 bg-gradient-to-b from-white to-gray-50 border-t border-gray-200">
          <div class="flex flex-col sm:flex-row items-center mb-2 sm:mb-0 space-y-2 sm:space-y-0 sm:space-x-3">
            <div class="text-xs text-gray-500">Showing {{ paginatedPlayersStart }} to {{ paginatedPlayersEnd }} of {{ filteredPlayers.length }}</div>
            <div class="flex items-center">
              <label for="playersPerPage" class="text-xs text-gray-500 mr-1 hidden sm:block">Per page:</label>
              <select id="playersPerPage" v-model="playersPerPage" @change="currentPage = 1" class="bg-white border border-gray-300 text-gray-700 rounded-md py-1 px-1 text-xs focus:outline-none focus:ring-2 focus:ring-gray-400">
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="15">15</option>
              </select>
            </div>
          </div>
          <div class="flex flex-wrap justify-center gap-1">
            <button @click="currentPage = 1" :disabled="currentPage === 1" class="w-6 h-6 sm:w-7 sm:h-7 flex items-center justify-center rounded-md transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700" :class="currentPage === 1 ? 'bg-gray-50' : 'bg-gray-100 hover:bg-gray-200'">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
              <span class="sr-only">First Page</span>
            </button>
            <button @click="currentPage = currentPage - 1" :disabled="currentPage === 1" class="w-6 h-6 sm:w-7 sm:h-7 bg-gray-100 text-gray-700 rounded-md transition-all duration-300 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-xs">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div class="flex space-x-1">
              <button v-for="page in displayedPages" :key="page" @click="currentPage = page" class="w-6 h-6 sm:w-7 sm:h-7 rounded-md flex items-center justify-center transition-all duration-300 text-xs" :class="currentPage === page ? 'bg-gray-600 text-white shadow-lg scale-110' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'">
                {{ page }}
              </button>
            </div>
            <button @click="currentPage = currentPage + 1" :disabled="currentPage === totalPages" class="w-6 h-6 sm:w-7 sm:h-7 bg-gray-100 text-gray-700 rounded-md transition-all duration-300 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-xs">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
            <button @click="currentPage = totalPages" :disabled="currentPage === totalPages" class="w-6 h-6 sm:w-7 sm:h-7 flex items-center justify-center rounded-md transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700" :class="currentPage === totalPages ? 'bg-gray-50' : 'bg-gray-100 hover:bg-gray-200'">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
import type { FantasyPlayer } from "@/helpers/types/fantasy";

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
  (newVal) => {
    if (newVal && newVal.isPlaceholder) {
    }
  },
  { immediate: true }
);

watch(
  () => [props.showSearchModal, props.selectedPlayer],
  ([isOpen, selectedPlayer]) => {
    if (isOpen && selectedPlayer) {
      filters.position = (selectedPlayer && typeof selectedPlayer === 'object' && 'position' in selectedPlayer)
        ? selectedPlayer.position
        : "";
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
  width: 4px;
  height: 4px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 8px;
}

::-webkit-scrollbar-thumb {
  background: #9ca3af;
  border-radius: 8px;
}

::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

@media (max-width: 640px) {
  table {
    font-size: 0.65rem;
  }
  
  .truncate {
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }
}
</style>