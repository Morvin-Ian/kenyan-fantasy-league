<template>
    <footer class="bg-gray-900 text-white py-16">
        <div class="max-w-7xl mx-auto px-6 lg:px-8">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-10">
                <!-- Brand Section -->
                <div>
                    <div class="flex items-center space-x-3 mb-4">
                        <img src="/logo.png" alt="Logo" class="h-16 w-auto" />
                        <h3 class="text-2xl font-bold">Fantasy KPL</h3>
                    </div>
                    <p class="text-gray-400 mb-6">
                        Experience the thrill of fantasy football for the Kenyan
                        Premier League.
                    </p>
                    <div class="flex space-x-4">
                        <a
                            href="#"
                            class="text-gray-400 hover:text-red-500 transition"
                        >
                            <i class="fab fa-twitter text-xl"></i>
                        </a>
                        <a
                            href="#"
                            class="text-gray-400 hover:text-red-500 transition"
                        >
                            <i class="fab fa-facebook text-xl"></i>
                        </a>
                        <a
                            href="#"
                            class="text-gray-400 hover:text-red-500 transition"
                        >
                            <i class="fab fa-instagram text-xl"></i>
                        </a>
                    </div>
                </div>

                <!-- Quick Links -->
                <div>
                    <h3 class="text-lg font-semibold mb-4 text-red-400">
                        Quick Links
                    </h3>
                    <ul class="space-y-3 text-gray-400">
                        <li>
                            <a href="#" class="hover:text-red-500 transition"
                                >How to Play</a
                            >
                        </li>
                        <li>
                            <a href="#" class="hover:text-red-500 transition"
                                >Rules</a
                            >
                        </li>
                        <li>
                            <a href="#" class="hover:text-red-500 transition"
                                >Prizes</a
                            >
                        </li>
                        <li>
                            <a href="#" class="hover:text-red-500 transition"
                                >Stats</a
                            >
                        </li>
                    </ul>
                </div>

                <!-- Support -->
                <div>
                    <h3 class="text-lg font-semibold mb-4 text-red-400">
                        Support
                    </h3>
                    <ul class="space-y-3 text-gray-400">
                        <li>
                            <a href="#" class="hover:text-red-500 transition"
                                >FAQs</a
                            >
                        </li>
                        <li>
                            <a href="#" class="hover:text-red-500 transition"
                                >Contact Us</a
                            >
                        </li>
                        <li>
                            <a href="#" class="hover:text-red-500 transition"
                                >Terms of Service</a
                            >
                        </li>
                        <li>
                            <a href="#" class="hover:text-red-500 transition"
                                >Privacy Policy</a
                            >
                        </li>
                    </ul>
                </div>

                <!-- Newsletter -->
                <div>
                    <h3 class="text-lg font-semibold mb-4 text-red-400">
                        Stay Updated
                    </h3>
                    <p class="text-gray-400 mb-4">
                        Subscribe for the latest fantasy football updates.
                    </p>
                    <div class="flex bg-gray-800 rounded-lg overflow-hidden">
                        <input
                            type="email"
                            placeholder="Your email"
                            class="w-full px-4 py-2 bg-transparent text-white outline-none"
                        />
                        <button
                            class="bg-red-500 px-4 py-2 text-white hover:bg-red-600 transition"
                        >
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Copyright -->
            <div class="border-t border-gray-700 mt-12 pt-6 text-center">
                <p class="text-gray-500">
                    &copy; {{ currentYear }} Fantasy Kenyan Premier League. All
                    rights reserved.
                </p>
                <div
                    class="mt-4 flex justify-center space-x-6 text-gray-400 text-sm"
                >
                    <a href="#" class="hover:text-white transition"
                        >Privacy Policy</a
                    >
                    <a href="#" class="hover:text-white transition"
                        >Terms of Service</a
                    >
                    <a href="#" class="hover:text-white transition"
                        >Cookies Settings</a
                    >
                </div>
            </div>
        </div>
    </footer>
</template>

<script setup>
import { ref } from "vue";

const currentYear = ref(new Date().getFullYear());
</script>

<style>
@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css");
</style>
