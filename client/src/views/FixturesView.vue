<template>
  <div class="bg-gray-50">
    <div class="max-w-4xl mx-auto px-3 sm:px-4 md:px-6 py-4 sm:py-6 md:py-8">
      <div v-if="isLoading" class="flex justify-center items-center min-h-screen">
        <div class="text-center">
          <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-gray-900 mx-auto"></div>
          <p class="mt-4 text-gray-600">Loading fixture ...</p>
        </div>
      </div>      

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
          :availableGameweeks="availableGameweeks"
          :activeGameweek="activeGameweek"
          :selectedGameweek="selectedGameweek"
          @update-tab="activeTab = $event"
          @update-gameweek="selectedGameweek = $event"
        />

        <FixtureList 
          :activeTab="activeTab" 
          :fixtures="filteredFixtures" 
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
import MatchEventsModal from '@/components/Fixtures/MatchEventsModal.vue'
import ViewEventsModal from '@/components/Fixtures/ViewEventsModal.vue'

const kplStore = useKplStore();
const { fixtures } = storeToRefs(kplStore);
const isLoading = ref(false);
const activeTab = ref('upcoming');
const currentPage = ref(1);
const selectedGameweek = ref<string | number>('all');
const itemsPerPage = 5;

const isUploadModalOpen = ref(false);
const isEventsModalOpen = ref(false);
const isViewEventsModalOpen = ref(false); 
const selectedFixture = ref(null);
const selectedFixtureForView = ref(null); 

const availableGameweeks = computed(() => {
  const gameweeks = new Set<number>();
  fixtures.value.forEach(fixture => {
    if (fixture.gameweek) {
      gameweeks.add(fixture.gameweek);
    }
  });
  return Array.from(gameweeks).sort((a, b) => a - b);
});

const activeGameweek = computed(() => {
  const activeFixture = fixtures.value.find(fixture => fixture.is_active === true);
  return activeFixture?.gameweek || availableGameweeks.value[availableGameweeks.value.length - 1] || 1;
});

const fixturesByGameweek = computed(() => {
  if (selectedGameweek.value === 'all') {
    return fixtures.value;
  }
  return fixtures.value.filter(fixture => fixture.gameweek === selectedGameweek.value);
});

const sortedFixturesByGameweek = computed(() => {
  return [...fixturesByGameweek.value].sort((a, b) => 
    new Date(a.match_date).getTime() - new Date(b.match_date).getTime()
  );
});

const upcomingAndLiveFixtures = computed(() => {
  return sortedFixturesByGameweek.value.filter(fixture =>
    fixture.status === 'upcoming' || fixture.status === 'live'
  );
});

const finishedFixtures = computed(() => {
  return sortedFixturesByGameweek.value
    .filter(fixture => fixture.status === 'completed');
});

const postponedFixtures = computed(() => {
  return sortedFixturesByGameweek.value.filter(fixture => fixture.status === 'postponed');
});

const filteredFixtures = computed(() => {
  if (activeTab.value === 'upcoming') return upcomingAndLiveFixtures.value;
  if (activeTab.value === 'finished') return finishedFixtures.value;
  if (activeTab.value === 'postponed') return postponedFixtures.value;
  return [];
});

const totalPages = computed(() => Math.ceil(filteredFixtures.value.length / itemsPerPage) || 1);

watch(() => fixtures.value, (newFixtures) => {
  if (newFixtures.length === 0) {
    fetchFixtures();
  } else {
    if (selectedGameweek.value === 'all') {
      selectedGameweek.value = activeGameweek.value;
    }
  }
}, { immediate: true });

watch([selectedGameweek, activeTab], () => {
  currentPage.value = 1;
});

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