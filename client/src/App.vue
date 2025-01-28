<script setup lang="ts">
import { RouterView } from "vue-router";
import { onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();

onMounted(async () => {
    await authStore.initialize();
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
