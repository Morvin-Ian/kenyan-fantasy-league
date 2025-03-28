<template>
    <div class="p-4">
        <div class="max-w-7xl mx-auto flex flex-col lg:flex-row gap-6">
            <div class="w-full lg:w-2/3 rounded-xl shadow-lg">
                <Pitch 
                    :goalkeeper="goalkeeper" 
                    :defenders="defenders" 
                    :midfielders="midfielders" 
                    :forwards="forwards"
                    :switch-source="switchSource" 
                    :switch-active="switchActive" 
                    @player-click="handlePlayerClick" 
                />

                <Bench 
                    :bench-players="benchPlayers" 
                    :switch-source="switchSource" 
                    :switch-active="switchActive"
                    @player-click="handlePlayerClick" 
                />
            </div>

            <Sidebar 
                :total-points="totalPoints" 
                :average-points="averagePoints" 
                :highest-points="highestPoints"
                :overall-rank="overallRank" 
                :upcoming-fixtures="upcomingFixtures" 
                :recent-results="recentResults"
                :top-performers="topPerformers" 
            />
        </div>

        <PlayerModal 
            :show-modal="showModal" 
            :selected-player="selectedPlayer" 
            @close-modal="closeModal"
            @initiate-switch="initiateSwitch" 
            @make-captain="makeCaptain" 
            @make-vice-captain="makeViceCaptain" 
        />
    </div>
</template>


<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import Pitch from "@/components/Team/Pitch.vue";
import Bench from "@/components/Team/Bench.vue";
import Sidebar from "@/components/Team/SideBar.vue";
import PlayerModal from "@/components/Team/PlayerModal.vue";
import { startingEleven, benchPlayers } from "@/helpers/data";
import type { Player, Fixture, Result, Performer } from "@/helpers/types/team";
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const showModal = ref(false);
const selectedPlayer = ref<Player | null>(null);
const switchActive = ref(false);
const switchSource = ref<Player | null>(null);
const isBenchSwitch = ref(false);

const totalPoints = ref(57);
const averagePoints = ref(52);
const highestPoints = ref(121);
const overallRank = ref("234,567");

const upcomingFixtures = ref<Fixture[]>([
    { match: "Black Stone FC vs Yellow Wolves", date: "20 Feb 2024" },
    { match: "Black Stone FC vs Silver Sharks", date: "25 Feb 2024" },
]);

const recentResults = ref<Result[]>([
    { match: "Black Stone FC 2-1 Red Devils", date: "15 Feb 2024" },
    { match: "Black Stone FC 3-0 Blue Tigers", date: "10 Feb 2024" },
    { match: "Black Stone FC 1-1 Green Eagles", date: "5 Feb 2024" },
]);

const topPerformers = ref<Performer[]>([
    { name: "E. Olunga", points: 15, image: "https://example.com/player1.png" },
    { name: "V. Manyara", points: 12, image: "https://example.com/player2.png" },
    { name: "B. Peter", points: 10, image: "https://example.com/player3.png" },
]);

interface StartingEleven {
    goalkeeper: Player;
    defenders: Player[];
    midfielders: Player[];
    forwards: Player[];
}

const startingElevenRef = ref<StartingEleven>(startingEleven);
const benchPlayersRef = ref<Player[]>(benchPlayers);

const goalkeeper = computed(() => startingElevenRef.value.goalkeeper);
const defenders = computed(() => startingElevenRef.value.defenders);
const midfielders = computed(() => startingElevenRef.value.midfielders);
const forwards = computed(() => startingElevenRef.value.forwards);

const openPlayerModal = (player: Player) => {
    selectedPlayer.value = player;
    showModal.value = true;
};

const closeModal = () => {
    showModal.value = false;
    selectedPlayer.value = null;
};

const handlePlayerClick = (player: Player, isBench = false) => {
    if (switchActive.value) {
        performSwitch(player, isBench);
    } else {
        openPlayerModal(player);
    }
};

const initiateSwitch = () => {
    if (!selectedPlayer.value) {
        console.warn("No player selected for switching.");
        return;
    }
    switchSource.value = selectedPlayer.value;
    switchActive.value = true;
    isBenchSwitch.value = benchPlayersRef.value.some(
        (p) => p.id === selectedPlayer.value?.id,
    );
    closeModal();
};

const performSwitch = (targetPlayer: Player, isBench: boolean) => {
    console.log(targetPlayer, isBench);
};

const isPlayerInStartingEleven = (player: Player) => {
    if (!player) return false;

    if (startingElevenRef.value.goalkeeper.id === player.id) {
        return true;
    }

    return ["defenders", "midfielders", "forwards"].some((position) => {
        const players = startingElevenRef.value[position as keyof StartingEleven] as Player[];
        return players.some((p) => p.id === player.id);
    });
};

const clearCaptaincy = () => {
    startingElevenRef.value.goalkeeper.isCaptain = false;

    ["defenders", "midfielders", "forwards"].forEach((position) => {
        const players = startingElevenRef.value[position as keyof StartingEleven] as Player[];
        players.forEach((player: Player) => {
            player.isCaptain = false;
        });
    });
};

const clearViceCaptaincy = () => {
    startingElevenRef.value.goalkeeper.isViceCaptain = false;

    ["defenders", "midfielders", "forwards"].forEach((position) => {
        const players = startingElevenRef.value[position as keyof StartingEleven] as Player[];
        players.forEach((player: Player) => {
            player.isViceCaptain = false;
        });
    });
};

const makeCaptain = () => {
    if (!selectedPlayer.value) {
        console.warn("No player selected to be captain.");
        return;
    }

    if (!isPlayerInStartingEleven(selectedPlayer.value)) {
        console.warn("Cannot assign captaincy to a bench player.");
        return;
    }

    if (selectedPlayer.value.isCaptain) {
        console.warn(`${selectedPlayer.value.name} is already the captain.`);
        return;
    }

    clearCaptaincy();
    selectedPlayer.value.isCaptain = true;
    closeModal();
};

const makeViceCaptain = () => {
    if (!selectedPlayer.value) {
        console.warn("No player selected to be vice-captain.");
        return;
    }

    if (!isPlayerInStartingEleven(selectedPlayer.value)) {
        console.warn("Cannot assign vice-captaincy to a bench player.");
        return;
    }

    if (selectedPlayer.value.isViceCaptain) {
        console.warn(`${selectedPlayer.value.name} is already the vice-captain.`);
        return;
    }

    clearViceCaptaincy();
    selectedPlayer.value.isViceCaptain = true;
    console.log(`${selectedPlayer.value.name} is now the vice-captain.`);
    closeModal();
};

onMounted(async () => {
    await authStore.initialize();
    if (!authStore.isAuthenticated) {
        router.push("/sign-in");
    }

});

const animateCard = (event) => {
    const card = event.currentTarget;
    card.classList.add('animate-pulse');
    setTimeout(() => {
        card.classList.remove('animate-pulse');
    }, 500);
};
</script>

<style scoped>
.team-card {
    transition: all 0.3s ease;
}

.team-card:hover {
    transform: scale(1.02);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}
</style>