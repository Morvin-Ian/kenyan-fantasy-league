<template>
    <nav class="bg-white mt-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Logo and Brand -->
          <div class="flex items-center mt-8">
            <a href="/" class="text-xl font-bold text-red-600">
              <img src="/logo.png" alt="">
            </a>
          </div>
  
          <!-- Desktop Menu -->
          <div class="hidden md:flex items-center space-x-4">
            <a href="#" class="text-gray-800 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium">
              Home
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium">
              League
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium">
              Teams
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium">
              Fixtures
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium">
              Results
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium">
              Standings
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium">
              Sign In
            </a>
            <a href="#" class="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700 transition duration-150">
              Sign Up
            </a>
          </div>
  
          <!-- Mobile Menu Button -->
          <div class="md:hidden flex items-center">
            <button
              @click="isOpen = !isOpen"
              class="inline-flex items-center justify-center p-2 rounded-md text-gray-600 hover:text-red-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-red-500"
            >
              <!-- Use v-if/v-else for menu icons -->
              <svg
                v-if="!isOpen"
                class="h-6 w-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
              <svg
                v-else
                class="h-6 w-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
  
      <!-- Mobile Menu -->
      <transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div v-if="isOpen" class="md:hidden">
          <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white shadow-lg">
            <a href="#" class="text-gray-800 hover:text-red-600 block px-3 py-2 rounded-md text-base font-medium">
              Home
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 block px-3 py-2 rounded-md text-base font-medium">
              League
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 block px-3 py-2 rounded-md text-base font-medium">
              Teams
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 block px-3 py-2 rounded-md text-base font-medium">
              Fixtures
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 block px-3 py-2 rounded-md text-base font-medium">
              Results
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 block px-3 py-2 rounded-md text-base font-medium">
              Standings
            </a>
            <a href="#" class="text-gray-600 hover:text-red-600 block px-3 py-2 rounded-md text-base font-medium">
              Sign In
            </a>
            <a href="#" class="bg-red-600 text-white block px-3 py-2 rounded-md text-base font-medium hover:bg-red-700 transition duration-150">
              Sign Up
            </a>
          </div>
        </div>
      </transition>
    </nav>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  
  const isOpen = ref(false)
  </script>