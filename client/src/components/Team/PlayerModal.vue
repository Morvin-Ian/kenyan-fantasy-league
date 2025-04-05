<template>
    <div 
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 backdrop-blur-sm"
      @click.self="emitAction('close-modal')"
    >
      <div 
        class="bg-white rounded-xl shadow-2xl max-w-md w-full m-4 transform transition-all duration-300 ease-in-out scale-100 hover:scale-105"
      >
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-t-xl">
          <div class="flex justify-between items-center">
            <h3 class="text-xl font-extrabold text-gray-800 tracking-tight">
              Manage {{ selectedPlayer?.name || "Player" }}
            </h3>
            <button
              @click="emitAction('close-modal')"
              class="text-gray-500 hover:text-red-500 transition-colors duration-200 group"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-7 w-7 group-hover:rotate-90 transition-transform"
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
        </div>
        
        <div class="p-6 space-y-4">
          <button
            @click="emitAction('initiate-switch')"
            class="w-full bg-blue-500 text-white py-3 rounded-lg text-sm font-semibold 
                   hover:bg-blue-600 transition-all duration-300 ease-in-out 
                   transform hover:-translate-y-1 shadow-md hover:shadow-lg"
          >
            <div class="flex items-center justify-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
              </svg>
              <span>Switch Player</span>
            </div>
          </button>
          
          <button
            @click="emitAction('make-captain')"
            class="w-full bg-green-500 text-white py-3 rounded-lg text-sm font-semibold 
                   hover:bg-green-600 transition-all duration-300 ease-in-out 
                   transform hover:-translate-y-1 shadow-md hover:shadow-lg"
          >
            <div class="flex items-center justify-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7 20l4-4 4 4m2-12l-2-2-4 4M3 4l2 2 4-4" />
              </svg>
              <span>Make Captain</span>
            </div>
          </button>
          
          <button
            @click="emitAction('make-vice-captain')"
            class="w-full bg-yellow-500 text-white py-3 rounded-lg text-sm font-semibold 
                   hover:bg-yellow-600 transition-all duration-300 ease-in-out 
                   transform hover:-translate-y-1 shadow-md hover:shadow-lg"
          >
            <div class="flex items-center justify-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span>Make Vice-Captain</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import type { FantasyPlayer as Player } from "@/helpers/types/team";
  
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