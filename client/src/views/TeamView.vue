<template>
  <div class="p-4 sm:p-6 md:p-8 mx-2 sm:mx-4">
    <div v-if="userTeam && userTeam.length" class="max-w-7xl mx-auto flex flex-col lg:flex-row gap-6">
      <div class="animate-fade-in w-full lg:w-2/3 relative team-card">
      <div class="relative">
        <div v-if="hasUnsavedChanges" 
            class="absolute top-7 right-1 z-20 mx-4 lg:hidden">
          <button @click="saveTeamChanges"
            class="animate-slide-up bg-white hover:bg-white text-dark font-semibold text-sm py-1.5 px-3 rounded-full shadow-md flex items-center transition transform hover:scale-105">
            <span class="mr-1">Save Changes</span>
          </button>
        </div>
      </div>



        <Pitch 
          :goalkeeper="goalkeeper" 
          :defenders="defenders" 
          :midfielders="midfielders" 
          :forwards="forwards"
          :bench-players="benchPlayers" 
          :switch-source="switchSource" 
          :switch-active="switchActive"
          @player-click="handlePlayerClick"
          @formation-change="handleFormationChange" 
        />

        <MessageAlert 
          v-if="message.text" 
          :type="message.type"
          :text="message.text"
          :dismissible="message.dismissible"
          :auto-dismiss="message.autoDismiss"
          @dismiss="clearMessage"
          class="absolute top-4 left-0 right-0 z-20 mx-4"
        />

        <!-- Save Changes Button for Larger Devices (Bottom) -->
        <div v-if="hasUnsavedChanges" class="hidden lg:block absolute bottom-4 right-4 z-10">
          <button @click="saveTeamChanges"
            class="animate-slide-up bg-white hover:bg-white text-dark font-bold py-2 px-6 rounded-full shadow-lg flex items-center transition transform hover:scale-105">
            <span class="mr-2">Save Changes</span>
          </button>
        </div>
      </div>

      <Sidebar 
        :total-points="totalPoints" 
        :average-points="averagePoints" 
        :highest-points="highestPoints"
        :overall-rank="overallRank" 
        :team="userTeamName" 
      />
    </div>

    <div v-else
      class="animate-fade-in max-w-3xl mx-auto text-center py-12 flex flex-col items-center justify-center min-h-[50vh]">
      <h2 class="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 mb-4">Build Your KPL Fantasy Team!</h2>
      <p class="text-sm sm:text-base text-gray-500 mb-6 max-w-md">Start your Kenyan Premier League fantasy journey by
        creating your team now.</p>
      <button @click="toggleModal"
        class="bg-gray-800 hover:bg-gray-900 text-white font-bold py-2 px-8 rounded-full shadow-lg transition transform hover:scale-105">Create
        Your Team</button>
    </div>

    <PlayerModal v-if="userTeam && userTeam.length" 
      :show-modal="showModal" 
      :selected-player="selectedPlayer"
      @close-modal="closeModal" 
      @initiate-switch="initiateSwitch" 
      @transfer-player="initiateTransfer"
      @make-captain="makeCaptain" 
      @make-vice-captain="makeViceCaptain" 
    />

    <SearchPlayer 
      :show-search-modal="showSearchModal" 
      :selectedPlayer="selectedPlayer" 
      @close-modal="closeSearchModal"
      @select-player="handlePlayerTransfer" 
    />

    <div v-if="showCreateTeamModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="animate-slide-up bg-white rounded-xl p-6 w-full max-w-md border border-gray-100 shadow-xl">
          <MessageAlert 
            v-if="modalMessage.text" 
            :type="modalMessage.type"
            :text="modalMessage.text"
            :dismissible="modalMessage.dismissible"
            @dismiss="clearModalMessage"
            class="mb-4"
          />
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, defineAsyncComponent } from "vue";
import memoizeOne from 'memoize-one';
import Pitch from "@/components/Team/Pitch.vue";
import Sidebar from "@/components/Team/SideBar.vue";
import MessageAlert from "@/components/common/MessageAlert.vue";
import type { StartingEleven, TeamData, Player as KplPlayer } from "@/helpers/types/team";
import type { FantasyPlayer as Player } from "@/helpers/types/fantasy";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import { useFantasyStore } from "@/stores/fantasy";
import defaultJersey from "@/assets/images/jerseys/default.png";
import goalkeeperJersey from "@/assets/images/jerseys/goalkeeper.png";

const PlayerModal = defineAsyncComponent(() => import('@/components/Team/PlayerModal.vue'));
const SearchPlayer = defineAsyncComponent(() => import('@/components/Team/SearchPlayer.vue'));

const authStore = useAuthStore();
const router = useRouter();
const fantasyStore = useFantasyStore();

const userTeam = computed(() => {
  return fantasyStore.userTeam || [];
});

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
const initialTeamState = ref<{
  startingEleven: StartingEleven;
  benchPlayers: Player[];
} | null>(null);

// Message states
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
  const players = fantasyStore.fantasyPlayers || [];
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

  //  populate with actual players
  players.forEach((player: Player) => {
    if (player.is_starter) {
      if (player.position === "GKP") startingElevenRef.value.goalkeeper = player;
      else if (player.position === "DEF") startingElevenRef.value.defenders.push(player);
      else if (player.position === "MID") startingElevenRef.value.midfielders.push(player);
      else if (player.position === "FWD") startingElevenRef.value.forwards.push(player);
    } else {
      benchPlayersRef.value.push(player);
    }
  });

  // Fill remaining starting positions with placeholders (If there is No team players for Starting 11)
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
  
  // Reduce the benchPlayersRef array to count how many players are on the bench for each position
  const benchCounts = benchPlayersRef.value.reduce((accumulator, player) => {
    // If the position already exists in the accumulator, increment its count
    // Otherwise, initialize it to 1
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
    // showMessage("Please select a valid player to transfer.", "info");  
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

    await fantasyStore.saveFantasyTeamPlayers(teamData);
    if(fantasyStore.error){
      showMessage(fantasyStore.error, "error");
        return
    }

    await fantasyStore.fetchUserFantasyTeam();
    await fantasyStore.fetchFantasyTeamPlayers();
    initializeTeamState();

    hasUnsavedChanges.value = false;
    showMessage("Team changes saved successfully!", "success");
  } catch (error) {
    showMessage("Failed to save team changes. Please try again.", "error");
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
    await fantasyStore.createFantasyTeam(teamName.value, selectedFormation.value);
    
    if(fantasyStore.error){
      showModalMessage(fantasyStore.error, "error");
      teamName.value = "";
      selectedFormation.value = "";
      fantasyStore.error = null; 
      return
    }

    toggleModal();
    teamName.value = "";
    selectedFormation.value = "";
    await fantasyStore.fetchUserFantasyTeam();
    await fantasyStore.fetchFantasyTeamPlayers();
    initializeTeamState();
    showMessage("Team created successfully!", "success");
  } catch (error) {
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

onMounted(async () => {
  authStore.initialize();
  if (!authStore.isAuthenticated) {
    router.push("/sign-in");
  }
  if (!fantasyStore.userTeam.length) {
    await fantasyStore.fetchUserFantasyTeam();
  }
  if (fantasyStore.userTeam.length > 0) {
    if (!fantasyStore.fantasyPlayers.length) {
      await fantasyStore.fetchFantasyTeamPlayers();
    }
    initializeTeamState();
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