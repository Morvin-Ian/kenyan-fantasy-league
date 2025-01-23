<template>
    <Navbar />

    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div class="max-w-7xl mt-4 mx-auto">
            <!-- Header Stats -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                <div
                    class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100"
                >
                    <h3
                        class="text-xs md:text-sm text-gray-600 mb-2 font-medium"
                    >
                        Gameweek Points
                    </h3>
                    <p class="text-xl md:text-3xl font-extrabold text-gray-800">
                        {{ totalPoints }}
                    </p>
                </div>
                <div
                    class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100"
                >
                    <h3
                        class="text-xs md:text-sm text-gray-600 mb-2 font-medium"
                    >
                        Average Points
                    </h3>
                    <p class="text-xl md:text-3xl font-extrabold text-gray-800">
                        {{ averagePoints }}
                    </p>
                </div>
                <div
                    class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100"
                >
                    <h3
                        class="text-xs md:text-sm text-gray-600 mb-2 font-medium"
                    >
                        Highest Score
                    </h3>
                    <p class="text-xl md:text-3xl font-extrabold text-gray-800">
                        {{ highestPoints }}
                    </p>
                </div>
                <div
                    class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100"
                >
                    <h3
                        class="text-xs md:text-sm text-gray-600 mb-2 font-medium"
                    >
                        Overall Rank
                    </h3>
                    <p class="text-xl md:text-3xl font-extrabold text-gray-800">
                        {{ overallRank }}
                    </p>
                </div>
            </div>

            <!-- Main Content -->
            <div class="bg-white rounded-xl shadow-lg p-4">
                <!-- Pitch Background -->
                <div
                    class="relative mx-auto bg-green-700 rounded-lg overflow-hidden"
                >
                    <div
                        class="absolute inset-0 bg-[url('https://fantasy.premierleague.com/static/media/pitch-default.dab51b01.svg')] bg-cover bg-center opacity-90"
                    ></div>

                    <!-- Players Layout -->
                    <div
                        class="relative min-h-[500px] md:min-h-[600px] p-4 md:p-8"
                    >
                        <!-- Goalkeeper -->
                        <div
                            class="absolute bottom-[83%] left-1/2 transform -translate-x-1/2 w-full max-w-[80px] md:max-w-[90px]"
                        >
                            <div
                                :class="getStartingPlayerClass(goalkeeper)"
                                @click="handlePlayerClick(goalkeeper)"
                            >
                                <PlayerCard
                                    :player="goalkeeper"
                                    :is-active="
                                        switchSource?.id === goalkeeper.id
                                    "
                                />
                            </div>
                        </div>

                        <!-- Defenders -->
                        <div class="absolute top-[20%] left-0 right-0">
                            <div class="flex justify-center gap-4">
                                <div
                                    v-for="player in defenders"
                                    :key="player.id"
                                    :class="getStartingPlayerClass(player)"
                                    @click="handlePlayerClick(player)"
                                >
                                    <PlayerCard
                                        :player="player"
                                        :is-active="
                                            switchSource?.id === player.id
                                        "
                                    />
                                </div>
                            </div>
                        </div>

                        <!-- Midfielders -->
                        <div class="absolute top-[45%] left-0 right-0">
                            <div class="flex justify-center gap-4">
                                <div
                                    v-for="player in midfielders"
                                    :key="player.id"
                                    :class="getStartingPlayerClass(player)"
                                    @click="handlePlayerClick(player)"
                                >
                                    <PlayerCard
                                        :player="player"
                                        :is-active="
                                            switchSource?.id === player.id
                                        "
                                    />
                                </div>
                            </div>
                        </div>

                        <!-- Forwards -->
                        <div class="absolute top-[70%] left-0 right-0">
                            <div class="flex justify-center gap-8">
                                <div
                                    v-for="player in forwards"
                                    :key="player.id"
                                    :class="getStartingPlayerClass(player)"
                                    @click="handlePlayerClick(player)"
                                >
                                    <PlayerCard
                                        :player="player"
                                        :is-active="
                                            switchSource?.id === player.id
                                        "
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Bench -->
                    <div class="bg-white rounded-lg mt-4 p-4 shadow-inner">
                        <div class="grid grid-cols-4 gap-2">
                            <div
                                v-for="player in benchPlayers"
                                :key="player.id"
                                :class="getBenchPlayerClass(player)"
                                @click="handlePlayerClick(player, true)"
                            >
                                <PlayerCard
                                    :player="player"
                                    :is-active="switchSource?.id === player.id"
                                    isBench
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Player Management Modal -->
            <div
                v-if="showModal"
                class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
            >
                <div
                    class="bg-white rounded-lg p-6 shadow-2xl max-w-md w-full m-4"
                >
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-bold text-gray-900">
                            Manage {{ selectedPlayer?.name }}
                        </h3>
                        <button
                            @click="closeModal"
                            class="text-gray-500 hover:text-gray-800 transition-colors"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                class="h-6 w-6"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M6 18L18 6M6 6l12 12"
                                />
                            </svg>
                        </button>
                    </div>
                    <div class="space-y-4">
                        <button
                            @click="initiateSwitch"
                            class="w-full bg-blue-100 py-3 text-blue-800 hover:bg-blue-200 rounded-lg text-sm font-semibold transition-all duration-300"
                        >
                            Switch
                        </button>
                        <button
                            @click="makeCaptain"
                            class="w-full bg-green-100 py-3 text-green-800 hover:bg-green-200 rounded-lg text-sm font-semibold transition-all duration-300"
                        >
                            Make Captain
                        </button>
                        <button
                            @click="makeViceCaptain"
                            class="w-full bg-yellow-100 py-3 text-yellow-800 hover:bg-yellow-200 rounded-lg text-sm font-semibold transition-all duration-300"
                        >
                            Make Vice-Captain
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from "vue";
import Navbar from "@/components/Navbar.vue";
import PlayerCard from "@/components/team/PlayerCard.vue";

