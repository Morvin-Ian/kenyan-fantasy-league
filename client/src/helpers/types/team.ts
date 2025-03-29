export type Team = {
  id: string;
  name: string;
  logo_url?: string; 
};


export interface Player {
  id: string;
  name: string;
  team: Team; 
  position: string;
  points: number;
  form: string;
  price: number;
  nextFixture: string;
  chanceOfPlaying: number;
  selectedBy: string;
  pointsPerGame: number;
  isCaptain?: boolean;
  isViceCaptain?: boolean;
}



export interface StartingEleven {
  goalkeeper: Player;
  defenders: Player[];
  midfielders: Player[];
  forwards: Player[];
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
  position:number;
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
  form: string;
}
