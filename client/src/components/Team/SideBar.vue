<template>
    <div
        class="w-full lg:w-1/3 bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.02]"
    >
        <!-- Team Stats Section -->
        <div class="mb-8">
            <div class="flex items-center mb-4">
                <h2 class="text-2xl font-bold text-gray-800">{{ team }}</h2>
            </div>

            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-blue-50 rounded-lg p-4 shadow-inner">
                        <div class="flex items-center justify-between">
                            <span class="text-gray-600">Total Points</span>
                            <span class="font-bold text-blue-600 text-lg">{{
                                totalPoints
                            }}</span>
                        </div>
                    </div>
                    <div class="bg-blue-50 rounded-lg p-4 shadow-inner">
                        <div class="flex items-center justify-between">
                            <span class="text-gray-600">Average Points</span>
                            <span class="font-bold text-blue-600 text-lg">{{
                                averagePoints.toFixed(1)
                            }}</span>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-blue-50 rounded-lg p-4 shadow-inner">
                        <div class="flex items-center justify-between">
                            <span class="text-gray-600">Highest Score</span>
                            <span class="font-bold text-blue-600 text-lg">{{
                                highestPoints
                            }}</span>
                        </div>
                    </div>
                    <div class="bg-blue-50 rounded-lg p-4 shadow-inner">
                        <div class="flex items-center justify-between">
                            <span class="text-gray-600">Overall Rank</span>
                            <span class="font-bold text-blue-600 text-sm">
                                {{ overallRank || "No rank" }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-6 flex space-x-4">
            <button
                class="px-5 py-2 bg-blue-600 text-white font-semibold rounded-xl shadow hover:bg-blue-700 transition duration-300 focus:outline-none focus:ring-2 focus:ring-blue-300"
            >
                Team
            </button>
            <button
                class="px-5 py-2 bg-white text-blue-600 font-semibold rounded-xl border border-blue-600 shadow hover:bg-blue-50 transition duration-300 focus:outline-none focus:ring-2 focus:ring-blue-300"
            >
                Transfers
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
const props = defineProps<{
    totalPoints: Number;
    averagePoints: Number;
    highestPoints: Number;
    overallRank: Number;
    team: string;
}>();
</script>

<style scoped>
.hover\:scale-\[1\.02\]:hover {
    transform: scale(1.02);
}
</style>
