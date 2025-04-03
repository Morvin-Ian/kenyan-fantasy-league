<template>
    <div class="">
        <div class="max-w-5xl mx-auto p-8">
            <div class="text-center mb-12 animate-fade-in-down">
                <h1 class="text-4xl font-bold text-gray-800 mb-4">
                    Profile Dashboard
                </h1>
                <p class="text-xl text-gray-600">
                    Manage your personal information
                </p>
            </div>

            <div
                class="bg-white/60 backdrop-blur-lg rounded-2xl shadow-lg overflow-hidden transform hover:scale-[1.01] transition-all duration-300">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div
                        class="relative p-8 flex flex-col items-center justify-center bg-gradient-to-br from-sky-200 to-pink-200">
                        <div class="relative group">
                            <div
                                class="absolute -inset-0.5 bg-gradient-to-r from-sky-300 to-pink-300 rounded-full opacity-75 group-hover:opacity-100 blur transition duration-500">
                            </div>
                            <div
                                class="relative w-48 h-48 rounded-full overflow-hidden border-4 border-white shadow-xl">
                                <img :src="previewImage || getProfilePhotoUrl()" :alt="user.first_name"
                                    class="w-full h-full object-cover transform transition duration-500 group-hover:scale-105" />

                                <div v-if="isEditing"
                                    class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                    <label for="photo-upload"
                                        class="cursor-pointer p-2 rounded-full bg-white/20 backdrop-blur-sm hover:bg-white/40 transition-all duration-300">
                                        <font-awesome-icon icon="fa-solid fa-camera" class="text-white text-2xl" />
                                    </label>
                                </div>
                            </div>
                        </div>

                        <input type="file" id="photo-upload" ref="fileInput" @change="handleFileUpload" accept="image/*"
                            class="hidden" />

                        <button v-if="isEditing" @click="triggerFileUpload"
                            class="mt-6 px-6 py-3 bg-white text-sky-600 rounded-xl shadow-lg hover:bg-sky-50 transform hover:scale-105 transition duration-300 font-semibold flex items-center gap-2">
                            <font-awesome-icon icon="fa-solid fa-camera" />
                            Update Photo
                        </button>


                        <div class="mt-6 text-center">
                            <h2 class="text-2xl font-bold text-gray-800">
                                {{ user.first_name }} {{ user.last_name }}
                            </h2>
                            <p class="text-gray-600">@{{ user.username }}</p>
                            <div class="mt-4 flex items-center justify-center">
                                <span class="inline-flex h-3 w-3 rounded-full bg-green-400"></span>
                                <span class="ml-2 text-sm text-gray-600">Online</span>
                            </div>
                            
                          <!-- Mobile Logout Button (only visible on small screens) -->
<button @click="logout" 
    class="flex md:hidden mt-4 px-5 py-3 bg-red-500 text-white rounded-full shadow-md hover:bg-red-600 hover:shadow-lg active:scale-95 transition-all duration-300 font-semibold items-center justify-center gap-2">
    <font-awesome-icon icon="fa-solid fa-sign-out-alt" />
    Logout
