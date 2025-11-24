<template>
  <div
    v-if="showModal"
    class="fixed inset-0 bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 
           flex justify-center items-center z-50 backdrop-blur-xl transition-all duration-500 ease-out
           animate-modal-overlay"
    :class="{ 'opacity-0 pointer-events-none': !showModal, 'opacity-100': showModal }"
    @click.self="emitAction('close-modal')"
  >
    <div
      class="relative bg-white rounded-3xl shadow-2xl max-w-md w-full mx-4 overflow-hidden 
             transform transition-all duration-500 ease-out border border-gray-200/20
             before:absolute before:inset-0 before:bg-gradient-to-br before:from-white/10 before:to-transparent before:pointer-events-none"
      :class="{ 'scale-90 opacity-0 translate-y-8': !showModal, 'scale-100 opacity-100 translate-y-0': showModal }"
    >
      <!-- Animated background pattern -->
      <div class="absolute inset-0 opacity-5">
        <div class="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-purple-500/20 to-blue-800/20 animate-gradient"></div>
      </div>

      <!-- Header Section -->
      <div class="relative bg-gradient-to-br from-slate-800 via-slate-700 to-slate-900 p-8 text-white overflow-hidden">
        <!-- Subtle animated background -->
        <div class="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-500/5 to-indigo-600/10 animate-gradient-slow"></div>
        
        <div class="relative flex justify-between items-start">
          <div class="flex-1">
            <h3 class="text-3xl font-black tracking-tight flex items-center gap-3 animate-slide-in-left
                       bg-gradient-to-r from-white via-gray-100 to-white bg-clip-text text-transparent
                       drop-shadow-sm">
              {{ selectedPlayer?.name || "Player" }}
            </h3>
            <div class="mt-4 flex items-center gap-4 animate-slide-in-left animation-delay-200">
              <PositionBadge :position="selectedPlayer?.position" />
              <div class="h-4 w-px bg-white/20"></div>
              <span class="text-gray-200 font-semibold text-sm tracking-wide uppercase">
                {{ typeof selectedPlayer?.team === 'object' ? selectedPlayer?.team.name : selectedPlayer?.team }}
              </span>
            </div>
          </div>
          
          <button
            @click="emitAction('close-modal')"
            class="text-white/60 hover:text-white transition-all duration-300 p-3 -mt-2 -mr-2 
                   rounded-full hover:bg-white/10 group transform hover:scale-110 active:scale-95"
            aria-label="Close modal"
          >
            <svg class="w-5 h-5 transition-transform duration-300 group-hover:rotate-90" 
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Content Section -->
      <div class="relative p-8 space-y-5 bg-gradient-to-b from-gray-50 to-white">
        <ActionButton
          v-if="!selectedPlayer?.id.startsWith('placeholder')"
          @click="emitAction('initiate-switch')"
          color="blue"
          icon="SwitchHorizontalIcon"
          class="animate-slide-in-up animation-delay-300"
        >
          Switch Player
        </ActionButton>

        <ActionButton
          @click="emitAction('transfer-player')"
          color="blue"
          icon="UserAddIcon"
          class="animate-slide-in-up animation-delay-400"
        >
          {{ selectedPlayer?.id.startsWith('placeholder') ? 'Add Player' : 'Transfer Player' }}
        </ActionButton>

        <ActionButton
          v-if="!selectedPlayer?.id.startsWith('placeholder')"
          @click="emitAction('make-captain')"
          color="green"
          icon="StarIcon"
          :disabled="selectedPlayer?.is_captain"
          :active="selectedPlayer?.is_captain"
          class="animate-slide-in-up animation-delay-500"
        >
          {{ selectedPlayer?.is_captain ? 'Current Captain' : 'Make Captain' }}
        </ActionButton>

        <ActionButton
          v-if="!selectedPlayer?.id.startsWith('placeholder')"
          @click="emitAction('make-vice-captain')"
          color="yellow"
          icon="BadgeCheckIcon"
          :disabled="selectedPlayer?.is_vice_captain"
          :active="selectedPlayer?.is_vice_captain"
          class="animate-slide-in-up animation-delay-600"
        >
          {{ selectedPlayer?.is_vice_captain ? 'Current Vice-Captain' : 'Make Vice-Captain' }}
        </ActionButton>

        <button
          v-if="selectedPlayer?.isInjured"
          class="w-full bg-gradient-to-r from-red-500 to-red-600 text-white py-4 px-6 rounded-2xl 
                 font-bold tracking-wide shadow-lg hover:shadow-xl transition-all duration-300 
                 flex items-center justify-center gap-3 transform hover:scale-[1.02] active:scale-98
                 border border-red-400/20 animate-slide-in-up animation-delay-700
                 hover:from-red-600 hover:to-red-700"
        >
          <svg class="w-5 h-5 drop-shadow-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span class="text-sm font-black uppercase tracking-wider">View Injury Details</span>
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

const props = defineProps<{
  showModal: boolean;
  selectedPlayer: Player | null;
}>();

const emit = defineEmits<(
  event: "close-modal" | "initiate-switch" | "make-captain" | "make-vice-captain" | "transfer-player",
  payload?: Player | null
) => void>();

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
/* Enhanced animations */
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes modalOverlay {
  from {
    backdrop-filter: blur(0px);
    background: rgba(15, 23, 42, 0);
  }
  to {
    backdrop-filter: blur(24px);
    background: rgba(15, 23, 42, 0.4);
  }
}

@keyframes gradient {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

@keyframes gradientSlow {
  0%, 100% {
    opacity: 0.05;
    transform: translateX(0%);
  }
  50% {
    opacity: 0.1;
    transform: translateX(10%);
  }
}

/* Animation classes */
.animate-slide-in-left {
  animation: slideInLeft 0.6s ease-out forwards;
}

.animate-slide-in-up {
  animation: slideInUp 0.5s ease-out forwards;
  opacity: 0;
}

.animate-modal-overlay {
  animation: modalOverlay 0.5s ease-out forwards;
}

.animate-gradient {
  background-size: 400% 400%;
  animation: gradient 8s ease infinite;
}

.animate-gradient-slow {
  animation: gradientSlow 12s ease-in-out infinite;
}

/* Animation delays */
.animation-delay-200 {
  animation-delay: 0.2s;
}

.animation-delay-300 {
  animation-delay: 0.3s;
}

.animation-delay-400 {
  animation-delay: 0.4s;
}

.animation-delay-500 {
  animation-delay: 0.5s;
}

.animation-delay-600 {
  animation-delay: 0.6s;
}

.animation-delay-700 {
  animation-delay: 0.7s;
}

/* Enhanced typography */
.font-black {
  font-weight: 900;
  letter-spacing: -0.025em;
}

/* Smooth transforms */
.transform {
  transition: transform 0.2s ease-out;
}

.active\:scale-98:active {
  transform: scale(0.98);
}

.hover\:scale-\[1\.02\]:hover {
  transform: scale(1.02);
}

/* Glass morphism effect */
.before\:absolute::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), transparent);
  pointer-events: none;
  border-radius: inherit;
}
</style>