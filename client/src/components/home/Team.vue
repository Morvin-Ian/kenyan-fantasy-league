<template>
    <div class="flex flex-col justify-between p-6 md:p-10 mt-6 main">
        <div class="flex flex-col md:flex-row title">
            <div class="flex flex-col md:flex-row justify-between items-center w-full">
                <div class="flex flex-col md:flex-row">
                    <h1 class="text-lg md:text-2xl">Black Stone</h1>
                    <div class="mt-2 md:mt-0">
                        <a class="block md:inline mx-1 md:mx-3 text-xs text-blue-600" href="#">Transfers</a>
                        <a class="block md:inline mx-1 md:mx-3 text-xs text-blue-600" href="#">Rules</a>
                        <a class="block md:inline mx-1 md:mx-3 text-xs text-blue-600" href="#">Prizes</a>
                        <a class="block md:inline mx-1 md:mx-3 text-xs text-blue-600" href="#">About</a>
                    </div>
                </div>
                <div class="flex mt-4 md:mt-0">
                    <p class="mx-1 md:mx-3 text-sm">Total Points</p>
                    <p class="mx-1 md:mx-3 text-sm">Rank</p>
                </div>
            </div>
        </div>

        <div class="flex flex-col md:flex-row mt-4 captain">
            <div class="flex flex-col md:flex-row justify-between items-center w-full">
                <div class="flex flex-col md:flex-row">
                    <div class="mt-2 md:mt-0">
                        <span class="text-gray-800">Captain - Engineer Olunga</span>
                        <font-awesome-icon
                            class="text-xs mx-3 cursor-pointer text-blue-600"
                            icon="fa-solid fa-pen"
                        />
                    </div>
                </div>
                <div class="flex mt-4 md:mt-0">
                    <p class="mx-1 md:mx-3 text-sm font-semibold">980</p>
                    <p class="mx-1 md:mx-3 text-sm font-semibold">200/2956</p>
                </div>
            </div>
        </div>

        <div class="flex flex-wrap mt-8 players">
            <div
                v-for="player in players"
                :key="player.name"
                class="player mx-1 mb-6 md:mx-3"
            >
                <div class="image rounded-2xl bg-gray-200 px-4 py-2">
                    <img
                        :src="player.image"
                        alt="Player Image"
                        class="w-20 h-28 md:w-28 md:h-40 rounded-sm object-cover"
                    />
                    <div class="p-2 md:p-4 text-center">
                        <h3 class="text-sm font-semibold text-gray-800 mb-1">
                            {{ player.name }}
                        </h3>
                        <span class="text-sm text-gray-600 font-medium">
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
import olungaImage from "@/assets/images/olunga.png";
import player1 from "@/assets/images/player1.png";
import player2 from "@/assets/images/player2.png";
import player3 from "@/assets/images/player3.png";
import user from "@/assets/images/shadow.png";


const players = ref([
  {
    name: "E. Olunga",
    team: "Al DulHail",
    image: olungaImage,
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
