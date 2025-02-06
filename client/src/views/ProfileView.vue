<template>
    <div
        class="min-h-screen bg-gradient-to-br from-sky-100 via-pink-100 to-violet-100"
    >
        <Navbar />

        <div class="max-w-5xl mx-auto p-8">
            <!-- Profile Header -->
            <div class="text-center mb-12 animate-fade-in-down">
                <h1 class="text-4xl font-bold text-gray-800 mb-4">
                    Profile Dashboard
                </h1>
                <p class="text-xl text-gray-600">
                    Manage your personal information
                </p>
            </div>

            <!-- Main Profile Card -->
            <div
                class="bg-white/60 backdrop-blur-lg rounded-2xl shadow-lg overflow-hidden transform hover:scale-[1.02] transition-all duration-300"
            >
                <!-- Profile Content Grid -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <!-- Profile Picture Section -->
                    <div
                        class="relative p-8 flex flex-col items-center justify-center bg-gradient-to-br from-sky-200 to-pink-200"
                    >
                        <div class="relative group">
                            <div
                                class="absolute -inset-0.5 bg-gradient-to-r from-sky-300 to-pink-300 rounded-full opacity-75 group-hover:opacity-100 blur transition duration-500"
                            ></div>
                            <img
                                :src="getProfilePhotoUrl()"
                                :alt="user.first_name"
                                class="relative w-48 h-48 rounded-full object-cover border-4 border-white shadow-xl transform transition duration-500"
                            />
                        </div>

                        <button
                            @click="editProfilePhoto"
                            class="mt-6 px-6 py-3 bg-white text-sky-600 rounded-xl shadow-lg hover:bg-sky-50 transform hover:scale-105 transition duration-300 font-semibold flex items-center gap-2"
                        >
                            <font-awesome-icon icon="fa-solid fa-camera" />
                            Update Photo
                        </button>

                        <div class="mt-4 text-center">
                            <h2 class="text-2xl font-bold text-gray-800">
                                {{ user.firstName }} {{ user.last_name }}
                            </h2>
                            <p class="text-gray-600">@{{ user.username }}</p>
                        </div>
                    </div>

                    <!-- User Details Section -->
                    <div class="lg:col-span-2 p-8">
                        <div class="space-y-8">
                            <!-- Personal Information -->
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <TransitionGroup
                                    enter-active-class="transition duration-500 ease-out"
                                    enter-from-class="transform -translate-y-4 opacity-0"
                                    enter-to-class="transform translate-y-0 opacity-100"
                                >
                                    <template
                                        v-for="(field, key) in userFields"
                                        :key="key"
                                    >
                                        <div
                                            class="bg-white/70 backdrop-blur rounded-xl p-4 hover:bg-white/90 transition-all duration-300 shadow-sm"
                                        >
                                            <label
                                                class="block text-sm font-medium text-gray-700 mb-2"
                                            >
                                                {{ field.label }}
                                            </label>
                                            <input
                                                v-if="isEditing"
                                                v-model="user[key]"
                                                :type="field.type"
                                                class="w-full px-4 py-2 bg-white rounded-lg border-2 border-transparent focus:border-sky-400 focus:ring-2 focus:ring-sky-400 transition-all duration-300"
                                            />
                                            <p
                                                v-else
                                                class="text-gray-800 text-lg font-medium"
                                            >
                                                {{ user[key] }}
                                            </p>
                                        </div>
                                    </template>
                                </TransitionGroup>
                            </div>
                        </div>

                        <!-- Action Buttons -->
                        <div class="mt-8 flex justify-end space-x-4">
                            <button
                                @click="toggleEdit"
                                :class="{
                                    'bg-gradient-to-r from-sky-400 to-blue-400':
                                        !isEditing,
                                    'bg-gradient-to-r from-emerald-400 to-teal-400':
                                        isEditing,
                                }"
                                class="px-8 py-3 text-white rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 font-semibold"
                            >
                                <span class="flex items-center gap-2">
                                    {{
                                        isEditing
                                            ? "Save Changes"
                                            : "Edit Profile"
                                    }}
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Decorative Elements -->
            <div
                class="fixed top-0 right-0 -z-10 w-96 h-96 bg-pink-100 rounded-full blur-3xl opacity-50"
            ></div>
            <div
                class="fixed bottom-0 left-0 -z-10 w-96 h-96 bg-sky-100 rounded-full blur-3xl opacity-50"
            ></div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import default_profile from "../assets/images/user.jpeg";
import Navbar from "@/components/Navbar.vue";

const authStore = useAuthStore();
const isEditing = ref(false);
const user = computed(
    () =>
        authStore.user ?? {
            username: "",
            first_name: "",
            last_name: "",
            email: "",
            gender: "",
            country: "",
            city: "",
        },
);

const getProfilePhotoUrl = () => {
    const profilePhoto = authStore.user?.profile_photo;

    if (!profilePhoto) {
        return default_profile;
    }

    if (profilePhoto.endsWith("default.png")) {
        return default_profile;
    }

    const image = profilePhoto.split("/");
    const image_name = image[image.length - 1];
    return `/mediafiles/${image_name}`;
};

const userFields = {
    username: { label: "Username", type: "text" },
    email: { label: "Email Address", type: "email" },
    first_name: { label: "First Name", type: "text" },
    last_name: { label: "Last Name", type: "text" },
    gender: { label: "Gender", type: "text" },
    country: { label: "Country", type: "text" },
    city: { label: "City", type: "text" },
};

const toggleEdit = () => {
    if (isEditing.value) {
        // Save changes (API calls can be added here)
        console.log("Updated User Data:", user);
    }
    isEditing.value = !isEditing.value;
};

const editProfilePhoto = () => {
    const newPhoto = prompt("Enter the URL of the new profile photo:");
    if (newPhoto) {
        user.profilePhoto = newPhoto;
    }
};

onMounted(async () => {
    await authStore.initialize();
    if (!authStore.isAuthenticated) {
        router.push("/sign-in");
    }
});
</script>

<style scoped>
.animate-fade-in-down {
    animation: fadeInDown 1s ease-out;
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Add smooth page transition */
.page-enter-active,
.page-leave-active {
    transition: opacity 0.5s ease;
}

.page-enter-from,
.page-leave-to {
    opacity: 0;
}
</style>
