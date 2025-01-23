<template>
  <div class="min-h-screen  bg-gradient-to-br from-blue-50 to-indigo-100">
    <Navbar />
    <UpcomingGames />
    <Team />
    <SearchPlayer />
    <!-- <Performance /> -->
    <div class=" md:block">
      <Footer />
    </div>
  </div>
</template>


<script setup>
import { onMounted, ref } from 'vue'
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import Team from '@/components/home/Team.vue';
import SearchPlayer from '@/components/home/SearchPlayer.vue';
import UpcomingGames from '@/components/home/UpcomingGames.vue';
import Performance from '@/components/home/Performance.vue';

const authStore = useAuthStore();
const router = useRouter();

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/sign-in');
  }
})
</script>
