<template>
    <div class="relative mx-auto bg-green-700 rounded-lg overflow-hidden">
        <div
            class="absolute inset-0 bg-[url('https://fantasy.premierleague.com/static/media/pitch-default.dab51b01.svg')] bg-cover bg-center opacity-90"
        ></div>

        <!-- Players Layout -->
        <div class="relative min-h-[500px] md:min-h-[600px] p-4 md:p-8">
            <!-- Goalkeeper -->
            <div
                class="absolute bottom-[83%] left-1/2 transform -translate-x-1/2 w-full max-w-[80px] md:max-w-[112px]"
            >
                <div
                    :class="getPlayerClass(goalkeeper)"
                    @click="handlePlayerClick(goalkeeper)"
                >
                    <PlayerCard
                        :player="goalkeeper"
                        :is-active="switchSource?.id === goalkeeper.id"
                    />
                </div>
            </div>

            <!-- Defenders -->
            <div class="absolute top-[20%] left-0 right-0">
                <div class="flex justify-center gap-4">
                    <div
                        v-for="player in defenders"
                        :key="player.id"
                        :class="getPlayerClass(player)"
                        @click="handlePlayerClick(player)"
                    >
                        <PlayerCard
                            :player="player"
                            :is-active="switchSource?.id === player.id"
                        />
                    </div>
                </div>
            </div>

            <!-- Midfielders -->
            <div class="absolute top-[45%] left-0 right-0">
                <div class="flex justify-center gap-4">
                    <div
                        v-for="player in midfielders"
                        :key="player.id"
                        :class="getPlayerClass(player)"
                        @click="handlePlayerClick(player)"
                    >
                        <PlayerCard
                            :player="player"
                            :is-active="switchSource?.id === player.id"
                        />
                    </div>
                </div>
            </div>

            <!-- Forwards -->
            <div class="absolute top-[70%] left-0 right-0">
                <div class="flex justify-center gap-8">
                    <div
                        v-for="player in forwards"
                        :key="player.id"
                        :class="getPlayerClass(player)"
                        @click="handlePlayerClick(player)"
                    >
                        <PlayerCard
                            :player="player"
                            :is-active="switchSource?.id === player.id"
                        />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import PlayerCard from "@/components/team/PlayerCard.vue";
import type { Player } from "@/types/team";

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
