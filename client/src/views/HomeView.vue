<template>
  <div>
    <div v-if="isLoading" class="flex justify-center items-center h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
    <div v-else>
      <UpcomingGames 
        :fixtures="kplStore.fixtures" 
        :standings="kplStore.standings" 
      />
      <Performance />
      <GameweekDetails />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, defineAsyncComponent } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useKplStore } from "@/stores/kpl";
import { useFantasyStore } from "@/stores/fantasy";
import { useRouter } from "vue-router";


const UpcomingGames = defineAsyncComponent(() => import('@/components/Home/UpcomingGames.vue'));
const Performance = defineAsyncComponent(() => import('@/components/Home/Performance.vue'));
const GameweekDetails = defineAsyncComponent(() => import('@/components/Home/GameweekDetails.vue'));

const authStore = useAuthStore();
const kplStore = useKplStore();
const fantasyStore = useFantasyStore();
const router = useRouter();
const isLoading = ref(true);



onMounted(async () => {
  try {
    if (!authStore.isAuthenticated) {
      router.push('/sign-in');
      return;
    }
    await Promise.all([
      authStore.initialize(),
      kplStore.fixtures.length === 0 || kplStore.standings.length === 0
        ? kplStore.fetchAllData()
        : Promise.resolve(),
      fantasyStore.goalsLeaderboard.length === 0
        ? fantasyStore.fetchTopGoalsScorers(5)
        : Promise.resolve(),
      !fantasyStore.gameweekStatus
        ? fantasyStore.fetchGameweekStatus()
        : Promise.resolve(),
    ]);
  } finally {
    isLoading.value = false;
  }
});
</script>