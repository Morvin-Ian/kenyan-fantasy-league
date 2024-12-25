<template>
    <div class="min-h-screen bg-gray-100 p-4">
        <Navbar />
        <div class="max-w-7xl mt-4 mx-auto">
            <!-- Header Stats -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div class="bg-white rounded-xl p-4 shadow-sm">
                    <h3 class="text-sm text-gray-500">Gameweek Points</h3>
                    <p class="text-2xl font-bold text-gray-900">{{ totalPoints }}</p>
                </div>
                <div class="bg-white rounded-xl p-4 shadow-sm">
                    <h3 class="text-sm text-gray-500">Average Points</h3>
                    <p class="text-2xl font-bold text-gray-900">{{ averagePoints }}</p>
                </div>
                <div class="bg-white rounded-xl p-4 shadow-sm">
                    <h3 class="text-sm text-gray-500">Highest Score</h3>
                    <p class="text-2xl font-bold text-gray-900">{{ highestPoints }}</p>
                </div>
                <div class="bg-white rounded-xl p-4 shadow-sm">
                    <h3 class="text-sm text-gray-500">Overall Rank</h3>
                    <p class="text-2xl font-bold text-gray-900">{{ overallRank }}</p>
                </div>
            </div>

            <!-- Main Content -->
            <div class="bg-white rounded-xl shadow-sm p-4 md:p-6">
                <!-- Header with Navigation -->
                <div class="flex flex-wrap justify-between items-center mb-6 gap-2">
                    <div class="flex items-center gap-3">
                        <h2 class="text-xl md:text-2xl font-bold text-gray-900">{{ teamName }}</h2>
                        <span class="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-600">Team Value: £{{ teamValue
                            }}m</span>
                    </div>
                    <div class="flex items-center gap-4">
                        <button @click="previousGameWeek" :disabled="currentGameWeek === 1"
                            class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round">
                                <polyline points="15 18 9 12 15 6"></polyline>
                            </svg>
                        </button>
                        <div class="flex flex-col items-center">
                            <span class="text-sm text-gray-500">Gameweek {{ currentGameWeek }}</span>
                        </div>
                        <button @click="nextGameWeek" :disabled="currentGameWeek === 38"
                            class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round">
                                <polyline points="9 18 15 12 9 6"></polyline>
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- Pitch -->
                <div class="relative rounded-lg overflow-hidden aspect-video bg-green-800">
                    <div class="absolute inset-0 bg-[url('/pitch-pattern.svg')] opacity-20"></div>
                    <div class="relative h-full p-6">
                        <!-- Formation Layout -->
                        <div class="h-full flex flex-col justify-between">
                            <!-- Forwards (3) -->
                            <div class="grid grid-cols-3 gap-4 mb-8">
                                <div v-for="player in forwards" :key="player.id" class="flex justify-center">
                                    <PlayerCard :player="player" />
                                </div>
                            </div>
                            <!-- Midfielders (3) -->
                            <div class="grid grid-cols-3 gap-4 mb-8">
                                <div v-for="player in midfielders" :key="player.id" class="flex justify-center">
                                    <PlayerCard :player="player" />
                                </div>
                            </div>
                            <!-- Defenders (4) -->
                            <div class="grid grid-cols-4 gap-4 mb-8">
                                <div v-for="player in defenders" :key="player.id" class="flex justify-center">
                                    <PlayerCard :player="player" />
                                </div>
                            </div>
                            <!-- Goalkeeper (1) -->
                            <div class="flex justify-center">
                                <PlayerCard :player="goalkeeper" />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Bench -->
                <div class="mt-6">
                    <h3 class="text-gray-700 font-semibold mb-4">Substitutes</h3>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div v-for="player in benchPlayers" :key="player.id">
                            <PlayerCard :player="player" isBench />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import Navbar from '@/components/Navbar.vue';
import PlayerCard from '@/components/team/PlayerCard.vue';

// Team Information
const teamName = ref('Black Stone FC');
const teamValue = ref(102.5);
const currentGameWeek = ref(1);
const overallRank = ref('234,567');

// Stats
const totalPoints = ref(57);
const averagePoints = ref(52);
const highestPoints = ref(121);

// Starting 11 Players with detailed information
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
            name: "Alexander-Arnold",
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
            team: "TOT",
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
            team: "ARS",
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
            team: "MCI",
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
            team: "LIV",
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
            team: "AVL",
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
        team: "ARS",
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
        team: "ARS",
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
        team: "NEW",
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
        team: "AVL",
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

// Computed properties for easy access
const goalkeeper = computed(() => startingEleven.value.goalkeeper);
const defenders = computed(() => startingEleven.value.defenders);
const midfielders = computed(() => startingEleven.value.midfielders);
const forwards = computed(() => startingEleven.value.forwards);

// Navigation functions
const previousGameWeek = () => {
    if (currentGameWeek.value > 1) {
        currentGameWeek.value--;
        // Here you would typically fetch data for the new gameweek
    }
};

const nextGameWeek = () => {
    if (currentGameWeek.value < 38) {
        currentGameWeek.value++;
        // Here you would typically fetch data for the new gameweek
    }
};
</script>

<style scoped>
.aspect-video {
    aspect-ratio: 16 / 9;
}
</style>