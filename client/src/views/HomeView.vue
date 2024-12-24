<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />
    <UpcomingGames/>
    <Team/>
    <SearchPlayer/>
    <Performance/>
    <Footer/>
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

const races = ref([
  {
    country: 'Belgium',
    name: 'De Brabantse Pijl',
    status: 'ENDED',
    startDate: '13.04.2022',
    stages: 'One day race',
    lockIcon: false
  },
  {
    country: 'France',
    name: 'Paris - Roubaix',
    status: 'UPCOMING',
    startDate: '17.04.2022',
    stages: 'One day race',
    lockIcon: false
  },
  {
    country: 'Italy',
    name: 'Tour of the Alps',
    status: 'LOCKED',
    startDate: '18.04.2022',
    stages: '5',
    lockIcon: true
  },
  {
    country: 'Belgium',
    name: 'La Flèche Wallonne',
    status: 'LOCKED',
    startDate: '20.04.2022',
    stages: 'One day race',
    lockIcon: true
  }
])

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/sign-in');
  }
})
</script>
