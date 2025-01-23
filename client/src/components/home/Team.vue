<template>
    <div class="min-h-screen flex items-center shadow-2xl justify-center">
        <div class="w-full bg-white overflow-hidden">
            <!-- Team Header -->
            <div class="p-6 md:p-8 text-gray-700">
                <div class="flex flex-col md:flex-row justify-between items-center">
                    <div>
                        <h1 class="text-2xl font-bold mb-2">Black Stone FC</h1>
                        <p class="text-sm opacity-80">Fantasy Football Team</p>
                    </div>
                    <div class="flex items-center space-x-6 mt-4 md:mt-0">
                        <div class="text-center">
                            <div class="text-1xl font-bold">980</div>
                            <div class="text-xs opacity-75">Total Points</div>
                        </div>
                        <div class="text-center">
                            <div class="text-1xl font-bold">200/2956</div>
                            <div class="text-xs opacity-75">Global Rank</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Captain and Team Management -->
            <div class="p-6 md:p-8 bg-gray-50">
                <div class="flex flex-col md:flex-row justify-between items-center mb-6">
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center">
                            <span class="text-lg  text-gray-800 mr-3">
                                Captain: Engineer Olunga
                            </span>
                            <button class="text-indigo-600 hover:text-indigo-800 transition">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    <button class="bg-transparent text-blue-500 px-4 py-2 rounded-lg hover:text-indigo-700 transition">
                        Make Transfer 
                    </button>
                </div>

                <!-- Players Grid -->
                <div class="grid grid-cols-3 md:grid-cols-6 gap-4">
                    <div 
                        v-for="player in players" 
                        :key="player.name" 
                        class="relative group transform transition hover:scale-105"
                    >
                        <!-- Captain Badge -->
                        <div 
                            v-if="player.captain" 
                            class="absolute top-2 right-2 bg-yellow-400 text-gray-900 text-xs font-bold px-2 py-1 rounded-full z-10"
                        >
                            C
                        </div>

                        <div class="bg-white rounded-2xl shadow-lg overflow-hidden">
                            <div class="relative">
                                <img 
                                    :src="player.image" 
                                    :alt="player.name" 
                                    class="w-full h-40 md:h-56 object-cover"
                                />
                                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition"></div>
                            </div>
                            <div class="p-3 text-center">
                                <h3 class="font-semibold text-gray-800">{{ player.name }}</h3>
                                <p class="text-xs text-gray-500">{{ player.team }}</p>
                            </div>
                        </div>
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