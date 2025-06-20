<template>
    <div class="p-4">
        <!-- Display team management UI if userTeam exists and is not empty -->
        <div
            v-if="userTeam && userTeam.length"
            class="max-w-7xl mx-auto flex flex-col lg:flex-row gap-6"
        >
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

                <!-- Save Button - appears when changes are detected -->
                <div
                    v-if="hasUnsavedChanges"
                    class="absolute bottom-4 right-4 z-10"
                >
                    <button
                        @click="saveTeamChanges"
                        class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded-full shadow-lg flex items-center"
                    >
                        <span class="mr-2">Save Changes</span>
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-5 w-5"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fill-rule="evenodd"
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                clip-rule="evenodd"
                            />
                        </svg>
                    </button>
                </div>
            </div>

            <Sidebar
                :total-points="totalPoints"
                :average-points="averagePoints"
                :highest-points="highestPoints"
                :overall-rank="overallRank"
                :upcoming-fixtures="upcomingFixtures"
                :recent-results="recentResults"
                :top-performers="topPerformers"
                :team="userTeamName"
            />
        </div>

        <!-- Display create team prompt if userTeam is empty or doesn't exist -->
        <div v-else class="max-w-3xl mx-auto text-center py-12">
            <h2 class="text-3xl font-bold text-gray-800 mb-4">
                You haven't created a team yet!
            </h2>
            <p class="text-lg text-gray-600 mb-6">
                Start your fantasy football journey by creating your team now.
            </p>
            <button
                @click="
                    toggleModal();
                    console.log(
                        'Button clicked, showCreateTeamModal:',
                        showCreateTeamModal,
                    );
                "
                class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transition duration-300"
            >
                Create Your Team
            </button>
        </div>

        <!-- Player Modal -->
        <PlayerModal
            v-if="userTeam && userTeam.length"
            :show-modal="showModal"
            :selected-player="selectedPlayer"
            @close-modal="closeModal"
            @initiate-switch="initiateSwitch"
            @make-captain="makeCaptain"
            @make-vice-captain="makeViceCaptain"
        />

        <!-- Create Team Modal -->
        <div
            v-if="showCreateTeamModal"
            class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50"
        >
            <div class="bg-white rounded-lg p-6 w-full max-w-md">
                <h3 class="text-2xl font-bold text-gray-800 mb-4">
                    Create Your Team
                </h3>
                <form @submit.prevent="createTeam">
                    <div class="mb-4">
                        <label
                            for="teamName"
                            class="block text-gray-700 font-medium mb-2"
                            >Team Name</label
                        >
                        <input
                            v-model="teamName"
                            id="teamName"
                            type="text"
                            class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter your team name"
                            required
                        />
                    </div>
                    <div class="flex justify-end gap-4">
                        <button
                            type="button"
                            @click="showCreateTeamModal = false"
                            class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded"
                        >
                            Create Team
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Saved changes notification toast -->
        <div
            v-if="showSavedNotification"
            class="fixed bottom-7 left-1/2 transform -translate-x-1/2 bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded shadow-md z-50 flex items-center"
        >
            <svg
                class="h-6 w-6 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                ></path>
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
import { startingEleven, benchPlayers } from "@/helpers/data";
import type {
    FantasyPlayer as Player,
    Fixture,
    Result,
    Performer,
    StartingEleven,
} from "@/helpers/types/team";
import type { FantasyTeam } from "@/helpers/types/fantasy";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import { useFantasyStore } from "@/stores/fantasy";
import apiClient from "@/axios-interceptor";

const authStore = useAuthStore();
const router = useRouter();
const fantasyStore = useFantasyStore();

const userTeam = computed(() => fantasyStore.userTeam);
const showModal = ref(false);
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

const totalPoints = computed(() =>
    userTeam.value.length ? userTeam.value[0].total_points : 0,
);

const overallRank = computed(() =>
    userTeam.value.length ? userTeam.value[0].overall_rank : null,
);

const userTeamName = computed(() =>
    userTeam.value.length ? userTeam.value[0].name : null,
);

const averagePoints = ref(52);
const highestPoints = ref(121);

const toggleModal = () => {
    showCreateTeamModal.value = !showCreateTeamModal.value;
};