const overallRank = ref("234,567");

// Modal State
const showModal = ref(false);
const selectedPlayer = ref(null);
const switchActive = ref(false);
const switchSource = ref(null);
const switchTarget = ref(null);
const isBenchSwitch = ref(false);

// Stats
const totalPoints = ref(57);
const averagePoints = ref(52);
const highestPoints = ref(121);

const startingEleven = ref({
    // Goalkeeper (1)
    goalkeeper: {
        id: 1,
        name: "Alisson",
        team: "GOR",
        position: "GK",
        points: 6,
        form: "6.7",
        price: 5.5,
        nextFixture: "MUN (H)",
        chanceOfPlaying: 10,
        selectedBy: "34.5%",
        pointsPerGame: 4.2,
    },

    // Defenders (4)
    defenders: [
        {
            id: 2,
            name: "Arnold",
            team: "AFC",
            position: "DEF",
            points: 12,
            form: "7.2",
            price: 7.8,
            nextFixture: "MUN (H)",
            chanceOfPlaying: 100,
            selectedBy: "28.9%",
            pointsPerGame: 5.3,
        },
        {
            id: 3,
            name: "Chilwell",
            team: "AFC",
            position: "DEF",
            points: 2,
            form: "5.4",
            price: 5.4,
            nextFixture: "BUR (H)",
            chanceOfPlaying: 100,
            selectedBy: "15.2%",
            pointsPerGame: 3.8,
        },
        {
            id: 4,
            name: "Dias",
            team: "ULINZI",
            position: "DEF",
            points: 6,
            form: "6.1",
            price: 6.2,
            nextFixture: "NEW (A)",
            chanceOfPlaying: 100,
            selectedBy: "22.1%",
            pointsPerGame: 4.5,
        },
        {
            id: 5,
            name: "Gabriel",
            team: "ULINZI",
            position: "DEF",
            points: 8,
            form: "6.8",
            price: 5.2,
            nextFixture: "TOT (H)",
            chanceOfPlaying: 100,
            selectedBy: "18.4%",
            pointsPerGame: 4.2,
        },
    ],

    // Midfielders (3)
    midfielders: [
        {
            id: 6,
            name: "Salah",
            team: "TUSKER",
            position: "MID",
            points: 15,
            form: "8.3",
            price: 12.8,
            nextFixture: "MUN (H)",
            chanceOfPlaying: 100,
            selectedBy: "45.6%",
            pointsPerGame: 7.8,
        },
        {
            id: 7,
            name: "Son",
            team: "TUSKER",
            position: "MID",
            points: 8,
            form: "7.1",
            price: 9.3,
            nextFixture: "ARS (A)",
            chanceOfPlaying: 100,
            selectedBy: "32.4%",
            pointsPerGame: 6.5,
        },
        {
            id: 8,
            name: "Saka",
            team: "ULINZI",
            position: "MID",
            points: 7,
            form: "7.4",
            price: 8.7,
            nextFixture: "TOT (H)",
            chanceOfPlaying: 100,
            selectedBy: "38.9%",
            pointsPerGame: 6.2,
        },
    ],

    // Forwards (3)
    forwards: [
        {
            id: 9,
            name: "Haaland",
            team: "GOR",
            position: "FWD",
            points: 13,
            form: "8.9",
            price: 14.2,
            nextFixture: "NEW (A)",
            chanceOfPlaying: 100,
            selectedBy: "82.3%",
            pointsPerGame: 8.5,
        },
        {
            id: 10,
            name: "Darwin",
            team: "AFC",
            position: "FWD",
            points: 6,
            form: "6.8",
            price: 7.8,
            isCaptain: true,
            nextFixture: "MUN (H)",
            chanceOfPlaying: 100,
            selectedBy: "24.7%",
            pointsPerGame: 5.1,
        },
        {
            id: 11,
            name: "Watkins",
            team: "AFC",
            position: "FWD",
            points: 8,
            form: "7.2",
            isViceCaptain: true,
            price: 8.5,
            nextFixture: "WOL (H)",
            chanceOfPlaying: 100,
            selectedBy: "28.3%",
            pointsPerGame: 5.8,
        },
    ],
});

