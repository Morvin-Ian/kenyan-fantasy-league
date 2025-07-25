<template>
  <div class="p-6 mx-auto max-w-4xl">
    
    <!-- Header -->
    <div class="text-center mb-8">
      <h1 class="text-3xl font-semibold text-gray-800 mb-3">
        Kenyan Leagues & Cups
      </h1>
      <p class="text-gray-600 max-w-lg mx-auto">
        Compete in Kenya's top leagues and cups
      </p>
    </div>

    <!-- Main Content -->
    <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      
      <!-- Section Title -->
      <div class="text-center mb-6">
        <h2 class="text-2xl font-medium text-gray-800 mb-2">
          KPL Classic Leagues
        </h2>
        <p class="text-gray-600">
          Compete where the highest point total crowns the champion
        </p>
      </div>

      <!-- League Options -->
      <div class="grid md:grid-cols-2 gap-6">
        
        <!-- Private Leagues -->
        <div class="border border-gray-200 rounded-lg p-5">
          <h3 class="text-lg font-medium text-gray-800 mb-3">
            Private Leagues
          </h3>
          <p class="text-sm text-gray-600 mb-4">
            Create or join exclusive leagues with friends
          </p>
          <div class="space-y-3">
            <button class="w-full bg-gray-800 text-white py-2.5 px-4 rounded-md text-sm font-medium hover:bg-gray-900 transition-colors">
              Create League
            </button>
            <button class="w-full border border-gray-300 text-gray-700 py-2.5 px-4 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors">
              Join League
            </button>
          </div>
        </div>

        <!-- Public Leagues -->
        <div class="border border-gray-200 rounded-lg p-5">
          <h3 class="text-lg font-medium text-gray-800 mb-3">
            Public Leagues
          </h3>
          <p class="text-sm text-gray-600 mb-4">
            Join open competitions with the community
          </p>
          <div class="space-y-3">
            <button class="w-full bg-gray-800 text-white py-2.5 px-4 rounded-md text-sm font-medium hover:bg-gray-900 transition-colors">
              Create League
            </button>
            <button class="w-full border border-gray-300 text-gray-700 py-2.5 px-4 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors">
              Join League
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

onMounted(async () => {
  await authStore.initialize();
  if (!authStore.isAuthenticated) {
    router.push("/sign-in");
  }
});
</script>

<style>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

.animate-slide-in {
  animation: slideIn 0.6s ease-out;
  animation-fill-mode: both;
}

.gradient-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.glass-effect {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}
</style>