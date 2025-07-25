<template>
  <div class="bg-gradient-to-br from-gray-50 to-blue-50 p-4 sm:p-6 md:p-8 rounded-2xl mx-2 sm:mx-4 shadow-lg mb-3">
    <div class="max-w-9xl mx-auto">

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column (Status + Stats) -->
        <div class="lg:col-span-2 flex flex-col gap-6">
          <!-- Status Section -->
          <div class="animate-fade-in bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
            <div class="bg-gray-50 px-6 py-4">
              <h2 class="text-xl sm:text-2xl font-bold text-gray-900 flex items-center">
                <span class="mr-2">Gameweek 34 Status</span>
                <span class="bg-gray-600 text-xs text-white font-bold px-2 py-1 rounded-full">LIVE</span>
              </h2>
            </div>

            <div class="overflow-x-auto p-1">
              <table class="w-full">
                <thead>
                  <tr class="text-left text-gray-600 font-medium border-b border-gray-100">
                    <th class="py-3 px-8">Matchday</th>
                    <th class="py-3 px-8 text-right">Match Points</th>
                    <th class="py-3 px-8 text-right">Bonus Points</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(day, index) in gameDays" :key="index"
                    class="border-b border-gray-100 hover:bg-gray-50 transition-all duration-200">
                    <td class="py-3 px-8">
                      <div class="flex items-center">
                        <div
                          class="w-12 h-12 rounded-xl bg-gray-200 flex items-center justify-center text-gray-700 font-bold mr-4 shadow-sm">
                          {{ day.date }}
                        </div>
                        <div>
                          <div class="font-semibold text-gray-900 text-base">{{ day.name }}</div>
                          <div class="text-xs text-gray-500 font-medium">{{ day.month }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="py-3 px-8 text-right">
                      <span
                        class="bg-gray-100 text-gray-700 px-4 py-1.5 rounded-full font-medium text-sm">
                        {{ day.matchStatus }}
                      </span>
                    </td>
                    <td class="py-3 px-8 text-right">
                      <span
                        class="bg-gray-100 text-gray-700 px-4 py-1.5 rounded-full font-medium text-sm">
                        {{ day.bonusStatus }}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td class="py-3 px-8">
                      <div class="font-medium text-gray-700 flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none"
                          viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        League Tables
                      </div>
                    </td>
                    <td colspan="2" class="py-3 px-8 text-right">
                      <span
                        class="bg-gray-900 text-white px-4 py-1.5 rounded-full font-medium text-sm shadow-sm">
                        UPDATED
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Stats Section -->
          <div
            class="animate-fade-in bg-white rounded-xl shadow-xl overflow-hidden transition-all duration-300 hover:shadow-xl border border-gray-100">
            <div class="bg-gradient-to-r from-gray-800 to-gray-900 p-8">
              <h2 class="text-xl sm:text-2xl font-bold text-white mb-6 flex items-center">
                Gameweek 34 Stats
              </h2>

              <div class="grid grid-cols-2 sm:grid-cols-3 gap-5">
                <div v-for="(stat, index) in gameStats" :key="index" :style="{ animationDelay: `${index * 100}ms` }"
                  class="animate-slide-up bg-white/10 backdrop-blur-sm p-4 rounded-2xl text-gray-200 hover:bg-white/20 transition-all duration-200 transform hover:-translate-y-1 border border-white/10">
                  <div class="text-xs uppercase tracking-wider mb-2 font-medium opacity-75">{{ stat.label }}</div>
                  <div class="text-xl font-light">{{ stat.value }}</div>
                </div>
              </div>

              <button
                class="mt-6 px-4 py-2 text-center text-white font-light bg-white/20 hover:bg-white/30 rounded-xl transition-all duration-200 flex items-center justify-center group shadow-lg hover:shadow-xl border border-white/10">
                <span>View My Team</span>
                <svg xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5 ml-2 transform group-hover:translate-x-1 transition-transform duration-200"
                  fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Right Column (Team of the Week) -->
        <div
          class="animate-fade-in bg-white rounded-xl shadow-xl overflow-hidden transition-all duration-300 hover:shadow-xl border border-gray-100">
          <div class="bg-gray-800 p-8">
            <div class="flex items-center text-white mb-2">
              <div class="w-10 h-10 rounded-full bg-gray-600 flex items-center justify-center mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-300" fill="none"
                  viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
              <div>
                <h2 class="text-xl sm:text-2xl font-bold">Team of the Week</h2>
                <p class="text-gray-300 text-sm">Top performers from GW34</p>
              </div>
            </div>
          </div>

          <div class="overflow-x-auto px-4">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-100 text-gray-600 font-medium">
                  <th class="py-3 text-center">#</th>
                  <th class="py-3 text-left">Pos</th>
                  <th class="py-3 text-left">Player</th>
                  <th class="py-3 text-right">Pts</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(player, index) in teamOfWeek" :key="index"
                  class="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150">
                  <td class="py-3 text-center text-gray-400">{{ index + 1 }}</td>
                  <td class="py-3">
                    <span :class="{
                      'bg-yellow-100 text-yellow-800': player.position === 'GKP',
                      'bg-gray-100 text-gray-800': player.position === 'DEF',
                      'bg-green-100 text-green-800': player.position === 'MID',
                      'bg-red-100 text-red-800': player.position === 'FWD'
                    }" class="px-2 py-1 rounded-md text-xs font-medium">
                      {{ player.position }}
                    </span>
                  </td>
                  <td class="py-3">
                    <div class="flex items-center">
                      <span class="w-2 h-2 rounded-full" :class="{
                        'bg-red-500': player.clubColor.includes('red'),
                        'bg-gray-500': player.clubColor.includes('blue'),
                        'bg-green-500': player.clubColor.includes('green'),
                        'bg-purple-500': player.clubColor.includes('purple'),
                        'bg-orange-500': player.clubColor.includes('orange')
                      }"></span>
                      <span class="ml-2 font-medium text-gray-900">{{ player.name }}</span>
                      <span class="ml-2 text-xs text-gray-500">{{ player.club }}</span>
                    </div>
                  </td>
                  <td class="py-3 text-right font-medium" :class="{
                    'text-green-600': player.points > 12,
                    'text-gray-600': player.points > 9 && player.points <= 12,
                    'text-gray-900': player.points <= 9
                  }">{{ player.points }}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="4" class="py-4 text-right">
                    <div class="flex items-center justify-end">
                      <span class="font-bold text-lg text-gray-900 mr-1">{{ totalPoints }}</span>
                      <span class="text-gray-600">Total Points</span>
                    </div>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';


