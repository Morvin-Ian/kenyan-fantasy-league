<template>
    <div
        v-if="showModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
    >
        <div class="bg-white rounded-lg p-6 shadow-2xl max-w-md w-full m-4">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-bold text-gray-900">
                    Manage {{ selectedPlayer?.name || "Player" }}
                </h3>
                <button
                    @click="emitAction('close-modal')"
                    class="text-gray-500 hover:text-gray-800 transition-colors"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-6 w-6"
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
            <div class="space-y-4">
                <button
                    @click="emitAction('initiate-switch')"
                    class="w-full bg-blue-100 py-3 text-blue-800 hover:bg-blue-200 rounded-lg text-sm font-semibold transition-all duration-300"
                >
                    Switch
                </button>
                <button
                    @click="emitAction('make-captain')"
                    class="w-full bg-green-100 py-3 text-green-800 hover:bg-green-200 rounded-lg text-sm font-semibold transition-all duration-300"
                >
                    Make Captain
                </button>
                <button
                    @click="emitAction('make-vice-captain')"
                    class="w-full bg-yellow-100 py-3 text-yellow-800 hover:bg-yellow-200 rounded-lg text-sm font-semibold transition-all duration-300"
                >
                    Make Vice-Captain
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { Player } from "@/types/team";

const props = defineProps<{
    showModal: boolean;
    selectedPlayer: Player | null;
}>();

const emit = defineEmits<{
  (event: "close-modal"): void;
  (event: "initiate-switch"): void;
  (event: "make-captain"): void;
  (event: "make-vice-captain"): void;
}>();


const emitAction = (action: "close-modal" | "initiate-switch" | "make-captain" | "make-vice-captain") => {
  emit(action as any);
};

</script>
