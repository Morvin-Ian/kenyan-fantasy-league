<template>
  <div class="p-4">
    <div v-if="userTeam && userTeam.length" class="max-w-7xl mx-auto flex flex-col lg:flex-row gap-6">
      <div class="w-full lg:w-2/3 rounded-xl shadow-lg relative">
        <Pitch 
          :goalkeeper="goalkeeper" 
          :defenders="defenders" 
          :midfielders="midfielders" 
          :forwards="forwards"
          :bench-players="benchPlayers" 
          :switch-source="switchSource" 
          :switch-active="switchActive"
          @player-click="handlePlayerClick" 
        />
        <div v-if="hasUnsavedChanges" class="absolute bottom-4 right-4 z-10">
          <button @click="saveTeamChanges" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded-full shadow-lg flex items-center">
            <span class="mr-2">Save Changes</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
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
    <div v-else class="max-w-3xl mx-auto text-center py-12">
      <h2 class="text-3xl font-bold text-gray-800 mb-4">You haven't created a team yet!</h2>
      <p class="text-lg text-gray-600 mb-6">Start your fantasy football journey by creating your team now.</p>
      <button @click="toggleModal" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transition duration-300">Create Your Team</button>
    </div>
    <PlayerModal 
      v-if="userTeam && userTeam.length" 
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
      @close-modal="closeSearchModal"
      @select-player="handlePlayerTransfer"
    />
    
    <div v-if="showCreateTeamModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-2xl font-bold text-gray-800 mb-4">Create Your Team</h3>
        <form @submit.prevent="createTeam">
          <div class="mb-4">
            <label for="teamName" class="block text-gray-700 font-medium mb-2">Team Name</label>
            <input v-model="teamName" id="teamName" type="text" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Enter your team name" required />
          </div>
          <div class="flex justify-end gap-4">
            <button type="button" @click="showCreateTeamModal = false" class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded">Cancel</button>
            <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded">Create Team</button>
          </div>
        </form>
      </div>
    </div>
    <div v-if="showSavedNotification" class="fixed bottom-7 left-1/2 transform -translate-x-1/2 bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded shadow-md z-50 flex items-center">
      <svg class="h-6 w-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
      </svg>
      <span>Team changes saved successfully!</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import Pitch from "@/components/Team/Pitch.vue";
import Sidebar from "@/components/Team/SideBar.vue";
import PlayerModal from "@/components/Team/PlayerModal.vue";
import SearchPlayer from "@/components/Team/SearchPlayer.vue";
import type { StartingEleven, Player as KplPlayer } from "@/helpers/types/team";
import type { FantasyPlayer as Player } from "@/helpers/types/fantasy";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import { useFantasyStore } from "@/stores/fantasy";
import { useKplStore } from "@/stores/kpl";

const authStore = useAuthStore();
const router = useRouter();
const fantasyStore = useFantasyStore();

const userTeam = computed(() => fantasyStore.userTeam);
const showModal = ref(false);
const showSearchModal = ref(false);
const selectedPlayer = ref<Player | null>(null);
const switchActive = ref(false);
const switchSource = ref<Player | null>(null);
const isBenchSwitch = ref(false);
const showCreateTeamModal = ref(false);
const teamName = ref("");
const hasUnsavedChanges = ref(false);
const showSavedNotification = ref(false);
const initialTeamState = ref<{
  startingEleven: StartingEleven;
  benchPlayers: Player[];
} | null>(null);

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

const totalPoints = computed(() => (userTeam.value.length ? userTeam.value[0].total_points : 0));
const overallRank = computed(() => (userTeam.value.length ? userTeam.value[0].overall_rank : null));
const userTeamName = computed(() => (userTeam.value.length ? userTeam.value[0].name : null));
const averagePoints = ref(52);
const highestPoints = ref(121);

const toggleModal = () => {
  showCreateTeamModal.value = !showCreateTeamModal.value;
};

const closeSearchModal = () => {
  showSearchModal.value = false;
  closeModal();
};

function initializeTeamState() {
  const players = fantasyStore.fantasyPlayers || [];
  startingElevenRef.value = {
    goalkeeper: {} as Player,
    defenders: [],
    midfielders: [],
    forwards: [],
  };
  benchPlayersRef.value = [];
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
  initialTeamState.value = {
    startingEleven: JSON.parse(JSON.stringify(startingElevenRef.value)),
    benchPlayers: JSON.parse(JSON.stringify(benchPlayersRef.value)),
  };
  hasUnsavedChanges.value = false;
}

