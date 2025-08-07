<template>
  <div class="min-h-screen bg-gradient-to-b from-blue-50 to-gray-100 p-4 sm:p-6 lg:p-8">
    <div class="max-w-5xl mx-auto">


      <!-- Main Content -->
      <div class="bg-white/90 rounded-2xl border border-gray-100 p-6 sm:p-8 lg:p-10 shadow-lg glass-effect animate-slide-in">
        <!-- Section Title -->
        <div class="text-center mb-8">
          <h2 class="text-xl sm:text-2xl lg:text-3xl font-medium text-gray-800 mb-2">
            KPL Classic Leagues
          </h2>
          <p class="text-sm sm:text-base text-gray-600">
            Battle for the top spot where every point counts
          </p>
        </div>

        <!-- League Options -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
          <!-- Private Leagues -->
          <div class="border border-gray-100 rounded-xl p-5 sm:p-6 bg-white/80 glass-effect card">
            <h3 class="text-lg sm:text-xl font-semibold text-gray-800 mb-3">
              Private Leagues
            </h3>
            <p class="text-xs sm:text-sm text-gray-600 mb-4">
              Create or join exclusive leagues with friends and rivals
            </p>
            <div class="space-y-3">
              <button class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2.5 px-4 rounded-lg text-sm sm:text-base font-medium btn-primary">
                Create League
              </button>
              <button class="w-full border border-gray-200 text-gray-700 py-2.5 px-4 rounded-lg text-sm sm:text-base font-medium btn-secondary">
                Join League
              </button>
            </div>
          </div>

          <!-- Public Leagues -->
          <div class="border border-gray-100 rounded-xl p-5 sm:p-6 bg-white/80 glass-effect card">
            <h3 class="text-lg sm:text-xl font-semibold text-gray-800 mb-3">
              Public Leagues
            </h3>
            <p class="text-xs sm:text-sm text-gray-600 mb-4">
              Compete with the Kenyan football community
            </p>
            <div class="space-y-3">
              <button class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2.5 px-4 rounded-lg text-sm sm:text-base font-medium btn-primary">
                Create League
              </button>
              <button class="w-full border border-gray-200 text-gray-700 py-2.5 px-4 rounded-lg text-sm sm:text-base font-medium btn-secondary">
                Join League
              </button>
            </div>
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

<style scoped>
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

.glass-effect {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.btn-primary {
  background: linear-gradient(135deg, gray 0%, #000 100%);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(62, 67, 90, 0.3);
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

/* Responsive font sizes */
@media (max-width: 640px) {
  .text-2xl {
    font-size: 1.5rem;
  }
  .text-xl {
    font-size: 1.125rem;
  }
  .text-lg {
    font-size: 0.875rem;
  }
  .text-base {
    font-size: 0.75rem;
  }
  .text-sm {
    font-size: 0.7rem;
  }
  .text-xs {
    font-size: 0.65rem;
  }
}
</style>