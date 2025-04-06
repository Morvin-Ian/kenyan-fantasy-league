<template>
  <div 
    v-if="showModal"
    class="fixed inset-0 bg-black/70 flex justify-center items-center z-50 backdrop-blur-sm transition-opacity duration-300"
    :class="{'opacity-0 pointer-events-none': !showModal, 'opacity-100': showModal}"
    @click.self="emitAction('close-modal')"
  >
    <div 
      class="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden transform transition-all duration-300"
      :class="{'scale-95': !showModal, 'scale-100': showModal}"
    >
      <div class="bg-gradient-to-r from-blue-600 to-blue-500 p-6 text-white">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-2xl font-bold tracking-tight flex items-center gap-2">
              {{ selectedPlayer?.name || "Player" }}
            </h3>
            <p class="text-blue-100 mt-1 flex items-center gap-2">
              <PositionBadge :position="selectedPlayer?.position" />
              <span class="text-white/80">{{ selectedPlayer?.team.name }}</span>
            </p>
          </div>
          <button
            @click="emitAction('close-modal')"
            class="text-white/80 hover:text-white transition-colors font-extrabold duration-200 p-1 -mt-2 -mr-2"
          >
            X
          </button>
        </div>
      </div>
      
      <div class="p-6 space-y-3">
        <ActionButton 
          @click="emitAction('initiate-switch')"
          color="blue"
        >
          Switch Player
        </ActionButton>
        
        <ActionButton 
          @click="emitAction('make-captain')"
          color="green"
          :disabled="selectedPlayer?.isCaptain"
          :active="selectedPlayer?.isCaptain"
        >
          {{ selectedPlayer?.isCaptain ? 'Current Captain' : 'Make Captain' }}
        </ActionButton>
        
        <ActionButton 
          @click="emitAction('make-vice-captain')"
          color="yellow"
          :disabled="selectedPlayer?.isViceCaptain"
          :active="selectedPlayer?.isViceCaptain"
        >
          {{ selectedPlayer?.isViceCaptain ? 'Current Vice-Captain' : 'Make Vice-Captain' }}
        </ActionButton>
        
        <button
          v-if="selectedPlayer?.isInjured"
          @click="emitAction('view-injury')"
          class="w-full bg-red-100 text-red-600 py-3 rounded-lg text-sm font-semibold 
                hover:bg-red-200 transition-colors duration-300 flex items-center justify-center gap-2"
        >
          <ExclamationTriangleIcon class="h-5 w-5" />
          <span>View Injury Details</span>
        </button>
      </div>
    </div>
  </div>
</template>
  
<script setup lang="ts">
import type { FantasyPlayer as Player } from "@/helpers/types/team";
import ActionButton from "./ActionButton.vue";
import PositionBadge from "./PositionBadge.vue";

const props = defineProps<{
  showModal: boolean;
  selectedPlayer: Player | null;
}>();

const emit = defineEmits<{
  (event: "close-modal"): void;
  (event: "initiate-switch"): void;
  (event: "make-captain"): void;
  (event: "make-vice-captain"): void;
}>();

const emitAction = (action: "close-modal" | "initiate-switch" | "make-captain" | "make-vice-captain") => {
  emit(action);
};

const getFormColor = (form?: number) => {
  if (!form) return 'text-gray-500';
  
  if (form >= 5) return 'text-green-600';
  if (form >= 3) return 'text-yellow-600';
  return 'text-red-600';
};
</script>