// stores/matchEvents.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { readonly } from 'vue'
import apiClient from '@/axios-interceptor'
import type { Assist, Card, Goal, Minute, Substitution, ApiResponse } from '@/helpers/types/matchEvents'

export const useMatchEventsStore = defineStore('matchEvents', () => {
  const isSaving = ref(false)
  const error = ref<string | null>(null)

  const updateAssists = async (fixtureId: string, assists: Assist[]): Promise<ApiResponse> => {
    isSaving.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/kpl/match-events/update-assists/', {
        fixture_id: fixtureId,
        assists: assists.filter(a => a.player_name && a.team_id)
      })

      const data: ApiResponse = response.data
      return data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Failed to update assists'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  const updateCards = async (
    fixtureId: string, 
    yellowCards: Card[], 
    redCards: Card[]
  ): Promise<ApiResponse> => {
    isSaving.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/kpl/match-events/update-cards/', {
        fixture_id: fixtureId,
        yellow_cards: yellowCards.filter(c => c.player_name && c.team_id),
        red_cards: redCards.filter(c => c.player_name && c.team_id)
      })

      const data: ApiResponse = response.data
      return data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Failed to update cards'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  const updateSubstitutions = async (
    fixtureId: string, 
    substitutions: Substitution[]
  ): Promise<ApiResponse> => {
    isSaving.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/kpl/match-events/update-substitutions/', {
        fixture_id: fixtureId,
        substitutions: substitutions.filter(s => s.player_out && s.player_in && s.team_id)
      })

      const data: ApiResponse = response.data
      return data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Failed to update substitutions'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  const updateMinutes = async (
    fixtureId: string, 
    minutes: Minute[]
  ): Promise<ApiResponse> => {
    isSaving.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/kpl/match-events/update-minutes/', {
        fixture_id: fixtureId,
        minutes: minutes.filter(m => m.player_name && m.team_id)
      })

      const data: ApiResponse = response.data
      return data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Failed to update minutes'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  const updateGoals = async (
    fixtureId: string, 
    goals: Goal[]
  ): Promise<ApiResponse> => {
    isSaving.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/kpl/match-events/update-goals/', {
        fixture_id: fixtureId,
        goals: goals.filter(g => g.player_name && g.team_id)
      })

      const data: ApiResponse = response.data
      return data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Failed to update goals'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  const updateGoalkeeperStats = async (
    fixtureId: string,
    saves: Array<{ player_name: string; team_id: string; count: number }>,
    penaltiesSaved: Array<{ player_name: string; team_id: string; count: number }>,
    penaltiesMissed: Array<{ player_name: string; team_id: string; count: number }>
  ): Promise<ApiResponse> => {
    isSaving.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/kpl/match-events/update-goalkeeper-stats/', {
        fixture_id: fixtureId,
        saves: saves.filter(s => s.player_name && s.team_id),
        penalties_saved: penaltiesSaved.filter(s => s.player_name && s.team_id),
        penalties_missed: penaltiesMissed.filter(s => s.player_name && s.team_id)
      })

      const data: ApiResponse = response.data
      return data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Failed to update goalkeeper stats'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  const saveAllEvents = async (
    fixtureId: string,
    events: {
      goals?: Goal[]
      assists?: Assist[]
      yellowCards?: Card[]
      redCards?: Card[]
      substitutions?: Substitution[]
      minutes?: Minute[]
    }
  ): Promise<{ success: boolean; errors: any[] }> => {
    isSaving.value = true
    error.value = null
    const allErrors: any[] = []

    try {
      // Save goals first (if any)
      if (events.goals && events.goals.length > 0) {
        try {
          await updateGoals(fixtureId, events.goals)
        } catch (err) {
          allErrors.push({ type: 'goals', error: err })
        }
      }

      // Save assists
      if (events.assists && events.assists.length > 0) {
        try {
          await updateAssists(fixtureId, events.assists)
        } catch (err) {
          allErrors.push({ type: 'assists', error: err })
        }
      }

      // Save cards
      if ((events.yellowCards && events.yellowCards.length > 0) || 
          (events.redCards && events.redCards.length > 0)) {
        try {
          await updateCards(
            fixtureId, 
            events.yellowCards || [], 
            events.redCards || []
          )
        } catch (err) {
          allErrors.push({ type: 'cards', error: err })
        }
      }

      // Save substitutions
      if (events.substitutions && events.substitutions.length > 0) {
        try {
          await updateSubstitutions(fixtureId, events.substitutions)
        } catch (err) {
          allErrors.push({ type: 'substitutions', error: err })
        }
      }

      // Save minutes
      if (events.minutes && events.minutes.length > 0) {
        try {
          await updateMinutes(fixtureId, events.minutes)
        } catch (err) {
          allErrors.push({ type: 'minutes', error: err })
        }
      }

      return {
        success: allErrors.length === 0,
        errors: allErrors
      }
    } finally {
      isSaving.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    isSaving: readonly(isSaving),
    error: readonly(error),
    updateAssists,
    updateCards,
    updateSubstitutions,
    updateMinutes,
    updateGoals,
    updateGoalkeeperStats,
    saveAllEvents,
    clearError
  }
})