<template>
    <Navbar />

    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div class="max-w-7xl mt-4 mx-auto">
            <!-- Header Stats -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                <div class="bg-white rounded-xl p-6 shadow-md border border-gray-200">
                    <h3 class="text-xs md:text-sm text-gray-500 mb-2">Gameweek Points</h3>
                    <p class="text-xl md:text-3xl font-extrabold text-gray-700">{{ totalPoints }}</p>
                </div>
                <div class="bg-white rounded-xl p-6 shadow-md border border-gray-200">
                    <h3 class="text-xs md:text-sm text-gray-500 mb-2">Average Points</h3>
                    <p class="text-xl md:text-3xl font-extrabold text-gray-700">{{ averagePoints }}</p>
                </div>
                <div class="bg-white rounded-xl p-6 shadow-md border border-gray-200">
                    <h3 class="text-xs md:text-sm text-gray-500 mb-2">Highest Score</h3>
                    <p class="text-xl md:text-3xl font-extrabold text-gray-700">{{ highestPoints }}</p>
                </div>
                <div class="bg-white rounded-xl p-6 shadow-md border border-gray-200">
                    <h3 class="text-xs md:text-sm text-gray-500 mb-2">Overall Rank</h3>
                    <p class="text-xl md:text-3xl font-extrabold text-gray-700">{{ overallRank }}</p>
                </div>
            </div>


            <!-- Main Content -->
            <div class="bg-white rounded-xl shadow-md p-2">
                <!-- Responsive Pitch -->
                <div class="relative mx-auto bg-green-700 rounded-lg overflow-scroll">
                    <div
                        class="absolute inset-0 bg-[url('https://fantasy.premierleague.com/static/media/pitch-default.dab51b01.svg')] bg-cover bg-center opacity-90">
                    </div>

                    <!-- Players -->
                    <div class="relative min-h-[500px] md:min-h-[600px] p-4 md:p-8">
                        <!-- Goalkeeper -->
                        <div
                            class="absolute bottom-[80%] left-1/2 transform -translate-x-1/2 w-full max-w-[115px] md:max-w-[150px] ">
                            <div class="p-4 cursor-pointer"
                                :class="!switchActive ? 'opacity-50 pointer-events-none' : ''"
                                @click="openPlayerModal(goalkeeper)">
                                <PlayerCard :player="goalkeeper" />
                            </div>
                        </div>

                        <!-- Defenders -->
                        <div class="absolute top-[20%] left-0 right-0">
                            <div class="flex justify-center">
                                <div v-for="player in defenders" :key="player.id" class="p-1 cursor-pointer"
                                    :class="!switchActive ? 'opacity-50 pointer-events-none' : ''"
                                    @click="openPlayerModal(player)">
                                    <PlayerCard :player="player" />
                                </div>
                            </div>
                        </div>

                        <!-- Midfielders -->
                        <div class="absolute top-[45%] left-0 right-0">
                            <div class="flex justify-center">
                                <div v-for="player in midfielders" :key="player.id" class="p-1 cursor-pointer"
                                    :class="!switchActive ? 'opacity-50 pointer-events-none' : ''"
                                    @click="openPlayerModal(player)">
                                    <PlayerCard :player="player" />
                                </div>
                            </div>
                        </div>


                        <!-- Forwards -->
                        <div class="absolute top-[70%] left-0 right-0">
                            <div class="flex gap-8 justify-center">
                                <div v-for="player in forwards" :key="player.id" class="p-4 cursor-pointer"
                                    :class="!switchActive ? 'opacity-50 pointer-events-none' : ''"
                                    @click="openPlayerModal(player)">
                                    <PlayerCard :player="player" />
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Bench -->
                    <div class="bg-white rounded-lg">
                        <div class="grid grid-cols-4 gap-2">
                            <div v-for="player in benchPlayers" :key="player.id" class="p-4 cursor-pointer"
                                :class="!switchActive ? 'opacity-50 pointer-events-none' : ''"
                                @click="openPlayerModal(player)">
                                <PlayerCard :player="player" isBench />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal -->
            <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                <div class="bg-white rounded-lg p-6 shadow-lg max-w-md w-full m-4 sm:p-4 sm:max-w-sm">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-sm font-bold text-gray-900 sm:text-base">Manage {{ selectedPlayer?.name }}</h3>
                        <button @click="closeModal" class="text-red-500 font-bold hover:text-gray-800 sm:text-sm">
                            X
                        </button>
                    </div>
                    <div class="space-y-4">
                        <button @click="initiateSwitch"
                            class="w-full bg-gray-100 py-1 text-gray-800 hover:bg-gray-200 rounded-lg text-xs font-medium sm:py-2 sm:text-xs">
                            Switch {{ selectedPlayer?.name }}
                        </button>
                        <button @click="makeCaptain"
                            class="w-full bg-gray-100 py-1 text-gray-800 hover:bg-gray-200 rounded-lg text-xs font-medium sm:py-2 sm:text-xs">
                            Make Captain
                        </button>
                        <button @click="makeViceCaptain"
                            class="w-full bg-gray-100 py-1 text-gray-800 hover:bg-gray-200 rounded-lg text-xs font-medium sm:py-2 sm:text-xs">
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


