<template>
    <div>
        <!-- Navbar -->
        <Navbar />
        <div class="w-full max-w-6xl mt-5 mx-auto bg-white shadow-lg rounded-lg overflow-hidden">

            <!-- Header -->
            <div class="p-6 bg-white text-center relative">
                <h2 class="text-xl md:text-2xl font-extrabold text-dark tracking-wide">
                    Kenyan Premier League Standings
                </h2>
                <div class="absolute -bottom-2 left-0 right-0 h-1 bg-red-500 animate-pulse"></div>
            </div>

            <div class="p-4 md:p-6">
                <div class="overflow-x-auto">
                    <table class="w-full text-xs md:text-sm text-left text-gray-500">
                        <thead class="bg-gray-50 text-gray-700 uppercase text-[10px] md:text-xs tracking-wide">
                            <tr class="border-b-2 border-green-200">
                                <th class="p-2 md:p-4">Pos</th>
                                <th class="p-2 md:p-4">Team</th>
                                <th class="p-2 md:p-4 text-center">P</th>
                                <th class="p-2 md:p-4 text-center">W</th>
                                <th class="p-2 md:p-4 text-center">D</th>
                                <th class="p-2 md:p-4 text-center">L</th>
                                <th class="p-2 md:p-4 text-center">GF</th>
                                <th class="p-2 md:p-4 text-center">GA</th>
                                <th class="p-2 md:p-4 text-center">GD</th>
                                <th class="p-2 md:p-4 text-center">Pts</th>
                                <th class="p-2 md:p-4 text-center">Form</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            <tr v-for="team in standings" :key="team.team"
                                class="hover:bg-gray-100 transition duration-300 ease-in-out transform hover:scale-105">
                                <td class="p-2 md:p-4 font-semibold">
                                    <span :class="getPositionClass(team.position)"
                                        class="inline-block w-6 h-6 text-center rounded">
                                        {{ team.position }}
                                    </span>
                                </td>
                                <td class="p-2 md:p-4 font-medium text-gray-800">{{ team.team }}</td>
                                <td class="p-2 md:p-4 text-center">{{ team.played }}</td>
                                <td class="p-2 md:p-4 text-center">{{ team.won }}</td>
                                <td class="p-2 md:p-4 text-center">{{ team.drawn }}</td>
                                <td class="p-2 md:p-4 text-center">{{ team.lost }}</td>
                                <td class="p-2 md:p-4 text-center">{{ team.goalsFor }}</td>
                                <td class="p-2 md:p-4 text-center">{{ team.goalsAgainst }}</td>
                                <td class="p-2 md:p-4 text-center font-semibold text-gray-700">
                                    {{ team.goalsFor - team.goalsAgainst }}
                                </td>
                                <td class="p-2 md:p-4 text-center font-bold text-green-600">
                                    {{ team.points }}
                                </td>
                                <td class="p-2 md:p-4">
                                    <div class="flex gap-1 justify-center">
                                        <span v-for="(result, index) in team.form" :key="index"
                                            :class="getFormBadgeColor(result)"
                                            class="w-5 h-5 md:w-6 md:h-6 rounded-full flex items-center justify-center text-white text-[10px] md:text-xs font-bold shadow-md">
                                            {{ result }}
                                        </span>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

</template>

<script setup>
import { reactive } from 'vue';
import Navbar from '@/components/Navbar.vue';

const standings = reactive([
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
        form: ['W', 'W', 'D', 'W', 'L']
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
        form: ['W', 'L', 'W', 'W', 'W']
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
        form: ['D', 'W', 'W', 'L', 'W']
    }
]);

function getFormBadgeColor(result) {
    switch (result) {
        case 'W': return 'bg-green-500';
        case 'D': return 'bg-yellow-500';
        case 'L': return 'bg-red-500';
        default: return 'bg-gray-500';
    }
}

function getPositionClass(position) {
    if (position === 1) return 'bg-green-400 text-white';
    if (position === 2) return 'bg-green-400 text-white';
    if (position === 3) return 'bg-red-600 text-white';
    return 'text-gray-700';
}
</script>

<style>
/* Mobile Optimizations */
body {
    font-size: 14px;
}

/* Add subtle hover effect for table rows */
tr:hover {
    background-color: #f1f5f9;
}
</style>