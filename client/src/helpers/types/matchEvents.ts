
export interface Goal {
  player_name: string
  team_id: string
  count: number
}

export interface Assist {
  player_name: string
  team_id: string
  count: number
}

export interface Card {
  player_name: string
  team_id: string
}

export interface Substitution {
  player_out: string
  player_in: string
  team_id: string
  minute: number
}

export interface Minute {
  player_name: string
  team_id: string
  minutes_played: number
}

export interface ApiResponse {
  success: boolean
  updated_count: number
  updated_players: any[]
  errors: any[]
}