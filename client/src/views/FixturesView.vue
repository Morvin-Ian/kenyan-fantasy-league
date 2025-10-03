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

      <MatchEventsModal
        v-if="selectedFixture"
        :isOpen="isEventsModalOpen"
        :fixture="selectedFixture"
        @close="closeEventsModal"
        @save-success="handleEventsSaveSuccess"
      />

      <ViewEventsModal
        v-if="selectedFixtureForView"
        :isOpen="isViewEventsModalOpen"
        :fixture="selectedFixtureForView"
        @close="closeViewEventsModal"
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
          @open-events="openEventsModal"
          @view-events="openViewEventsModal"
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
import MatchEventsModal from '@/components/Fixtures/MatchEventsModal.vue'
import ViewEventsModal from '@/components/Fixtures/ViewEventsModal.vue'

const kplStore = useKplStore();
const { fixtures } = storeToRefs(kplStore);
const isLoading = ref(false);
const activeTab = ref('upcoming');
const currentPage = ref(1);
const itemsPerPage = 5;

const isUploadModalOpen = ref(false);
const isEventsModalOpen = ref(false);
const isViewEventsModalOpen = ref(false); 
const selectedFixture = ref(null);
const selectedFixtureForView = ref(null); 

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

const openEventsModal = (fixture: any) => {
  selectedFixture.value = fixture;
  isEventsModalOpen.value = true;
};

const closeEventsModal = () => {
  isEventsModalOpen.value = false;
  selectedFixture.value = null;
};

const openViewEventsModal = (fixture: any) => {
  selectedFixtureForView.value = fixture;
  isViewEventsModalOpen.value = true;
};

const closeViewEventsModal = () => {
  isViewEventsModalOpen.value = false;
  selectedFixtureForView.value = null;
};

const handleEventsSaveSuccess = () => {
  fetchFixtures();
};

const handleUploadSuccess = () => {
  console.log('Lineup uploaded successfully');
};

</script>