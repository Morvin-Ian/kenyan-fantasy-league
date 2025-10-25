<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="closeModal"></div>

      <!-- Modal panel -->
      <div class="inline-block w-full max-w-4xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900">
              Create Lineup
            </h3>
            <p class="mt-1 text-sm text-gray-500">
              Select starting 11 and bench players for {{ selectedTeamData?.name }}
            </p>
          </div>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Team Selection -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-3">Select Team</label>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <label class="flex items-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all" 
                   :class="selectedTeam === 'home' ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'">
              <input type="radio" v-model="selectedTeam" value="home" class="text-blue-600 focus:ring-blue-500">
              <img :src="fixture.home_team.logo_url" :alt="fixture.home_team.name" class="w-10 h-10 rounded-full">
              <div>
                <span class="font-medium text-gray-900">{{ fixture.home_team.name }}</span>
                <p class="text-sm text-gray-500">{{ homeTeamPlayers.length }} players available</p>
              </div>
            </label>
            <label class="flex items-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all"
                   :class="selectedTeam === 'away' ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'">
              <input type="radio" v-model="selectedTeam" value="away" class="text-blue-600 focus:ring-blue-500">
              <img :src="fixture.away_team.logo_url" :alt="fixture.away_team.name" class="w-10 h-10 rounded-full">
              <div>
                <span class="font-medium text-gray-900">{{ fixture.away_team.name }}</span>
                <p class="text-sm text-gray-500">{{ awayTeamPlayers.length }} players available</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Lineup Builder -->
        <div v-if="selectedTeam && availablePlayers.length > 0" class="mb-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Starting 11 -->
            <div class="space-y-4">
              <h4 class="font-medium text-gray-900">Starting 11</h4>
              
              <!-- Goalkeeper -->
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700">Goalkeeper</label>
                <select v-model="startingLineup.goalkeeper" class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="">Select Goalkeeper</option>
                  <option v-for="player in availablePlayers.filter(p => p.position === 'GKP')" 
                         :key="player.id" 
                         :value="player.id"
                         :disabled="isPlayerSelected(player.id)">
                    {{ player.name }} (#{{ player.jersey_number }})
                  </option>
                </select>
              </div>

              <!-- Defenders -->
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700">Defenders</label>
                <select v-model="startingLineup.defenders" multiple class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 h-32">
                  <option v-for="player in availablePlayers.filter(p => p.position === 'DEF')" 
                         :key="player.id" 
                         :value="player.id"
                         :disabled="isPlayerSelected(player.id) && !startingLineup.defenders.includes(player.id)">
                    {{ player.name }} (#{{ player.jersey_number }})
                  </option>
                </select>
              </div>

              <!-- Midfielders -->
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700">Midfielders</label>
                <select v-model="startingLineup.midfielders" multiple class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 h-32">
                  <option v-for="player in availablePlayers.filter(p => p.position === 'MID')" 
                         :key="player.id" 
                         :value="player.id"
                         :disabled="isPlayerSelected(player.id) && !startingLineup.midfielders.includes(player.id)">
                    {{ player.name }} (#{{ player.jersey_number }})
                  </option>
                </select>
              </div>

              <!-- Forwards -->
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-700">Forwards</label>
                <select v-model="startingLineup.forwards" multiple class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 h-32">
                  <option v-for="player in availablePlayers.filter(p => p.position === 'FWD')" 
                         :key="player.id" 
                         :value="player.id"
                         :disabled="isPlayerSelected(player.id) && !startingLineup.forwards.includes(player.id)">
                    {{ player.name }} (#{{ player.jersey_number }})
                  </option>
                </select>
              </div>
            </div>

            <!-- Bench Players -->
            <div class="space-y-4">
              <h4 class="font-medium text-gray-900">Bench Players</h4>
              <div class="space-y-2">
                <select v-model="benchPlayers" multiple class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 h-96">
                  <option v-for="player in availablePlayers" 
                         :key="player.id" 
                         :value="player.id"
                         :disabled="isPlayerSelected(player.id) && !benchPlayers.includes(player.id)">
                    {{ player.name }} (#{{ player.jersey_number }}) - {{ player.position }}
                  </option>
                </select>
              </div>

              <!-- Selected Players Summary -->
              <div class="mt-4 p-4 bg-gray-50 rounded-lg">
                <h5 class="font-medium text-gray-900 mb-2">Selected Players Summary</h5>
                <div class="space-y-1 text-sm">
                  <p>Starting 11: {{ totalStarters }}/11</p>
                  <p>Bench: {{ benchPlayers.length }} players</p>
                  <p>Total Selected: {{ totalSelectedPlayers }} players</p>
                  <p v-if="!isLineupValid" class="text-red-600 font-medium">
                    Please select exactly 11 starters
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading / Empty / Error -->
        <div v-else-if="selectedTeam && isLoadingPlayers" class="flex justify-center items-center py-8">
          <div class="text-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-2 text-sm text-gray-600">Loading players...</p>
          </div>
        </div>
        <div v-else-if="selectedTeam && availablePlayers.length === 0" class="text-center py-8">
          <svg class="w-12 h-12 text-gray-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <p class="mt-2 text-sm text-gray-600">No players available for this team</p>
        </div>

        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center space-x-2">
            <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-sm font-medium text-red-800">{{ error }}</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex space-x-3 pt-6 border-t border-gray-200">
          <button @click="closeModal" class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors">
            Cancel
          </button>
          <button 
            @click="submitLineup" 
            :disabled="!isLineupValid || isSubmitting"
            :class="{
              'opacity-50 cursor-not-allowed': !isLineupValid || isSubmitting,
              'hover:bg-blue-600 focus:ring-blue-500': isLineupValid && !isSubmitting
            }"
            class="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-500 border border-transparent rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors"
          >
            <span v-if="isSubmitting" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Submitting...
            </span>
            <span v-else>Submit Lineup</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useKplStore } from '@/stores/kpl'

interface Props {
  isOpen: boolean
  fixture: any
}

interface Emits {
  (e: 'close'): void
  (e: 'upload-success'): void
}

interface LineupData {
  goalkeeper: string
  defenders: string[]
  midfielders: string[]
  forwards: string[]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const kplStore = useKplStore()

const selectedTeam = ref<'home' | 'away' | null>(null)
const startingLineup = ref<LineupData>({
  goalkeeper: '',
  defenders: [],
  midfielders: [],
  forwards: []
})
const benchPlayers = ref<string[]>([])
const isSubmitting = ref(false)
const error = ref('')
const isLoadingPlayers = ref(false)

const selectedTeamData = computed(() => {
  if (!selectedTeam.value) return null
  return selectedTeam.value === 'home' ? props.fixture.home_team : props.fixture.away_team
})

const homeTeamPlayers = computed(() => kplStore.players.filter(p => p.team.id === props.fixture.home_team.id))
const awayTeamPlayers = computed(() => kplStore.players.filter(p => p.team.id === props.fixture.away_team.id))
const availablePlayers = computed(() => selectedTeam.value === 'home' ? homeTeamPlayers.value : awayTeamPlayers.value)

const totalStarters = computed(() => {
  const gk = startingLineup.value.goalkeeper ? 1 : 0
  return gk + startingLineup.value.defenders.length + startingLineup.value.midfielders.length + startingLineup.value.forwards.length
})
const totalSelectedPlayers = computed(() => totalStarters.value + benchPlayers.value.length)
const isLineupValid = computed(() => totalStarters.value === 11)

const isPlayerSelected = (id: string) => {
  return startingLineup.value.goalkeeper === id ||
         startingLineup.value.defenders.includes(id) ||
         startingLineup.value.midfielders.includes(id) ||
         startingLineup.value.forwards.includes(id) ||
         benchPlayers.value.includes(id)
}

const closeModal = () => {
  resetModal()
  emit('close')
}

const resetModal = () => {
  selectedTeam.value = null
  startingLineup.value = { goalkeeper: '', defenders: [], midfielders: [], forwards: [] }
  benchPlayers.value = []
  isSubmitting.value = false
  error.value = ''
  isLoadingPlayers.value = false
}

const submitLineup = async () => {
  if (!isLineupValid.value || !selectedTeam.value) return
  isSubmitting.value = true
  error.value = ''

  try {
    const teamId = selectedTeam.value === 'home' ? props.fixture.home_team.id : props.fixture.away_team.id

    const lineupData = {
      fixture_id: props.fixture.id,
      team_id: teamId,
      side: selectedTeam.value,
      formation: '4-4-2', 
      starting_xi: [
        startingLineup.value.goalkeeper,
        ...startingLineup.value.defenders,
        ...startingLineup.value.midfielders,
        ...startingLineup.value.forwards
      ],
      bench_players: benchPlayers.value
    }

    await kplStore.submitLineup(lineupData)
    emit('upload-success')
    closeModal()
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to submit lineup.'
    console.error('Lineup submission error:', err)
  } finally {
    isSubmitting.value = false
  }
}

watch(selectedTeam, async (newTeam) => {
  if (newTeam && kplStore.players.length === 0) {
    isLoadingPlayers.value = true
    try {
      await kplStore.fetchPlayers()
    } catch (err) {
      error.value = 'Failed to load players'
    } finally {
      isLoadingPlayers.value = false
    }
  }
})

watch(() => props.isOpen, (val) => {
  if (val) resetModal()
})
</script>