<template>
    <div class="min-h-screen p-2 md:p-10">
        <div class="max-w-7xl mx-auto">
            <div class="bg-white rounded-xl md:rounded-3xl shadow-xl overflow-hidden transition-all duration-500 hover:shadow-2xl">
                <!-- Header Section - Made more compact on mobile -->
                <div class="bg-white p-3 md:p-6 text-center relative">
                    <h1 class="text-2xl md:text-4xl font-black text-gray-600 flex items-center justify-center space-x-2 md:space-x-4">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 md:h-10 md:w-10 text-gray-600" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd" />
                            <path d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z" />
                        </svg>
                        <span class="truncate">KPL Standings</span>
                    </h1>
                </div>

                <!-- Table Section with horizontal scrolling for small screens -->
                <div class="p-2 md:p-6">
                    <div class="overflow-x-auto rounded-lg shadow">
                        <table class="w-full text-xs md:text-sm border-collapse table-fixed">
                            <thead class="bg-green-100 text-green-800 sticky top-0 z-10">
                                <tr>
                                    <th v-for="header in tableHeaders" :key="header" 
                                        class="px-1 py-2 md:p-4 font-black uppercase tracking-wider text-center border-b-2 border-green-200 hover:bg-green-200 transition-colors">
                                        {{ getResponsiveHeader(header) }}
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr 
                                    v-for="team in paginatedTeams" 
                                    :key="team.team.id"
                                    class="hover:bg-green-50 transition-all duration-300 transform hover:scale-[1.01] hover:shadow-lg rounded-xl"
                                >
                                    <td class="p-1 md:p-3 text-center">
                                        <span 
                                            :class="getPositionClass(team.position)"
                                            class="inline-block w-6 h-6 md:w-10 md:h-10 rounded-full shadow-md flex items-center justify-center font-bold text-dark transition-transform hover:scale-110"
                                        >
                                            {{ team.position }}
                                        </span>
                                    </td>

                                    <td class="p-1 md:p-3 text-center">
                                        <img 
                                            v-if="team.team.logo_url" 
                                            :src="team.team.logo_url" 
                                            :alt="`${team.team.name} logo`" 
                                            class="w-8 h-8 md:w-12 md:h-12 mx-auto object-contain transition-transform rounded-full hover:scale-125 hover:rotate-6"
                                        />
                                    </td>

                                    <td class="p-1 md:p-3 font-semibold text-gray-800 hover:text-green-600 transition-colors max-w-[80px] md:max-w-none truncate">
                                        {{ team.team.name }}
                                    </td>

                                    <td class="p-1 md:p-3 text-center font-medium text-gray-700">{{ team.played }}</td>
                                    <td class="p-1 md:p-3 text-center text-green-600 font-bold">{{ team.wins }}</td>
                                    <td class="p-1 md:p-3 text-center text-yellow-600 font-bold">{{ team.draws }}</td>
                                    <td class="p-1 md:p-3 text-center text-red-600 font-bold">{{ team.losses }}</td>
                                    <td class="p-1 md:p-3 text-center text-blue-600">{{ team.goals_for }}</td>
                                    <td class="p-1 md:p-3 text-center text-red-500">{{ team.goals_against }}</td>
                                    <td class="p-1 md:p-3 text-center font-bold text-purple-600">{{ team.goal_differential }}</td>
                                    <td class="p-1 md:p-3 text-center font-bold text-green-700">{{ team.points }}</td>

                                    <td class="p-1 md:p-3">
                                        <div class="flex justify-center space-x-1 md:space-x-2">
                                            <span 
                                                v-for="(result, index) in getMobileFormResults(team.form)" 
                                                :key="index"
                                                :class="getFormBadgeColor(result)"
                                                class="w-5 h-5 md:w-7 md:h-7 rounded-full flex items-center justify-center text-white font-bold text-xs md:text-sm transition-transform hover:scale-110 shadow-md"
                                            >
                                                {{ result }}
                                            </span>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Pagination Controls - Simplified for mobile -->
                    <div class="flex justify-center items-center mt-4 md:mt-8 space-x-2 md:space-x-6">
                        <button 
                            @click="prevPage" 
                            :disabled="currentPage === 1"
                            class="group px-3 py-2 md:px-6 md:py-3 bg-green-500 text-white text-xs md:text-base rounded-full shadow-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-300 flex items-center space-x-1 md:space-x-2"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5 transform group-hover:-translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                            </svg>
                            <span class="hidden md:inline">Previous</span>
                        </button>

                        <div class="text-gray-700 font-bold text-sm md:text-lg">
                            {{ currentPage }}/{{ totalPages }}
                        </div>

                        <button 
                            @click="nextPage" 
                            :disabled="currentPage === totalPages"
                            class="group px-3 py-2 md:px-6 md:py-3 bg-green-500 text-white text-xs md:text-base rounded-full shadow-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-300 flex items-center space-x-1 md:space-x-2"
                        >
                            <span class="hidden md:inline">Next</span>
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5 transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- League Insights with improved mobile layout -->
                <div class="bg-gray-50 p-3 md:p-6 grid grid-cols-1 gap-3 md:grid-cols-3 md:gap-6">
                    <div 
                        v-for="(insight, index) in leagueInsights" 
                        :key="index"
                        :class="insight.cardClasses"
                        class="transform transition-all duration-500 hover:scale-105 hover:shadow-2xl"
                    >
                        <div class="flex items-center mb-2 md:mb-4">
                            <div 
                                :class="insight.iconContainerClasses" 
                                class="p-2 md:p-3 rounded-lg md:rounded-xl mr-2 md:mr-4 shadow-md"
                            >
                                <component 
                                    :is="insight.icon" 
                                    class="h-4 w-4 md:h-6 md:w-6 text-white" 
                                />
                            </div>
                            <h3 
                                :class="insight.titleClasses" 
                                class="text-base md:text-xl font-black tracking-tight"
                            >
                                {{ insight.title }}
                            </h3>
                        </div>
                        <div class="flex items-center">
                            <div 
                                :class="insight.avatarClasses"
                                class="w-8 h-8 md:w-12 md:h-12 rounded-full flex items-center justify-center text-xs md:text-lg font-bold mr-2 md:mr-4 border-2 md:border-4 shadow-md"
                            >
                                {{ insight.team.team.name.substring(0, 2) }}
                            </div>
                            <div>
                                <p class="text-sm md:text-base text-gray-700 font-semibold truncate">
                                    {{ insight.team.team.name }}
                                </p>
                                <p 
                                    :class="insight.valueClasses" 
                                    class="text-base md:text-2xl font-black tracking-tight"
                                >
                                    {{ insight.value }}
                                </p>
                            </div>
                        </div>
                        <div 
                            :class="insight.subtextClasses" 
                            class="mt-2 md:mt-3 text-xs md:text-sm opacity-75"
                        >
                            {{ insight.subtext }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from '@/stores/auth';
import { useKplStore } from "@/stores/kpl";
import { useRouter } from 'vue-router';
import { StarIcon, UserIcon, ShieldIcon } from 'lucide-vue-next';
import type { TeamStanding } from "@/helpers/types/team";

const authStore = useAuthStore();
const kplStore = useKplStore();
const router = useRouter();

const tableHeaders: string[] = [
    "Pos",
    "Team",
    "",
    "P",
    "W",
    "D",
    "L",
    "GF",
    "GA",
    "GD",
    "Pts",
    "Form",
];

const currentPage = ref(1);
const itemsPerPage = ref(window.innerWidth < 640 ? 5 : 9); // Fewer items per page on mobile

// Function to get responsive headers for small screens
function getResponsiveHeader(header: string): string {
    // For mobile screens, simplify headers
    if (window.innerWidth < 640) {
        if (header === "Position") return "Pos";
        if (header === "Goals For") return "GF";
        if (header === "Goals Against") return "GA";
        if (header === "Goal Differential") return "GD";
        if (header === "Points") return "Pts";
    }
    return header;
}

// Function to limit form results on mobile
function getMobileFormResults(form: string[]): string[] {
    if (window.innerWidth < 640) {
        return form.slice(0, 3); // Show only the last 3 results on mobile
    }
    return form;
}

// Update items per page on window resize
onMounted(() => {
    window.addEventListener('resize', () => {
        itemsPerPage.value = window.innerWidth < 640 ? 5 : 9;
    });
});

const paginatedTeams = computed<TeamStanding[]>(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value;
    const end = start + itemsPerPage.value;
    return kplStore.standings.slice(start, end);
});

