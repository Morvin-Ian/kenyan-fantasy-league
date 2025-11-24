<template>
  <div class="p-4 sm:p-6 md:p-8 mx-2 sm:mx-4">
    <div v-if="fantasyStore.userTeam && fantasyStore.userTeam.length > 0"
      class="max-w-7xl mx-auto mb-6 animate-fade-in">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 truncate">
            {{ fantasyStore.userTeam[0]?.name || 'My Team' }}
          </h1>
          <p class="text-gray-600 mt-1 text-sm sm:text-base">
            Manage your fantasy squad across different gameweeks
          </p>
        </div>

        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 w-full sm:w-auto">
          <div class="relative group">
            <div
              class="flex items-center gap-2 bg-white rounded-xl border border-gray-300 px-4 py-3 shadow-sm hover:shadow-md transition-all duration-200">
              <svg class="w-5 h-5 text-gray-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <select v-model="selectedGameweek" @change="handleGameweekChange"
                class="bg-transparent border-none focus:ring-0 text-sm font-semibold text-gray-700 cursor-pointer appearance-none pr-6">
                <option value="" disabled>Select Gameweek</option>
                <option v-for="gw in fantasyStore.availableGameweeks" :key="gw.number" :value="gw.number"
                  class="text-sm">
                  {{ gw.name }}
                </option>
              </select>
              <svg class="w-4 h-4 text-gray-400 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none"
                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <div v-if="fantasyStore.currentGameweek && currentGameweekInfo"
              class="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"
                  :class="{ 'bg-green-500': currentGameweekInfo.is_active }"></div>

                <span v-if="currentGameweekInfo.is_active"
                  class="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                  Active
                </span>
                <span v-else class="text-xs text-gray-500">
                  Past
                </span>
              </div>
            </div>

            <button @click="openChipSelector"
              class="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-black to-gray-600 hover:from-gray-700 hover:to-black text-white rounded-lg shadow-md transition-all duration-200 transform hover:scale-105">
              <span>Apply Chips</span>
              <span class="text-sm font-semibold hidden sm:inline">Power-Ups</span>
            </button>
          </div>
        </div>
      </div>

    </div>

    <div v-if="isInitializing || fantasyStore.isLoading" class="flex justify-center items-center min-h-64">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">
          {{ isInitializing ? 'Loading your team...' : 'Switching gameweek...' }}
        </p>
      </div>
    </div>

    <div v-else-if="fantasyStore.userTeam && fantasyStore.userTeam.length > 0"
      class="max-w-7xl mx-auto mb-4 animate-fade-in">

      <div v-if="hasEmptySlots" class="flex flex-col sm:flex-row gap-3 mb-6">
        <button @click="autoFillTeam" :disabled="isAutoFilling"
          class="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2">
          <svg v-if="isAutoFilling" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg"
            fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
            </path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span class="text-sm sm:text-base">{{ isAutoFilling ? 'Auto-Selecting...' : 'Auto-Select Players' }}</span>
        </button>

        <button @click="clearTeamSelections"
          class="flex-1 bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition transform hover:scale-105 flex items-center justify-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span class="text-sm sm:text-base">Clear Autoselection</span>
        </button>
      </div>

      <div v-else-if="fantasyStore.fantasyPlayers.length == 0" class="flex justify-center mb-6">
        <button @click="clearTeamSelections"
          class="bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition transform hover:scale-105 flex items-center justify-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span class="text-sm sm:text-base">Clear Autoselection</span>
        </button>
      </div>

      <div class="max-w-7xl mx-auto flex flex-col lg:flex-row gap-6">
        <div class="animate-fade-in w-full lg:w-2/3 relative team-card">
          <div class="relative">
            <div v-if="hasUnsavedChanges" class="absolute top-7 right-1 z-20 mx-4 lg:hidden">
              <button @click="saveTeamChanges" :disabled="isSaving"
                class="animate-slide-up bg-white hover:bg-white text-dark font-semibold text-sm py-1.5 px-3 rounded-full shadow-md flex items-center transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none">
                <svg v-if="isSaving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-dark"
                  xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                  </path>
                </svg>
                <span class="mr-1">{{ isSaving ? 'Saving...' : 'Save Changes' }}</span>
              </button>
            </div>
          </div>

          <Pitch :goalkeeper="goalkeeper" :defenders="defenders" :midfielders="midfielders" :forwards="forwards"
            :bench-players="benchPlayers" :switch-source="switchSource" :switch-active="switchActive"
            @player-click="handlePlayerClick" @formation-change="handleFormationChange" />

          <MessageAlert v-if="message.text" :type="message.type" :text="message.text" :dismissible="message.dismissible"
            :auto-dismiss="message.autoDismiss" @dismiss="clearMessage"
            class="absolute top-4 left-0 right-0 z-20 mx-4" />

          <div v-if="hasUnsavedChanges && canEditCurrentGameweek"
            class="hidden lg:block absolute bottom-4 right-4 z-10">
            <button @click="saveTeamChanges" :disabled="isSaving"
              class="animate-slide-up bg-white hover:bg-white text-dark font-bold py-2 px-6 rounded-full shadow-lg flex items-center transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none">
              <svg v-if="isSaving" class="animate-spin -ml-1 mr-2 h-5 w-5 text-dark" xmlns="http://www.w3.org/2000/svg"
                fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              <span class="mr-2">{{ isSaving ? 'Saving...' : 'Save Changes' }}</span>
            </button>
          </div>
        </div>

        <Sidebar :total-points="totalPoints" :average-points="averagePoints" :highest-points="highestPoints"
          :overall-rank="overallRank" :team="userTeamName" :in-bank="remainingBudget"
          :currentGameweek="fantasyStore.currentGameweek" />
      </div>
    </div>

    <!-- No Team State -->
    <div v-if="!fantasyStore.userTeam || fantasyStore.userTeam.length === 0"
      class="animate-fade-in max-w-3xl mx-auto text-center py-12 flex flex-col items-center justify-center min-h-[50vh]">
      <h2 class="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 mb-4">Build Your KPL Fantasy Team!</h2>
      <p class="text-sm sm:text-base text-gray-500 mb-6 max-w-md">Start your Kenyan Premier League fantasy journey by
        creating your team now.</p>
      <button @click="toggleModal"
        class="bg-gray-800 hover:bg-gray-900 text-white font-bold py-2 px-8 rounded-full shadow-lg transition transform hover:scale-105">Create
        Your Team</button>
    </div>

    <PlayerModal v-if="userTeam && userTeam.length" :show-modal="showModal" :selected-player="selectedPlayer"
      @close-modal="closeModal" @initiate-switch="initiateSwitch" @transfer-player="initiateTransfer"
      @make-captain="makeCaptain" @make-vice-captain="makeViceCaptain" />

    <SearchPlayer :show-search-modal="showSearchModal" :selectedPlayer="selectedPlayer" @close-modal="closeSearchModal"
      @select-player="handlePlayerTransfer" />

    <div v-if="showCreateTeamModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="animate-slide-up bg-white rounded-xl p-6 w-full max-w-md border border-gray-100 shadow-xl">

        <MessageAlert v-if="modalMessage.text" :type="modalMessage.type" :text="modalMessage.text"
          :dismissible="modalMessage.dismissible" @dismiss="clearModalMessage" class="mb-4" />

        <h3 class="text-xl sm:text-2xl font-bold text-gray-900 mb-4">Create Your KPL Team</h3>
        <form @submit.prevent="createTeam">
          <div class="mb-4">
            <label for="teamName" class="block text-gray-700 font-medium mb-2">Team Name</label>
            <input v-model="teamName" id="teamName" type="text"
              class="w-full p-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-gray-500"
              placeholder="Enter your team name" required />
          </div>
          <div class="mb-4">
            <label for="formation" class="block text-gray-700 font-medium mb-2">Select Formation</label>
            <select v-model="selectedFormation" id="formation"
              class="w-full p-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-gray-500"
              required>
              <option value="" disabled>Select a formation</option>
              <option value="3-4-3">3-4-3</option>
              <option value="4-4-2">4-4-2</option>
              <option value="4-3-3">4-3-3</option>
            </select>
          </div>

          <div class="flex justify-end gap-4">
            <button type="button" @click="showCreateTeamModal = false"
              class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded-lg transition transform hover:scale-105">Cancel</button>
            <button type="submit"
              class="bg-gray-800 hover:bg-gray-900 text-white font-medium py-2 px-4 rounded-lg transition transform hover:scale-105">Create
              Team</button>
          </div>
        </form>
      </div>
    </div>

    <ChipSelector :show="showChipSelector" :chips="fantasyStore.chips" @close="showChipSelector = false"
      @select="handleChipSelection" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, defineAsyncComponent } from "vue";
