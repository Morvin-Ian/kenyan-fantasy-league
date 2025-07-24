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
  startingEleven: StartingElevenRef;
  benchPlayers: FantasyPlayer[];
}
export interface Fixture {
  id: string;
  status: string;
  type: string;
  home_team: Team;
  away_team: Team;
  match_date?: string;
  datetime?: string;
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
