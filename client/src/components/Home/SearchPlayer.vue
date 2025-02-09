<template>
    <div class="bg-gradient-to-br from-gray-50 to-blue-50 p-8 rounded-2xl mx-4 shadow-lg mb-8">
        <div
            class="bg-white rounded-2xl shadow-2xl overflow-hidden "
        >
            <div class="p-8">
                <h1 class="text-2xl font-bold text-gray-700 bg-clip-text flex items-center">
                    Fantasy Player Search
                </h1>
            </div>

            <!-- Search and Filters -->
            <div class="p-8 bg-gray-50 border-b">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div class="relative">
                        <input
                            v-model="filters.name"
                            type="text"
                            placeholder="Search by name"
                            class="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                        />
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="absolute left-4 top-3.5 h-5 w-5 text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                            />
                        </svg>
                    </div>

                    <select
                        v-model="filters.position"
                        class="w-full py-3 px-4 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 transition-all duration-300"
                    >
                        <option value="">All Positions</option>
                        <option value="GKP">Goalkeeper</option>
                        <option value="DEF">Defender</option>
                        <option value="MID">Midfielder</option>
                        <option value="ST">Striker</option>
                    </select>

                    <select
                        v-model="filters.team"
                        class="w-full py-3 px-4 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 transition-all duration-300"
                    >
                        <option value="">All Teams</option>
                        <option value="Manchester United">
                            Manchester United
                        </option>
                        <option value="Real Madrid">Real Madrid</option>
                        <option value="Barcelona">Barcelona</option>
                    </select>

                    <button
                        @click="clearFilters"
                        class="hover:bg-red-100 text-red-500 rounded-lg transition-all duration-300 flex items-center justify-center px-4 py-3"
                    >
                        Clear Filters
                    </button>
                </div>
            </div>

            <!-- Player Table -->
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-blue-100">
                        <tr>
                            <th class="px-8 py-4 text-left">Player</th>
                            <th class="px-8 py-4 text-left">Position</th>
                            <th class="px-8 py-4 text-left">UCI Ranking</th>
                            <th class="px-8 py-4 text-left">Form</th>
                            <th class="px-8 py-4 text-left">Fantasy Points</th>
                            <th class="px-8 py-4 text-left">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr
                            v-for="player in paginatedPlayers"
                            :key="player.id"
                            class="border-b hover:bg-blue-50 transition-all duration-300"
                        >
                            <td class="px-8 py-6">
                                <div class="flex items-center">
                                    <img
                                        :src="player.image"
                                        :alt="player.name"
                                        class="h-14 w-14 rounded-full object-cover mr-4 shadow-lg transition-all duration-300 hover:scale-105"
                                    />
                                    <div>
                                        <div
                                            class="font-semibold text-gray-800"
                                        >
                                            {{ player.name }}
                                        </div>
                                        <div class="text-gray-500 text-sm">
                                            {{ player.team }}
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-8 py-6">
                                <span
                                    class="px-4 py-2 rounded-full text-xs font-semibold"
                                    :class="{
                                        'bg-yellow-100 text-yellow-800':
                                            player.position === 'GKP',
                                        'bg-blue-100 text-blue-800':
                                            player.position === 'DEF',
                                        'bg-green-100 text-green-800':
                                            player.position === 'MID',
                                        'bg-red-100 text-red-800':
                                            player.position === 'ST',
                                    }"
                                >
                                    {{ player.position }}
                                </span>
                            </td>
                            <td class="px-8 py-6">{{ player.uciRanking }}</td>
                            <td class="px-8 py-6">{{ player.form }}%</td>
                            <td class="px-8 py-6">
                                {{ player.fantasyPoints }}
                            </td>
                            <td class="px-8 py-6">
                                <button
                                    @click="addPlayer(player)"
                                    class="px-6 py-2 bg-blue-100 text-blue-800 rounded-lg transition-all duration-300 hover:bg-blue-200 hover:text-blue-900"
                                >
                                    Add Player
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div class="flex justify-center items-center p-8 bg-gray-50">
                <div class="flex space-x-4">
                    <button
                        @click="currentPage = currentPage - 1"
                        :disabled="currentPage === 1"
                        class="px-6 py-2 bg-blue-100 text-blue-800 rounded-lg transition-all duration-300 hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        << Previous
                    </button>
                    <span class="px-6 py-2 text-sm text-gray-700">
                        Page {{ currentPage }} of {{ totalPages }}
                    </span>
                    <button
                        @click="currentPage = currentPage + 1"
                        :disabled="currentPage === totalPages"
                        class="px-6 py-2 bg-blue-100 text-blue-800 rounded-lg transition-all duration-300 hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Next >>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed } from "vue";
import player3 from "@/assets/images/player3.png";
import player2 from "@/assets/images/player2.png";

const filters = reactive({
    name: "",
    position: "",
    team: "",
});

const players = reactive([
    {
        id: 1,
        name: "Cristiano Ronaldo",
        image: player3,
        position: "ST",
        uciRanking: 1,
        form: 90,
        fantasyPoints: 12000,
        team: "Al-Nassr",
    },
    {
        id: 2,
        name: "Lionel Messi",
        image: player2,
        position: "MID",
        uciRanking: 2,
        form: 95,
        fantasyPoints: 15000,
        team: "Inter Miami",
    },
    {
        id: 3,
        name: "David de Gea",
        image: player2,
        position: "GKP",
        uciRanking: 10,
        form: 10,
        fantasyPoints: 5000,
        team: "Manchester United",
    },
    {
        id: 4,
        name: "Kylian Mbappé",
        image: player3,
        position: "ST",
        uciRanking: 3,
        form: 88,
        fantasyPoints: 11500,
        team: "Real Madrid",
    },
    {
        id: 5,
        name: "Erling Haaland",
        image: player2,
        position: "ST",
        uciRanking: 4,
        form: 92,
        fantasyPoints: 13000,
        team: "Manchester United",
    },
]);

const currentPage = ref(1);
const playersPerPage = ref(3);

const filteredPlayers = computed(() => {
    return players.filter((player) => {
        const matchesName = player.name
            .toLowerCase()
            .includes(filters.name.toLowerCase());
        const matchesPosition =
            !filters.position || player.position === filters.position;
        const matchesTeam = !filters.team || player.team === filters.team;
        return matchesName && matchesPosition && matchesTeam;
    });
});

const totalPages = computed(() =>
    Math.ceil(filteredPlayers.value.length / playersPerPage.value),
);

const paginatedPlayers = computed(() => {
    const start = (currentPage.value - 1) * playersPerPage.value;
    const end = start + playersPerPage.value;
    return filteredPlayers.value.slice(start, end);
});

const clearFilters = () => {
    filters.name = "";
    filters.position = "";
    filters.team = "";
    currentPage.value = 1;
};

const addPlayer = (player) => {
    alert(`Added ${player.name} to your fantasy team!`);
};
</script>
