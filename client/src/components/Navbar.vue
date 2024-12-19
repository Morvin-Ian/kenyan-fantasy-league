<template>
  <nav class="bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="relative flex justify-between items-center h-16">
        <!-- Logo with responsive sizing -->
        <div class="flex items-center space-x-4 md:mt-12">
          <img src="/logo.png" alt="Logo" class="h-20 w-auto md:h-30" />

          <!-- Desktop Navigation - Moved inside the flex container with logo -->
          <div class="hidden md:flex md:items-center md:space-x-4">
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

        <!-- Authentication - Desktop (pushed to the right) -->
        <div class="hidden md:flex md:items-center">
          <div v-if="isAuthenticated" class="relative">
            <button @click="isAccountOpen = !isAccountOpen"
              class="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50">
              <img src="../assets/images/user.jpeg" alt="Avatar" class="h-12 w-12 rounded-full" />

              <span>
                <span class="font-bold text-xs">Hello, Morvin</span>
                <font-awesome-icon icon="fa-solid fa-chevron-down" />
              </span>
            </button>

            <Transition enter-active-class="transition ease-out duration-200" enter-from-class="opacity-0 translate-y-1"
              enter-to-class="opacity-100 translate-y-0" leave-active-class="transition ease-in duration-150"
              leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 translate-y-1">
              <div v-if="isAccountOpen"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5">
                <div class="py-1">
                  <button v-for="item in accountItems" :key="item.name" @click="item.action"
                    class="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600">
                    {{ item.name }}
                  </button>
                </div>
              </div>
            </Transition>
          </div>
          <a v-else href="#"
            class="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50">
            Sign In
          </a>
        </div>

        <!-- Mobile menu button -->
        <div class="flex md:hidden">
          <button @click="isOpen = !isOpen"
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-600 hover:text-red-600 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-red-500">
            <svg :class="['h-6 w-6 transition-transform', isOpen ? 'rotate-90' : '']" xmlns="http://www.w3.org/2000/svg"
              fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <Transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100" leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
      <div v-if="isOpen" class="md:hidden">
        <div class="px-2 pt-2 pb-3 space-y-1">
          <a v-for="item in navItems" :key="item.name" :href="item.href" :class="[
            'block px-3 py-2 rounded-md text-base font-medium',
            item.current
              ? 'text-red-600 bg-red-50'
              : 'text-gray-600 hover:text-red-600 hover:bg-red-50'
          ]">
            {{ item.name }}
          </a>

          <!-- Authentication - Mobile -->
          <div v-if="isAuthenticated">
            <button @click="isAccountOpen = !isAccountOpen"
              class="w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-red-600 hover:bg-red-50">
              <!-- <img src="../assets/images/user.jpeg" alt="Avatar" class="h-11 w-12 rounded-full" />

              <span>
                <span class="font-bold text-xs">Hello, Morvin</span>
                <font-awesome-icon icon="fa-solid fa-chevron-down" />
              </span> -->
              Account
            </button>
            <Transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0"
              enter-to-class="opacity-100" leave-active-class="transition duration-100 ease-in"
              leave-from-class="opacity-100" leave-to-class="opacity-0">
              <div v-if="isAccountOpen" class="px-3 py-2">
                <button v-for="item in accountItems" :key="item.name" @click="item.action"
                  class="w-full text-left block px-3 py-2 rounded-md text-base text-gray-600 hover:text-red-600 hover:bg-red-50">
                  {{ item.name }}
                </button>
              </div>
            </Transition>
          </div>
          <a v-else href="#"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-red-600 hover:bg-red-50">
            Sign In
          </a>
        </div>
      </div>
    </Transition>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const isOpen = ref(false)
const isAccountOpen = ref(false)
const isAuthenticated = ref(true) // Toggle this to simulate authentication
const router = useRouter()
const authStore = useAuthStore()

const navItems = ref([
  { name: 'Leagues', href: '#', current: true },
  { name: 'Teams', href: '#', current: false },
  { name: 'Fixtures', href: '#', current: false },
  { name: 'Results', href: '#', current: false },
  { name: 'Standings', href: '#', current: false },
])

const accountItems = ref([
  { name: 'Settings', action: () => handleSettings() },
  { name: 'Profile', action: () => handleProfile() },
  { name: 'Logout', action: () => handleLogout() }
])

const handleSettings = () => {
  router.push('/settings')
}

const handleProfile = () => {
  router.push('/profile')
}

const handleLogout = async () => {
  await authStore.logout();
  router.push('/sign-in');

};

</script>
