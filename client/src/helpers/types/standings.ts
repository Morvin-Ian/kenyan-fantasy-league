export interface TeamStanding {
    position: number;
    team: string;
    played: number;
    wins: number;
    draws: number;
    losses: number;
    goals_for: number;
    goals_against: number;
    points: number;
    form: ("W" | "D" | "L")[];
}