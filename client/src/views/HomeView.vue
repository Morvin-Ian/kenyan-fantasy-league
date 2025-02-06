<template>
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Navbar />
        <UpcomingGames />
        <Team />
        <SearchPlayer />
        <Performance />
        <div class="md:block">
            <Footer />
        </div>
    </div>
</template>

<script setup lang="ts">
import Navbar from "@/components/Navbar.vue";
import Footer from "@/components/Footer.vue";
import Team from "@/components/home/Team.vue";
import SearchPlayer from "@/components/home/SearchPlayer.vue";
import UpcomingGames from "@/components/home/UpcomingGames.vue";
import Performance from "@/components/home/Performance.vue";
</script>
