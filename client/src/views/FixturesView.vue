<template>
  <div class="bg-gray-50">
    <div class="max-w-4xl mx-auto px-3 sm:px-4 md:px-6 py-4 sm:py-6 md:py-8">
      <LoadingSpinner v-if="isLoading" />
      <LineupUploadModal 
        v-if="selectedFixture" 
        :isOpen="isUploadModalOpen" 
        :fixture="selectedFixture"
        @close="closeUploadModal" 
        @upload-success="handleUploadSuccess" 
      />

      <div v-else-if="fixtures.length > 0" class="space-y-3 sm:space-y-4 md:space-y-6">
        <FixtureHeader />
        <FixtureTabs 
          :activeTab="activeTab" 
          :upcomingCount="upcomingAndLiveFixtures.length"
          :finishedCount="finishedFixtures.length" 
          :postponedCount="postponedFixtures.length"
          @update-tab="activeTab = $event" 
        />
        <FixtureList 
          :activeTab="activeTab" 
          :fixtures="currentFixtures" 
          :currentPage="currentPage"
          :itemsPerPage="itemsPerPage" 
          @open-upload="openUploadModal"
        />

        <Pagination 
          :currentPage="currentPage" 
          :totalPages="totalPages" 
          @next-page="nextPage" 
          @prev-page="prevPage" />
      </div>
      <EmptyState v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useKplStore } from '@/stores/kpl';
import LineupUploadModal from '@/components/Fixtures/LineupUploadModal.vue';
import FixtureHeader from '@/components/Fixtures/FixtureHeader.vue';
import FixtureTabs from '@/components/Fixtures/FixtureTabs.vue';
import FixtureList from '@/components/Fixtures/FixtureList.vue';
import Pagination from '@/components/Fixtures/Pagination.vue';
import EmptyState from '@/components/Fixtures/EmptyState.vue';
import LoadingSpinner from '@/components/Fixtures/LoadingSpinner.vue';

const kplStore = useKplStore();
const { fixtures } = storeToRefs(kplStore);
const isLoading = ref(false);
const activeTab = ref('upcoming');
const currentPage = ref(1);
const itemsPerPage = 5;

watch(() => fixtures.value, (newFixtures) => {
  if (newFixtures.length === 0) {
    fetchFixtures();
  }
}, { immediate: true });

async function fetchFixtures() {
  try {
    isLoading.value = true;
    await kplStore.fetchFixtures(true);
  } catch (error) {
    console.error("Failed to fetch fixtures:", error);
  } finally {
    isLoading.value = false;
  }
}

const upcomingAndLiveFixtures = computed(() => {
  return fixtures.value.filter(fixture =>
    fixture.status === 'upcoming' || fixture.status === 'live'
  );
});

const finishedFixtures = computed(() => {
  return fixtures.value
    .filter(fixture => fixture.status === 'completed')
    .sort((a, b) => new Date(b.match_date).getTime() - new Date(a.match_date).getTime());
});

const postponedFixtures = computed(() => {
  return fixtures.value.filter(fixture => fixture.status === 'postponed');
});

const currentFixtures = computed(() => {
  if (activeTab.value === 'upcoming') return upcomingAndLiveFixtures.value;
  if (activeTab.value === 'finished') return finishedFixtures.value;
  if (activeTab.value === 'postponed') return postponedFixtures.value;
  return [];
});

const totalPages = computed(() => Math.ceil(currentFixtures.value.length / itemsPerPage) || 1);

const isUploadModalOpen = ref(false);
const selectedFixture = ref(null);

const openUploadModal = (fixture: any) => {
  selectedFixture.value = fixture;
  isUploadModalOpen.value = true;
};

const closeUploadModal = () => {
  isUploadModalOpen.value = false;
  selectedFixture.value = null;
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};

const handleUploadSuccess = () => {
  console.log('Lineup uploaded successfully');
};
</script>