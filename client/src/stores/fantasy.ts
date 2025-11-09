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
    teamOfWeek: [] as FantasyPlayer[],
    userTeam: [] as FantasyTeam[],
    goalsLeaderboard: [] as PlayerGoalsLeaderboard[],
    gameweekStatus: null as GameweekStatusResponse | null,
    availableGameweeks: [] as any[],
    currentGameweek: null as number | null,
    gameweekData: null as any,
    isLoading: false,
    error: null as string | null,
  }),

  getters: {
    topScorers: (state) => state.goalsLeaderboard,
    topScorer: (state) => state.goalsLeaderboard[0] || null,
    currentGameweekInfo: (state) => {
      if (!state.currentGameweek) return null;
      return state.availableGameweeks.find(gw => gw.number === state.currentGameweek);
    },
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

    async fetchUserFantasyTeam(gameweek: number | null = null) {
      try {
        this.isLoading = true;
        this.error = null;

        const params: any = {};
        if (gameweek) {
          params.gameweek = gameweek;
        }

        const response = await apiClient.get(`/fantasy/teams/user-team`, { params });
        this.userTeam = response.data;

        if (response.data.length > 0) {
          const teamData = response.data[0];
          this.currentGameweek = teamData.requested_gameweek;
          this.gameweekData = {
            gameweek_name: teamData.requested_gameweek_name,
            gameweek_points: teamData.requested_gameweek_points,
            formation: teamData.requested_gameweek_formation,
            is_active: teamData.requested_gameweek ?
              this.availableGameweeks.find(gw => gw.number === teamData.requested_gameweek)?.is_active : false,
            has_selection: teamData.has_selection_for_requested_gameweek
          };
        }

        return response.data;
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error);
        return null;
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

    async fetchFantasyTeamPlayers(gameweek: number | null = null) {
      try {
        this.isLoading = true;
        const params: any = {};
        if (gameweek) {
          params.gameweek = gameweek;
        }

        const response = await apiClient.get(`/fantasy/players/gameweek-players/`, { params });

        if (response.data.detail && response.data.detail.startsWith("No team selection found")) {
          console.warn('No team selection found for the specified gameweek.');
          return;
        }


        if (Array.isArray(response.data)) {
          this.fantasyPlayers = response.data;
        } else if (response.data && typeof response.data === 'object') {
          console.warn('Received object instead of array:', response.data);
          this.fantasyPlayers = [];
        } else {
          this.fantasyPlayers = [];
        }
      } catch (error) {
        console.error('Error fetching fantasy players:', error);
        this.error = error instanceof Error ? error.message : String(error);
        this.fantasyPlayers = [];
      } finally {
        this.isLoading = false;
      }
    },

    async fetchAvailableGameweeks() {
      try {
        this.isLoading = true;
        const response = await apiClient.get('/fantasy/players/available-gameweeks/');
        this.availableGameweeks = response.data;
      } catch (error) {
        console.error('Error fetching available gameweeks:', error);
        this.availableGameweeks = [];
      } finally {
        this.isLoading = false;
      }
    },


    async fetchTeamOfWeek() {
      try {
        this.isLoading = true;
        const response = await apiClient.get(`/fantasy/performance/gameweek-team/`);
        this.teamOfWeek = response.data;
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
        this.error = null;
        const response = await apiClient.post(`/fantasy/players/save-team-players/`, team);

        if (response.status === 200) {
          await this.fetchFantasyTeamPlayers();
          return response;
        } else {
          this.error = `Unexpected response status: ${response.status}`;
          return response;
        }
      } catch (error) {
        let errMsg = "Saving changes failed";
        let rawError: any;

        if (error instanceof Error) {
          const axiosError = error as any;
          rawError = axiosError.response?.data?.error;
        }

        if (typeof rawError === "string") {
          try {
            const parsed = JSON.parse(rawError.replace(/'/g, '"'));
            errMsg = parsed[0] || errMsg;
          } catch {
            errMsg = rawError;
          }
        } else if (Array.isArray(rawError)) {
          errMsg = rawError[0];
        }

        console.error("Error saving fantasy team players:", errMsg);
        this.error = errMsg;
        return null;
      } finally {
        this.isLoading = false;
      }
    }
  },
});