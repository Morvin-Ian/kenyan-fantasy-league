<template>
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      <Navbar class="w-full top-0 left-0" />
      <main class="flex-grow mt-20 md:mt-16 lg:mt-12 mb-16">
        <RouterView />
      </main>
      <Footer class="w-full hidden sm:block" />
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