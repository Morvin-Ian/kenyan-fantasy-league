import { defineStore } from "pinia";
import apiClient from "@/axios-interceptor";
import type { Fixture, TeamStanding, Team, Player, Lineup } from "@/helpers/types/team";


type PaginatedResponse<T> = {
  results: T[];
  next: string | null;
};



export const useKplStore = defineStore({
  id: "kpl",
  state: () => ({
    teams: [] as Team[],
    standings: [] as TeamStanding[],
    fixtures: [] as Fixture[],
    players: [] as Player[],
    fixtureLineups: new Map<string, Lineup[]>()
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

    async fetchFixtures(includeLineups: boolean = true) {
      try {
        const query = includeLineups ? "?include=lineups=true" : "";
        const response = await apiClient.get(`/kpl/fixtures/${query}`);
        this.fixtures = response.data.results;
      } catch (error) {
        console.error("Error fetching fixtures:", error);
      }
    },
    async fetchFixtureLineups(fixtureId: string, { force }: { force?: boolean } = {}) {
      try {
        if (!force && this.fixtureLineups.has(fixtureId)) {
          return this.fixtureLineups.get(fixtureId)!;
        }
        const response = await apiClient.get(`/kpl/fixtures/${fixtureId}/lineups/`);
        const data: Lineup[] = response.data;
        this.fixtureLineups.set(fixtureId, data);
        return data;
      } catch (error) {
        console.error(`Error fetching lineups for fixture ${fixtureId}:`, error);
        throw error;
      }
    },

    async fetchPlayers() {
      try {
        let nextUrl: string | null = "/kpl/players/";

        while (nextUrl) {
          const response: { data: PaginatedResponse<Player> } = await apiClient.get(nextUrl);          
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
        this.fetchFixtures(true)
      ]);
    },
  },
});
