<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-xl shadow-lg w-full max-w-3xl p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">Lineups</h2>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">✖</button>
      </div>

      <div v-for="lineup in fixture.lineups" :key="lineup.id" class="mb-6">
        <h3 class="font-bold text-gray-800 mb-2">
          {{ lineup.team.name }} ({{ lineup.side.toUpperCase() }}) - {{ lineup.formation || 'N/A' }}
          <span v-if="lineup.is_confirmed" class="ml-2 text-green-600 text-sm">✅ Confirmed</span>
        </h3>

        <div class="mb-3">
          <h4 class="font-medium text-gray-600">Starters</h4>
          <ul class="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-1">
            <li v-for="p in lineup.starters" :key="p.id" class="p-2 border rounded">
              <div class="font-semibold text-gray-800">{{ p.player?.name }}</div>
              <div class="text-xs text-gray-500">{{ p.position }}</div>
              <div class="text-xs text-gray-400">#{{ p.player?.jersey_number }}</div>
            </li>
          </ul>
        </div>

        <div>
          <h4 class="font-medium text-gray-600">Bench</h4>
          <ul class="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-1">
            <li v-for="p in lineup.bench" :key="p.id" class="p-2 border rounded">
              <div class="font-semibold text-gray-800">{{ p.player?.name }}</div>
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
defineEmits(['close']);
</script>
