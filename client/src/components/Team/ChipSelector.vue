<template>
    <Teleport to="body">
        <Transition name="modal">
            <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
                <!-- Backdrop -->
                <div class="absolute inset-0 bg-black/40" @click="$emit('close')"></div>

                <!-- Modal -->
                <div class="relative bg-white rounded-lg shadow-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
                    <!-- Header -->
                    <div class="bg-gray-800 text-white px-6 py-5 rounded-t-lg">
                        <div class="flex items-center justify-between">
                            <div>
                                <h2 class="text-xl font-semibold">Power-Up Chips</h2>
                                <p class="text-gray-300 text-sm mt-1">Choose a chip to activate</p>
                            </div>
                            <button @click="$emit('close')" class="hover:bg-gray-700 rounded-full p-2 transition">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- Chips List -->
                    <div class="p-6 space-y-3">
                        <!-- Triple Captain -->
                        <button @click="selectChip('TC')" :disabled="getChipStatus('TC') === 'used'"
                            :class="[
                                'w-full text-left border rounded-lg p-4 transition-all duration-200',
                                getChipStatus('TC') === 'used' 
                                    ? 'bg-gray-100 border-gray-200 cursor-not-allowed opacity-60' 
                                    : 'bg-white border-gray-300 hover:border-gray-500 hover:shadow-md cursor-pointer'
                            ]">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="font-semibold text-gray-900">Triple Captain</h3>
                                    <p class="text-gray-600 text-sm mt-1">Captain gets 3x points instead of 2x</p>
                                </div>
                                <span v-if="getChipStatus('TC') === 'used'" class="text-xs font-medium text-gray-500 bg-gray-200 px-2 py-1 rounded">
                                    Used
                                </span>
                            </div>
                        </button>

                        <!-- Bench Boost -->
                        <button @click="selectChip('BB')" :disabled="getChipStatus('BB') === 'used'"
                            :class="[
                                'w-full text-left border rounded-lg p-4 transition-all duration-200',
                                getChipStatus('BB') === 'used' 
                                    ? 'bg-gray-100 border-gray-200 cursor-not-allowed opacity-60' 
                                    : 'bg-white border-gray-300 hover:border-gray-500 hover:shadow-md cursor-pointer'
                            ]">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="font-semibold text-gray-900">Bench Boost</h3>
                                    <p class="text-gray-600 text-sm mt-1">All 15 players count for one gameweek</p>
                                </div>
                                <span v-if="getChipStatus('BB') === 'used'" class="text-xs font-medium text-gray-500 bg-gray-200 px-2 py-1 rounded">
                                    Used
                                </span>
                            </div>
                        </button>

                        <!-- Wildcard -->
                        <button @click="selectChip('WC')" :disabled="getChipStatus('WC') === 'used'"
                            :class="[
                                'w-full text-left border rounded-lg p-4 transition-all duration-200',
                                getChipStatus('WC') === 'used' 
                                    ? 'bg-gray-100 border-gray-200 cursor-not-allowed opacity-60' 
                                    : 'bg-white border-gray-300 hover:border-gray-500 hover:shadow-md cursor-pointer'
                            ]">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="font-semibold text-gray-900">Wildcard</h3>
                                    <p class="text-gray-600 text-sm mt-1">Unlimited free transfers for one gameweek</p>
                                </div>
                                <span v-if="getChipStatus('WC') === 'used'" class="text-xs font-medium text-gray-500 bg-gray-200 px-2 py-1 rounded">
                                    Used
                                </span>
                            </div>
                        </button>
                    </div>

                    <!-- Info -->
                    <div class="px-6 pb-6">
                        <div class="bg-gray-50 border border-gray-200 p-4 rounded-lg">
                            <p class="text-sm text-gray-700">
                                <span class="font-semibold">Note:</span> Each chip can only be used once per season.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Chip {
    id: string;
    chip_type: 'TC' | 'BB' | 'WC';
    chip_type_display: string;
    is_used: boolean;
    used_in_gameweek: number | null;
    used_in_gameweek_number: number | null;
}

interface Props {
    show: boolean;
    chips: Chip[];
}

const props = defineProps<Props>();
const emit = defineEmits<{
    (e: 'close'): void;
    (e: 'select', chipType: 'TC' | 'BB' | 'WC'): void;
}>();

const getChipStatus = (chipType: 'TC' | 'BB' | 'WC'): 'available' | 'used' => {
    const chip = props.chips.find(c => c.chip_type === chipType);
    return chip && chip.is_used ? 'used' : 'available';
};

const selectChip = (chipType: 'TC' | 'BB' | 'WC') => {
    if (getChipStatus(chipType) === 'used') {
        return;
    }
    emit('select', chipType);
};
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
    transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}

.modal-enter-active .relative,
.modal-leave-active .relative {
    transition: all 0.3s ease;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
    transform: scale(0.95);
    opacity: 0;
}
</style>