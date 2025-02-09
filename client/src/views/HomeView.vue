<template>
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <UpcomingGames />
        <Team />
        <SearchPlayer />
        <Performance />
    </div>
</template>

<script setup lang="ts">

import Team from "@/components/Home/Team.vue";
import SearchPlayer from "@/components/Home/SearchPlayer.vue";
import UpcomingGames from "@/components/Home/UpcomingGames.vue";
import Performance from "@/components/Home/Performance.vue";
import { onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

onMounted(async () => {
    await authStore.initialize();
    if (!authStore.isAuthenticated) {
        router.push("/sign-in");
    }
});
</script>
