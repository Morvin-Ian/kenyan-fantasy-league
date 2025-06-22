<template>
    <div class="relative w-18 sm:w-22 md:w-18 lg:w-20 xl:w-24 transition-all duration-300">
        <div @click="showDetails = !showDetails"
            class="player-card bg-gradient-to-br from-green-700 to-green-900 hover:from-green-600 hover:to-green-800 rounded-xl p-1.5 sm:p-2 text-center cursor-pointer relative transition-all duration-300 shadow-lg hover:shadow-2xl transform hover:-translate-y-1.5 overflow-hidden border border-green-600/20 hover:border-green-400/30"
            :class="{
                active: isActive,
                'ring-2 ring-yellow-400':
                    player.is_captain || player.is_vice_captain,
            }">
            <div class="absolute inset-0 overflow-hidden">
                <div class="absolute -top-8 -right-8 w-16 h-16 bg-green-500/10 rounded-full blur-sm"></div>
                <div class="absolute -bottom-8 -left-8 w-16 h-16 bg-green-500/10 rounded-full blur-sm"></div>
                <div class="absolute inset-0 bg-gradient-to-br from-transparent via-green-900/10 to-transparent"></div>
            </div>

            <div class="relative mb-2 flex justify-center items-center">
                <div class="absolute inset-0 bg-green-800/30 rounded-full transform scale-90"></div>
                <div class="jersey-container relative group">
                    <img :src="jerseyImage" :alt="`${player.team} jersey`"
                        class="w-12 h-12 sm:w-14 sm:h-14 md:w-12 md:h-12 lg:w-16 lg:h-16 object-contain transition-all duration-500 transform group-hover:scale-110 group-hover:rotate-2 relative z-10 drop-shadow-md" />
                    <div
                        class="absolute inset-0 bg-green-500/10 rounded-full transform scale-110 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    </div>
                </div>

                <div v-if="player.is_captain || player.is_vice_captain"
                    class="captain-badge absolute -top-2 -right-2 w-5 h-5 sm:w-6 sm:h-6 bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-full flex items-center justify-center text-xs font-bold text-black shadow-lg border-2 border-yellow-200 z-20">
                    {{ player.is_captain ? "C" : "V" }}
                </div>
            </div>

            <div class="px-1 min-h-[1rem] flex items-center justify-center">
                <p class="text-white text-xs sm:text-sm font-semibold truncate max-w-full relative">
                    <span class="name-gradient">{{ player.name }}</span>
                </p>
            </div>

            <div 
                class="points-container relative mt-1 bg-gradient-to-b from-green-800/60 to-green-900/80 rounded-full py-1 px-1 backdrop-blur-sm border border-green-500/20">
                <div
                    class="shine-effect absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300">
                </div>
                <p class="text-white text-xs sm:text-sm font-bold leading-tight tracking-wide">
                    {{ player.gameweek_points }}
                    <span class="text-green-300 text-[0.6rem]">PTS</span>
                </p>
            </div>

            <div v-if="isActive"
                class="absolute -top-2 -right-2 w-3 h-3 bg-green-400 rounded-full shadow-md border border-white"></div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from "vue";
import goalkeeperJersey from "@/assets/images/jerseys/goalkeeper.png";
import defaultJersey from "@/assets/images/jerseys/default.png";

const showDetails = ref(false);
const props = defineProps({
    player: {
        type: Object,
        required: true,
    },
    isActive: {
        type: Boolean,
        default: false,
    },
});

const jerseyImage = computed(() => {
    if (props.player.position === "GKP") {
        return goalkeeperJersey;
    }
    return props.player.jersey_image || defaultJersey;
});
</script>

<style scoped>
.player-card {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.player-card:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
}

.player-card.active {
    border: 2px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 0 15px rgba(74, 222, 128, 0.6);
}

.captain-badge {
    animation: pulse 2s infinite ease-in-out;
    box-shadow: 0 0 10px rgba(234, 179, 8, 0.6);
}

.jersey-container:hover img {
    filter: drop-shadow(0 0 8px rgba(74, 222, 128, 0.4));
}

.name-gradient {
    background: linear-gradient(to right, #ffffff, #d1fae5);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.points-container {
    transition: all 0.3s ease;
}

.points-container:hover {
    background: linear-gradient(to bottom,
            rgba(6, 95, 70, 0.7),
            rgba(5, 150, 105, 0.8));
    transform: scale(1.05);
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }

    100% {
        transform: scale(1);
    }
}

@keyframes float {
    0% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-5px);
    }

    100% {
        transform: translateY(0px);
    }
}

@media (hover: hover) {
    .player-card:hover {
        animation: float 3s ease-in-out infinite;
    }
}
</style>