watch(
  [() => JSON.stringify(startingElevenRef.value), () => JSON.stringify(benchPlayersRef.value)],
  () => {
    if (initialTeamState.value) {
      hasUnsavedChanges.value = true;
    }
  },
  { deep: true }
);

const openPlayerModal = (player: Player) => {
  selectedPlayer.value = player;
  showModal.value = true;
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

const initiateTransfer = (player: Player) => {
  openPlayerModal(player);
  showSearchModal.value = true;
};

const handlePlayerTransfer = async (newPlayer: KplPlayer) => {
  if (!selectedPlayer.value) {
    console.error("No player selected for transfer");
    return;
  }


  const oldPlayer = selectedPlayer.value;

  if (!isValidFormationChange(oldPlayer, newPlayer)) {
    alert("Invalid transfer: Formation constraints not met (min 3 DEF, 3 MID, 1 FWD).");
    return;
  }

  // Validate max 3 players from same team
  const sameTeamPlayers = [
    ...startingElevenRef.value.defenders,
    ...startingElevenRef.value.midfielders,
    ...startingElevenRef.value.forwards,
    startingElevenRef.value.goalkeeper,
    ...benchPlayersRef.value,
  ].filter((p) => p.team === newPlayer.team.name && p.id !== oldPlayer.id);
  if (sameTeamPlayers.length >= 3) {
    alert("Cannot select more than 3 players from the same team.");
    return;
  }

  // Validate max 15 players
  const totalPlayers = [
    ...startingElevenRef.value.defenders,
    ...startingElevenRef.value.midfielders,
    ...startingElevenRef.value.forwards,
    startingElevenRef.value.goalkeeper,
    ...benchPlayersRef.value,
  ].length;
  if (totalPlayers >= 15 && !isPlayerInTeam(newPlayer)) {
    alert("Cannot have more than 15 players in your fantasy team.");
    return;
  }
  console.log("Transferring player:", oldPlayer, "to new player:", newPlayer);
  // Perform the transfer
  if (isPlayerInStartingEleven(oldPlayer)) {
    replaceStartingWithNewPlayer(oldPlayer, newPlayer);
  } else {
    replaceBenchWithNewPlayer(oldPlayer, newPlayer);
  }

  hasUnsavedChanges.value = true;
  showSearchModal.value = false;

  // Save changes to backend
//   try {
//     await saveTeamChanges();
//     await fantasyStore.fetchFantasyTeamPlayers();
//     initializeTeamState();
//   } catch (error) {
//     console.error("Transfer failed:", error);
//     alert("Failed to save transfer. Please try again.");
//     initializeTeamState();
//     return;
//   }

  // Show notification
  showSavedNotification.value = true;
  setTimeout(() => {
    showSavedNotification.value = false;
  }, 3000);

  closeModal();
};

const replaceStartingWithNewPlayer = (oldPlayer: Player, newPlayer: KplPlayer) => {
  const newFantasyPlayer: Player = {
    id: newPlayer.id,
    name: newPlayer.name,
    position: newPlayer.position,
    team: newPlayer.team.name, 
    jersey_image: newPlayer.team.jersey_image || "",
    price: oldPlayer.price, 
    fantasy_team: oldPlayer.fantasy_team,
    player: newPlayer.id,
    gameweek: oldPlayer.gameweek,
    total_points: 0,
    gameweek_points: 0,
    is_captain: oldPlayer.is_captain,
    is_vice_captain: oldPlayer.is_vice_captain,
    is_starter: true,
    purchase_price: oldPlayer.purchase_price,
    current_value: oldPlayer.current_value,
  };

  console.log("new fantasy player:", newFantasyPlayer);


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
        players[index] = newFantasyPlayer;
      }
    }
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
      jersey_image: newPlayer.team.jersey_image || "",
      price: oldPlayer.price,
      fantasy_team: oldPlayer.fantasy_team,
      player: newPlayer.id,
      gameweek: oldPlayer.gameweek,
      total_points: 0,
      gameweek_points: 0,
      is_captain: false,
      is_vice_captain: false,
      is_starter: false,
      purchase_price: oldPlayer.purchase_price,
      current_value: oldPlayer.current_value,
    };
    benchPlayersRef.value[index] = newFantasyPlayer;
  }
};

