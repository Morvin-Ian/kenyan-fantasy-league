<template>
  <div class="bg-gradient-to-br from-gray-50 to-blue-50 p-4 sm:p-6 md:p-8 rounded-2xl mx-2 sm:mx-4 shadow-lg mb-3">
    <div class=" mx-auto">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-md overflow-hidden border border-gray-100 h-full">
            <div class="bg-gray-50 px-4 sm:px-6 py-4 border-b border-gray-200">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <h2 class="text-xl md:text-2xl font-bold text-gray-900">
                  Gameweek {{ gameweekStatus.gameweek.number }}
                </h2>
                <span class="bg-gray-800 text-xs sm:text-sm text-white font-semibold px-3 py-1.5 rounded-full w-fit">
                  {{ gameweekStatus.gameweek.status }}
                </span>
              </div>
            </div>

            <!-- Match Days Table -->
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th class="py-3 px-4 text-left text-xs sm:text-sm font-semibold text-gray-600">Matchday</th>
                    <th class="py-3 px-4 text-right text-xs sm:text-sm font-semibold text-gray-600">Match Status</th>
                    <th class="py-3 px-4 text-right text-xs sm:text-sm font-semibold text-gray-600">Bonus Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(day, index) in gameweekStatus.match_days" :key="index"
                    class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td class="py-3 px-4">
                      <div class="flex items-center gap-3">
                        <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-gray-200 flex items-center justify-center flex-shrink-0">
                          <span class="text-sm sm:text-base font-bold text-gray-800">{{ day.date }}</span>
                        </div>
                        <div class="min-w-0">
                          <div class="font-semibold text-gray-900 text-sm sm:text-base truncate">
                            {{ day.name }}
                          </div>
                          <div class="text-xs text-gray-500 font-medium">
                            {{ day.month }}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="py-3 px-4 text-right">
                      <span class="inline-block bg-gray-100 text-gray-700 px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap">
                        {{ day.match_status }}
                      </span>
                    </td>
                    <td class="py-3 px-4 text-right">
                      <span class="inline-block bg-gray-100 text-gray-700 px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap">
                        {{ day.bonus_status }}
                      </span>
                    </td>
                  </tr>
                  
                  <!-- League Tables Row -->
                  <tr class="bg-gray-50">
                    <td class="py-3 px-4">
                      <span class="font-semibold text-gray-700 text-sm sm:text-base">League Tables</span>
                    </td>
                    <td colspan="2" class="py-3 px-4 text-right">
                      <span class="inline-block bg-gray-900 text-white px-3 py-1 rounded-full text-xs font-semibold">
                        UPDATED
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Team of the Week Section - Takes 1 column on large screens -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-xl shadow-md overflow-hidden border border-gray-100 h-full flex flex-col">
            <!-- Header -->
            <div class="bg-gray-800 p-4 sm:p-6 flex-shrink-0">
              <div class="flex items-start gap-3">
                <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 sm:h-6 sm:w-6 text-gray-300"
                    fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <div class="min-w-0">
                  <h2 class="text-lg sm:text-xl font-bold text-white">
                    Team of the Week
                    <span class="block sm:inline text-sm font-normal text-gray-300 mt-1 sm:mt-0">
                      {{ isTeamWeekComplete ? '(Complete)' : '(Incomplete)' }}
                    </span>
                  </h2>
                  <p class="text-gray-300 text-xs sm:text-sm mt-1">Top performers from GW{{ gameweekStatus.gameweek.number }}</p>
                </div>
              </div>
            </div>

            <!-- Players Table -->
            <div class="flex-1 overflow-x-auto">
              <table class="w-full text-xs sm:text-sm">
                <thead class="sticky top-0 bg-white border-b border-gray-200">
                  <tr class="text-gray-600 font-semibold">
                    <th class="py-3 px-3 text-center">#</th>
                    <th class="py-3 px-3 text-left">Pos</th>
                    <th class="py-3 px-3 text-left">Player</th>
                    <th class="py-3 px-3 text-right">Pts</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!isTeamComplete">
                    <td colspan="4" class="py-8 text-center text-gray-500 text-sm font-medium">
                      {{ errorMessage }}
                    </td>
                  </tr>
                  <tr v-else v-for="(player, index) in formattedTeamOfWeek" :key="index"
                    class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td class="py-2.5 px-3 text-center text-gray-400 font-medium">{{ index + 1 }}</td>
                    <td class="py-2.5 px-3">
                      <span :class="{
                        'bg-yellow-100 text-yellow-800': player.position === 'GKP',
                        'bg-gray-100 text-gray-800': player.position === 'DEF',
                        'bg-green-100 text-green-800': player.position === 'MID',
                        'bg-red-100 text-red-800': player.position === 'FWD'
                      }" class="px-2 py-1 rounded-md text-xs font-semibold inline-block">
                        {{ player.position }}
                      </span>
                    </td>
                    <td class="py-2.5 px-3">
                      <div class="min-w-0">
                        <div class="font-semibold text-gray-900 truncate">{{ player.name }}</div>
                        <div class="text-xs text-gray-500 truncate">{{ player.club }}</div>
                      </div>
                    </td>
                    <td class="py-2.5 px-3 text-right font-bold text-base" :class="{
                      'text-green-600': player.points > 12,
                      'text-gray-600': player.points > 9 && player.points <= 12,
                      'text-gray-900': player.points <= 9
                    }">{{ player.points }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Total Points Footer -->
            <div v-if="isTeamComplete" class="border-t border-gray-200 bg-gray-50 p-4 flex-shrink-0">
              <div class="flex items-center justify-between">
                <span class="text-sm font-semibold text-gray-600">Total Points</span>
                <span class="text-2xl font-bold text-gray-900">{{ totalPoints }}</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useFantasyStore } from '@/stores/fantasy';