</button>

                        </div>
                    </div>

                    <div class="lg:col-span-2 p-8">
                        <div class="space-y-8">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <TransitionGroup enter-active-class="transition duration-500 ease-out"
                                    enter-from-class="transform -translate-y-4 opacity-0"
                                    enter-to-class="transform translate-y-0 opacity-100">
                                    <template v-for="(field, key) in userFields" :key="key">
                                        <div class="bg-white/70 backdrop-blur rounded-xl p-4 hover:bg-white/90 transition-all duration-300 shadow-sm"
                                            :class="{ 'border-2 border-sky-200': isEditing }">
                                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                                {{ field.label }}
                                            </label>

                                            <select v-if="isEditing && key === 'gender'" v-model="user[key]"
                                                class="w-full px-4 py-2 bg-white rounded-lg border-2 border-sky-100 focus:border-sky-400 focus:ring-2 focus:ring-sky-400 transition-all duration-300">
                                                <option v-for="option in field.options" :key="option" :value="option">
                                                    {{ option }}
                                                </option>
                                            </select>

                                            <input v-else-if="isEditing" v-model="user[key]" :type="field.type"
                                                class="w-full px-4 py-2 bg-white rounded-lg border-2 border-sky-100 focus:border-sky-400 focus:ring-2 focus:ring-sky-400 transition-all duration-300"
                                                :placeholder="`Enter your ${field.label.toLowerCase()}`" />

                                            <!-- Display value when not editing -->
                                            <p v-else class="text-gray-800 text-lg font-medium">
                                                {{ user[key] || `No ${field.label.toLowerCase()} provided` }}
                                            </p>
                                        </div>
                                    </template>
                                </TransitionGroup>
                            </div>
                        </div>

                        <div class="mt-8 flex justify-end space-x-4">
                            <button v-if="isEditing" @click="cancelEdit"
                                class="px-8 py-3 bg-gray-200 text-gray-700 rounded-xl shadow hover:shadow-md transform hover:scale-105 transition-all duration-300 font-semibold">
                                <span class="flex items-center gap-2">
                                    <font-awesome-icon icon="fa-solid fa-times" />
                                    Cancel
                                </span>
                            </button>
                            <button @click="toggleEdit" :class="{
                                'bg-gradient-to-r from-sky-400 to-blue-500': !isEditing,
                                'bg-gradient-to-r from-emerald-400 to-teal-500': isEditing,
                            }"
                                class="px-8 py-3 text-white rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 font-semibold">
                                <span class="flex items-center gap-2">
                                    <font-awesome-icon :icon="isEditing ? 'fa-solid fa-check' : 'fa-solid fa-pen'" />
                                    {{ isEditing ? "Save Changes" : "Edit Profile" }}
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="showNotification"
                class="fixed top-12 left-0 right-0 md:left-auto md:right-12 md:top-24 mx-auto md:mx-0 max-w-sm bg-white/90 backdrop-blur-md px-6 py-4 rounded-xl shadow-lg transform transition-all duration-500 flex items-center gap-3 z-50"
                :class="{ 'translate-y-0 opacity-100': showNotification, 'translate-y-12 opacity-0': !showNotification }">
                <div class="flex-shrink-0 w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
                    <font-awesome-icon icon="fa-solid fa-check" class="text-emerald-500" />
                </div>
                <div>
                    <p class="text-gray-800 font-medium">Profile Updated!</p>
                    <p class="text-gray-600 text-sm">Your changes have been saved successfully.</p>
                </div>
                <button @click="showNotification = false" class="ml-2 text-gray-400 hover:text-gray-600">
                    <font-awesome-icon icon="fa-solid fa-times" />
                </button>
            </div>

            <div v-if="errorMessages.length > 0"
                class="fixed top-12 left-0 right-0 md:left-auto md:right-12 md:top-24 mx-auto mx-auto md:mx-0 max-w-sm bg-red-100/90 backdrop-blur-md px-6 py-4 rounded-xl shadow-lg z-50">
                <div class="space-y-2">
                    <div v-for="(error, index) in errorMessages" :key="index" class="flex items-center gap-3">
                        <div class="flex-shrink-0 w-10 h-10 bg-red-200 rounded-full flex items-center justify-center">
                            <font-awesome-icon icon="fa-solid fa-cancel" class="text-red-500" />
                        </div>
                        <p class="text-red-800 font-medium">{{ error }}</p>
                    </div>
                </div>
            </div>

            <div class="fixed top-0 right-0 -z-10 w-96 h-96 bg-pink-100 rounded-full blur-3xl opacity-50"></div>
            <div class="fixed bottom-0 left-0 -z-10 w-96 h-96 bg-sky-100 rounded-full blur-3xl opacity-50"></div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
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
const errorMessages = ref([]);

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

    const image = profilePhoto.split("/");
    const image_name = image[image.length - 1];
    return `/mediafiles/${image_name}`;
};

const userFields = {
    username: { label: "Username", type: "text" },
    email: { label: "Email Address", type: "email" },
    first_name: { label: "First Name", type: "text" },
    last_name: { label: "Last Name", type: "text" },
    gender: { label: "Gender", type: "select", options: ["Male", "Female", "Other"] },
    phone_number: { label: "Phone", type: "number" },
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
            errorMessages.value = [];
            await authStore.updateProfile(formData, user.value.id);

            showNotification.value = true;
            setTimeout(() => {
                showNotification.value = false;
            }, 4000);

            isEditing.value = false;
        } catch (error) {
            errorMessages.value.push("An unexpected error occurred. Please try again.");
            setTimeout(() => {
                errorMessages.value = [];
            }, 4000);
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
        errorMessages.value.push("Logout failed. Please try again.");
        setTimeout(() => {
            errorMessages.value = [];
        }, 4000);
    }
};

onMounted(async () => {
    await authStore.initialize();
    if (!authStore.isAuthenticated) {
        router.push("/sign-in");
    } else {
        user.value = {
            ...user.value,
            ...authStore.user
        };
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