const upcomingFixtures = ref<Fixture[]>([
    {
        id: "1",
        status: "upcoming",
        type: "league",
        home_team: { id: "blackstonefc", name: "Black Stone FC" },
        away_team: { id: "yellowwolves", name: "Yellow Wolves" },
        match_date: "2024-02-20T19:00:00Z",
    },
    {
        id: "2",
        status: "upcoming",
        type: "league",
        home_team: { id: "blackstonefc", name: "Black Stone FC" },
        away_team: { id: "silversharks", name: "Silver Sharks" },
        match_date: "2024-02-25T18:30:00Z",
    },
]);

const recentResults = ref<Result[]>([
    { match: "Black Stone FC 2-1 Red Devils", date: "15 Feb 2024" },
    { match: "Black Stone FC 3-0 Blue Tigers", date: "10 Feb 2024" },
    { match: "Black Stone FC 1-1 Green Eagles", date: "5 Feb 2024" },
]);

const topPerformers = ref<Performer[]>([
    { name: "E. Olunga", points: 15, image: "https://example.com/player1.png" },
    {
        name: "V. Manyara",
        points: 12,
        image: "https://example.com/player2.png",
    },
    { name: "B. Peter", points: 10, image: "https://example.com/player3.png" },
]);

const startingElevenRef = ref<StartingEleven>(startingEleven);
const benchPlayersRef = ref<Player[]>(benchPlayers);

const goalkeeper = computed(() => startingElevenRef.value.goalkeeper);
const defenders = computed(() => startingElevenRef.value.defenders);
const midfielders = computed(() => startingElevenRef.value.midfielders);
const forwards = computed(() => startingElevenRef.value.forwards);

function initializeTeamState() {
    initialTeamState.value = {
        startingEleven: JSON.parse(JSON.stringify(startingElevenRef.value)),
        benchPlayers: JSON.parse(JSON.stringify(benchPlayersRef.value)),
    };
    hasUnsavedChanges.value = false;
}

