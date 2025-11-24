<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-2 sm:p-4">
    <div
      class="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto"
    >
      <!-- Header -->
      <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-xl font-bold text-gray-900">Match Lineups</h2>
            <p class="text-sm text-gray-600 mt-1">
              {{ fixture.home_team.name }} vs {{ fixture.away_team.name }}
            </p>
          </div>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-colors p-2 hover:bg-gray-100 rounded-lg"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Lineups Container -->
      <div class="p-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Home Team Lineup -->
          <div
            v-for="lineup in fixture.lineups"
            :key="lineup.id"
            class="bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-200 p-6"
          >
            <!-- Team Header -->
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center space-x-3">
                <img
                  v-if="lineup.team.logo_url"
                  :src="lineup.team.logo_url"
                  :alt="lineup.team.name"
                  class="w-10 h-10 rounded-full border border-gray-200"
                />
                <div>
                  <h3 class="font-bold text-gray-900 text-lg">{{ lineup.team.name }}</h3>
                  <div class="flex items-center space-x-2 mt-1">
                    <span
                      class="text-xs font-medium px-2 py-1 rounded-full"
                      :class="lineup.side === 'home' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'"
                    >
                      {{ lineup.side.toUpperCase() }}
                    </span>
                    <span
                      v-if="lineup.is_confirmed"
                      class="text-xs font-medium bg-green-100 text-green-800 px-2 py-1 rounded-full"
                    >
                      ✓ Confirmed
                    </span>
                  </div>
                </div>
              </div>
              <div class="text-right">
                <div class="text-sm text-gray-500">Formation</div>
                <div class="font-bold text-gray-900 text-lg">{{ lineup.formation || 'N/A' }}</div>
              </div>
            </div>

            <!-- Starting XI -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-4">
                <h4 class="font-semibold text-gray-800 text-base">Starting XI</h4>
                <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  {{ lineup.starters.length }} players
                </span>
              </div>
              
              <div class="space-y-2">
                <div
                  v-for="(player, index) in lineup.starters"
                  :key="player.id"
                  class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-all duration-200"
                >
                  <div class="flex items-center space-x-3 min-w-0 flex-1">
                    <div class="flex items-center justify-center w-6 h-6 bg-gray-100 rounded text-xs font-medium text-gray-600">
                      {{ index + 1 }}
                    </div>
                    <div class="min-w-0 flex-1">
                      <div class="font-medium text-gray-900 text-sm truncate">
                        {{ player.player?.name }}
                      </div>
                      <div class="flex items-center space-x-2 mt-1">
                        <span class="text-xs text-gray-500 capitalize">{{ player.position?.toLowerCase() }}</span>
                        <span class="text-xs text-gray-400">•</span>
                        <span class="text-xs text-gray-500">#{{ player.player?.jersey_number || 'N/A' }}</span>
                      </div>
                    </div>
                  </div>
                  <div
                    class="text-xs font-medium px-2 py-1 rounded-full"
                    :class="getPositionColor(player.position)"
                  >
                    {{ player.position }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Bench Players -->
            <div v-if="lineup.bench.length > 0">
              <div class="flex items-center justify-between mb-4">
                <h4 class="font-semibold text-gray-800 text-base">Substitutes</h4>
                <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  {{ lineup.bench.length }} players
                </span>
              </div>
              
              <div class="space-y-2">
                <div
                  v-for="(player, index) in lineup.bench"
                  :key="player.id"
                  class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-all duration-200"
                >
                  <div class="flex items-center space-x-3 min-w-0 flex-1">
                    <div class="flex items-center justify-center w-6 h-6 bg-gray-100 rounded text-xs font-medium text-gray-600">
                      {{ index + 1 }}
                    </div>
                    <div class="min-w-0 flex-1">
                      <div class="font-medium text-gray-900 text-sm truncate">
                        {{ player.player?.name }}
                      </div>
                      <div class="flex items-center space-x-2 mt-1">
                        <span class="text-xs text-gray-500 capitalize">{{ player.position?.toLowerCase() }}</span>
                        <span class="text-xs text-gray-400">•</span>
                        <span class="text-xs text-gray-500">#{{ player.player?.jersey_number || 'N/A' }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="text-xs text-gray-400 italic">
                    Bench
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty Bench State -->
            <div v-else class="text-center py-6 border border-dashed border-gray-300 rounded-lg bg-gray-50">
              <svg class="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
              </svg>
              <p class="text-sm text-gray-500">No substitutes</p>
            </div>
          </div>
        </div>

        <!-- Single Lineup State (when only one team has lineup) -->
        <div
          v-if="fixture.lineups.length === 1"
          class="text-center py-8 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50"
        >
          <svg class="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Waiting for Opponent Lineup</h3>
          <p class="text-gray-600 max-w-md mx-auto">
            The {{ getMissingTeam() }} lineup hasn't been submitted yet.
          </p>
        </div>

        <!-- No Lineups State -->
        <div
          v-if="fixture.lineups.length === 0"
          class="text-center py-12 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50"
        >
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 class="text-xl font-bold text-gray-900 mb-2">No Lineups Available</h3>
          <p class="text-gray-600 max-w-md mx-auto">
            Lineups for this match haven't been submitted yet. Check back closer to kick-off time.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Fixture } from "@/helpers/types/team";

interface Props {
  fixture: Fixture;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void;
}>();

const getPositionColor = (position: string | null) => {
  if (!position) return 'bg-gray-100 text-gray-800';
  
  const colors = {
    'GKP': 'bg-purple-100 text-purple-800',
    'DEF': 'bg-blue-100 text-blue-800',
    'MID': 'bg-green-100 text-green-800',
    'FWD': 'bg-red-100 text-red-800'
  };
  return colors[position as keyof typeof colors] || 'bg-gray-100 text-gray-800';
};

const getMissingTeam = () => {
  const homeTeamInLineup = props.fixture.lineups.some(lineup => lineup.side === 'home');
  const awayTeamInLineup = props.fixture.lineups.some(lineup => lineup.side === 'away');
  
  if (!homeTeamInLineup) return props.fixture.home_team.name;
  if (!awayTeamInLineup) return props.fixture.away_team.name;
  return 'opponent';
};
</script>

<style scoped>
/* Smooth scrolling for the modal */
.modal-content {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: #f7fafc;
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
</style>