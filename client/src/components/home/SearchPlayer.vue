<template>
    <div class="bg-gradient-to-br from-blue-50 to-gray-100 p-4 md:p-6 lg:p-8">
      <div class="mx-auto max-w-7xl">
        <h1 class="text-lg md:text-lg font-semibold text-gray-800 mb-6">Fantasy Player Search</h1>
        
        <!-- Search and Filters -->
        <div class="space-y-4 md:space-y-0 md:flex md:items-center md:gap-4 mb-6">
          <div class="relative flex-1">
            <input
              v-model="filters.name"
              type="text"
              placeholder="Search by name"
              class="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
            />
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
            </svg>
          </div>
          
          <select
            v-model="filters.position"
            class="w-full md:w-48 py-2 px-4 rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
          >
            <option value="">All Positions</option>
            <option value="GKP">Goalkeeper</option>
            <option value="DEF">Defender</option>
            <option value="MID">Midfielder</option>
            <option value="ST">Striker</option>
          </select>
          
          <select
            v-model="filters.team"
            class="w-full md:w-48 py-2 px-4 rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
          >
            <option value="">All Teams</option>
            <option value="Manchester United">Manchester United</option>
            <option value="Real Madrid">Real Madrid</option>
            <option value="Barcelona">Barcelona</option>
          </select>
          
          <button
            @click="clearFilters"
            class="w-full md:w-auto px-6 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
          >
         
            Clear
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
  
        <!-- Player Table -->
        <div class="overflow-x-auto bg-white rounded-xl shadow-sm">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Player</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Position</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">UCI Ranking</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Form</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fantasy Points</th>
                <th class="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr
                v-for="player in filteredPlayers"
                :key="player.id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="h-12 w-12 flex-shrink-0">
                      <img
                        :src="player.image"
                        :alt="player.name"
                        class="h-12 w-12 rounded-lg object-cover shadow-sm"
                      />
                    </div>
                    <div class="ml-4">
                      <div class="font-medium text-gray-900">{{ player.name }}</div>
                      <div class="text-sm text-gray-500">{{ player.team }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-3 py-1 text-sm rounded-full" :class="{
                    'bg-yellow-100 text-yellow-800': player.position === 'GKP',
                    'bg-blue-100 text-blue-800': player.position === 'DEF',
                    'bg-green-100 text-green-800': player.position === 'MID',
                    'bg-red-100 text-red-800': player.position === 'ST'
                  }">
                    {{ player.position }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  #{{ player.uciRanking }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-green-500 rounded-full h-2"
                      :style="{ width: `${player.form}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-500 mt-1">{{ player.form }}%</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                  {{ player.fantasyPoints.toLocaleString() }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <button
                    @click="addPlayer(player)"
                    class="inline-flex items-center px-3 py-1 border border-transparent text-sm leading-5 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
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
      form: 70,
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