// Watch for changes in team composition or captain selections
watch(
    [
        () => JSON.stringify(startingElevenRef.value),
        () => JSON.stringify(benchPlayersRef.value),
    ],
    () => {
        if (initialTeamState.value) {
            hasUnsavedChanges.value = true;
        }
    },
    { deep: true },
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

const initiateSwitch = (player) => {
    if (!selectedPlayer.value) {
        selectedPlayer.value = player;
    }

    switchSource.value = selectedPlayer.value;
    switchActive.value = true;
    isBenchSwitch.value = benchPlayersRef.value.some(
        (p) => p.id === selectedPlayer.value?.id,
    );
    closeModal();
};
function performSwitch(targetPlayer: Player) {
    if (!switchSource.value) return;

    const sourcePlayer = switchSource.value;

    // Check if the switch is between players of different positions
    if (sourcePlayer.position !== targetPlayer.position) {
        if (!isValidFormationChange(sourcePlayer, targetPlayer)) {
            alert(
                "Invalid formation change. Must have at least 3 defenders, 3 midfielders, and 1 forward.",
            );
            resetSwitchState();
            return;
        }
    }

    // Handle switching between positions in starting eleven
    if (
        isPlayerInStartingEleven(sourcePlayer) &&
        isPlayerInStartingEleven(targetPlayer)
    ) {
        swapPlayersInStartingEleven(sourcePlayer, targetPlayer);
    }
    // Handle switching between starting eleven and bench
    else if (
        isPlayerInStartingEleven(sourcePlayer) &&
        !isPlayerInStartingEleven(targetPlayer)
    ) {
        movePlayerFromStartingToBench(sourcePlayer, targetPlayer);
    }
    // Handle switching from bench to starting eleven
    else if (
        !isPlayerInStartingEleven(sourcePlayer) &&
        isPlayerInStartingEleven(targetPlayer)
    ) {
        movePlayerFromStartingToBench(targetPlayer, sourcePlayer);
    }
    // Handle switching positions on the bench
    else {
        swapBenchPlayers(sourcePlayer, targetPlayer);
    }

    // Reset switch state
    resetSwitchState();
    hasUnsavedChanges.value = true;
}

const saveTeamChanges = async () => {
    try {
        // Here you would typically make an API call to save the team
        // For example:
        // await api.saveTeam({
        //   startingEleven: startingElevenRef.value,
        //   benchPlayers: benchPlayersRef.value
        // });

        console.log("Saving team:", {
            startingEleven: startingElevenRef.value,
            benchPlayers: benchPlayersRef.value,
        });

        // Update the initial state to reflect saved changes
        initializeTeamState();

        // Show saved notification
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

        // Initialize team state with default or fetched values
        if (fantasyStore.userTeam) {
            startingElevenRef.value =
                fantasyStore.userTeam.startingEleven || startingEleven;
            benchPlayersRef.value =
                fantasyStore.userTeam.benchPlayers || benchPlayers;
            initializeTeamState();
        }

        // Show success notification
        showSavedNotification.value = true;
        setTimeout(() => {
            showSavedNotification.value = false;
        }, 3000);
    } catch (error) {
        console.error("Error creating team:", error);
        alert("Failed to create team. Please try again.");
    }
}

// Helper function to check if a formation change would be valid
function isValidFormationChange(
    sourcePlayer: Player,
    targetPlayer: Player,
): boolean {
    // If positions are the same, no formation change
    if (sourcePlayer.position === targetPlayer.position) {
        return true;
    }

    // Count current number of players in each position
    let defCount = countPlayersInPosition("DEF");
    let midCount = countPlayersInPosition("MID");
    let fwdCount = countPlayersInPosition("FWD");

    // Adjust counts based on the proposed change
    if (isPlayerInStartingEleven(sourcePlayer)) {
        // Removing a player from starting eleven
        if (sourcePlayer.position === "DEF") defCount--;
        else if (sourcePlayer.position === "MID") midCount--;
        else if (sourcePlayer.position === "FWD") fwdCount--;
    }

    if (!isPlayerInStartingEleven(targetPlayer)) {
        // Adding a player to starting eleven
        if (targetPlayer.position === "DEF") defCount++;
        else if (targetPlayer.position === "MID") midCount++;
        else if (targetPlayer.position === "FWD") fwdCount++;
    }

    // Check if the new formation meets minimum requirements
    return (
        defCount >= 3 &&
        midCount >= 3 &&
        fwdCount >= 1 &&
        defCount + midCount + fwdCount + 1 === 11
    ); // +1 for GK
}

// Count players in starting eleven by position
function countPlayersInPosition(position: string): number {
    let count = 0;

    if (
        position === "GK" &&
        startingElevenRef.value.goalkeeper.position === "GK"
    ) {
        count = 1;
    } else {
        // Count players in respective position arrays
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

// Function to handle moving a player from starting eleven to bench and bench player to starting
function movePlayerFromStartingToBench(
    startingPlayer: Player,
    benchPlayer: Player,
) {
    const startingPosition = startingPlayer.position;
    const benchPosition = benchPlayer.position;

    // Handle cases where positions are the same (simple swap)
    if (startingPosition === benchPosition) {
        replaceStartingWithBenchPlayer(startingPlayer, benchPlayer);
        return;
    }

    // Handle cases where positions are different (formation change)

    // Remove the starting player from starting eleven
    removePlayerFromStartingEleven(startingPlayer);

    // Add the bench player to starting eleven in its position
    addPlayerToStartingEleven(benchPlayer);

    // Move the starting player to bench
    const benchIndex = benchPlayersRef.value.findIndex(
        (p) => p.id === benchPlayer.id,
    );
    benchPlayersRef.value[benchIndex] = {
        ...startingPlayer,
        isCaptain: false,
        isViceCaptain: false,
    };
}

// Remove a player from the starting eleven
function removePlayerFromStartingEleven(player: Player) {
    if (player.position === "GK") {
        // Can't remove goalkeeper without replacement
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
        const index = players.findIndex((p) => p.id === player.id);
        if (index !== -1) {
            players.splice(index, 1);
        }
    }
}

// Add a player to the starting eleven in their position
function addPlayerToStartingEleven(player: Player) {
    if (player.position === "GK") {
        // Handle goalkeeper replacement
        startingElevenRef.value.goalkeeper = { ...player };
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
        players.push({ ...player });
    }
}

// Replace a starting player with a bench player (same position)
function replaceStartingWithBenchPlayer(
    startingPlayer: Player,
    benchPlayer: Player,
) {
    // If replacing goalkeeper
    if (startingPlayer.position === "GK" && benchPlayer.position === "GK") {
        const tempGoalkeeper = { ...startingElevenRef.value.goalkeeper };
        startingElevenRef.value.goalkeeper = { ...benchPlayer };

        // Update the bench player
        const benchIndex = benchPlayersRef.value.findIndex(
            (p) => p.id === benchPlayer.id,
        );
        benchPlayersRef.value[benchIndex] = {
            ...tempGoalkeeper,
            isCaptain: false,
            isViceCaptain: false,
        };
        return;
    }

    // Handle other positions
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
            // Keep track of captain/vice-captain status
            const isCaptain = players[index].isCaptain;
            const isViceCaptain = players[index].isViceCaptain;

            // Replace the player
            const tempPlayer = { ...players[index] };
            players[index] = { ...benchPlayer, isCaptain, isViceCaptain };

            // Update the bench player
            const benchIndex = benchPlayersRef.value.findIndex(
                (p) => p.id === benchPlayer.id,
            );
            benchPlayersRef.value[benchIndex] = {
                ...tempPlayer,
                isCaptain: false,
                isViceCaptain: false,
            };
        }
    }
}

// Swap players within the starting eleven
function swapPlayersInStartingEleven(player1: Player, player2: Player) {
    if (player1.position === player2.position) {
        // Simple swap within the same position group
        const positionMapping: Record<string, keyof StartingEleven> = {
            GK: "goalkeeper",
            DEF: "defenders",
            MID: "midfielders",
            FWD: "forwards",
        };

        const positionKey = positionMapping[player1.position];

        if (positionKey === "goalkeeper") {
            // This shouldn't happen as there's only one goalkeeper
            return;
        }

        if (positionKey) {
            const players = startingElevenRef.value[positionKey] as Player[];
            const index1 = players.findIndex((p) => p.id === player1.id);
            const index2 = players.findIndex((p) => p.id === player2.id);

            if (index1 !== -1 && index2 !== -1) {
                [players[index1], players[index2]] = [
                    players[index2],
                    players[index1],
                ];
            }
        }
    } else {
        // Cross-position swap - need to change formation

        // Store captaincy status
        const isCaptain1 = player1.isCaptain;
        const isViceCaptain1 = player1.isViceCaptain;
        const isCaptain2 = player2.isCaptain;
        const isViceCaptain2 = player2.isViceCaptain;

        // Remove both players from their current positions
        removePlayerFromStartingEleven(player1);
        removePlayerFromStartingEleven(player2);

        // Add them to their new positions (swapped)
        addPlayerToStartingEleven({
            ...player1,
            position: player2.position,
            isCaptain: isCaptain1,
            isViceCaptain: isViceCaptain1,
        });

        addPlayerToStartingEleven({
            ...player2,
            position: player1.position,
            isCaptain: isCaptain2,
            isViceCaptain: isViceCaptain2,
        });
    }
}

// Swap bench players
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

// Reset the switch state after a switch is completed or canceled
function resetSwitchState() {
    switchSource.value = null;
    switchActive.value = false;
    isBenchSwitch.value = false;
    selectedPlayer.value = null;
}

const isPlayerInStartingEleven = (player: Player) => {
    if (!player) return false;

    if (startingElevenRef.value.goalkeeper.id === player.id) {
        return true;
    }

    return ["defenders", "midfielders", "forwards"].some((position) => {
        const players = startingElevenRef.value[
            position as keyof StartingEleven
        ] as Player[];
        return players.some((p) => p.id === player.id);
    });
};

const clearCaptaincy = () => {
    startingElevenRef.value.goalkeeper.isCaptain = false;

    ["defenders", "midfielders", "forwards"].forEach((position) => {
        const players = startingElevenRef.value[
            position as keyof StartingEleven
        ] as Player[];
        players.forEach((player: Player) => {
            player.isCaptain = false;
        });
    });
};

const clearViceCaptaincy = () => {
    startingElevenRef.value.goalkeeper.isViceCaptain = false;

    ["defenders", "midfielders", "forwards"].forEach((position) => {
        const players = startingElevenRef.value[
            position as keyof StartingEleven
        ] as Player[];
        players.forEach((player: Player) => {
            player.isViceCaptain = false;
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

    if (selectedPlayer.value.isCaptain) {
        console.warn(`${selectedPlayer.value.name} is already the captain.`);
        return;
    }

    clearCaptaincy();
    selectedPlayer.value.isCaptain = true;
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

    if (selectedPlayer.value.isViceCaptain) {
        console.warn(
            `${selectedPlayer.value.name} is already the vice-captain.`,
        );
        return;
    }

    clearViceCaptaincy();
    selectedPlayer.value.isViceCaptain = true;
    console.log(`${selectedPlayer.value.name} is now the vice-captain.`);
    closeModal();
    hasUnsavedChanges.value = true;
};

onMounted(() => {
    authStore.initialize();
    if (!authStore.isAuthenticated) {
        router.push("/sign-in");
    }
    fantasyStore.fetchUserFantasyTeam().then(() => {
        console.log("Fetched userTeam:", userTeam.value);
    });
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
