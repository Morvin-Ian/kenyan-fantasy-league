export interface MatchDayStatus {
  date: number;
  name: string; 
  month: string; 
  full_date: string; 
  match_status: "COMPLETED" | "LIVE" | "POSTPONED" | "UPCOMING" | "CONFIRMED";
  bonus_status: "ADDED" | "PENDING";
  fixtures_count: number;
  completed_count: number;
  live_count: number;
  goals_scored: number;
  interesting_fact: string;
}


export interface FixturesSummary {
  total_fixtures: number;
  completed: number;
  live: number;
  upcoming: number;
  postponed: number;
  total_goals: number;
  average_goals: number;
  home_wins: number;
  draws: number;
  away_wins: number;
  biggest_win: MatchSummary | null;
  highest_scoring: MatchSummary | null;
}

export interface MatchSummary {
  home_team: string;
  away_team: string;
  score: string; // e.g. "3-1"
  margin?: number; // only for biggest_win
  goals?: number; // only for highest_scoring
}

export interface TeamPerformanceSummary {
  teams_played: number;
  best_attack: { team: string; goals: number } | null;
  best_defense: { team: string; goals_conceded: number } | null;
  team_stats: Record<
    string,
    { played: number; goals_for: number; goals_against: number; points: number }
  >;
}

export interface InterestingStat {
  label: string;
  value: string;
  icon: string;
  trend: "up" | "down" | "neutral";
}

export interface LineupDetail {
  fixture_id: number;
  home_team: string;
  away_team: string;
  match_date: string;
  home_lineup_confirmed: boolean;
  away_lineup_confirmed: boolean;
  home_formation: string | null;
  away_formation: string | null;
  status: string; 
}

export interface LiveUpdate {
  type: "live_match" | "upcoming_match" | "match_completed";
  message: string;
  fixture_id: number;
  priority: "high" | "medium" | "low";
  timestamp: string; 
}


export interface LineupsStatus {
  total_fixtures: number;
  confirmed_lineups: number;
  confirmation_percentage: number;
  lineup_details: LineupDetail[];
}

export interface GameweekStatusResponse {
  gameweek: {
    number: number;
    is_active: boolean;
    start_date: string; 
    end_date: string;   
    transfer_deadline: string; 
    status: "UPCOMING" | "ACTIVE" | "LIVE" | "COMPLETED" | "DELAYED";
    progress_percentage: number;
  };
  match_days: MatchDayStatus[];
  fixtures_summary: FixturesSummary;
  team_performance: TeamPerformanceSummary;
  interesting_stats: InterestingStat[];
  lineups_status: LineupsStatus;
  live_updates: LiveUpdate[];
}



