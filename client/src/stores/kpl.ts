import { defineStore } from "pinia";
import apiClient from "@/axios-interceptor";
import  type {Fixture, TeamStanding, Team, Player } from "@/helpers/types/team";

export const useKplStore = defineStore({
  id: "kpl",
  state: () => ({
    teams: [] as Team[],
    standings: [] as TeamStanding[], 
    fixtures: [] as Fixture[],
    players:[] as Player[]
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

    async fetchPlayers() {
      try {
        let nextUrl: string | null = "/kpl/players/";
    
        while (nextUrl) {
          const response = await apiClient.get(nextUrl);
          this.players = this.players.concat(response.data.results);
          nextUrl = response.data.next; 
        }
    
      } catch (error) {
        console.error("Error fetching players:", error);
      }
    },

    async fetchAllData() {
      await Promise.all([
        this.fetchTeams(),
        this.fetchStandings(),
        this.fetchFixtures()
      ]);
    },
  },
});
