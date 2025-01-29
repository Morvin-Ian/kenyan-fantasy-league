<template>
    <div>
        <Navbar />
    </div>
    <div
        class="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 p-4 md:p-10"
    >
        <div class="mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden">
            <!-- Animated Header -->
            <div class="bg-white p-6 text-center relative">
                <h1
                    class="text-3xl font-extrabold text-gray-700 tracking-wide flex items-center justify-center space-x-4"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-10 w-10"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path
                            fill-rule="evenodd"
                            d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z"
                            clip-rule="evenodd"
                        />
                        <path
                            d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z"
                        />
                    </svg>
                    <span>Kenyan Premier League Standings</span>
                </h1>
                <div
                    class="absolute bottom-0 left-0 right-0 h-1 bg-red-600 animate-pulse"
                ></div>
            </div>

            <!-- Standings Table -->
            <div class="p-6 overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-green-100 text-green-800">
                        <tr>
                            <th
                                v-for="header in tableHeaders"
                                :key="header"
                                class="p-3 text-center font-semibold"
                            >
                                {{ header }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr
                            v-for="team in standings"
                            :key="team.team"
                            class="hover:bg-green-50 transition-all duration-300 transform hover:scale-[1.01]"
                        >
                            <td class="p-3 text-center">
                                <span
                                    :class="getPositionClass(team.position)"
                                    class="inline-block w-8 h-8 rounded-full flex items-center justify-center font-bold"
                                >
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
                            <td
                                class="p-3 text-center font-bold text-green-700"
                            >
                                {{ team.points }}
                            </td>
                            <td class="p-3">
                                <div class="flex justify-center space-x-1">
                                    <span
                                        v-for="(result, index) in team.form"
                                        :key="index"
                                        :class="getFormBadgeColor(result)"
                                        class="w-6 h-6 rounded-full flex items-center justify-center text-white font-bold"
                                    >
                                        {{ result }}
                                    </span>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Performance Insights -->
            <div class="bg-green-50 p-6 grid md:grid-cols-3 gap-4">
                <div class="bg-white rounded-lg p-4 shadow-md">
                    <h3 class="text-lg font-bold text-green-700 mb-2">
                        Top Performer
                    </h3>
                    <p class="text-gray-600">
                        {{ standings[0].team }} -
                        {{ standings[0].points }} points
                    </p>
                </div>
                <div class="bg-white rounded-lg p-4 shadow-md">
                    <h3 class="text-lg font-bold text-blue-700 mb-2">
                        Goals Leader
                    </h3>
                    <p class="text-gray-600">
                        {{ standings[0].team }} -
                        {{ standings[0].goalsFor }} goals
                    </p>
                </div>
                <div class="bg-white rounded-lg p-4 shadow-md">
                    <h3 class="text-lg font-bold text-red-700 mb-2">
                        Best Defense
                    </h3>
                    <p class="text-gray-600">
                        {{ standings[0].team }} -
                        {{ standings[0].goalsAgainst }} conceded
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import Navbar from "@/components/Navbar.vue";

const tableHeaders = [
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

const standings = ref([
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

function getFormBadgeColor(result) {
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

function getPositionClass(position) {
    if (position === 1) return "bg-green-500 text-white";
    if (position === 2) return "bg-blue-500 text-white";
    if (position === 3) return "bg-yellow-500 text-white";
    return "bg-gray-200 text-gray-700";
}
</script>
