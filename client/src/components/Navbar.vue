<template>
  <div>
    <!-- Desktop Navigation -->
    <nav class="bg-white">
      <div class="md:hidden fixed bg-white w-full mt-0 flex justify-center ">
          <img src="/logo.png" alt="Logo" class="h-16 w-auto" />
        </div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Mobile-only logo -->
      

        <!-- Desktop navigation with aligned logo and items -->
        <div class="hidden md:flex justify-between items-center h-20">
          <div class="flex items-center space-x-8">
            <img src="/logo.png" alt="Logo" class="h-20 w-auto" />

            <div class="flex items-center space-x-4">
              <template v-for="item in navItems" :key="item.name">
                <a :href="item.href" :class="[
                  'px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200',
                  item.current
                    ? 'text-red-600 bg-red-50'
                    : 'text-gray-600 hover:text-red-600 hover:bg-red-50'
                ]">
                  {{ item.name }}
                </a>
              </template>
            </div>
          </div>

          <!-- Desktop Account Menu -->
          <div class="flex items-center">
            <div v-if="isAuthenticated" class="relative">
              <button @click="isAccountOpen = !isAccountOpen"
                class="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50">
                <img src="../assets/images/user.jpeg" alt="Avatar" class="h-11 w-12 rounded-full" />
                <span class="ml-2">
                  <span class="font-bold text-xs">Hello, Morvin</span>
                  <font-awesome-icon icon="fa-solid fa-chevron-down" class="ml-1" />
                </span>
              </button>

              <div v-if="isAccountOpen"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5">
                <div class="py-1">
                  <button v-for="item in accountItems" :key="item.name" @click="item.action"
                    class="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600">
                    {{ item.name }}
                  </button>
                </div>
              </div>
            </div>
            <a v-else href="#"
              class="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50">
              Sign In
            </a>
          </div>
        </div>
      </div>
    </nav>

    <!-- Mobile Bottom Navigation -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-gray-200 border-t rounded-full border-gray-200 mx-2 mb-1">
      <div class="grid grid-cols-4 h-16">
        <a v-for="item in mobileNavItems" :key="item.name" :href="item.href"
          class="flex flex-col items-center justify-center" :class="[
            item.current
              ? 'text-red-600'
              : 'text-gray-600'
          ]">
          <font-awesome-icon :icon="item.icon" class="text-lg" />
          <span class="text-xs mt-1">{{ item.name }}</span>
        </a>
      </div>
    </nav>

    <!-- Add bottom padding to main content on mobile -->
    <div class="pb-20 md:pb-0">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const isAccountOpen = ref(false)
const isAuthenticated = ref(true)
const router = useRouter()
const authStore = useAuthStore()

// Simplified navigation items
const navItems = ref([
  { name: 'Leagues', href: '#', current: true },
  { name: 'Team', href: '/fkl_team', current: false },
  { name: 'Fixtures', href: '#', current: false },
  { name: 'Results', href: '#', current: false },
  { name: 'Standings', href: '#', current: false },
])

// Mobile navigation items with icons
const mobileNavItems = ref([
  { name: 'Home', href: '/', icon: "fa-solid fa-home", current: false },
  { name: 'Team', href: '/fkl_team', icon: "fa-solid fa-users", current: false },
  { name: 'Leagues', href: '#', icon: "fa-solid fa-futbol", current: false },
  { name: 'Account', href: '#', icon: "fa-solid fa-user", current: false },
])

const accountItems = ref([
  { name: 'Profile', action: () => handleProfile() },
  { name: 'Logout', action: () => handleLogout() }
])

const handleProfile = () => {
  router.push('/profile')
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/sign-in')
}
</script>

<style scoped>
.md\:hidden.fixed {
  z-index: 1000;
}
</style>