import { storeToRefs } from 'pinia';

const fantasyStore = useFantasyStore();
const { gameweekStatus, teamOfWeek } = storeToRefs(fantasyStore);

const formattedTeamOfWeek = ref([]);
const isTeamWeekComplete = ref(false);
const errorMessage = ref('Team of the Week not available');

const isTeamComplete = computed(() => formattedTeamOfWeek.value && formattedTeamOfWeek.value.length > 0);
const totalPoints = computed(() => isTeamComplete.value ? formattedTeamOfWeek.value.reduce((sum, p) => sum + p.points, 0) : 0);

const fetchTeamOfWeek = async () => {
  try {
    await fantasyStore.fetchTeamOfWeek();

    const data = teamOfWeek.value; 
    if (!data) return;

    const formatted = [];

    data.goalkeeper?.slice(0, 1).forEach((gkp) => {
      formatted.push(formatPlayer(gkp, 'GKP'));
    });

    isTeamWeekComplete.value = data.complete;

    data.defenders
      ?.sort((a, b) => b.fantasy_points - a.fantasy_points)
      .slice(0, 5)
      .forEach((def) => formatted.push(formatPlayer(def, 'DEF')));

    data.midfielders
      ?.sort((a, b) => b.fantasy_points - a.fantasy_points)
      .slice(0, 5)
      .forEach((mid) => formatted.push(formatPlayer(mid, 'MID')));

    data.forwards
      ?.sort((a, b) => b.fantasy_points - a.fantasy_points)
      .slice(0, 3)
      .forEach((fwd) => formatted.push(formatPlayer(fwd, 'FWD')));

    formattedTeamOfWeek.value = formatted;
  } catch (err) {
    console.error('Error fetching team of the week:', err);
  }
};

const formatPlayer = (player, position) => ({
  position,
  name: player.name,
  club: player.team,
  clubColor: getClubColor(player.team),
  points: player.fantasy_points,
});

const getClubColor = (team) => {
  const colors = {
    'AFC Leopards': 'red',
    'Gor Mahia': 'green',
    'Posta Rangers': 'orange',
    'Kakamega Homeboyz': 'yellow',
    'Nairobi United': 'purple',
    'Mara Sugar': 'blue',
  };
  return colors[team] || 'gray';
};

onMounted(async () => {
  await fetchTeamOfWeek();
});
</script>

<style scoped>
* {
  transition-property: background-color, border-color, color;
  transition-duration: 150ms;
  transition-timing-function: ease-in-out;
}

table {
  border-collapse: separate;
  border-spacing: 0;
}

thead {
  position: sticky;
  top: 0;
  z-index: 10;
}
</style>