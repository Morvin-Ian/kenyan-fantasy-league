<template>
  <div
    v-if="showModal"
    class="fixed inset-0 bg-black/75 flex justify-center items-center z-50 backdrop-blur-sm transition-opacity duration-300 ease-in-out"
    :class="{ 'opacity-0 pointer-events-none': !showModal, 'opacity-100': showModal }"
    @click.self="emitAction('close-modal')"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden transform transition-all duration-300 ease-out"
      :class="{ 'scale-95 opacity-0': !showModal, 'scale-100 opacity-100': showModal }"
    >
      <div class="bg-gradient-to-r from-blue-600 to-blue-700 p-6 text-white">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-2xl font-bold tracking-tight flex items-center gap-2 animate-in fade-in">
              {{ selectedPlayer?.name || "Player" }}
            </h3>
            <p class="text-blue-100 mt-2 flex items-center gap-3 text-sm">
              <PositionBadge :position="selectedPlayer?.position" />
              <span class="text-white/90 font-medium">{{ selectedPlayer?.team.name }}</span>
            </p>
          </div>
          <button
            @click="emitAction('close-modal')"
            class="text-white/80 hover:text-white transition-colors duration-200 p-2 -mt-2 -mr-2 rounded-full hover:bg-white/10"
            aria-label="Close modal"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div class="p-6 space-y-4 bg-gray-50">
        <ActionButton
          v-if="!selectedPlayer.id.startsWith('placeholder')"
          @click="emitAction('initiate-switch')"
          color="blue"
          icon="SwitchHorizontalIcon"
        >
          Switch Player
        </ActionButton>

        <ActionButton
          @click="emitAction('transfer-player')"
          color="blue"
          icon="UserAddIcon"
        >
          {{ selectedPlayer.id.startsWith('placeholder') ? 'Add Player' : 'Transfer Player' }}
        </ActionButton>

        <ActionButton
          v-if="!selectedPlayer.id.startsWith('placeholder')"
          @click="emitAction('make-captain')"
          color="green"
          icon="StarIcon"
          :disabled="selectedPlayer?.is_captain"
          :active="selectedPlayer?.is_captain"
        >
          {{ selectedPlayer?.is_captain ? 'Current Captain' : 'Make Captain' }}
        </ActionButton>

        <ActionButton
          v-if="!selectedPlayer.id.startsWith('placeholder')"
          @click="emitAction('make-vice-captain')"
          color="yellow"
          icon="BadgeCheckIcon"
          :disabled="selectedPlayer?.is_vice_captain"
          :active="selectedPlayer?.is_vice_captain"
        >
          {{ selectedPlayer?.is_vice_captain ? 'Current Vice-Captain' : 'Make Vice-Captain' }}
        </ActionButton>

        <button
          v-if="selectedPlayer?.isInjured"
          @click="emitAction('view-injury')"
          class="w-full bg-red-100 text-red-700 py-3 px-4 rounded-lg text-sm font-semibold 
                hover:bg-red-200 transition-colors duration-300 flex items-center justify-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>View Injury Details</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FantasyPlayer as Player } from "@/helpers/types/fantasy";
import ActionButton from "./ActionButton.vue";
import PositionBadge from "./PositionBadge.vue";
import { watch } from 'vue';

// Icons (assuming Heroicons or similar)
import { SwitchHorizontalIcon, UserAddIcon, StarIcon, BadgeCheckIcon } from '@heroicons/vue/outline';

const props = defineProps<{
  showModal: boolean;
  selectedPlayer: Player | null;
}>();

const emit = defineEmits<{
  (event: "close-modal"): void;
  (event: "initiate-switch"): void;
  (event: "make-captain"): void;
  (event: "make-vice-captain"): void;
  (event: "transfer-player"): void;
}>();

const emitAction = (action: "close-modal" | "initiate-switch" | "make-captain" | "make-vice-captain" | "transfer-player") => {
  emit(action, props.selectedPlayer);
};

// Auto-emit 'transfer-player' if selectedPlayer is a placeholder
watch(
  () => props.selectedPlayer?.id,
  (newId) => {
    if (newId?.startsWith('placeholder')) {
      emit('transfer-player', props.selectedPlayer);
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.animate-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>