import memoizeOne from 'memoize-one';
import Pitch from "@/components/Team/Pitch.vue";
import Sidebar from "@/components/Team/SideBar.vue";
import MessageAlert from "@/components/common/MessageAlert.vue";
import ChipSelector from "@/components/Team/ChipSelector.vue";
import type { StartingEleven, TeamData, Player as KplPlayer } from "@/helpers/types/team";
import type { FantasyPlayer as Player, PositionSlot } from "@/helpers/types/fantasy";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import { useFantasyStore } from "@/stores/fantasy";
import { useKplStore } from "@/stores/kpl";
import defaultJersey from "@/assets/images/jerseys/default.png";
import goalkeeperJersey from "@/assets/images/jerseys/goalkeeper.png";

const selectedGameweek = ref<number | null>(null);
const isSwitchingGameweek = ref(false);

const userTeam = computed(() => fantasyStore.userTeam || []);
const currentGameweekInfo = computed(() => {
  if (!fantasyStore.currentGameweek) return null;
  return fantasyStore.availableGameweeks.find(gw => gw.number === fantasyStore.currentGameweek);
});

const canEditCurrentGameweek = computed(() => {
  return currentGameweekInfo.value?.is_active || false;
});

const remainingBudget = computed(() => {
  const teamValue = calculateTeamValue();
  return 70.0 - teamValue;
});

const calculateTeamValue = () => {
  if (!fantasyStore.fantasyPlayers.length) return 0;
  return fantasyStore.fantasyPlayers
    .filter(player => !player.id.startsWith('placeholder'))
    .reduce((total, player) => total + parseFloat(player.current_value || '0'), 0);
};

const handleGameweekChange = async () => {
  try {
    isSwitchingGameweek.value = true;
    showMessage(`Loading Gameweek ${selectedGameweek.value}...`, 'info');

    await fantasyStore.fetchFantasyTeamPlayers(selectedGameweek.value);
    await fantasyStore.fetchUserFantasyTeam(selectedGameweek.value)
    initializeTeamState();

    showMessage(`Gameweek ${selectedGameweek.value} loaded successfully!`, 'success', 3000);
  } catch (error) {
    console.error('Error switching gameweek:', error);
    showMessage('Failed to load gameweek data. Please try again.', 'error');
  } finally {
    isSwitchingGameweek.value = false;
  }
};

onMounted(async () => {
  try {
    authStore.initialize();
    if (!authStore.isAuthenticated) {
      router.push("/sign-in");
      return;
    }

    if (!fantasyStore.userTeam || !fantasyStore.userTeam.length) {
      await fantasyStore.fetchUserFantasyTeam();
    }

    if (fantasyStore.userTeam && fantasyStore.userTeam.length > 0) {
      await fantasyStore.fetchAvailableGameweeks();

      const currentGw = fantasyStore.availableGameweeks.find(gw => gw.is_active);
      selectedGameweek.value = currentGw?.number ||
        (fantasyStore.availableGameweeks[0]?.number || null);

      if (selectedGameweek.value) {
        await fantasyStore.fetchFantasyTeamPlayers(selectedGameweek.value);
        await fantasyStore.fetchUserFantasyTeam(selectedGameweek.value)
        initializeTeamState();
      }
    }
  } catch (error) {
    console.error("Error initializing team:", error);
    showMessage("Failed to load team data. Please refresh the page.", "error");
  } finally {
    isInitializing.value = false;
  }
});

const hasEmptySlots = computed(() => {
  if (!userTeam.value || userTeam.value.length === 0) return false;
  if (!canEditCurrentGameweek.value) return false; // Can't edit past gameweeks

  const hasPlaceholderGoalkeeper = startingElevenRef.value.goalkeeper?.id?.startsWith('placeholder');
  const hasPlaceholderDefenders = startingElevenRef.value.defenders.some(p => p.id.startsWith('placeholder'));
  const hasPlaceholderMidfielders = startingElevenRef.value.midfielders.some(p => p.id.startsWith('placeholder'));
  const hasPlaceholderForwards = startingElevenRef.value.forwards.some(p => p.id.startsWith('placeholder'));
  const hasPlaceholderBench = benchPlayersRef.value.some(p => p.id.startsWith('placeholder'));

  return hasPlaceholderGoalkeeper || hasPlaceholderDefenders || hasPlaceholderMidfielders || hasPlaceholderForwards || hasPlaceholderBench;
});