const currentGameWeek = ref(1);
const overallRank = ref("234,567");

// Modal State
const showModal = ref(false);
const selectedPlayer = ref(null);
const switchActive = ref(true);

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
        pointsPerGame: 4.2
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
            pointsPerGame: 5.3
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
            pointsPerGame: 3.8
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
            pointsPerGame: 4.5
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
            pointsPerGame: 4.2
        }
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
            pointsPerGame: 7.8
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
            pointsPerGame: 6.5
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
            pointsPerGame: 6.2
        }
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
            pointsPerGame: 8.5
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
            pointsPerGame: 5.1
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
            pointsPerGame: 5.8
        }
    ]
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
        pointsPerGame: 3.8
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
        pointsPerGame: 4.2
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
        pointsPerGame: 4.5
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
        pointsPerGame: 2.8
    }
]);

const goalkeeper = computed(() => startingEleven.value.goalkeeper);
const defenders = computed(() => startingEleven.value.defenders);
const midfielders = computed(() => startingEleven.value.midfielders);
const forwards = computed(() => startingEleven.value.forwards);


// Modal Functions
const openPlayerModal = (player) => {
    selectedPlayer.value = player;
    showModal.value = true;
};


const initiateSwitch = () => {
    switchActive.value = true;
    closeModal();
};

const closeModal = () => {
    showModal.value = false;
    selectedPlayer.value = null;
};


const switchPlayers = (benchPlayer) => {
    if (!switchActive.value || !selectedPlayer.value) return;

    // Store the selected field player
    const fieldPlayer = selectedPlayer.value;


    // Verify positions match
    if (fieldPlayer.position !== benchPlayer.position) {
        switchActive.value = false;
        return;
    }

    // Find and replace the field player
    if (fieldPlayer.position === "GK") {
        benchPlayers.value.push(startingEleven.value.goalkeeper);
        startingEleven.value.goalkeeper = benchPlayer;
    } else if (fieldPlayer.position === "DEF") {
        const index = startingEleven.value.defenders.findIndex(p => p.id === fieldPlayer.id);
        if (index !== -1) {
            benchPlayers.value.push(startingEleven.value.defenders[index]);
            startingEleven.value.defenders[index] = benchPlayer;
        }
    } else if (fieldPlayer.position === "MID") {
        const index = startingEleven.value.midfielders.findIndex(p => p.id === fieldPlayer.id);
        if (index !== -1) {
            benchPlayers.value.push(startingEleven.value.midfielders[index]);
            startingEleven.value.midfielders[index] = benchPlayer;
        }
    } else if (fieldPlayer.position === "FWD") {
        const index = startingEleven.value.forwards.findIndex(p => p.id === fieldPlayer.id);
        if (index !== -1) {
            benchPlayers.value.push(startingEleven.value.forwards[index]);
            startingEleven.value.forwards[index] = benchPlayer;
        }
    }

    // Remove the bench player from benchPlayers
    const benchIndex = benchPlayers.value.findIndex(p => p.id === benchPlayer.id);
    if (benchIndex !== -1) {
        benchPlayers.value.splice(benchIndex, 1);
    }

    // Reset states
    switchActive.value = false;
    selectedPlayer.value = null;
};

const makeCaptain = () => {
    clearCaptaincy();
    selectedPlayer.value.isCaptain = true;
    closeModal();
};

const makeViceCaptain = () => {
    clearCaptaincy();
    selectedPlayer.value.isViceCaptain = true;
    closeModal();
};

const clearCaptaincy = () => {
    startingEleven.value.forwards.forEach((p) => {
        p.isCaptain = false;
        p.isViceCaptain = false;
    });
};

</script>

<style scoped>
.aspect-video {
    aspect-ratio: 16 / 9;
}

@media (max-width: 768px) {
    .aspect-video {
        aspect-ratio: 4 / 3;
    }
}
</style>234,567