<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/40" @click="$emit('close')"></div>
    <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-4xl mx-4">
      <div class="flex items-center justify-between px-5 py-4 border-b">
        <h3 class="text-lg font-semibold">Lineups</h3>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-800">✕</button>
      </div>
      <div class="p-4">
        <div v-if="isLoading" class="py-10 text-center text-gray-500">Loading...</div>
        <div v-else class="grid md:grid-cols-2 gap-4">
          <div v-for="(group, idx) in grouped" :key="idx" class="bg-gray-50 rounded-xl p-4">
            <div class="flex items-center justify-between mb-2">
              <div class="font-semibold">{{ group.sideLabel }} - {{ group.team.name }}</div>
              <div class="text-xs text-gray-600">{{ group.formation || '—' }}</div>
            </div>
            <Pitch
              :goalkeeper="group.gk"
              :defenders="group.def"
              :midfielders="group.mid"
              :forwards="group.fwd"
              :benchPlayers="group.bench"
              :switchSource="null"
              :switchActive="false"
            />
          </div>
        </div>
      </div>
      <div class="px-5 py-4 border-t flex items-center justify-end">
        <button @click="$emit('close')" class="px-4 py-2 rounded-full bg-gray-800 text-white">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Pitch from '@/components/Team/Pitch.vue';
import type { Lineup, LineupPlayer } from '@/helpers/types/team';
import type { FantasyPlayer } from '@/helpers/types/fantasy';

const props = defineProps<{ open: boolean; lineups: Lineup[]; isLoading: boolean }>();
defineEmits<{ (e: 'close'): void }>();

const toFantasyPlayer = (lp: LineupPlayer): FantasyPlayer => ({
  id: (lp.player?.id ?? `placeholder-${lp.order_index}`).toString(),
  name: lp.player?.name ?? 'TBD',
  position: lp.position ?? 'MID',
  team: '',
  jersey_image: '',
  price: '0',
  fantasy_team: '',
  player: '',
  gameweek: 0,
  total_points: 0,
  gameweek_points: 0,
  is_captain: false,
  is_vice_captain: false,
  is_starter: true,
  purchase_price: '0',
  current_value: '0',
  isInjured: null,
  isPlaceholder: null,
});

const grouped = computed(() => {
  return props.lineups.map((l) => {
    const startersRaw: LineupPlayer[] = (l.starters ?? l.players ?? []).filter((p) => !p.is_bench);
    const starters: LineupPlayer[] = assignPositions(startersRaw, l.formation);
    const bench: LineupPlayer[] = (l.bench ?? l.players ?? []).filter((p) => p.is_bench);
    const gk = starters.filter((p) => p.position === 'GKP').map(toFantasyPlayer)[0] as FantasyPlayer;
    const def = starters.filter((p) => p.position === 'DEF').map(toFantasyPlayer) as FantasyPlayer[];
    const mid = starters.filter((p) => p.position === 'MID').map(toFantasyPlayer) as FantasyPlayer[];
    const fwd = starters.filter((p) => p.position === 'FWD').map(toFantasyPlayer) as FantasyPlayer[];
    const benchPlayers = bench.map(toFantasyPlayer) as FantasyPlayer[];
    return {
      sideLabel: l.side === 'home' ? 'Home' : 'Away',
      team: l.team,
      formation: l.formation,
      gk,
      def,
      mid,
      fwd,
      bench: benchPlayers,
    };
  });
});

function parseFormationParts(formation?: string, startersCount: number = 11): number[] {
  if (!formation) return [4, 3, 3];
  const parts = formation
    .split('-')
    .map((p) => parseInt(p.trim(), 10))
    .filter((n) => Number.isFinite(n) && n >= 0);
  if (parts.length < 2) return [4, 3, 3];
  const sum = parts.reduce((a, b) => a + b, 0);
  // Formation usually excludes GK; normalize to 10 outfielders
  if (sum === 10) return [parts[0], parts[1], parts.slice(2).reduce((a, b) => a + b, 0)];
  // If more than 3 lines, merge last lines to get DEF, MID, FWD buckets
  if (parts.length >= 3) return [parts[0], parts[1], parts.slice(2).reduce((a, b) => a + b, 0)];
  // Fallback
  return [4, 3, 3];
}

function assignPositions(starters: LineupPlayer[], formation?: string): LineupPlayer[] {
  if (!starters || starters.length === 0) return starters;
  const hasAnyPosition = starters.some((p) => p.position);
  const hasGK = starters.some((p) => p.position === 'GKP');
  if (hasAnyPosition && hasGK) return starters;

  // Decide distribution
  const startersCount = starters.length;
  const [defCDefault, midCDefault, fwdCDefault] = parseFormationParts(formation, startersCount);
  // Ensure total starters → 1 GK + outfielders
  const outfielders = Math.max(startersCount - 1, 0);
  let defC = Math.min(defCDefault, outfielders);
  let midC = Math.min(midCDefault, Math.max(outfielders - defC, 0));
  let fwdC = Math.max(outfielders - defC - midC, 0);

  // Assign positions by index order (assuming list order mirrors jersey order 1..11)
  return starters.map((p, idx) => {
    if (idx === 0) return { ...p, position: 'GKP' } as LineupPlayer;
    const outIdx = idx - 1;
    if (outIdx < defC) return { ...p, position: 'DEF' } as LineupPlayer;
    if (outIdx < defC + midC) return { ...p, position: 'MID' } as LineupPlayer;
    return { ...p, position: 'FWD' } as LineupPlayer;
  });
}
</script>