const PlayerModal = defineAsyncComponent(() => import('@/components/Team/PlayerModal.vue'));
const SearchPlayer = defineAsyncComponent(() => import('@/components/Team/SearchPlayer.vue'));

const authStore = useAuthStore();
const router = useRouter();
const fantasyStore = useFantasyStore();
const kplStore = useKplStore();


const showModal = ref(false);
const showSearchModal = ref(false);
const selectedPlayer = ref<Player | null>(null);
const switchActive = ref(false);
const switchSource = ref<Player | null>(null);
const isBenchSwitch = ref(false);
const showCreateTeamModal = ref(false);
const teamName = ref("");
const selectedFormation = ref("");
const hasUnsavedChanges = ref(false);
const isSaving = ref(false);
const isInitializing = ref(true);
const showChipSelector = ref(false);
const initialTeamState = ref<{
  startingEleven: StartingEleven;
  benchPlayers: Player[];
} | null>(null);

const message = ref({
  text: '',
  type: 'info',
  dismissible: true,
  autoDismiss: 0
});

const modalMessage = ref({
  text: '',
  type: 'info',
  dismissible: true,
  autoDismiss: 0
});

const clearMessage = () => {
  message.value = {
    text: '',
    type: 'info',
    dismissible: true,
    autoDismiss: 0
  };
};

const clearModalMessage = () => {
  modalMessage.value = {
    text: '',
    type: 'info',
    dismissible: true,
    autoDismiss: 0
  };
};

const showMessage = (text: string, type: 'error' | 'success' | 'warning' | 'info' = 'info', autoDismiss: number = 5000) => {
  message.value = {
    text,
    type,
    dismissible: true,
    autoDismiss
  };
};

const showModalMessage = (text: string, type: 'error' | 'success' | 'warning' | 'info' = 'info', autoDismiss: number = 5000) => {
  modalMessage.value = {
    text,
    type,
    dismissible: true,
    autoDismiss
  };
};

const startingElevenRef = ref<StartingEleven>({
  goalkeeper: {} as Player,
  defenders: [],
  midfielders: [],
  forwards: [],
});
const benchPlayersRef = ref<Player[]>([]);

const goalkeeper = computed(() => startingElevenRef.value.goalkeeper);
const defenders = computed(() => startingElevenRef.value.defenders);
const midfielders = computed(() => startingElevenRef.value.midfielders);
const forwards = computed(() => startingElevenRef.value.forwards);
const benchPlayers = computed(() => benchPlayersRef.value);
const currentFormation = ref(fantasyStore.userTeam[0]?.formation || "4-4-2");

const totalPoints = computed(() => (userTeam.value.length ? userTeam.value[0].total_points : 0));
const overallRank = computed(() => (userTeam.value.length ? userTeam.value[0].overall_rank : null));
const userTeamName = computed(() => (userTeam.value.length ? userTeam.value[0].name : null));
const averagePoints = ref(52);
const highestPoints = ref(121);

type FormationKey = "3-4-3" | "3-5-2" | "4-4-2" | "4-3-3" | "5-3-2" | "5-4-1" | "5-2-3";
type BenchComposition = { DEF: number; MID: number; FWD: number };
const isAutoFilling = ref(false);

const benchCompositions: Record<FormationKey, BenchComposition> = {
  "3-4-3": { DEF: 2, MID: 1, FWD: 0 },
  "3-5-2": { DEF: 2, MID: 0, FWD: 1 },
  "4-4-2": { DEF: 1, MID: 1, FWD: 1 },
  "4-3-3": { DEF: 1, MID: 2, FWD: 0 },
  "5-3-2": { DEF: 0, MID: 2, FWD: 1 },
  "5-2-3": { DEF: 0, MID: 3, FWD: 0 },
  "5-4-1": { DEF: 0, MID: 1, FWD: 2 },
};

const createPlaceholderPlayer = (position: string, index: number, isStarter: boolean = true): Player => ({
  id: `placeholder-${position.toLowerCase()}-${index}`,
  name: `Add ${position}`,
  position,
  team: "N/A",
  price: "0.00",
  fantasy_team: "",
  player: "",
  gameweek: 1,
  total_points: 0,
  gameweek_points: null,
  is_captain: false,
  is_vice_captain: false,
  is_starter: isStarter,
  purchase_price: "0.00",
  current_value: "0.00",
  jersey_image: position === "GKP" ? goalkeeperJersey : defaultJersey,
  isInjured: false,
  isPlaceholder: true,
});

const toggleModal = () => {
  showCreateTeamModal.value = !showCreateTeamModal.value;
  clearModalMessage();
};

const closeSearchModal = () => {
  showSearchModal.value = false;
  closeModal();
};

