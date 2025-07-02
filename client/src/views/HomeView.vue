<template>
  <div>
    <div v-if="isLoading" class="flex justify-center items-center h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
    <div v-else>
      <UpcomingGames :fixtures="kplStore.fixtures" :standings="kplStore.standings" />
      <GameweekDetails />
      <Performance />
    </div>
  </div>
</template>

<script setup lang="ts">
import GameweekDetails from "@/components/Home/GameweekDetails.vue";
import UpcomingGames from "@/components/Home/UpcomingGames.vue";
import Performance from "@/components/Home/Performance.vue";
import { onMounted, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useKplStore } from "@/stores/kpl";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const kplStore = useKplStore();
const router = useRouter();
const isLoading = ref(true);



onMounted(async () => {
  try {
    if (!authStore.isAuthenticated) {
      router.push("/sign-in");
    } else {
      await authStore.initialize();
      if (kplStore.fixtures.length == 0 || kplStore.standings.length == 0) {
        await kplStore.fetchAllData();
      }
    }
  } finally {
    isLoading.value = false;
  }
});
</script>