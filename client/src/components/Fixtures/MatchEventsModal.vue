<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold">Match Events - {{ fixture?.home_team?.name }} vs {{ fixture?.away_team?.name }}
        </h2>
        <button @click="close" class="text-gray-500 hover:text-gray-700">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Error Alert -->
      <div v-if="store.error" class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
        {{ store.error }}
        <button @click="store.clearError()" class="float-right font-bold">×</button>
      </div>

      <div class="space-y-6">
        <!-- Goals -->
        <div class="border rounded-lg p-4">
          <h3 class="font-semibold mb-3">Goals</h3>
          <div class="space-y-2">
            <div v-for="(goal, index) in goals" :key="index" class="border rounded p-3 space-y-2">
              <div class="flex items-center space-x-2">
                <input v-model="goal.player_name" placeholder="Player name" class="flex-1 border rounded px-3 py-2" />
                <select v-model="goal.team_id" class="border rounded px-3 py-2">
                  <option value="">Select Team</option>
                  <option :value="fixture?.home_team?.id">{{ fixture?.home_team?.name }}</option>
                  <option :value="fixture?.away_team?.id">{{ fixture?.away_team?.name }}</option>
                </select>
                <input v-model.number="goal.count" type="number" placeholder="Count"
                  class="w-20 border rounded px-3 py-2" />
              </div>
              <div class="flex items-center space-x-2">
                <label class="flex items-center space-x-2 cursor-pointer">
                  <input v-model="goal.is_own_goal" type="checkbox"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                  <span class="text-sm text-gray-700">Own Goal (-2 points)</span>
                </label>
                <button @click="removeGoal(index)" class="ml-auto text-red-500 hover:text-red-700">
                  Remove
                </button>
              </div>
            </div>
            <button @click="addGoal" class="text-blue-500 hover:text-blue-700">+ Add Goal</button>
          </div>
        </div>

        <!-- Assists -->
        <div class="border rounded-lg p-4">
          <h3 class="font-semibold mb-3">Assists</h3>
          <div class="space-y-2">
            <div v-for="(assist, index) in assists" :key="index" class="flex items-center space-x-2">
              <input v-model="assist.player_name" placeholder="Player name" class="flex-1 border rounded px-3 py-2" />
              <select v-model="assist.team_id" class="border rounded px-3 py-2">
                <option value="">Select Team</option>
                <option :value="fixture?.home_team?.id">{{ fixture?.home_team?.name }}</option>
                <option :value="fixture?.away_team?.id">{{ fixture?.away_team?.name }}</option>
              </select>
              <input v-model.number="assist.count" type="number" placeholder="Count"
                class="w-20 border rounded px-3 py-2" />
              <button @click="removeAssist(index)" class="text-red-500 hover:text-red-700">Remove</button>
            </div>
            <button @click="addAssist" class="text-blue-500 hover:text-blue-700">+ Add Assist</button>
          </div>
        </div>

        <!-- Cards -->
        <div class="border rounded-lg p-4">
          <h3 class="font-semibold mb-3">Cards</h3>
          <div class="space-y-4">
            <!-- Yellow Cards -->
            <div>
              <h4 class="font-medium mb-2">Yellow Cards</h4>
              <div class="space-y-2">
                <div v-for="(card, index) in yellowCards" :key="index" class="flex items-center space-x-2">
                  <input v-model="card.player_name" placeholder="Player name" class="flex-1 border rounded px-3 py-2" />
                  <select v-model="card.team_id" class="border rounded px-3 py-2">
                    <option value="">Select Team</option>
                    <option :value="fixture?.home_team?.id">{{ fixture?.home_team?.name }}</option>
                    <option :value="fixture?.away_team?.id">{{ fixture?.away_team?.name }}</option>
                  </select>
                  <button @click="removeYellowCard(index)" class="text-red-500 hover:text-red-700">Remove</button>
                </div>
                <button @click="addYellowCard" class="text-blue-500 hover:text-blue-700">+ Add Yellow Card</button>
              </div>
            </div>

            <!-- Red Cards -->
            <div>
              <h4 class="font-medium mb-2">Red Cards</h4>
              <div class="space-y-2">
                <div v-for="(card, index) in redCards" :key="index" class="flex items-center space-x-2">
                  <input v-model="card.player_name" placeholder="Player name" class="flex-1 border rounded px-3 py-2" />
                  <select v-model="card.team_id" class="border rounded px-3 py-2">
                    <option value="">Select Team</option>
                    <option :value="fixture?.home_team?.id">{{ fixture?.home_team?.name }}</option>
                    <option :value="fixture?.away_team?.id">{{ fixture?.away_team?.name }}</option>
                  </select>
                  <button @click="removeRedCard(index)" class="text-red-500 hover:text-red-700">Remove</button>
                </div>
                <button @click="addRedCard" class="text-blue-500 hover:text-blue-700">+ Add Red Card</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Substitutions -->
        <div class="border rounded-lg p-4">
          <h3 class="font-semibold mb-3">Substitutions</h3>
          <div class="space-y-2">
            <div v-for="(sub, index) in substitutions" :key="index" class="border rounded p-3 space-y-2">
              <div class="flex items-center space-x-2">
                <input v-model="sub.player_out" placeholder="Player out" class="flex-1 border rounded px-3 py-2" />
                <input v-model="sub.player_in" placeholder="Player in" class="flex-1 border rounded px-3 py-2" />
              </div>
              <div class="flex items-center space-x-2">
                <select v-model="sub.team_id" class="flex-1 border rounded px-3 py-2">
                  <option value="">Select Team</option>
                  <option :value="fixture?.home_team?.id">{{ fixture?.home_team?.name }}</option>
                  <option :value="fixture?.away_team?.id">{{ fixture?.away_team?.name }}</option>
                </select>
                <input v-model.number="sub.minute" type="number" placeholder="Minute"
                  class="w-24 border rounded px-3 py-2" />
                <button @click="removeSubstitution(index)" class="text-red-500 hover:text-red-700">Remove</button>
              </div>
            </div>
            <button @click="addSubstitution" class="text-blue-500 hover:text-blue-700">+ Add Substitution</button>
          </div>
        </div>

        <!-- Minutes Played -->
        <div class="border rounded-lg p-4">
          <h3 class="font-semibold mb-3">Minutes Played</h3>
          <div class="space-y-2">
            <div v-for="(minute, index) in minutes" :key="index" class="flex items-center space-x-2">
              <input v-model="minute.player_name" placeholder="Player name" class="flex-1 border rounded px-3 py-2" />
              <select v-model="minute.team_id" class="border rounded px-3 py-2">
                <option value="">Select Team</option>
                <option :value="fixture?.home_team?.id">{{ fixture?.home_team?.name }}</option>
                <option :value="fixture?.away_team?.id">{{ fixture?.away_team?.name }}</option>
              </select>
              <input v-model.number="minute.minutes_played" type="number" placeholder="Minutes"
                class="w-24 border rounded px-3 py-2" />
              <button @click="removeMinute(index)" class="text-red-500 hover:text-red-700">Remove</button>
            </div>
            <button @click="addMinute" class="text-blue-500 hover:text-blue-700">+ Add Minutes</button>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-3 pt-4">
          <button @click="close" class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
            Cancel
          </button>
          <button @click="saveEvents" :disabled="store.isSaving"
            class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50">
            {{ store.isSaving ? 'Saving...' : 'Save All Events' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useMatchEventsStore } from '@/stores/matchEvents'
import type { Goal, Assist, Card, Substitution, Minute } from '@/helpers/types/matchEvents'

interface Props {
  isOpen: boolean
  fixture: any
}


const props = defineProps<Props>()
const emit = defineEmits(['close', 'save-success'])

const store = useMatchEventsStore()

const goals = ref<Goal[]>([])
const assists = ref<Assist[]>([])
const yellowCards = ref<Card[]>([])
const redCards = ref<Card[]>([])
const substitutions = ref<Substitution[]>([])
const minutes = ref<Minute[]>([])

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    resetForm()
  }
})

