<template>
    <div class="w-full lg:w-1/3 bg-white rounded-xl shadow-lg p-6">
        <!-- Team Stats -->
        <div class="mb-8">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Team Stats</h2>
            <div class="space-y-4">
                <div class="flex justify-between">
                    <span class="text-gray-600">Total Points</span>
                    <span class="font-semibold text-gray-800">{{
                        totalPoints
                    }}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Average Points</span>
                    <span class="font-semibold text-gray-800">{{
                        averagePoints
                    }}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Highest Score</span>
                    <span class="font-semibold text-gray-800">{{
                        highestPoints
                    }}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Overall Rank</span>
                    <span class="font-semibold text-gray-800">{{
                        overallRank
                    }}</span>
                </div>
            </div>
        </div>

        <!-- Upcoming Fixtures -->
        <div class="mb-8">
            <h2 class="text-xl font-bold text-gray-800 mb-4">
                Upcoming Fixtures
            </h2>
            <div class="space-y-4">
                <div
                    v-for="fixture in upcomingFixtures"
                    :key="fixture.date"
                    class="flex justify-between"
                >
                    <span class="text-gray-600">{{ fixture.match }}</span>
                    <span class="text-sm text-gray-500">{{
                        fixture.date
                    }}</span>
                </div>
            </div>
        </div>

        <!-- Recent Results -->
        <div class="mb-8">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Recent Results</h2>
            <div class="space-y-4">
                <div
                    v-for="result in recentResults"
                    :key="result.date"
                    class="flex justify-between"
                >
                    <span class="text-gray-600">{{ result.match }}</span>
                    <span class="text-sm text-gray-500">{{ result.date }}</span>
                </div>
            </div>
        </div>

        <!-- Top Performers -->
        <div>
            <h2 class="text-xl font-bold text-gray-800 mb-4">Top Performers</h2>
            <div class="space-y-4">
                <div
                    v-for="performer in topPerformers"
                    :key="performer.name"
                    class="flex items-center space-x-4"
                >
                    <img
                        :src="performer.image"
                        :alt="performer.name"
                        class="h-10 w-10 rounded-full"
                    />
                    <div>
                        <p class="font-semibold text-gray-800">
                            {{ performer.name }}
                        </p>
                        <p class="text-sm text-gray-600">
                            {{ performer.points }} Points
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { Fixture, Result, Performer } from "@/types/team";

const props = defineProps<{
    totalPoints: number;
    averagePoints: number;
    highestPoints: number;
    overallRank: string;
    upcomingFixtures: Fixture[];
    recentResults: Result[];
    topPerformers: Performer[];
}>();
</script>
