<template>
    <div class="min-h-screen p-2 md:p-10">
        <div v-if="isLoading" class="flex justify-center items-center h-64">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
        </div>
        <div v-else class="max-w-7xl mx-auto">
            <div
                class="bg-white rounded-xl md:rounded-3xl shadow-xl overflow-hidden transition-all duration-500 hover:shadow-2xl">
                <div class="bg-white p-3 md:p-6 text-center relative">
                    <h1
                        class="text-2xl md:text-4xl font-black text-gray-600 flex items-center justify-center space-x-2 md:space-x-4">
                        <span class="truncate">Premier League Standings</span>
                    </h1>
                </div>

                <div class="p-2 md:p-6">
                    <!-- Mobile swipe hint -->
                    <div class="md:hidden mb-3 text-center">
                        <div class="inline-flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                            Swipe right for more stats
                        </div>
                    </div>

                    <!-- Table Container with horizontal scroll -->
                    <div class="overflow-x-auto rounded-lg shadow" style="scrollbar-width: thin; scrollbar-color: #10b981 #f0f0f0;">
                        <div class="min-w-full inline-block">
                            <table class="w-full text-xs md:text-sm border-collapse" style="min-width: 640px;">
                                <thead class="bg-green-100 text-green-800 sticky top-0 z-10">
                                    <tr>
                                        <!-- Always visible columns on mobile -->
                                        <th class="sticky left-0 bg-green-100 z-20 px-2 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[40px]">
                                            Pos
                                        </th>
                                        <th class="sticky left-10 bg-green-100 z-20 px-1 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[40px]">
                                            
                                        </th>
                                        <th class="sticky left-20 bg-green-100 z-20 px-2 py-2 md:p-4 font-black uppercase tracking-wider text-left border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[120px] md:min-w-[150px]">
                                            Team
                                        </th>
                                        
                                        <!-- Scrollable columns -->
                                       
                                        <th class="px-2 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[40px]">
                                            P
                                        </th>
                                        <th class="px-2 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[40px]">
                                            W
                                        </th>
                                        <th class="px-2 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[40px]">
                                            D
                                        </th>
                                        <th class="px-2 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[40px]">
                                            L
                                        </th>
                                        <th class="px-2 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[45px]">
                                            GF
                                        </th>
                                        <th class="px-2 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[45px]">
                                            GA
                                        </th>
                                        <th class="px-2 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[45px]">
                                            GD
                                        </th>
                                         <th class="px-2 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors min-w-[50px]">
                                            Pts
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="team in paginatedTeams" :key="team.team.id"
                                        class="hover:bg-green-50 transition-all duration-300 border-b border-gray-100">
                                        <!-- Sticky columns -->
                                        <td class="sticky left-0 bg-white z-10 p-2 text-center border-r border-gray-100">
                                            <span :class="getPositionClass(team.position)"
                                                class="inline-block w-6 h-6 md:w-8 md:h-8 rounded-full shadow-sm flex items-center justify-center font-bold text-xs transition-transform hover:scale-110">
                                                {{ team.position }}
                                            </span>
                                        </td>

                                        <td class="sticky left-10 bg-white z-10 p-1 text-center border-r border-gray-100">
                                            <img v-if="team.team.logo_url" :src="team.team.logo_url"
                                                :alt="`${team.team.name} logo`"
                                                class="w-6 h-6 md:w-8 md:h-8 mx-auto object-contain transition-transform rounded-full hover:scale-110" />
                                        </td>

                                        <td class="sticky left-20 bg-white z-10 px-2 py-2 font-semibold text-gray-800 hover:text-green-600 transition-colors text-left border-r border-gray-100">
                                            <div class="truncate max-w-[100px] md:max-w-[130px]" :title="team.team.name">
                                                {{ team.team.name }}
                                            </div>
                                        </td>

                                        <!-- Scrollable columns -->
                                       
                                        <td class="px-2 py-2 text-center font-medium text-gray-700">{{ team.played }}</td>
                                        <td class="px-2 py-2 text-center text-green-600 font-bold">{{ team.wins }}</td>
                                        <td class="px-2 py-2 text-center text-yellow-600 font-bold">{{ team.draws }}</td>
                                        <td class="px-2 py-2 text-center text-red-600 font-bold">{{ team.losses }}</td>
                                        <td class="px-2 py-2 text-center text-blue-600 font-medium">{{ team.goals_for }}</td>
                                        <td class="px-2 py-2 text-center text-red-500 font-medium">{{ team.goals_against }}</td>
                                        <td class="px-2 py-2 text-center font-bold text-purple-600">{{ team.goal_differential }}</td>
                                         <td class="px-2 py-2 text-center font-bold text-green-700 text-sm">
                                            {{ team.points }}
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Mobile legend for quick reference -->
                    <div class="md:hidden mt-4 bg-gray-50 rounded-lg p-3">
                        <h4 class="text-xs font-bold text-gray-700 mb-2">Legend:</h4>
                        <div class="grid grid-cols-2 gap-2 text-xs text-gray-600">
                            <div><span class="font-semibold">P:</span> Played</div>
                            <div><span class="font-semibold">W:</span> Won</div>
                            <div><span class="font-semibold">D:</span> Drawn</div>
                            <div><span class="font-semibold">L:</span> Lost</div>
                            <div><span class="font-semibold">GF:</span> Goals For</div>
                            <div><span class="font-semibold">GA:</span> Goals Against</div>
                            <div><span class="font-semibold">GD:</span> Goal Difference</div>
                            <div><span class="font-semibold">Pts:</span> Points</div>
                        </div>
                    </div>

                    <!-- Pagination Controls -->
                    <div class="flex justify-center items-center mt-4 md:mt-8 space-x-2 md:space-x-6">
                        <button @click="prevPage" :disabled="currentPage === 1"
                            class="group px-3 py-2 md:px-6 md:py-3 bg-green-500 text-white text-xs md:text-base rounded-full shadow-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-300 flex items-center space-x-1 md:space-x-2">
                            <svg xmlns="http://www.w3.org/2000/svg"
                                class="h-4 w-4 md:h-5 md:w-5 transform group-hover:-translate-x-1" fill="none"
                                viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                    d="M15 19l-7-7 7-7" />
                            </svg>
                            <span class="hidden md:inline">Previous</span>
                        </button>

                        <div class="text-gray-700 font-bold text-sm md:text-lg">
                            {{ currentPage }}/{{ totalPages }}
                        </div>

                        <button @click="nextPage" :disabled="currentPage === totalPages"
                            class="group px-3 py-2 md:px-6 md:py-3 bg-green-500 text-white text-xs md:text-base rounded-full shadow-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-300 flex items-center space-x-1 md:space-x-2">
                            <span class="hidden md:inline">Next</span>
                            <svg xmlns="http://www.w3.org/2000/svg"
                                class="h-4 w-4 md:h-5 md:w-5 transform group-hover:translate-x-1" fill="none"
                                viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- League Insights -->
                <div class="bg-gray-50 p-3 md:p-6 grid grid-cols-1 gap-3 md:grid-cols-3 md:gap-6">
                    <div v-for="(insight, index) in leagueInsights" :key="index" :class="insight.cardClasses"
                        class="transform transition-all duration-500 hover:scale-105 hover:shadow-2xl">
                        <div class="flex items-center mb-2 md:mb-4">
                            <div :class="insight.iconContainerClasses"
                                class="p-2 md:p-3 rounded-lg md:rounded-xl mr-2 md:mr-4 shadow-md">
                                <component :is="insight.icon" class="h-4 w-4 md:h-6 md:w-6 text-white" />
                            </div>
                            <h3 :class="insight.titleClasses" class="text-base md:text-xl font-black tracking-tight">
                                {{ insight.title }}
                            </h3>
                        </div>
                        <div class="flex items-center">
                            <div :class="insight.avatarClasses"
                                class="w-8 h-8 md:w-12 md:h-12 rounded-full flex items-center justify-center text-xs md:text-lg font-bold mr-2 md:mr-4 border-2 md:border-4 shadow-md">
                                {{ insight.team.team.name.substring(0, 2) }}
                            </div>
                            <div>
                                <p class="text-sm md:text-base text-gray-700 font-semibold truncate">
                                    {{ insight.team.team.name }}
                                </p>
                                <p :class="insight.valueClasses"
                                    class="text-base md:text-2xl font-black tracking-tight">
                                    {{ insight.value }}
                                </p>
                            </div>
                        </div>
                        <div :class="insight.subtextClasses" class="mt-2 md:mt-3 text-xs md:text-sm opacity-75">
                            {{ insight.subtext }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import { useAuthStore } from '@/stores/auth';
import { useKplStore } from "@/stores/kpl";
import { useRouter } from 'vue-router';
import { StarIcon, UserIcon, ShieldIcon } from 'lucide-vue-next';
import type { TeamStanding } from "@/helpers/types/team";

const authStore = useAuthStore();
const kplStore = useKplStore();
const router = useRouter();

const currentPage = ref(1);
const itemsPerPage = ref(window.innerWidth < 640 ? 5 : 9);
const isLoading = ref(false);

watch(() => kplStore.standings, (newStandings) => {
    if (newStandings.length === 0) {
        fetchStandings();
    }
}, { immediate: true });

async function fetchStandings() {
    try {
        isLoading.value = true;
        await kplStore.fetchStandings();
    } catch (error) {
        console.error("Failed to fetch standings:", error);
    } finally {
        isLoading.value = false;
    }
}

const paginatedTeams = computed<TeamStanding[]>(() => {
    if (kplStore.standings.length === 0) return [];
    const start = (currentPage.value - 1) * itemsPerPage.value;
    const end = start + itemsPerPage.value;
    return kplStore.standings.slice(start, end);
});

const totalPages = computed(() =>
    Math.ceil(kplStore.standings.length / itemsPerPage.value) || 1
);

function nextPage() {
    if (currentPage.value < totalPages.value) {
        currentPage.value++;
    }
}

function prevPage() {
    if (currentPage.value > 1) {
        currentPage.value--;
    }
}

function getPositionClass(position: number): string {
    if (position === 1) return "bg-green-600 text-white";
    if (position === 2) return "bg-blue-600 text-white";
    if (position === 3) return "bg-amber-500 text-white";
    if (position >= 17) return "bg-red-600 text-white";
    return "bg-gray-200 text-gray-700";
}

const leagueInsights = computed(() => {
    if (kplStore.standings.length === 0) return [];

    const leagueLeader = kplStore.standings.reduce((max, team) =>
        (max.points > team.points) ? max : team
    );

    const topScorer = kplStore.standings.reduce((max, team) =>
        (max.goals_for > team.goals_for) ? max : team
    );

    const bestDefense = kplStore.standings.reduce((min, team) =>
        (min.goals_against < team.goals_against) ? min : team
    );

    return [
        {
            title: "League Leader",
            team: leagueLeader,
            value: `${leagueLeader.points} pts`,
            subtext: `${leagueLeader.wins}W, ${leagueLeader.draws}D, ${leagueLeader.losses}L`,
            icon: StarIcon,
            cardClasses: "bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg md:rounded-xl p-3 md:p-5 shadow-md border border-gray-200 transform transition-all duration-300 hover:scale-105 hover:shadow-lg",
            iconContainerClasses: "bg-gray-600",
            titleClasses: "text-gray-700",
            avatarClasses: "border-dark-400",
            valueClasses: "text-gray-800",
            subtextClasses: "text-gray-600"
        },
        {
            title: "Top Scorer",
            team: topScorer,
            value: `${topScorer.goals_for} goals`,
            subtext: `${(topScorer.goals_for / topScorer.played).toFixed(1)} goals/game`,
            icon: UserIcon,
            cardClasses: "bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg md:rounded-xl p-3 md:p-5 shadow-md border border-blue-200 transform transition-all duration-300 hover:scale-105 hover:shadow-lg",
            iconContainerClasses: "bg-blue-600",
            titleClasses: "text-blue-700",
            avatarClasses: "border-blue-400",
            valueClasses: "text-blue-800",
            subtextClasses: "text-blue-600"
        },
        {
            title: "Best Defense",
            team: bestDefense,
            value: `${bestDefense.goals_against} GA`,
            subtext: `${(bestDefense.goals_against / bestDefense.played).toFixed(1)} conceded/game`,
            icon: ShieldIcon,
            cardClasses: "bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg md:rounded-xl p-3 md:p-5 shadow-md border border-amber-200 transform transition-all duration-300 hover:scale-105 hover:shadow-lg",
            iconContainerClasses: "bg-amber-600",
            titleClasses: "text-amber-700",
            avatarClasses: "border-amber-400",
            valueClasses: "text-amber-800",
            subtextClasses: "text-amber-600"
        }
    ];
});

onMounted(() => {
    authStore.initialize();
    if (!authStore.isAuthenticated) {
        router.push("/sign-in");
    }

    itemsPerPage.value = window.innerWidth < 640 ? 9 : 10;

    window.addEventListener('resize', () => {
        itemsPerPage.value = window.innerWidth < 640 ? 9 : 10;
    });

    if (kplStore.standings.length === 0) {
        fetchStandings();
    }
});
</script>

<style scoped>
/* Custom scrollbar for webkit browsers */
.overflow-x-auto::-webkit-scrollbar {
    height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
    background: #f0f0f0;
    border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
    background: #10b981;
    border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
    background: #059669;
}

/* Smooth scrolling */
.overflow-x-auto {
    scroll-behavior: smooth;
}
</style>