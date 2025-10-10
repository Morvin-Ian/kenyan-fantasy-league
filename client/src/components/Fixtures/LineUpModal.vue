<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-2 sm:p-4">
    <div
      class="bg-white rounded-2xl shadow-xl w-full max-w-2xl sm:max-w-3xl max-h-[90vh] overflow-y-auto p-4 sm:p-6"
    >
      <div class="flex justify-between items-center border-b pb-2 mb-4">
        <h2 class="text-base sm:text-lg font-semibold text-gray-800">Lineups</h2>
        <button
          @click="$emit('close')"
          class="text-gray-500 hover:text-gray-700 transition-colors text-xl leading-none"
        >
          ✖
        </button>
      </div>

      <!-- Lineups -->
      <div
        v-for="lineup in fixture.lineups"
        :key="lineup.id"
        class="mb-6 last:mb-0 border rounded-lg p-4 sm:p-5 bg-gray-50"
      >
        <h3 class="font-semibold text-gray-800 mb-3 flex flex-wrap items-center gap-2">
          <span>{{ lineup.team.name }}</span>
          <span class="text-gray-500 text-sm">({{ lineup.side.toUpperCase() }})</span>
          <span class="text-sm text-gray-600">
            - Formation: <strong>{{ lineup.formation || 'N/A' }}</strong>
          </span>
          <span
            v-if="lineup.is_confirmed"
            class="text-green-600 text-xs font-medium bg-green-100 px-2 py-0.5 rounded-full"
          >
            Confirmed
          </span>
        </h3>

        <!-- Starters -->
        <div class="mb-4">
          <h4 class="font-medium text-gray-700 mb-2 text-sm sm:text-base">Starters</h4>
          <ul class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            <li
              v-for="p in lineup.starters"
              :key="p.id"
              class="p-2 border border-gray-200 rounded-lg bg-white hover:shadow-sm transition"
            >
              <div class="font-medium text-gray-800 text-sm truncate">
                {{ p.player?.name }}
              </div>
              <div class="text-xs text-gray-500">{{ p.position }}</div>
              <div class="text-xs text-gray-400">#{{ p.player?.jersey_number }}</div>
            </li>
          </ul>
        </div>

        <!-- Bench -->
        <div>
          <h4 class="font-medium text-gray-700 mb-2 text-sm sm:text-base">Bench</h4>
          <ul class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            <li
              v-for="p in lineup.bench"
              :key="p.id"
              class="p-2 border border-gray-200 rounded-lg bg-white hover:shadow-sm transition"
            >
              <div class="font-medium text-gray-800 text-sm truncate">
                {{ p.player?.name }}
              </div>
              <div class="text-xs text-gray-500">{{ p.position }}</div>
              <div class="text-xs text-gray-400">#{{ p.player?.jersey_number }}</div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Fixture } from "@/helpers/types/team";
defineProps<{ fixture: Fixture }>();
defineEmits(["close"]);
</script>
