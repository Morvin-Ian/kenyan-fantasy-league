<script setup lang="ts">
import { onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "./stores/auth";
import AppLayout from "@/layouts/AppLayout.vue";

const authStore = useAuthStore();
const route = useRoute();

const excludedRoutes = ["sign-in", "sign-up", "activation", "reset-password", "reset-password-request"];

const isExcludedRoute = computed(() => excludedRoutes.includes(route.name as string));

onMounted(async () => {
    await authStore.initialize();
});
</script>

<template>
    <AppLayout v-if="!isExcludedRoute">
        <RouterView />
    </AppLayout>
    <RouterView v-else />
</template>

<style>
* {
    padding: 0;
    margin: 0;
}
</style>