const resetForm = () => {
  goals.value = []
  assists.value = []
  yellowCards.value = []
  redCards.value = []
  substitutions.value = []
  minutes.value = []
}

const close = () => {
  emit('close')
}

const addGoal = () => {
  goals.value.push({ 
    player_name: '', 
    team_id: '', 
    count: 1,
    is_own_goal: false 
  })
}

const removeGoal = (index: number) => {
  goals.value.splice(index, 1)
}

const addAssist = () => {
  assists.value.push({ player_name: '', team_id: '', count: 1 })
}

const removeAssist = (index: number) => {
  assists.value.splice(index, 1)
}

const addYellowCard = () => {
  yellowCards.value.push({ player_name: '', team_id: '' })
}

const removeYellowCard = (index: number) => {
  yellowCards.value.splice(index, 1)
}

const addRedCard = () => {
  redCards.value.push({ player_name: '', team_id: '' })
}

const removeRedCard = (index: number) => {
  redCards.value.splice(index, 1)
}

const addSubstitution = () => {
  substitutions.value.push({ player_out: '', player_in: '', team_id: '', minute: 0 })
}

const removeSubstitution = (index: number) => {
  substitutions.value.splice(index, 1)
}

const addMinute = () => {
  minutes.value.push({ player_name: '', team_id: '', minutes_played: 0 })
}

const removeMinute = (index: number) => {
  minutes.value.splice(index, 1)
}
const saveEvents = async () => {
  if (!props.fixture) return

  try {
    const regularGoals = goals.value.filter(g => !g.is_own_goal)
    const ownGoals = goals.value.filter(g => g.is_own_goal)

    const events: any = {
      assists: assists.value,
      yellowCards: yellowCards.value,
      redCards: redCards.value,
      substitutions: substitutions.value,
      minutes: minutes.value
    }

    if (regularGoals.length > 0) {
      events.goals = regularGoals
    }

    if (ownGoals.length > 0) {
      events.ownGoals = ownGoals
    }

    const result = await store.saveAllEvents(props.fixture.id, events)

    if (result.success) {
      emit('save-success')
      close()
    } else {
      console.error('Some events failed to save:', result.errors)
    }
  } catch (error) {
    console.error('Failed to save match events:', error)
  }
}
</script>