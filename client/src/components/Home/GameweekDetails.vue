<template>
  <div class="bg-gradient-to-br from-gray-50 to-blue-50 p-2 sm:p-4 md:p-6 lg:p-8 rounded-xl sm:rounded-2xl mx-1 sm:mx-2 md:mx-4 shadow-lg mb-3">
    <div class="mx-auto">
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
        <!-- Left Column (Gameweek Status) -->
        <div class="xl:col-span-2 flex flex-col gap-3 sm:gap-4 md:gap-6">
          <div class="animate-fade-in bg-white rounded-lg sm:rounded-xl shadow-md overflow-hidden border border-gray-100">
            <div class="bg-gray-50 px-4 py-3 flex items-center justify-between">
              <h2 class="text-lg md:text-xl font-bold text-gray-900 flex items-center">
                <span class="mr-2">Gameweek {{ gameweekStatus.gameweek.number }}</span>
                <span class="bg-gray-800 text-xs text-white font-semibold px-2 py-0.5 rounded-full">
                  {{ gameweekStatus.gameweek.status }}
                </span>
              </h2>
            </div>

            <!-- Table -->
            <div class="overflow-x-auto">
              <table class="w-full min-w-[400px]">
                <thead class="bg-gray-50 border-b border-gray-200">
                  <tr class="text-left text-gray-600 font-semibold text-sm">
                    <th class="py-2 px-3">Matchday</th>
                    <th class="py-2 px-3 text-right">Match Status</th>
                    <th class="py-2 px-3 text-right">Bonus Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(day, index) in gameweekStatus.match_days" :key="index"
                    class="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150">
                    <td class="py-2.5 px-3">
                      <div class="flex items-center space-x-2">
                        <div class="w-9 h-9 rounded-md bg-gray-200 flex items-center justify-center text-gray-800 font-semibold text-sm">
                          {{ day.date }}
                        </div>
                        <div>
                          <div class="font-semibold text-gray-900 text-sm leading-tight">
                            {{ day.name }}
                          </div>
                          <div class="text-xs text-gray-500 font-medium">
                            {{ day.month }}
                          </div>
                        </div>
                      </div>
                    </td>

                    <td class="py-2.5 px-3 text-right">
                      <span class="inline-block bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-xs font-medium">
                        {{ day.match_status }}
                      </span>
                    </td>

                    <td class="py-2.5 px-3 text-right">
                      <span class="inline-block bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-xs font-medium">
                        {{ day.bonus_status }}
                      </span>
                    </td>
                  </tr>

                  <tr>
                    <td class="py-2.5 px-3">
                      <div class="font-medium text-gray-700 text-sm">
                        League Tables
                      </div>
                    </td>
                    <td colspan="2" class="py-2.5 px-3 text-right">
                      <span class="bg-gray-900 text-white px-2 py-0.5 rounded-full text-xs font-semibold shadow-sm">
                        UPDATED
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Right Column (Team of the Week) -->
        <div class="animate-fade-in bg-white rounded-lg sm:rounded-xl shadow-xl overflow-hidden transition-all duration-300 hover:shadow-xl border border-gray-100">
          <div class="bg-gray-800 p-4 sm:p-6 md:p-8">
            <div class="flex items-center text-white mb-2">
              <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gray-600 flex items-center justify-center mr-2 sm:mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 md:h-6 md:w-6 text-gray-300"
                  fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
              <div>
                <h2 class="text-base sm:text-lg md:text-xl lg:text-2xl font-bold">Team of the Week {{ isTeamWeekComplete ? '- (Complete)' : '- (Incomplete)' }}</h2>
                <p class="text-gray-300 text-xs sm:text-sm">Top performers from GW{{ gameweekStatus.gameweek.number }}</p>
              </div>
            </div>
          </div>

          <div class="overflow-x-auto px-2 sm:px-4">
            <table class="w-full text-xs sm:text-sm min-w-[280px]">
              <thead>
                <tr class="border-b border-gray-100 text-gray-600 font-medium">
                  <th class="py-2 sm:py-3 text-center">#</th>
                  <th class="py-2 sm:py-3 text-left">Pos</th>
                  <th class="py-2 sm:py-3 text-left">Player</th>
                  <th class="py-2 sm:py-3 text-right">Pts</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!isTeamComplete">
                  <td colspan="4" class="p-4 text-center text-gray-500 text-sm font-medium">
                    {{ errorMessage }}
                  </td>
                </tr>
                <tr v-else v-for="(player, index) in formattedTeamOfWeek" :key="index"
                  class="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150">
                  <td class="py-2 sm:py-3 text-center text-gray-400">{{ index + 1 }}</td>
                  <td class="py-2 sm:py-3">
                    <span :class="{
                      'bg-yellow-100 text-yellow-800': player.position === 'GKP',
                      'bg-gray-100 text-gray-800': player.position === 'DEF',
                      'bg-green-100 text-green-800': player.position === 'MID',
                      'bg-red-100 text-red-800': player.position === 'FWD'
                    }" class="px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-md text-xs font-medium">
                      {{ player.position }}
                    </span>
                  </td>
                  <td class="py-2 sm:py-3">
                    <div class="flex items-center">
                      <span class="ml-1 sm:ml-2 font-medium text-gray-900 truncate">{{ player.name }}</span>
                      <span class="ml-1 sm:ml-2 text-xs text-gray-500 hidden sm:inline">{{ player.club }}</span>
                    </div>
                  </td>
                  <td class="py-2 sm:py-3 text-right font-medium" :class="{
                    'text-green-600': player.points > 12,
                    'text-gray-600': player.points > 9 && player.points <= 12,
                    'text-gray-900': player.points <= 9
                  }">{{ player.points }}</td>
                </tr>
              </tbody>
              <tfoot v-if="isTeamComplete">
                <tr>
                  <td colspan="4" class="py-3 sm:py-4 text-right">
                    <div class="flex items-center justify-end">
                      <span class="font-bold text-base sm:text-lg text-gray-900 mr-1">{{ totalPoints }}</span>
                      <span class="text-gray-600 text-xs sm:text-sm">Total Points</span>
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
import { ref, computed, onMounted } from 'vue';
import { useFantasyStore } from '@/stores/fantasy';
import { storeToRefs } from 'pinia';

const fantasyStore = useFantasyStore();
const { gameweekStatus, teamOfWeek } = storeToRefs(fantasyStore);

const formattedTeamOfWeek = ref([]);
const isTeamWeekComplete = ref(false);
const errorMessage = ref('Team of the Week data not available');

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
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.5s ease-out;
}
</style>