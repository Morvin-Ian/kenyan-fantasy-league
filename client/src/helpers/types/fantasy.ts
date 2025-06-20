export interface FantasyTeam {
  user: string;
  id: string;
  name: string;
  budget: string;
  gameweek: number;
  formation: string;
  total_points: number;
  overall_rank: number | null;
  transfer_budget: string;
}
