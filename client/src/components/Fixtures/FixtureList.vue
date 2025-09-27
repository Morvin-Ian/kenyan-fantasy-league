<template>
  <div class="space-y-3 sm:space-y-4">
    <div v-if="activeTab === 'upcoming' && paginatedFixtures.length === 0" class="text-center py-8 sm:py-12">
      <div class="max-w-sm mx-auto">
        <svg class="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-gray-400 mb-3 sm:mb-4" fill="none"
          stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
        <h3 class="text-base sm:text-lg font-semibold text-gray-800 mb-1 sm:mb-2">No Upcoming Fixtures</h3>
        <p class="text-gray-500 text-xs sm:text-sm">Check back later for scheduled matches</p>
      </div>
    </div>
    <div v-else-if="activeTab === 'finished' && paginatedFixtures.length === 0" class="text-center py-8 sm:py-12">
      <div class="max-w-sm mx-auto">
        <svg class="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-gray-400 mb-3 sm:mb-4" fill="none"
          stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <h3 class="text-base sm:text-lg font-semibold text-gray-800 mb-1 sm:mb-2">No Finished Matches</h3>
        <p class="text-gray-500 text-xs sm:text-sm">Completed matches will appear here</p>
      </div>
    </div>
    <div v-else-if="activeTab === 'postponed' && paginatedFixtures.length === 0" class="text-center py-8 sm:py-12">
      <div class="max-w-sm mx-auto">
        <svg class="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-gray-400 mb-3 sm:mb-4" fill="none"
          stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
        </svg>
        <h3 class="text-base sm:text-lg font-semibold text-gray-800 mb-1 sm:mb-2">No Postponed Matches</h3>
        <p class="text-gray-500 text-xs sm:text-sm">Postponed matches will appear here</p>
      </div>
    </div>
    <div v-else class="space-y-3 sm:space-y-4">
        <FixtureCard
            v-for="fixture in fixtures"
            :key="fixture.id"
            :match="fixture"
            @open-upload="openUploadModal"
            @view-lineup="openLineupModal"
        />

        <LineUpModal
            v-if="selectedFixture"
            :fixture="selectedFixture"
            @close="selectedFixture = null"
        />    
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, computed} from "vue"
import FixtureCard from '@/components/Fixtures/FixtureCard.vue';
import LineUpModal from "./LineUpModal.vue";
import type { Fixture } from "@/helpers/types/team";

const props = defineProps<{
  activeTab: string;
  fixtures: any[];
  currentPage: number;
  itemsPerPage: number;
}>();

const selectedFixture = ref<Fixture | null>(null);

const emit = defineEmits<{
  (e: 'open-upload', fixture: any): void;
}>();

const paginatedFixtures = computed(() => {
  const start = (props.currentPage - 1) * props.itemsPerPage;
  return props.fixtures.slice(start, start + props.itemsPerPage);
});

const openLineupModal = (fixture: Fixture) => {
  selectedFixture.value = fixture;
};

const openUploadModal = (fixture: any) => {
  emit('open-upload', fixture);
};
</script>