const initiateSwitch = (player: Player) => {
  if (!selectedPlayer.value) {
    selectedPlayer.value = player;
  }
  switchSource.value = selectedPlayer.value;
  switchActive.value = true;
  isBenchSwitch.value = benchPlayersRef.value.some((p) => p.id === selectedPlayer.value?.id);
  closeModal();
};

function performSwitch(targetPlayer: Player) {
  if (!switchSource.value) return;
  const sourcePlayer = switchSource.value;

  if (targetPlayer.id.startsWith("placeholder")) {
    alert("Cannot switch with a placeholder player. Please select a valid player.");
    resetSwitchState();
    return;
  }

  if (sourcePlayer.position !== targetPlayer.position) {
    if (!isValidFormationChange(sourcePlayer, targetPlayer)) {
      alert("Invalid formation change. Must have at least 3 defenders, 3 midfielders, and 1 forward.");
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
}

const saveTeamChanges = async () => {
  try {
    const teamData = {
      startingEleven: {
        goalkeeper: startingElevenRef.value.goalkeeper,
        defenders: startingElevenRef.value.defenders,
        midfielders: startingElevenRef.value.midfielders,
        forwards: startingElevenRef.value.forwards,
      },
      benchPlayers: benchPlayersRef.value,
    };
    await fantasyStore.saveTeam(teamData); // Re-enable API call
    initializeTeamState();
    showSavedNotification.value = true;
    setTimeout(() => {
      showSavedNotification.value = false;
    }, 3000);
  } catch (error) {
    console.error("Error saving team:", error);
    alert("Failed to save team changes. Please try again.");
  }
};

async function createTeam() {
  try {
    if (!teamName.value.trim()) {
      alert("Please enter a valid team name.");
      return;
    }
    await fantasyStore.createFantasyTeam(teamName.value);
    toggleModal();
    teamName.value = "";
    await fantasyStore.fetchUserFantasyTeam();
    await fantasyStore.fetchFantasyTeamPlayers();
    initializeTeamState();
    showSavedNotification.value = true;
    setTimeout(() => {
      showSavedNotification.value = false;
    }, 3000);
  } catch (error) {
    console.error("Error creating team:", error);
    alert("Failed to create team. Please try again.");
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
  if (position === "GKP" && startingElevenRef.value.goalkeeper.position === "GKP") {
    count = 1;
  } else {
    const positionMapping: Record<string, keyof StartingEleven> = {
      DEF: "defenders",
      MID: "midfielders",
      FWD: "forwards",
    };
    const positionKey = positionMapping[position];
    if (positionKey) {
      count = (startingElevenRef.value[positionKey] as Player[]).length;
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
      is_captain: is_captain1,
      is_vice_captain: is_vice_captain1,
      is_starter: true,
    });
    addPlayerToStartingEleven({
      ...player2,
      position: player1.position,
      is_captain: is_captain2,
      is_vice_captain: is_vice_captain2,
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
    console.warn("No player selected to be captain.");
    return;
  }
  if (!isPlayerInStartingEleven(selectedPlayer.value)) {
    console.warn("Cannot assign captaincy to a bench player.");
    return;
  }
  if (selectedPlayer.value.is_captain) {
    console.warn(`${selectedPlayer.value.name} is already the captain.`);
    return;
  }
  clearCaptaincy();
  selectedPlayer.value.is_captain = true;
  closeModal();
  hasUnsavedChanges.value = true;
};

const makeViceCaptain = () => {
  if (!selectedPlayer.value) {
    console.warn("No player selected to be vice-captain.");
    return;
  }
  if (!isPlayerInStartingEleven(selectedPlayer.value)) {
    console.warn("Cannot assign vice-captaincy to a bench player.");
    return;
  }
  if (selectedPlayer.value.is_vice_captain) {
    console.warn(`${selectedPlayer.value.name} is already the vice-captain.`);
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
  await fantasyStore.fetchUserFantasyTeam();
  await fantasyStore.fetchFantasyTeamPlayers();
  initializeTeamState();
});
</script>


<style scoped>
.team-card {
    transition: all 0.3s ease;
}

.team-card:hover {
    transform: scale(1.02);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}
</style>