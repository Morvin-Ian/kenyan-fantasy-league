import { defineStore } from "pinia";
import apiClient from "@/axios-interceptor";
import type { FantasyPlayer, FantasyTeam } from "@/helpers/types/fantasy";
import type { TeamData } from "@/helpers/types/team";

export const useFantasyStore = defineStore("fantasy", {
  state: () => ({
    fantasyTeams: [] as FantasyTeam[],
    fantasyPlayers: [] as FantasyPlayer[],
    userTeam: [] as FantasyTeam[],
    isLoading: false,
    error: null as string | null,
  }),

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
      } catch (error: any) {
        const errorMessage = error.response?.data[0] || "Failed to create team. Please try again.";
        this.error = errorMessage;
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

    async saveFantasyTeamPlayers(team: TeamData) {
      try {
        this.isLoading = true;
        const response = await apiClient.post(`/fantasy/players/save-team-players/`, team);
        this.fetchFantasyTeamPlayers();
        return response.data;
      } catch (error) {
        let errMsg = "Saving changes failed";
        const rawError = error.response?.data?.error;

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
      } finally {
        this.isLoading = false;
      }
    }
  },
});
