<template>
  <div class="bg-gradient-to-br from-gray-50 to-blue-50 p-2 sm:p-4 md:p-6 lg:p-8 rounded-xl sm:rounded-2xl mx-1 sm:mx-2 md:mx-4 shadow-lg mb-3">
    <div class="mx-auto">
      <!-- Enhanced Header with Tagline -->
      <div class="animate-fade-in mb-6 sm:mb-8 md:mb-10 mt-3 sm:mt-4 md:mt-6 ml-2 sm:ml-3">
        <h1 class="text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-2 sm:mb-3 md:mb-4">
          Discover Kenya's <span class="text-transparent bg-clip-text bg-gradient-to-r from-gray-700 to-gray-900">Best Talent</span>
        </h1>
        <p class="text-xs sm:text-sm md:text-base text-gray-500 mt-1 sm:mt-1.5 md:mt-2">
          Explore the extraordinary plays and exceptional talents shaping Kenyan football
        </p>
      </div>

      <div class="animate-fade-in grid grid-cols-1 gap-4 sm:gap-6 mb-6 sm:mb-8">
        <div class="bg-white rounded-xl sm:rounded-2xl shadow-lg border border-gray-100 p-3 sm:p-4 md:p-6">
          <h3 class="text-base sm:text-lg md:text-xl font-bold text-gray-900 mb-3 sm:mb-4">Top Goal Scorers</h3>
          
          <div class="space-y-2 sm:space-y-3 md:space-y-4">
            <!-- Header Row -->
            <div class="grid grid-cols-8 text-xs sm:text-sm font-medium text-gray-600 mb-1 sm:mb-2 px-1">
              <div class="col-span-1">#</div>
              <div class="col-span-3">Player</div>
              <div class="col-span-2">Team</div>
              <div class="col-span-1 text-center">Apps</div>
              <div class="col-span-1 text-center">Goals</div>
            </div>
            
            <!-- Player Rows -->
            <div class="grid grid-cols-8 items-center py-2 sm:py-2.5 md:py-3 border-b border-gray-100 px-1">
              <div class="col-span-1 font-bold text-xs sm:text-sm md:text-base">1</div>
              <div class="col-span-3 flex items-center">
                <span class="text-xs sm:text-sm md:text-base font-medium truncate">Benson Omala</span>
              </div>
              <div class="col-span-2 flex items-center">
                <span class="text-xs sm:text-sm text-gray-600 truncate">Gor Mahia</span>
              </div>
              <div class="col-span-1 text-center text-xs sm:text-sm md:text-base">26</div>
              <div class="col-span-1 text-center font-bold text-gray-900 text-xs sm:text-sm md:text-base">18</div>
            </div>
            
            <div class="grid grid-cols-8 items-center py-2 sm:py-2.5 md:py-3 border-b border-gray-100 px-1">
              <div class="col-span-1 font-bold text-xs sm:text-sm md:text-base">2</div>
              <div class="col-span-3 flex items-center">
                <span class="text-xs sm:text-sm md:text-base font-medium truncate">Titus Achesa</span>
              </div>
              <div class="col-span-2 flex items-center">
                <span class="text-xs sm:text-sm text-gray-600 truncate">AFC Leopards</span>
              </div>
              <div class="col-span-1 text-center text-xs sm:text-sm md:text-base">25</div>
              <div class="col-span-1 text-center font-bold text-gray-900 text-xs sm:text-sm md:text-base">14</div>
            </div>
            
            <div class="grid grid-cols-8 items-center py-2 sm:py-2.5 md:py-3 border-b border-gray-100 px-1">
              <div class="col-span-1 font-bold text-xs sm:text-sm md:text-base">3</div>
              <div class="col-span-3 flex items-center">
                <span class="text-xs sm:text-sm md:text-base font-medium truncate">John Mark Makwatta</span>
              </div>
              <div class="col-span-2 flex items-center">
                <span class="text-xs sm:text-sm text-gray-600 truncate">Kariobangi Sharks</span>
              </div>
              <div class="col-span-1 text-center text-xs sm:text-sm md:text-base">26</div>
              <div class="col-span-1 text-center font-bold text-gray-900 text-xs sm:text-sm md:text-base">12</div>
            </div>
            
            <div class="grid grid-cols-8 items-center py-2 sm:py-2.5 md:py-3 border-b border-gray-100 px-1">
              <div class="col-span-1 font-bold text-xs sm:text-sm md:text-base">4</div>
              <div class="col-span-3 flex items-center">
                <span class="text-xs sm:text-sm md:text-base font-medium truncate">Elvis Rupia</span>
              </div>
              <div class="col-span-2 flex items-center">
                <span class="text-xs sm:text-sm text-gray-600 truncate">Kenya Police</span>
              </div>
              <div class="col-span-1 text-center text-xs sm:text-sm md:text-base">24</div>
              <div class="col-span-1 text-center font-bold text-gray-900 text-xs sm:text-sm md:text-base">11</div>
            </div>
            
            <div class="grid grid-cols-8 items-center py-2 sm:py-2.5 md:py-3 px-1">
              <div class="col-span-1 font-bold text-xs sm:text-sm md:text-base">5</div>
              <div class="col-span-3 flex items-center">
                <span class="text-xs sm:text-sm md:text-base font-medium truncate">Michael Olunga</span>
              </div>
              <div class="col-span-2 flex items-center">
                <span class="text-xs sm:text-sm text-gray-600 truncate">Tusker FC</span>
              </div>
              <div class="col-span-1 text-center text-xs sm:text-sm md:text-base">25</div>
              <div class="col-span-1 text-center font-bold text-gray-900 text-xs sm:text-sm md:text-base">10</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

</script>

<style scoped>
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}

@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.animate-slide-up {
  animation: slide-up 0.5s ease-out;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Additional responsive utilities for very small screens */
@media (max-width: 320px) {
  .truncate {
    max-width: 80px;
  }
}

@media (min-width: 321px) and (max-width: 640px) {
  .truncate {
    max-width: 120px;
  }
}
</style>