const totalPages = computed(() => Math.ceil(kplStore.standings.length / itemsPerPage.value));

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

function getFormBadgeColor(result: string): string {
    const formResults = ["W", "D", "L"];
    if (!formResults.includes(result)) return "bg-gray-500"; // Default color for unexpected values
    return result === "W" ? "bg-green-500" : result === "D" ? "bg-yellow-500" : "bg-red-500";
}

function getPositionClass(position: number): string {
    if (position === 1) return "bg-green-600 text-white";
    if (position === 2) return "bg-blue-600 text-white";
    if (position === 3) return "bg-amber-500 text-white";
    if (position >= 17) return "bg-red-600 text-white";
    return "bg-gray-200 text-gray-700";
}

const leagueInsights = computed(() => {
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
            cardClasses: "bg-gradient-to-br from-green-50 to-green-100 rounded-lg md:rounded-xl p-3 md:p-5 shadow-md border border-green-200 transform transition-all duration-300 hover:scale-105 hover:shadow-lg",
            iconContainerClasses: "bg-green-600",
            titleClasses: "text-green-700",
            avatarClasses: "border-green-400",
            valueClasses: "text-green-800",
            subtextClasses: "text-green-600"
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

onMounted(async () => {
  await authStore.initialize();
  if (!authStore.isAuthenticated) {
    router.push("/sign-in");
  }
});
</script>