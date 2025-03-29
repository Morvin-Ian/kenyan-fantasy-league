import { defineStore } from "pinia";
import apiClient from "@/axios-interceptor";
import  type {Fixture, TeamStanding } from "@/helpers/types/team";

export const useKplStore = defineStore({
  id: "kpl",
  state: () => ({
    teams: [],
    standings: [] as TeamStanding[], 
    fixtures: [] as Fixture[]
  }),
  actions: {
    async fetchTeams() {
      try {
        const response = await apiClient.get("/kpl/teams/");
        this.teams = response.data.results;
      } catch (error) {
        console.error("Error fetching teams:", error);
      }
    },

    async fetchStandings() {
      try {
        const response = await apiClient.get("/kpl/standings/");
        this.standings = response.data.results;
      } catch (error) {
        console.error("Error fetching standings:", error);
      }
    },

    async fetchFixtures() {
      try {
        const response = await apiClient.get("/kpl/fixtures/");
        this.fixtures = response.data.results;
      } catch (error) {
        console.error("Error fetching fixtures:", error);
      }
    },

    async fetchAllData() {
      await Promise.all([
        this.fetchTeams(),
        this.fetchStandings(),
        this.fetchFixtures(),
      ]);
    },
  },
});