// Bench Players (4)
const benchPlayers = ref([
    {
        id: 12,
        name: "Raya",
        team: "AFC",
        position: "GK",
        points: 0,
        form: "6.2",
        price: 4.8,
        nextFixture: "TOT (H)",
        chanceOfPlaying: 100,
        selectedBy: "12.4%",
        pointsPerGame: 3.8,
    },
    {
        id: 13,
        name: "White",
        team: "GOR",
        position: "DEF",
        points: 0,
        form: "6.5",
        price: 5.1,
        nextFixture: "TOT (H)",
        chanceOfPlaying: 100,
        selectedBy: "15.7%",
        pointsPerGame: 4.2,
    },
    {
        id: 14,
        name: "Gordon",
        team: "TUSKER",
        position: "MID",
        points: 0,
        form: "6.8",
        price: 6.2,
        nextFixture: "MCI (H)",
        chanceOfPlaying: 100,
        selectedBy: "8.9%",
        pointsPerGame: 4.5,
    },
    {
        id: 15,
        name: "Archer",
        team: "ULINZI",
        position: "FWD",
        points: 0,
        form: "5.4",
        price: 4.5,
        nextFixture: "WOL (H)",
        chanceOfPlaying: 100,
        selectedBy: "5.2%",
        pointsPerGame: 2.8,
    },
]);

// Modify the initiateSwitch function
const initiateSwitch = () => {
    switchSource.value = selectedPlayer.value;
    switchActive.value = true;
    // Set isBenchSwitch based on whether the selected player is from bench
    isBenchSwitch.value = benchPlayers.value.some(
        (p) => p.id === selectedPlayer.value.id,
    );
    showModal.value = false;
};

const goalkeeper = computed(() => startingEleven.value.goalkeeper);
const defenders = computed(() => startingEleven.value.defenders);
const midfielders = computed(() => startingEleven.value.midfielders);
const forwards = computed(() => startingEleven.value.forwards);

// Modal Functions
const openPlayerModal = (player) => {
    selectedPlayer.value = player;
    showModal.value = true;
};

const closeModal = () => {
    showModal.value = false;
    selectedPlayer.value = null;
};

const isPlayerDisabled = (player, isBench = false) => {
    if (!switchActive.value || !switchSource.value) return false;

    // If it's a goalkeeper, only allow switching with other goalkeepers
    if (switchSource.value.position === "GK" || player.position === "GK") {
        return switchSource.value.position !== player.position;
    }

    // Allow switching only between bench and field players
    return isBenchSwitch.value === isBench;
};

const handlePlayerClick = (player, isBench = false) => {
    if (switchActive.value) {
        // Handle second click (target selection)
        performSwitch(player, isBench);
    } else {
        // Handle first click (normal modal opening)
        openPlayerModal(player);
    }
};

