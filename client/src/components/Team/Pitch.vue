<template>
  <div class="relative mx-auto bg-gradient-to-br from-green-600 to-emerald-500 rounded-3xl overflow-hidden shadow-2xl border-8 border-white">
      <div 
          class="absolute inset-0 bg-[url('https://fantasy.premierleague.com/static/media/pitch-default.dab51b01.svg')] 
          bg-cover bg-center opacity-20 animate-background-pulse"
      ></div>

      <div class="absolute inset-0 pointer-events-none">
          <div class="absolute top-1/2 left-0 right-0 border-t-2 border-white/30"></div>
          <div class="absolute top-1/2 left-1/2 w-32 h-32 border-2 border-white/30 rounded-full transform -translate-x-1/2 -translate-y-1/2"></div>
          <div class="absolute top-1/2 left-1/2 w-2 h-2 bg-white/50 rounded-full transform -translate-x-1/2 -translate-y-1/2"></div>
      </div>

      <div class="relative min-h-[600px] p-4 md:p-8">
          <div 
              class="absolute bottom-[83%] left-1/2 transform -translate-x-1/2 w-full max-w-[120px] transition-all duration-300 hover:scale-105"
          >
              <div 
                  :class="[
                      getPlayerClass(goalkeeper), 
                      'transform hover:rotate-6 hover:scale-110 transition-all duration-300'
                  ]"
                  @click="handlePlayerClick(goalkeeper)"
              >
                  <PlayerCard
                      :player="goalkeeper"
                      :is-active="switchSource?.id === goalkeeper.id"
                      class="shadow-2xl"
                  />
              </div>
          </div>

          <div class="absolute top-[20%] left-0 right-0">
              <div class="flex justify-center space-x-6 md:space-x-10 px-4">
                  <div 
                      v-for="(player, index) in defenders" 
                      :key="player.id"
                      :class="[
                          getPlayerClass(player), 
                          'transform transition-all duration-300 hover:rotate-3 hover:scale-110',
                          `delay-${index * 100}`
                      ]"
                      @click="handlePlayerClick(player)"
                      class="origin-bottom"
                  >
                      <PlayerCard
                          :player="player"
                          :is-active="switchSource?.id === player.id"
                          class="shadow-xl"
                      />
                  </div>
              </div>
          </div>

          <div class="absolute top-[45%] left-0 right-0">
              <div class="flex justify-center space-x-6 md:space-x-10 px-4">
                  <div 
                      v-for="(player, index) in midfielders" 
                      :key="player.id"
                      :class="[
                          getPlayerClass(player), 
                          'transform transition-all duration-300 hover:rotate-3 hover:scale-110',
                          `delay-${index * 100}`
                      ]"
                      @click="handlePlayerClick(player)"
                      class="origin-bottom"
                  >
                      <PlayerCard
                          :player="player"
                          :is-active="switchSource?.id === player.id"
                          class="shadow-xl"
                      />
                  </div>
              </div>
          </div>

          <div class="absolute top-[70%] left-0 right-0">
              <div class="flex justify-center space-x-6 md:space-x-10 px-4">
                  <div 
                      v-for="(player, index) in forwards" 
                      :key="player.id"
                      :class="[
                          getPlayerClass(player), 
                          'transform transition-all duration-300 hover:rotate-3 hover:scale-110',
                          `delay-${index * 100}`
                      ]"
                      @click="handlePlayerClick(player)"
                      class="origin-bottom"
                  >
                      <PlayerCard
                          :player="player"
                          :is-active="switchSource?.id === player.id"
                          class="shadow-xl"
                      />
                  </div>
              </div>
          </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PlayerCard from "@/components/Team/PlayerCard.vue";
import type {FantasyPlayer as Player } from "@/helpers/types/team";

const props = defineProps<{
  goalkeeper: Player;
  defenders: Player[];
  midfielders: Player[];
  forwards: Player[];
  switchSource: Player | null;
  switchActive: boolean;
}>();

const emit = defineEmits<{
  (e: "player-click", player: Player): void;
}>();

const getPlayerClass = (player: Player) => ({
  "opacity-50 pointer-events-none": props.switchActive && isPlayerDisabled(player),
  "cursor-pointer": true,
  "transition-all duration-300": true,
});

const isPlayerDisabled = (player: Player) => {
  if (!props.switchActive || !props.switchSource) return false;
  return props.switchSource.position === "GK" || player.position === "GK"
      ? props.switchSource.position !== player.position
      : false;
};

const handlePlayerClick = (player: Player) => {
  emit("player-click", player);
};
</script>

<style scoped>
@keyframes backgroundPulse {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.3; }
}

.animate-background-pulse {
  animation: backgroundPulse 5s ease-in-out infinite;
}

.delay-0 { transition-delay: 0ms; }
.delay-100 { transition-delay: 100ms; }
.delay-200 { transition-delay: 200ms; }
.delay-300 { transition-delay: 300ms; }
</style>