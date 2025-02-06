// data.ts
export interface Player {
  id: number;
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

export const overallRank = "234,567";

export const totalPoints = 57;
export const averagePoints = 52;
export const highestPoints = 121;

export const startingEleven = {
  // Goalkeeper (1)
  goalkeeper: {
    id: 1,
    name: "Alisson",
    team: "GOR",
    position: "GK",
    points: 6,
    form: "6.7",
    price: 5.5,
    nextFixture: "MUN (H)",
    chanceOfPlaying: 10,
    selectedBy: "34.5%",
    pointsPerGame: 4.2,
  },

  // Defenders (4)
  defenders: [
    {
      id: 2,
      name: "Arnold",
      team: "AFC",
      position: "DEF",
      points: 12,
      form: "7.2",
      price: 7.8,
      nextFixture: "MUN (H)",
      chanceOfPlaying: 100,
      selectedBy: "28.9%",
      pointsPerGame: 5.3,
    },
    {
      id: 3,
      name: "Chilwell",
      team: "AFC",
      position: "DEF",
      points: 2,
      form: "5.4",
      price: 5.4,
      nextFixture: "BUR (H)",
      chanceOfPlaying: 100,
      selectedBy: "15.2%",
      pointsPerGame: 3.8,
    },
    {
      id: 4,
      name: "Dias",
      team: "ULINZI",
      position: "DEF",
      points: 6,
      form: "6.1",
      price: 6.2,
      nextFixture: "NEW (A)",
      chanceOfPlaying: 100,
      selectedBy: "22.1%",
      pointsPerGame: 4.5,
    },
    {
      id: 5,
      name: "Gabriel",
      team: "ULINZI",
      position: "DEF",
      points: 8,
      form: "6.8",
      price: 5.2,
      nextFixture: "TOT (H)",
      chanceOfPlaying: 100,
      selectedBy: "18.4%",
      pointsPerGame: 4.2,
    },
  ],

  // Midfielders (3)
  midfielders: [
    {
      id: 6,
      name: "Salah",
      team: "TUSKER",
      position: "MID",
      points: 15,
      form: "8.3",
      price: 12.8,
      nextFixture: "MUN (H)",
      chanceOfPlaying: 100,
      selectedBy: "45.6%",
      pointsPerGame: 7.8,
    },
    {
      id: 7,
      name: "Son",
      team: "TUSKER",
      position: "MID",
      points: 8,
      form: "7.1",
      price: 9.3,
      nextFixture: "ARS (A)",
      chanceOfPlaying: 100,
      selectedBy: "32.4%",
      pointsPerGame: 6.5,
    },
    {
      id: 8,
      name: "Saka",
      team: "ULINZI",
      position: "MID",
      points: 7,
      form: "7.4",
      price: 8.7,
      nextFixture: "TOT (H)",
      chanceOfPlaying: 100,
      selectedBy: "38.9%",
      pointsPerGame: 6.2,
    },
  ],

  // Forwards (3)
  forwards: [
    {
      id: 9,
      name: "Haaland",
      team: "GOR",
      position: "FWD",
      points: 13,
      form: "8.9",
      price: 14.2,
      nextFixture: "NEW (A)",
      chanceOfPlaying: 100,
      selectedBy: "82.3%",
      pointsPerGame: 8.5,
    },
    {
      id: 10,
      name: "Darwin",
      team: "AFC",
      position: "FWD",
      points: 6,
      form: "6.8",
      price: 7.8,
      isCaptain: true,
      nextFixture: "MUN (H)",
      chanceOfPlaying: 100,
      selectedBy: "24.7%",
      pointsPerGame: 5.1,
    },
    {
      id: 11,
      name: "Watkins",
      team: "AFC",
      position: "FWD",
      points: 8,
      form: "7.2",
      isViceCaptain: true,
      price: 8.5,
      nextFixture: "WOL (H)",
      chanceOfPlaying: 100,
      selectedBy: "28.3%",
      pointsPerGame: 5.8,
    },
  ],
};

// Bench Players (4)
export const benchPlayers = [
  {
    id: 12,
    name: "Raya",
    team: "AFC",
    position: "GK",
    points: 0,
    form: "6.2",
    price: 4.8,
    nextFixture: "TOT (H)",
    chanceOfPlaying: 100,
    selectedBy: "12.4%",
    pointsPerGame: 3.8,
  },
  {
    id: 13,
    name: "White",
    team: "GOR",
    position: "DEF",
    points: 0,
    form: "6.5",
    price: 5.1,
    nextFixture: "TOT (H)",
    chanceOfPlaying: 100,
    selectedBy: "15.7%",
    pointsPerGame: 4.2,
  },
  {
    id: 14,
    name: "Gordon",
    team: "TUSKER",
    position: "MID",
    points: 0,
    form: "6.8",
    price: 6.2,
    nextFixture: "MCI (H)",
    chanceOfPlaying: 100,
    selectedBy: "8.9%",
    pointsPerGame: 4.5,
  },
  {
    id: 15,
    name: "Archer",
    team: "ULINZI",
    position: "FWD",
    points: 0,
    form: "5.4",
    price: 4.5,
    nextFixture: "WOL (H)",
    chanceOfPlaying: 100,
    selectedBy: "5.2%",
    pointsPerGame: 2.8,
  },
];
