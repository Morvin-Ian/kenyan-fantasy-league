import { defineStore } from "pinia";
import apiClient from "@/axios-interceptor";
import type {
  FantasyPlayer,
  FantasyTeam,
  PlayerGoalsLeaderboard,
  GoalsLeaderboardResponse
} from "@/helpers/types/fantasy";

import type { GameweekStatusResponse } from "@/helpers/types/gameweek";
import type { TeamData } from "@/helpers/types/team";

export const useFantasyStore = defineStore("fantasy", {
  state: () => ({
    fantasyTeams: [] as FantasyTeam[],
    fantasyPlayers: [] as FantasyPlayer[],
    userTeam: [] as FantasyTeam[],
    goalsLeaderboard: [] as PlayerGoalsLeaderboard[],
    gameweekStatus: null as GameweekStatusResponse | null,
    isLoading: false,
    error: null as string | null,
  }),

  getters: {
    topScorers: (state) => state.goalsLeaderboard,
    topScorer: (state) => state.goalsLeaderboard[0] || null,
  },

  actions: {
    async fetchFantasyTeams() {
      try {
        this.isLoading = true;
        const response = await apiClient.get("/fantasy/teams/");
        this.fantasyTeams = response.data;
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchUserFantasyTeam() {
      try {
        this.isLoading = true;
        const response = await apiClient.get(`/fantasy/teams/user-team`);
        this.userTeam = response.data;
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error);
      } finally {
        this.isLoading = false;
      }
    },

    async createFantasyTeam(name: string, formation: string) {
      try {
        this.isLoading = true;
        const response = await apiClient.post("/fantasy/teams/", { name, formation });
        this.userTeam = response.data;
        return response;
      } catch (error: any) {
        let errorMessage = "Failed to create team. Please try again.";

        if (error.response?.data) {
          const data = error.response.data;

          if (typeof data === "object") {
            const firstKey = Object.keys(data)[0];
            if (firstKey && Array.isArray(data[firstKey])) {
              errorMessage = data[firstKey][0];
            } else if (data.detail) {
              errorMessage = data.detail;
            }
          }
        }

        this.error = errorMessage;
        return error.response;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchFantasyTeamPlayers() {
      try {
        this.isLoading = true;
        const response = await apiClient.get(`/fantasy/players/team-players`);
        this.fantasyPlayers = response.data;
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchTopGoalsScorers(limit: number = 5) {
      try {
        this.isLoading = true;
        const response = await apiClient.get<GoalsLeaderboardResponse>(
          `fantasy/performance/goals-leaderboard/?limit=${limit}`
        );
        this.goalsLeaderboard = response.data.results;
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error);
        console.error("Failed to fetch top goals scorers:", error);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchGameweekStatus(gameweekId?: number): Promise<GameweekStatusResponse> {
      try {
        this.isLoading = true;
        const response = await apiClient.get<GameweekStatusResponse>(
          `/fantasy/gameweek/status/`,
          {
            params: gameweekId ? { gameweek_id: gameweekId } : {},
          }
        );
        this.gameweekStatus = response.data;
        return response.data;
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error);
        console.error("Failed to fetch gameweek status:", error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async saveFantasyTeamPlayers(team: TeamData) {
      try {
        this.isLoading = true;
        const response = await apiClient.post(`/fantasy/players/save-team-players/`, team);
        this.fetchFantasyTeamPlayers();
        return response.data;
      } catch (error) {
        let errMsg = "Saving changes failed";
        let rawError: any;

        if (error instanceof Error) {
          // Axios errors usually have `response`
          const axiosError = error as any;
          rawError = axiosError.response?.data?.error;
        }

        if (typeof rawError === "string") {
          try {
            // Convert Python-like list string into JSON
            const parsed = JSON.parse(rawError.replace(/'/g, '"'));
            console.log("Parsed error message:", parsed[0]);
            errMsg = parsed[0] || errMsg;
          } catch {
            errMsg = rawError;
          }
        } else if (Array.isArray(rawError)) {
          errMsg = rawError[0];
        }

        console.error("Error saving fantasy team players:", errMsg);
        this.error = errMsg;
      }
      finally {
        this.isLoading = false;
      }
    }
  },
});
