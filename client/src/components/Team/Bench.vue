<template>
    <div class="bg-white rounded-lg mt-4 p-4 shadow-inner">
        <div class="grid grid-cols-4 gap-2">
            <div
                v-for="player in benchPlayers"
                :key="player.id"
                :class="getPlayerClass(player)"
                @click="handlePlayerClick(player)"
            >
                <PlayerCard
                    :player="player"
                    :is-active="switchSource?.id === player.id"
                    isBench
                />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import PlayerCard from "@/components/Team/PlayerCard.vue";
import type {FantasyPlayer as Player } from "@/helpers/types/team";

const props = defineProps<{
    benchPlayers: Player[];
    switchSource: Player | null;
    switchActive: boolean;
}>();

const emit = defineEmits<{
    (e: "player-click", player: Player): void;
}>();

const getPlayerClass = (player: Player) => ({
    "opacity-50 pointer-events-none":
        props.switchActive && isPlayerDisabled(player),
    "cursor-pointer": true,
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
