export interface Player {
  id: string; 
  name: string;
  team: string;
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

interface StartingEleven {
  goalkeeper: Player;
  defenders: Player[];
  midfielders: Player[];
  forwards: Player[];
  [key: string]: Player | Player[]; 
}
export interface Fixture {
  match: string;
  date: string;
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