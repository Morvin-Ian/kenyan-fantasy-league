<template>
    <div class="p-4">
      <div class="max-w-7xl mx-auto flex flex-col lg:flex-row gap-6">
        <!-- Left side: Available Players -->
        <div class="w-full lg:w-2/3 bg-white rounded-xl shadow-lg p-4">
          <div class="mb-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">Transfer Market</h2>
            
            <!-- Search and Filter -->
            <div class="flex flex-col md:flex-row gap-3 mb-4">
              <div class="relative flex-grow">
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search players..." 
                  class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <div class="absolute inset-y-0 left-0 flex items-center pl-3">
                  <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>
              
              <div class="flex gap-2">
                <select 
                  v-model="positionFilter" 
                  class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Positions</option>
                  <option value="GK">Goalkeepers</option>
                  <option value="DEF">Defenders</option>
                  <option value="MID">Midfielders</option>
                  <option value="FWD">Forwards</option>
                </select>
                
                <select 
                  v-model="sortBy" 
                  class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="price_asc">Price: Low to High</option>
                  <option value="price_desc">Price: High to Low</option>
                  <option value="points_desc">Points: High to Low</option>
                  <option value="name_asc">Name: A to Z</option>
                </select>
              </div>
            </div>
            
            <!-- Team budget info -->
            <div class="flex items-center justify-between bg-blue-50 p-3 rounded-lg mb-4">
              <div class="flex items-center gap-2">
                <span class="font-semibold text-blue-800">Team Budget:</span>
                <span class="text-xl font-bold text-blue-900">${{ remainingBudget.toFixed(1) }}m</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="font-semibold text-blue-800">Players:</span>
                <span class="font-bold text-blue-900">{{ currentTeamCount }}/{{ maxTeamSize }}</span>
              </div>
            </div>
          </div>
          
          <!-- Players List -->
          <div class="bg-gray-50 rounded-lg overflow-hidden">
            <div class="overflow-x-auto">
              <table class="min-w-full">
                <thead>
                  <tr class="bg-gray-100 text-gray-600 uppercase text-sm leading-normal">
                    <th class="py-3 px-4 text-left">Player</th>
                    <th class="py-3 px-4 text-left">Team</th>
                    <th class="py-3 px-4 text-center">Points</th>
                    <th class="py-3 px-4 text-center">Price</th>
                    <th class="py-3 px-4 text-center">Action</th>
                  </tr>
                </thead>
                <tbody class="text-gray-700">
                  <tr 
                    v-for="player in filteredPlayers" 
                    :key="player.id"
                    class="border-b border-gray-200 hover:bg-gray-100 transition-colors"
                  >
                    <td class="py-3 px-4">
                      <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full overflow-hidden bg-gray-200">
                          <img 
                            :src="player.image || '/placeholder-player.png'" 
                            :alt="player.name"
                            class="w-full h-full object-cover"
                          />
                        </div>
                        <div>
                          <p class="font-medium">{{ player.name }}</p>
                          <p class="text-xs text-gray-500">{{ player.position }}</p>
                        </div>
                      </div>
                    </td>
                    <td class="py-3 px-4">
                      <div class="flex items-center">
                        <div class="w-6 h-6 mr-2">
                          <img 
                            :src="player.teamLogo || '/placeholder-team.png'" 
                            :alt="player.team"
                            class="w-full h-full object-contain"
                          />
                        </div>
                        {{ player.team }}
                      </div>
                    </td>
                    <td class="py-3 px-4 text-center">{{ player.points }}</td>
                    <td class="py-3 px-4 text-center font-medium">${{ player.price.toFixed(1) }}m</td>
                    <td class="py-3 px-4 text-center">
                      <button 
                        v-if="isPlayerInTeam(player)"
                        @click="sellPlayer(player)"
                        class="bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded-full text-sm transition-colors"
                        :disabled="isTransferring"
                      >
                        Sell
                      </button>
                      <button 
                        v-else
                        @click="buyPlayer(player)"
                        class="bg-green-500 hover:bg-green-600 text-white py-1 px-3 rounded-full text-sm transition-colors"
                        :disabled="!canBuyPlayer(player) || isTransferring"
                      >
                        Buy
                      </button>
                    </td>
                  </tr>
                  
                  <tr v-if="filteredPlayers.length === 0">
                    <td colspan="5" class="py-8 text-center text-gray-500">
                      No players found matching your criteria
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <!-- Right side: Current Team -->
        <div class="w-full lg:w-1/3">
          <div class="bg-white rounded-xl shadow-lg p-4 mb-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Your Team</h2>
            
            <!-- Team Summary -->
            <div class="grid grid-cols-2 gap-3 mb-4">
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <p class="text-sm text-gray-500">Total Value</p>
                <p class="text-xl font-bold text-gray-800">${{ teamValue.toFixed(1) }}m</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <p class="text-sm text-gray-500">Team Points</p>
                <p class="text-xl font-bold text-gray-800">{{ teamPoints }}</p>
              </div>
            </div>
            
            <!-- Position Counts -->
            <div class="flex justify-between mb-4 text-sm">
              <div class="flex flex-col items-center">
                <span class="font-semibold text-red-600">GK</span>
                <span>{{ positionCounts.GK }}/{{ positionLimits.GK }}</span>
              </div>
              <div class="flex flex-col items-center">
                <span class="font-semibold text-blue-600">DEF</span>
                <span>{{ positionCounts.DEF }}/{{ positionLimits.DEF }}</span>
              </div>
              <div class="flex flex-col items-center">
                <span class="font-semibold text-green-600">MID</span>
                <span>{{ positionCounts.MID }}/{{ positionLimits.MID }}</span>
              </div>
              <div class="flex flex-col items-center">
                <span class="font-semibold text-orange-600">FWD</span>
                <span>{{ positionCounts.FWD }}/{{ positionLimits.FWD }}</span>
              </div>
            </div>
          </div>
          
          <!-- Team List -->
          <div class="bg-white rounded-xl shadow-lg p-4">
            <h3 class="font-semibold text-gray-700 mb-3">Current Squad</h3>
            
            <div v-if="myTeam.length === 0" class="text-center py-6 text-gray-500">
              Your team is empty. Start buying players!
            </div>
            
            <div v-else class="space-y-3">
              <!-- Goalkeepers -->
              <div>
                <h4 class="text-xs font-medium text-gray-500 uppercase mb-2">Goalkeepers</h4>
                <div class="space-y-2">
                  <div 
                    v-for="player in getPlayersByPosition('GK')" 
                    :key="player.id"
                    class="flex items-center justify-between bg-gray-50 p-2 rounded-lg"
                  >
                    <div class="flex items-center gap-2">
                      <div class="w-8 h-8 rounded-full overflow-hidden bg-gray-200">
                        <img 
                          :src="player.image || '/placeholder-player.png'" 
                          :alt="player.name"
                          class="w-full h-full object-cover"
                        />
                      </div>
                      <span class="font-medium text-sm">{{ player.name }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-medium">${{ player.price.toFixed(1) }}m</span>
                      <button 
                        @click="sellPlayer(player)"
                        class="text-red-500 hover:text-red-700"
                        :disabled="isTransferring"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Defenders -->
              <div>
                <h4 class="text-xs font-medium text-gray-500 uppercase mb-2">Defenders</h4>
                <div class="space-y-2">
                  <div 
                    v-for="player in getPlayersByPosition('DEF')" 
                    :key="player.id"
                    class="flex items-center justify-between bg-gray-50 p-2 rounded-lg"
                  >
                    <div class="flex items-center gap-2">
                      <div class="w-8 h-8 rounded-full overflow-hidden bg-gray-200">
                        <img 
                          :src="player.image || '/placeholder-player.png'" 
                          :alt="player.name"
                          class="w-full h-full object-cover"
                        />
                      </div>
                      <span class="font-medium text-sm">{{ player.name }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-medium">${{ player.price.toFixed(1) }}m</span>
                      <button 
                        @click="sellPlayer(player)"
                        class="text-red-500 hover:text-red-700"
                        :disabled="isTransferring"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Midfielders -->
              <div>
                <h4 class="text-xs font-medium text-gray-500 uppercase mb-2">Midfielders</h4>
                <div class="space-y-2">
                  <div 
                    v-for="player in getPlayersByPosition('MID')" 
                    :key="player.id"
                    class="flex items-center justify-between bg-gray-50 p-2 rounded-lg"
                  >
                    <div class="flex items-center gap-2">
                      <div class="w-8 h-8 rounded-full overflow-hidden bg-gray-200">
                        <img 
                          :src="player.image || '/placeholder-player.png'" 
                          :alt="player.name"
                          class="w-full h-full object-cover"
                        />
                      </div>
                      <span class="font-medium text-sm">{{ player.name }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-medium">${{ player.price.toFixed(1) }}m</span>
                      <button 
                        @click="sellPlayer(player)"
                        class="text-red-500 hover:text-red-700"
                        :disabled="isTransferring"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Forwards -->
              <div>
                <h4 class="text-xs font-medium text-gray-500 uppercase mb-2">Forwards</h4>
                <div class="space-y-2">
                  <div 
                    v-for="player in getPlayersByPosition('FWD')" 
                    :key="player.id"
                    class="flex items-center justify-between bg-gray-50 p-2 rounded-lg"
                  >
                    <div class="flex items-center gap-2">
                      <div class="w-8 h-8 rounded-full overflow-hidden bg-gray-200">
                        <img 
                          :src="player.image || '/placeholder-player.png'" 
                          :alt="player.name"
                          class="w-full h-full object-cover"
                        />
                      </div>
                      <span class="font-medium text-sm">{{ player.name }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-medium">${{ player.price.toFixed(1) }}m</span>
                      <button 
                        @click="sellPlayer(player)"
                        class="text-red-500 hover:text-red-700"
                        :disabled="isTransferring"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Confirm Team Button -->
            <div class="mt-6">
              <button 
                @click="confirmTeam"
                class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                :disabled="myTeam.length < maxTeamSize || isTransferring"
              >
                Confirm Team
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Success/Error Notification Toast -->
      <div 
        v-if="notification.show" 
        class="fixed bottom-4 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-lg shadow-lg z-50 flex items-center gap-2"
        :class="notification.type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'"
      >
        <svg v-if="notification.type === 'success'" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ notification.message }}</span>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, computed, onMounted, watch } from 'vue';
  import { useAuthStore } from '@/stores/auth';
  import { useRouter } from 'vue-router';
  import type { FantasyPlayer as Player } from "@/helpers/types/team";
  
  // Mock data for available players - in a real app, this would come from an API
  import { availablePlayers } from '@/helpers/data';
  
  const authStore = useAuthStore();
  const router = useRouter();
  
  // State
  const searchQuery = ref('');
  const positionFilter = ref('');
  const sortBy = ref('price_asc');
  const myTeam = ref<Player[]>([]);
  const totalBudget = ref(100.0); // Start with 100 million budget
  const isTransferring = ref(false);
  const notification = ref({
    show: false,
    type: 'success',
    message: ''
  });
  
  // Team constraints
  const maxTeamSize = 15; // Total players allowed
  const positionLimits = {
    GK: 2,  // Must have exactly 2 goalkeepers
    DEF: 5, // Must have exactly 5 defenders
    MID: 5, // Must have exactly 5 midfielders
    FWD: 3  // Must have exactly 3 forwards
  };
  
  // Computed values
  const availablePlayersRef = ref(availablePlayers);
  
  const filteredPlayers = computed(() => {
    let players = [...availablePlayersRef.value];
    
    // Apply search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      players = players.filter(player => 
        player.name.toLowerCase().includes(query) || 
        player.team.toLowerCase().includes(query)
      );
    }
    
    // Apply position filter
    if (positionFilter.value) {
      players = players.filter(player => player.position === positionFilter.value);
    }
    
    // Apply sorting
    switch (sortBy.value) {
      case 'price_asc':
        players.sort((a, b) => a.price - b.price);
        break;
      case 'price_desc':
        players.sort((a, b) => b.price - a.price);
        break;
      case 'points_desc':
        players.sort((a, b) => b.points - a.points);
        break;
      case 'name_asc':
        players.sort((a, b) => a.name.localeCompare(b.name));
        break;
    }
    
    return players;
  });
  
  const remainingBudget = computed(() => {
    return totalBudget.value - myTeam.value.reduce((sum, player) => sum + player.price, 0);
  });
  
  const teamValue = computed(() => {
    return myTeam.value.reduce((sum, player) => sum + player.price, 0);
  });
  
  const teamPoints = computed(() => {
    return myTeam.value.reduce((sum, player) => sum + player.points, 0);
  });
  
  const currentTeamCount = computed(() => myTeam.value.length);
  
  const positionCounts = computed(() => {
    const counts = { GK: 0, DEF: 0, MID: 0, FWD: 0 };
    
    myTeam.value.forEach(player => {
      counts[player.position as keyof typeof counts]++;
    });
    
    return counts;
  });
  
  // Methods
  const isPlayerInTeam = (player: Player) => {
    return myTeam.value.some(p => p.id === player.id);
  };
  
  const canBuyPlayer = (player: Player) => {
    // Check if we have budget
    if (player.price > remainingBudget.value) {
      return false;
    }
    
    // Check if we've reached total team size
    if (myTeam.value.length >= maxTeamSize) {
      return false;
    }
    
    // Check position limits
    const currentPositionCount = myTeam.value.filter(p => p.position === player.position).length;
    const maxForPosition = positionLimits[player.position as keyof typeof positionLimits];
    
    return currentPositionCount < maxForPosition;
  };
  
  const getPlayersByPosition = (position: string) => {
    return myTeam.value.filter(player => player.position === position);
  };
  
  const buyPlayer = (player: Player) => {
    if (!canBuyPlayer(player)) {
      showNotification('error', `Cannot add ${player.name} to your team`);
      return;
    }
    
    isTransferring.value = true;
    
    // Simulate API call
    setTimeout(() => {
      myTeam.value.push({...player});
      showNotification('success', `${player.name} added to your team`);
      isTransferring.value = false;
    }, 500);
  };
  
  const sellPlayer = (player: Player) => {
    isTransferring.value = true;
    
    // Simulate API call
    setTimeout(() => {
      const index = myTeam.value.findIndex(p => p.id === player.id);
      if (index !== -1) {
        myTeam.value.splice(index, 1);
        showNotification('success', `${player.name} removed from your team`);
      }
      isTransferring.value = false;
    }, 500);
  };
  
  const confirmTeam = () => {
    // Check if team is complete
    if (myTeam.value.length < maxTeamSize) {
      showNotification('error', `Your team must have exactly ${maxTeamSize} players`);
      return;
    }
    
    // Check position requirements
    for (const [position, limit] of Object.entries(positionLimits)) {
      const count = myTeam.value.filter(p => p.position === position).length;
      if (count !== limit) {
        showNotification('error', `You must have exactly ${limit} ${position} players`);
        return;
      }
    }
    
    isTransferring.value = true;
    
    // Simulate saving
    setTimeout(() => {
      showNotification('success', 'Team saved successfully!');
      isTransferring.value = false;
      
      // In a real app, you'd save to backend and redirect to team view
      // router.push('/team');
    }, 1000);
  };
  
  const showNotification = (type: 'success' | 'error', message: string) => {
    notification.value = {
      show: true,
      type,
      message
    };
    
    // Auto-hide notification after 3 seconds
    setTimeout(() => {
      notification.value.show = false;
    }, 3000);
  };
  
  // Initialize
  onMounted(() => {
    authStore.initialize();
    if (!authStore.isAuthenticated) {
      router.push("/sign-in");
    }
    
    // Load user team if available
    // In a real app, you'd fetch this from an API
    const savedTeam = localStorage.getItem('userTeam');
    if (savedTeam) {
      try {
        myTeam.value = JSON.parse(savedTeam);
      } catch (e) {
        console.error('Failed to load saved team', e);
      }
    }
  });
  
  // Save team to localStorage when it changes
  watch(myTeam, (newTeam) => {
    localStorage.setItem('userTeam', JSON.stringify(newTeam));
  }, { deep: true });
  </script>
  
  <style scoped>
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.5s;
  }
  
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
  </style>