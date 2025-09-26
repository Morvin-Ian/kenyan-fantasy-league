import { type FantasyPlayer } from "./fantasy";

export interface Team {
  id: string;
  name: string;
  logo_url?: string;
  jersey_image?: string;
}

export interface Player {
  id: string;
  name: string;
  position: string;
  age?: number;
  current_value:number;
  jersey_number?: number;
  team: Team;
}

export interface StartingEleven {
  goalkeeper: FantasyPlayer;
  defenders: FantasyPlayer[];
  midfielders: FantasyPlayer[];
  forwards: FantasyPlayer[];
}

export interface StartingElevenRef {
  goalkeeper: FantasyPlayer | null;
  defenders: FantasyPlayer[];
  midfielders: FantasyPlayer[];
  forwards: FantasyPlayer[];
}

export interface TeamData {
  formation: string;
  startingEleven: StartingElevenRef;
  benchPlayers: FantasyPlayer[];
}
export interface Fixture {
  id: string;
  status: string;
  type: string;
  home_team: Team;
  away_team: Team;
  home_team_score: string;
  away_team_score: string;
  venue:string;
  is_active:boolean;
  match_date: string;
  datetime?: string;
  lineup_status?: LineupStatus | null;
}

export interface Result {
  match: string;
  date: string;
}

export interface Performer {
  name: string;
  points: number;
  image: string;
}

export interface TeamStanding {
  id: number;
  position: number;
  team: Team;
  played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goalDifference: number;
  goal_differential: number;
  points: number;
  form: string[];
}

export interface LineupPlayer {
  id: string;
  player: Player | null;
  position: "GKP" | "DEF" | "MID" | "FWD" | null;
  order_index: number;
  is_bench: boolean;
}

export interface Lineup {
  id: string;
  team: Team;
  side: "home" | "away";
  formation?: string;
  is_confirmed: boolean;
  source: string;
  published_at: string | null;
  starters?: LineupPlayer[];
  bench?: LineupPlayer[];
  players?: LineupPlayer[];
}

export interface LineupStatus {
  available: boolean;
  confirmed: boolean;
  status: "Predicted" | "Confirmed" | "NA";
}