function initializeTeamState() {
  let players: Player[] = [];

  if (Array.isArray(fantasyStore.fantasyPlayers)) {
    players = fantasyStore.fantasyPlayers.map(p => ({ ...p }));
  } else if (fantasyStore.fantasyPlayers && typeof fantasyStore.fantasyPlayers === 'object') {
    console.error('fantasyPlayers is not an array:', fantasyStore.fantasyPlayers);
    players = [];
  }

  const rawFormation = selectedFormation.value || fantasyStore.userTeam[0]?.formation || "4-4-2";
  const formationString = (Object.keys(benchCompositions).includes(rawFormation)
    ? rawFormation
    : "4-4-2") as FormationKey;

  const [def, mid, fwd] = formationString.split("-").map(Number);
  const desiredBench = benchCompositions[formationString];

  const requiredBenchPlayers = 4;

  startingElevenRef.value = {
    goalkeeper: {} as Player,
    defenders: [],
    midfielders: [],
    forwards: [],
  };

  benchPlayersRef.value = [];

  players.forEach((player: Player) => {
    const fullPlayer = { ...player };

    if (player.is_starter) {
      if (player.position === "GKP") startingElevenRef.value.goalkeeper = fullPlayer;
      else if (player.position === "DEF") startingElevenRef.value.defenders.push(fullPlayer);
      else if (player.position === "MID") startingElevenRef.value.midfielders.push(fullPlayer);
      else if (player.position === "FWD") startingElevenRef.value.forwards.push(fullPlayer);
    } else {
      benchPlayersRef.value.push(fullPlayer);
    }
  });

  if (!startingElevenRef.value.goalkeeper.id || startingElevenRef.value.goalkeeper.id.startsWith("placeholder")) {
    startingElevenRef.value.goalkeeper = createPlaceholderPlayer("GKP", 0);
  }
  while (startingElevenRef.value.defenders.length < def) {
    startingElevenRef.value.defenders.push(createPlaceholderPlayer("DEF", startingElevenRef.value.defenders.length));
  }
  while (startingElevenRef.value.midfielders.length < mid) {
    startingElevenRef.value.midfielders.push(createPlaceholderPlayer("MID", startingElevenRef.value.midfielders.length));
  }
  while (startingElevenRef.value.forwards.length < fwd) {
    startingElevenRef.value.forwards.push(createPlaceholderPlayer("FWD", startingElevenRef.value.forwards.length));
  }

  const hasGoalkeeperOnBench = benchPlayersRef.value.some(p => p.position === "GKP");
  if (!hasGoalkeeperOnBench) {
    benchPlayersRef.value.push(createPlaceholderPlayer("GKP", 0, false));
  }

  const benchCounts = benchPlayersRef.value.reduce((accumulator, player) => {
    accumulator[player.position] = (accumulator[player.position] || 0) + 1;
    return accumulator;
  }, {
    GKP: 0,
    DEF: 0,
    MID: 0,
    FWD: 0
  } as Record<string, number>);


  let benchIndex = benchPlayersRef.value.length;

  const positionsToAdd = [
    { position: "DEF", count: Math.max(0, desiredBench.DEF - (benchCounts.DEF || 0)) },
    { position: "MID", count: Math.max(0, desiredBench.MID - (benchCounts.MID || 0)) },
    { position: "FWD", count: Math.max(0, desiredBench.FWD - (benchCounts.FWD || 0)) },
  ];

  positionsToAdd.forEach(({ position, count }) => {
    for (let i = 0; i < count; i++) {
      if (benchPlayersRef.value.length < requiredBenchPlayers) {
        benchPlayersRef.value.push(createPlaceholderPlayer(position, benchIndex++, false));
      }
    }
  });

  while (benchPlayersRef.value.length < requiredBenchPlayers) {
    benchPlayersRef.value.push(createPlaceholderPlayer("MID", benchIndex++, false));
  }

  initialTeamState.value = {
    startingEleven: JSON.parse(JSON.stringify(startingElevenRef.value)),
    benchPlayers: JSON.parse(JSON.stringify(benchPlayersRef.value)),
  };
  hasUnsavedChanges.value = false;
}

const areTeamsEqual = memoizeOne((state1, state2) => {
  const comparePlayers = (p1: Player, p2: Player) => p1.id === p2.id && p1.is_captain === p2.is_captain && p1.is_vice_captain === p2.is_vice_captain && p1.is_starter === p2.is_starter;
  const comparePlayerArrays = (arr1: Player[], arr2: Player[]) => arr1.length === arr2.length && arr1.every((p1, i) => comparePlayers(p1, arr2[i]));

  return (
    comparePlayers(state1.startingEleven.goalkeeper, state2.startingEleven.goalkeeper) &&
    comparePlayerArrays(state1.startingEleven.defenders, state2.startingEleven.defenders) &&
    comparePlayerArrays(state1.startingEleven.midfielders, state2.startingEleven.midfielders) &&
    comparePlayerArrays(state1.startingEleven.forwards, state2.startingEleven.forwards) &&
    comparePlayerArrays(state1.benchPlayers, state2.benchPlayers)
  );
});

watch(
  () => ({
    goalkeeper: startingElevenRef.value.goalkeeper.id,
    defenders: startingElevenRef.value.defenders.map(p => p.id),
    midfielders: startingElevenRef.value.midfielders.map(p => p.id),
    forwards: startingElevenRef.value.forwards.map(p => p.id),
    bench: benchPlayersRef.value.map(p => p.id),
  }),
  (newState, oldState) => {
    if (initialTeamState.value) {
      hasUnsavedChanges.value = !areTeamsEqual(initialTeamState.value, {
        startingEleven: startingElevenRef.value,
        benchPlayers: benchPlayersRef.value,
      });
    }
  },
  { deep: true }
);

const openPlayerModal = (player: Player) => {
  if (!player.id.startsWith("placeholder")) {
    selectedPlayer.value = player;
    showModal.value = true;
  } else {
    selectedPlayer.value = player;
    showSearchModal.value = true;
  }
};

const closeModal = () => {
  showModal.value = false;
  selectedPlayer.value = null;
};

const handlePlayerClick = (player: Player) => {
  if (switchActive.value) {
    performSwitch(player);
  } else {
    openPlayerModal(player);
  }
};

const handleFormationChange = (newFormation: string) => {
  currentFormation.value = newFormation;
  hasUnsavedChanges.value = true;
};

const initiateTransfer = (player: Player | null | undefined) => {
  if (player === null || player === undefined) {
    showMessage("Please select a player to transfer.", "info");
    return;
  }

  if (player.id.startsWith("placeholder")) {

    return;
  }
  selectedPlayer.value = player;
  showSearchModal.value = true;
};

const handlePlayerTransfer = async (newPlayer: KplPlayer) => {
  if (!selectedPlayer.value) {
    showMessage("Please select a player to transfer.", "info");
    return;
  }

  const oldPlayer = selectedPlayer.value;

  if (oldPlayer.position !== newPlayer.position && !isValidFormationChange(oldPlayer, newPlayer)) {
    showMessage("Invalid transfer: Formation constraints not met (min 3 DEF, 3 MID, 1 FWD).", "error");
    closeSearchModal();
    return;
  }

  const sameTeamPlayers = [
    ...startingElevenRef.value.defenders,
    ...startingElevenRef.value.midfielders,
    ...startingElevenRef.value.forwards,
    startingElevenRef.value.goalkeeper,
    ...benchPlayersRef.value,
  ].filter((p) => p.team === newPlayer.team.name && p.id !== oldPlayer.id && !p.id.startsWith("placeholder"));
  if (sameTeamPlayers.length >= 3) {
    showMessage("Cannot select more than 3 players from the same team.", "error");
    closeSearchModal();
    return;
  }

  if (isPlayerInTeam(newPlayer)) {
    showMessage("This player is already in your team.", "error");
    closeSearchModal();
    return;
  }

  if (isPlayerInStartingEleven(oldPlayer)) {
    replaceStartingWithNewPlayer(oldPlayer, newPlayer);
  } else {
    replaceBenchWithNewPlayer(oldPlayer, newPlayer);
  }

  hasUnsavedChanges.value = true;
  closeSearchModal();
};

