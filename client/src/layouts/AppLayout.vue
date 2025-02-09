<template>
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div class="mb-16">
            <Navbar />
        </div>

        <main>
            <RouterView />
        </main>
        <Footer />
    </div>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
import Navbar from "@/components/Navbar.vue";
import Footer from "@/components/Footer.vue";

</script>

<style scoped>
/* Custom styles (if needed) */
</style>