const gameDays = ref([
    { name: 'Saturday', date: '26', month: 'Apr', matchStatus: 'CONFIRMED', bonusStatus: 'ADDED' },
    { name: 'Sunday', date: '27', month: 'Apr', matchStatus: 'CONFIRMED', bonusStatus: 'ADDED' },
    { name: 'Thursday', date: '1', month: 'May', matchStatus: 'CONFIRMED', bonusStatus: 'ADDED' }
]);

const gameStats = ref([
    { label: 'Highest Points', value: '132' },
    { label: 'Average Points', value: '47' },
    { label: 'Transfers Made', value: '23.7M' },
    { label: 'Most Transferred', value: 'Olunga' },
    { label: 'Wildcards Played', value: '310K' },
    { label: 'Most Captained', value: 'Akumu' }
]);

const teamOfWeek = ref([
    { position: 'GKP', name: 'Origi', club: 'GOR', clubColor: 'text-red-600', points: 13 },
    { position: 'DEF', name: 'Otieno', club: 'KCB', clubColor: 'text-green-600', points: 15 },
    { position: 'DEF', name: 'Onyango', club: 'KCB', clubColor: 'text-green-600', points: 13 },
    { position: 'DEF', name: 'Omurwa', club: 'TUS', clubColor: 'text-blue-600', points: 11 },
    { position: 'DEF', name: 'Ochieng', club: 'GOR', clubColor: 'text-red-600', points: 11 },
    { position: 'MID', name: 'Miheso', club: 'BDH', clubColor: 'text-orange-600', points: 11 },
    { position: 'MID', name: 'Akumu', club: 'TUS', clubColor: 'text-blue-600', points: 10 },
    { position: 'MID', name: 'Muguna', club: 'GOR', clubColor: 'text-red-600', points: 10 },
    { position: 'MID', name: 'Mutinda', club: 'AFC', clubColor: 'text-purple-600', points: 10 },
    { position: 'FWD', name: 'Olunga', club: 'BDH', clubColor: 'text-orange-600', points: 15 }
]);



const totalPoints = computed(() => {
    return teamOfWeek.value.reduce((sum, player) => sum + player.points, 0);
});


</script>

<style scoped>
/* Add any component-specific styles here */
</style>