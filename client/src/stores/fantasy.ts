import { defineStore } from "pinia";
import apiClient from "@/axios-interceptor";
import type { Fixture, TeamStanding, Team, Player } from "@/helpers/types/team";
import type { FantasyTeam } from "@/helpers/types/fantasy";

export const useFantasyStore = defineStore("fantasy", {
  state: () => ({
    fantasyTeams: [] as FantasyTeam[],
    userTeam: [] as FantasyTeam[],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchFantasyTeams() {
      try {
        this.isLoading = true;
        const response = await apiClient.get("/fantasy/teams/");
        this.fantasyTeams = response.data;
      } catch (error) {
        this.error = error;
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
        this.error = error;
      } finally {
        this.isLoading = false;
      }
    },

    async createFantasyTeam(name: string) {
      try {
        this.isLoading = true;
        const response = await apiClient.post("/fantasy/teams/", { name });
        this.userTeam = response.data;
      } catch (error) {
        this.error = error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
