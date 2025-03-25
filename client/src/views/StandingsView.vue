<template>
    <div class="p-10 md:p-10">
        <div class="mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div class="bg-white p-4 sm:p-6 text-center relative">
                <h1
                    class="text-xl sm:text-2xl md:text-3xl font-extrabold text-gray-700 tracking-wide flex flex-col sm:flex-row items-center justify-center sm:space-x-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 sm:h-10 sm:w-10 mb-2 sm:mb-0"
                        viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd"
                            d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z"
                            clip-rule="evenodd" />
                        <path
                            d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z" />
                    </svg>
                    <span>Kenyan Premier League Standings</span>
                </h1>
                <div class="absolute bottom-0 left-0 right-0 h-1 bg-red-600 animate-pulse"></div>
            </div>

            <div class="p-6 overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-green-100 text-green-800">
                        <tr>
                            <th v-for="header in tableHeaders" :key="header" class="p-3 font-semibold">
                                {{ header }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="team in paginatedTeams" :key="team.team"
                            :class="[
                                'hover:bg-green-50 transition-all duration-300 transform hover:scale-[1.01]',
                                {'bg-red-100': team.position >= 17}
                            ]">
                            <td class="p-3 text-center">
                                <span :class="getPositionClass(team.position)"
                                    class="inline-block w-8 h-8 rounded-full flex items-center justify-center font-bold">
                                    {{ team.position }}
                                </span>
                            </td>
                            <td class="p-3 text-center">
                                <img 
                                    v-if="team.team.logo_url" 
                                    :src="team.team.logo_url" 
                                    :alt="`${team.team.name} logo`" 
                                    class="w-10 h-10 mx-auto object-contain"
                                />
                            </td>
                            <td class="p-3 font-semibold text-gray-800">
                                {{ team.team.name }}
                            </td>
                            <td class="p-3 text-center">{{ team.played }}</td>
                            <td class="p-3 text-center text-green-600">
                                {{ team.wins }}
                            </td>
                            <td class="p-3 text-center text-yellow-600">
                                {{ team.draws }}
                            </td>
                            <td class="p-3 text-center text-red-600">
                                {{ team.losses }}
                            </td>
                            <td class="p-3 text-center">{{ team.goals_for }}</td>
                            <td class="p-3 text-center">
                                {{ team.goals_against }}
                            </td>
                            <td class="p-3 text-center font-bold">
                                {{ team.goal_differential }}
                            </td>
                            <td class="p-3 text-center font-bold text-green-700">
                                {{ team.points }}
                            </td>
                            <td class="p-3">
                                <div class="flex justify-center space-x-1">
                                    <span v-for="(result, index) in team.form" :key="index"
                                        :class="getFormBadgeColor(result)"
                                        class="w-6 h-6 rounded-full flex items-center justify-center text-white font-bold">
                                        {{ result }}
                                    </span>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <div class="flex justify-center items-center mt-6 space-x-4">
                    <button 
                        @click="prevPage" 
                        :disabled="currentPage === 1"
                        class="px-4 py-2 bg-green-500 text-white rounded-lg shadow-md hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-300 flex items-center"
                    >
                        
                        <<
                    </button>

                    <div class="text-gray-700 font-medium">
                        Page {{ currentPage }} of {{ totalPages }}
                    </div>

                    <button 
                        @click="nextPage" 
                        :disabled="currentPage === totalPages"
                        class="px-4 py-2 bg-green-500 text-white rounded-lg shadow-md hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-300 flex items-center"
                    >
                    >>
                    </button>
                </div>
            </div>

=            <div class="bg-gray-50 p-4 md:p-6 grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
                <div v-for="(insight, index) in leagueInsights" :key="index"
                    :class="insight.cardClasses">
                    <div class="flex items-center mb-2 md:mb-3">
                        <div :class="insight.iconContainerClasses" class="p-1 md:p-2 rounded-lg mr-2 md:mr-3">
                            <component :is="insight.icon" class="h-4 w-4 md:h-6 md:w-6 text-white" />
                        </div>
                        <h3 class="text-base md:text-lg font-bold" :class="insight.titleClasses">
                            {{ insight.title }}
                        </h3>
                    </div>
                    <div class="flex items-center">
                        <div
                            :class="insight.avatarClasses"
                            class="w-8 h-8 md:w-12 md:h-12 rounded-full flex items-center justify-center text-sm md:text-lg font-bold mr-2 md:mr-3 border-2">
                            {{ insight.team.team.name.substring(0, 2) }}
                        </div>
                        <div>
                            <p class="text-sm md:text-base text-gray-700 font-medium">{{ insight.team.team.name }}</p>
                            <p :class="insight.valueClasses" class="text-base md:text-xl font-bold">
                                {{ insight.value }}
                            </p>
                        </div>
                    </div>
                    <div :class="insight.subtextClasses" class="mt-1 md:mt-2 text-xs md:text-sm">
                        {{ insight.subtext }}
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
const itemsPerPage = 9;

const paginatedTeams = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return kplStore.standings.slice(start, end);
});

const totalPages = computed(() => Math.ceil(kplStore.standings.length / itemsPerPage));

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

function getFormBadgeColor(result: "W" | "D" | "L"): string {
    switch (result) {
        case "W":
            return "bg-green-500";
        case "D":
            return "bg-yellow-500";
        case "L":
            return "bg-red-500";
        default:
            return "bg-gray-500";
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
            value: `${leagueLeader.points} points`,
            subtext: `${leagueLeader.wins} wins, ${leagueLeader.draws} draws, ${leagueLeader.losses} losses`,
            icon: StarIcon,
            cardClasses: "bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-3 md:p-5 shadow-md border border-green-200 transform transition-all duration-300 hover:scale-105 hover:shadow-lg",
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
            subtext: `${(topScorer.goals_for / topScorer.played).toFixed(1)} goals per game`,
            icon: UserIcon,
            cardClasses: "bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-3 md:p-5 shadow-md border border-blue-200 transform transition-all duration-300 hover:scale-105 hover:shadow-lg",
            iconContainerClasses: "bg-blue-600",
            titleClasses: "text-blue-700",
            avatarClasses: "border-blue-400",
            valueClasses: "text-blue-800",
            subtextClasses: "text-blue-600"
        },
        {
            title: "Best Defense",
            team: bestDefense,
            value: `${bestDefense.goals_against} conceded`,
            subtext: `${(bestDefense.goals_against / bestDefense.played).toFixed(1)} goals per game`,
            icon: ShieldIcon,
            cardClasses: "bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-3 md:p-5 shadow-md border border-amber-200 transform transition-all duration-300 hover:scale-105 hover:shadow-lg",
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