const replaceStartingWithNewPlayer = (oldPlayer: Player, newPlayer: KplPlayer) => {
  const newFantasyPlayer: Player = {
    id: newPlayer.id,
    name: newPlayer.name,
    position: newPlayer.position,
    team: newPlayer.team.name,
    jersey_image: newPlayer.team.jersey_image || (newPlayer.position === "GKP" ? goalkeeperJersey : defaultJersey),
    price: oldPlayer.price,
    fantasy_team: fantasyStore.userTeam[0].id,
    player: newPlayer.id,
    gameweek: oldPlayer.gameweek,
    total_points: 0,
    gameweek_points: null,
    is_captain: oldPlayer.is_captain,
    is_vice_captain: oldPlayer.is_vice_captain,
    is_starter: true,
    purchase_price: oldPlayer.purchase_price,
    current_value: oldPlayer.current_value,
    isInjured: false,
    isPlaceholder: false,
  };

  if (oldPlayer.position === "GKP" && newPlayer.position === "GKP") {
    startingElevenRef.value.goalkeeper = newFantasyPlayer;
  } else {
    const positionMapping: Record<string, keyof StartingEleven> = {
      DEF: "defenders",
      MID: "midfielders",
      FWD: "forwards",
    };
    const positionKey = positionMapping[oldPlayer.position];
    if (positionKey) {
      const players = startingElevenRef.value[positionKey] as Player[];
      const index = players.findIndex((p) => p.id === oldPlayer.id);
      if (index !== -1) {
        players.splice(index, 1, newFantasyPlayer);
      }
    }
  }

  const benchIndex = benchPlayersRef.value.findIndex((p) => p.id.startsWith("placeholder") && p.position === newPlayer.position);
  if (benchIndex !== -1) {
    benchPlayersRef.value.splice(benchIndex, 1, createPlaceholderPlayer(newPlayer.position, benchIndex, false));
  }
};

const replaceBenchWithNewPlayer = (oldPlayer: Player, newPlayer: KplPlayer) => {
  const index = benchPlayersRef.value.findIndex((p) => p.id === oldPlayer.id);
  if (index !== -1) {
    const newFantasyPlayer: Player = {
      id: newPlayer.id,
      name: newPlayer.name,
      position: newPlayer.position,
      team: newPlayer.team.name,
      jersey_image: newPlayer.team.jersey_image || (newPlayer.position === "GKP" ? goalkeeperJersey : defaultJersey),
      price: oldPlayer.price,
      fantasy_team: fantasyStore.userTeam[0].id,
      player: newPlayer.id,
      gameweek: oldPlayer.gameweek,
      total_points: 0,
      gameweek_points: null,
      is_captain: false,
      is_vice_captain: false,
      is_starter: false,
      purchase_price: oldPlayer.purchase_price,
      current_value: oldPlayer.current_value,
      isInjured: false,
      isPlaceholder: false,
    };
    benchPlayersRef.value.splice(index, 1, newFantasyPlayer);
  }

  const benchComposition = {
    GKP: 1,
    DEF: 1,
    MID: 1,
    FWD: 1,
  };
  const benchPositionCounts = benchPlayersRef.value.reduce(
    (acc, player) => {
      if (!player.id.startsWith("placeholder")) {
        acc[player.position] = (acc[player.position] || 0) + 1;
      }
      return acc;
    },
    { GKP: 0, DEF: 0, MID: 0, FWD: 0 } as Record<string, number>
  );

  const missingPosition = Object.keys(benchComposition).find(
    (pos) => benchPositionCounts[pos] < benchComposition[pos as keyof typeof benchComposition] && pos !== newPlayer.position
  );

  if (missingPosition) {
    const placeholderIndex = benchPlayersRef.value.findIndex((p) => p.id.startsWith("placeholder") && p.position === missingPosition);
    if (placeholderIndex !== -1) {
      benchPlayersRef.value.splice(placeholderIndex, 1, createPlaceholderPlayer(missingPosition, placeholderIndex, false));
    }
  }
};

const initiateSwitch = (player: Player | null | undefined) => {
  if (player === null || player === undefined) {
    showMessage("Please select a player to switch.", "info");
    return;
  }

  if (player.id.startsWith("placeholder")) {
    showMessage("Cannot initiate switch with a non-existent player.", "info");
    return;
  }
  if (!selectedPlayer.value) {
    selectedPlayer.value = player;
  }
  switchSource.value = selectedPlayer.value;
  switchActive.value = true;
  isBenchSwitch.value = benchPlayers.value.some((p) => p.id === selectedPlayer.value?.id);
  closeModal();
};

function performSwitch(targetPlayer: Player) {
  if (!switchSource.value) return;
  const sourcePlayer = switchSource.value;

  if (targetPlayer.id.startsWith("placeholder")) {
    showMessage("Cannot switch with a placeholder player. Please select a valid player.", "error");
    resetSwitchState();
    return;
  }

  if (sourcePlayer.position !== targetPlayer.position) {
    if (!isValidFormationChange(sourcePlayer, targetPlayer)) {
      showMessage("Invalid formation change. Must have at least 3 defenders, 3 midfielders, and 1 forward.", "error");
      resetSwitchState();
      return;
    }
  }
  if (isPlayerInStartingEleven(sourcePlayer) && isPlayerInStartingEleven(targetPlayer)) {
    swapPlayersInStartingEleven(sourcePlayer, targetPlayer);
  } else if (isPlayerInStartingEleven(sourcePlayer) && !isPlayerInStartingEleven(targetPlayer)) {
    movePlayerFromStartingToBench(sourcePlayer, targetPlayer);
  } else if (!isPlayerInStartingEleven(sourcePlayer) && isPlayerInStartingEleven(targetPlayer)) {
    movePlayerFromStartingToBench(targetPlayer, sourcePlayer);
  } else {
    swapBenchPlayers(sourcePlayer, targetPlayer);
  }
  resetSwitchState();
  hasUnsavedChanges.value = true;
  // showMessage("Players switched successfully!", "success");
}

