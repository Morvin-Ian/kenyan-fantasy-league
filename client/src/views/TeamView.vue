<template>
    <div class="bg-gray-50 p-4 md:p-6 rounded-xl">
        <Navbar/>
        <!-- Header -->
        <div class="flex flex-wrap justify-between items-center mb-6 gap-2">
            <h2 class="text-lg md:text-2xl font-bold text-gray-900">Black Stone</h2>
            <div class="flex items-center gap-4">
                <button @click="previousGameWeek"
                    class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors text-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" viewBox="0 0 24 24"
                        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <polyline points="15 18 9 12 15 6"></polyline>
                    </svg>
                </button>
                <span class="text-gray-700 font-medium text-sm">
                    Gameweek {{ currentGameWeek }}
                </span>
                <button @click="nextGameWeek"
                    class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors text-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" viewBox="0 0 24 24"
                        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                </button>
            </div>
        </div>
        <div class="rounded-lg h-screen p-6 relative" :style="{
            backgroundImage: `url(${fieldImage})`,
            backgroundRepeat: 'no-repeat',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
        }">
            <div class="grid grid-cols-3 gap-y-4">
                <!-- Players -->
                <div v-for="player in fieldPlayers" :key="player.id" class="flex justify-center">
                    <div class="bg-white shadow-lg p-2 rounded-lg w-24 text-center">
                        <p class="text-sm font-semibold text-gray-800">{{ player.name }}</p>
                        <p class="text-xs text-gray-600">{{ player.position }}</p>
                        <span class="block bg-gray-100 rounded-md text-xs mt-2 text-gray-700">{{ player.points }}
                            pts</span>
                    </div>
                </div>
            </div>
        </div>


        <!-- Bench Players -->
        <div class="mt-6">
            <h3 class="text-gray-700 text-lg font-semibold mb-2">Bench Players</h3>
            <div class="flex justify-between items-center gap-4">
                <div v-for="player in benchPlayers" :key="player.id"
                    class="bg-gray-100 p-3 rounded-lg text-center flex-1">
                    <p class="text-sm font-semibold text-gray-800">{{ player.name }}</p>
                    <p class="text-xs text-gray-600">Bench</p>
                    <span class="block bg-gray-200 rounded-md text-xs mt-2 text-gray-700">{{ player.points }} pts</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";
import fieldImage from "../assets/images/pitch.webp"
import Navbar from "@/components/Navbar.vue";

// Gameweek state
const currentGameWeek = ref(1);

// Field players (active players on the field)
const fieldPlayers = ref([
    { id: 1, name: "Player 1", position: "Forward", points: 7 },
    { id: 2, name: "Player 2", position: "Midfielder", points: 5 },
    { id: 3, name: "Player 3", position: "Midfielder", points: 6 },
    { id: 4, name: "Player 4", position: "Defender", points: 4 },
    { id: 5, name: "Player 5", position: "Defender", points: 3 },
    { id: 6, name: "Player 6", position: "Defender", points: 8 },
    { id: 7, name: "Player 7", position: "Goalkeeper", points: 10 },
]);

// Bench players
const benchPlayers = ref([
    { id: 8, name: "Player 8", points: 0 },
    { id: 9, name: "Player 9", points: 0 },
    { id: 10, name: "Player 10", points: 0 },
    { id: 11, name: "Player 11", points: 0 },
]);

// Functions to navigate gameweeks
const previousGameWeek = () => {
    if (currentGameWeek.value > 1) {
        currentGameWeek.value -= 1;
    }
};

const nextGameWeek = () => {
    currentGameWeek.value += 1;
};
</script>

<style scoped>
/* Add custom styles if needed */
</style>