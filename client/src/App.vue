<script setup lang="ts">
import { onMounted } from "vue";
import { useAuthStore } from "./stores/auth";
import AppLayout from "@/layouts/AppLayout.vue";

const authStore = useAuthStore();

onMounted(async () => {
    await authStore.initialize();
});
</script>


<template>
    <AppLayout />
</template>

<style>
* {
    padding: 0;
    margin: 0;
}
</style>
