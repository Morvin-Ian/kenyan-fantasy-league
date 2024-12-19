<template>
  <div v-if="isAuthenticated">
    <Navbar/>
  </div>
</template>

<script setup lang="ts">
import Navbar from '@/components/Navbar.vue';
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const isAuthenticated = ref(false);
const router = useRouter();

onMounted(() => {
  const token = localStorage.getItem('token');
  if (token) {
    isAuthenticated.value = true;
  } else {
    router.replace({ name: 'sign-in' }); 
  }
});
</script>
