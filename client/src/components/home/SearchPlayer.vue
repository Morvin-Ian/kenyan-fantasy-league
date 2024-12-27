<template>
    <div class="bg-white mt-4 p-4 sm:p-3 md:p-6 lg:p-8">
      <div class="mx-auto max-w-7xl">
        <h1 class="text-sm sm:text-base md:text-lg font-semibold text-gray-800 mb-4 sm:mb-6">
          Fantasy Player Search
        </h1>
  
        <!-- Search and Filters -->
        <div class="space-y-2 sm:space-y-4 md:space-y-0 flex flex-col md:flex-row md:items-center md:gap-4 mb-4 sm:mb-6">
          <div class="relative flex-1">
            <input
              v-model="filters.name"
              type="text"
              placeholder="Search by name"
              class="w-full pl-8 pr-3 py-1 sm:py-2 rounded-md sm:rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors text-xs sm:text-sm"
            />
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4 sm:h-5 sm:w-5 absolute left-2 top-1/2 -translate-y-1/2 text-gray-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
  
          <select
            v-model="filters.position"
            class="w-full sm:w-auto py-1 sm:py-2 px-3 sm:px-4 rounded-md sm:rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors text-xs sm:text-sm"
          >
            <option value="">All Positions</option>
            <option value="GKP">Goalkeeper</option>
            <option value="DEF">Defender</option>
            <option value="MID">Midfielder</option>
            <option value="ST">Striker</option>
          </select>
  
          <select
            v-model="filters.team"
            class="w-full sm:w-auto py-1 sm:py-2 px-3 sm:px-4 rounded-md sm:rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors text-xs sm:text-sm"
          >
            <option value="">All Teams</option>
            <option value="Manchester United">Manchester United</option>
            <option value="Real Madrid">Real Madrid</option>
            <option value="Barcelona">Barcelona</option>
          </select>
  
          <button
            @click="clearFilters"
            class="w-full sm:w-auto px-4 sm:px-6 py-2 sm:py-2 bg-red-500 hover:bg-red-600 text-white rounded-md sm:rounded-lg transition-colors flex items-center justify-center gap-1 sm:gap-2 text-xs sm:text-sm"
          >
            Clear
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4 sm:h-5 sm:w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>
  
        <!-- Player Table -->
        <div class="overflow-x-auto bg-white rounded-lg shadow-sm">
          <table class="min-w-full divide-y divide-gray-200 text-xs sm:text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 sm:px-6 py-2 sm:py-4 text-left font-medium text-gray-500 uppercase tracking-wider">
                  Player
                </th>
                <th class="px-4 sm:px-6 py-2 sm:py-4 text-left font-medium text-gray-500 uppercase tracking-wider">
                  Position
                </th>
                <th class="px-4 sm:px-6 py-2 sm:py-4 text-left font-medium text-gray-500 uppercase tracking-wider">
                  UCI Ranking
                </th>
                <th class="px-4 sm:px-6 py-2 sm:py-4 text-left font-medium text-gray-500 uppercase tracking-wider">
                  Form
                </th>
                <th class="px-4 sm:px-6 py-2 sm:py-4 text-left font-medium text-gray-500 uppercase tracking-wider">
                  Fantasy Points
                </th>
                <th class="px-4 sm:px-6 py-2 sm:py-4 text-left font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr
                v-for="player in filteredPlayers"
                :key="player.id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-4 sm:px-6 py-2 sm:py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="h-10 w-10 sm:h-12 sm:w-12 flex-shrink-0">
                      <img
                        :src="player.image"
                        :alt="player.name"
                        class="h-10 w-10 sm:h-12 sm:w-12 rounded-md object-cover shadow-sm"
                      />
                    </div>
                    <div class="ml-2 sm:ml-4">
                      <div class="font-medium text-gray-900">{{ player.name }}</div>
                      <div class="text-gray-500">{{ player.team }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-4 sm:px-6 py-2 sm:py-4">
                  <span
                    class="px-2 sm:px-3 py-1 text-xs sm:text-sm rounded-full"
                    :class="{
                      'bg-yellow-100 text-yellow-800': player.position === 'GKP',
                      'bg-blue-100 text-blue-800': player.position === 'DEF',
                      'bg-green-100 text-green-800': player.position === 'MID',
                      'bg-red-100 text-red-800': player.position === 'ST'
                    }"
                  >
                    {{ player.position }}
                  </span>
                </td>
                <td class="px-4 sm:px-6 py-2 sm:py-4">{{ player.uciRanking }}</td>
                <td class="px-4 sm:px-6 py-2 sm:py-4">{{ player.form }}%</td>
                <td class="px-4 sm:px-6 py-2 sm:py-4">{{ player.fantasyPoints }}</td>
                <td class="px-4 sm:px-6 py-2 sm:py-4">
                  <button
                    @click="addPlayer(player)"
                    class="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
                  >
                    Add Player
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </template>
  
  
  <script setup>
  import { reactive, computed } from "vue";
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
  ]);
  
  const filteredPlayers = computed(() => {
    return players.filter((player) => {
      const matchesName = player.name.toLowerCase().includes(filters.name.toLowerCase());
      const matchesPosition = !filters.position || player.position === filters.position;
      const matchesTeam = !filters.team || player.team === filters.team;
      return matchesName && matchesPosition && matchesTeam;
    });
  });
  
  const clearFilters = () => {
    filters.name = "";
    filters.position = "";
    filters.team = "";
  };
  
  const addPlayer = (player) => {
    alert(`Added ${player.name} to your fantasy team!`);
  };
  </script>