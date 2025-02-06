<template>
    <div
        class="bg-gradient-to-br from-gray-50 to-blue-50 p-8 rounded-2xl shadow-lg"
    >
        <!-- Header -->
        <div
            class="flex flex-col md:flex-row md:justify-between items-start mb-8"
        >
            <div class="animate-fade-in">
                <h2 class="text-2xl font-bold text-gray-700 bg-clip-text">
                    Upcoming Matches
                </h2>
                <p class="text-gray-500 mt-2">
                    Stay updated with the latest fixtures
                </p>
            </div>
            <div class="flex items-center gap-4 justify-start">
                <a
                    href="/fixtures"
                    class="flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="w-4 h-4"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <rect
                            x="3"
                            y="4"
                            width="18"
                            height="18"
                            rx="2"
                            ry="2"
                        ></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    <span class="text-sm font-medium">Full Calendar</span>
                </a>
                <div class="flex gap-2">
                    <button
                        @click="scroll('left')"
                        class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="w-5 h-5 text-gray-600"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        >
                            <polyline points="15 18 9 12 15 6"></polyline>
                        </svg>
                    </button>
                    <button
                        @click="scroll('right')"
                        class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 border border-gray-200 transition-colors"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="w-5 h-5 text-gray-600"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        >
                            <polyline points="9 18 15 12 9 6"></polyline>
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <!-- Matches Container -->
        <div
            ref="scrollContainer"
            class="flex gap-6 overflow-x-auto pb-6 hide-scrollbar"
        >
            <div
                v-for="(game, index) in games"
                :key="game.id"
                :style="{ animationDelay: `${index * 100}ms` }"
                class="animate-slide-up flex-shrink-0 w-72 rounded-2xl bg-white border-2 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 group"
                :class="[
                    game.status === 'UPCOMING'
                        ? 'border-blue-400 shadow-lg'
                        : 'border-gray-100 shadow-md',
                    game.status === 'POSTPONED' ? 'opacity-75' : '',
                ]"
            >
                <div class="p-6 space-y-4">
                    <!-- League & Status -->
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div
                                class="w-10 h-10 bg-gray-50 rounded-full p-2 group-hover:scale-110 transition-transform duration-300"
                            >
                                <img
                                    src="../../assets/logo.png"
                                    alt=""
                                    class="w-full h-full object-contain"
                                />
                            </div>
                            <span class="text-sm font-light text-gray-700">{{
                                game.type
                            }}</span>
                        </div>
                        <div
                            :class="[
                                'px-3 py-1 rounded-full text-xs font-bold tracking-wide transition-colors duration-300',
                                {
                                    'bg-blue-100 text-blue-700 group-hover:bg-blue-200':
                                        game.status === 'UPCOMING',
                                    'bg-gray-100 text-gray-600 group-hover:bg-gray-200':
                                        game.status === 'ENDED',
                                    'bg-red-50 text-red-600 group-hover:bg-red-100':
                                        game.status === 'POSTPONED',
                                },
                            ]"
                        >
                            {{ game.status }}
                        </div>
                    </div>

                    <!-- Teams -->
                    <div class="space-y-1">
                        <div class="text-sm font-medium text-gray-900">
                            {{ game.homeTeam }}
                        </div>
                        <div class="text-sm font-medium text-gray-900">
                            {{ game.awayTeam }}
                        </div>
                    </div>

                    <!-- Date & Time -->
                    <div
                        class="flex items-center gap-2 pt-2 border-t border-gray-100"
                    >
                        <div
                            class="flex items-center gap-2 text-sm text-gray-500"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                class="w-4 h-4"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            >
                                <rect
                                    x="3"
                                    y="4"
                                    width="18"
                                    height="18"
                                    rx="2"
                                    ry="2"
                                ></rect>
                                <line x1="16" y1="2" x2="16" y2="6"></line>
                                <line x1="8" y1="2" x2="8" y2="6"></line>
                                <line x1="3" y1="10" x2="21" y2="10"></line>
                            </svg>
                            <span>{{ formatDate(game.date) }}</span>
                            <span class="text-gray-300">•</span>
                            <span>{{ game.time }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const scrollContainer = ref<HTMLElement | null>(null);

const games = [
    {
        id: 1,
        homeTeam: "Manchester United",
        awayTeam: "Arsenal",
        date: "2024-12-28",
        time: "20:00",
        type: "Premier Leaguee",
        status: "ENDED",
    },
    {
        id: 2,
        homeTeam: "Real Madrid",
        awayTeam: "Barcelona",
        date: "2024-12-30",
        time: "21:00",
        type: "Premier League",
        status: "UPCOMING",
    },
    {
        id: 3,
        homeTeam: "Juventus",
        awayTeam: "Napoli",
        date: "2025-01-01",
        time: "19:45",
        type: "Premier League",
        status: "POSTPONED",
    },
    {
        id: 4,
        homeTeam: "PSG",
        awayTeam: "Marseille",
        date: "2025-01-05",
        time: "20:00",
        type: "Premier League",
        status: "POSTPONED",
    },
    {
        id: 4,
        homeTeam: "PSG",
        awayTeam: "Marseille",
        date: "2025-01-05",
        time: "20:00",
        type: "Premier League",
        status: "POSTPONED",
    },
    {
        id: 4,
        homeTeam: "PSG",
        awayTeam: "Marseille",
        date: "2025-01-05",
        time: "20:00",
        type: "Premier League",
        status: "POSTPONED",
    },
];

const scroll = (direction: "left" | "right") => {
    if (!scrollContainer.value) return;

    const scrollAmount = 280;
    const isLeft = direction === "left";

    scrollContainer.value.scrollBy({
        left: isLeft ? -scrollAmount : scrollAmount,
        behavior: "smooth",
    });
};

const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
    }).format(date);
};
</script>

<style scoped>
.hide-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

.hide-scrollbar::-webkit-scrollbar {
    display: none;
}

.animate-fade-in {
    animation: fadeIn 0.6s ease-out;
}

.animate-slide-in {
    animation: slideIn 0.6s ease-out;
}

.animate-slide-up {
    animation: slideUp 0.6s ease-out forwards;
    opacity: 0;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Add smooth transitions for all interactive elements */
button,
a {
    transition: all 0.3s ease;
}
</style>
