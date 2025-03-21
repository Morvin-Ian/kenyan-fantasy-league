<template>
    <div class="p-4 md:p-10">
        <div class="mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div class="bg-white p-4 sm:p-6 text-center relative">
                <h1
                    class="text-xl sm:text-2xl md:text-3xl font-extrabold text-gray-700 tracking-wide flex flex-col sm:flex-row items-center justify-center sm:space-x-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 sm:h-10 sm:w-10 mb-2 sm:mb-0"
                        viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd"
                            d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z"
                            clip-rule="evenodd" />
                        <path
                            d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z" />
                    </svg>
                    <span>Kenyan Premier League Standings</span>
                </h1>
                <div class="absolute bottom-0 left-0 right-0 h-1 bg-red-600 animate-pulse"></div>
            </div>

            <!-- Scroll Indicator for Small Devices -->
            <div class="md:hidden px-6 py-2 flex items-center text-sm text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-500 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
                <span>Swipe left to view more stats</span>
            </div>

            <!-- Standings Table -->
            <div class="p-6 overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-green-100 text-green-800">
                        <tr>
                            <th v-for="header in tableHeaders" :key="header" class="p-3 text-center font-semibold">
                                {{ header }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="team in standings" :key="team.team"
                            class="hover:bg-green-50 transition-all duration-300 transform hover:scale-[1.01]">
                            <td class="p-3 text-center">
                                <span :class="getPositionClass(team.position)"
                                    class="inline-block w-8 h-8 rounded-full flex items-center justify-center font-bold">
                                    {{ team.position }}
                                </span>
                            </td>
                            <td class="p-3 font-semibold text-gray-800">
                                {{ team.team }}
                            </td>
                            <td class="p-3 text-center">{{ team.played }}</td>
                            <td class="p-3 text-center text-green-600">
                                {{ team.won }}
                            </td>
                            <td class="p-3 text-center text-yellow-600">
                                {{ team.drawn }}
                            </td>
                            <td class="p-3 text-center text-red-600">
                                {{ team.lost }}
                            </td>
                            <td class="p-3 text-center">{{ team.goalsFor }}</td>
                            <td class="p-3 text-center">
                                {{ team.goalsAgainst }}
                            </td>
                            <td class="p-3 text-center font-bold">
                                {{ team.goalsFor - team.goalsAgainst }}
                            </td>
                            <td class="p-3 text-center font-bold text-green-700">
                                {{ team.points }}
                            </td>
                            <td class="p-3">
                                <div class="flex justify-center space-x-1">
                                    <span v-for="(result, index) in team.form" :key="index"
                                        :class="getFormBadgeColor(result)"
                                        class="w-6 h-6 rounded-full flex items-center justify-center text-white font-bold">
                                        {{ result }}
                                    </span>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>


            <!-- Performance Insights Cards - More compact on mobile -->
            <div class="bg-gray-50 p-4 md:p-6 grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
                <div
                    class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-3 md:p-5 shadow-md border border-green-200 transform transition-all duration-300 hover:scale-105 hover:shadow-lg">
                    <div class="flex items-center mb-2 md:mb-3">
                        <div class="bg-green-600 p-1 md:p-2 rounded-lg mr-2 md:mr-3">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-6 md:w-6 text-white" fill="none"
                                viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                            </svg>
                        </div>
                        <h3 class="text-base md:text-lg font-bold text-green-700">
                            League Leader
                        </h3>
                    </div>
                    <div class="flex items-center">
                        <div
                            class="w-8 h-8 md:w-12 md:h-12 bg-white rounded-full flex items-center justify-center text-sm md:text-lg font-bold mr-2 md:mr-3 border-2 border-green-400">
                            {{ standings[0].team.substring(0, 2) }}
                        </div>
                        <div>
                            <p class="text-sm md:text-base text-gray-700 font-medium">{{ standings[0].team }}</p>
                            <p class="text-base md:text-xl text-green-800 font-bold">{{ standings[0].points }} points</p>
                        </div>
                    </div>
                    <div class="mt-1 md:mt-2 text-xs md:text-sm text-green-600">
                        {{ standings[0].won }} wins, {{ standings[0].drawn }} draws, {{ standings[0].lost }} losses
                    </div>
                </div>

                <div
                    class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-3 md:p-5 shadow-md border border-blue-200 transform transition-all duration-300 hover:scale-105 hover:shadow-lg">
                    <div class="flex items-center mb-2 md:mb-3">
                        <div class="bg-blue-600 p-1 md:p-2 rounded-lg mr-2 md:mr-3">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-6 md:w-6 text-white" fill="none"
                                viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                        </div>
                        <h3 class="text-base md:text-lg font-bold text-blue-700">
                            Top Scorer
                        </h3>
                    </div>
                    <div class="flex items-center">
                        <div
                            class="w-8 h-8 md:w-12 md:h-12 bg-white rounded-full flex items-center justify-center text-sm md:text-lg font-bold mr-2 md:mr-3 border-2 border-blue-400">
                            {{ standings[0].team.substring(0, 2) }}
                        </div>
                        <div>
                            <p class="text-sm md:text-base text-gray-700 font-medium">{{ standings[0].team }}</p>
                            <p class="text-base md:text-xl text-blue-800 font-bold">{{ standings[0].goalsFor }} goals</p>
                        </div>
                    </div>
                    <div class="mt-1 md:mt-2 text-xs md:text-sm text-blue-600">
                        {{ (standings[0].goalsFor / standings[0].played).toFixed(1) }} goals per game
                    </div>
                </div>

                <div
                    class="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-3 md:p-5 shadow-md border border-amber-200 transform transition-all duration-300 hover:scale-105 hover:shadow-lg">
                    <div class="flex items-center mb-2 md:mb-3">
                        <div class="bg-amber-600 p-1 md:p-2 rounded-lg mr-2 md:mr-3">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-6 md:w-6 text-white" fill="none"
                                viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                        </div>
                        <h3 class="text-base md:text-lg font-bold text-amber-700">
                            Best Defense
                        </h3>
                    </div>
                    <div class="flex items-center">
                        <div
                            class="w-8 h-8 md:w-12 md:h-12 bg-white rounded-full flex items-center justify-center text-sm md:text-lg font-bold mr-2 md:mr-3 border-2 border-amber-400">
                            {{ standings[0].team.substring(0, 2) }}
                        </div>
                        <div>
                            <p class="text-sm md:text-base text-gray-700 font-medium">{{ standings[0].team }}</p>
                            <p class="text-base md:text-xl text-amber-800 font-bold">{{ standings[0].goalsAgainst }} conceded</p>
                        </div>
                    </div>
                    <div class="mt-1 md:mt-2 text-xs md:text-sm text-amber-600">
                        {{ (standings[0].goalsAgainst / standings[0].played).toFixed(1) }} goals conceded per game
                    </div>
                </div>
            </div>

            <div
                class="p-4 md:p-6 bg-white border-t border-gray-100 flex flex-col md:flex-row justify-between items-center text-xs md:text-sm">
                <div class="text-gray-500 mb-3 md:mb-0">
                    Last updated: February 25, 2025
                </div>
                <div class="flex space-x-3 md:space-x-4">
                    <div class="flex items-center">
                        <span class="w-3 h-3 md:w-4 md:h-4 bg-green-500 rounded-full mr-1 md:mr-2"></span>
                        <span class="text-gray-600">Win</span>
                    </div>
                    <div class="flex items-center">
                        <span class="w-3 h-3 md:w-4 md:h-4 bg-yellow-500 rounded-full mr-1 md:mr-2"></span>
                        <span class="text-gray-600">Draw</span>
                    </div>
                    <div class="flex items-center">
                        <span class="w-3 h-3 md:w-4 md:h-4 bg-red-500 rounded-full mr-1 md:mr-2"></span>
                        <span class="text-gray-600">Loss</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

interface TeamStanding {
    position: number;
    team: string;
    played: number;
    won: number;
    drawn: number;
    lost: number;
    goalsFor: number;
    goalsAgainst: number;
    points: number;
    form: ("W" | "D" | "L")[];
}

const tableHeaders: string[] = [
    "Pos",
    "Team",
    "P",
    "W",
    "D",
    "L",
    "GF",
    "GA",
    "GD",
    "Pts",
    "Form",
];

const standings = ref<TeamStanding[]>([
    {
        position: 1,
        team: "Gor Mahia",
        played: 24,
        won: 16,
        drawn: 5,
        lost: 3,
        goalsFor: 38,
        goalsAgainst: 15,
        points: 53,
        form: ["W", "W", "D", "W", "L"],
    },
    {
        position: 2,
        team: "Tusker FC",
        played: 24,
        won: 15,
        drawn: 4,
        lost: 5,
        goalsFor: 35,
        goalsAgainst: 18,
        points: 49,
        form: ["W", "L", "W", "W", "W"],
    },
    {
        position: 3,
        team: "AFC Leopards",
        played: 24,
        won: 13,
        drawn: 6,
        lost: 5,
        goalsFor: 32,
        goalsAgainst: 20,
        points: 45,
        form: ["D", "W", "W", "L", "W"],
    },
]);

function getFormBadgeColor(result: "W" | "D" | "L"): string {
    switch (result) {
        case "W":
            return "bg-green-500";
        case "D":
            return "bg-yellow-500";
        case "L":
            return "bg-red-500";
        default:
            return "bg-gray-500";
    }
}

function getPositionClass(position: number): string {
    if (position === 1) return "bg-green-600 text-white";
    if (position === 2) return "bg-blue-600 text-white";
    if (position === 3) return "bg-amber-500 text-white";
    return "bg-gray-200 text-gray-700";
}

function getGDClass(goalDifference: number): string {
    if (goalDifference > 0) return "text-green-600";
    if (goalDifference < 0) return "text-red-600";
    return "text-gray-600";
}

function getHeaderClass(header: string): string {
    return header === "Team" ? "text-left" : "text-center";
}

onMounted(async () => {
  await authStore.initialize();
  if (!authStore.isAuthenticated) {
    router.push("/sign-in");
  }

});
</script>