const saveTeamChanges = async () => {
  try {
    isSaving.value = true;

    const teamData: TeamData = {
      formation: currentFormation.value,
      startingEleven: {
        goalkeeper: startingElevenRef.value.goalkeeper.id.startsWith("placeholder") ? null : startingElevenRef.value.goalkeeper,
        defenders: startingElevenRef.value.defenders.filter((p) => !p.id.startsWith("placeholder")),
        midfielders: startingElevenRef.value.midfielders.filter((p) => !p.id.startsWith("placeholder")),
        forwards: startingElevenRef.value.forwards.filter((p) => !p.id.startsWith("placeholder")),
      },
      benchPlayers: benchPlayersRef.value.filter((p) => !p.id.startsWith("placeholder")),
    };

    const response = await fantasyStore.saveFantasyTeamPlayers(teamData);

    if (response && response.status === 200) {
      await fantasyStore.fetchUserFantasyTeam();
      await fantasyStore.fetchFantasyTeamPlayers();
      initializeTeamState();
      hasUnsavedChanges.value = false;
      showMessage("Team changes saved successfully!", "success");
    } else {
      showMessage(fantasyStore.error || "Failed to save team changes.", "error");
    }
  } catch (error) {
    showMessage("Failed to save team changes. Please try again.", "error");
  } finally {
    isSaving.value = false;
  }
};

async function createTeam() {
  try {
    if (!teamName.value.trim()) {
      showModalMessage("Please enter a valid team name.", "error");
      return;
    }
    if (!selectedFormation.value) {
      showModalMessage("Please select a formation.", "error");
      return;
    }

    const response = await fantasyStore.createFantasyTeam(
      teamName.value,
      selectedFormation.value
    );

    if (response && (response.status === 200 || response.status === 201)) {
      toggleModal();
      teamName.value = "";
      selectedFormation.value = "";

      await fantasyStore.fetchUserFantasyTeam();
      await fantasyStore.fetchFantasyTeamPlayers();
      initializeTeamState();

      showMessage("Team created successfully!", "success");
    } else {
      const message = fantasyStore.error || "Failed to create team.";
      showModalMessage(message, "error");
    }
  } catch (error) {
    console.error(error);
    showModalMessage("Failed to create team. Please try again.", "error");
  }
}


function isValidFormationChange(sourcePlayer: Player, targetPlayer: Player | KplPlayer): boolean {
  if (sourcePlayer.position === targetPlayer.position) return true;
  let defCount = countPlayersInPosition("DEF");
  let midCount = countPlayersInPosition("MID");
  let fwdCount = countPlayersInPosition("FWD");
  if (isPlayerInStartingEleven(sourcePlayer)) {
    if (sourcePlayer.position === "DEF") defCount--;
    else if (sourcePlayer.position === "MID") midCount--;
    else if (sourcePlayer.position === "FWD") fwdCount--;
  }
  if (!isPlayerInStartingEleven(targetPlayer)) {
    if (targetPlayer.position === "DEF") defCount++;
    else if (targetPlayer.position === "MID") midCount++;
    else if (targetPlayer.position === "FWD") fwdCount++;
  }
  return (
    defCount >= 3 &&
    midCount >= 3 &&
    fwdCount >= 1 &&
    defCount + midCount + fwdCount + 1 === 11
  );
}

function countPlayersInPosition(position: string): number {
  let count = 0;
  if (position === "GKP" && startingElevenRef.value.goalkeeper.position === "GKP" && !startingElevenRef.value.goalkeeper.id.startsWith("placeholder")) {
    count = 1;
  } else {
    const positionMapping: Record<string, keyof StartingEleven> = {
      DEF: "defenders",
      MID: "midfielders",
      FWD: "forwards",
    };
    const positionKey = positionMapping[position];
    if (positionKey) {
      count = (startingElevenRef.value[positionKey] as Player[]).filter((p) => !p.id.startsWith("placeholder")).length;
    }
  }
  return count;
}

function movePlayerFromStartingToBench(startingPlayer: Player, benchPlayer: Player) {
  const startingPosition = startingPlayer.position;
  const benchPosition = benchPlayer.position;
  if (startingPosition === benchPosition) {
    replaceStartingWithBenchPlayer(startingPlayer, benchPlayer);
    return;
  }
  removePlayerFromStartingEleven(startingPlayer);
  addPlayerToStartingEleven(benchPlayer);
  const benchIndex = benchPlayersRef.value.findIndex((p) => p.id === benchPlayer.id);
  benchPlayersRef.value[benchIndex] = {
    ...startingPlayer,
    is_captain: false,
    is_vice_captain: false,
    is_starter: false,
  };
}

function removePlayerFromStartingEleven(player: Player) {
  if (player.position === "GKP") return;
  const positionMapping: Record<string, keyof StartingEleven> = {
    DEF: "defenders",
    MID: "midfielders",
    FWD: "forwards",
  };
  const positionKey = positionMapping[player.position];
  if (positionKey) {
    const players = startingElevenRef.value[positionKey] as Player[];
    const index = players.findIndex((p) => p.id === player.id);
    if (index !== -1) {
      players.splice(index, 1);
    }
  }
}

function addPlayerToStartingEleven(player: Player) {
  if (player.position === "GKP") {
    startingElevenRef.value.goalkeeper = { ...player, is_starter: true };
    return;
  }
  const positionMapping: Record<string, keyof StartingEleven> = {
    DEF: "defenders",
    MID: "midfielders",
    FWD: "forwards",
  };
  const positionKey = positionMapping[player.position];
  if (positionKey) {
    const players = startingElevenRef.value[positionKey] as Player[];
    players.push({ ...player, is_starter: true });
  }
}

function replaceStartingWithBenchPlayer(startingPlayer: Player, benchPlayer: Player) {
  if (startingPlayer.position === "GKP" && benchPlayer.position === "GKP") {
    const tempGoalkeeper = { ...startingElevenRef.value.goalkeeper };
    startingElevenRef.value.goalkeeper = { ...benchPlayer, is_starter: true };
    const benchIndex = benchPlayersRef.value.findIndex((p) => p.id === benchPlayer.id);
    benchPlayersRef.value[benchIndex] = {
      ...tempGoalkeeper,
      is_captain: false,
      is_vice_captain: false,
      is_starter: false,
    };
    return;
  }
  const positionMapping: Record<string, keyof StartingEleven> = {
    DEF: "defenders",
    MID: "midfielders",
    FWD: "forwards",
  };
  const positionKey = positionMapping[startingPlayer.position];
  if (positionKey) {
    const players = startingElevenRef.value[positionKey] as Player[];
    const index = players.findIndex((p) => p.id === startingPlayer.id);
    if (index !== -1) {
      const is_captain = players[index].is_captain;
      const is_vice_captain = players[index].is_vice_captain;
      players[index] = { ...benchPlayer, is_captain, is_vice_captain, is_starter: true };
      const benchIndex = benchPlayersRef.value.findIndex((p) => p.id === benchPlayer.id);
      benchPlayersRef.value[benchIndex] = {
        ...startingPlayer,
        is_captain: false,
        is_vice_captain: false,
        is_starter: false,
      };
    }
  }
}

