<template>
  <div class="flex items-center justify-center  p-2 sm:p-4 md:p-4">
    <div class="w-full bg-white rounded-xl sm:rounded-2xl overflow-hidden shadow-xl border border-gray-100">
      <div class="relative overflow-hidden">
        <div class="absolute inset-0 bg-gray-500 opacity-5 pattern-dots"></div>
        
        <div class="relative p-4 sm:p-6 md:p-8 bg-white text-gray-800">
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center">
            <div class="flex items-center space-x-3 sm:space-x-4">
              <div class="bg-indigo-100 p-2 sm:p-3 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 sm:h-8 sm:w-8 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118l-2.8-2.034c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
              <div>
                <h1 class="text-xl sm:text-2xl font-bold mb-0 sm:mb-1 text-gray-800">Black Stone FC</h1>
                <p class="text-xs sm:text-sm text-gray-500">Fantasy Football Team</p>
              </div>
            </div>
            
            <div class="flex items-center space-x-4 sm:space-x-6 mt-4 md:mt-0 bg-gray-50 px-4 sm:px-6 py-2 sm:py-3 rounded-lg sm:rounded-xl border border-gray-100 w-full md:w-auto">
              <div class="text-center flex-1 md:flex-auto">
                <div class="text-lg sm:text-2xl font-bold text-gray-800">980</div>
                <div class="text-xs text-gray-500">Total Points</div>
              </div>
              <div class="h-10 w-px bg-gray-200 hidden sm:block"></div>
              <div class="text-center flex-1 md:flex-auto">
                <div class="text-lg sm:text-2xl font-bold text-gray-800">200</div>
                <div class="text-xs text-gray-500">Rank <span class="text-gray-400 hidden sm:inline">(out of 2956)</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Captain and Team Management -->
      <div class="p-4 sm:p-6 md:p-8 bg-gray-50 border-b border-gray-100">
        <div class="flex flex-col md:flex-row justify-between items-center mb-4 sm:mb-6">
          <div class="flex items-center space-x-2 sm:space-x-4 mb-4 md:mb-0 w-full md:w-auto">
            <div class="flex items-center px-3 sm:px-4 py-2 rounded-lg text-sm sm:text-md">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 text-yellow-500 mr-1 sm:mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <span class="text-sm sm:text-md">Captain: Engineer Olunga</span>
              <button class="ml-2 sm:ml-3 text-indigo-600 hover:text-indigo-800 transition">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
              </button>
            </div>
          </div>
          
          <button class="bg-indigo-600 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg hover:bg-indigo-700 transition shadow-md flex items-center text-sm sm:text-base w-full md:w-auto justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 mr-1 sm:mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path d="M8 5a1 1 0 100 2h5.586l-1.293 1.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L13.586 5H8z" />
              <path d="M12 15a1 1 0 100-2H6.414l1.293-1.293a1 1 0 10-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L6.414 15H12z" />
            </svg>
            Make Transfer
          </button>
        </div>

        <!-- Team Formation Visual Indicator -->
        <div class="flex justify-center mb-4 sm:mb-6">
          <div class="inline-flex items-center bg-white px-3 sm:px-4 py-1 sm:py-2 rounded-full text-xs sm:text-sm text-gray-600 border border-gray-200 shadow-sm">
            <span class="font-medium">Formation:</span>
            <span class="ml-1 sm:ml-2 text-indigo-600 font-semibold">4-3-3</span>
          </div>
        </div>

        <!-- Players Grid -->
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 sm:gap-4">
          <div v-for="player in players" :key="player.name" class="relative group">
            <!-- Player Card -->
            <div class="bg-white rounded-lg sm:rounded-2xl shadow-md overflow-hidden border border-gray-100 transition-all duration-300 transform hover:scale-105 hover:shadow-lg">
              <!-- Captain Badge -->
              <div v-if="player.captain" class="absolute top-1 sm:top-2 right-1 sm:right-2 bg-yellow-400 text-gray-900 text-xs font-bold w-5 h-5 sm:w-6 sm:h-6 flex items-center justify-center rounded-full z-10 shadow-md">
                C
              </div>

              <div class="relative">
                <img :src="player.image" :alt="player.name" class="w-full h-24 sm:h-32 md:h-40 object-cover" />
                
                <!-- Overlay -->
                <div class="absolute inset-0 bg-gradient-to-t from-black to-transparent opacity-50"></div>
                
                <!-- Player Team -->
                <div class="absolute bottom-1 sm:bottom-2 left-1 sm:left-2 right-1 sm:right-2 text-white text-xs font-medium bg-black bg-opacity-30 rounded px-1 sm:px-2 py-0.5 sm:py-1 text-center sm:text-left">
                  {{ player.team }}
                </div>
              </div>
              
              <div class="p-2 sm:p-3 text-center">
                <h3 class="font-semibold text-gray-800 truncate text-xs sm:text-sm">
                  {{ player.name }}
                </h3>
                <p v-if="player.name !== '+'" class="text-xs mt-0.5 sm:mt-1 text-indigo-500 font-medium text-xs">
                  {{ player.position || 'Forward' }} · {{ player.points || '38' }} pts
                </p>
                <p v-else class="text-xs mt-0.5 sm:mt-1 text-gray-400 text-xs">
                  Add new player
                </p>
              </div>
              
              <!-- Quick Actions (visible on hover) -->
              <div v-if="player.name !== '+'" class="absolute inset-0 bg-indigo-900 bg-opacity-80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div class="flex space-x-1 sm:space-x-2">
                  <button class="bg-white text-indigo-600 p-1 sm:p-2 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 sm:h-4 sm:w-4" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </button>
                  <button class="bg-white text-red-600 p-1 sm:p-2 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 sm:h-4 sm:w-4" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <!-- Add Player Card Special Styling -->
              <div v-if="player.name === '+'" class="absolute inset-0 flex items-center justify-center">
                <div class="bg-indigo-100 rounded-full w-8 h-8 sm:w-12 sm:h-12 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-6 sm:w-6 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Footer with Action Buttons -->
      <div class="p-3 sm:p-6 flex flex-col sm:flex-row justify-between items-center border-t border-gray-100 gap-3 sm:gap-0">
        <button class="text-gray-600 flex items-center hover:text-indigo-600 transition text-xs sm:text-sm w-full sm:w-auto justify-center sm:justify-start">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd" />
          </svg>
          View Stats
        </button>
        
        <button class="bg-indigo-100 text-indigo-700 px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg hover:bg-indigo-200 transition flex items-center text-xs sm:text-sm w-full sm:w-auto justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2h2a1 1 0 100-2H9z" clip-rule="evenodd" />
          </svg>
          View Rules
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import olunga from "@/assets/images/olunga.png";
import player1 from "@/assets/images/player1.png";
import player2 from "@/assets/images/player2.png";
import player3 from "@/assets/images/player3.png";
import user from "@/assets/images/shadow.png";

const players = ref([
  {
    name: "E. Olunga",
    team: "Al DulHail",
    image: olunga,
    captain: true,
    position: "Forward",
    points: 58
  },
  {
    name: "V. Manyara",
    team: "Gor Mahia",
    image: player1,
    position: "Midfielder",
    points: 42
  },
  {
    name: "B. Peter",
    team: "Tusker FC",
    image: player2,
    position: "Defender",
    points: 35
  },
  {
    name: "E. Nderitu",
    team: "Tusker FC",
    image: player3,
    position: "Goalkeeper",
    points: 28
  },
  {
    name: "S. Kimanzi",
    team: "Tusker FC",
    image: player2,
    position: "Midfielder",
    points: 31
  },
  {
    name: "+",
    team: "Add player",
    image: user,
  },
]);
</script>

<style scoped>
.pattern-dots {
  background-image: radial-gradient(currentColor 1px, transparent 1px);
  background-size: 20px 20px;
}

.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Additional responsive styles */
@media (max-width: 640px) {
  .pattern-dots {
    background-size: 15px 15px;
  }
}
</style>