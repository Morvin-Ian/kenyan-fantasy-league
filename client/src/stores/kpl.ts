import { defineStore } from "pinia";
import apiClient from "@/axios-interceptor";
import type { Fixture, TeamStanding, Team, Player, Lineup } from "@/helpers/types/team";


type PaginatedResponse<T> = {
  results: T[];
  next: string | null;
};



export const useKplStore = defineStore('kpl', {
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
        const baseQuery = '?up_to_active=true';

        // First request to get total count
        const firstResponse = await apiClient.get(`/kpl/fixtures/${baseQuery}&page=1`);
        const { results, next } = firstResponse.data;

        // If there's no next page, we're done
        if (!next) {
          this.fixtures = results;
          return;
        }

        // Parse the next URL to determine total pages
        // Most Django REST pagination includes page info
        let allFixtures = [...results];
        let currentPage = 2;
        const maxConcurrentRequests = 3; // Limit concurrent requests

        // Fetch remaining pages in batches
        while (true) {
          const pagePromises = [];
          for (let i = 0; i < maxConcurrentRequests; i++) {
            const pageQuery = `${baseQuery}&page=${currentPage + i}`;
            pagePromises.push(
              apiClient.get(`/kpl/fixtures/${pageQuery}`)
                .then(res => res.data)
                .catch(err => {
                  // If page doesn't exist, we've reached the end
                  if (err.response?.status === 404) return null;
                  throw err;
                })
            );
          }

          const responses = await Promise.all(pagePromises);
          const validResponses = responses.filter(r => r !== null);

          if (validResponses.length === 0) break;

          for (const response of validResponses) {
            allFixtures = [...allFixtures, ...response.results];
          }

          // Check if we should continue
          const lastResponse = validResponses[validResponses.length - 1];
          if (!lastResponse || !lastResponse.next) break;

          currentPage += maxConcurrentRequests;
        }

        this.fixtures = allFixtures;
      } catch (error) {
        console.error("Error fetching fixtures:", error);
        this.fixtures = [];
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
        const isProduction = import.meta.env.MODE === 'production';
        let nextUrl: string | null = "/kpl/players/";

        // Fetch all pages sequentially for now (simpler and more reliable)
        // Can be optimized later if needed
        while (nextUrl) {
          let url = nextUrl;
          if (isProduction && url.startsWith('http://')) {
            url = url.replace(/^http:\/\//, 'https://');
          }

          const response: { data: PaginatedResponse<Player> } = await apiClient.get(url);
          this.players = this.players.concat(response.data.results);
          nextUrl = response.data.next;
        }
      } catch (error) {
        console.error("Error fetching players:", error);
      }
    },


    async submitLineup(lineupData: {
      fixture_id: string;
      team_id: string;
      side: 'home' | 'away';
      formation: string;
      starting_xi: string[];
      bench_players: string[];
    }) {
      try {
        const response = await apiClient.post(`/kpl/fixtures/submit-lineup/`, lineupData)
        return response.data
      } catch (error) {
        throw error
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
