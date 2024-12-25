<template>
    <div class="flex flex-col justify-between p-6 md:p-10 mt-2 main">
        <!-- Title Section -->
        <div class="flex flex-col md:flex-row title">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center w-full">
                <!-- Title and Links -->
                <div class="flex flex-col md:flex-row">
                    <h2 class="text-lg font-semibold text-gray-900 md:mr-4 mb-2 md:mb-0 text-left">Black Stone</h2>
                </div>
                <!-- Hidden on small devices -->
                <div class="flex mt-4 md:mt-0 hidden md:flex">
                    <p class="mx-1 md:mx-3 text-sm">Total Points</p>
                    <p class="mx-1 md:mx-3 text-sm">Rank</p>
                </div>
            </div>
        </div>

        <!-- Captain Section -->
        <div class="flex flex-col md:flex-row mt-4 captain">
            <div class="flex flex-col md:flex-row justify-between w-full">
                <!-- Captain Details -->
                <div class="flex flex-col md:flex-row">
                    <div class="mt-1 md:mt-0 flex items-center">
                        <span class="text-xs md:text-base text-gray-800">Captain - Engineer Olunga</span>
                        <font-awesome-icon class="text-xs mx-3 cursor-pointer text-blue-600" icon="fa-solid fa-pen" />
                    </div>
                </div>
                <!-- Hidden on small devices -->
                <div class="flex mt-4 md:mt-0 hidden md:flex">
                    <p class="mx-1 md:mx-3 text-sm font-semibold">980</p>
                    <p class="mx-1 md:mx-3 text-sm font-semibold">200/2956</p>
                </div>
            </div>
        </div>

        <!-- Players Section -->
        <div class="flex flex-wrap mt-4 players">
            <div v-for="player in players" :key="player.name" class="player relative mx-1 mb-6 md:mx-3">
                <!-- Captain Badge -->
                <div v-if="player.captain"
                    class="absolute top-2 right-2 bg-blue-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-md">
                    C
                </div>

                <div class="image rounded-2xl bg-gray-200 px-4 py-2">
                    <!-- Player Image -->
                    <img :src="player.image" alt="Player Image"
                        class="w-16 h-20 md:w-28 md:h-40 rounded-sm object-cover" />
                    <!-- Player Info -->
                    <div class="p-2 md:p-4 text-center">
                        <h3 class="text-xs md:text-sm font-semibold text-gray-800 mb-1">
                            {{ player.name }}
                        </h3>
                        <span class="text-xs md:text-sm text-gray-600 font-medium">
                            {{ player.team }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script setup>
import { ref } from "vue";
import olunga from "@/assets/images/olunga.png";
import player1 from "@/assets/images/player1.png";
import player2 from "@/assets/images/player2.png";
import player3 from "@/assets/images/player3.png";
import user from "@/assets/images/shadow.png";

// Player Data
const players = ref([
    {
        name: "E. Olunga",
        team: "Al DulHail",
        image: olunga,
        captain: true,
    },
    {
        name: "V. Manyara",
        team: "Gor Mahia",
        image: player1,
    },
    {
        name: "B. Peter",
        team: "Tusker FC",
        image: player2,
    },
    {
        name: "E. Nderitu",
        team: "Tusker FC",
        image: player3,
    },
    {
        name: "+",
        team: "Add player",
        image: user,
    },
]);
</script>

<style>
/* Responsive Design Tweaks */
@media (max-width: 768px) {
    .title .hidden {
        display: none;
    }

    .captain .hidden {
        display: none;
    }

    h1 {
        font-size: 1rem;
    }

    .main {
        font-size: 0.875rem;
        /* Smaller base font size for small devices */
    }
}
</style>
