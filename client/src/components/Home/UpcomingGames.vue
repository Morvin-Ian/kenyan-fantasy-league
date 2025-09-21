<template>
  <div class="bg-gradient-to-br from-gray-50 to-blue-50 p-4 sm:p-6 md:p-8 rounded-2xl mx-2 sm:mx-4 shadow-lg mb-3">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:justify-between items-start gap-4">
      <div class="animate-fade-in">
        <h2 class="text-xl sm:text-2xl font-bold text-gray-700 bg-clip-text">
          Upcoming Matches
        </h2>
        <p class="text-sm sm:text-base text-gray-500 mt-1 sm:mt-2">
          Stay updated with the latest fixtures
        </p>
      </div>
      <div class="flex items-center gap-2 sm:gap-4 justify-start">
        <router-link to="/fixtures"
          class="flex items-center gap-1 sm:gap-2 text-blue-600 hover:text-blue-700 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-4 sm:h-4" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <span class="text-xs sm:text-sm font-medium">Full Calendar</span>
        </router-link>
        <div class="flex gap-1 sm:gap-2">
          <button @click="scroll('left')"
            class="p-1 sm:p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
          <button @click="scroll('right')"
            class="p-1 sm:p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Matches Container -->
    <div ref="scrollContainer" class="flex gap-3 sm:gap-4 md:gap-6 overflow-x-auto pb-4 sm:pb-6 mt-4 hide-scrollbar">
      <div v-for="(game, index) in activeStandings" :key="game.id" :style="{ animationDelay: `${index * 100}ms` }"
        class="animate-slide-up flex-shrink-0 w-56 sm:w-64 md:w-72 rounded-xl sm:rounded-2xl bg-white border-2 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 group"
        :class="[
          game.status === 'upcoming' ? 'border-gray-100 shadow-lg' : 'border-gray-100 shadow-md',
          game.status === 'postponed' ? 'opacity-75' : '',
          game.status === 'live' ? '' : '',
        ]">
        <div class="p-3 sm:p-4 md:p-6 space-y-3 sm:space-y-4">
          <!-- League & Status -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 sm:gap-3">
              <div
                class="w-8 h-8 sm:w-10 sm:h-10 bg-gray-50 rounded-full p-2 group-hover:scale-110 transition-transform duration-300">
                <img :src="game.home_team?.logo_url || defaultLogo" :alt="`${game.home_team.name} logo`"
                  class="w-full h-full object-contain" />
              </div>
            </div>
            <div :class="[
              'px-2 sm:px-3 py-1 rounded-full text-xs font-bold tracking-wide transition-colors duration-300',
              {
                'bg-blue-100 text-blue-700 group-hover:bg-blue-200': game.status === 'upcoming',
                'bg-gray-100 text-gray-600 group-hover:bg-gray-200': game.status === 'completed',
                'bg-red-100 text-red-700 animate-pulse': game.status === 'live',
                'bg-red-50 text-red-600 group-hover:bg-red-100': game.status === 'postponed',
              },
            ]">
              {{ game.status.toUpperCase() }}
            </div>
          </div>

          <!-- Teams -->
          <div class="space-y-1">
            <!-- Live Match (with scores) -->
            <template v-if="game.status === 'live' || game.status === 'completed'">
              <div class="flex items-center justify-between text-sm sm:text-base font-bold">
                <span class="text-gray-900">{{ game.home_team.name }}</span>
                <span class="px-2 py-0.5 rounded-md text-xs sm:text-sm font-extrabold" :class="{
                  'bg-red-100 text-red-600': game.status === 'live',
                  'bg-gray-50 text-gray-600': game.status === 'completed'
                }">
                  {{ game.home_team_score }}
                </span>
              </div>
              <div class="flex items-center justify-between text-sm sm:text-base font-bold">
                <span class="text-gray-900">{{ game.away_team.name }}</span>
                <span class="px-2 py-0.5 rounded-md text-xs sm:text-sm font-extrabold" :class="{
                  'bg-red-100 text-red-600': game.status === 'live',
                  'bg-gray-50 text-gray-600': game.status === 'completed'
                }">
                  {{ game.away_team_score }}
                </span>
              </div>
            </template>

            <!-- Non-live Match -->
            <template v-else>
              <div class="text-xs sm:text-sm font-medium text-gray-900">
                {{ game.home_team.name }}
              </div>
              <div class="text-xs sm:text-sm font-medium text-gray-900">
                {{ game.away_team.name }}
              </div>
            </template>
          </div>

          <!-- Date & Time -->
          <div class="flex items-center gap-2 pt-2 border-t border-gray-100">
            <div class="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-4 sm:h-4" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <span>{{ formatDatePart(game.match_date || game.datetime) }}</span>
              <span class="text-gray-300">•</span>
              <span>{{ formatTimePart(game.match_date || game.datetime) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- League Standings Header with View Full Table link -->
    <div class="animate-fade-in mb-6 flex flex-col sm:flex-row sm:justify-between items-start sm:items-center">
      <div>
        <h2 class="text-xl sm:text-2xl font-bold text-gray-700 bg-clip-text">
          League Standings
        </h2>
        <p class="text-sm sm:text-base text-gray-500 mt-1 sm:mt-2">
          Stay updated with the latest standings
        </p>
      </div>
      <router-link to="/standings"
        class="flex items-center gap-1 sm:gap-2 text-blue-600 hover:text-blue-700 transition-colors mt-2 sm:mt-0">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-4 sm:h-4" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
        <span class="text-xs sm:text-sm font-medium">View Full Table</span>
      </router-link>
    </div>

    <div
      class="bg-white rounded-xl md:rounded-3xl shadow-lg md:shadow-xl p-4 md:p-8 border border-gray-100 overflow-hidden relative">

      <div class="overflow-x-auto relative">
        <table class="w-full min-w-full table-auto">
          <thead>
            <tr class="border-b border-gray-100">
              <th
                class="py-3 px-2 sm:px-4 text-left text-gray-500 font-semibold uppercase tracking-wider text-xs sm:text-sm">
                Pos</th>
              <th
                class="py-3 px-2 sm:px-4 text-left text-gray-500 font-semibold uppercase tracking-wider text-xs sm:text-sm">
                Team</th>
              <th
                class="py-3 px-2 sm:px-4 text-center text-gray-500 font-semibold uppercase tracking-wider text-xs sm:text-sm">
                MP</th>
              <th
                class="py-3 px-2 sm:px-4 text-center text-gray-500 font-semibold uppercase tracking-wider text-xs sm:text-sm">
                W</th>
              <th
                class="py-3 px-2 sm:px-4 text-center text-gray-500 font-semibold uppercase tracking-wider text-xs sm:text-sm">
                D</th>
              <th
                class="py-3 px-2 sm:px-4 text-center text-gray-500 font-semibold uppercase tracking-wider text-xs sm:text-sm">
                L</th>
              <th
                class="py-3 px-2 sm:px-4 text-center text-gray-500 font-semibold uppercase tracking-wider text-xs sm:text-sm">
                GF</th>
              <th
                class="py-3 px-2 sm:px-4 text-center text-gray-500 font-semibold uppercase tracking-wider text-xs sm:text-sm">
                GA</th>
              <th
                class="py-3 px-2 sm:px-4 text-center text-gray-500 font-semibold uppercase tracking-wider text-xs sm:text-sm">
                GD</th>
              <th
                class="py-3 px-2 sm:px-4 text-center text-gray-500 font-semibold uppercase tracking-wider text-xs sm:text-sm">
                PTS</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(team, index) in firstFiveStandings" :key="team.id"
              class="border-b hover:bg-gray-50 transition-colors">
              <td class="py-3 md:py-4 px-2 md:px-4 font-medium text-xs sm:text-sm"
                :class="{ 'text-gray-600': index < 4, 'text-red-500': index > 16 }">{{ index + 1 }}</td>
              <td class="py-3 md:py-4 px-2 md:px-4">
                <div class="flex items-center space-x-2 md:space-x-3">
                  <span class="font-medium text-gray-900 text-xs sm:text-sm">{{ team.team.name }}</span>
                </div>
              </td>
              <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-xs sm:text-sm">{{ team.played }}</td>
              <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-xs sm:text-sm">{{ team.wins }}</td>
              <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-xs sm:text-sm">{{ team.draws }}</td>
              <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-xs sm:text-sm">{{ team.losses }}</td>
              <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-xs sm:text-sm">{{ team.goals_for }}
              </td>
              <td class="py-3 md:py-4 px-2 md:px-4 text-center text-gray-700 text-xs sm:text-sm">{{ team.goals_against
              }}
              </td>
              <td class="py-3 md:py-4 px-2 md:px-4 text-center font-medium text-xs sm:text-sm"
                :class="{ 'text-green-500': team.goalDifference > 0, 'text-red-500': team.goalDifference < 0 }">{{
                  team.goal_differential }}</td>
              <td class="py-3 md:py-4 px-2 md:px-4 text-center font-bold text-gray-900 text-xs sm:text-sm">{{
                team.points }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Visual indicator that table scrolls horizontally (mobile only) -->
      <div class="flex justify-center mt-3 md:hidden">
        <div class="flex space-x-1 items-center text-xs text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 animate-pulse" fill="none"
            viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          <span>Swipe right to see more</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 animate-pulse" fill="none"
            viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type { Fixture, TeamStanding } from "src/helpers/types/team";
import defaultLogo from "../../assets/logo.png";

const props = defineProps({
  fixtures: {
    type: Array as () => Fixture[],
    required: true
  },
  standings: {
    type: Array as () => TeamStanding[],
    required: true
  }
});

const activeStandings = computed(() =>
  props.fixtures.filter(fixture => fixture.is_active)
);

const firstFiveStandings = computed(() => props.standings.slice(0, 5));

const scrollContainer = ref<HTMLElement | null>(null);

const scroll = (direction: "left" | "right") => {
  if (!scrollContainer.value) return;

  const scrollAmount = window.innerWidth < 640 ? 230 : 280;
  const isLeft = direction === "left";

  scrollContainer.value.scrollBy({
    left: isLeft ? -scrollAmount : scrollAmount,
    behavior: "smooth",
  });
};

const toUpperCase = (text: string) => {
  return text.toUpperCase();
};

function getRandomFormResults(): string[] {
  const results = ['W', 'D', 'L'];
  const form = [];
  for (let i = 0; i < 5; i++) {
    form.push(results[Math.floor(Math.random() * results.length)]);
  }
  return window.innerWidth < 640 ? form.slice(0, 3) : form;
}

function getFormBadgeColor(result: string): string {
  const formResults = ["W", "D", "L"];
  if (!formResults.includes(result)) return "bg-gray-500"; // Default color for unexpected values
  return result === "W" ? "bg-green-500" : result === "D" ? "bg-yellow-500" : "bg-red-500";
}

const formatDatePart = (dateStr?: string) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  }).format(date);
};

const formatTimePart = (dateStr?: string) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true
  }).format(date);
};
</script>


<style scoped>
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

.animate-fade-in {
  animation: fadeIn 0.6s ease-out;
}

.animate-slide-in {
  animation: slideIn 0.6s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out forwards;
  opacity: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Add smooth transitions for all interactive elements */
button,
a {
  transition: all 0.3s ease;
}

@media (max-width: 640px) {
  .animate-slide-up {
    animation-duration: 0.5s;
  }
}
</style>