<template>
  <div class="p-2 sm:p-4">
    <div class="max-w-7xl mx-auto space-y-4 sm:space-y-8">
      <div class="text-center bg-white/80 backdrop-blur-sm p-4 sm:p-8 rounded-xl">
        <h1
          class="text-lg sm:text-xl md:text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-600 to-gray-700 mb-2 sm:mb-4">
          Leagues & Cups
        </h1>
        <p class="text-sm sm:text-base text-gray-600 mx-auto max-w-md">
          Elevate your competitive spirit by competing in diverse leagues, challenging players globally and locally.
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
        <div class="bg-white/80 backdrop-blur-sm border-0 shadow-xl rounded-xl sm:rounded-2xl p-4 sm:p-6">
          <h2 class="text-lg sm:text-xl md:text-2xl font-bold text-gray-700 mb-2 sm:mb-4">Classic Leagues</h2>
          <p class="text-xs sm:text-sm md:text-base text-gray-600 mb-3 sm:mb-4">
            Compete where the highest point total determines the champion.
          </p>
          <div class="space-y-3 sm:space-y-4">
            <div class="bg-blue-50/50 p-3 sm:p-4 rounded-lg">
              <h3 class="font-semibold text-sm sm:text-base md:text-lg mb-2">Private Leagues</h3>
              <div class="flex flex-col xs:flex-row space-y-2 xs:space-y-0 xs:space-x-2 sm:space-x-4">
                <button
                  class="bg-blue-500 text-white px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg hover:bg-blue-600 transition w-full xs:w-auto">
                  Create League
                </button>
                <button
                  class="border border-green-500 text-green-600 px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg hover:bg-green-50 transition w-full xs:w-auto">
                  Join League
                </button>
              </div>
            </div>
            <div class="bg-green-50/50 p-3 sm:p-4 rounded-lg">
              <h3 class="font-semibold text-sm sm:text-base md:text-lg mb-2">Public Leagues</h3>
              <div class="flex flex-col xs:flex-row space-y-2 xs:space-y-0 xs:space-x-2 sm:space-x-4">
                <button
                  class="bg-blue-500 text-white px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg hover:bg-blue-600 transition w-full xs:w-auto">
                  Create League
                </button>
                <button
                  class="border border-green-500 text-green-600 px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg hover:bg-green-50 transition w-full xs:w-auto">
                  Join League
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white/80 backdrop-blur-sm border-0 shadow-xl rounded-xl sm:rounded-2xl p-4 sm:p-6">
          <h2 class="text-lg sm:text-xl md:text-2xl font-bold text-gray-700 mb-2 sm:mb-4">Head-to-Head Leagues</h2>
          <p class="text-xs sm:text-sm md:text-base text-gray-600 mb-3 sm:mb-4">
            Direct competition where weekly matchups determine progression.
          </p>
          <div class="space-y-3 sm:space-y-4">
            <div class="bg-purple-50/50 p-3 sm:p-4 rounded-lg">
              <h3 class="font-semibold text-sm sm:text-base md:text-lg mb-2">Private Leagues</h3>
              <div class="flex flex-col xs:flex-row space-y-2 xs:space-y-0 xs:space-x-2 sm:space-x-4">
                <button
                  class="bg-blue-500 text-white px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg hover:bg-blue-600 transition w-full xs:w-auto">
                  Create League
                </button>
                <button
                  class="border border-green-500 text-green-600 px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg hover:bg-green-50 transition w-full xs:w-auto">
                  Join League
                </button>
              </div>
            </div>
            <div class="bg-teal-50/50 p-3 sm:p-4 rounded-lg">
              <h3 class="font-semibold text-sm sm:text-base md:text-lg mb-2">Public Leagues</h3>
              <div class="flex flex-col xs:flex-row space-y-2 xs:space-y-0 xs:space-x-2 sm:space-x-4">
                <button
                  class="bg-blue-500 text-white px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg hover:bg-blue-600 transition w-full xs:w-auto">
                  Create League
                </button>
                <button
                  class="border border-green-500 text-green-600 px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg hover:bg-green-50 transition w-full xs:w-auto">
                  Join League
                </button>
              </div>
            </div>
          </div>
        </div>

        <div
          class="bg-white/80 backdrop-blur-sm border-0 shadow-xl rounded-xl sm:rounded-2xl p-4 sm:p-6 sm:col-span-2 lg:col-span-1">
          <h2 class="text-lg sm:text-xl md:text-2xl font-bold text-gray-700 mb-2 sm:mb-4">Global Leagues</h2>
          <p class="text-xs sm:text-sm md:text-base text-gray-600 mb-3 sm:mb-4">
            Challenge players worldwide across multiple competitive arenas.
          </p>
          <div class="overflow-x-auto -mx-4 sm:mx-0">
            <table class="w-full text-left text-xs sm:text-sm">
              <thead>
                <tr class="bg-gray-100">
                  <th class="p-2 sm:p-4">League</th>
                  <th class="p-2 sm:p-4">Current</th>
                  <th class="p-2 sm:p-4">Previous</th>
                  <th class="p-2 sm:p-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="league in globalLeagues" :key="league.name" class="border-b">
                  <td class="p-2 sm:p-4">{{ league.name }}</td>
                  <td class="p-2 sm:p-4">{{ league.current.toLocaleString() }}</td>
                  <td class="p-2 sm:p-4">{{ league.previous.toLocaleString() }}</td>
                  <td class="p-2 sm:p-4">
                    <button
                      class="bg-blue-500 text-white px-2 py-1 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg hover:bg-blue-600 transition">
                      View
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
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

const globalLeagues = [
  { name: "Challenge", current: 985724, previous: 985747 },
  { name: "Kenya", current: 285416, previous: 277745 },
  { name: "Overall", current: 274033, previous: 528166 }
];

onMounted(async () => {
  await authStore.initialize();
  if (!authStore.isAuthenticated) {
    router.push("/sign-in");
  }
});
</script>

<style scoped>
@media (min-width: 475px) {
  .xs\:flex-row {
    flex-direction: row;
  }

  .xs\:space-y-0 {
    margin-top: 0;
  }

  .xs\:space-x-2>*+* {
    margin-left: 0.5rem;
  }

  .xs\:w-auto {
    width: auto;
  }
}
</style>