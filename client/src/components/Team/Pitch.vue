<template>
  <div class="relative  bg-white overflow-hidden shadow-2xl rounded-2xl max-w-full">
    <div
      class="absolute inset-0 bg-[url('/pitch.jpg')] bg-cover bg-center"
      :style="{
        filter: 'brightness(0.9) contrast(1.1)',
        'background-image':
          'linear-gradient(to bottom, rgba(0, 80, 0, 0.2), rgba(0, 60, 0, 0.4)), url(/pitch.jpg)',
      }"
    ></div>

    <div class="relative min-h-[500px] xs:min-h-[600px] sm:min-h-[700px] md:min-h-[800px] p-2 xs:p-3 sm:p-4 md:p-8">
      <!-- Goalkeeper -->
      <div
        class="absolute top-[0%] left-1/2 transform -translate-x-1/2 w-full max-w-[60px] xs:max-w-[70px] sm:max-w-[80px] md:max-w-[90px] lg:max-w-[100px] transition-all duration-300 hover:scale-105"
      >
        <div :class="getPlayerClass(goalkeeper)" @click="handlePlayerClick(goalkeeper)">
          <PlayerCard
            :player="goalkeeper"
            :is-active="switchSource?.id === goalkeeper.id"
            class="w-[60px] xs:w-[60px] sm:w-[70px] md:w-[80px] lg:w-[90px] shadow-2xl"
          />
        </div>
      </div>

      <!-- Defenders -->
      <div class="absolute top-[18%] left-0 right-0">
        <div class="flex justify-center flex-wrap gap-x-1 xs:gap-x-4 sm:gap-x-4 md:gap-x-4 lg:gap-x-6 px-2 xs:px-4 sm:px-4 md:px-4">
          <div
            v-for="(player, index) in defenders"
            :key="player.id"
            :class="[
              getPlayerClass(player),
              `delay-${index * 100}`,
            ]"
            @click="handlePlayerClick(player)"
            class="origin-bottom mb-1 xs:mb-2 sm:mb-0 mx-1"
          >
            <PlayerCard
              :player="player"
              :is-active="switchSource?.id === player.id"
              class="w-[50px] xs:w-[55px] sm:w-[60px] md:w-[70px] lg:w-[80px] xl:w-[90px] shadow-xl"
            />
          </div>
        </div>
      </div>

      <!-- Midfielders -->
      <div class="absolute top-[40%] left-0 right-0">
        <div class="flex justify-center flex-wrap gap-x-1 xs:gap-x-2 sm:gap-x-3 md:gap-x-4 lg:gap-x-6 px-1 xs:px-2 sm:px-3 md:px-4">
          <div
            v-for="(player, index) in midfielders"
            :key="player.id"
            :class="[
              getPlayerClass(player),
              `delay-${index * 100}`,
            ]"
            @click="handlePlayerClick(player)"
            class="origin-bottom mb-1 xs:mb-2 sm:mb-0 mx-1"
          >
            <PlayerCard
              :player="player"
              :is-active="switchSource?.id === player.id"
              class="w-[50px] xs:w-[55px] sm:w-[60px] md:w-[70px] lg:w-[80px] xl:w-[90px] shadow-xl"
            />
          </div>
        </div>
      </div>

      <!-- Forwards -->
      <div class="absolute top-[60%] left-0 right-0">
        <div class="flex justify-center flex-wrap gap-x-1 xs:gap-x-2 sm:gap-x-3 md:gap-x-4 lg:gap-x-6 px-1 xs:px-2 sm:px-3 md:px-4">
          <div
            v-for="(player, index) in forwards"
            :key="player.id"
            :class="[
              getPlayerClass(player),
              `delay-${index * 100}`,
            ]"
            @click="handlePlayerClick(player)"
            class="origin-bottom mb-1 xs:mb-2 sm:mb-0 mx-3"
          >
            <PlayerCard
              :player="player"
              :is-active="switchSource?.id === player.id"
              class="w-[50px] xs:w-[55px] sm:w-[60px] md:w-[70px] lg:w-[80px] xl:w-[90px] shadow-xl"
            />
          </div>
        </div>
      </div>

      <!-- Substitutes -->
      <div class="absolute bottom-0 left-0 right-0">
        <div class="flex justify-center overflow-x-auto py-1 xs:py-2 px-1 xs:px-2 sm:px-3 md:px-4">
          <div class="flex gap-1 xs:gap-2 sm:gap-3 md:gap-4">
            <div
              v-for="(player, index) in benchPlayers"
              :key="player.id"
              :class="[
                getPlayerClass(player),
                `delay-${index * 100}`,
                { 'placeholder-bench': player.id.startsWith('placeholder') },
              ]"
              @click="handlePlayerClick(player)"
              class="origin-bottom mb-1 xs:mb-2 sm:mb-0 mx-2"

            >
              <PlayerCard
                :player="player"
                :is-active="switchSource?.id === player.id"
                class="w-[55px] xs:w-[50px] sm:w-[60px] md:w-[65px] lg:w-[70px] shadow-md"
                :compact="true"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import PlayerCard from "@/components/Team/PlayerCard.vue";
import type { FantasyPlayer as Player } from "@/helpers/types/fantasy";

const props = defineProps<{
  goalkeeper: Player;
  defenders: Player[];
  midfielders: Player[];
  forwards: Player[];
  benchPlayers: Player[];
  switchSource: Player | null;
  switchActive: boolean;
}>();

const emit = defineEmits<{
  (e: "player-click", player: Player): void;
  (e: "formation-change", formation: string): void;
}>();

const getPlayerClass = (player: Player) => ({
  "opacity-50 pointer-events-none": props.switchActive && isPlayerDisabled(player),
  "transition-all duration-300": true,
  "gk-hover": player.position === "GKP",
  "def-hover": player.position === "DEF",
  "mid-hover": player.position === "MID",
  "fwd-hover": player.position === "FWD",
});


const currentFormation = computed(() => {
  return `${props.defenders.length}-${props.midfielders.length}-${props.forwards.length}`;
});

watch(currentFormation, (newFormation, oldFormation) => {
  if (newFormation !== oldFormation) {
    emit('formation-change', newFormation);
  }
});


const isPlayerDisabled = (player: Player) => {
  if (player.id.startsWith("placeholder")) return true;
  if (!props.switchActive || !props.switchSource) return false;
  if (props.switchSource.position === "GKP" || player.position === "GKP") {
    return props.switchSource.position !== player.position;
  }
  return false;
};

const handlePlayerClick = (player: Player) => {
  emit("player-click", player);
};
</script>