function swapPlayersInStartingEleven(player1: Player, player2: Player) {
  if (player1.position === player2.position) {
    const positionMapping: Record<string, keyof StartingEleven> = {
      GKP: "goalkeeper",
      DEF: "defenders",
      MID: "midfielders",
      FWD: "forwards",
    };
    const positionKey = positionMapping[player1.position];
    if (positionKey === "goalkeeper") return;
    if (positionKey) {
      const players = startingElevenRef.value[positionKey] as Player[];
      const index1 = players.findIndex((p) => p.id === player1.id);
      const index2 = players.findIndex((p) => p.id === player2.id);
      if (index1 !== -1 && index2 !== -1) {
        [players[index1], players[index2]] = [players[index2], players[index1]];
      }
    }
  } else {
    const is_captain1 = player1.is_captain;
    const is_vice_captain1 = player1.is_vice_captain;
    const is_captain2 = player2.is_captain;
    const is_vice_captain2 = player2.is_vice_captain;
    removePlayerFromStartingEleven(player1);
    removePlayerFromStartingEleven(player2);
    addPlayerToStartingEleven({
      ...player1,
      position: player2.position,
      is_captain: is_captain2,
      is_vice_captain: is_vice_captain2,
      is_starter: true,
    });
    addPlayerToStartingEleven({
      ...player2,
      position: player1.position,
      is_captain: is_captain1,
      is_vice_captain: is_vice_captain1,
      is_starter: true,
    });
  }
}

function swapBenchPlayers(player1: Player, player2: Player) {
  const index1 = benchPlayersRef.value.findIndex((p) => p.id === player1.id);
  const index2 = benchPlayersRef.value.findIndex((p) => p.id === player2.id);
  if (index1 !== -1 && index2 !== -1) {
    [benchPlayersRef.value[index1], benchPlayersRef.value[index2]] = [
      benchPlayersRef.value[index2],
      benchPlayersRef.value[index1],
    ];
  }
}

function resetSwitchState() {
  switchSource.value = null;
  switchActive.value = false;
  isBenchSwitch.value = false;
  selectedPlayer.value = null;
}

const isPlayerInStartingEleven = (player: Player | KplPlayer) => {
  if (!player) return false;
  if (startingElevenRef.value.goalkeeper.id === player.id) return true;
  return ["defenders", "midfielders", "forwards"].some((position) => {
    const players = startingElevenRef.value[position as keyof StartingEleven] as Player[];
    return players.some((p) => p.id === player.id);
  });
};

const isPlayerInTeam = (player: Player | KplPlayer) => {
  return (
    startingElevenRef.value.goalkeeper.id === player.id ||
    startingElevenRef.value.defenders.some((p) => p.id === player.id) ||
    startingElevenRef.value.midfielders.some((p) => p.id === player.id) ||
    startingElevenRef.value.forwards.some((p) => p.id === player.id) ||
    benchPlayersRef.value.some((p) => p.id === player.id)
  );
};

const clearCaptaincy = () => {
  startingElevenRef.value.goalkeeper.is_captain = false;
  ["defenders", "midfielders", "forwards"].forEach((position) => {
    const players = startingElevenRef.value[position as keyof StartingEleven] as Player[];
    players.forEach((player: Player) => {
      player.is_captain = false;
    });
  });
};

const clearViceCaptaincy = () => {
  startingElevenRef.value.goalkeeper.is_vice_captain = false;
  ["defenders", "midfielders", "forwards"].forEach((position) => {
    const players = startingElevenRef.value[position as keyof StartingEleven] as Player[];
    players.forEach((player: Player) => {
      player.is_vice_captain = false;
    });
  });
};

const makeCaptain = () => {
  if (!selectedPlayer.value) {
    showMessage("No player selected to be captain.", "info");

    return;
  }
  if (!isPlayerInStartingEleven(selectedPlayer.value)) {
    showMessage("Captain must be a starting player.", "info");
    return;
  }
  if (selectedPlayer.value.is_captain) {
    showMessage("Player is already captain.", "info");
    return;
  }
  clearCaptaincy();
  selectedPlayer.value.is_captain = true;
  closeModal();
  hasUnsavedChanges.value = true;
};

const makeViceCaptain = () => {
  if (!selectedPlayer.value) {
    showMessage("No player selected to be vice-captain.", "info");
    return;
  }
  if (!isPlayerInStartingEleven(selectedPlayer.value)) {
    showMessage("Vice-captain must be a starting player.", "info");
    return;
  }
  if (selectedPlayer.value.is_vice_captain) {
    showMessage("Player is already vice-captain.", "info");
    return;
  }
  clearViceCaptaincy();
  selectedPlayer.value.is_vice_captain = true;
  closeModal();
  hasUnsavedChanges.value = true;
};