const performSwitch = (targetPlayer, isBench) => {
    const sourcePlayer = switchSource.value;

    // Only allow switches between bench and starting 11
    if (isBenchSwitch.value === isBench) {
        return;
    }

    const getFormationCounts = () => {
        return {
            DEF: startingEleven.value.defenders.length,
            MID: startingEleven.value.midfielders.length,
            FWD: startingEleven.value.forwards.length,
        };
    };

    const getTotalFieldPlayers = () => {
        const counts = getFormationCounts();
        return counts.DEF + counts.MID + counts.FWD + 1; // +1 for goalkeeper
    };

    const isValidFormationChange = (sourcePos, targetPos) => {
        if (sourcePos === "GK" || targetPos === "GK") {
            return false; // Goalkeepers can only switch with goalkeepers
        }

        const currentCounts = getFormationCounts();
        const newCounts = { ...currentCounts };

        // Calculate new formation numbers
        if (isBenchSwitch.value) {
            // Player coming from bench to replace targetPos
            newCounts[targetPos]--;
            newCounts[sourcePos]++;
        } else {
            // Player from field going to bench, being replaced by targetPos
            newCounts[sourcePos]--;
            newCounts[targetPos]++;
        }

        // Check formation constraints
        const constraints = {
            DEF: { min: 3, max: 5 },
            MID: { min: 3, max: 5 },
            FWD: { min: 1, max: 3 },
        };

        return Object.entries(newCounts).every(([pos, count]) => {
            return (
                count >= constraints[pos].min && count <= constraints[pos].max
            );
        });
    };

    // Perform the switch based on positions
    if (isBenchSwitch.value) {
        // Switching from bench to starting 11
        const benchIndex = benchPlayers.value.findIndex(
            (p) => p.id === sourcePlayer.id,
        );

        if (targetPlayer.position === sourcePlayer.position) {
            if (targetPlayer.position === "GK") {
                // Switch goalkeepers
                const tempGK = startingEleven.value.goalkeeper;
                startingEleven.value.goalkeeper = sourcePlayer;
                benchPlayers.value[benchIndex] = tempGK;
            } else {
                // Switch same positions
                const positionArray = getPositionArray(targetPlayer.position);
                const fieldIndex = positionArray.findIndex(
                    (p) => p.id === targetPlayer.id,
                );

                if (fieldIndex !== -1) {
                    const tempPlayer = positionArray[fieldIndex];
                    positionArray[fieldIndex] = sourcePlayer;
                    benchPlayers.value[benchIndex] = tempPlayer;
                }
            }
        } else {
            // Different positions - check if valid formation change
            if (
                !isValidFormationChange(
                    sourcePlayer.position,
                    targetPlayer.position,
                )
            ) {
                console.warn(
                    "Invalid formation change. Must maintain valid formation constraints.",
                );
                return;
            }

            // Remove target player from their position array
            const targetPosArray = getPositionArray(targetPlayer.position);
            const fieldIndex = targetPosArray.findIndex(
                (p) => p.id === targetPlayer.id,
            );

            if (fieldIndex !== -1) {
                // Remove target player
                targetPosArray.splice(fieldIndex, 1);

                // Add source player to their new position array
                const sourcePosArray = getPositionArray(sourcePlayer.position);
                sourcePosArray.push(sourcePlayer);

                // Update bench
                benchPlayers.value[benchIndex] = targetPlayer;
            }
        }
    } else {
        // Switching from starting 11 to bench
        const benchIndex = benchPlayers.value.findIndex(
            (p) => p.id === targetPlayer.id,
        );

        if (sourcePlayer.position === targetPlayer.position) {
            if (sourcePlayer.position === "GK") {
                // Switch goalkeepers
                const tempGK = startingEleven.value.goalkeeper;
                startingEleven.value.goalkeeper = targetPlayer;
                benchPlayers.value[benchIndex] = tempGK;
            } else {
                // Switch same positions
                const positionArray = getPositionArray(sourcePlayer.position);
                const fieldIndex = positionArray.findIndex(
                    (p) => p.id === sourcePlayer.id,
                );

                if (fieldIndex !== -1) {
                    const tempPlayer = positionArray[fieldIndex];
                    positionArray[fieldIndex] = targetPlayer;
                    benchPlayers.value[benchIndex] = tempPlayer;
                }
            }
        } else {
            // Different positions - check if valid formation change
            if (
                !isValidFormationChange(
                    sourcePlayer.position,
                    targetPlayer.position,
                )
            ) {
                console.warn(
                    "Invalid formation change. Must maintain valid formation constraints.",
                );
                return;
            }

            // Remove source player from their position array
            const sourcePosArray = getPositionArray(sourcePlayer.position);
            const fieldIndex = sourcePosArray.findIndex(
                (p) => p.id === sourcePlayer.id,
            );

            if (fieldIndex !== -1) {
                // Remove source player
                sourcePosArray.splice(fieldIndex, 1);

                // Add target player to their new position array
                const targetPosArray = getPositionArray(targetPlayer.position);
                targetPosArray.push(targetPlayer);

                // Update bench
                benchPlayers.value[benchIndex] = sourcePlayer;
            }
        }
    }

    // Validate total players is still 11
    if (getTotalFieldPlayers() !== 11) {
        console.error("Invalid total number of players");
        return;
    }

    // Reset switch state
    switchActive.value = false;
    switchSource.value = null;
    isBenchSwitch.value = false;
};

