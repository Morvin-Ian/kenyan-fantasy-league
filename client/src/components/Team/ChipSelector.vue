<template>
    <Teleport to="body">
        <Transition name="modal">
            <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
                <!-- Backdrop -->
                <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('close')"></div>

                <!-- Modal -->
                <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                    <!-- Header -->
                    <div
                        class="sticky top-0 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-4 rounded-t-2xl">
                        <div class="flex items-center justify-between">
                            <div>
                                <h2 class="text-2xl font-bold">Activate Power-Up Chip</h2>
                                <p class="text-purple-100 text-sm mt-1">Use special chips to boost your team's
                                    performance</p>
                            </div>
                            <button @click="$emit('close')" class="hover:bg-white/20 rounded-full p-2 transition">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- Chips Grid -->
                    <div class="p-6 space-y-4">
                        <!-- Triple Captain -->
                        <div :class="[
                            'relative border-2 rounded-xl p-6 transition-all duration-300 cursor-pointer',
                            getChipStatus('TC') === 'used' ? 'border-gray-300 bg-gray-50 opacity-60' : 'border-purple-300 hover:border-purple-500 hover:shadow-lg bg-gradient-to-br from-purple-50 to-pink-50'
                        ]" @click="selectChip('TC')">
                            <div class="flex items-start gap-4">
                                <div class="text-4xl">🏆</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2">
                                        <h3 class="text-xl font-bold text-gray-900">Triple Captain</h3>
                                        <span v-if="getChipStatus('TC') === 'used'"
                                            class="px-2 py-1 bg-gray-500 text-white text-xs font-semibold rounded-full">
                                            USED GW{{ getUsedGameweek('TC') }}
                                        </span>
                                    </div>
                                    <p class="text-gray-600 mt-2">Your captain gets <span
                                            class="font-bold text-purple-600">3x points</span> instead of 2x for one
                                        gameweek</p>
                                    <div class="mt-3 flex items-center gap-2 text-sm text-gray-500">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd"
                                                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                                                clip-rule="evenodd" />
                                        </svg>
                                        <span>Best used when your captain has a favorable fixture</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Bench Boost -->
                        <div :class="[
                            'relative border-2 rounded-xl p-6 transition-all duration-300 cursor-pointer',
                            getChipStatus('BB') === 'used' ? 'border-gray-300 bg-gray-50 opacity-60' : 'border-green-300 hover:border-green-500 hover:shadow-lg bg-gradient-to-br from-green-50 to-emerald-50'
                        ]" @click="selectChip('BB')">
                            <div class="flex items-start gap-4">
                                <div class="text-4xl">💪</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2">
                                        <h3 class="text-xl font-bold text-gray-900">Bench Boost</h3>
                                        <span v-if="getChipStatus('BB') === 'used'"
                                            class="px-2 py-1 bg-gray-500 text-white text-xs font-semibold rounded-full">
                                            USED GW{{ getUsedGameweek('BB') }}
                                        </span>
                                    </div>
                                    <p class="text-gray-600 mt-2">Points from all <span
                                            class="font-bold text-green-600">15 players</span> (including bench) count
                                        for one gameweek</p>
                                    <div class="mt-3 flex items-center gap-2 text-sm text-gray-500">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd"
                                                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                                                clip-rule="evenodd" />
                                        </svg>
                                        <span>Best used in a double gameweek or when bench has good fixtures</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Wildcard -->
                        <div :class="[
                            'relative border-2 rounded-xl p-6 transition-all duration-300 cursor-pointer',
                            getChipStatus('WC') === 'used' ? 'border-gray-300 bg-gray-50 opacity-60' : 'border-blue-300 hover:border-blue-500 hover:shadow-lg bg-gradient-to-br from-blue-50 to-cyan-50'
                        ]" @click="selectChip('WC')">
                            <div class="flex items-start gap-4">
                                <div class="text-4xl">🔄</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2">
                                        <h3 class="text-xl font-bold text-gray-900">Wildcard</h3>
                                        <span v-if="getChipStatus('WC') === 'used'"
                                            class="px-2 py-1 bg-gray-500 text-white text-xs font-semibold rounded-full">
                                            USED GW{{ getUsedGameweek('WC') }}
                                        </span>
                                    </div>
                                    <p class="text-gray-600 mt-2">Make <span class="font-bold text-blue-600">unlimited
                                            free transfers</span> for one gameweek without point deductions</p>
                                    <div class="mt-3 flex items-center gap-2 text-sm text-gray-500">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd"
                                                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                                                clip-rule="evenodd" />
                                        </svg>
                                        <span>Best used to overhaul your team mid-season</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Note -->
                    <div class="px-6 pb-6">
                        <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                            <div class="flex">
                                <svg class="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" fill="currentColor"
                                    viewBox="0 0 20 20">
                                    <path fill-rule="evenodd"
                                        d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                                        clip-rule="evenodd" />
                                </svg>
                                <div class="ml-3">
                                    <p class="text-sm text-yellow-700">
                                        <span class="font-semibold">Important:</span> Each chip can only be used once
                                        per season. Choose wisely!
                                    </p>
                                </div>
                            </div>
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

const getUsedGameweek = (chipType: 'TC' | 'BB' | 'WC'): number | null => {
    const chip = props.chips.find(c => c.chip_type === chipType);
    return chip?.used_in_gameweek_number || chip?.used_in_gameweek || null;
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
    transform: scale(0.9);
    opacity: 0;
}

@keyframes fade-in {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

.animate-fade-in {
    animation: fade-in 0.3s ease-out;
}
</style>
