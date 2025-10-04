<template>
    <div>
        <!-- Desktop Navigation -->
        <nav class="bg-white ">
            <div class="md:hidden fixed inset-x-0 top-0 bg-white flex justify-center py-1">
                <router-link to="/">
                    <img src="/logo.png" alt="Logo" class="h-14 w-auto" />
                </router-link>
            </div>
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="hidden md:flex justify-between items-center h-20">
                    <div class="flex items-center space-x-8">
                        <img src="/logo.png" alt="Logo" class="h-20 w-auto" />
                        <div class="flex items-center space-x-4">
                            <template v-for="item in navItems" :key="item.name">
                                <router-link :to="item.href" :class="[
                                    'px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200',
                                    isActive(item.href)
                                        ? 'text-red-600 bg-red-50'
                                        : 'text-gray-600 hover:text-red-600 hover:bg-red-50',
                                ]">
                                    {{ item.name }}
                                </router-link>
                            </template>
                        </div>
                    </div>

                    <!-- Desktop Account Menu -->
                    <div class="flex items-center">
                        <div v-if="authStore.isAuthenticated" class="relative">
                            <button @click="isAccountOpen = !isAccountOpen"
                                class="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50 transition-colors duration-200">
                                <img :src="getProfilePhotoUrl()" alt="Avatar"
                                    class="h-10 w-10 rounded-full object-cover" />
                                <span class="ml-2 flex items-center">
                                    <span class="font-bold text-xs">Hello, {{ authStore.user?.username }}</span>
                                    <ChevronDownIcon class="ml-1 h-4 w-4 transition-transform duration-200"
                                        :class="{ 'rotate-180': isAccountOpen }" />
                                </span>
                            </button>

                            <transition enter-active-class="transition ease-out duration-100"
                                enter-from-class="transform opacity-0 scale-95"
                                enter-to-class="transform opacity-100 scale-100"
                                leave-active-class="transition ease-in duration-75"
                                leave-from-class="transform opacity-100 scale-100"
                                leave-to-class="transform opacity-0 scale-95">
                                <div v-if="isAccountOpen" style="z-index: 500"
                                    class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5">
                                    <div class="py-1">
                                        <button v-for="item in accountItems" :key="item.name" @click="item.action"
                                            class="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600 transition-colors duration-200">
                                            {{ item.name }}
                                        </button>
                                    </div>
                                </div>
                            </transition>
                        </div>
                        <router-link v-else to="/sign-in"
                            class="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50 transition-colors duration-200">
                            Sign In
                        </router-link>
                    </div>
                </div>
            </div>
        </nav>

        <!-- Mobile Bottom Navigation (Fixed to Bottom) -->
        <nav class="md:hidden fixed inset-x-0 bottom-0 bg-white rounded-t-2xl border-t border-gray-300 shadow-lg">
            <div class="grid grid-cols-5 h-16">
                <router-link v-for="item in mobileNavItems" :key="item.name" :to="item.href"
                    class="flex flex-col items-center justify-center transition-colors duration-200"
                    :class="[isActive(item.href) ? 'text-red-600' : 'text-gray-600 hover:text-red-600']">

                    <!-- Replace icon per item -->
                    <component :is="item.icon" class="h-5 w-5" />

                    <span class="text-xs mt-1">{{ item.name }}</span>
                </router-link>
            </div>
        </nav>


    </div>
</template>


<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import default_profile from "../../assets/images/user.jpeg";
import {
    HomeIcon,
    UsersIcon,
    TrophyIcon,
    UserIcon,
    ChevronDownIcon,
    ChartBarIcon,
} from "@heroicons/vue/24/solid";


const isAccountOpen = ref(false);
const isAuthenticated = ref(true);
const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// Simplified navigation items
const navItems = ref([
    { name: "Home", href: "/", current: false },
    { name: "Leagues", href: "/leagues", current: false },
    { name: "Team", href: "/fkl_team", current: false },
    { name: "Fixtures", href: "/fixtures", current: false },
    { name: "Standings", href: "/standings", current: false },
]);

// Mobile navigation items with icons
const mobileNavItems = ref([
    { name: "Home", href: "/", icon: HomeIcon },
    { name: "Team", href: "/fkl_team", icon: UsersIcon },
    { name: "Leagues", href: "/leagues", icon: TrophyIcon },
    { name: "Standings", href: "/standings", icon: ChartBarIcon },
    { name: "Account", href: "/profile", icon: UserIcon },
]);


const accountItems = ref([
    { name: "Profile", action: () => handleProfile() },
    { name: "Logout", action: () => handleLogout() },
]);

const handleProfile = () => {
    router.push("/profile");
};

const handleLogout = async () => {
    await authStore.logout();
    router.push("/sign-in");
};

const getProfilePhotoUrl = () => {
    const profilePhoto = authStore.user?.profile_photo;

    if (!profilePhoto) {
        return default_profile;
    }

    if (profilePhoto.endsWith("default.png")) {
        return default_profile;
    }

    return profilePhoto;
};

const isActive = (href: string) => {
    return route.path === href;
};
</script>

<style scoped>
.md\:hidden.fixed {
    z-index: 1000;
}
</style>
