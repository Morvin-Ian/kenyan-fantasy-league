<template>
    <div class="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
        <div class="max-w-6xl mx-auto px-4 py-8 lg:px-8">
            <div class="text-center mb-12">
                <h1 class="text-2xl lg:text-3xl font-semibold text-gray-900 mb-2">
                    Profile Dashboard
                </h1>
                <p class="text-base lg:text-lg text-gray-600">
                    Manage your personal information and settings
                </p>
            </div>

            <div class="bg-white rounded-2xl shadow-xl overflow-hidden ring-1 ring-gray-100">
                <div class="grid grid-cols-1 lg:grid-cols-4 min-h-[600px]">
                    <div class="lg:col-span-1 bg-gradient-to-b from-gray-800 to-gray-900 p-6 lg:p-8 flex flex-col items-center justify-center text-center">
                        <div class="relative mb-6 group">
                            <div class="w-28 h-28 lg:w-36 lg:h-36 rounded-full overflow-hidden bg-white p-1 shadow-lg ring-2 ring-gray-200">
                                <img :src="previewImage || getProfilePhotoUrl()" :alt="user.first_name || 'Profile'"
                                    class="w-full h-full rounded-full object-cover" />
                                
                                <div v-if="isEditing"
                                    class="absolute inset-0 bg-black/60 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 cursor-pointer"
                                    @click="triggerFileUpload">
                                    <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                                    </svg>
                                </div>
                            </div>
                        </div>

                        <input type="file" ref="fileInput" @change="handleFileUpload" accept="image/*" class="hidden" />

                        <div class="text-white mb-6">
                            <h2 class="text-lg lg:text-xl font-semibold mb-1">
                                {{ user.first_name }} {{ user.last_name }}
                            </h2>
                            <p class="text-gray-300 text-sm">@{{ user.username }}</p>
                        </div>

                        <div class="flex items-center justify-center mb-6">
                            <div class="w-2.5 h-2.5 bg-green-400 rounded-full animate-pulse"></div>
                            <span class="ml-2 text-gray-300 text-xs">Online</span>
                        </div>

                        <button v-if="isEditing" @click="triggerFileUpload"
                            class="lg:hidden mb-6 px-4 py-2 bg-white text-gray-900 rounded-lg hover:bg-gray-100 transition-colors duration-300 text-sm font-medium">
                            Change Photo
                        </button>

                        <button @click="logout"
                            class="w-full px-6 py-2.5 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors duration-300 font-medium text-sm">
                            <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                            </svg>
                            Logout
                        </button>
                    </div>

                    <!-- Form Section -->
                    <div class="lg:col-span-3 p-6 lg:p-8">
                        <div class="space-y-6">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 lg:gap-6">
                                <div v-for="(field, key) in userFields" :key="key"
                                    class="bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors duration-200"
                                    :class="{ 'bg-blue-50 hover:bg-blue-100': isEditing }">
                                    
                                    <label class="block text-xs lg:text-sm font-semibold text-gray-700 mb-2">
                                        {{ field.label }}
                                    </label>

                                    <select v-if="isEditing && key === 'gender'" v-model="user[key]"
                                        class="w-full px-3 py-2.5 bg-white border border-gray-200 rounded-lg focus:border-gray-900 focus:ring-2 focus:ring-gray-900/20 transition-all duration-200 text-gray-900 text-sm">
                                        <option value="" disabled>Select gender</option>
                                        <option v-for="option in field.options" :key="option" :value="option">
                                            {{ option }}
                                        </option>
                                    </select>

                                    <input v-else-if="isEditing" v-model="user[key]" :type="field.type"
                                        class="w-full px-3 py-2.5 bg-white border border-gray-200 rounded-lg focus:border-gray-900 focus:ring-2 focus:ring-gray-900/20 transition-all duration-200 text-gray-900 text-sm"
                                        :placeholder="`Enter your ${field.label.toLowerCase()}`" />

                                    <div v-else class="px-3 py-2.5 text-gray-900 font-medium text-sm min-h-[44px] flex items-center">
                                        {{ user[key] || `No ${field.label.toLowerCase()} provided` }}
                                    </div>
                                </div>
                            </div>

                            <!-- Action Buttons -->
                            <div class="flex flex-col sm:flex-row gap-3 sm:justify-end pt-6 border-t border-gray-200">
                                <button v-if="isEditing" @click="cancelEdit"
                                    class="w-full sm:w-auto px-5 py-2.5 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200 font-medium text-sm order-2 sm:order-1">
                                    Cancel
                                </button>
                                <button @click="toggleEdit"
                                    class="w-full sm:w-auto px-5 py-2.5 rounded-lg transition-all duration-200 font-medium text-sm order-1 sm:order-2"
                                    :class="{
                                        'bg-gray-900 text-white hover:bg-gray-800': !isEditing,
                                        'bg-green-500 text-white hover:bg-green-600': isEditing
                                    }">
                                    <svg v-if="!isEditing" class="w-4 h-4 inline mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                    </svg>
                                    <svg v-else class="w-4 h-4 inline mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                    </svg>
                                    {{ isEditing ? "Save Changes" : "Edit Profile" }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Success Notification -->
        <div v-if="showNotification && !authStore.error"
            class="fixed top-4 right-4 z-50 max-w-xs sm:max-w-sm bg-white rounded-lg shadow-2xl border border-gray-100 transform transition-all duration-500"
            :class="{ 'translate-x-0 opacity-100': showNotification, 'translate-x-full opacity-0': !showNotification }">
            <div class="p-4 flex items-start">
                <div class="flex-shrink-0 w-7 h-7 bg-green-100 rounded-full flex items-center justify-center mr-3">
                    <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="flex-1">
                    <p class="text-gray-900 font-medium text-sm">Profile Updated!</p>
                    <p class="text-gray-600 text-xs mt-1">Your changes have been saved successfully.</p>
                </div>
                <button @click="showNotification = false" class="ml-2 text-gray-400 hover:text-gray-600">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
        </div>

        <!-- Error Notification -->
        <div v-if="authStore.error"
            class="fixed top-4 right-4 z-50 max-w-xs sm:max-w-sm bg-white rounded-lg shadow-2xl border border-red-100">
            <div class="p-4 flex items-start">
                <div class="flex-shrink-0 w-7 h-7 bg-red-100 rounded-full flex items-center justify-center mr-3">
                    <svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="flex-1">
                    <p class="text-red-800 font-medium text-sm">{{ authStore.error }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import default_profile from "../assets/images/user.jpeg";

const router = useRouter();
const authStore = useAuthStore();
const isEditing = ref(false);
const fileInput = ref(null);
const previewImage = ref(null);
const showNotification = ref(false);
const originalUserData = ref({});

const user = ref({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    gender: "",
    country: "",
    city: "",
    ...authStore.user
});

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

const userFields = {
    username: { label: "Username", type: "text" },
    email: { label: "Email Address", type: "email" },
    first_name: { label: "First Name", type: "text" },
    last_name: { label: "Last Name", type: "text" },
    gender: { label: "Gender", type: "select", options: ["Male", "Female", "Other"] },
    country: { label: "Country", type: "text" },
    city: { label: "City", type: "text" },
};

const toggleEdit = async () => {
    if (isEditing.value) {
        try {
            const formData = new FormData();
            for (const key in user.value) {
                if (key !== "profile_photo" && user.value[key]) {
                    formData.append(key, user.value[key]);
                }
            }

            if (user.value.profile_photo instanceof File) {
                formData.append("profile_photo", user.value.profile_photo);
            }

            await authStore.updateProfile(formData, user.value.id);

            showNotification.value = true;
            setTimeout(() => {
                showNotification.value = false;
            }, 4000);

            isEditing.value = false;
        } catch (error) {
           console.error("Profile update failed:", error);
        }
    } else {
        originalUserData.value = JSON.parse(JSON.stringify(user.value));
        isEditing.value = true;
    }
};

const cancelEdit = () => {
    user.value = JSON.parse(JSON.stringify(originalUserData.value));
    previewImage.value = null;
    isEditing.value = false;
};

const triggerFileUpload = () => {
    if (isEditing.value) {
        fileInput.value.click();
    }
};

const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
        user.value.profile_photo = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.value = e.target.result;
        };
        reader.readAsDataURL(file);
    } else {
        user.value.profile_photo = null;
    }
};

const logout = async () => {
    try {
        await authStore.logout();
        router.push("/sign-in");
    } catch (error) {
        authStore.error = "Logout failed. Please try again.";
    }
};

onMounted(async () => {
    if (!authStore.isAuthenticated) {
        router.push("/sign-in");
    } else {
        await authStore.initialize();
        user.value = {
            ...user.value,
            ...authStore.user
        };
    }
});
</script>

<style scoped>
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

.animate-fade-in-down {
    animation: fadeInDown 0.6s ease-out;
}

* {
    transition-property: color, background-color, border-color, transform, opacity;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 200ms;
}

input:focus,
select:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
    .grid {
        gap: 0.75rem;
    }
    .text-2xl {
        font-size: 1.5rem;
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

button:hover:not(:disabled) {
    transform: translateY(-1px);
}

button:active:not(:disabled) {
    transform: translateY(0);
}
</style>