const getPositionArray = (position) => {
    switch (position) {
        case "DEF":
            return startingEleven.value.defenders;
        case "MID":
            return startingEleven.value.midfielders;
        case "FWD":
            return startingEleven.value.forwards;
        default:
            return null;
    }
};

const isPlayerInStartingEleven = (player) => {
    if (!player) return false;

    // Check goalkeeper
    if (startingEleven.value.goalkeeper.id === player.id) {
        return true;
    }

    // Check other positions
    return ["defenders", "midfielders", "forwards"].some((position) => {
        return startingEleven.value[position].some((p) => p.id === player.id);
    });
};

const findCurrentCaptain = () => {
    // Check all positions for current captain
    const positions = ["defenders", "midfielders", "forwards"];
    for (const position of positions) {
        const player = startingEleven.value[position].find((p) => p.isCaptain);
        if (player) return player;
    }
    // Check goalkeeper
    if (startingEleven.value.goalkeeper.isCaptain) {
        return startingEleven.value.goalkeeper;
    }
    return null;
};

const findCurrentViceCaptain = () => {
    // Check all positions for current vice captain
    const positions = ["defenders", "midfielders", "forwards"];
    for (const position of positions) {
        const player = startingEleven.value[position].find(
            (p) => p.isViceCaptain,
        );
        if (player) return player;
    }
    // Check goalkeeper
    if (startingEleven.value.goalkeeper.isViceCaptain) {
        return startingEleven.value.goalkeeper;
    }
    return null;
};

const clearCaptaincy = () => {
    // Clear goalkeeper
    if (startingEleven.value.goalkeeper) {
        startingEleven.value.goalkeeper.isCaptain = false;
        startingEleven.value.goalkeeper.isViceCaptain = false;
    }

    // Clear all positions
    ["defenders", "midfielders", "forwards"].forEach((position) => {
        startingEleven.value[position].forEach((player) => {
            player.isCaptain = false;
            player.isViceCaptain = false;
        });
    });
};

const makeCaptain = () => {
    if (!selectedPlayer.value) {
        console.warn("No player selected");
        return;
    }

    if (!isPlayerInStartingEleven(selectedPlayer.value)) {
        console.warn("Cannot make bench player captain");
        return;
    }

    const currentCaptain = findCurrentCaptain();
    const currentViceCaptain = findCurrentViceCaptain();

    // If current captain is becoming vice captain, clear their captain status
    if (currentCaptain?.id === selectedPlayer.value.id) {
        currentCaptain.isCaptain = false;
    }

    // If current vice captain is becoming captain, clear their vice captain status
    if (currentViceCaptain?.id === selectedPlayer.value.id) {
        currentViceCaptain.isViceCaptain = false;
    }

    clearCaptaincy();
    selectedPlayer.value.isCaptain = true;
    closeModal();
};

const makeViceCaptain = () => {
    if (!selectedPlayer.value) {
        console.warn("No player selected");
        return;
    }

    if (!isPlayerInStartingEleven(selectedPlayer.value)) {
        console.warn("Cannot make bench player vice captain");
        return;
    }

    const currentCaptain = findCurrentCaptain();
    const currentViceCaptain = findCurrentViceCaptain();

    // If current captain is becoming vice captain, clear their captain status
    if (currentCaptain?.id === selectedPlayer.value.id) {
        currentCaptain.isCaptain = false;
    }

    // If current vice captain is becoming captain, clear their vice captain status
    if (currentViceCaptain?.id === selectedPlayer.value.id) {
        currentViceCaptain.isViceCaptain = false;
    }

    clearCaptaincy();
    selectedPlayer.value.isViceCaptain = true;
    closeModal();
};

// Template helper computed properties
const getStartingPlayerClass = (player) => {
    return {
        "opacity-50 pointer-events-none":
            switchActive.value && isPlayerDisabled(player),
        "cursor-pointer": true,
    };
};

const getBenchPlayerClass = (player) => {
    return {
        "opacity-50 pointer-events-none":
            switchActive.value && isPlayerDisabled(player, true),
        "cursor-pointer": true,
    };
};
</script>

<style scoped>
.transition-all {
    transition-property: all;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 300ms;
}

.bg-green-700 {
    background-color: #2e7d32;
}

/* Add a subtle glow effect on hover for player cards */
.player-card:hover {
    filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.5));
}
</style>
