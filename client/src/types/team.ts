export interface Player {
  id: string;
  name: string;
  position: string;
  isCaptain?: boolean;
  isViceCaptain?: boolean;
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
