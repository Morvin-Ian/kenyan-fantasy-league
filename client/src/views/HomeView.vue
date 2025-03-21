<template>
    <div>
      <div v-if="isLoading" class="flex justify-center items-center h-screen">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
      <div v-else>
        <UpcomingGames />
        <!-- <Team /> -->
        <SearchPlayer />
        <Performance />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import Team from "@/components/Home/Team.vue";
  import SearchPlayer from "@/components/Home/SearchPlayer.vue";
  import UpcomingGames from "@/components/Home/UpcomingGames.vue";
  import Performance from "@/components/Home/Performance.vue";
  import { onMounted, ref } from "vue";
  import { useAuthStore } from "@/stores/auth";
  import { useRouter } from "vue-router";
  
  const authStore = useAuthStore();
  const router = useRouter();
  const isLoading = ref(true);
  
  onMounted(async () => {
    try {
      await authStore.initialize();
      if (!authStore.isAuthenticated) {
        router.push("/sign-in");
      }
    } finally {
      isLoading.value = false;
    }
  });
  </script>