<script setup lang="ts">
import { RouterView } from "vue-router";
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

<template>
    <RouterView />
</template>

<style>
* {
    padding: 0;
    margin: 0;
}
</style>
