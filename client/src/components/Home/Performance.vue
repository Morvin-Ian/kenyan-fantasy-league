<template>
  <div class="bg-gradient-to-br from-gray-50 to-blue-50 p-4 sm:p-6 md:p-8 rounded-2xl mx-2 sm:mx-4 shadow-lg">
    <div class="max-w-9xl mx-auto">
    <!-- Enhanced Header with Tagline -->
    <div class="mb-10 mt-6 ml-3 ">
      <h1 class=" font-bold text-gray-900 tracking-tight mb-4 text-xl sm:text-2xl font-bold ">Discover Kenya's <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Best Talent</span></h1>
      <p class="text-sm sm:text-base text-gray-500 mt-1 sm:mt-2">Explore the extraordinary plays and exceptional talents shaping the beautiful game worldwide</p>
    </div>

    <!-- Featured Section -->
    <div class="bg-white rounded-3xl shadow-xl p-8 border border-gray-100 mb-8 relative overflow-hidden">
      <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full -mr-32 -mt-32 opacity-70"></div>
      
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 relative">
        <h2 class="text-xl sm:text-2xl font-bold text-gray-700 bg-clip-text">
          <span class="mr-3 bg-gradient-to-br from-blue-500 to-indigo-600 text-white p-2 rounded-lg">⚽</span> Star Performers
        </h2>
        <div class="flex gap-2 mt-4 md:mt-0">
          <button class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-5 py-2 rounded-full hover:from-blue-700 hover:to-indigo-700 transition transform hover:scale-105 shadow-md font-medium text-sm flex items-center">
            <span>Explore All Players</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Player Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 group overflow-hidden relative">
          <div class="absolute top-0 right-0 bg-blue-500 text-white text-xs font-bold py-1 px-3 rounded-bl-lg">TOP SCORER</div>
          
          <div class="flex items-center space-x-4 mb-6 relative">
            <div class="w-20 h-20 rounded-full overflow-hidden border-4 border-indigo-100 group-hover:border-indigo-200 transition transform group-hover:scale-105 shadow-md">
              <img src="" alt="Erling Haaland" class="w-full h-full object-cover" />
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">Erling Haaland</h3>
              <div class="flex items-center mt-1">
                <img src="" alt="Manchester City logo" class="w-4 h-4 mr-2" />
                <p class="text-sm text-gray-500">Manchester City</p>
              </div>
              <div class="flex items-center mt-1">
                <span class="text-yellow-500 mr-1">★★★★★</span>
                <span class="text-xs text-gray-500">Elite</span>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-3 mb-5">
            <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100 group-hover:border-blue-100 transition-all duration-300">
              <p class="text-xs text-gray-500 mb-1 flex justify-center items-center">
                <span class="mr-1">🥅</span> Goals
              </p>
              <p class="font-bold text-blue-700 text-lg">28</p>
            </div>
            <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100 group-hover:border-blue-100 transition-all duration-300">
              <p class="text-xs text-gray-500 mb-1 flex justify-center items-center">
                <span class="mr-1">👟</span> Assists
              </p>
              <p class="font-bold text-blue-700 text-lg">5</p>
            </div>
            <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100 group-hover:border-blue-100 transition-all duration-300">
              <p class="text-xs text-gray-500 mb-1 flex justify-center items-center">
                <span class="mr-1">⭐</span> Rating
              </p>
              <p class="font-bold text-blue-700 text-lg">9.2</p>
            </div>
          </div>
        </div>
        
        <!-- Player 2 -->
        <div class="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 group overflow-hidden relative">
          <div class="absolute top-0 right-0 bg-indigo-500 text-white text-xs font-bold py-1 px-3 rounded-bl-lg">PLAYMAKER</div>
          
          <div class="flex items-center space-x-4 mb-6 relative">
            <div class="w-20 h-20 rounded-full overflow-hidden border-4 border-indigo-100 group-hover:border-indigo-200 transition transform group-hover:scale-105 shadow-md">
              <img src="" alt="Jude Bellingham" class="w-full h-full object-cover" />
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">Jude Bellingham</h3>
              <div class="flex items-center mt-1">
                <img src="" alt="Real Madrid logo" class="w-4 h-4 mr-2" />
                <p class="text-sm text-gray-500">Real Madrid</p>
              </div>
              <div class="flex items-center mt-1">
                <span class="text-yellow-500 mr-1">★★★★★</span>
                <span class="text-xs text-gray-500">Elite</span>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-3 mb-5">
            <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100 group-hover:border-blue-100 transition-all duration-300">
              <p class="text-xs text-gray-500 mb-1 flex justify-center items-center">
                <span class="mr-1">🥅</span> Goals
              </p>
              <p class="font-bold text-blue-700 text-lg">18</p>
            </div>
            <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100 group-hover:border-blue-100 transition-all duration-300">
              <p class="text-xs text-gray-500 mb-1 flex justify-center items-center">
                <span class="mr-1">👟</span> Assists
              </p>
              <p class="font-bold text-blue-700 text-lg">10</p>
            </div>
            <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100 group-hover:border-blue-100 transition-all duration-300">
              <p class="text-xs text-gray-500 mb-1 flex justify-center items-center">
                <span class="mr-1">⭐</span> Rating
              </p>
              <p class="font-bold text-blue-700 text-lg">9.3</p>
            </div>
          </div>
          
        </div>
        
        <!-- Player 3 -->
        <div class="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 group overflow-hidden relative">
          <div class="absolute top-0 right-0 bg-purple-500 text-white text-xs font-bold py-1 px-3 rounded-bl-lg">RISING STAR</div>
          
          <div class="flex items-center space-x-4 mb-6 relative">
            <div class="w-20 h-20 rounded-full overflow-hidden border-4 border-indigo-100 group-hover:border-indigo-200 transition transform group-hover:scale-105 shadow-md">
              <img src="" alt="Marcus Rashford" class="w-full h-full object-cover" />
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">Marcus Rashford</h3>
              <div class="flex items-center mt-1">
                <img src="" alt="Manchester United logo" class="w-4 h-4 mr-2" />
                <p class="text-sm text-gray-500">Manchester United</p>
              </div>
              <div class="flex items-center mt-1">
                <span class="text-yellow-500 mr-1">★★★★☆</span>
                <span class="text-xs text-gray-500">Pro</span>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-3 mb-5">
            <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100 group-hover:border-blue-100 transition-all duration-300">
              <p class="text-xs text-gray-500 mb-1 flex justify-center items-center">
                <span class="mr-1">🥅</span> Goals
              </p>
              <p class="font-bold text-blue-700 text-lg">14</p>
            </div>
            <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100 group-hover:border-blue-100 transition-all duration-300">
              <p class="text-xs text-gray-500 mb-1 flex justify-center items-center">
                <span class="mr-1">👟</span> Assists
              </p>
              <p class="font-bold text-blue-700 text-lg">7</p>
            </div>
            <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100 group-hover:border-blue-100 transition-all duration-300">
              <p class="text-xs text-gray-500 mb-1 flex justify-center items-center">
                <span class="mr-1">⭐</span> Rating
              </p>
              <p class="font-bold text-blue-700 text-lg">8.6</p>
            </div>
          </div>
          

        </div>
      </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-1 gap-6 mb-8">
      
      <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 col-span-2">
        <h3 class="text-xl font-bold text-gray-800 mb-4">Top Goal Scorers</h3>
        
        <div class="space-y-4">
          <div class="grid grid-cols-8 text-xs font-medium text-gray-500 mb-2">
            <div class="col-span-1">#</div>
            <div class="col-span-3">Player</div>
            <div class="col-span-2">Team</div>
            <div class="col-span-1 text-center">Apps</div>
            <div class="col-span-1 text-center">Goals</div>
          </div>
          
          <div class="grid grid-cols-8 items-center py-3 border-b border-gray-100">
            <div class="col-span-1 font-bold">1</div>
            <div class="col-span-3 flex items-center">
              <span>Erling Haaland</span>
            </div>
            <div class="col-span-2 flex items-center">
              <span class="text-sm">Man City</span>
            </div>
            <div class="col-span-1 text-center">26</div>
            <div class="col-span-1 text-center font-bold text-blue-600">28</div>
          </div>
          
          <div class="grid grid-cols-8 items-center py-3 border-b border-gray-100">
            <div class="col-span-1 font-bold">2</div>
            <div class="col-span-3 flex items-center">
              <span>Kylian Mbappé</span>
            </div>
            <div class="col-span-2 flex items-center">
              <span class="text-sm">Real Madrid</span>
            </div>
            <div class="col-span-1 text-center">25</div>
            <div class="col-span-1 text-center font-bold text-blue-600">24</div>
          </div>
          
          <div class="grid grid-cols-8 items-center py-3 border-b border-gray-100">
            <div class="col-span-1 font-bold">3</div>
            <div class="col-span-3 flex items-center">
              <span>Harry Kane</span>
            </div>
            <div class="col-span-2 flex items-center">
              <span class="text-sm">Bayern</span>
            </div>
            <div class="col-span-1 text-center">26</div>
            <div class="col-span-1 text-center font-bold text-blue-600">22</div>
          </div>
          
          <div class="grid grid-cols-8 items-center py-3 border-b border-gray-100">
            <div class="col-span-1 font-bold">4</div>
            <div class="col-span-3 flex items-center">
              <span>Mohamed Salah</span>
            </div>
            <div class="col-span-2 flex items-center">
              <span class="text-sm">Liverpool</span>
            </div>
            <div class="col-span-1 text-center">24</div>
            <div class="col-span-1 text-center font-bold text-blue-600">19</div>
          </div>
          
          <div class="grid grid-cols-8 items-center py-3">
            <div class="col-span-1 font-bold">5</div>
            <div class="col-span-3 flex items-center">
              <span>Jude Bellingham</span>
            </div>
            <div class="col-span-2 flex items-center">
              <span class="text-sm">Real Madrid</span>
            </div>
            <div class="col-span-1 text-center">25</div>
            <div class="col-span-1 text-center font-bold text-blue-600">18</div>
          </div>
        </div>        
      </div>
    </div>
    
    <!-- Newsletter Section -->
    <div class="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl shadow-xl p-8 text-white">
      <div class="max-w-lg mx-auto text-center">
        <h3 class="text-2xl font-bold mb-4">Never Miss a Match</h3>
        <p class="mb-6 text-blue-100">Subscribe to our newsletter for exclusive content, match previews, and player insights delivered straight to your inbox.</p>
        
        <div class="flex">
          <input type="email" placeholder="Your email address" class="flex-grow bg-white bg-opacity-20 border border-blue-400 rounded-l-lg px-4 py-3 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-white" />
          <button class="bg-white text-blue-700 px-6 py-3 rounded-r-lg font-medium hover:bg-blue-50 transition">Subscribe</button>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import player3 from "@/assets/images/player3.png";
import player2 from "@/assets/images/player2.png";
import player1 from "@/assets/images/player1.png";

const featuredPlayers = [
  {
    id: 1,
    name: "Marcus Rashford",
    team: "Manchester United",
    image: player3,
    stats: {
      goals: 12,
      assists: 5,
      rating: 8.4
    }
  },
  {
    id: 2,
    name: "Jude Bellingham",
    team: "Real Madrid",
    image: player2,
    stats: {
      goals: 15,
      assists: 8,
      rating: 9.1
    }
  },
  {
    id: 3,
    name: "Erling Haaland",
    team: "Manchester City",
    image: player1,
    stats: {
      goals: 18,
      assists: 3,
      rating: 8.9
    }
  }
];


</script>

<style scoped>
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>