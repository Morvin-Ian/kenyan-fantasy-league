<template>
    <div style="background: linear-gradient(135deg, #f0f4f8, #e0f2f1);" class="min-h-screen flex flex-col">
      <Navbar class="w-full top-0 left-0" />
      <main class="flex-grow mt-20 md:mt-16 lg:mt-6 mb-16">
        <RouterView />
      </main>
      <Footer class="hidden sm:block" />
    </div>
  </template>


<script setup lang="ts">
import { RouterView } from "vue-router";
import Navbar from "@/components/reusables/Navbar.vue";
import Footer from "@/components/reusables/Footer.vue";

</script>

<style scoped>
/* Custom styles (if needed) */
</style>