const autoFillTeam = async () => {
  try {
    isAutoFilling.value = true;
    const maxPrice = 70.0;

    const availablePlayers = await kplStore.players;

    if (!availablePlayers || availablePlayers.length === 0) {
      showMessage("No players available to auto-fill team.", "error");
      return;
    }

    // Get current player IDs to avoid duplicates
    const currentPlayerIds = [
      startingElevenRef.value.goalkeeper?.id,
      ...startingElevenRef.value.defenders.map(p => p.id),
      ...startingElevenRef.value.midfielders.map(p => p.id),
      ...startingElevenRef.value.forwards.map(p => p.id),
      ...benchPlayersRef.value.map(p => p.id)
    ].filter(id => !id?.startsWith('placeholder'));

    // Filter eligible players and shuffle them
    const eligiblePlayers = availablePlayers.filter((player: KplPlayer) => {
      const price = parseFloat(player.current_value || '0');
      return price <= maxPrice && !currentPlayerIds.includes(player.id);
    });

    // Shuffle function to randomize player selection
    const shufflePlayers = <T>(players: T[]): T[] => {
      const shuffled = [...players];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      return shuffled;
    };

    // Track team counts for validation
    const teamCounts: Record<string, number> = {};
    [...startingElevenRef.value.defenders, ...startingElevenRef.value.midfielders, ...startingElevenRef.value.forwards, startingElevenRef.value.goalkeeper, ...benchPlayersRef.value]
      .filter(p => !p.id.startsWith('placeholder'))
      .forEach(p => {
        const teamName = typeof p.team === 'object' ? p.team.name : p.team;
        teamCounts[teamName] = (teamCounts[teamName] || 0) + 1;
      });

    // Get shuffled players by position with some randomness
    const getPlayersByPosition = (position: string) => {
      const positionPlayers = eligiblePlayers.filter((p: KplPlayer) => p.position === position);

      // Add some randomness: sometimes prioritize cheaper players, sometimes better players
      const shouldPrioritizeCheap = Math.random() > 0.5;

      return shufflePlayers(positionPlayers).sort((a: KplPlayer, b: KplPlayer) => {
        const priceA = parseFloat(a.current_value || '0');
        const priceB = parseFloat(b.current_value || '0');

        if (shouldPrioritizeCheap) {
          return priceA - priceB; // Cheaper first
        } else {
          // Mix of price and some randomness for variety
          return Math.random() > 0.7 ? priceB - priceA : priceA - priceB;
        }
      });
    };

    const canAddPlayer = (player: KplPlayer) => {
      const teamName = typeof player.team === 'object' ? player.team.name : player.team;
      return (teamCounts[teamName] || 0) < 3;
    };

    const addPlayer = (player: KplPlayer) => {
      const teamName = typeof player.team === 'object' ? player.team.name : player.team;
      teamCounts[teamName] = (teamCounts[teamName] || 0) + 1;
      currentPlayerIds.push(player.id);
    };

    // Function to fill a specific position slot
    const fillPositionSlot = async (playerSlot: Player, position: string) => {
      if (playerSlot?.id?.startsWith('placeholder')) {
        const availablePositionPlayers = getPlayersByPosition(position);
        const foundPlayer = availablePositionPlayers.find((p: KplPlayer) =>
          canAddPlayer(p) && !currentPlayerIds.includes(p.id)
        );

        if (foundPlayer) {
          selectedPlayer.value = playerSlot;
          await handlePlayerTransfer(foundPlayer);
          addPlayer(foundPlayer);
          return true;
        }
      }
      return false;
    };

    const fillPositions: PositionSlot[] = [
      // Starting lineup
      { slot: startingElevenRef.value.goalkeeper, position: 'GKP' },
      ...startingElevenRef.value.defenders.map((slot) => ({ slot, position: 'DEF' })),
      ...startingElevenRef.value.midfielders.map((slot) => ({ slot, position: 'MID' })),
      ...startingElevenRef.value.forwards.map((slot) => ({ slot, position: 'FWD' })),
      // Bench
      ...benchPlayersRef.value.map((slot) => ({ slot, position: slot.position }))
    ];

    // Shuffle the order in which positions are filled for more variety
    const shuffledPositions = shufflePlayers(fillPositions);

    for (const { slot, position } of shuffledPositions) {
      await fillPositionSlot(slot, position);
    }

    hasUnsavedChanges.value = true;
    showMessage("Team auto-filled successfully! Don't forget to save your changes.", "success", 8000);

  } catch (error) {
    console.error("Error auto-filling team:", error);
    showMessage("Failed to auto-fill team. Please try again.", "error");
  } finally {
    isAutoFilling.value = false;
  }
};

const clearTeamSelections = () => {
  startingElevenRef.value.goalkeeper = createPlaceholderPlayer("GKP", 0);
  startingElevenRef.value.defenders = Array.from({ length: defenders.value.length }, (_, i) =>
    createPlaceholderPlayer("DEF", i)
  );
  startingElevenRef.value.midfielders = Array.from({ length: midfielders.value.length }, (_, i) =>
    createPlaceholderPlayer("MID", i)
  );
  startingElevenRef.value.forwards = Array.from({ length: forwards.value.length }, (_, i) =>
    createPlaceholderPlayer("FWD", i)
  );

  benchPlayersRef.value = benchPlayersRef.value.map((player, index) =>
    createPlaceholderPlayer(player.position, index, false)
  );

  hasUnsavedChanges.value = true;
  showMessage("Team cleared! You can now auto-select new players.", "success");
};

const openChipSelector = async () => {
  // Fetch chips if not already loaded
  if (!fantasyStore.chips || fantasyStore.chips.length === 0) {
    await fantasyStore.fetchAvailableChips();
  }
  showChipSelector.value = true;
};

const handleChipSelection = async (chipType: 'TC' | 'BB' | 'WC') => {
  try {
    if (!fantasyStore.currentGameweek) {
      showMessage('No active gameweek found. Please try again.', 'error');
      return;
    }

    const response = await fantasyStore.activateChip(chipType, fantasyStore.currentGameweek);

    showChipSelector.value = false;
    await fantasyStore.fetchAvailableChips(); // Refresh chip status
    showMessage(`${chipType === 'TC' ? 'Triple Captain' : chipType === 'BB' ? 'Bench Boost' : 'Wildcard'} activated successfully!`, 'success');
  } catch (error: any) {
    showChipSelector.value = false;
    console.error('Error activating chip:', error);
    showMessage(error.message || 'Failed to activate chip. Please try again.', 'error');
  }
};

onMounted(async () => {
  try {
    authStore.initialize();
    if (!authStore.isAuthenticated) {
      router.push("/sign-in");
      return;
    }

    if (!fantasyStore.userTeam || !fantasyStore.userTeam.length) {
      await fantasyStore.fetchUserFantasyTeam();
    }

    if (fantasyStore.userTeam && fantasyStore.userTeam.length > 0) {
      if (!fantasyStore.fantasyPlayers || !fantasyStore.fantasyPlayers.length) {
        await fantasyStore.fetchFantasyTeamPlayers();
      }
      initializeTeamState();
    }
  } catch (error) {
    console.error("Error initializing team:", error);
    showMessage("Failed to load team data. Please refresh the page.", "error");
  } finally {
    isInitializing.value = false;
  }
});
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}

@keyframes slide-up {
  from {
    transform: translateY(20px);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-up {
  animation: slide-up 0.5s ease-out;
}
</style>