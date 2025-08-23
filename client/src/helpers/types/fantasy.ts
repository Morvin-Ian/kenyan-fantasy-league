export interface FantasyTeam {
  user: string;
  id: string;
  name: string;
  budget: string;
  gameweek: number;
  formation: string;
  free_transfers: number;
  total_points: number;
  overall_rank: number | null;
  transfer_budget: string;
}

export interface FantasyPlayer {
  id: string;
  name: string;
  position: string;
  team: FantasyTeam | string;
  jersey_image: string;
  price: string;
  fantasy_team: string;
  player: string;
  gameweek: number;
  total_points: number;
  gameweek_points: number | null;
  is_captain: boolean;
  is_vice_captain: boolean;
  is_starter: boolean;
  purchase_price: string;
  current_value: string;
  isInjured: boolean | null;
  isPlaceholder: boolean | null;
}
