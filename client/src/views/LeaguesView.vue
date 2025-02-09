<template>
    <div class="p-4">
      <div class="max-w-7xl mx-auto space-y-8">
        <!-- Elegant Header -->
        <div class="text-center bg-white/80 backdrop-blur-sm  p-8">
          <h1 class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-600 to-gray-700 mb-4">
            Leagues & Cups
          </h1>
          <p class="text-gray-600 mx-auto">
            Elevate your competitive spirit by competing in diverse leagues, challenging players globally and locally.
          </p>
        </div>
  
        <!-- Leagues Grid -->
        <div class="grid md:grid-cols-3 gap-6">
          <!-- Classic Leagues -->
          <div class="bg-white/80 backdrop-blur-sm border-0 shadow-xl rounded-2xl p-6">
            <h2 class="text-2xl font-bold text-gray-700 mb-4">Classic Leagues</h2>
            <p class="text-gray-600 mb-4">
              Compete where the highest point total determines the champion.
            </p>
            <div class="space-y-4">
              <div class="bg-blue-50/50 p-4 rounded-lg">
                <h3 class="font-semibold text-lg mb-2">Private Leagues</h3>
                <div class="flex space-x-4">
                  <button class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition">
                    Create League
                  </button>
                  <button class="border border-green-500 text-green-600 px-4 py-2 rounded-lg hover:bg-green-50 transition">
                    Join League
                  </button>
                </div>
              </div>
              <div class="bg-green-50/50 p-4 rounded-lg">
                <h3 class="font-semibold text-lg mb-2">Public Leagues</h3>
                <div class="flex space-x-4">
                  <button class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition">
                    Create League
                  </button>
                  <button class="border border-green-500 text-green-600 px-4 py-2 rounded-lg hover:bg-green-50 transition">
                    Join League
                  </button>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Head-to-Head Leagues -->
          <div class="bg-white/80 backdrop-blur-sm border-0 shadow-xl rounded-2xl p-6">
            <h2 class="text-2xl font-bold text-gray-700 mb-4">Head-to-Head Leagues</h2>
            <p class="text-gray-600 mb-4">
              Direct competition where weekly matchups determine progression.
            </p>
            <div class="space-y-4">
              <div class="bg-purple-50/50 p-4 rounded-lg">
                <h3 class="font-semibold text-lg mb-2">Private Leagues</h3>
                <div class="flex space-x-4">
                  <button class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition">
                    Create League
                  </button>
                  <button class="border border-green-500 text-green-600 px-4 py-2 rounded-lg hover:bg-green-50 transition">
                    Join League
                  </button>
                </div>
              </div>
              <div class="bg-teal-50/50 p-4 rounded-lg">
                <h3 class="font-semibold text-lg mb-2">Public Leagues</h3>
                <div class="flex space-x-4">
                  <button class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition">
                    Create League
                  </button>
                  <button class="border border-green-500 text-green-600 px-4 py-2 rounded-lg hover:bg-green-50 transition">
                    Join League
                  </button>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Global Leagues -->
          <div class="bg-white/80 backdrop-blur-sm border-0 shadow-xl rounded-2xl p-6">
            <h2 class="text-2xl font-bold text-gray-700 mb-4">Global Leagues</h2>
            <p class="text-gray-600 mb-4">
              Challenge players worldwide across multiple competitive arenas.
            </p>
            <div class="overflow-x-auto">
              <table class="w-full text-left">
                <thead>
                  <tr class="bg-gray-100">
                    <th class="p-4">League</th>
                    <th class="p-4">Current</th>
                    <th class="p-4">Previous</th>
                    <th class="p-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="league in globalLeagues" :key="league.name" class="border-b">
                    <td class="p-4">{{ league.name }}</td>
                    <td class="p-4">{{ league.current.toLocaleString() }}</td>
                    <td class="p-4">{{ league.previous.toLocaleString() }}</td>
                    <td class="p-4">
                      <button class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition">
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
  
  const globalLeagues = [
    { name: "Challenge", current: 985724, previous: 985747 },
    { name: "Kenya", current: 285416, previous: 277745 },
    { name: "Overall", current: 274033, previous: 528166 }
  ];
  </script>
  
  <style scoped>
  /* Additional custom styles if needed */
  </style>